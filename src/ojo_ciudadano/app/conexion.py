"""Conexión de solo lectura a DuckDB, compartida por las pantallas.

Sin acceso a ficheros externos: la pantalla del asistente ejecuta SQL y así ninguna consulta
puede leer fuera de la base (docs/05-asistente.md).
"""

import threading

import duckdb
import streamlit as st

from ojo_ciudadano.asistente.sql_seguro import conexion_lectura
from ojo_ciudadano.indicadores.ejecutor import RUTA_DB

_CERROJO = threading.Lock()


@st.cache_resource
def _base() -> duckdb.DuckDBPyConnection:
    return conexion_lectura(RUTA_DB)


def conexion() -> duckdb.DuckDBPyConnection:
    """Un cursor nuevo en cada llamada. DuckDB no deja usar el mismo cursor desde dos hilos a la
    vez («connection is busy»), y Streamlit puede tener a la vez una ejecución a medias y otra
    nueva de la misma sesión (al teclear en un buscador con autocompletado, por ejemplo). Cada
    cursor comparte la base y su configuración de solo lectura y sin acceso a ficheros."""
    with _CERROJO:  # crear el cursor es instantáneo; usarlo ya no bloquea a los demás
        return _base().cursor()
