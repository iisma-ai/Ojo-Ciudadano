"""Consultas del mapa general del dinero de la Comunidad de Madrid (D-026).

Mismo criterio que `app.datos`: solo leen y devuelven listas de diccionarios. El presupuesto
(crédito, gasto reconocido) y los contratos y subvenciones vienen de fuentes distintas y no se
cruzan partida a partida: aquí se comparan por consejería y año, y la pantalla lo dice.
Personas físicas: sus nombres no salen nunca (D-007).
"""

import duckdb

from ojo_ciudadano.app import datos_contexto
from ojo_ciudadano.app.datos import AGREGADO_PERSONAS, _beneficiario_visible, _filas

PRIMER_ANIO = 2015
LIMITE_CONTRATOS = 15

# Nombres de los adjudicatarios, en orden fijo (si cambiara entre ejecuciones, Streamlit vería un
# mapa nuevo y perdería el clic) y sin personas físicas: esas salen agregadas (D-007).
_NOMBRES_VISIBLES = f"""
    array_to_string(
        list_sort(list_distinct(list(
            CASE WHEN {_beneficiario_visible("d")} THEN d.nombre ELSE '{AGREGADO_PERSONAS}' END
        ))), ' ; ')
"""


def periodos(con: duckdb.DuckDBPyConnection) -> list[dict]:
    """Años que se pueden ver, del más reciente al más antiguo. `liquidado` es que ya hay gasto
    reconocido (presupuesto liquidado); si no, solo el presupuesto inicial."""
    liquidados = {
        f[0]
        for f in con.execute(
            "SELECT DISTINCT anio FROM presupuesto_organo WHERE tipo = 'liquidado' AND anio >= ?",
            [PRIMER_ANIO],
        ).fetchall()
    }
    iniciales = {
        f[0]
        for f in con.execute(
            "SELECT DISTINCT anio FROM presupuesto_organo WHERE tipo = 'inicial' AND anio >= ?",
            [PRIMER_ANIO],
        ).fetchall()
    }
    return [
        {"anio": a, "liquidado": a in liquidados}
        for a in sorted(liquidados | iniciales, reverse=True)
    ]


def _importes_por_consejeria(con: duckdb.DuckDBPyConnection, anio: int) -> dict[str, dict]:
    """Contratos (Plataforma sin IVA y portal con IVA) y subvenciones de cada consejería en el
    año, con el número de cada uno."""
    destino = datos_contexto._consejeria_de(con)
    acumulado: dict[str, dict] = {}

    def sumar(organo_id: str, campo: str, importe: float | None, cuenta: int) -> None:
        fila = acumulado.setdefault(
            destino.get(organo_id, organo_id),
            {"plataforma": 0.0, "n_plataforma": 0, "portal": 0.0, "n_portal": 0,
             "subvenciones": 0.0, "n_subvenciones": 0},
        )  # fmt: skip
        fila[campo] += importe or 0.0
        fila["n_" + campo] += cuenta

    for organo_id, fuente, importe, cuenta in con.execute(
        """
        SELECT c.organo_id, c.fuente, sum(coalesce(a.importe_sin_iva, a.importe_con_iva)),
               count(DISTINCT c.contrato_id)
        FROM contrato_unico AS c JOIN adjudicacion AS a USING (contrato_id)
        WHERE year(coalesce(c.fecha_contrato, a.fecha_formalizacion)) = ?
        GROUP BY 1, 2
        """,
        [anio],
    ).fetchall():
        sumar(organo_id, "plataforma" if fuente == "placsp" else "portal", importe, cuenta)
    for organo_id, importe, cuenta in con.execute(
        "SELECT organo_id, sum(importe), count(*) FROM concesion "
        "WHERE year(fecha_concesion) = ? GROUP BY 1",
        [anio],
    ).fetchall():
        sumar(organo_id, "subvenciones", importe, cuenta)
    return acumulado


def reparto(con: duckdb.DuckDBPyConnection, anio: int) -> dict:
    """Dinero de la Comunidad en un año, repartido entre sus consejerías y órganos.

    Devuelve `entidades` (crédito, gasto reconocido, pagos, % gastado y lo que se contrató o
    subvencionó) y los totales. Con presupuesto liquidado, `credito` es el crédito actual; sin
    él (año en curso), el presupuesto inicial y sin gasto reconocido (`gastado` es None)."""
    liquidado = bool(
        con.execute(
            "SELECT count(*) FROM presupuesto_organo WHERE tipo = 'liquidado' AND anio = ?",
            [anio],
        ).fetchone()[0]
    )
    filas = _filas(
        con,
        """
        SELECT entidad, any_value(organo_id) AS organo_id,
               max(importe_eur) FILTER (WHERE tipo = 'inicial') AS inicial,
               max(importe_eur) FILTER (WHERE fase = 'Crédito actual') AS credito_actual,
               max(importe_eur) FILTER (WHERE fase = 'Obligaciones reconocidas') AS gastado,
               max(importe_eur) FILTER (WHERE fase = 'Pagos realizados') AS pagado,
               any_value(url_origen) FILTER (WHERE tipo = 'liquidado') AS url_liquidado,
               any_value(url_origen) FILTER (WHERE tipo = 'inicial') AS url_inicial,
               max(fecha_descarga) AS fecha_descarga
        FROM presupuesto_organo WHERE anio = ?
        GROUP BY lower(entidad), entidad
        """,
        [anio],
    )
    importes = _importes_por_consejeria(con, anio)
    entidades = []
    for f in filas:
        credito = f["credito_actual"] if liquidado else f["inicial"]
        if not credito or credito <= 0:
            continue
        gastado = f["gastado"] if liquidado else None
        extra = importes.get(f["organo_id"] or "", {})
        entidades.append(
            {
                **f,
                "credito": credito,
                "gastado": gastado,
                "llenado": (min(gastado / credito, 1.0) if gastado is not None else None),
                "sin_gastar": (max(credito - gastado, 0.0) if gastado is not None else None),
                "contratos_plataforma": extra.get("plataforma"),
                "n_plataforma": extra.get("n_plataforma", 0),
                "contratos_portal": extra.get("portal"),
                "n_portal": extra.get("n_portal", 0),
                "subvenciones": extra.get("subvenciones"),
                "n_subvenciones": extra.get("n_subvenciones", 0),
                "url_origen": f["url_liquidado"] if liquidado else f["url_inicial"],
            }
        )
    entidades.sort(key=lambda e: e["credito"], reverse=True)
    total_credito = sum(e["credito"] for e in entidades)
    total_gastado = sum(e["gastado"] for e in entidades if e["gastado"] is not None)
    return {
        "anio": anio,
        "liquidado": liquidado,
        "entidades": entidades,
        "credito": total_credito,
        "gastado": total_gastado if liquidado else None,
        "pagado": sum(e["pagado"] or 0 for e in entidades) if liquidado else None,
        "url_origen": entidades[0]["url_origen"] if entidades else None,
        "fecha_descarga": max((e["fecha_descarga"] for e in entidades), default=None),
    }


def _organos_de(con: duckdb.DuckDBPyConnection, organo_id: str) -> list[str]:
    """Los órganos de una consejería: ella misma y los que dependen de ella."""
    return [o for o, c in datos_contexto._consejeria_de(con).items() if c == organo_id]


def contratos_consejeria(
    con: duckdb.DuckDBPyConnection, organo_id: str, anio: int, limite: int = LIMITE_CONTRATOS
) -> dict:
    """Los contratos más grandes de una consejería en un año (sin menores) y el resumen de
    los menores y las subvenciones. Importes: Plataforma sin IVA y portal con IVA, sin sumar."""
    organos = _organos_de(con, organo_id)
    if not organos:
        return {"contratos": [], "menores": None, "subvenciones": None, "n_organos": 0}
    contratos = _filas(
        con,
        f"""
        SELECT c.contrato_id, c.titulo, c.fuente, c.procedimiento, c.tipo_contrato,
               o.nombre AS organo, c.url_origen,
               sum(coalesce(a.importe_sin_iva, a.importe_con_iva)) AS importe,
               min(a.n_ofertas) AS n_ofertas,
               {_NOMBRES_VISIBLES} AS adjudicatarios
        FROM contrato_unico AS c
        JOIN adjudicacion AS a USING (contrato_id)
        JOIN organo AS o ON o.organo_id = c.organo_id
        LEFT JOIN adjudicatario AS d ON d.adjudicatario_id = a.adjudicatario_id
        WHERE list_contains(?, c.organo_id) AND NOT c.es_menor
          AND year(coalesce(c.fecha_contrato, a.fecha_formalizacion)) = ?
        GROUP BY c.contrato_id, c.titulo, c.fuente, c.procedimiento, c.tipo_contrato,
                 o.nombre, c.url_origen
        HAVING sum(coalesce(a.importe_sin_iva, a.importe_con_iva)) > 0
        ORDER BY importe DESC, c.contrato_id LIMIT ?
        """,
        [organos, anio, limite],
    )
    menores = _filas(
        con,
        """
        SELECT count(DISTINCT c.contrato_id) AS n, sum(a.importe_con_iva) AS importe
        FROM contrato_unico AS c JOIN adjudicacion AS a USING (contrato_id)
        WHERE list_contains(?, c.organo_id) AND c.es_menor
          AND year(coalesce(c.fecha_contrato, a.fecha_formalizacion)) = ?
        """,
        [organos, anio],
    )[0]
    subvenciones = {"n": 0, "importe": None}
    if con.execute(
        "SELECT count(*) FROM duckdb_tables() WHERE table_name = 'concesion'"
    ).fetchone()[0]:
        subvenciones = _filas(
            con,
            "SELECT count(*) AS n, sum(importe) AS importe FROM concesion "
            "WHERE list_contains(?, organo_id) AND year(fecha_concesion) = ?",
            [organos, anio],
        )[0]
    return {
        "contratos": contratos,
        "menores": menores if menores["n"] else None,
        "subvenciones": subvenciones if subvenciones["n"] else None,
        "n_organos": len(organos),
    }


def detalle_contrato(con: duckdb.DuckDBPyConnection, contrato_id: str) -> dict | None:
    """Lo que se sabe de un contrato: procedimiento, ofertas, presupuesto, adjudicatarias,
    fechas y enlace. Los adjudicatarios que son personas físicas no salen con nombre."""
    filas = _filas(
        con,
        f"""
        SELECT c.contrato_id, c.titulo, c.fuente, c.tipo_contrato, c.procedimiento, c.estado,
               c.presupuesto_sin_iva, c.presupuesto_con_iva, c.fecha_contrato, c.fecha_fin_plazo,
               c.url_origen, o.nombre AS organo, o.organo_id,
               sum(a.importe_sin_iva) AS importe_sin_iva, sum(a.importe_con_iva) AS importe_con_iva,
               min(a.n_ofertas) AS n_ofertas, max(a.fecha_formalizacion) AS fecha_formalizacion,
               {_NOMBRES_VISIBLES} AS adjudicatarios
        FROM contrato_unico AS c
        JOIN organo AS o ON o.organo_id = c.organo_id
        LEFT JOIN adjudicacion AS a ON a.contrato_id = c.contrato_id
        LEFT JOIN adjudicatario AS d ON d.adjudicatario_id = a.adjudicatario_id
        WHERE c.contrato_id = ?
        GROUP BY c.contrato_id, c.titulo, c.fuente, c.tipo_contrato, c.procedimiento, c.estado,
                 c.presupuesto_sin_iva, c.presupuesto_con_iva, c.fecha_contrato,
                 c.fecha_fin_plazo, c.url_origen, o.nombre, o.organo_id
        """,
        [contrato_id],
    )
    return filas[0] if filas else None
