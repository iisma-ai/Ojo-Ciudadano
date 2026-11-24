import pytest

from ojo_ciudadano.app import datos_flujos


@pytest.fixture
def con(base):
    """Un contrato de PLACSP con fondos del PRTR y un recurso, su duplicado del portal y tres
    encargos: dos a una empresa pública y uno a una persona física."""
    con = base.con
    base.contrato("placsp:1", expediente="A/SER-1/2026")
    base.contrato("portal_cm:C1", fuente="portal_cm", duplicado_de="placsp:1")
    con.execute(
        "INSERT INTO contrato_financiacion VALUES "
        "('placsp:1', TRUE, 'PRTR,FEDER', 'placsp', 'https://ejemplo.test/placsp:1', current_date)"
    )
    con.execute(
        "INSERT INTO recurso_especial VALUES ('tacpcm:1/2026', '1/2026', DATE '2026-03-01', "
        "'Consejerías', 'Estimatoria', 'Pliegos', 'A/SER-1/2026', 'placsp:1', 'tacpcm', "
        "'https://tacp.test/1', NULL, current_date)"
    )
    con.execute("INSERT INTO adjudicatario VALUES ('A28476208', 'A28476208', 'TRAGSA', 'juridica')")
    con.execute("INSERT INTO adjudicatario VALUES ('PF-1', NULL, NULL, 'fisica')")
    for n, (medio, importe, anio) in enumerate(
        [("A28476208", 1000.0, 2025), ("A28476208", 500.0, 2026), ("PF-1", 10.0, 2026)]
    ):
        con.execute(
            "INSERT INTO encargo (encargo_id, orden, fuente, organo_id, titulo, anio_publicacion, "
            "medio_propio_id, importe_con_iva, url_origen, fecha_descarga) "
            "VALUES (?, 1, 'portal_cm', 'ORG', 'Encargo', ?, ?, ?, ?, current_date)",
            [f"portal_cm:C{n}", anio, medio, importe, f"https://ejemplo.test/C{n}"],
        )
    return con


def test_encargos_del_organo_sin_nombres_de_personas(con):
    resumen = datos_flujos.encargos_organo(con, "ORG")
    assert resumen["n_encargos"] == 3
    assert resumen["importe"] == 1510.0
    assert resumen["por_medio_propio"][0] == ("TRAGSA", 1500.0)
    assert {e["medio_propio"] for e in resumen["lista"]} == {
        "TRAGSA",
        datos_flujos.AGREGADO_PERSONAS,
    }
    assert datos_flujos.encargos_organo(con, "OTRO") is None


def test_encargos_de_la_empresa(con):
    resumen = datos_flujos.encargos_empresa(con, "A28476208")
    assert resumen["n_encargos"] == 2 and resumen["importe"] == 1500.0
    assert resumen["por_organo"][0]["organo"] == "Órgano"


def test_fondos_y_recurso_tambien_desde_el_duplicado_del_portal(con):
    for contrato_id in ("placsp:1", "portal_cm:C1"):
        assert datos_flujos.financiacion_contrato(con, contrato_id)["programas_ue"] == "PRTR,FEDER"
        (recurso,) = datos_flujos.recursos_contrato(con, contrato_id)
        assert recurso["tipo_resolucion"] == "Estimatoria"


def test_resumenes(con):
    (pliegos,) = datos_flujos.resumen_recursos(con)
    assert pliegos["acto_recurrido"] == "Pliegos" and pliegos["estimadas"] == 1
    assert [a["anio"] for a in datos_flujos.resumen_encargos(con)["por_anio"]] == [2025, 2026]


def test_base_sin_tablas_nuevas(base):
    base.con.execute("DROP TABLE encargo")
    assert datos_flujos.encargos_organo(base.con, "ORG") is None
    assert datos_flujos.resumen_encargos(base.con) is None


def test_pliegos_tambien_desde_el_duplicado_del_portal(con):
    con.execute(
        "INSERT INTO contrato_documento VALUES ('placsp:1', 1, 'pcap', 'p.pdf', "
        "'https://contratos-publicos.comunidad.madrid/p.pdf', 'placsp', 'https://x.test', "
        "DATE '2026-11-23')"
    )
    for contrato_id in ("placsp:1", "portal_cm:C1"):
        (pliego,) = datos_flujos.pliegos_contrato(con, contrato_id)
        assert pliego["contrato_id"] == "placsp:1" and pliego["tipo"] == "pcap"


def test_sin_tabla_de_pliegos(base):
    base.con.execute("DROP TABLE contrato_documento")
    assert datos_flujos.pliegos_contrato(base.con, "placsp:1") == []


def test_cpv_con_su_nombre_tambien_desde_el_duplicado(con):
    con.execute("UPDATE contrato SET cpv = '33100000' WHERE contrato_id = 'placsp:1'")
    con.execute(
        "INSERT INTO cpv VALUES ('33100000', 'Equipamiento médico', '33', "
        "'Equipamiento y artículos médicos', 'placsp', 'https://x.test', DATE '2026-11-23')"
    )
    for contrato_id in ("placsp:1", "portal_cm:C1"):
        objeto = datos_flujos.cpv_contrato(con, contrato_id)
        assert objeto["codigo"] == "33100000" and objeto["nombre"] == "Equipamiento médico"


def test_sector_publico_con_aviso_si_el_nombre_no_se_parece(con):
    con.execute(
        "INSERT INTO entidad_sector_publico VALUES ('Q2818011E', 'INV3', "
        "'Universidad Complutense de Madrid', 'Universidad pública', 'Estado', NULL, 'OE1', "
        "'invente', 'https://x.test', DATE '2026-11-23')"
    )
    bien = datos_flujos.sector_publico(con, "Q2818011E", "UNIVERSIDAD COMPLUTENSE DE MADRID")
    assert bien["forma_juridica"] == "Universidad pública" and bien["nombre_compatible"]
    mal = datos_flujos.sector_publico(con, "Q2818011E", "AUDALIA AUDITORES SL")
    assert not mal["nombre_compatible"]
    assert datos_flujos.sector_publico(con, "B00000000", "Otra") is None
    assert datos_flujos.sector_publico(con, None, "Sin NIF") is None
