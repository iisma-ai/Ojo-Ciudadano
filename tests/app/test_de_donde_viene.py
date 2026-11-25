"""«¿De dónde viene el dinero?» (D-054): consultas de ingresos y cuentas de la pantalla.

Todo con filas sintéticas en una base en memoria; nada depende de lo descargado.
"""

from datetime import date

import duckdb

from ojo_ciudadano.app import datos_contexto as dc
from ojo_ciudadano.app import de_donde_viene as dv

HOY = date(2026, 11, 23)
URL = "https://datos.comunidad.madrid/dataset/x"


def _base() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute(
        """CREATE TABLE serie_cm (serie_id VARCHAR, serie VARCHAR, anio INTEGER,
        concepto VARCHAR, dimension VARCHAR, valor DOUBLE, unidad VARCHAR, valor_eur DOUBLE,
        estado_dato VARCHAR, fuente VARCHAR, url_origen VARCHAR, fecha_descarga DATE)"""
    )
    return con


def _fila(con, serie, anio, concepto, valor, dimension=None) -> None:
    con.execute(
        "INSERT INTO serie_cm VALUES (?, 'S', ?, ?, ?, ?, 'Euros', ?, NULL, 'ckan_cm', ?, ?)",
        [serie, anio, concepto, dimension, valor, valor, URL, HOY],
    )


def test_ingresos_iniciales_por_capitulo_sin_totales():
    con = _base()
    s = dc.SERIE_INGRESOS_INICIALES
    _fila(con, s, 2026, "Ingresos consolidados por impuestos directos de los presupuestos", 60.0)
    _fila(con, s, 2026, "Ingresos consolidados por pasivos financieros de los presupuestos", 30.0)
    _fila(con, s, 2026, "Ingresos consolidados por transferencias corrientes de los presup.", -10.0)
    _fila(con, s, 2026, "Total ingresos consolidados de los presupuestos", 80.0)
    _fila(con, s, 2026, "Ingresos consolidados por el total de operaciones corrientes", 50.0)
    ingresos = dc.ingresos_del_anio(con, 2026)
    assert not ingresos["liquidado"]
    assert {c["capitulo"] for c in ingresos["capitulos"]} == {
        "directos",
        "pasivos",
        "transferencias_corrientes",
    }
    assert ingresos["total"] == 80.0
    entradas, saldo = dv.entradas_y_saldo(ingresos)
    assert entradas == {"directos": 60.0, "pasivos": 30.0}
    assert saldo == -10.0


def test_con_el_anio_cerrado_usa_derechos_reconocidos_y_lo_previsto():
    con = _base()
    s = dc.SERIE_INGRESOS_LIQUIDADOS
    concepto = "Ingresos consolidados por impuestos indirectos en la fase de {} de los presup."
    _fila(con, s, 2025, concepto.format("derechos"), 90.0, "Derechos reconocidos")
    _fila(con, s, 2025, concepto.format("previsión"), 100.0, "Previsión actual")
    _fila(con, s, 2025, concepto.format("recaudación"), 85.0, "Recaudación líquida")
    _fila(
        con,
        s,
        2025,
        "Ingresos consolidados patrimoniales en la fase de derechos reconocidos",
        5.0,
        "Derechos reconocidos",
    )
    ingresos = dc.ingresos_del_anio(con, 2025)
    assert ingresos["liquidado"]
    indirectos = next(c for c in ingresos["capitulos"] if c["capitulo"] == "indirectos")
    assert (indirectos["importe"], indirectos["previsto"]) == (90.0, 100.0)
    assert ingresos["total"] == 95.0
    assert ingresos["url_origen"] == URL
    # la burbuja se llena hasta lo que entró frente a lo previsto
    nodos, _ = dv.grafo(ingresos, dv.entradas_y_saldo(ingresos)[0])
    assert next(n for n in nodos if n.id == "indirectos").llenado == 0.9


def test_sin_datos_del_anio_no_hay_capitulos():
    ingresos = dc.ingresos_del_anio(_base(), 2030)
    assert ingresos["capitulos"] == [] and ingresos["url_origen"] is None


def test_de_cada_100_suma_100_y_respeta_el_peso():
    partes = dv.de_cada_100({"a": 49.6, "b": 38.6, "c": 8.2, "d": 3.6})
    assert sum(partes.values()) == 100
    assert partes["a"] > partes["b"] > partes["c"] > partes["d"]
    assert dv.de_cada_100({"a": 0.0}) == {"a": 0}


def test_barra_agrupa_el_resto_y_lo_explica_en_una_frase():
    entradas = {"directos": 50.0, "indirectos": 39.0, "pasivos": 8.0, "tasas": 2.0, "activos": 1.0}
    grupos = dv.grupos_barra(entradas)
    assert grupos["resto"] == 3.0
    ingresos = {"anio": 2026, "liquidado": False, "capitulos": []}
    html = dv.barra_entradas(ingresos, entradas)
    assert "De cada 100 € que entran" in html
    assert "<b>50</b> impuestos directos" in html


def test_sistema_de_financiacion_del_ultimo_anio_publicado():
    con = _base()
    s = dc.SERIE_SISTEMA_FINANCIACION
    for anio, garantia in ((2022, -5.0), (2023, -6.0)):
        _fila(
            con,
            s,
            anio,
            "Transferencia del Fondo de Garantía de Servicios Públicos Fundamentales para la "
            "financiación de la Comunidad de Madrid",
            garantia,
        )
    _fila(con, s, 2023, "Fondo de suficiencia global para la financiación", -1.0)
    sistema = dc.sistema_financiacion(con, 2026)
    assert (sistema["anio"], sistema["garantia"], sistema["suficiencia"]) == (2023, -6.0, -1.0)
    assert dc.sistema_financiacion(con, 2021) is None


def test_ayudas_ue_del_ultimo_anio_publicado():
    con = _base()
    s = dc.SERIE_AYUDAS_UE
    _fila(con, s, 2023, "Total ayudas procedentes del presupuesto general de la UE", 300.0)
    _fila(con, s, 2023, "Ayudas del Fondo Social Europeo procedentes del presupuesto", 230.0)
    ue = dc.ayudas_ue(con, 2026)
    assert (ue["anio"], ue["total"], ue["fse"]) == (2023, 300.0, 230.0)
