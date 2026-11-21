"""Conexión de solo lectura a DuckDB, compartida por las pantallas.

Sin acceso a ficheros externos: la pantalla del asistente ejecuta SQL y así ninguna consulta
puede leer fuera de la base (docs/05-asistente.md).
"""

import duckdb
import streamlit as st

from ojo_ciudadano.asistente.sql_seguro import conexion_lectura
from ojo_ciudadano.indicadores.ejecutor import RUTA_DB


@st.cache_resource
def _base() -> duckdb.DuckDBPyConnection:
    return conexion_lectura(RUTA_DB)


def conexion() -> duckdb.DuckDBPyConnection:
    """Una conexión por sesión del navegador. DuckDB no deja usar la misma conexión desde dos
    sesiones a la vez («connection is busy»); un cursor comparte la base y su configuración de
    solo lectura y sin acceso a ficheros."""
    if "_conexion" not in st.session_state:
        st.session_state["_conexion"] = _base().cursor()
    return st.session_state["_conexion"]
