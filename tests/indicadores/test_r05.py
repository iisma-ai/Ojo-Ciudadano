import pytest

SQL = "r05_sobrecoste_modificaciones.sql"


def _licitacion(base, contrato_id, adjudicado, modificaciones, prorrogas=0.0, **campos):
    base.contrato(
        contrato_id,
        [
            {
                "importe_con_iva": adjudicado,
                "importe_modificaciones_con_iva": modificaciones,
                "importe_prorrogas_con_iva": prorrogas,
            }
        ],
        fuente="portal_cm",
        procedimiento="Abierto",
        **campos,
    )


def test_modificaciones_por_encima_del_20_por_ciento_activan(base):
    _licitacion(base, "portal_cm:A", 100000.0, 25000.0, prorrogas=100000.0)
    fila = base.resultado(SQL)["portal_cm:A"]
    assert fila["activado"] is True
    assert fila["valor"] == pytest.approx(0.25)
    assert fila["motivo"] == (
        "Las modificaciones (25.000,00 € con IVA) suponen el 25,0 % del importe adjudicado "
        "(100.000,00 € con IVA); referencia: 20 %, límite de las modificaciones previstas en "
        "la LCSP. Prórrogas, no incluidas en el cálculo: 100.000,00 €"
    )
    assert fila["url_origen"] == "https://ejemplo.test/portal_cm:A"


def test_justo_el_20_por_ciento_no_activa(base):
    _licitacion(base, "portal_cm:A", 100000.0, 20000.0)
    fila = base.resultado(SQL)["portal_cm:A"]
    assert fila["activado"] is False
    assert fila["motivo"] is None


def test_las_prorrogas_no_cuentan(base):
    _licitacion(base, "portal_cm:A", 100000.0, 0.0, prorrogas=300000.0)
    fila = base.resultado(SQL)["portal_cm:A"]
    assert fila["aplicable"] is True
    assert fila["activado"] is False
    assert fila["valor"] == 0


def test_suma_los_lotes(base):
    lotes = [
        {"importe_con_iva": 50000.0, "importe_modificaciones_con_iva": 15000.0},
        {"importe_con_iva": 50000.0, "importe_modificaciones_con_iva": 0.0},
    ]
    base.contrato("portal_cm:A", lotes, fuente="portal_cm", procedimiento="Abierto")
    fila = base.resultado(SQL)["portal_cm:A"]
    assert fila["valor"] == pytest.approx(0.15)
    assert fila["activado"] is False


def test_se_asigna_al_contrato_de_placsp_si_esta_duplicado(base):
    base.contrato("placsp:1", [{"n_ofertas": 2}], procedimiento="Abierto")
    _licitacion(base, "portal_cm:A", 100000.0, 30000.0, duplicado_de="placsp:1")
    resultado = base.resultado(SQL)
    assert list(resultado) == ["placsp:1"]
    assert resultado["placsp:1"]["url_origen"] == "https://ejemplo.test/portal_cm:A"


def test_no_aplicable_sin_datos_menores_o_importe_cero(base):
    _licitacion(base, "sin_dato", 100000.0, None)
    _licitacion(base, "cero", 0.0, 5000.0)
    base.menor("menor", None, 1000.0)
    base.contrato("placsp:2", [{"importe_sin_iva": 1000.0}])
    assert base.resultado(SQL) == {}
