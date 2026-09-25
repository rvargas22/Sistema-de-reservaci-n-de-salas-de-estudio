"""
Creacion e inicializacion de la base de datos del sistema.
"""

import sqlite3

from aplicacion.persistencia.base_datos import obtener_conexion


ESTUDIANTES_INICIALES = [
    (
        "A001234567",
        "Andrea Solano",
        "andrea@universidad.ac.cr",
        "activo",
    ),
    (
        "B009876543",
        "Carlos Méndez",
        "carlos@universidad.ac.cr",
        "activo",
    ),
    (
        "C004567890",
        "Daniela Rojas",
        "daniela@universidad.ac.cr",
        "inactivo",
    ),
]


SALAS_INICIALES = [
    (
        "S01",
        "Sala Biblioteca 1",
        4,
        "disponible",
    ),
    (
        "S02",
        "Sala Biblioteca 2",
        6,
        "disponible",
    ),
    (
        "S03",
        "Laboratorio de estudio",
        10,
        "disponible",
    ),
    (
        "S04",
        "Sala multimedia",
        8,
        "fuera_de_servicio",
    ),
    (
        "S05",
        "Cubículo individual",
        1,
        "disponible",
    ),
]


def crear_tablas(conexion):
    """
    Crea las tablas e indices principales del sistema
    si todavia no existen.
    """

    conexion.executescript(
        """
        CREATE TABLE IF NOT EXISTS estudiantes (
            carne TEXT PRIMARY KEY COLLATE NOCASE,

            nombre TEXT NOT NULL,

            correo TEXT NOT NULL,

            estado TEXT NOT NULL
                DEFAULT 'activo'
                CHECK (
                    estado IN (
                        'activo',
                        'inactivo'
                    )
                )
        );


        CREATE TABLE IF NOT EXISTS salas (
            codigo TEXT PRIMARY KEY COLLATE NOCASE,

            nombre TEXT NOT NULL,

            capacidad INTEGER NOT NULL
                CHECK (capacidad > 0),

            estado TEXT NOT NULL
                DEFAULT 'disponible'
                CHECK (
                    estado IN (
                        'disponible',
                        'fuera_de_servicio'
                    )
                )
        );


        CREATE TABLE IF NOT EXISTS reservaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            carne_estudiante TEXT NOT NULL
                COLLATE NOCASE,

            codigo_sala TEXT NOT NULL
                COLLATE NOCASE,

            fecha TEXT NOT NULL,

            hora_inicio TEXT NOT NULL,

            duracion_horas INTEGER NOT NULL
                CHECK (
                    duracion_horas IN (1, 2)
                ),

            cantidad_personas INTEGER NOT NULL
                CHECK (
                    cantidad_personas > 0
                ),

            estado TEXT NOT NULL
                DEFAULT 'activa'
                CHECK (
                    estado IN (
                        'activa',
                        'cancelada'
                    )
                ),

            FOREIGN KEY (carne_estudiante)
                REFERENCES estudiantes(carne),

            FOREIGN KEY (codigo_sala)
                REFERENCES salas(codigo)
        );

        CREATE TABLE IF NOT EXISTS series_recurrentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            carne_estudiante TEXT NOT NULL
                COLLATE NOCASE,

            codigo_sala TEXT NOT NULL
                COLLATE NOCASE,

            fecha_inicio TEXT NOT NULL,

            hora_inicio TEXT NOT NULL,

            duracion_horas INTEGER NOT NULL
                CHECK (
                    duracion_horas IN (1, 2)
                ),

            cantidad_personas INTEGER NOT NULL
                CHECK (
                    cantidad_personas > 0
                ),

            total_ocurrencias INTEGER NOT NULL
                CHECK (
                    total_ocurrencias BETWEEN 2 AND 8
                ),

            FOREIGN KEY (carne_estudiante)
                REFERENCES estudiantes(carne),

            FOREIGN KEY (codigo_sala)
                REFERENCES salas(codigo)
        );


        CREATE TABLE IF NOT EXISTS ocurrencias_recurrentes (
            serie_id INTEGER NOT NULL,

            numero_ocurrencia INTEGER NOT NULL
                CHECK (
                    numero_ocurrencia >= 1
                ),

            reservacion_id INTEGER NOT NULL UNIQUE,

            PRIMARY KEY (
                serie_id,
                numero_ocurrencia
            ),

            FOREIGN KEY (serie_id)
                REFERENCES series_recurrentes(id),

            FOREIGN KEY (reservacion_id)
                REFERENCES reservaciones(id)
        );


        CREATE INDEX IF NOT EXISTS
            idx_ocurrencias_recurrentes_serie
        ON ocurrencias_recurrentes (
            serie_id,
            numero_ocurrencia
        );

        CREATE INDEX IF NOT EXISTS
            idx_reservaciones_sala_fecha
        ON reservaciones (
            codigo_sala,
            fecha,
            estado
        );


        CREATE INDEX IF NOT EXISTS
            idx_reservaciones_estudiante
        ON reservaciones (
            carne_estudiante,
            fecha,
            estado
        );
        """
    )


def cargar_datos_iniciales(conexion):
    """
    Carga los estudiantes y las salas iniciales.

    Si los registros ya existen, no se duplican ni se
    sobrescriben.
    """

    conexion.executemany(
        """
        INSERT INTO estudiantes (
            carne,
            nombre,
            correo,
            estado
        )
        VALUES (?, ?, ?, ?)

        ON CONFLICT(carne) DO NOTHING
        """,
        ESTUDIANTES_INICIALES,
    )

    conexion.executemany(
        """
        INSERT INTO salas (
            codigo,
            nombre,
            capacidad,
            estado
        )
        VALUES (?, ?, ?, ?)

        ON CONFLICT(codigo) DO NOTHING
        """,
        SALAS_INICIALES,
    )


def inicializar_base_datos(ruta_base_datos=None):
    """
    Inicializa completamente la base de datos.

    Crea las tablas, indices y datos iniciales.
    """

    conexion = obtener_conexion(ruta_base_datos)

    try:
        crear_tablas(conexion)
        cargar_datos_iniciales(conexion)

        conexion.commit()

    except sqlite3.Error:
        conexion.rollback()
        raise

    finally:
        conexion.close()