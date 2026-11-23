"""Consultas que alimentan la interfaz. Solo leen; reciben la conexión DuckDB.

Todas devuelven listas de diccionarios para que las pantallas no dependan de DuckDB y los
tests puedan usar una base sintética en memoria. Las personas físicas no tienen ficha (D-007).
"""

import duckdb

from ojo_ciudadano.normalizacion.nif import PATRON_EMPRESA


def _filas(con: duckdb.DuckDBPyConnection, sql: str, parametros: list | None = None) -> list[dict]:
    cursor = con.execute(sql, parametros or [])
    columnas = [d[0] for d in cursor.description]
    return [dict(zip(columnas, fila, strict=True)) for fila in cursor.fetchall()]


# NIF con forma de DNI o NIE, también con erratas (sin el cero inicial, una cifra de más).
_PATRON_DNI_NIE = r"^([0-9]{7,8}[A-Z]|[XYZ][0-9]{7,8}[A-Z]|[KLM][0-9]{7}[0-9A-Z])$"


def _sin_personas(alias: str) -> str:
    """Condición SQL que deja fuera a las personas físicas (D-007): las marcadas como tales y,
    por si la base es anterior a la corrección de la normalización, cualquier NIF con forma
    de DNI o NIE. Un NIF «otro» solo pasa si el nombre lleva una forma jurídica."""
    return (
        f"{alias}.tipo_persona <> 'fisica' "
        f"AND NOT regexp_matches(coalesce({alias}.nif, ''), '{_PATRON_DNI_NIE}') "
        f"AND NOT contains({alias}.adjudicatario_id, 'PF-') "  # UTE con personas físicas
        f"AND ({alias}.tipo_persona <> 'otro' "
        f"OR regexp_matches(coalesce({alias}.nombre, ''), '{PATRON_EMPRESA}'))"
    )


def fechas_datos(con: duckdb.DuckDBPyConnection) -> list[dict]:
    """Fecha de la última descarga de cada fuente (se muestra en todas las pantallas)."""
    sql = "SELECT fuente, max(fecha_descarga) AS fecha FROM contrato GROUP BY fuente"
    if hay_subvenciones(con):
        sql += (
            " UNION ALL SELECT 'bdns', max(fecha_descarga) FROM concesion"
            " HAVING max(fecha_descarga) IS NOT NULL"
        )
    return _filas(con, f"SELECT * FROM ({sql}) ORDER BY 1")


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


def _entidades_con_datos(con: duckdb.DuckDBPyConnection) -> str:
    """Subconsulta con los identificadores que tienen ficha: contratos puntuados, subvenciones o
    encargos como medio propio (las dos últimas tablas pueden no existir en una base antigua)."""
    existentes = {
        f[0]
        for f in con.execute(
            "SELECT table_name FROM duckdb_tables() WHERE table_name IN ('concesion', 'encargo')"
        ).fetchall()
    }
    partes = ["SELECT adjudicatario_id FROM puntuacion_empresa"]
    if "concesion" in existentes:
        partes.append("SELECT beneficiario_id FROM concesion")
    if "encargo" in existentes:
        partes.append("SELECT medio_propio_id FROM encargo")
    return "(" + " UNION ".join(partes) + ")"


def sugerir_empresas(con: duckdb.DuckDBPyConnection, texto: str, limite: int = 15) -> list[dict]:
    """Empresas para el autocompletado: primero las que empiezan por lo escrito, luego (con tres
    letras o más) las que lo contienen. Sin texto, las de más contratos. Sin personas físicas."""
    texto = texto.strip()
    return _filas(
        con,
        f"""
        SELECT a.adjudicatario_id, a.nombre, a.nif, coalesce(p.n_contratos, 0) AS n_contratos
        FROM adjudicatario AS a
        JOIN {_entidades_con_datos(con)} USING (adjudicatario_id)
        LEFT JOIN puntuacion_empresa AS p USING (adjudicatario_id)
        WHERE {_sin_personas("a")} AND a.nombre IS NOT NULL
          AND (? = '' OR strip_accents(a.nombre) ILIKE strip_accents(?) || '%' OR a.nif = upper(?)
               OR (length(?) >= 3 AND strip_accents(a.nombre) ILIKE '%' || strip_accents(?) || '%'))
        ORDER BY (strip_accents(a.nombre) ILIKE strip_accents(?) || '%') DESC,
                 n_contratos DESC
        LIMIT ?
        """,
        [texto, texto, texto, texto, texto, texto, limite],
    )


def sugerir_organos(con: duckdb.DuckDBPyConnection, texto: str, limite: int = 15) -> list[dict]:
    """Órganos para el autocompletado: primero los que empiezan por lo escrito, luego los que
    lo contienen. Sin texto, los de más contratos."""
    texto = texto.strip()
    return _filas(
        con,
        """
        SELECT o.organo_id, o.nombre, p.n_contratos
        FROM organo AS o
        JOIN puntuacion_organo AS p USING (organo_id)
        WHERE ? = '' OR strip_accents(o.nombre) ILIKE strip_accents(?) || '%'
           OR strip_accents(o.nombre) ILIKE '%' || strip_accents(?) || '%'
        ORDER BY (strip_accents(o.nombre) ILIKE strip_accents(?) || '%') DESC, p.n_contratos DESC
        LIMIT ?
        """,
        [texto, texto, texto, texto, limite],
    )


def ficha_empresa(con: duckdb.DuckDBPyConnection, adjudicatario_id: str) -> dict | None:
    """Resumen de una empresa. Los importes se dan por separado según el IVA de la fuente."""
    filas = _filas(
        con,
        f"""
        SELECT a.adjudicatario_id, a.nif, a.nombre, a.tipo_persona,
               coalesce(p.n_contratos, 0) AS n_contratos,
               coalesce(p.n_con_alertas, 0) AS n_con_alertas,
               p.puntuacion_ponderada, p.puntuacion_media,
               (SELECT sum(importe_sin_iva) FROM adjudicacion
                 WHERE adjudicatario_id = a.adjudicatario_id) AS importe_sin_iva,
               (SELECT sum(importe_con_iva) FROM adjudicacion
                 WHERE adjudicatario_id = a.adjudicatario_id) AS importe_con_iva
        FROM adjudicatario AS a
        JOIN {_entidades_con_datos(con)} USING (adjudicatario_id)
        LEFT JOIN puntuacion_empresa AS p USING (adjudicatario_id)
        WHERE a.adjudicatario_id = ? AND {_sin_personas("a")}
        """,
        [adjudicatario_id],
    )
    return filas[0] if filas else None


def hay_subvenciones(con: duckdb.DuckDBPyConnection) -> bool:
    """La base tiene la tabla `concesion` (se cargó con la BDNS)."""
    return bool(
        con.execute(
            "SELECT count(*) FROM duckdb_tables() WHERE table_name = 'concesion'"
        ).fetchone()[0]
    )


# Beneficiario que se puede mostrar con nombre; el resto (personas físicas, NIF extranjeros o
# erróneos) se agrupa en una sola fila por órgano (D-007).
AGREGADO_PERSONAS = "Personas físicas y otros beneficiarios (agregados)"


def _beneficiario_visible(alias: str) -> str:
    return f"({alias}.tipo_persona IN ('juridica', 'ute') AND {_sin_personas(alias)})"


def subvenciones_empresa(
    con: duckdb.DuckDBPyConnection, adjudicatario_id: str, limite: int = 20
) -> list[dict]:
    """Subvenciones concedidas a la empresa por convocatoria, con enlace a la BDNS. Vacío si la
    base no tiene la tabla `concesion` (se cargó sin la BDNS)."""
    if not hay_subvenciones(con):
        return []
    return _filas(
        con,
        f"""
        SELECT s.convocatoria, o.nombre AS organo, count(*) AS n_concesiones,
               sum(s.importe) AS importe, min(s.fecha_concesion) AS desde,
               max(s.fecha_concesion) AS hasta, any_value(s.url_origen) AS url_origen,
               count(*) OVER () AS n_convocatorias_total,
               sum(sum(s.importe)) OVER () AS importe_total,
               max(max(s.fecha_descarga)) OVER () AS fecha_descarga
        FROM concesion AS s
        JOIN organo AS o USING (organo_id)
        JOIN adjudicatario AS a ON a.adjudicatario_id = s.beneficiario_id
        WHERE s.beneficiario_id = ? AND {_sin_personas("a")}
        GROUP BY s.convocatoria, o.nombre
        ORDER BY importe DESC
        LIMIT ?
        """,
        [adjudicatario_id, limite],
    )


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


ORDEN_ALERTAS = {
    "puntuacion": "p.puntuacion DESC, p.n_activados DESC, p.importe DESC",
    "senales": "p.n_activados DESC, p.puntuacion DESC, p.importe DESC",
    "importe_desc": "p.importe DESC NULLS LAST, p.puntuacion DESC",
    "importe_asc": "p.importe ASC NULLS LAST, p.puntuacion DESC",
    "reciente": "p.anio DESC NULLS LAST, p.puntuacion DESC, p.importe DESC",
}


def alertas(
    con: duckdb.DuckDBPyConnection,
    min_aplicables: int = 3,
    indicador: str | None = None,
    limite: int = 100,
    texto: str | None = None,
    anio: int | None = None,
    organo_id: str | None = None,
    *,
    indicadores: list[str] | None = None,
    todas: bool = False,
    orden: str = "puntuacion",
    min_puntuacion: float = 0.0,
    min_activados: int = 1,
    tipo_contrato: str | None = None,
    adjudicatario_id: str | None = None,
) -> list[dict]:
    """Contratos con alguna señal. Por defecto solo los que tienen 3 o más indicadores
    aplicables, para que no dominen los menores (solo R-03 y R-04). `texto` busca en el título
    y en el nombre del organismo. `indicadores` filtra por las señales elegidas (cualquiera de
    ellas o, con `todas`, todas a la vez); `indicador` es la forma de una sola señal."""
    elegidas = list(indicadores or ([indicador] if indicador else []))
    condiciones = ["p.n_aplicables >= ?", "p.n_activados >= ?", "p.puntuacion >= ?"]
    parametros: list = [min_aplicables, max(min_activados, 1), min_puntuacion]
    if elegidas:
        funcion = "list_has_all" if todas else "list_has_any"
        condiciones.append(f"{funcion}(string_split(p.indicadores_activados, ', '), ?)")
        parametros.append(elegidas)
    if texto:
        condiciones.append("(c.titulo ILIKE '%' || ? || '%' OR o.nombre ILIKE '%' || ? || '%')")
        parametros += [texto, texto]
    if anio is not None:
        condiciones.append("p.anio = ?")
        parametros.append(anio)
    if organo_id:
        condiciones.append("p.organo_id = ?")
        parametros.append(organo_id)
    if tipo_contrato:
        condiciones.append("c.tipo_contrato = ?")
        parametros.append(tipo_contrato)
    if adjudicatario_id:
        condiciones.append(
            "EXISTS (SELECT 1 FROM adjudicacion AS ad WHERE ad.contrato_id = p.contrato_id "
            "AND ad.adjudicatario_id = ?)"
        )
        parametros.append(adjudicatario_id)
    parametros.append(limite)
    return _filas(
        con,
        f"""
        SELECT p.contrato_id, c.titulo, c.tipo_contrato, c.procedimiento, o.nombre AS organo,
               p.anio, p.importe, c.fuente, p.puntuacion, p.n_aplicables, p.n_activados,
               p.indicadores_activados, c.url_origen
        FROM puntuacion_contrato AS p
        JOIN contrato_unico AS c USING (contrato_id)
        JOIN organo AS o ON o.organo_id = p.organo_id
        WHERE {" AND ".join(condiciones)}
        ORDER BY {ORDEN_ALERTAS.get(orden, ORDEN_ALERTAS["puntuacion"])}
        LIMIT ?
        """,
        parametros,
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
    organo_id: str | None = None,
) -> list[dict]:
    """Mayores flujos órgano → empresa. El importe es sin IVA en PLACSP y con IVA en el portal
    (se elige una fuente cada vez: no se suman importes de bases distintas). Sin personas
    físicas (D-007). Con `organo_id`, solo los de ese organismo."""
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
        WHERE {_FILTRO_FLUJO} AND {campo} > 0 AND (? IS NULL OR c.organo_id = ?)
        GROUP BY ALL ORDER BY importe DESC LIMIT ?
        """,
        [
            *_parametros_flujo(fuente, incluir_menores, anio, tipo_contrato),
            organo_id,
            organo_id,
            limite,
        ],
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


def subvenciones_organo(con: duckdb.DuckDBPyConnection, organo_id: str) -> dict | None:
    """Resumen de las subvenciones concedidas por un órgano (None si no hay)."""
    if not hay_subvenciones(con):
        return None
    filas = _filas(
        con,
        f"""
        SELECT count(*) AS n_concesiones, sum(s.importe) AS importe,
               count(DISTINCT s.beneficiario_id) FILTER (WHERE {_beneficiario_visible("a")})
                   AS n_entidades,
               coalesce(sum(s.importe) FILTER (WHERE NOT {_beneficiario_visible("a")}), 0)
                   AS importe_agregado,
               count(*) FILTER (WHERE NOT {_beneficiario_visible("a")}) AS n_agregado,
               min(s.fecha_concesion) AS desde, max(s.fecha_concesion) AS hasta,
               max(s.fecha_descarga) AS fecha_descarga
        FROM concesion AS s
        JOIN adjudicatario AS a ON a.adjudicatario_id = s.beneficiario_id
        WHERE s.organo_id = ?
        """,
        [organo_id],
    )
    return filas[0] if filas and filas[0]["n_concesiones"] else None


def convocatorias_organo(
    con: duckdb.DuckDBPyConnection, organo_id: str, limite: int = 10
) -> list[dict]:
    """Convocatorias del órgano con más importe concedido, con enlace a su ficha en la BDNS."""
    if not hay_subvenciones(con):
        return []
    return _filas(
        con,
        """
        SELECT convocatoria, count(*) AS n_concesiones, sum(importe) AS importe,
               any_value(url_origen) AS url_origen
        FROM concesion WHERE organo_id = ?
        GROUP BY convocatoria ORDER BY importe DESC LIMIT ?
        """,
        [organo_id, limite],
    )


def beneficiarios_organo(
    con: duckdb.DuckDBPyConnection, organo_id: str, limite: int = 10
) -> list[dict]:
    """Entidades (personas jurídicas) con más importe concedido por el órgano."""
    if not hay_subvenciones(con):
        return []
    return _filas(
        con,
        f"""
        SELECT a.adjudicatario_id, a.nombre, a.nif, count(*) AS n_concesiones,
               sum(s.importe) AS importe
        FROM concesion AS s
        JOIN adjudicatario AS a ON a.adjudicatario_id = s.beneficiario_id
        WHERE s.organo_id = ? AND {_beneficiario_visible("a")}
        GROUP BY ALL ORDER BY importe DESC LIMIT ?
        """,
        [organo_id, limite],
    )


def _beneficiario_flujo() -> str:
    return f"CASE WHEN {_beneficiario_visible('a')} THEN a.adjudicatario_id ELSE 'AGREGADO' END"


def flujos_subvenciones(
    con: duckdb.DuckDBPyConnection,
    anio: int | None = None,
    limite: int = 25,
    organo_id: str | None = None,
) -> list[dict]:
    """Mayores flujos órgano → beneficiario de subvenciones. Las personas físicas y los NIF no
    verificables de cada órgano forman un solo flujo agregado (D-007)."""
    if not hay_subvenciones(con):
        return []
    return _filas(
        con,
        f"""
        SELECT s.organo_id, o.nombre AS organo,
               {_beneficiario_flujo()} AS adjudicatario_id,
               CASE WHEN {_beneficiario_visible("a")} THEN a.nombre
                    ELSE '{AGREGADO_PERSONAS}' END AS empresa,
               count(*) AS n_contratos, sum(s.importe) AS importe
        FROM concesion AS s
        JOIN organo AS o USING (organo_id)
        JOIN adjudicatario AS a ON a.adjudicatario_id = s.beneficiario_id
        WHERE (? IS NULL OR year(s.fecha_concesion) = ?) AND s.importe > 0
          AND (? IS NULL OR s.organo_id = ?)
        GROUP BY ALL ORDER BY importe DESC LIMIT ?
        """,
        [anio, anio, organo_id, organo_id, limite],
    )


MIN_CONCESIONES_AGREGADO = 5


def fecha_subvenciones(con: duckdb.DuckDBPyConnection):
    """Fecha de descarga de la BDNS (None si la base no tiene subvenciones)."""
    if not hay_subvenciones(con):
        return None
    return con.execute("SELECT max(fecha_descarga) FROM concesion").fetchone()[0]


def concesiones_flujo(
    con: duckdb.DuckDBPyConnection,
    organo_id: str,
    adjudicatario_id: str,
    anio: int | None = None,
    limite: int = 50,
) -> list[dict]:
    """Convocatorias de un flujo de subvenciones, con el enlace a su ficha en la BDNS.

    En el flujo agregado de personas físicas solo se listan las convocatorias con al menos
    MIN_CONCESIONES_AGREGADO concesiones; las demás se suman en una fila «Otras convocatorias»
    sin enlace, para que una convocatoria con una o dos personas no permita identificarlas.
    """
    filas = _filas(
        con,
        f"""
        SELECT s.convocatoria AS titulo, count(*) AS n_concesiones,
               min(year(s.fecha_concesion)) AS anio, sum(s.importe) AS importe,
               any_value(s.url_origen) AS url_origen
        FROM concesion AS s
        JOIN adjudicatario AS a ON a.adjudicatario_id = s.beneficiario_id
        WHERE s.organo_id = ? AND {_beneficiario_flujo()} = ?
          AND (? IS NULL OR year(s.fecha_concesion) = ?) AND s.importe > 0
        GROUP BY s.convocatoria ORDER BY importe DESC
        """,
        [organo_id, adjudicatario_id, anio, anio],
    )
    if adjudicatario_id != "AGREGADO":
        return filas[:limite]
    visibles = [f for f in filas if f["n_concesiones"] >= MIN_CONCESIONES_AGREGADO]
    resto = [f for f in filas if f["n_concesiones"] < MIN_CONCESIONES_AGREGADO]
    if resto:
        visibles = visibles[:limite]
        visibles.append(
            {
                "titulo": f"Otras convocatorias ({len(resto)}), con menos de "
                f"{MIN_CONCESIONES_AGREGADO} concesiones cada una",
                "n_concesiones": sum(f["n_concesiones"] for f in resto),
                "anio": None,
                "importe": sum(f["importe"] for f in resto),
                "url_origen": None,
            }
        )
    return visibles


def hay_anomalias(con: duckdb.DuckDBPyConnection) -> bool:
    """La base tiene la tabla derivada `anomalia_resultado` (D-021)."""
    return bool(
        con.execute(
            "SELECT count(*) FROM duckdb_tables() WHERE table_name = 'anomalia_resultado'"
        ).fetchall()[0][0]
    )


# Contrato con algún adjudicatario que no se puede mostrar con nombre (D-007).
_CON_PERSONAS = f"""
    EXISTS (
        SELECT 1 FROM adjudicacion AS ad
        JOIN adjudicatario AS a ON a.adjudicatario_id = ad.adjudicatario_id
        WHERE ad.contrato_id = r.contrato_id AND NOT {_beneficiario_visible("a")}
    )
"""


def grupos_anomalias(con: duckdb.DuckDBPyConnection) -> list[dict]:
    """Grupos de pares con su número de contratos y de atípicos."""
    if not hay_anomalias(con):
        return []
    return _filas(
        con,
        """
        SELECT grupo, any_value(n_grupo) AS n_grupo, count_if(atipico) AS n_atipicos
        FROM anomalia_resultado GROUP BY grupo ORDER BY n_grupo DESC
        """,
    )


ORDEN_ATIPICOS = {
    "mas_atipico": "r.puntuacion DESC, r.contrato_id",
    "menos_atipico": "r.puntuacion ASC, r.contrato_id",
    "importe_desc": "v.importe DESC NULLS LAST, r.puntuacion DESC",
    "importe_asc": "v.importe ASC NULLS LAST, r.puntuacion DESC",
}

# Posible error al introducir los datos en la fuente: valores que no tienen sentido (baja
# negativa de más del 100 %, o sea, adjudicado por más del doble del presupuesto; modificaciones
# de más de cinco veces el importe adjudicado; importe adjudicado de menos de 1 euro).
_POSIBLE_ERROR = "(v.baja < -1 OR v.modificaciones > 5 OR v.importe < 1)"

_VARIABLES_ATIPICOS = """
    SELECT contrato_id, grupo, max(importe) AS importe, min(baja) AS baja,
           max(modificaciones) AS modificaciones
    FROM anomalia_variables GROUP BY contrato_id, grupo
"""


def _filtro_atipicos(
    grupo: str | None,
    min_puntuacion: float,
    con_errores: bool,
    variable: str | None,
    texto: str | None,
) -> tuple[str, list]:
    condiciones = ["r.atipico", "(? IS NULL OR r.grupo = ?)", "r.puntuacion >= ?"]
    parametros: list = [grupo, grupo, min_puntuacion]
    if not con_errores:
        condiciones.append(f"NOT coalesce({_POSIBLE_ERROR}, false)")
    if variable:
        condiciones.append("list_contains(string_split(r.variables, ', '), ?)")
        parametros.append(variable)
    if texto:
        condiciones.append(
            "(c.titulo ILIKE '%' || ? || '%' OR o.nombre ILIKE '%' || ? || '%' OR EXISTS ("
            "SELECT 1 FROM adjudicacion AS ad2 JOIN adjudicatario AS a2 "
            "ON a2.adjudicatario_id = ad2.adjudicatario_id "
            "WHERE ad2.contrato_id = r.contrato_id AND a2.nombre ILIKE '%' || ? || '%'))"
        )
        parametros += [texto, texto, texto]
    return " AND ".join(condiciones), parametros


def atipicos(
    con: duckdb.DuckDBPyConnection,
    grupo: str | None = None,
    limite: int = 100,
    *,
    orden: str = "mas_atipico",
    min_puntuacion: float = 0.0,
    con_errores: bool = True,
    variable: str | None = None,
    texto: str | None = None,
) -> list[dict]:
    """Contratos atípicos respecto a sus pares. `orden`: de más a menos atípico (por defecto),
    al revés, o por importe. `min_puntuacion` deja solo los más alejados que ese nivel,
    `con_errores=False` oculta los que parecen un error de introducción de los datos y
    `variable` deja los que se alejan en una variable concreta. Los contratos de personas
    físicas no se listan uno a uno (D-007): se cuentan en `atipicos_agregados`."""
    if not hay_anomalias(con):
        return []
    donde, parametros = _filtro_atipicos(grupo, min_puntuacion, con_errores, variable, texto)
    return _filas(
        con,
        f"""
        SELECT r.contrato_id, c.titulo, o.nombre AS organo, r.grupo, r.n_grupo,
               r.puntuacion, r.variables, r.motivo, r.url_origen, v.importe,
               coalesce({_POSIBLE_ERROR}, false) AS posible_error,
               string_agg(DISTINCT a.nombre, ', ') AS adjudicatarios
        FROM anomalia_resultado AS r
        JOIN contrato_unico AS c USING (contrato_id)
        JOIN organo AS o ON o.organo_id = c.organo_id
        LEFT JOIN ({_VARIABLES_ATIPICOS}) AS v
          ON v.contrato_id = r.contrato_id AND v.grupo = r.grupo
        LEFT JOIN adjudicacion AS ad ON ad.contrato_id = r.contrato_id
        LEFT JOIN adjudicatario AS a ON a.adjudicatario_id = ad.adjudicatario_id
        WHERE {donde} AND NOT {_CON_PERSONAS}
        GROUP BY ALL
        ORDER BY {ORDEN_ATIPICOS.get(orden, ORDEN_ATIPICOS["mas_atipico"])}
        LIMIT ?
        """,
        [*parametros, limite],
    )


def atipicos_errores_ocultos(
    con: duckdb.DuckDBPyConnection, grupo: str | None = None, min_puntuacion: float = 0.0
) -> int:
    """Cuántos atípicos que parecen un error de introducción de datos hay con estos filtros."""
    if not hay_anomalias(con):
        return 0
    return con.execute(
        f"""
        SELECT count(*) FROM anomalia_resultado AS r
        JOIN ({_VARIABLES_ATIPICOS}) AS v ON v.contrato_id = r.contrato_id AND v.grupo = r.grupo
        WHERE r.atipico AND (? IS NULL OR r.grupo = ?) AND r.puntuacion >= ?
          AND coalesce({_POSIBLE_ERROR}, false) AND NOT {_CON_PERSONAS}
        """,
        [grupo, grupo, min_puntuacion],
    ).fetchall()[0][0]


def atipicos_agregados(
    con: duckdb.DuckDBPyConnection, grupo: str | None = None, min_puntuacion: float = 0.0
) -> int:
    """Contratos atípicos de personas físicas u otros adjudicatarios sin ficha (D-007)."""
    if not hay_anomalias(con):
        return 0
    return con.execute(
        f"""
        SELECT count(*) FROM anomalia_resultado AS r
        WHERE r.atipico AND (? IS NULL OR r.grupo = ?) AND r.puntuacion >= ?
          AND {_CON_PERSONAS}
        """,
        [grupo, grupo, min_puntuacion],
    ).fetchall()[0][0]


def anomalia_contrato(con: duckdb.DuckDBPyConnection, contrato_id: str) -> dict | None:
    """Resultado de la detección de anomalías para un contrato, si es atípico."""
    if not hay_anomalias(con):
        return None
    filas = _filas(
        con,
        "SELECT * FROM anomalia_resultado WHERE contrato_id = ? AND atipico",
        [contrato_id],
    )
    return filas[0] if filas else None


# --- Portada y visualizaciones por señal (D-023, docs/11-accesibilidad.md) ---


def resumen_portada(con: duckdb.DuckDBPyConnection) -> dict:
    """Cifras grandes de la portada. Recuentos, no sumas: los importes de las fuentes no
    se pueden sumar entre sí (P-10)."""
    fila = _filas(
        con,
        """
        SELECT (SELECT count(*) FROM contrato_unico) AS n_contratos,
               (SELECT count(*) FROM puntuacion_contrato WHERE n_activados > 0) AS n_con_senales,
               (SELECT count(*) FROM organo) AS n_organos
        """,
    )[0]
    fila["n_concesiones"] = (
        con.execute("SELECT count(*) FROM concesion").fetchall()[0][0]
        if hay_subvenciones(con)
        else 0
    )
    return fila


def conteo_senales(con: duckdb.DuckDBPyConnection) -> dict[str, dict]:
    """Por indicador: contratos en los que se pudo comprobar y en los que salió la señal."""
    filas = _filas(
        con,
        """
        SELECT indicador, count(*) AS comprobados, count_if(activado) AS encontrados
        FROM indicador_resultado GROUP BY indicador ORDER BY indicador
        """,
    )
    return {f["indicador"]: f for f in filas}


def detalle_r01(con: duckdb.DuckDBPyConnection, contrato_id: str) -> dict | None:
    """E-01: ofertas de este contrato frente a cuántas reciben los contratos parecidos (mismo
    tipo de contrato, procedimientos con concurrencia)."""
    filas = _filas(
        con,
        """
        WITH ofertas AS (
            SELECT r.contrato_id, c.tipo_contrato, min(a.n_ofertas) AS n_ofertas
            FROM indicador_resultado AS r
            JOIN contrato_unico AS c USING (contrato_id)
            JOIN adjudicacion AS a USING (contrato_id)
            WHERE r.indicador = 'R-01' AND a.n_ofertas IS NOT NULL
            GROUP BY r.contrato_id, c.tipo_contrato
        ),
        este AS (SELECT * FROM ofertas WHERE contrato_id = ?),
        pares AS (
            SELECT o.n_ofertas FROM ofertas AS o
            JOIN este AS e ON o.tipo_contrato IS NOT DISTINCT FROM e.tipo_contrato
        )
        SELECT least(p.n_ofertas, 10) AS n_ofertas, count(*) AS n_contratos,
               (SELECT n_ofertas FROM este) AS ofertas_este,
               (SELECT tipo_contrato FROM este) AS tipo,
               (SELECT median(n_ofertas) FROM pares) AS mediana
        FROM pares AS p
        GROUP BY 1 ORDER BY 1
        """,
        [contrato_id],
    )
    if not filas:
        return None
    return {
        "ofertas": filas[0]["ofertas_este"],
        "tipo": filas[0]["tipo"],
        "mediana": filas[0]["mediana"],
        "distribucion": [(f["n_ofertas"], f["n_contratos"]) for f in filas],
    }


def detalle_r02(con: duckdb.DuckDBPyConnection, contrato_id: str) -> dict | None:
    """E-02: qué parte del importe del organismo (en contratos comprobados por R-02, misma
    fuente) se adjudicó sin anuncio público."""
    filas = _filas(
        con,
        """
        WITH base AS (
            SELECT c.contrato_id, c.organo_id, c.fuente, r.activado,
                   coalesce(sum(coalesce(a.importe_sin_iva, a.importe_con_iva)), 0) AS importe
            FROM indicador_resultado AS r
            JOIN contrato_unico AS c USING (contrato_id)
            LEFT JOIN adjudicacion AS a USING (contrato_id)
            WHERE r.indicador = 'R-02'
            GROUP BY ALL
        ),
        este AS (SELECT * FROM base WHERE contrato_id = ?)
        SELECT o.nombre AS organo, b.fuente,
               coalesce(sum(b.importe) FILTER (WHERE b.activado), 0) AS sin_anuncio,
               coalesce(sum(b.importe) FILTER (WHERE NOT b.activado), 0) AS con_anuncio,
               count_if(b.activado) AS n_sin_anuncio, count(*) AS n_contratos,
               any_value(e.importe) AS importe_este
        FROM base AS b
        JOIN este AS e ON b.organo_id = e.organo_id AND b.fuente = e.fuente
        JOIN organo AS o ON o.organo_id = b.organo_id
        GROUP BY o.nombre, b.fuente
        """,
        [contrato_id],
    )
    return filas[0] if filas else None


def detalle_r03(con: duckdb.DuckDBPyConnection, contrato_id: str) -> dict | None:
    """E-03: contratos menores de la misma empresa, organismo y tipo en los 12 meses que
    rodean a este, con el límite legal (con IVA). Personas físicas: sin nombre (D-007)."""
    filas = _filas(
        con,
        f"""
        WITH este AS (
            SELECT c.organo_id, c.tipo_contrato, c.fecha_contrato, a.adjudicatario_id,
                   CASE WHEN c.tipo_contrato = 'obras' THEN 48400 ELSE 18150 END AS umbral
            FROM contrato_unico AS c JOIN adjudicacion AS a USING (contrato_id)
            WHERE c.contrato_id = ? AND c.es_menor AND a.adjudicatario_id IS NOT NULL
            LIMIT 1
        )
        SELECT c.contrato_id, c.fecha_contrato AS fecha, a.importe_con_iva AS importe,
               c.titulo, c.url_origen, e.umbral,
               CASE WHEN {_beneficiario_visible("d")} THEN d.nombre END AS empresa
        FROM este AS e
        JOIN contrato_unico AS c
          ON c.organo_id = e.organo_id AND c.tipo_contrato = e.tipo_contrato AND c.es_menor
         AND c.fecha_contrato BETWEEN e.fecha_contrato - INTERVAL 364 DAYS
                                  AND e.fecha_contrato + INTERVAL 364 DAYS
        JOIN adjudicacion AS a
          ON a.contrato_id = c.contrato_id AND a.adjudicatario_id = e.adjudicatario_id
        JOIN adjudicatario AS d ON d.adjudicatario_id = a.adjudicatario_id
        WHERE a.importe_con_iva >= e.umbral / 3
        ORDER BY c.fecha_contrato
        """,
        [contrato_id],
    )
    if not filas:
        return None
    return {"umbral": filas[0]["umbral"], "empresa": filas[0]["empresa"], "contratos": filas}


def detalle_r04(con: duckdb.DuckDBPyConnection, contrato_id: str) -> dict | None:
    """E-04: reparto del importe del organismo en este tipo de contrato (misma fuente): la
    empresa de este contrato frente a las 4 siguientes y el resto. Personas físicas y
    adjudicatarios sin ficha, sin nombre (D-007)."""
    filas = _filas(
        con,
        f"""
        WITH este AS (
            SELECT c.fuente, c.organo_id, c.tipo_contrato, a.adjudicatario_id
            FROM contrato_unico AS c JOIN adjudicacion AS a USING (contrato_id)
            WHERE c.contrato_id = ? AND a.adjudicatario_id IS NOT NULL
            ORDER BY coalesce(a.importe_sin_iva, a.importe_con_iva) DESC NULLS LAST
            LIMIT 1
        ),
        mercado AS (
            SELECT a.adjudicatario_id,
                   sum(coalesce(a.importe_sin_iva, a.importe_con_iva)) AS importe
            FROM este AS e
            JOIN contrato_unico AS c
              ON c.fuente = e.fuente AND c.organo_id = e.organo_id
             AND c.tipo_contrato = e.tipo_contrato
            JOIN adjudicacion AS a USING (contrato_id)
            WHERE a.adjudicatario_id IS NOT NULL
              AND (a.resultado IS NULL OR a.resultado IN ('Adjudicado', 'Formalizado'))
            GROUP BY a.adjudicatario_id
            HAVING sum(coalesce(a.importe_sin_iva, a.importe_con_iva)) > 0
        )
        SELECT m.importe, m.adjudicatario_id = e.adjudicatario_id AS es_este,
               CASE WHEN {_beneficiario_visible("d")} THEN d.nombre END AS empresa,
               e.fuente, e.tipo_contrato, o.nombre AS organo
        FROM mercado AS m
        CROSS JOIN este AS e
        JOIN adjudicatario AS d ON d.adjudicatario_id = m.adjudicatario_id
        JOIN organo AS o ON o.organo_id = e.organo_id
        ORDER BY m.importe DESC
        """,
        [contrato_id],
    )
    if not filas:
        return None
    total = sum(f["importe"] for f in filas)
    este = next((f for f in filas if f["es_este"]), None)
    otros = [f for f in filas if not f["es_este"]]
    partes = []
    if este:
        partes.append(
            {
                "nombre": este["empresa"] or "Adjudicataria de este contrato",
                "importe": este["importe"],
                "es_este": True,
            }
        )
    for f in otros[:4]:
        partes.append(
            {
                "nombre": f["empresa"] or "Otra adjudicataria",
                "importe": f["importe"],
                "es_este": False,
            }
        )
    resto = sum(f["importe"] for f in otros[4:])
    if resto > 0:
        partes.append(
            {"nombre": f"Otras {len(otros) - 4} empresas", "importe": resto, "es_este": False}
        )
    return {
        "organo": filas[0]["organo"],
        "tipo": filas[0]["tipo_contrato"],
        "fuente": filas[0]["fuente"],
        "total": total,
        "cuota": este["importe"] / total if este and total else None,
        "n_empresas": len(filas),
        "partes": partes,
    }


def detalle_importes(con: duckdb.DuckDBPyConnection, contrato_id: str) -> dict | None:
    """E-05 y E-06: presupuesto de salida, importe adjudicado, modificaciones y prórrogas del
    contrato, en la base de IVA de su fuente."""
    filas = _filas(
        con,
        """
        SELECT c.fuente,
               any_value(CASE WHEN c.fuente = 'placsp' THEN c.presupuesto_sin_iva
                              ELSE c.presupuesto_con_iva END) AS presupuesto,
               sum(CASE WHEN c.fuente = 'placsp' THEN a.importe_sin_iva
                        ELSE a.importe_con_iva END) AS adjudicado,
               sum(a.importe_modificaciones_con_iva) AS modificaciones,
               sum(a.importe_prorrogas_con_iva) AS prorrogas
        FROM contrato_unico AS c JOIN adjudicacion AS a USING (contrato_id)
        WHERE c.contrato_id = ?
        GROUP BY c.fuente
        """,
        [contrato_id],
    )
    return filas[0] if filas else None


def reparto_empresa(con: duckdb.DuckDBPyConnection, adjudicatario_id: str) -> list[dict]:
    """A-05: importe recibido por la empresa de cada organismo, por fuente (cada fuente tiene
    su base de IVA y no se suman entre sí): contratos de PLACSP (sin IVA), del portal
    regional (con IVA) y subvenciones de la BDNS."""
    subvenciones = (
        """
        UNION ALL
        SELECT 'bdns' AS fuente, o.nombre AS organo, sum(s.importe) AS importe, count(*) AS n
        FROM concesion AS s JOIN organo AS o USING (organo_id)
        WHERE s.beneficiario_id = ? AND s.importe > 0
        GROUP BY o.nombre
        """
        if hay_subvenciones(con)
        else ""
    )
    parametros = [adjudicatario_id] + ([adjudicatario_id] if subvenciones else [])
    return _filas(
        con,
        f"""
        SELECT * FROM (
            SELECT c.fuente, o.nombre AS organo,
                   sum(CASE WHEN c.fuente = 'placsp' THEN a.importe_sin_iva
                            ELSE a.importe_con_iva END) AS importe,
                   count(DISTINCT c.contrato_id) AS n
            FROM adjudicacion AS a
            JOIN contrato_unico AS c USING (contrato_id)
            JOIN organo AS o USING (organo_id)
            WHERE a.adjudicatario_id = ?
            GROUP BY c.fuente, o.nombre
            {subvenciones}
        )
        WHERE importe > 0
        ORDER BY fuente, importe DESC
        """,
        parametros,
    )


def senales_empresa(con: duckdb.DuckDBPyConnection, adjudicatario_id: str) -> list[dict]:
    """A-05: en cuántos contratos de la empresa se encontró cada señal."""
    return _filas(
        con,
        """
        SELECT r.indicador, count(DISTINCT r.contrato_id) AS n
        FROM indicador_resultado AS r
        JOIN adjudicacion AS a USING (contrato_id)
        WHERE a.adjudicatario_id = ? AND r.activado
        GROUP BY r.indicador ORDER BY r.indicador
        """,
        [adjudicatario_id],
    )


def reparto_organo(con: duckdb.DuckDBPyConnection, organo_id: str) -> list[dict]:
    """A-06: importe que el organismo ha adjudicado (o concedido) a cada empresa o entidad, por
    fuente y sin mezclar bases de IVA. Personas físicas y adjudicatarios sin ficha, en una
    sola fila agregada (D-007)."""
    visible = _beneficiario_visible("d")
    subvenciones = (
        f"""
        UNION ALL
        SELECT 'bdns' AS fuente,
               CASE WHEN {visible} THEN d.nombre ELSE '{AGREGADO_PERSONAS}' END AS nombre,
               sum(s.importe) AS importe, count(*) AS n
        FROM concesion AS s JOIN adjudicatario AS d ON d.adjudicatario_id = s.beneficiario_id
        WHERE s.organo_id = ? AND s.importe > 0
        GROUP BY 1, 2
        """
        if hay_subvenciones(con)
        else ""
    )
    parametros = [organo_id] + ([organo_id] if subvenciones else [])
    return _filas(
        con,
        f"""
        SELECT * FROM (
            SELECT c.fuente,
                   CASE WHEN {visible} THEN d.nombre ELSE '{AGREGADO_PERSONAS}' END AS nombre,
                   sum(CASE WHEN c.fuente = 'placsp' THEN a.importe_sin_iva
                            ELSE a.importe_con_iva END) AS importe,
                   count(DISTINCT c.contrato_id) AS n
            FROM contrato_unico AS c
            JOIN adjudicacion AS a USING (contrato_id)
            JOIN adjudicatario AS d ON d.adjudicatario_id = a.adjudicatario_id
            WHERE c.organo_id = ?
            GROUP BY 1, 2
            {subvenciones}
        )
        WHERE importe > 0
        ORDER BY fuente, importe DESC
        """,
        parametros,
    )


def totales_organos(
    con: duckdb.DuckDBPyConnection,
    fuente: str,
    incluir_menores: bool = False,
    anio: int | None = None,
    tipo_contrato: str | None = None,
    limite: int = 15,
) -> list[dict]:
    """A-07: organismos que más han adjudicado (o concedido, si `fuente` es «bdns»), con los
    mismos filtros que los flujos. Una fuente cada vez (bases de IVA distintas)."""
    if fuente == "bdns":
        if not hay_subvenciones(con):
            return []
        return _filas(
            con,
            """
            SELECT s.organo_id, o.nombre AS organo, sum(s.importe) AS importe,
                   count(*) AS n_contratos
            FROM concesion AS s JOIN organo AS o USING (organo_id)
            WHERE (? IS NULL OR year(s.fecha_concesion) = ?) AND s.importe > 0
            GROUP BY ALL ORDER BY importe DESC LIMIT ?
            """,
            [anio, anio, limite],
        )
    campo = "a.importe_sin_iva" if fuente == "placsp" else "a.importe_con_iva"
    return _filas(
        con,
        f"""
        SELECT c.organo_id, o.nombre AS organo, sum({campo}) AS importe,
               count(DISTINCT c.contrato_id) AS n_contratos
        FROM adjudicacion AS a
        JOIN contrato_unico AS c USING (contrato_id)
        JOIN organo AS o USING (organo_id)
        JOIN adjudicatario AS d USING (adjudicatario_id)
        WHERE {_FILTRO_FLUJO} AND {campo} > 0
        GROUP BY ALL ORDER BY importe DESC LIMIT ?
        """,
        [*_parametros_flujo(fuente, incluir_menores, anio, tipo_contrato), limite],
    )


def pares_anomalia(
    con: duckdb.DuckDBPyConnection, contrato_id: str, muestra: int = 1500
) -> dict | None:
    """E-07: valores de un contrato atípico y de una muestra fija de sus contratos similares
    (mismo grupo), para dibujarlo frente a ellos. None si la base no tiene la tabla."""
    existe = con.execute(
        "SELECT count(*) FROM duckdb_tables() WHERE table_name = 'anomalia_variables'"
    ).fetchall()[0][0]
    if not existe:
        return None
    este = _filas(con, "SELECT * FROM anomalia_variables WHERE contrato_id = ?", [contrato_id])
    if not este:
        return None
    pares = _filas(
        con,
        f"""
        SELECT * FROM (
            SELECT * FROM anomalia_variables WHERE grupo = ? AND contrato_id <> ?
        )
        USING SAMPLE reservoir({int(muestra)} ROWS) REPEATABLE (42)
        """,
        [este[0]["grupo"], contrato_id],
    )
    return {"este": este[0], "pares": pares}


def _hay_tabla(con: duckdb.DuckDBPyConnection, tabla: str) -> bool:
    return bool(
        con.execute(
            "SELECT count(*) FROM duckdb_tables() WHERE table_name = ?", [tabla]
        ).fetchall()[0][0]
    )


def encargos_atipicos(con: duckdb.DuckDBPyConnection, limite: int = 50) -> list[dict]:
    """Encargos a medios propios atípicos frente a otros encargos (D-031), del más alejado al
    menos. Los medios propios son entidades públicas: se muestran con su nombre."""
    if not (_hay_tabla(con, "anomalia_encargo") and _hay_tabla(con, "encargo")):
        return []
    return _filas(
        con,
        """
        WITH e AS (
            SELECT encargo_id, any_value(titulo) AS titulo, any_value(organo_id) AS organo_id,
                   arg_min(medio_propio_id, orden) AS medio_propio_id,
                   sum(importe_con_iva) AS importe_con_iva, any_value(anio_publicacion) AS anio,
                   max(fecha_descarga) AS fecha_descarga
            FROM encargo GROUP BY encargo_id
        )
        SELECT r.encargo_id, e.titulo, o.nombre AS organo, m.nombre AS medio_propio,
               e.importe_con_iva, e.anio, r.puntuacion, r.motivo, r.n_grupo, r.url_origen,
               e.fecha_descarga
        FROM anomalia_encargo AS r
        JOIN e USING (encargo_id)
        LEFT JOIN organo AS o USING (organo_id)
        LEFT JOIN adjudicatario AS m ON m.adjudicatario_id = e.medio_propio_id
        WHERE r.atipico
        ORDER BY r.puntuacion DESC
        LIMIT ?
        """,
        [limite],
    )


def validacion_anomalias(con: duckdb.DuckDBPyConnection) -> list[dict]:
    """Proporción de atípicos con y sin recursos estimados ante el TACPCM y con y sin fondos
    europeos (D-031). Descriptiva: con pocos casos no prueba nada."""
    if not _hay_tabla(con, "anomalia_validacion"):
        return []
    return _filas(con, "SELECT * FROM anomalia_validacion")
