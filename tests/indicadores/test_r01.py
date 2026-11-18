SQL = "r01_licitador_unico.sql"


def test_una_oferta_en_procedimiento_abierto_activa(base):
    base.contrato("c1", [{"n_ofertas": 1, "resultado": "Formalizado"}], procedimiento="Abierto")
    fila = base.resultado(SQL)["c1"]
    assert fila["aplicable"] is True
    assert fila["activado"] is True
    assert fila["valor"] == 1
    assert fila["motivo"] == "Se recibió una sola oferta en un procedimiento abierto"
    assert fila["url_origen"] == "https://ejemplo.test/c1"


def test_dos_ofertas_no_activa(base):
    base.contrato("c1", [{"n_ofertas": 2, "resultado": "Adjudicado"}], procedimiento="Abierto")
    fila = base.resultado(SQL)["c1"]
    assert fila["activado"] is False
    assert fila["motivo"] is None


def test_lotes_cuenta_los_de_una_oferta(base):
    lotes = [
        {"n_ofertas": 1, "resultado": "Formalizado"},
        {"n_ofertas": 4, "resultado": "Formalizado"},
        {"n_ofertas": 1, "resultado": "Formalizado"},
    ]
    base.contrato("c1", lotes, procedimiento="Abierto simplificado")
    fila = base.resultado(SQL)["c1"]
    assert fila["activado"] is True
    assert fila["valor"] == 2
    assert "en 2 de 3 lotes" in fila["motivo"]


def test_no_aplicable_sin_datos_o_fuera_de_procedimiento(base):
    base.contrato("negociado", [{"n_ofertas": 1}], procedimiento="Negociado sin publicidad")
    base.contrato("menor", [{"n_ofertas": 1}], procedimiento="Contrato menor", es_menor=True)
    base.contrato("sin_ofertas", [{"n_ofertas": None}], procedimiento="Abierto")
    base.contrato("cero", [{"n_ofertas": 0, "resultado": "Formalizado"}], procedimiento="Abierto")
    base.contrato("desierto", [{"n_ofertas": 1, "resultado": "Desierto"}], procedimiento="Abierto")
    assert base.resultado(SQL) == {}


def test_lote_desierto_no_cuenta(base):
    lotes = [
        {"n_ofertas": 1, "resultado": "Desierto"},
        {"n_ofertas": 3, "resultado": "Formalizado"},
    ]
    base.contrato("c1", lotes, procedimiento="Abierto")
    fila = base.resultado(SQL)["c1"]
    assert fila["activado"] is False


def test_el_duplicado_del_portal_no_se_cuenta_dos_veces(base):
    base.contrato(
        "placsp:1", [{"n_ofertas": 1, "resultado": "Formalizado"}], procedimiento="Abierto"
    )
    base.contrato(
        "portal_cm:X",
        [{"n_ofertas": 1}],
        fuente="portal_cm",
        procedimiento="Abierto",
        duplicado_de="placsp:1",
    )
    assert list(base.resultado(SQL)) == ["placsp:1"]


def test_licitacion_solo_en_el_portal(base):
    base.contrato("portal_cm:Y", [{"n_ofertas": 1}], fuente="portal_cm", procedimiento="Abierto")
    assert base.resultado(SQL)["portal_cm:Y"]["activado"] is True
