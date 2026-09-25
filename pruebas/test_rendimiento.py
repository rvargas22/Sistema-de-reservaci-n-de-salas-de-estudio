"""
Prueba formal de rendimiento para RNF-09.

Condicion requerida:

- 1 000 estudiantes.
- 5 000 reservaciones.
- Cada consulta relevante debe responder
  en menos de 2 segundos en el equipo
  utilizado para la prueba.

La preparacion de datos no forma parte del
tiempo medido.
"""

import os
import platform
import sqlite3
import statistics
import time
from datetime import (
    date,
    datetime,
    timedelta,
)
from pathlib import Path

import pytest

from aplicacion.persistencia import (
    inicializar_base_datos,
    obtener_conexion,
)

from aplicacion.servicios import (
    buscar_reservaciones_estudiante,
    consultar_estudiantes,
    consultar_historial_auditoria,
    consultar_horarios_disponibles,
    consultar_panel,
    consultar_salas,
    generar_reporte_reservaciones,
)


pytestmark = [
    pytest.mark.rnf,
    pytest.mark.rendimiento,
]


LIMITE_SEGUNDOS = 2.0

REPETICIONES = 3

TOTAL_ESTUDIANTES = 1000

TOTAL_RESERVACIONES = 5000


AHORA = datetime(
    2026,
    9,
    25,
    9,
    0,
)


def _preparar_base_rendimiento(
    tmp_path,
):
    """
    Crea una base temporal con exactamente:

    - 1 000 estudiantes.
    - 5 000 reservaciones.

    La carga se realiza fuera de la medicion.
    """

    ruta = (
        tmp_path
        / "rendimiento.db"
    )

    inicializar_base_datos(
        ruta
    )

    conexion = obtener_conexion(
        ruta
    )

    try:
        estudiantes_adicionales = [
            (
                f"T{numero:09d}",
                f"Estudiante {numero:04d}",
                (
                    f"estudiante{numero:04d}"
                    "@universidad.ac.cr"
                ),
                "activo",
            )
            for numero
            in range(
                1,
                998,
            )
        ]

        conexion.executemany(
            """
            INSERT INTO estudiantes (
                carne,
                nombre,
                correo,
                estado
            )
            VALUES (?, ?, ?, ?)
            """,
            estudiantes_adicionales,
        )

        carnes = [
            fila["carne"]
            for fila
            in conexion.execute(
                """
                SELECT carne
                FROM estudiantes
                ORDER BY carne
                """
            ).fetchall()
        ]

        assert (
            len(carnes)
            == TOTAL_ESTUDIANTES
        )

        codigos_sala = [
            "S01",
            "S02",
            "S03",
            "S05",
        ]

        fecha_base = date(
            2026,
            10,
            1,
        )

        reservaciones = []

        for indice in range(
            TOTAL_RESERVACIONES
        ):
            carne = carnes[
                indice
                % len(carnes)
            ]

            codigo_sala = codigos_sala[
                indice
                % len(codigos_sala)
            ]

            fecha = (
                fecha_base
                + timedelta(
                    days=(
                        indice
                        % 120
                    )
                )
            )

            hora = (
                8
                + (
                    indice
                    % 12
                )
            )

            estado = (
                "cancelada"
                if indice % 10 == 0
                else "activa"
            )

            reservaciones.append(
                (
                    carne,
                    codigo_sala,
                    fecha.isoformat(),
                    f"{hora:02d}:00",
                    1,
                    1,
                    estado,
                )
            )

        conexion.executemany(
            """
            INSERT INTO reservaciones (
                carne_estudiante,
                codigo_sala,
                fecha,
                hora_inicio,
                duracion_horas,
                cantidad_personas,
                estado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            reservaciones,
        )

        conexion.commit()

        cantidad_estudiantes = (
            conexion.execute(
                """
                SELECT COUNT(*)
                FROM estudiantes
                """
            ).fetchone()[0]
        )

        cantidad_reservaciones = (
            conexion.execute(
                """
                SELECT COUNT(*)
                FROM reservaciones
                """
            ).fetchone()[0]
        )

    finally:
        conexion.close()

    assert (
        cantidad_estudiantes
        == TOTAL_ESTUDIANTES
    )

    assert (
        cantidad_reservaciones
        == TOTAL_RESERVACIONES
    )

    return (
        ruta,
        carnes,
    )


def _medir_consulta(
    funcion,
):
    """
    Ejecuta una consulta varias veces y devuelve
    los tiempos en segundos.
    """

    tiempos = []

    for _ in range(
        REPETICIONES
    ):
        inicio = time.perf_counter()

        funcion()

        fin = time.perf_counter()

        tiempos.append(
            fin - inicio
        )

    return tiempos


def _datos_entorno():
    """
    Devuelve informacion basica y no sensible
    del equipo de prueba.
    """

    return {
        "sistema":
            platform.system(),

        "version_sistema":
            platform.release(),

        "arquitectura":
            platform.machine(),

        "procesador":
            (
                platform.processor()
                or "No informado por Python"
            ),

        "python":
            platform.python_version(),

        "sqlite":
            sqlite3.sqlite_version,
    }


def _crear_texto_evidencia(
    entorno,
    resultados,
):
    """
    Genera el contenido de evidencia sin incluir
    rutas personales del equipo.
    """

    lineas = [
        "EVIDENCIA RNF-09 - RENDIMIENTO",
        "================================",
        "",
        "Equipo de prueba",
        "----------------",
        (
            "Sistema: "
            f"{entorno['sistema']}"
        ),
        (
            "Versión del sistema: "
            f"{entorno['version_sistema']}"
        ),
        (
            "Arquitectura: "
            f"{entorno['arquitectura']}"
        ),
        (
            "Procesador: "
            f"{entorno['procesador']}"
        ),
        (
            "Python: "
            f"{entorno['python']}"
        ),
        (
            "SQLite: "
            f"{entorno['sqlite']}"
        ),
        "",
        "Carga utilizada",
        "---------------",
        (
            "Estudiantes: "
            f"{TOTAL_ESTUDIANTES}"
        ),
        (
            "Reservaciones: "
            f"{TOTAL_RESERVACIONES}"
        ),
        (
            "Límite por consulta: "
            f"{LIMITE_SEGUNDOS:.2f} segundos"
        ),
        (
            "Repeticiones por consulta: "
            f"{REPETICIONES}"
        ),
        "",
        "Resultados",
        "----------",
    ]

    for nombre, datos in resultados.items():
        lineas.extend(
            [
                nombre,
                (
                    "  mínimo: "
                    f"{datos['minimo']:.6f} s"
                ),
                (
                    "  promedio: "
                    f"{datos['promedio']:.6f} s"
                ),
                (
                    "  máximo: "
                    f"{datos['maximo']:.6f} s"
                ),
                (
                    "  resultado: "
                    + (
                        "APROBADO"
                        if datos["maximo"]
                        < LIMITE_SEGUNDOS
                        else "NO APROBADO"
                    )
                ),
                "",
            ]
        )

    aprobado = all(
        datos["maximo"]
        < LIMITE_SEGUNDOS
        for datos
        in resultados.values()
    )

    lineas.extend(
        [
            "Resultado general",
            "-----------------",
            (
                "APROBADO"
                if aprobado
                else "NO APROBADO"
            ),
            "",
        ]
    )

    return "\n".join(
        lineas
    )


def _guardar_evidencia(
    contenido,
):
    """
    Guarda evidencia solamente cuando se solicita
    mediante la variable GENERAR_EVIDENCIA_RNF09.

    El archivo no incluye rutas personales.
    """

    raiz = (
        Path(__file__)
        .resolve()
        .parents[1]
    )

    carpeta = (
        raiz
        / "evidencias"
    )

    carpeta.mkdir(
        parents=True,
        exist_ok=True,
    )

    destino = (
        carpeta
        / "rnf09_rendimiento.txt"
    )

    destino.write_text(
        contenido,
        encoding="utf-8",
    )

    return destino


def test_rnf09_consultas_menores_de_dos_segundos(
    tmp_path,
):
    """
    RNF-09 Rendimiento.

    Mide consultas relevantes del sistema sobre
    una base con la carga exigida.
    """

    ruta, carnes = (
        _preparar_base_rendimiento(
            tmp_path
        )
    )

    consultas = {
        "Consultar 1 000 estudiantes":
            lambda: consultar_estudiantes(
                ruta
            ),

        "Consultar salas":
            lambda: consultar_salas(
                ruta
            ),

        "Panel completo con 5 000 reservaciones":
            lambda: consultar_panel(
                ruta_base_datos=ruta
            ),

        "Panel con filtros combinados":
            lambda: consultar_panel(
                fecha="2026-10-20",
                codigo_sala="S01",
                estado="activa",
                ruta_base_datos=ruta,
            ),

        "Buscar reservaciones por estudiante":
            lambda: buscar_reservaciones_estudiante(
                carnes[0],
                ruta,
            ),

        "Consultar disponibilidad":
            lambda: consultar_horarios_disponibles(
                codigo_sala="S01",
                fecha="2026-10-20",
                duracion_horas=1,
                ruta_base_datos=ruta,
                ahora=AHORA,
            ),

        "Generar reporte de 5 000 reservaciones":
            lambda: generar_reporte_reservaciones(
                "2026-10-01",
                "2027-01-28",
                ruta,
            ),

        "Consultar historial de auditoria":
            lambda: consultar_historial_auditoria(
                ruta
            ),
    }

    resultados = {}

    for nombre, consulta in consultas.items():
        tiempos = _medir_consulta(
            consulta
        )

        resultados[nombre] = {
            "minimo":
                min(
                    tiempos
                ),

            "promedio":
                statistics.mean(
                    tiempos
                ),

            "maximo":
                max(
                    tiempos
                ),
        }

    entorno = _datos_entorno()

    evidencia = _crear_texto_evidencia(
        entorno,
        resultados,
    )

    print(
        "\n"
        + evidencia
    )

    if (
        os.environ.get(
            "GENERAR_EVIDENCIA_RNF09"
        )
        == "1"
    ):
        destino = _guardar_evidencia(
            evidencia
        )

        print(
            "Evidencia guardada en: "
            "evidencias/rnf09_rendimiento.txt"
        )

        assert destino.exists()

    for nombre, datos in resultados.items():
        assert (
            datos["maximo"]
            < LIMITE_SEGUNDOS
        ), (
            f"{nombre} superó el límite: "
            f"{datos['maximo']:.6f} segundos."
        )