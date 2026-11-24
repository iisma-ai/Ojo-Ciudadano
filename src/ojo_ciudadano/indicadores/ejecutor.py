"""Ejecuta los indicadores de riesgo y guarda sus resultados en la tabla indicador_resultado.

Cada fichero sql/indicadores/rXX_*.sql es una consulta SELECT que devuelve una fila por
contrato aplicable con las columnas de COLUMNAS. Un contrato que no aparece en el resultado de
un indicador es «no aplicable» para ese indicador: no cuenta ni a favor ni en contra.

Uso: uv run python -m ojo_ciudadano.indicadores.ejecutor
"""

import re
from pathlib import Path

import duckdb

RAIZ = Path(__file__).resolve().parents[3]
CARPETA_SQL = RAIZ / "sql" / "indicadores"
CARPETA_ESQUEMA = RAIZ / "sql" / "esquema"

# Tablas de contexto que leen los indicadores (D-036) y que se cargan aparte de la base
# (`ingesta.cpv`, `ingesta.invente`). Si faltan, se crean vacías: los indicadores funcionan
# igual, solo que sin divisiones CPV ni entes públicos reconocidos.
CONTEXTO = {"cpv": "008_cpv.sql", "entidad_sector_publico": "009_sector_publico.sql"}
RUTA_DB = RAIZ / "data" / "ojo_ciudadano.duckdb"

COLUMNAS = ["contrato_id", "indicador", "aplicable", "activado", "valor", "motivo", "url_origen"]


def ficheros_indicadores(carpeta: Path = CARPETA_SQL) -> list[Path]:
    """Los SQL de indicador (r01_…, r03_…), en orden."""
    return sorted(p for p in carpeta.glob("*.sql") if re.match(r"r\d{2}_", p.name))


def crear_funciones(con: duckdb.DuckDBPyConnection, carpeta: Path = CARPETA_SQL) -> None:
    con.execute((carpeta / "000_funciones.sql").read_text(encoding="utf-8"))


def asegurar_contexto(con: duckdb.DuckDBPyConnection) -> None:
    """Crea vacías las tablas de contexto que falten (CONTEXTO) y la lista de adjudicatarios
    que son entes del sector público."""
    for tabla, fichero in CONTEXTO.items():
        ddl = (CARPETA_ESQUEMA / fichero).read_text(encoding="utf-8")
        con.execute(ddl.replace(f"CREATE TABLE {tabla}", f"CREATE TABLE IF NOT EXISTS {tabla}"))
    marcar_entes_publicos(con)


def marcar_entes_publicos(con: duckdb.DuckDBPyConnection) -> None:
    """Tabla derivada `adjudicatario_ente_publico`: adjudicatarios cuyo NIF está en INVENTE y
    cuyo nombre se parece al del inventario (D-036). Si el nombre no cuadra, suele ser un NIF
    de otra entidad puesto por error en la fuente (D-035), y la empresa se sigue tratando como
    privada: un error de la fuente no debe apagar sus señales."""
    from ojo_ciudadano.ingesta.invente import nombres_compatibles

    candidatos = con.execute(
        "SELECT d.adjudicatario_id, d.nif, d.nombre, e.nombre FROM adjudicatario AS d "
        "JOIN entidad_sector_publico AS e ON e.nif = d.nif"
    ).fetchall()
    con.execute(
        "CREATE OR REPLACE TABLE adjudicatario_ente_publico "
        "(adjudicatario_id VARCHAR PRIMARY KEY, nif VARCHAR)"
    )
    filas = [(a, n) for a, n, d, e in candidatos if nombres_compatibles(d, e)]
    if filas:
        con.executemany("INSERT INTO adjudicatario_ente_publico VALUES (?, ?)", filas)


def ejecutar(con: duckdb.DuckDBPyConnection, ruta_sql: Path) -> duckdb.DuckDBPyRelation:
    """Ejecuta un indicador y comprueba que devuelve las columnas acordadas."""
    relacion = con.sql(ruta_sql.read_text(encoding="utf-8"))
    if relacion.columns != COLUMNAS:
        raise ValueError(f"{ruta_sql.name} devuelve {relacion.columns}, se esperaba {COLUMNAS}")
    return relacion


def calcular_todos(con: duckdb.DuckDBPyConnection, carpeta: Path = CARPETA_SQL) -> None:
    """Sustituye indicador_resultado por el resultado de todos los indicadores."""
    crear_funciones(con, carpeta)
    asegurar_contexto(con)
    consultas = [ejecutar(con, ruta).sql_query() for ruta in ficheros_indicadores(carpeta)]
    union = "\nUNION ALL\n".join(f"SELECT * FROM ({q})" for q in consultas)
    con.execute(f"CREATE OR REPLACE TABLE indicador_resultado AS {union}")
    calcular_puntuacion(con, carpeta)


def calcular_puntuacion(con: duckdb.DuckDBPyConnection, carpeta: Path = CARPETA_SQL) -> None:
    """Puntuación por contrato, órgano y empresa a partir de indicador_resultado."""
    asegurar_contexto(con)
    con.execute((carpeta / "900_puntuacion.sql").read_text(encoding="utf-8"))


def resumen(con: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyRelation:
    return con.sql(
        """
        SELECT indicador, count(*) AS aplicables, count_if(activado) AS activados,
               round(100 * count_if(activado) / count(*), 1) AS pct_activados
        FROM indicador_resultado
        GROUP BY indicador
        ORDER BY indicador
        """
    )


def main() -> None:
    with duckdb.connect(str(RUTA_DB)) as con:
        calcular_todos(con)
        resumen(con).show()


if __name__ == "__main__":
    main()
