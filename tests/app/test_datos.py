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
    con.execute(
        "UPDATE adjudicatario SET nombre = 'Limpiezas Ejemplo SA', nif = 'B12345678' WHERE adjudicatario_id='A1'"
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


def test_fecha_datos(con):
    assert datos.fecha_datos(con) is not None
