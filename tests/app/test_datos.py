import pytest

from ojo_ciudadano.app import datos
from ojo_ciudadano.indicadores import ejecutor


@pytest.fixture
def con(base):
    """Base sintética con dos empresas, una persona física y resultados de indicadores."""
    con = base.con
    base.contrato(
        "c1",
        [{"adjudicatario_id": "A1", "importe_sin_iva": 1000, "n_ofertas": 1}],
        titulo="Servicio de limpieza",
        tipo_contrato="servicios",
        procedimiento="Abierto",
        fecha_fin_plazo="2025-02-01",
    )
    base.contrato(
        "c2",
        [{"adjudicatario_id": "PF-x", "importe_sin_iva": 50}],
        titulo="Suministro",
        fecha_fin_plazo="2025-02-01",
    )
    # Persona física con el DNI sin el cero inicial, mal clasificada como en una base antigua.
    base.contrato(
        "c3",
        [{"adjudicatario_id": "1234567L", "importe_sin_iva": 70}],
        organo_id="OTRO",
        fecha_fin_plazo="2025-02-01",
    )
    con.execute(
        "UPDATE adjudicatario SET nombre = 'Limpiezas Ejemplo SA', nif = 'B12345678' WHERE adjudicatario_id='A1'"
    )
    con.execute(
        "UPDATE adjudicatario SET tipo_persona = 'otro', nombre = 'Nombre Apellido' "
        "WHERE adjudicatario_id = '1234567L'"
    )
    con.execute(
        "UPDATE adjudicatario SET tipo_persona='fisica', nif=NULL, nombre=NULL "
        "WHERE adjudicatario_id = 'PF-x'"
    )
    con.execute(
        "CREATE TABLE indicador_resultado (contrato_id VARCHAR, indicador VARCHAR, "
        "aplicable BOOLEAN, activado BOOLEAN, valor DOUBLE, motivo VARCHAR, url_origen VARCHAR)"
    )
    for cid in ("c1", "c2"):
        for ind, act in (("R-01", True), ("R-02", False), ("R-04", False)):
            con.execute(
                "INSERT INTO indicador_resultado VALUES (?, ?, TRUE, ?, 1, ?, 'https://x.test')",
                [cid, ind, act, "Una sola oferta" if act else None],
            )
    ejecutor.calcular_puntuacion(con)
    return con


def test_busca_empresa_por_nombre_y_nif(con):
    assert [e["adjudicatario_id"] for e in datos.buscar_empresas(con, "limpiezas")] == ["A1"]
    assert [e["adjudicatario_id"] for e in datos.buscar_empresas(con, "b12345678")] == ["A1"]


def test_no_hay_ficha_ni_busqueda_de_personas_fisicas(con):
    assert datos.ficha_empresa(con, "PF-x") is None
    assert datos.buscar_empresas(con, "PF-x") == []


def test_busqueda_corta_no_devuelve_nada(con):
    assert datos.buscar_empresas(con, "li") == []


def test_ficha_y_contratos_de_la_empresa(con):
    ficha = datos.ficha_empresa(con, "A1")
    assert ficha["n_contratos"] == 1
    assert ficha["importe_sin_iva"] == 1000
    contratos = datos.contratos_empresa(con, "A1")
    assert contratos[0]["contrato_id"] == "c1"
    assert contratos[0]["url_origen"] == "https://ejemplo.test/c1"
    assert contratos[0]["indicadores_activados"] == "R-01"


def test_alertas_filtran_por_minimo_de_aplicables_e_indicador(con):
    assert [a["contrato_id"] for a in datos.alertas(con, min_aplicables=3)] == ["c1", "c2"]
    assert datos.alertas(con, min_aplicables=4) == []
    assert len(datos.alertas(con, indicador="R-01")) == 2
    assert datos.alertas(con, indicador="R-02") == []


def test_motivos_solo_los_activados(con):
    assert [m["indicador"] for m in datos.motivos(con, "c1")] == ["R-01"]


def test_nif_con_forma_de_dni_no_aparece_en_ningun_listado(con):
    assert datos.buscar_empresas(con, "1234567L") == []
    assert datos.buscar_empresas(con, "Apellido") == []
    assert datos.ficha_empresa(con, "1234567L") is None
    assert datos.proveedores_organo(con, "OTRO") == []
    todos = datos.flujos(con, "placsp", limite=100)
    assert "1234567L" not in [f["adjudicatario_id"] for f in todos]
    assert datos.contratos_flujo(con, "OTRO", "1234567L", "placsp") == []


def test_fecha_de_descarga_por_fuente(con):
    fechas = datos.fechas_datos(con)
    assert [f["fuente"] for f in fechas] == ["placsp"]
    assert fechas[0]["fecha"] is not None


def test_ficha_de_organo(con):
    ficha = datos.ficha_organo(con, "ORG")
    assert ficha["n_contratos"] == 2
    assert ficha["importe_sin_iva"] == 1050
    assert datos.ficha_organo(con, "NO_EXISTE") is None
    assert [o["organo_id"] for o in datos.buscar_organos(con, "órgano")] == ["ORG"]


def test_indicadores_del_organo_frente_al_global(con):
    por_ind = {i["indicador"]: i for i in datos.indicadores_organo(con, "ORG")}
    assert por_ind["R-01"]["activados"] == 2
    assert por_ind["R-01"]["pct_organo"] == 1.0
    assert por_ind["R-02"]["pct_organo"] == 0.0


def test_procedimientos_y_proveedores_sin_personas_fisicas(con):
    assert datos.procedimientos_organo(con, "ORG")[0]["n_contratos"] >= 1
    proveedores = datos.proveedores_organo(con, "ORG")
    assert [p["adjudicatario_id"] for p in proveedores] == ["A1"]


def test_tendencia_del_organo(con):
    assert datos.tendencia_organo(con, "ORG")[0]["anio"] == 2025


def test_flujos_por_fuente_sin_personas_fisicas(con):
    flujos = datos.flujos(con, "placsp")
    assert [(f["organo_id"], f["adjudicatario_id"], f["importe"]) for f in flujos] == [
        ("ORG", "A1", 1000)
    ]
    assert datos.flujos(con, "portal_cm") == []  # no mezcla fuentes


def test_flujos_filtran_por_anio_y_tipo(con):
    assert len(datos.flujos(con, "placsp", anio=2025)) == 1
    assert datos.flujos(con, "placsp", anio=2024) == []
    assert datos.flujos(con, "placsp", tipo_contrato="obras") == []


def test_contratos_del_flujo_con_enlace(con):
    contratos = datos.contratos_flujo(con, "ORG", "A1", "placsp")
    assert [c["contrato_id"] for c in contratos] == ["c1"]
    assert contratos[0]["url_origen"] == "https://ejemplo.test/c1"


def test_subvenciones_de_la_empresa_con_enlace(con):
    con.execute(
        "INSERT INTO concesion (concesion_id, fuente, organo_id, beneficiario_id, convocatoria, "
        "fecha_concesion, importe, url_origen, fecha_descarga) VALUES "
        "('bdns:1', 'bdns', 'ORG', 'A1', 'Ayudas de prueba', '2025-04-01', 300, "
        "'https://bdns.test/1', '2026-11-20'), "
        "('bdns:2', 'bdns', 'ORG', 'PF-x', 'Ayudas de prueba', '2025-04-01', 50, "
        "'https://bdns.test/1', '2026-11-20')"
    )
    filas = datos.subvenciones_empresa(con, "A1")
    assert [(f["n_concesiones"], f["importe"], f["url_origen"]) for f in filas] == [
        (1, 300, "https://bdns.test/1")
    ]
    assert filas[0]["importe_total"] == 300
    assert datos.subvenciones_empresa(con, "PF-x") == []


def _con_subvenciones(con):
    con.execute(
        "INSERT INTO concesion (concesion_id, fuente, organo_id, beneficiario_id, convocatoria, "
        "fecha_concesion, importe, url_origen, fecha_descarga) VALUES "
        "('bdns:1', 'bdns', 'ORG', 'A1', 'Ayudas A', '2025-04-01', 300, 'https://bdns.test/1', "
        "'2026-11-20'), "
        "('bdns:2', 'bdns', 'ORG', 'PF-x', 'Ayudas B', '2025-04-01', 50, 'https://bdns.test/2', "
        "'2026-11-20'), "
        "('bdns:3', 'bdns', 'ORG', '1234567L', 'Ayudas B', '2024-04-01', 20, "
        "'https://bdns.test/2', '2026-11-20')"
    )
    return con


def test_subvenciones_del_organo_agregan_personas(con):
    _con_subvenciones(con)
    resumen = datos.subvenciones_organo(con, "ORG")
    assert resumen["n_concesiones"] == 3 and resumen["importe"] == 370
    assert resumen["n_entidades"] == 1
    assert (resumen["n_agregado"], resumen["importe_agregado"]) == (2, 70)
    assert [b["adjudicatario_id"] for b in datos.beneficiarios_organo(con, "ORG")] == ["A1"]
    convocatorias = datos.convocatorias_organo(con, "ORG")
    assert [c["convocatoria"] for c in convocatorias] == ["Ayudas A", "Ayudas B"]
    assert datos.subvenciones_organo(con, "OTRO") is None


def test_flujos_de_subvenciones_con_personas_agregadas(con):
    _con_subvenciones(con)
    flujos = {f["empresa"]: f for f in datos.flujos_subvenciones(con)}
    assert flujos[datos.AGREGADO_PERSONAS]["importe"] == 70
    assert flujos[datos.AGREGADO_PERSONAS]["adjudicatario_id"] == "AGREGADO"
    assert flujos["Limpiezas Ejemplo SA"]["importe"] == 300
    assert len(datos.flujos_subvenciones(con, anio=2024)) == 1
    # Con solo 2 concesiones, «Ayudas B» no se muestra por su nombre en el flujo agregado.
    detalle = datos.concesiones_flujo(con, "ORG", "AGREGADO")
    assert len(detalle) == 1
    assert detalle[0]["titulo"].startswith("Otras convocatorias (1)")
    assert (detalle[0]["importe"], detalle[0]["url_origen"]) == (70, None)
    assert datos.concesiones_flujo(con, "ORG", "A1")[0]["titulo"] == "Ayudas A"
    assert datos.fecha_subvenciones(con) is not None


@pytest.fixture
def con_anomalias(con):
    con.execute(
        "CREATE TABLE anomalia_resultado (contrato_id VARCHAR, grupo VARCHAR, n_grupo BIGINT, "
        "puntuacion DOUBLE, atipico BOOLEAN, variables VARCHAR, motivo VARCHAR, "
        "url_origen VARCHAR)"
    )
    for cid, atipico in (("c1", True), ("c2", True), ("c3", False)):
        con.execute(
            "INSERT INTO anomalia_resultado VALUES (?, 'placsp · licitación · servicios', 3, "
            "0.99, ?, 'importe', 'Importe adjudicado alto', 'https://x.test')",
            [cid, atipico],
        )
    return con


def test_sin_tabla_de_anomalias_no_falla(con):
    assert not datos.hay_anomalias(con)
    assert datos.atipicos(con) == []
    assert datos.atipicos_agregados(con) == 0
    assert datos.anomalia_contrato(con, "c1") is None


def test_atipicos_sin_personas_fisicas(con_anomalias):
    filas = datos.atipicos(con_anomalias)
    assert [f["contrato_id"] for f in filas] == ["c1"]
    assert filas[0]["adjudicatarios"] == "Limpiezas Ejemplo SA"
    # c2 es de una persona física: solo se cuenta.
    assert datos.atipicos_agregados(con_anomalias) == 1
    assert datos.grupos_anomalias(con_anomalias)[0]["n_atipicos"] == 2
    assert datos.anomalia_contrato(con_anomalias, "c1")["motivo"] == "Importe adjudicado alto"
    assert datos.anomalia_contrato(con_anomalias, "c3") is None


def test_fecha_de_descarga_incluye_la_bdns(con):
    con.execute(
        "INSERT INTO concesion (concesion_id, fuente, organo_id, url_origen, fecha_descarga) "
        "VALUES ('s1', 'bdns', 'ORG', 'https://x.test', '2026-11-20')"
    )
    assert [f["fuente"] for f in datos.fechas_datos(con)] == ["bdns", "placsp"]


def test_ute_con_persona_fisica_de_una_base_antigua_no_tiene_ficha(base, con):
    """Bases cargadas antes de la corrección: la UTE con un PF- conserva nombre y tipo «ute»."""
    base.contrato("u1", [{"adjudicatario_id": "UTE:PF-abc+B1", "importe_sin_iva": 10}])
    base.con.execute(
        "UPDATE adjudicatario SET tipo_persona = 'ute', nif = NULL, "
        "nombre = 'UTE NOMBRE APELLIDO - EMPRESA' WHERE adjudicatario_id = 'UTE:PF-abc+B1'"
    )
    assert datos.buscar_empresas(base.con, "apellido") == []
    assert datos.ficha_empresa(base.con, "UTE:PF-abc+B1") is None
