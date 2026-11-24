SQL = "r04_concentracion_proveedor.sql"


def mercado(base, importes, tipo="servicios", organo="ORG", prefijo="c"):
    """Un contrato por importe; la empresa es E1, E2… según la posición."""
    for i, importe in enumerate(importes, start=1):
        base.contrato(
            f"{prefijo}{i}",
            [{"adjudicatario_id": f"E{i}", "importe_sin_iva": importe}],
            organo_id=organo,
            tipo_contrato=tipo,
        )


def test_empresa_con_mas_de_la_mitad_activa(base):
    # E1 tiene 1.000 de 1.900 (52,6 %); 10 contratos y 10 empresas.
    mercado(base, [1000] + [100] * 9)
    resultado = base.resultado(SQL)
    assert resultado["c1"]["activado"] is True
    assert resultado["c1"]["valor"] == 1000 / 1900
    assert "52,6 %" in resultado["c1"]["motivo"]
    assert "contratos de servicios" in resultado["c1"]["motivo"]
    assert resultado["c2"]["activado"] is False
    assert resultado["c2"]["motivo"] is None


def test_mercado_repartido_no_activa(base):
    mercado(base, [100] * 10)
    assert not any(f["activado"] for f in base.resultado(SQL).values())


def test_mercado_pequeno_no_es_aplicable(base):
    mercado(base, [1000] + [10] * 8)  # solo 9 contratos
    assert base.resultado(SQL) == {}


def test_pocas_empresas_no_es_aplicable(base):
    for i in range(1, 11):
        base.contrato(
            f"c{i}",
            [{"adjudicatario_id": "E1" if i < 9 else "E2", "importe_sin_iva": 100}],
            tipo_contrato="servicios",
        )
    assert base.resultado(SQL) == {}


def test_limite_exacto_del_50_por_ciento_no_activa(base):
    mercado(base, [900] + [100] * 9)  # E1 = 900 de 1.800: justo el 50 %
    assert base.resultado(SQL)["c1"]["activado"] is False


def test_los_mercados_se_separan_por_organo_y_tipo(base):
    mercado(base, [1000] + [100] * 9, organo="ORG", prefijo="a")
    mercado(base, [100] * 10, organo="OTRO", prefijo="b")
    mercado(base, [1000] + [100] * 9, tipo="obras", prefijo="d")
    resultado = base.resultado(SQL)
    assert resultado["a1"]["activado"] is True
    assert resultado["b1"]["activado"] is False
    assert resultado["d1"]["activado"] is True  # mismo órgano, otro tipo: mercado aparte


def test_sin_tipo_o_sin_adjudicatario_no_es_aplicable(base):
    for i in range(1, 12):
        base.contrato(f"s{i}", [{"adjudicatario_id": f"E{i}", "importe_sin_iva": 100}])
        base.contrato(f"n{i}", [{"importe_sin_iva": 100}], tipo_contrato="servicios")
    assert base.resultado(SQL) == {}


def test_no_mezcla_importes_de_fuentes_distintas(base):
    # El mismo órgano y tipo en las dos fuentes: cada fuente es su propio mercado.
    mercado(base, [1000] + [100] * 9, prefijo="p")
    for i in range(1, 11):
        base.contrato(
            f"m{i}",
            [{"adjudicatario_id": f"F{i}", "importe_con_iva": 100}],
            fuente="portal_cm",
            tipo_contrato="servicios",
        )
    resultado = base.resultado(SQL)
    assert resultado["p1"]["activado"] is True
    assert resultado["m1"]["activado"] is False


def test_en_placsp_el_mercado_se_separa_por_division_cpv(base):
    # Mismo órgano y tipo: E1 domina el material sanitario (33) pero no el de oficina (30).
    for i in range(1, 11):
        base.contrato(
            f"s{i}",
            [
                {
                    "adjudicatario_id": "E1" if i == 1 else f"S{i}",
                    "importe_sin_iva": 1000 if i == 1 else 100,
                }
            ],
            tipo_contrato="suministros",
            cpv="33141000",
        )
        base.contrato(
            f"o{i}",
            [{"adjudicatario_id": f"O{i}", "importe_sin_iva": 100}],
            tipo_contrato="suministros",
            cpv="30192000",
        )
    resultado = base.resultado(SQL)
    assert resultado["s1"]["activado"] is True
    assert resultado["s1"]["valor"] == 1000 / 1900
    assert "división CPV 33" in resultado["s1"]["motivo"]
    assert resultado["o1"]["activado"] is False


def ente_publico(base, adjudicatario_id, nif, nombre="UNIVERSIDAD COMPLUTENSE DE MADRID"):
    base.con.execute(
        "UPDATE adjudicatario SET nif = ?, nombre = ? WHERE adjudicatario_id = ?",
        [nif, nombre, adjudicatario_id],
    )
    base.con.execute(
        "INSERT INTO entidad_sector_publico (nif, codigo_invente, nombre, fuente, url_origen, "
        "fecha_descarga) VALUES (?, 'INV1', 'Universidad Complutense de Madrid', 'invente', "
        "'https://x.test', DATE '2026-11-23')",
        [nif],
    )


def test_un_ente_del_sector_publico_no_activa_pero_cuenta_en_el_mercado(base):
    mercado(base, [1000] + [100] * 9)
    ente_publico(base, "E1", "Q2818014I")
    resultado = base.resultado(SQL)
    assert "c1" not in resultado  # su contrato no es aplicable
    # Los demás siguen midiéndose sobre todo el mercado (1.900), ente incluido.
    assert resultado["c2"]["valor"] == 100 / 1900


def test_nif_de_ente_publico_con_otro_nombre_sigue_siendo_empresa(base):
    # Un NIF de la fuente mal puesto (D-035): el nombre no cuadra y no se trata como ente.
    mercado(base, [1000] + [100] * 9)
    ente_publico(base, "E1", "Q2818014I", nombre="PIXELWARE SA")
    assert base.resultado(SQL)["c1"]["activado"] is True
