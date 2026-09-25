"""
Pruebas relacionadas con la preparacion
de la version candidata.
"""

import re
from pathlib import Path

from main import (
    obtener_version_aplicacion,
)


RAIZ_PROYECTO = (
    Path(__file__).resolve().parents[1]
)


def test_archivo_version_existe_y_es_valido():
    """
    La candidata debe estar identificada mediante
    un archivo VERSION.
    """

    ruta = (
        RAIZ_PROYECTO
        / "VERSION"
    )

    assert ruta.exists()

    version = ruta.read_text(
        encoding="utf-8"
    ).strip()

    patron = (
        r"^\d+\.\d+\.\d+-rc\d+$"
    )

    assert re.fullmatch(
        patron,
        version,
    )


def test_main_lee_la_version_candidata():
    """
    La aplicacion debe obtener la version desde
    el mismo archivo VERSION.
    """

    version_archivo = (
        (
            RAIZ_PROYECTO
            / "VERSION"
        )
        .read_text(
            encoding="utf-8"
        )
        .strip()
    )

    assert (
        obtener_version_aplicacion()
        == version_archivo
    )


def test_dependencias_necesarias_declaradas():
    """
    requirements.txt debe declarar las
    dependencias externas utilizadas.
    """

    contenido = (
        (
            RAIZ_PROYECTO
            / "requirements.txt"
        )
        .read_text(
            encoding="utf-8"
        )
        .lower()
    )

    assert "pyside6" in contenido
    assert "pytest" in contenido


def test_readme_contiene_instrucciones_reproducibles():
    """
    El README debe contener los comandos mínimos
    para preparar y ejecutar el proyecto.
    """

    contenido = (
        (
            RAIZ_PROYECTO
            / "README.md"
        )
        .read_text(
            encoding="utf-8"
        )
    )

    elementos = [
        "python3 -m venv .venv",
        "pip install -r requirements.txt",
        "python main.py",
        "pytest -v",
        "VERSION",
        "datos/reservaciones.db",
    ]

    for elemento in elementos:
        assert elemento in contenido


def test_readme_documenta_datos_iniciales():
    """
    Los datos iniciales obligatorios deben
    encontrarse documentados.
    """

    contenido = (
        (
            RAIZ_PROYECTO
            / "README.md"
        )
        .read_text(
            encoding="utf-8"
        )
    )

    elementos = [
        "A001234567",
        "B009876543",
        "C004567890",
        "S01",
        "S02",
        "S03",
        "S04",
        "S05",
        "Andrea Solano",
        "Cubículo individual",
    ]

    for elemento in elementos:
        assert elemento in contenido


def test_gitignore_excluye_archivos_locales_basicos():
    """
    Verifica que los archivos locales principales
    no se incluyan accidentalmente en Git.
    """

    contenido = (
        (
            RAIZ_PROYECTO
            / ".gitignore"
        )
        .read_text(
            encoding="utf-8"
        )
    )

    elementos = [
        ".venv/",
        "__pycache__/",
        "*.pyc",
        "datos/*.db",
        ".pytest_cache/",
    ]

    for elemento in elementos:
        assert elemento in contenido