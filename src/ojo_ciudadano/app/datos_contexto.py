"""Consultas del contexto de la Comunidad de Madrid (D-024): presupuesto, convenios, registros.

Como `app.datos`, solo leen y devuelven listas de diccionarios. Las tablas nuevas pueden no
existir en una base antigua: `hay_contexto` lo comprueba y las pantallas lo avisan.
Personas físicas: ninguna de estas tablas las contiene (D-007).
"""

import duckdb

from ojo_ciudadano.app import cache
from ojo_ciudadano.normalizacion import texto as n_texto

TABLAS = ("serie_cm", "presupuesto_organo", "convenio", "entidad_registro", "plantilla_organismo")
SERIE_GASTOS_CAPITULO = "presupuestos_liquidados_gastos_consolidados_por_capitulo_y_fase_ejecucion"
SERIE_GASTOS_INICIALES = "1502013"
SERIE_INGRESOS_INICIALES = "1502012"
SERIE_PERSONAL = "personal_comunidad_madrid_por_area_actividad_y_sexo"
NOMBRE_REGISTRO = {
    "transparencia": "Registro de transparencia (grupos de interés)",
    "fundaciones": "Registro de fundaciones",
    "cooperativas": "Registro de cooperativas",
}


def _filas(con: duckdb.DuckDBPyConnection, sql: str, parametros: list | None = None) -> list[dict]:
    """Filas como diccionarios; en la web salen de la caché (app/cache.py)."""
    return cache.filas(con, sql, parametros)


def hay_contexto(con: duckdb.DuckDBPyConnection) -> bool:
    """Las cinco tablas existen y tienen filas (la base se cargó con `modelo.contexto`)."""
    existentes = {
        f[0]
        for f in con.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
        ).fetchall()
    }
    if not set(TABLAS) <= existentes:
        return False
    return con.execute("SELECT count(*) FROM presupuesto_organo").fetchone()[0] > 0


def fechas_contexto(con: duckdb.DuckDBPyConnection) -> list[dict]:
    """Fecha de descarga de cada fuente del contexto (vacío si la base no lo tiene)."""
    if not hay_contexto(con):
        return []
    return _filas(
        con,
        """
        SELECT fuente, max(fecha_descarga) AS fecha FROM (
            SELECT fuente, fecha_descarga FROM serie_cm
            UNION ALL SELECT fuente, fecha_descarga FROM convenio
        ) GROUP BY fuente ORDER BY fuente
        """,
    )


def anios_liquidados(con: duckdb.DuckDBPyConnection) -> list[int]:
    """Años con presupuesto liquidado por consejería, del más reciente al más antiguo."""
    filas = con.execute(
        "SELECT DISTINCT anio FROM presupuesto_organo WHERE tipo = 'liquidado' "
        "AND organo_id IS NOT NULL AND anio >= 2015 ORDER BY anio DESC"
    ).fetchall()
    return [f[0] for f in filas]


def _consejeria_de(con: duckdb.DuckDBPyConnection) -> dict[str, str]:
    """organo_id → organo_id de su consejería (o el propio si es una consejería)."""
    ids = {f[0] for f in con.execute("SELECT organo_id FROM organo").fetchall()}
    resultado = {}
    for organo_id, consejeria in con.execute("SELECT organo_id, consejeria FROM organo").fetchall():
        clave = n_texto.clave(consejeria)
        resultado[organo_id] = clave if clave in ids else organo_id
    return resultado


def _importes_por_consejeria(con: duckdb.DuckDBPyConnection) -> dict[tuple[str, int], dict]:
    """Contratos (Plataforma sin IVA, portal con IVA) y subvenciones por consejería y año."""
    destino = _consejeria_de(con)
    acumulado: dict[tuple[str, int], dict] = {}

    def sumar(organo_id: str, anio: int | None, campo: str, importe: float | None) -> None:
        if anio is None or importe is None:
            return
        entrada = acumulado.setdefault(
            (destino.get(organo_id, organo_id), int(anio)),
            {"plataforma": 0.0, "portal": 0.0, "subvenciones": 0.0},
        )
        entrada[campo] += importe

    for organo_id, anio, fuente, importe in con.execute(
        """
        SELECT c.organo_id, year(coalesce(c.fecha_contrato, a.fecha_formalizacion)), c.fuente,
               sum(coalesce(a.importe_sin_iva, a.importe_con_iva))
        FROM contrato_unico AS c JOIN adjudicacion AS a USING (contrato_id)
        GROUP BY 1, 2, 3
        """
    ).fetchall():
        sumar(organo_id, anio, "plataforma" if fuente == "placsp" else "portal", importe)
    for organo_id, anio, importe in con.execute(
        "SELECT organo_id, year(fecha_concesion), sum(importe) FROM concesion GROUP BY 1, 2"
    ).fetchall():
        sumar(organo_id, anio, "subvenciones", importe)
    return acumulado


def ejecucion_consejerias(con: duckdb.DuckDBPyConnection, anio: int) -> list[dict]:
    """Por consejería y año: lo presupuestado, lo ejecutado y lo que pasó por contratos y
    subvenciones de sus órganos. Las cifras son de fuentes distintas y no se restan."""
    presupuesto = _filas(
        con,
        """
        SELECT organo_id, any_value(entidad) AS consejeria,
               max(importe_eur) FILTER (WHERE tipo = 'inicial') AS inicial,
               max(importe_eur) FILTER (WHERE fase = 'Crédito actual') AS credito_actual,
               max(importe_eur) FILTER (WHERE fase = 'Obligaciones reconocidas') AS obligaciones,
               max(importe_eur) FILTER (WHERE fase = 'Pagos realizados') AS pagos,
               any_value(url_origen) FILTER (WHERE tipo = 'liquidado') AS url_origen,
               max(fecha_descarga) AS fecha_descarga
        FROM presupuesto_organo
        WHERE anio = ? AND organo_id IS NOT NULL AND organo_id LIKE 'CONSEJERIA%'
        GROUP BY organo_id
        ORDER BY obligaciones DESC NULLS LAST
        """,
        [anio],
    )
    importes = _importes_por_consejeria(con)
    for fila in presupuesto:
        extra = importes.get((fila["organo_id"], anio), {})
        fila["contratos_plataforma"] = extra.get("plataforma")
        fila["contratos_portal"] = extra.get("portal")
        fila["subvenciones"] = extra.get("subvenciones")
    return presupuesto


def ejecucion_organo(con: duckdb.DuckDBPyConnection, organo_id: str) -> list[dict]:
    """Presupuesto liquidado de una consejería, año a año (vacío si el órgano no lo tiene)."""
    return _filas(
        con,
        """
        SELECT anio,
               max(importe_eur) FILTER (WHERE fase = 'Crédito actual') AS credito_actual,
               max(importe_eur) FILTER (WHERE fase = 'Obligaciones reconocidas') AS obligaciones,
               max(importe_eur) FILTER (WHERE fase = 'Pagos realizados') AS pagos,
               any_value(url_origen) AS url_origen
        FROM presupuesto_organo
        WHERE organo_id = ? AND tipo = 'liquidado'
        GROUP BY anio HAVING max(importe_eur) FILTER (WHERE fase = 'Obligaciones reconocidas') > 0
        ORDER BY anio
        """,
        [organo_id],
    )


def gasto_por_capitulo(con: duckdb.DuckDBPyConnection, desde: int = 2008) -> list[dict]:
    """Obligaciones reconocidas por capítulo y año (presupuestos liquidados consolidados)."""
    return _filas(
        con,
        """
        SELECT * FROM (
            SELECT anio,
                   CASE
                     WHEN concepto ILIKE 'Gastos de personal%' THEN 'Personal'
                     WHEN concepto ILIKE '%bienes y servicios%' THEN 'Bienes y servicios'
                     WHEN concepto ILIKE 'Gastos financieros%' THEN 'Gastos financieros'
                     WHEN concepto ILIKE '%transferencias corrientes%'
                         THEN 'Transferencias corrientes'
                     WHEN concepto ILIKE '%inversiones reales%' THEN 'Inversiones reales'
                     WHEN concepto ILIKE '%transferencias de capital%'
                         THEN 'Transferencias de capital'
                     WHEN concepto ILIKE '%activos financieros%' THEN 'Activos financieros'
                     WHEN concepto ILIKE '%pasivos financieros%' THEN 'Pasivos financieros'
                   END AS capitulo,
                   valor_eur AS importe, url_origen, fecha_descarga
            FROM serie_cm
            WHERE serie_id = ? AND dimension = 'Obligaciones reconocidas' AND anio >= ?
              AND valor_eur IS NOT NULL AND valor_eur > 0
        ) WHERE capitulo IS NOT NULL
        ORDER BY anio, capitulo
        """,
        [SERIE_GASTOS_CAPITULO, desde],
    )


def gastos_e_ingresos_iniciales(con: duckdb.DuckDBPyConnection, desde: int = 2008) -> list[dict]:
    """Total de gastos y de ingresos de los presupuestos iniciales, por año."""
    return _filas(
        con,
        """
        SELECT anio,
               max(valor_eur) FILTER (
                   WHERE serie_id = ? AND concepto ILIKE 'Total gastos%') AS gastos,
               max(valor_eur) FILTER (
                   WHERE serie_id = ? AND concepto ILIKE 'Total ingresos%') AS ingresos,
               any_value(url_origen) FILTER (WHERE serie_id = ?) AS url_origen
        FROM serie_cm
        WHERE serie_id IN (?, ?) AND anio >= ?
        GROUP BY anio HAVING gastos IS NOT NULL ORDER BY anio
        """,
        [
            SERIE_GASTOS_INICIALES,
            SERIE_INGRESOS_INICIALES,
            SERIE_GASTOS_INICIALES,
            SERIE_GASTOS_INICIALES,
            SERIE_INGRESOS_INICIALES,
            desde,
        ],
    )


def ingresos_por_capitulo(con: duckdb.DuckDBPyConnection, anio: int) -> list[dict]:
    """Ingresos iniciales por capítulo de un año (impuestos, tasas, transferencias…)."""
    return _filas(
        con,
        """
        SELECT regexp_extract(concepto, 'Ingresos consolidados por (.+?) de los presupuestos', 1)
                 AS capitulo,
               valor_eur AS importe, url_origen, fecha_descarga
        FROM serie_cm
        WHERE serie_id = ? AND anio = ? AND concepto ILIKE 'Ingresos consolidados por%'
          AND concepto NOT ILIKE '%el total de%' AND valor_eur > 0
        ORDER BY importe DESC
        """,
        [SERIE_INGRESOS_INICIALES, anio],
    )


def personal_por_area(con: duckdb.DuckDBPyConnection) -> list[dict]:
    """Personal al servicio de la Comunidad por área, último año disponible."""
    return _filas(
        con,
        """
        SELECT anio, concepto, valor AS personas, url_origen, fecha_descarga
        FROM serie_cm
        WHERE serie_id = ? AND concepto ILIKE 'Personal al servicio%'
          AND anio = (SELECT max(anio) FROM serie_cm WHERE serie_id = ?)
        ORDER BY valor DESC
        """,
        [SERIE_PERSONAL, SERIE_PERSONAL],
    )


def plantilla(con: duckdb.DuckDBPyConnection) -> list[dict]:
    """Puestos de la relación de puestos de trabajo (funcionarios) por organismo."""
    return _filas(
        con,
        "SELECT organismo, n_puestos, url_origen, fecha_descarga FROM plantilla_organismo "
        "ORDER BY n_puestos DESC",
    )


def convenios_por_consejeria(con: duckdb.DuckDBPyConnection) -> list[dict]:
    """Convenios vigentes por consejería y año de firma (desde 2019)."""
    return _filas(
        con,
        """
        SELECT consejeria, year(fecha_firma) AS anio, count(*) AS n,
               count(*) FILTER (WHERE con_financiacion) AS n_con_financiacion
        FROM convenio
        WHERE year(fecha_firma) >= 2019
        GROUP BY 1, 2 ORDER BY 1, 2
        """,
    )


def lista_convenios(
    con: duckdb.DuckDBPyConnection,
    consejeria: str | None = None,
    texto: str = "",
    solo_con_financiacion: bool = False,
    limite: int = 50,
) -> list[dict]:
    """Convenios vigentes, más recientes primero, con filtros."""
    condiciones, parametros = ["1 = 1"], []
    if consejeria:
        condiciones.append("consejeria = ?")
        parametros.append(consejeria)
    if texto.strip():
        condiciones.append("(titulo ILIKE '%' || ? || '%' OR entidades ILIKE '%' || ? || '%')")
        parametros += [texto.strip(), texto.strip()]
    if solo_con_financiacion:
        condiciones.append("con_financiacion")
    parametros.append(limite)
    return _filas(
        con,
        f"""
        SELECT referencia, consejeria, titulo, fecha_firma, vigencia_hasta, indefinido,
               entidad_cm, entidades, n_firmantes, financiacion, con_financiacion,
               url_origen, fecha_descarga
        FROM convenio WHERE {" AND ".join(condiciones)}
        ORDER BY fecha_firma DESC NULLS LAST LIMIT ?
        """,
        parametros,
    )


def consejerias_con_convenios(con: duckdb.DuckDBPyConnection) -> list[str]:
    return [
        f[0] for f in con.execute("SELECT DISTINCT consejeria FROM convenio ORDER BY 1").fetchall()
    ]


def empresas_en_registros(con: duckdb.DuckDBPyConnection) -> list[dict]:
    """Por registro: cuántas de nuestras empresas adjudicatarias o beneficiarias están inscritas."""
    return _filas(
        con,
        """
        SELECT e.registro, count(DISTINCT e.nif) AS n_entidades,
               count(DISTINCT a.adjudicatario_id) AS n_con_contratos,
               any_value(e.url_origen) AS url_origen, max(e.fecha_descarga) AS fecha_descarga
        FROM entidad_registro AS e LEFT JOIN adjudicatario AS a ON a.nif = e.nif
        GROUP BY e.registro ORDER BY e.registro
        """,
    )


def entidades_registradas_con_contratos(
    con: duckdb.DuckDBPyConnection, registro: str, limite: int = 30
) -> list[dict]:
    """Entidades de un registro con más importe adjudicado (importe de la Plataforma, sin IVA)."""
    return _filas(
        con,
        """
        SELECT a.adjudicatario_id, a.nombre, a.nif, e.detalle, e.estado,
               count(DISTINCT ad.contrato_id) AS n_contratos,
               sum(ad.importe_sin_iva) AS importe_sin_iva, e.url_origen
        FROM entidad_registro AS e
        JOIN adjudicatario AS a ON a.nif = e.nif
        JOIN adjudicacion AS ad ON ad.adjudicatario_id = a.adjudicatario_id
        WHERE e.registro = ?
        GROUP BY a.adjudicatario_id, a.nombre, a.nif, e.detalle, e.estado, e.url_origen
        ORDER BY importe_sin_iva DESC NULLS LAST LIMIT ?
        """,
        [registro, limite],
    )


def registros_de_empresa(con: duckdb.DuckDBPyConnection, nif: str | None) -> list[dict]:
    """En qué registros de la Comunidad figura una empresa (por NIF)."""
    if not nif:
        return []
    return _filas(
        con,
        "SELECT registro, detalle, estado, url_origen, fecha_descarga FROM entidad_registro "
        "WHERE nif = ? ORDER BY registro",
        [nif],
    )
