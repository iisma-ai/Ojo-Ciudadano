SQL = "r06_baja_anormal_o_nula.sql"


def licitacion(base, cid, presupuesto, adjudicado, ofertas=3, **campos):
    base.contrato(
        cid,
        [{"importe_sin_iva": adjudicado, "n_ofertas": ofertas, "resultado": "Formalizado"}],
        procedimiento=campos.pop("procedimiento", "Abierto"),
        presupuesto_sin_iva=presupuesto,
        **campos,
    )


def test_sin_baja_activa(base):
    licitacion(base, "c1", 1000, 1000)
    fila = base.resultado(SQL)["c1"]
    assert fila["activado"] is True
    assert fila["valor"] == 0
    assert "sin baja" in fila["motivo"]


def test_adjudicar_por_encima_del_presupuesto_activa(base):
    licitacion(base, "c1", 1000, 1100)
    assert base.resultado(SQL)["c1"]["activado"] is True


def test_baja_extrema_activa(base):
    licitacion(base, "c1", 1000, 400)
    fila = base.resultado(SQL)["c1"]
    assert fila["activado"] is True
    assert fila["motivo"] == "Baja del 60,0 % sobre el presupuesto base"


def test_baja_normal_no_activa(base):
    licitacion(base, "c1", 1000, 800)
    fila = base.resultado(SQL)["c1"]
    assert fila["activado"] is False
    assert fila["motivo"] is None


def test_limites(base):
    licitacion(base, "justo_nula", 1000, 995)  # baja 0,5 %: activa
    licitacion(base, "casi_nula", 1000, 994)  # baja 0,6 %: no
    licitacion(base, "justo_extrema", 1000, 500)  # baja 50 %: activa
    licitacion(base, "casi_extrema", 1000, 501)  # baja 49,9 %: no
    r = base.resultado(SQL)
    assert [
        r[k]["activado"] for k in ("justo_nula", "casi_nula", "justo_extrema", "casi_extrema")
    ] == [
        True,
        False,
        True,
        False,
    ]


def test_no_aplicable(base):
    licitacion(base, "una_oferta", 1000, 1000, ofertas=1)
    licitacion(base, "sin_ofertas", 1000, 1000, ofertas=None)
    licitacion(base, "negociado", 1000, 1000, procedimiento="Negociado sin publicidad")
    licitacion(base, "sin_presupuesto", None, 1000)
    licitacion(base, "menor", 1000, 1000, es_menor=True)
    base.contrato(
        "lote_desierto",
        [
            {"importe_sin_iva": 500, "n_ofertas": 3, "resultado": "Formalizado"},
            {"importe_sin_iva": None, "n_ofertas": 0, "resultado": "Desierto"},
        ],
        procedimiento="Abierto",
        presupuesto_sin_iva=1000,
    )
    assert base.resultado(SQL) == {}


def test_lotes_suman_el_adjudicado(base):
    lotes = [
        {"importe_sin_iva": 400, "n_ofertas": 2, "resultado": "Formalizado"},
        {"importe_sin_iva": 400, "n_ofertas": 5, "resultado": "Formalizado"},
    ]
    base.contrato("c1", lotes, procedimiento="Abierto", presupuesto_sin_iva=1000)
    fila = base.resultado(SQL)["c1"]
    assert fila["valor"] == 0.2
    assert fila["activado"] is False


def test_portal_usa_importes_con_iva(base):
    base.contrato(
        "p1",
        [{"importe_con_iva": 1210, "n_ofertas": 3}],
        fuente="portal_cm",
        procedimiento="Abierto",
        presupuesto_con_iva=1210,
    )
    assert base.resultado(SQL)["p1"]["activado"] is True
