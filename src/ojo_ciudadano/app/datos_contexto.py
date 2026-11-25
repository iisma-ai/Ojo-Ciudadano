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


# ------------------------------------------------------------ de dónde viene el dinero (D-054)
SERIE_INGRESOS_LIQUIDADOS = (
    "presupuestos_liquidados_ingresos_consolidados_por_capitulo_y_fase_ejecucion"
)
SERIE_SISTEMA_FINANCIACION = "1902613"
SERIE_AYUDAS_UE = "1902617"
# capítulo de ingresos a partir del texto del concepto (las dos series lo escriben distinto)
_CAPITULO_INGRESO = """
    CASE WHEN concepto ILIKE '%total%' THEN NULL
         WHEN concepto ILIKE '%impuestos directos%' THEN 'directos'
         WHEN concepto ILIKE '%impuestos indirectos%' THEN 'indirectos'
         WHEN concepto ILIKE '%tasas%' THEN 'tasas'
         WHEN concepto ILIKE '%transferencias corrientes%' THEN 'transferencias_corrientes'
         WHEN concepto ILIKE '%patrimoniales%' THEN 'patrimoniales'
         WHEN concepto ILIKE '%enajenaci%' THEN 'enajenacion'
         WHEN concepto ILIKE '%transferencias de capital%' THEN 'transferencias_capital'
         WHEN concepto ILIKE '%activos financieros%' THEN 'activos'
         WHEN concepto ILIKE '%pasivos financieros%' THEN 'pasivos'
    END
"""


def ingresos_del_anio(con: duckdb.DuckDBPyConnection, anio: int) -> dict:
    """Ingresos consolidados de la Comunidad en un año, por capítulo.

    Con el año cerrado: lo que entró (derechos reconocidos, como «gastado» son las obligaciones
    reconocidas) y lo previsto (previsión actual). Si no, el presupuesto inicial. Las
    transferencias corrientes pueden salir en negativo: es un saldo (ver D-054)."""
    liquidados = _filas(
        con,
        f"""
        SELECT capitulo,
               max(valor_eur) FILTER (WHERE dimension = 'Derechos reconocidos') AS importe,
               max(valor_eur) FILTER (WHERE dimension = 'Previsión actual') AS previsto,
               any_value(url_origen) AS url_origen, max(fecha_descarga) AS fecha_descarga
        FROM (SELECT {_CAPITULO_INGRESO} AS capitulo, * FROM serie_cm
              WHERE serie_id = ? AND anio = ?)
        WHERE capitulo IS NOT NULL GROUP BY capitulo
        """,
        [SERIE_INGRESOS_LIQUIDADOS, anio],
    )
    liquidado = any(f["importe"] is not None for f in liquidados)
    if liquidado:
        capitulos = [f for f in liquidados if f["importe"] is not None]
    else:
        capitulos = _filas(
            con,
            f"""
            SELECT capitulo, max(valor_eur) AS importe, NULL AS previsto,
                   any_value(url_origen) AS url_origen, max(fecha_descarga) AS fecha_descarga
            FROM (SELECT {_CAPITULO_INGRESO} AS capitulo, * FROM serie_cm
                  WHERE serie_id = ? AND anio = ?)
            WHERE capitulo IS NOT NULL AND valor_eur IS NOT NULL GROUP BY capitulo
            """,
            [SERIE_INGRESOS_INICIALES, anio],
        )
    capitulos = sorted(capitulos, key=lambda f: -(f["importe"] or 0))
    return {
        "anio": anio,
        "liquidado": liquidado,
        "capitulos": capitulos,
        "total": sum(f["importe"] or 0 for f in capitulos),
        "url_origen": capitulos[0]["url_origen"] if capitulos else None,
        "fecha_descarga": capitulos[0]["fecha_descarga"] if capitulos else None,
    }


def sistema_financiacion(con: duckdb.DuckDBPyConnection, anio: int) -> dict | None:
    """Saldo de la Comunidad con los fondos del sistema de financiación autonómica, del último año
    publicado hasta `anio` (la serie llega con unos años de retraso)."""
    filas = _filas(
        con,
        """
        WITH ultimo AS (SELECT max(anio) AS anio FROM serie_cm
                        WHERE serie_id = ? AND anio <= ? AND valor_eur IS NOT NULL)
        SELECT s.anio,
               max(valor_eur) FILTER (WHERE concepto ILIKE '%Fondo de Garant%') AS garantia,
               max(valor_eur) FILTER (WHERE concepto ILIKE '%suficiencia%') AS suficiencia,
               max(valor_eur) FILTER (WHERE concepto ILIKE 'Recaudación del  IVA%'
                                         OR concepto ILIKE 'Recaudación del IVA%') AS iva,
               max(valor_eur) FILTER (WHERE concepto ILIKE 'Tarifa autonómica del IRPF%') AS irpf,
               any_value(url_origen) AS url_origen, max(fecha_descarga) AS fecha_descarga
        FROM serie_cm s JOIN ultimo u ON s.anio = u.anio
        WHERE serie_id = ? GROUP BY s.anio
        """,
        [SERIE_SISTEMA_FINANCIACION, anio, SERIE_SISTEMA_FINANCIACION],
    )
    return filas[0] if filas and filas[0]["garantia"] is not None else None


def ayudas_ue(con: duckdb.DuckDBPyConnection, anio: int) -> dict | None:
    """Ayudas del presupuesto de la Unión Europea a la Comunidad, del último año publicado hasta
    `anio`: el total y el fondo que más aporta."""
    filas = _filas(
        con,
        """
        WITH ultimo AS (SELECT max(anio) AS anio FROM serie_cm
                        WHERE serie_id = ? AND anio <= ? AND valor_eur IS NOT NULL)
        SELECT s.anio,
               max(valor_eur) FILTER (WHERE concepto ILIKE 'Total ayudas procedentes%') AS total,
               max(valor_eur) FILTER (WHERE concepto ILIKE '%Fondo Social Europeo%') AS fse,
               any_value(url_origen) AS url_origen, max(fecha_descarga) AS fecha_descarga
        FROM serie_cm s JOIN ultimo u ON s.anio = u.anio
        WHERE serie_id = ? GROUP BY s.anio
        """,
        [SERIE_AYUDAS_UE, anio, SERIE_AYUDAS_UE],
    )
    return filas[0] if filas and filas[0]["total"] is not None else None


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
