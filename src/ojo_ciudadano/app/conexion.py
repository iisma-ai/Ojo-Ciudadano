"""Conexión de solo lectura a DuckDB, compartida por las pantallas."""

import duckdb
import streamlit as st

from ojo_ciudadano.indicadores.ejecutor import RUTA_DB


@st.cache_resource
def conexion() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(RUTA_DB), read_only=True)
