"""Consultas de los datos añadidos el 23-nov: encargos a medios propios (D-028), fondos
europeos de cada licitación (D-027) y recursos ante el Tribunal de Contratación (D-029).

Como `app.datos`, solo leen y devuelven listas de diccionarios. Las tablas pueden no existir en
una base antigua: `hay_tabla` lo comprueba y las pantallas no muestran el bloque. Ninguno de
estos datos es una señal de riesgo. Los medios propios que sean personas físicas solo se
muestran sumados (D-007).
"""

import duckdb

from ojo_ciudadano.app.datos import AGREGADO_PERSONAS, _beneficiario_visible, _filas

NOMBRE_PROGRAMA_UE = {
    "PRTR": "Plan de Recuperación, Transformación y Resiliencia",
    "FEDER": "Fondo Europeo de Desarrollo Regional",
    "FSE+": "Fondo Social Europeo Plus",
    "FEADER": "Fondo Europeo Agrícola de Desarrollo Rural",
    "OFE": "otros fondos europeos",
}


def hay_tabla(con: duckdb.DuckDBPyConnection, nombre: str) -> bool:
    """La tabla existe y tiene filas."""
    existe = con.execute(
        "SELECT count(*) FROM information_schema.tables WHERE table_name = ?", [nombre]
    ).fetchone()[0]
    return bool(existe) and con.execute(f"SELECT count(*) > 0 FROM {nombre}").fetchone()[0]


def encargos_organo(con: duckdb.DuckDBPyConnection, organo_id: str) -> dict | None:
    """Resumen y lista de los encargos de un órgano (None si no tiene)."""
    if not hay_tabla(con, "encargo"):
        return None
    lista = _filas(
        con,
        f"""
        SELECT e.titulo, e.anio_publicacion AS anio, e.importe_con_iva AS importe, e.url_origen,
               CASE WHEN a.adjudicatario_id IS NULL THEN 'Sin medio propio en la fuente'
                    WHEN {_beneficiario_visible("a")} THEN a.nombre
                    ELSE '{AGREGADO_PERSONAS}' END AS medio_propio
        FROM encargo e LEFT JOIN adjudicatario a ON a.adjudicatario_id = e.medio_propio_id
        WHERE e.organo_id = ?
        ORDER BY e.importe_con_iva DESC NULLS LAST
        """,
        [organo_id],
    )
    if not lista:
        return None
    por_medio: dict[str, float] = {}
    for e in lista:
        por_medio[e["medio_propio"]] = por_medio.get(e["medio_propio"], 0) + (e["importe"] or 0)
    return {
        "n_encargos": len({e["url_origen"] for e in lista}),
        "importe": sum(e["importe"] or 0 for e in lista),
        "por_medio_propio": sorted(por_medio.items(), key=lambda x: x[1], reverse=True),
        "lista": lista,
        "fecha_descarga": _fecha_descarga(con, "encargo"),
    }


def encargos_empresa(con: duckdb.DuckDBPyConnection, adjudicatario_id: str) -> dict | None:
    """Encargos recibidos por una entidad como medio propio, por órgano (None si no tiene)."""
    if not hay_tabla(con, "encargo"):
        return None
    por_organo = _filas(
        con,
        """
        SELECT o.nombre AS organo, count(DISTINCT e.encargo_id) AS n_encargos,
               sum(e.importe_con_iva) AS importe
        FROM encargo e JOIN organo o USING (organo_id)
        WHERE e.medio_propio_id = ?
        GROUP BY 1 ORDER BY importe DESC NULLS LAST
        """,
        [adjudicatario_id],
    )
    if not por_organo:
        return None
    return {
        "n_encargos": sum(o["n_encargos"] for o in por_organo),
        "importe": sum(o["importe"] or 0 for o in por_organo),
        "por_organo": por_organo,
        "fecha_descarga": _fecha_descarga(con, "encargo"),
    }


def financiacion_contrato(con: duckdb.DuckDBPyConnection, contrato_id: str) -> dict | None:
    """Fondos europeos de una licitación de PLACSP (o de la que duplica una fila del portal)."""
    if not hay_tabla(con, "contrato_financiacion"):
        return None
    filas = _filas(
        con,
        """
        SELECT f.financiado_ue, f.programas_ue, f.url_origen
        FROM contrato c
        JOIN contrato_financiacion f ON f.contrato_id = coalesce(c.duplicado_de, c.contrato_id)
        WHERE c.contrato_id = ?
        """,
        [contrato_id],
    )
    return filas[0] if filas else None


def recursos_contrato(con: duckdb.DuckDBPyConnection, contrato_id: str) -> list[dict]:
    """Resoluciones del Tribunal enlazadas con el contrato (o con su fila de PLACSP)."""
    if not hay_tabla(con, "recurso_especial"):
        return []
    return _filas(
        con,
        """
        SELECT r.numero, r.fecha, r.tipo_resolucion, r.acto_recurrido, r.url_origen,
               r.fecha_descarga, r.expediente_citado
        FROM contrato c
        JOIN recurso_especial r ON r.contrato_id IN (c.contrato_id, c.duplicado_de)
        WHERE c.contrato_id = ?
        ORDER BY r.fecha
        """,
        [contrato_id],
    )


def pliegos_contrato(con: duckdb.DuckDBPyConnection, contrato_id: str) -> list[dict]:
    """Pliegos que enlaza PLACSP para el contrato o para su fila de PLACSP (D-030, bloque B)."""
    if not hay_tabla(con, "contrato_documento"):
        return []
    return _filas(
        con,
        """
        SELECT d.contrato_id, d.tipo, d.url_documento, d.fecha_descarga
        FROM contrato c
        JOIN contrato_documento d ON d.contrato_id = coalesce(c.duplicado_de, c.contrato_id)
        WHERE c.contrato_id = ?
        ORDER BY d.orden
        """,
        [contrato_id],
    )


def cpv_contrato(con: duckdb.DuckDBPyConnection, contrato_id: str) -> dict | None:
    """Código CPV del contrato (o de su fila de PLACSP) con su nombre oficial (D-035)."""
    if not hay_tabla(con, "cpv"):
        return None
    filas = _filas(
        con,
        """
        SELECT coalesce(c.cpv, p.cpv) AS codigo, v.nombre, v.nombre_division, v.fecha_descarga
        FROM contrato c
        LEFT JOIN contrato p ON p.contrato_id = c.duplicado_de
        JOIN cpv v ON v.codigo = coalesce(c.cpv, p.cpv)
        WHERE c.contrato_id = ?
        """,
        [contrato_id],
    )
    return filas[0] if filas else None


def sector_publico(con: duckdb.DuckDBPyConnection, nif: str | None, nombre: str | None):
    """El ente del sector público (INVENTE, D-035) con ese NIF, si lo hay, y si su nombre se
    parece al del adjudicatario (`nombre_compatible`)."""
    from ojo_ciudadano.ingesta.invente import nombres_compatibles

    if not nif or not hay_tabla(con, "entidad_sector_publico"):
        return None
    filas = _filas(
        con,
        "SELECT nombre, forma_juridica, administracion, fecha_descarga, url_origen "
        "FROM entidad_sector_publico WHERE nif = ?",
        [nif],
    )
    if not filas:
        return None
    return {**filas[0], "nombre_compatible": nombres_compatibles(nombre, filas[0]["nombre"])}


def resumen_recursos(con: duckdb.DuckDBPyConnection) -> list[dict]:
    """Resoluciones por acto recurrido y resultado, para el contexto general."""
    if not hay_tabla(con, "recurso_especial"):
        return []
    return _filas(
        con,
        """
        SELECT acto_recurrido,
               count(*) AS n,
               count(*) FILTER (WHERE tipo_resolucion IN ('Estimatoria', 'Estimatoria parcial'))
                   AS estimadas,
               count(*) FILTER (WHERE tipo_resolucion = 'Desestimatoria') AS desestimadas,
               count(*) FILTER (WHERE tipo_resolucion = 'Inadmisión') AS inadmitidas,
               min(fecha) AS desde, max(fecha) AS hasta, max(fecha_descarga) AS fecha_descarga
        FROM recurso_especial
        WHERE acto_recurrido IN ('Pliegos', 'Exclusión', 'Adjudicación')
        GROUP BY 1 ORDER BY n DESC
        """,
    )


def resumen_encargos(con: duckdb.DuckDBPyConnection) -> dict | None:
    """Encargos de toda la Comunidad por año, por medio propio y por órgano."""
    if not hay_tabla(con, "encargo"):
        return None
    por_anio = _filas(
        con,
        """
        SELECT anio_publicacion AS anio, count(DISTINCT encargo_id) AS n_encargos,
               sum(importe_con_iva) AS importe
        FROM encargo GROUP BY 1 ORDER BY 1
        """,
    )
    por_medio = _filas(
        con,
        f"""
        SELECT CASE WHEN a.adjudicatario_id IS NULL THEN 'Sin medio propio en la fuente'
                    WHEN {_beneficiario_visible("a")} THEN a.nombre
                    ELSE '{AGREGADO_PERSONAS}' END AS medio_propio,
               count(DISTINCT e.encargo_id) AS n_encargos, sum(e.importe_con_iva) AS importe
        FROM encargo e LEFT JOIN adjudicatario a ON a.adjudicatario_id = e.medio_propio_id
        GROUP BY 1 ORDER BY importe DESC NULLS LAST LIMIT 15
        """,
    )
    por_organo = _filas(
        con,
        """
        SELECT o.nombre AS organo, count(DISTINCT e.encargo_id) AS n_encargos,
               sum(e.importe_con_iva) AS importe
        FROM encargo e JOIN organo o USING (organo_id)
        GROUP BY 1 ORDER BY importe DESC NULLS LAST LIMIT 15
        """,
    )
    return {
        "por_anio": por_anio,
        "por_medio_propio": por_medio,
        "por_organo": por_organo,
        "fecha_descarga": _fecha_descarga(con, "encargo"),
    }


def _fecha_descarga(con: duckdb.DuckDBPyConnection, tabla: str):
    return con.execute(f"SELECT max(fecha_descarga) FROM {tabla}").fetchone()[0]
