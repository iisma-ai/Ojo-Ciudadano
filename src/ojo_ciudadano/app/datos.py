"""Consultas que alimentan la interfaz. Solo leen; reciben la conexión DuckDB.

Todas devuelven listas de diccionarios para que las pantallas no dependan de DuckDB y los
tests puedan usar una base sintética en memoria. Las personas físicas no tienen ficha (D-007).
"""

import duckdb


def _filas(con: duckdb.DuckDBPyConnection, sql: str, parametros: list | None = None) -> list[dict]:
    cursor = con.execute(sql, parametros or [])
    columnas = [d[0] for d in cursor.description]
    return [dict(zip(columnas, fila, strict=True)) for fila in cursor.fetchall()]


# NIF con forma de DNI o NIE, también con erratas (sin el cero inicial, una cifra de más).
_PATRON_DNI_NIE = r"^([0-9]{7,8}[A-Z]|[XYZ][0-9]{7,8}[A-Z]|[KLM][0-9]{7}[0-9A-Z])$"


def _sin_personas(alias: str) -> str:
    """Condición SQL que deja fuera a las personas físicas (D-007): las marcadas como tales y,
    por si la base es anterior a la corrección de la normalización, cualquier NIF con forma
    de DNI o NIE."""
    return (
        f"{alias}.tipo_persona <> 'fisica' "
        f"AND NOT regexp_matches(coalesce({alias}.nif, ''), '{_PATRON_DNI_NIE}')"
    )


def fechas_datos(con: duckdb.DuckDBPyConnection) -> list[dict]:
    """Fecha de la última descarga de cada fuente (se muestra en todas las pantallas)."""
    return _filas(
        con,
        "SELECT fuente, max(fecha_descarga) AS fecha FROM contrato GROUP BY fuente ORDER BY 1",
    )


def buscar_empresas(con: duckdb.DuckDBPyConnection, texto: str, limite: int = 20) -> list[dict]:
    """Empresas por nombre o NIF. Excluye personas físicas."""
    texto = texto.strip()
    if len(texto) < 3:
        return []
    return _filas(
        con,
        f"""
        SELECT a.adjudicatario_id, a.nif, a.nombre, a.tipo_persona,
               p.n_contratos, p.n_con_alertas, p.puntuacion_ponderada
        FROM adjudicatario AS a
        JOIN puntuacion_empresa AS p USING (adjudicatario_id)
        WHERE {_sin_personas("a")}
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
        f"""
        SELECT a.adjudicatario_id, a.nif, a.nombre, a.tipo_persona,
               p.n_contratos, p.n_con_alertas, p.puntuacion_ponderada, p.puntuacion_media,
               (SELECT sum(importe_sin_iva) FROM adjudicacion
                 WHERE adjudicatario_id = a.adjudicatario_id) AS importe_sin_iva,
               (SELECT sum(importe_con_iva) FROM adjudicacion
                 WHERE adjudicatario_id = a.adjudicatario_id) AS importe_con_iva
        FROM adjudicatario AS a
        JOIN puntuacion_empresa AS p USING (adjudicatario_id)
        WHERE a.adjudicatario_id = ? AND {_sin_personas("a")}
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


def buscar_organos(con: duckdb.DuckDBPyConnection, texto: str, limite: int = 30) -> list[dict]:
    """Órganos por nombre (o todos, los de más contratos, si no se escribe nada)."""
    return _filas(
        con,
        """
        SELECT o.organo_id, o.nombre, p.n_contratos, p.puntuacion_ponderada
        FROM organo AS o
        JOIN puntuacion_organo AS p USING (organo_id)
        WHERE o.nombre ILIKE '%' || ? || '%'
        ORDER BY p.n_contratos DESC
        LIMIT ?
        """,
        [texto.strip(), limite],
    )


def ficha_organo(con: duckdb.DuckDBPyConnection, organo_id: str) -> dict | None:
    """Resumen de un órgano y su posición frente al resto (percentil de puntuación entre los
    órganos con al menos 100 contratos puntuados). Importes por separado según el IVA."""
    filas = _filas(
        con,
        """
        WITH comparables AS (
            SELECT organo_id, puntuacion_ponderada FROM puntuacion_organo
            WHERE n_contratos >= 100 AND puntuacion_ponderada IS NOT NULL
        )
        SELECT o.organo_id, o.nombre, o.consejeria, p.n_contratos, p.n_con_alertas,
               p.puntuacion_ponderada,
               (SELECT count(*) FROM comparables WHERE puntuacion_ponderada
                    <= p.puntuacion_ponderada) / nullif((SELECT count(*) FROM comparables), 0)
                    AS percentil,
               (SELECT count(*) FROM comparables) AS n_comparables,
               (SELECT sum(a.importe_sin_iva) FROM adjudicacion AS a
                 JOIN contrato_unico AS c USING (contrato_id)
                 WHERE c.organo_id = o.organo_id) AS importe_sin_iva,
               (SELECT sum(a.importe_con_iva) FROM adjudicacion AS a
                 JOIN contrato_unico AS c USING (contrato_id)
                 WHERE c.organo_id = o.organo_id) AS importe_con_iva
        FROM organo AS o
        JOIN puntuacion_organo AS p USING (organo_id)
        WHERE o.organo_id = ?
        """,
        [organo_id],
    )
    return filas[0] if filas else None


def tendencia_organo(con: duckdb.DuckDBPyConnection, organo_id: str) -> list[dict]:
    return _filas(
        con,
        """
        SELECT anio, n_contratos, n_con_alertas, puntuacion_ponderada
        FROM puntuacion_organo_anio WHERE organo_id = ? ORDER BY anio
        """,
        [organo_id],
    )


def indicadores_organo(con: duckdb.DuckDBPyConnection, organo_id: str) -> list[dict]:
    """Por indicador: % de contratos del órgano con la señal activada frente al % global."""
    return _filas(
        con,
        """
        WITH r AS (
            SELECT i.indicador, c.organo_id = ? AS del_organo, i.activado
            FROM indicador_resultado AS i
            JOIN contrato_unico AS c USING (contrato_id)
            WHERE i.aplicable
        )
        SELECT indicador,
               count_if(del_organo) AS aplicables,
               count_if(del_organo AND activado) AS activados,
               count_if(del_organo AND activado) / nullif(count_if(del_organo), 0) AS pct_organo,
               count_if(activado) / count(*) AS pct_global
        FROM r
        GROUP BY indicador
        HAVING count_if(del_organo) > 0
        ORDER BY indicador
        """,
        [organo_id],
    )


def procedimientos_organo(con: duckdb.DuckDBPyConnection, organo_id: str) -> list[dict]:
    """Nº de contratos por procedimiento (los menores aparecen como «Contrato menor»)."""
    return _filas(
        con,
        """
        SELECT coalesce(procedimiento, 'No indicado') AS procedimiento, count(*) AS n_contratos
        FROM contrato_unico WHERE organo_id = ?
        GROUP BY 1 ORDER BY 2 DESC
        """,
        [organo_id],
    )


def proveedores_organo(
    con: duckdb.DuckDBPyConnection, organo_id: str, limite: int = 10
) -> list[dict]:
    """Principales empresas por número de contratos; sin personas físicas (D-007)."""
    return _filas(
        con,
        f"""
        SELECT d.adjudicatario_id, d.nombre, d.nif, count(DISTINCT a.contrato_id) AS n_contratos,
               sum(a.importe_sin_iva) AS importe_sin_iva, sum(a.importe_con_iva) AS importe_con_iva
        FROM adjudicacion AS a
        JOIN contrato_unico AS c USING (contrato_id)
        JOIN adjudicatario AS d USING (adjudicatario_id)
        WHERE c.organo_id = ? AND {_sin_personas("d")}
        GROUP BY ALL ORDER BY n_contratos DESC LIMIT ?
        """,
        [organo_id, limite],
    )


_FILTRO_FLUJO = f"""
    c.fuente = ?
    AND {_sin_personas("d")}
    AND (? OR NOT c.es_menor)
    AND (? IS NULL
         OR year(coalesce(c.fecha_contrato, a.fecha_formalizacion, c.fecha_fin_plazo)) = ?)
    AND (? IS NULL OR c.tipo_contrato = ?)
"""


def _parametros_flujo(fuente, incluir_menores, anio, tipo_contrato) -> list:
    return [fuente, incluir_menores, anio, anio, tipo_contrato, tipo_contrato]


def flujos(
    con: duckdb.DuckDBPyConnection,
    fuente: str,
    incluir_menores: bool = False,
    anio: int | None = None,
    tipo_contrato: str | None = None,
    limite: int = 25,
) -> list[dict]:
    """Mayores flujos órgano → empresa. El importe es sin IVA en PLACSP y con IVA en el portal
    (se elige una fuente cada vez: no se suman importes de bases distintas). Sin personas
    físicas (D-007)."""
    campo = "a.importe_sin_iva" if fuente == "placsp" else "a.importe_con_iva"
    return _filas(
        con,
        f"""
        SELECT c.organo_id, o.nombre AS organo, a.adjudicatario_id, d.nombre AS empresa,
               count(DISTINCT c.contrato_id) AS n_contratos, sum({campo}) AS importe
        FROM adjudicacion AS a
        JOIN contrato_unico AS c USING (contrato_id)
        JOIN organo AS o USING (organo_id)
        JOIN adjudicatario AS d USING (adjudicatario_id)
        WHERE {_FILTRO_FLUJO} AND {campo} > 0
        GROUP BY ALL ORDER BY importe DESC LIMIT ?
        """,
        [*_parametros_flujo(fuente, incluir_menores, anio, tipo_contrato), limite],
    )


def contratos_flujo(
    con: duckdb.DuckDBPyConnection,
    organo_id: str,
    adjudicatario_id: str,
    fuente: str,
    incluir_menores: bool = False,
    anio: int | None = None,
    tipo_contrato: str | None = None,
    limite: int = 50,
) -> list[dict]:
    """Contratos de un flujo, con el enlace a la ficha oficial de cada uno."""
    campo = "a.importe_sin_iva" if fuente == "placsp" else "a.importe_con_iva"
    return _filas(
        con,
        f"""
        SELECT c.contrato_id, c.titulo, c.tipo_contrato, c.procedimiento,
               year(coalesce(c.fecha_contrato, a.fecha_formalizacion, c.fecha_fin_plazo)) AS anio,
               {campo} AS importe, c.url_origen
        FROM adjudicacion AS a
        JOIN contrato_unico AS c USING (contrato_id)
        JOIN adjudicatario AS d USING (adjudicatario_id)
        WHERE {_FILTRO_FLUJO} AND c.organo_id = ? AND a.adjudicatario_id = ? AND {campo} > 0
        ORDER BY importe DESC LIMIT ?
        """,
        [
            *_parametros_flujo(fuente, incluir_menores, anio, tipo_contrato),
            organo_id,
            adjudicatario_id,
            limite,
        ],
    )


def tipos_contrato(con: duckdb.DuckDBPyConnection) -> list[str]:
    filas = con.execute(
        "SELECT DISTINCT tipo_contrato FROM contrato_unico WHERE tipo_contrato IS NOT NULL "
        "ORDER BY 1"
    ).fetchall()
    return [f[0] for f in filas]
