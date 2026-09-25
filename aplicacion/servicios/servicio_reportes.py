"""
Servicio para generar reportes y exportarlos
en formato CSV.
"""

import csv
import os
import tempfile
from pathlib import Path

from aplicacion.persistencia import (
    consultar_reservaciones_por_rango,
)

from aplicacion.validaciones import (
    ErrorReglaNegocio,
    ErrorValidacion,
    convertir_fecha,
)


CAMPOS_CSV = [
    "id",
    "carne_estudiante",
    "nombre_estudiante",
    "codigo_sala",
    "nombre_sala",
    "fecha",
    "hora_inicio",
    "duracion_horas",
    "cantidad_personas",
    "estado",
]


def _validar_rango_fechas(
    fecha_inicial,
    fecha_final,
):
    """
    Valida y normaliza el rango utilizado
    para generar reportes.
    """

    if fecha_inicial is None:
        raise ErrorValidacion(
            "La fecha inicial es obligatoria."
        )

    if fecha_final is None:
        raise ErrorValidacion(
            "La fecha final es obligatoria."
        )

    if (
        isinstance(fecha_inicial, str)
        and not fecha_inicial.strip()
    ):
        raise ErrorValidacion(
            "La fecha inicial es obligatoria."
        )

    if (
        isinstance(fecha_final, str)
        and not fecha_final.strip()
    ):
        raise ErrorValidacion(
            "La fecha final es obligatoria."
        )

    inicio = convertir_fecha(
        fecha_inicial
    )

    fin = convertir_fecha(
        fecha_final
    )

    if fin < inicio:
        raise ErrorReglaNegocio(
            "La fecha final no puede ser anterior "
            "a la fecha inicial."
        )

    return (
        inicio,
        fin,
    )


def generar_reporte_reservaciones(
    fecha_inicial,
    fecha_final,
    ruta_base_datos=None,
):
    """
    Genera un reporte de reservaciones
    dentro del rango indicado.

    La funcion no modifica la base de datos.
    """

    inicio, fin = _validar_rango_fechas(
        fecha_inicial,
        fecha_final,
    )

    return consultar_reservaciones_por_rango(
        inicio.isoformat(),
        fin.isoformat(),
        ruta_base_datos,
    )


def _normalizar_ruta_csv(
    ruta_destino,
):
    """
    Normaliza la ruta de exportacion.

    Devuelve None cuando el usuario cancela
    la seleccion del destino.
    """

    if ruta_destino is None:
        return None

    if isinstance(
        ruta_destino,
        Path,
    ):
        ruta = ruta_destino

    elif isinstance(
        ruta_destino,
        str,
    ):
        if not ruta_destino.strip():
            return None

        ruta = Path(
            ruta_destino.strip()
        )

    else:
        raise ErrorValidacion(
            "La ruta de destino no es válida."
        )

    if ruta.suffix.lower() != ".csv":
        ruta = ruta.with_suffix(
            ".csv"
        )

    return ruta


def exportar_reporte_csv(
    reporte,
    ruta_destino,
):
    """
    Exporta un reporte a CSV utilizando UTF-8.

    Si el usuario cancela la seleccion del destino,
    devuelve None y no crea ningun archivo.

    La escritura se realiza primero sobre un archivo
    temporal. Solo al completarse correctamente se
    reemplaza el destino final.
    """

    ruta = _normalizar_ruta_csv(
        ruta_destino
    )

    if ruta is None:
        return None

    if ruta.exists() and ruta.is_dir():
        raise ErrorValidacion(
            "La ruta de destino corresponde "
            "a una carpeta y no a un archivo."
        )

    carpeta = ruta.parent

    if not carpeta.exists():
        raise ErrorValidacion(
            "La carpeta de destino no existe."
        )

    ruta_temporal = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            delete=False,
            dir=carpeta,
            prefix=f".{ruta.stem}_",
            suffix=".tmp",
        ) as archivo_temporal:

            ruta_temporal = Path(
                archivo_temporal.name
            )

            escritor = csv.DictWriter(
                archivo_temporal,
                fieldnames=CAMPOS_CSV,
                extrasaction="ignore",
            )

            escritor.writeheader()

            for fila in reporte:
                escritor.writerow(
                    {
                        campo: fila.get(
                            campo,
                            "",
                        )
                        for campo
                        in CAMPOS_CSV
                    }
                )

        os.replace(
            ruta_temporal,
            ruta,
        )

    except Exception:
        if (
            ruta_temporal is not None
            and ruta_temporal.exists()
        ):
            ruta_temporal.unlink()

        raise

    return ruta