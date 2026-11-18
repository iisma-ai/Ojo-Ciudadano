from datetime import date

SQL = "r03_posible_fraccionamiento.sql"


def test_dos_menores_que_suman_mas_del_umbral_activan(base):
    base.menor("m1", date(2025, 1, 10), 10000.0)
    base.menor("m2", date(2025, 6, 1), 9000.0)
    resultado = base.resultado(SQL)
    for contrato in ("m1", "m2"):
        assert resultado[contrato]["activado"] is True
        assert resultado[contrato]["valor"] == 19000.0
    assert resultado["m1"]["motivo"] == (
        "2 contratos menores con el mismo adjudicatario, órgano y tipo de contrato suman "
        "19.000,00 € con IVA en 12 meses (umbral de referencia: 18.150,00 € con IVA)"
    )


def test_en_el_umbral_no_activa_y_un_centimo_mas_si(base):
    base.menor("m1", date(2025, 1, 10), 9075.0)
    base.menor("m2", date(2025, 2, 10), 9075.0)
    base.menor("m3", date(2025, 1, 10), 9075.0, adjudicatario="B2")
    base.menor("m4", date(2025, 2, 10), 9075.01, adjudicatario="B2")
    resultado = base.resultado(SQL)
    assert resultado["m1"]["activado"] is False
    assert resultado["m2"]["activado"] is False
    assert resultado["m3"]["activado"] is True


def test_un_solo_menor_por_encima_no_activa(base):
    base.menor("m1", date(2025, 1, 10), 18149.0)
    base.menor("grande", date(2024, 1, 10), 25000.0, adjudicatario="B2")
    resultado = base.resultado(SQL)
    assert resultado["m1"]["activado"] is False
    assert resultado["grande"]["activado"] is False


def test_fuera_de_la_ventana_de_12_meses_no_activa(base):
    base.menor("m1", date(2025, 1, 10), 10000.0)
    base.menor("m2", date(2026, 1, 10), 10000.0)
    resultado = base.resultado(SQL)
    assert not resultado["m1"]["activado"]
    assert not resultado["m2"]["activado"]


def test_distinto_organo_adjudicatario_o_tipo_no_se_suman(base):
    base.menor("m1", date(2025, 1, 10), 10000.0)
    base.menor("m2", date(2025, 2, 10), 10000.0, organo_id="OTRO")
    base.menor("m3", date(2025, 3, 10), 10000.0, adjudicatario="B2")
    base.menor("m4", date(2025, 4, 10), 10000.0, tipo_contrato="suministros")
    assert not any(f["activado"] for f in base.resultado(SQL).values())


def test_obras_usa_su_umbral(base):
    base.menor("o1", date(2025, 1, 10), 20000.0, tipo_contrato="obras")
    base.menor("o2", date(2025, 2, 10), 20000.0, tipo_contrato="obras")
    base.menor("o3", date(2025, 1, 10), 25000.0, tipo_contrato="obras", adjudicatario="B2")
    base.menor("o4", date(2025, 2, 10), 25000.0, tipo_contrato="obras", adjudicatario="B2")
    resultado = base.resultado(SQL)
    assert resultado["o1"]["activado"] is False
    assert resultado["o3"]["activado"] is True
    assert "48.400,00 €" in resultado["o3"]["motivo"]


def test_un_contrato_anterior_se_activa_por_una_ventana_posterior(base):
    # m1 y m2 no superan el umbral; m3 completa la ventana de los tres.
    base.menor("m1", date(2025, 1, 10), 6000.0)
    base.menor("m2", date(2025, 5, 10), 6000.0)
    base.menor("m3", date(2025, 12, 10), 6200.0)
    resultado = base.resultado(SQL)
    assert all(resultado[m]["activado"] for m in ("m1", "m2", "m3"))
    assert resultado["m1"]["motivo"].startswith("3 contratos menores")


def test_no_aplicable_otros_tipos_sin_fecha_y_suscripciones(base):
    base.menor("otros", date(2025, 1, 10), 20000.0, tipo_contrato="otros")
    base.menor("sin_fecha", None, 20000.0)
    base.menor("revista", date(2025, 1, 10), 20000.0, titulo="Suscripción a base de datos")
    base.menor("revista2", date(2025, 2, 10), 20000.0, titulo="SUBSCRIPCION revistas")
    base.contrato("licitacion", [{"adjudicatario_id": "B1", "importe_con_iva": 1.0}])
    assert base.resultado(SQL) == {}
