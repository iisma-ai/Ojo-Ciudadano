"""Conexión de solo lectura a DuckDB, compartida por las pantallas.

Sin acceso a ficheros externos: la pantalla del asistente ejecuta SQL y así ninguna consulta
puede leer fuera de la base (docs/05-asistente.md).
"""

import duckdb
import streamlit as st

from ojo_ciudadano.asistente.sql_seguro import conexion_lectura
from ojo_ciudadano.indicadores.ejecutor import RUTA_DB


@st.cache_resource
def conexion() -> duckdb.DuckDBPyConnection:
    return conexion_lectura(RUTA_DB)
