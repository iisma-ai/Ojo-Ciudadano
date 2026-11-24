"""Mapa general del dinero (D-026): consultas y componente de nodos, con datos sintéticos."""

import base64
from datetime import date

from ojo_ciudadano.app import datos_mapa, red

URL = "https://datos.comunidad.madrid/dataset/x"
HOY = date(2026, 11, 23)


def _presupuesto(con):
    con.execute(
        "INSERT INTO organo (organo_id, nombre, consejeria) "
        "VALUES ('CONSEJERIA DE SANIDAD', 'Consejería de Sanidad', NULL)"
    )
    con.execute("UPDATE organo SET consejeria = 'Consejería de Sanidad' WHERE organo_id = 'ORG'")
    for fase, importe in (
        ("Crédito actual", 1000.0),
        ("Obligaciones reconocidas", 900.0),
        ("Pagos realizados", 800.0),
    ):
        con.execute(
            "INSERT INTO presupuesto_organo VALUES (2025, 'liquidado', ?, 'Consejería de Sanidad', "
            "'CONSEJERIA DE SANIDAD', ?, 'ckan_cm', ?, ?)",
            [fase, importe, URL, HOY],
        )
    con.execute(
        "INSERT INTO presupuesto_organo VALUES (2026, 'inicial', NULL, 'Consejería de Sanidad', "
        "'CONSEJERIA DE SANIDAD', 1100.0, 'ckan_cm', ?, ?)",
        [URL, HOY],
    )


def test_periodos_marcan_si_hay_gasto(base):
    _presupuesto(base.con)
    assert datos_mapa.periodos(base.con) == [
        {"anio": 2026, "liquidado": False},
        {"anio": 2025, "liquidado": True},
    ]


def test_reparto_con_gasto_y_sin_el(base):
    con = base.con
    _presupuesto(con)
    base.contrato(
        "c1",
        [{"adjudicatario_id": "A1", "importe_sin_iva": 100.0, "n_ofertas": 3}],
        titulo="Servicio",
        fecha_contrato=date(2025, 3, 1),
    )
    r = datos_mapa.reparto(con, 2025)
    sanidad = r["entidades"][0]
    assert r["liquidado"] and r["credito"] == 1000.0 and r["gastado"] == 900.0
    assert sanidad["llenado"] == 0.9 and sanidad["sin_gastar"] == 100.0
    assert sanidad["contratos_plataforma"] == 100.0  # el órgano ORG cuelga de la consejería
    inicial = datos_mapa.reparto(con, 2026)
    assert not inicial["liquidado"] and inicial["gastado"] is None
    assert inicial["entidades"][0]["llenado"] is None and inicial["credito"] == 1100.0


def test_contratos_de_una_consejeria_y_detalle(base):
    con = base.con
    _presupuesto(con)
    base.contrato(
        "c1",
        [{"adjudicatario_id": "A1", "importe_sin_iva": 100.0, "n_ofertas": 3}],
        titulo="Servicio",
        procedimiento="Abierto",
        fecha_contrato=date(2025, 3, 1),
    )
    base.contrato(
        "c2",
        [{"adjudicatario_id": "A2", "importe_sin_iva": 5000.0}],
        titulo="Grande",
        fecha_contrato=date(2025, 4, 1),
    )
    cuerpo = datos_mapa.contratos_consejeria(con, "CONSEJERIA DE SANIDAD", 2025)
    assert [c["contrato_id"] for c in cuerpo["contratos"]] == ["c2", "c1"]  # el mayor primero
    assert cuerpo["menores"] is None and cuerpo["n_organos"] == 2
    otro_anio = datos_mapa.contratos_consejeria(con, "CONSEJERIA DE SANIDAD", 2024)
    assert otro_anio["contratos"] == []
    detalle = datos_mapa.detalle_contrato(con, "c1")
    assert detalle["n_ofertas"] == 3 and detalle["procedimiento"] == "Abierto"
    assert datos_mapa.detalle_contrato(con, "no-existe") is None


def test_nodos_svg_y_texto():
    uri = red.svg_nodo("#3D8BFD", 0.5)
    assert uri.startswith("data:image/svg+xml;base64,")
    svg = base64.b64decode(uri.split(",", 1)[1]).decode()
    assert 'clip-path="url(#c)"' in svg  # la parte gastada va rellena hasta su nivel
    sin_dato = base64.b64decode(red.svg_nodo("#3D8BFD", None).split(",", 1)[1]).decode()
    assert "clip-path" not in sin_dato  # sin dato de gasto, toda del color
    assert red.envolver("Familia, Juventud y Asuntos Sociales", 18) == (
        "Familia, Juventud\ny Asuntos Sociales"
    )
    assert red.mapa([], []) is None


def test_contratos_principales_de_todas_las_consejerias(base):
    con = base.con
    _presupuesto(con)
    for n, importe in enumerate((100.0, 5000.0, 300.0), start=1):
        base.contrato(
            f"c{n}",
            [{"adjudicatario_id": f"A{n}", "importe_sin_iva": importe}],
            titulo=f"Contrato {n}",
            fecha_contrato=date(2025, 3, n),
        )
    base.contrato(
        "m1",
        [{"adjudicatario_id": "A9", "importe_con_iva": 40.0}],
        fuente="portal_cm",
        es_menor=True,
        fecha_contrato=date(2025, 5, 1),
    )
    top2 = datos_mapa.contratos_principales(con, 2025, 2)
    assert [c["contrato_id"] for c in top2["CONSEJERIA DE SANIDAD"]] == ["c2", "c3"]
    assert datos_mapa.contratos_principales(con, 2025, 0) == {}
    assert datos_mapa.contratos_principales(con, 2024, 3) == {}
    agrupados = datos_mapa.menores_y_subvenciones(con, 2025)
    assert agrupados["CONSEJERIA DE SANIDAD"]["menores"] == {"n": 1, "importe": 40.0}


def test_diseno_radial_cabe_en_el_lienzo():
    puntos = red.posiciones_radiales(8, 200)
    assert len(puntos) == 8
    assert all(abs(x) <= 200.01 and abs(y) <= 200.01 for x, y in puntos)
    assert round(sum(x for x, _ in puntos), 6) == 0  # repartidos por igual alrededor del centro
    assert red.alternar_tamanos([1, 2, 3, 4, 5]) == [1, 5, 2, 4, 3]
