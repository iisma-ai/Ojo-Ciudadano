SQL = "r02_sin_publicidad.sql"
SIN_PUBLICIDAD = "Contratos adjudicados por procedimientos sin publicidad"


def test_negociado_sin_publicidad_activa(base):
    base.contrato("placsp:1", procedimiento="Negociado sin publicidad")
    fila = base.resultado(SQL)["placsp:1"]
    assert fila["aplicable"] is True
    assert fila["activado"] is True
    assert fila["valor"] is None
    assert fila["motivo"] == "Adjudicado por procedimiento negociado sin publicidad"


def test_abierto_no_activa(base):
    base.contrato("placsp:1", procedimiento="Abierto")
    fila = base.resultado(SQL)["placsp:1"]
    assert fila["activado"] is False
    assert fila["motivo"] is None


def test_otro_procedimiento_en_la_lista_sin_publicidad_del_portal(base):
    base.contrato(
        "portal_cm:E",
        fuente="portal_cm",
        procedimiento="Otro procedimiento",
        tipo_publicacion=SIN_PUBLICIDAD,
    )
    base.contrato(
        "portal_cm:F",
        fuente="portal_cm",
        procedimiento="Otro procedimiento",
        tipo_publicacion="Convocatoria anunciada a licitación",
    )
    resultado = base.resultado(SQL)
    assert resultado["portal_cm:E"]["activado"] is True
    assert "emergencia" in resultado["portal_cm:E"]["motivo"]
    assert resultado["portal_cm:F"]["activado"] is False


def test_mira_la_ficha_del_portal_del_duplicado(base):
    base.contrato("placsp:1", procedimiento="Otros")
    base.contrato(
        "portal_cm:E",
        fuente="portal_cm",
        procedimiento="Otro procedimiento",
        tipo_publicacion=SIN_PUBLICIDAD,
        duplicado_de="placsp:1",
    )
    resultado = base.resultado(SQL)
    assert list(resultado) == ["placsp:1"]
    assert resultado["placsp:1"]["activado"] is True
    assert resultado["placsp:1"]["url_origen"] == "https://ejemplo.test/placsp:1"


def test_no_aplicable_menores_derivados_y_sin_procedimiento(base):
    base.menor("menor", None, 100.0)
    base.contrato("am", procedimiento="Derivado de acuerdo marco")
    base.contrato("sda", procedimiento="Basado en un sistema dinámico de adquisición")
    base.contrato("sin")
    assert base.resultado(SQL) == {}
