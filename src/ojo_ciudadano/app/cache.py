"""Caché de las consultas de las pantallas (web fluida, 24-nov).

Streamlit vuelve a ejecutar la pantalla entera con cada clic, y sin caché cada vez se repetían
todas sus consultas a la base. La base solo cambia al regenerarla (y entonces se reinicia la
web, porque DuckDB no deja escribir con la web abierta), así que el resultado de una consulta
con los mismos parámetros se puede guardar una hora.

Fuera de Streamlit (tests, scripts) no se usa la caché: cada test tiene su propia base.
"""

import duckdb
import streamlit as st
from streamlit import runtime

SEGUNDOS = 3600
MAXIMO = 3000  # consultas distintas guardadas


def _ejecutar(con: duckdb.DuckDBPyConnection, sql: str, parametros) -> list[dict]:
    cursor = con.execute(sql, list(parametros or []))
    columnas = [d[0] for d in cursor.description]
    return [dict(zip(columnas, fila, strict=True)) for fila in cursor.fetchall()]


@st.cache_data(ttl=SEGUNDOS, max_entries=MAXIMO, show_spinner=False)
def _guardada(sql: str, parametros: tuple) -> list[dict]:
    from ojo_ciudadano.app.conexion import conexion  # evita el ciclo al importar

    return _ejecutar(conexion(), sql, parametros)


def filas(con: duckdb.DuckDBPyConnection, sql: str, parametros=None) -> list[dict]:
    """Filas de la consulta como diccionarios; dentro de la web, desde la caché."""
    if runtime.exists():
        return _guardada(sql, tuple(parametros or ()))
    return _ejecutar(con, sql, parametros)
