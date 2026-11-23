"""Búsqueda por palabras en los títulos de contratos, convenios y convocatorias (D-030, bloque A).

`ILIKE` no reconoce plurales ni tildes («ambulancias» no encuentra «ambulancia»). Esta búsqueda
usa BM25 de DuckDB (`fts`, raíces en español, sin tildes) sobre una tabla derivada,
`busqueda_texto`, con su índice guardado en la base: «ambulancias» encuentra 120 contratos
frente a 73 con `ILIKE`.

Construir (con la interfaz cerrada, tras regenerar la base):
    uv run python -m ojo_ciudadano.asistente.texto

Deben aparecer todas las palabras de la consulta (modo conjuntivo): si no, «ambulancias
transporte sanitario» contaría cualquier título con «transporte». Para alternativas, se
hacen búsquedas separadas. La consulta del modelo nunca entra en el SQL como texto: va
como parámetro.
"""

import sys
from pathlib import Path

import duckdb

from ojo_ciudadano.indicadores.ejecutor import RUTA_DB

TABLA = "busqueda_texto"
ORIGENES = {
    "contrato": "contratos (título del contrato)",
    "convenio": "convenios vigentes (título del convenio)",
    "convocatoria": "convocatorias de subvenciones (nombre de la convocatoria)",
}
EJEMPLOS = 20  # filas de ejemplo que se devuelven, ordenadas por relevancia

_SQL_TABLA = f"""
CREATE OR REPLACE TABLE {TABLA} AS
SELECT contrato_id AS id, 'contrato' AS origen, titulo, organo_id, fuente, url_origen,
       fecha_descarga
FROM contrato_unico WHERE titulo IS NOT NULL
UNION ALL
SELECT convenio_id, 'convenio', titulo, organo_id, fuente, url_origen, fecha_descarga
FROM convenio WHERE titulo IS NOT NULL
UNION ALL
SELECT 'bdns:convocatoria:' || id_convocatoria, 'convocatoria', any_value(convocatoria),
       any_value(organo_id), 'bdns', any_value(url_origen), max(fecha_descarga)
FROM concesion WHERE convocatoria IS NOT NULL AND id_convocatoria IS NOT NULL
GROUP BY id_convocatoria
"""


def construir_en(con: duckdb.DuckDBPyConnection) -> int:
    """Crea la tabla y su índice en una conexión con escritura. Devuelve las filas."""
    con.execute("INSTALL fts; LOAD fts")
    con.execute(_SQL_TABLA)
    con.execute(
        f"PRAGMA create_fts_index('{TABLA}', 'id', 'titulo', stemmer='spanish', "
        "stopwords='none', strip_accents=1, lower=1, overwrite=1)"
    )
    return con.execute(f"SELECT count(*) FROM {TABLA}").fetchall()[0][0]


def disponible(con: duckdb.DuckDBPyConnection) -> bool:
    try:
        con.execute(f"SELECT fts_main_{TABLA}.match_bm25('x', 'x')").fetchall()
        return True
    except duckdb.Error:
        return False


class BusquedaNoDisponible(ValueError):
    """La tabla o el índice no existen en esta base, o el origen no es válido."""


_COINCIDENCIAS = f"""
WITH c AS (
    SELECT b.*, fts_main_{TABLA}.match_bm25(b.id, $consulta, conjunctive := 1) AS relevancia
    FROM {TABLA} AS b WHERE b.origen = $origen
)
SELECT * FROM c WHERE relevancia IS NOT NULL
"""


def _resumen(con, origen: str, parametros: dict) -> tuple[list[str], list[list]]:
    """Recuento por fuente; para contratos, también el importe adjudicado (sin mezclar IVA)."""
    if origen == "contrato":
        sql = f"""
        WITH c AS ({_COINCIDENCIAS})
        SELECT c.fuente, count(DISTINCT c.id) AS n,
               sum(a.importe_sin_iva) FILTER (WHERE c.fuente = 'placsp') AS importe_sin_iva,
               sum(a.importe_con_iva) FILTER (WHERE c.fuente = 'portal_cm') AS importe_con_iva,
               max(c.fecha_descarga) AS fecha_descarga
        FROM c LEFT JOIN adjudicacion AS a ON a.contrato_id = c.id
        GROUP BY 1 ORDER BY 1
        """
    elif origen == "convocatoria":
        sql = f"""
        WITH c AS ({_COINCIDENCIAS})
        SELECT 'bdns' AS fuente, count(DISTINCT c.id) AS n_convocatorias,
               count(s.concesion_id) AS n_concesiones, sum(s.importe) AS importe_concedido,
               max(c.fecha_descarga) AS fecha_descarga
        FROM c LEFT JOIN concesion AS s
          ON 'bdns:convocatoria:' || s.id_convocatoria = c.id
        """
    else:
        sql = f"""
        WITH c AS ({_COINCIDENCIAS})
        SELECT fuente, count(*) AS n, max(fecha_descarga) AS fecha_descarga FROM c GROUP BY 1
        """
    cursor = con.execute(sql, parametros)
    return [d[0] for d in cursor.description], [list(f) for f in cursor.fetchall()]


def buscar(con: duckdb.DuckDBPyConnection, consulta: str, origen: str) -> dict:
    """Busca la consulta en los títulos del origen. Devuelve, con la forma de los resultados de
    `sql_seguro.ejecutar`, los ejemplos más relevantes con su enlace, y aparte el resumen."""
    if origen not in ORIGENES:
        raise BusquedaNoDisponible(f"Origen no válido: {origen}. Usa: {', '.join(ORIGENES)}.")
    if not consulta.strip():
        raise BusquedaNoDisponible("La búsqueda está vacía.")
    if not disponible(con):
        raise BusquedaNoDisponible(
            "La búsqueda por palabras no está preparada en esta base "
            "(uv run python -m ojo_ciudadano.asistente.texto). Usa consultar_sql con ILIKE."
        )
    parametros = {"consulta": consulta, "origen": origen}
    sql = f"""
    WITH c AS ({_COINCIDENCIAS})
    SELECT c.titulo, o.nombre AS organo, c.fuente, c.url_origen, c.fecha_descarga,
           round(c.relevancia, 2) AS relevancia
    FROM c LEFT JOIN organo AS o USING (organo_id)
    ORDER BY c.relevancia DESC LIMIT {EJEMPLOS}
    """
    cursor = con.execute(sql, parametros)
    columnas = [d[0] for d in cursor.description]
    filas = [list(f) for f in cursor.fetchall()]
    columnas_resumen, resumen = _resumen(con, origen, parametros)
    return {
        "sql": f"-- Búsqueda por palabras en {ORIGENES[origen]}: «{consulta}»\n{sql.strip()}",
        "columnas": columnas,
        "filas": filas,
        "recortado": False,
        "busqueda": consulta,
        "origen": origen,
        "resumen": {"columnas": columnas_resumen, "filas": resumen},
    }


def main() -> None:
    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else RUTA_DB
    with duckdb.connect(str(ruta)) as con:
        print(f"{TABLA}: {construir_en(con)} títulos indexados en {ruta}.")


if __name__ == "__main__":
    main()
