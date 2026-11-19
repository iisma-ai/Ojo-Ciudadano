"""Consultas que alimentan la interfaz. Solo leen; reciben la conexión DuckDB.

Todas devuelven listas de diccionarios para que las pantallas no dependan de DuckDB y los
tests puedan usar una base sintética en memoria. Las personas físicas no tienen ficha (D-007).
"""

import duckdb


def _filas(con: duckdb.DuckDBPyConnection, sql: str, parametros: list | None = None) -> list[dict]:
    cursor = con.execute(sql, parametros or [])
    columnas = [d[0] for d in cursor.description]
    return [dict(zip(columnas, fila, strict=True)) for fila in cursor.fetchall()]


def fecha_datos(con: duckdb.DuckDBPyConnection):
    """Fecha de la última descarga de datos (se muestra en todas las pantallas)."""
    return con.execute("SELECT max(fecha_descarga) FROM contrato").fetchone()[0]


def buscar_empresas(con: duckdb.DuckDBPyConnection, texto: str, limite: int = 20) -> list[dict]:
    """Empresas por nombre o NIF. Excluye personas físicas."""
    texto = texto.strip()
    if len(texto) < 3:
        return []
    return _filas(
        con,
        """
        SELECT a.adjudicatario_id, a.nif, a.nombre, a.tipo_persona,
               p.n_contratos, p.n_con_alertas, p.puntuacion_ponderada
        FROM adjudicatario AS a
        JOIN puntuacion_empresa AS p USING (adjudicatario_id)
        WHERE a.tipo_persona <> 'fisica'
          AND (a.nombre ILIKE '%' || ? || '%' OR a.nif = upper(?))
        ORDER BY p.n_contratos DESC
        LIMIT ?
        """,
        [texto, texto, limite],
    )


def ficha_empresa(con: duckdb.DuckDBPyConnection, adjudicatario_id: str) -> dict | None:
    """Resumen de una empresa. Los importes se dan por separado según el IVA de la fuente."""
    filas = _filas(
        con,
        """
        SELECT a.adjudicatario_id, a.nif, a.nombre, a.tipo_persona,
               p.n_contratos, p.n_con_alertas, p.puntuacion_ponderada, p.puntuacion_media,
               (SELECT sum(importe_sin_iva) FROM adjudicacion
                 WHERE adjudicatario_id = a.adjudicatario_id) AS importe_sin_iva,
               (SELECT sum(importe_con_iva) FROM adjudicacion
                 WHERE adjudicatario_id = a.adjudicatario_id) AS importe_con_iva
        FROM adjudicatario AS a
        JOIN puntuacion_empresa AS p USING (adjudicatario_id)
        WHERE a.adjudicatario_id = ? AND a.tipo_persona <> 'fisica'
        """,
        [adjudicatario_id],
    )
    return filas[0] if filas else None


def tendencia_empresa(con: duckdb.DuckDBPyConnection, adjudicatario_id: str) -> list[dict]:
    return _filas(
        con,
        """
        SELECT anio, n_contratos, n_con_alertas, puntuacion_ponderada
        FROM puntuacion_empresa_anio WHERE adjudicatario_id = ? ORDER BY anio
        """,
        [adjudicatario_id],
    )


def contratos_empresa(
    con: duckdb.DuckDBPyConnection, adjudicatario_id: str, limite: int = 200
) -> list[dict]:
    """Contratos de la empresa con su puntuación; primero los de más alertas e importe."""
    return _filas(
        con,
        """
        SELECT c.contrato_id, c.titulo, c.tipo_contrato, c.procedimiento, o.nombre AS organo,
               e.anio, e.importe, c.fuente, e.puntuacion, p.n_aplicables, p.n_activados,
               p.indicadores_activados, c.url_origen
        FROM puntuacion_empresa_contrato AS e
        JOIN contrato_unico AS c USING (contrato_id)
        JOIN organo AS o USING (organo_id)
        JOIN puntuacion_contrato AS p USING (contrato_id)
        WHERE e.adjudicatario_id = ?
        ORDER BY e.puntuacion DESC, e.importe DESC
        LIMIT ?
        """,
        [adjudicatario_id, limite],
    )


def alertas(
    con: duckdb.DuckDBPyConnection,
    min_aplicables: int = 3,
    indicador: str | None = None,
    limite: int = 100,
) -> list[dict]:
    """Contratos ordenados por puntuación. Por defecto solo los que tienen 3 o más
    indicadores aplicables, para que no dominen los menores (solo R-03 y R-04)."""
    return _filas(
        con,
        """
        SELECT p.contrato_id, c.titulo, c.tipo_contrato, c.procedimiento, o.nombre AS organo,
               p.anio, p.importe, c.fuente, p.puntuacion, p.n_aplicables, p.n_activados,
               p.indicadores_activados, c.url_origen
        FROM puntuacion_contrato AS p
        JOIN contrato_unico AS c USING (contrato_id)
        JOIN organo AS o ON o.organo_id = p.organo_id
        WHERE p.n_aplicables >= ? AND p.n_activados > 0
          AND (? IS NULL OR list_contains(string_split(p.indicadores_activados, ', '), ?))
        ORDER BY p.puntuacion DESC, p.n_activados DESC, p.importe DESC
        LIMIT ?
        """,
        [min_aplicables, indicador, indicador, limite],
    )


def motivos(con: duckdb.DuckDBPyConnection, contrato_id: str) -> list[dict]:
    """Indicadores activados de un contrato: valor, motivo y enlace al origen."""
    return _filas(
        con,
        """
        SELECT indicador, valor, motivo, url_origen
        FROM indicador_resultado
        WHERE contrato_id = ? AND activado
        ORDER BY indicador
        """,
        [contrato_id],
    )
