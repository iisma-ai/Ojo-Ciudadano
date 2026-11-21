"""Batería de preguntas de prueba del asistente, sobre una base sintética."""

import pytest

from ojo_ciudadano.asistente import bateria, sql_seguro
from ojo_ciudadano.indicadores import ejecutor


@pytest.fixture
def con(base):
    base.contrato(
        "c1",
        [{"adjudicatario_id": "B12345678", "importe_sin_iva": 1000, "n_ofertas": 1}],
        procedimiento="Abierto",
        tipo_contrato="servicios",
        fecha_fin_plazo="2025-03-01",
    )
    base.contrato(
        "c2",
        [{"adjudicatario_id": "B87654321", "importe_sin_iva": 3000, "n_ofertas": 4}],
        procedimiento="Abierto",
        tipo_contrato="servicios",
        presupuesto_sin_iva=6000,
        fecha_fin_plazo="2025-04-01",
    )
    base.menor("m1", "2025-05-01", 7000, adjudicatario="PF-abc")
    base.menor("m2", "2026-07-01", 900, adjudicatario="B12345678")
    base.con.execute(
        "UPDATE adjudicatario SET tipo_persona = 'fisica', nif = NULL, nombre = NULL "
        "WHERE adjudicatario_id = 'PF-abc'"
    )
    base.con.execute(
        "UPDATE adjudicatario SET nombre = 'Servicios Ejemplo SL' WHERE adjudicatario_id = 'B12345678'"
    )
    base.con.execute(
        "INSERT INTO concesion (concesion_id, fuente, organo_id, beneficiario_id, "
        "convocatoria, fecha_concesion, importe, url_origen, fecha_descarga) VALUES "
        "('bdns:1', 'bdns', 'ORG', 'B12345678', 'Ayudas A', '2025-04-01', 2500, 'https://x.test', "
        "'2026-11-20'), ('bdns:2', 'bdns', 'ORG', 'PF-abc', 'Ayudas A', '2025-06-01', 7500, "
        "'https://x.test', '2026-11-20')"
    )
    ejecutor.calcular_todos(base.con)
    return base.con


def test_hay_veinte_preguntas_con_id_unico():
    assert len(bateria.BATERIA) == 20
    assert len({p.id for p in bateria.BATERIA}) == 20
    assert sum(p.sql is None for p in bateria.BATERIA) == 2


@pytest.mark.parametrize("prueba", bateria.BATERIA, ids=lambda p: p.id)
def test_cada_referencia_es_valida_y_se_evalua_como_correcta(con, prueba):
    if prueba.sql is not None:
        sql_seguro.validar(con, prueba.sql)
    evaluacion = bateria.evaluar(con, prueba, prueba.sql)
    assert evaluacion.correcta, evaluacion.motivo


def _prueba(id_):
    return next(p for p in bateria.BATERIA if p.id == id_)


def test_acepta_otro_sql_con_el_mismo_resultado_y_otros_nombres(con):
    otro = "SELECT fuente AS origen, count(contrato_id) AS total FROM contrato_unico GROUP BY 1"
    assert bateria.evaluar(con, _prueba("B01"), otro).correcta


def test_acepta_porcentaje_en_lugar_de_proporcion(con):
    otro = (
        "SELECT 100.0 * count_if(activado) / count(*) FROM indicador_resultado "
        "WHERE indicador = 'R-01'"
    )
    assert bateria.evaluar(con, _prueba("B04"), otro).correcta


def test_rechaza_resultado_distinto(con):
    mal = "SELECT fuente, count(*) + 1 AS n FROM contrato_unico GROUP BY fuente"
    evaluacion = bateria.evaluar(con, _prueba("B01"), mal)
    assert not evaluacion.correcta
    assert evaluacion.coincidencia == 0


def test_rechaza_sql_no_permitido(con):
    evaluacion = bateria.evaluar(con, _prueba("B01"), "SELECT * FROM contrato")
    assert not evaluacion.correcta
    assert "no se pudo ejecutar" in evaluacion.motivo


def test_preguntas_sin_respuesta(con):
    prueba = _prueba("B19")
    assert bateria.evaluar(con, prueba, None).correcta
    assert not bateria.evaluar(con, prueba, "SELECT 1").correcta
    assert not bateria.evaluar(con, _prueba("B01"), None).correcta


def test_personas_fisicas_solo_agregadas(con):
    r = sql_seguro.ejecutar(con, _prueba("B14").sql)
    assert [f[0] for f in r["filas"]] == ["Servicios Ejemplo SL"]
    proporcion = sql_seguro.ejecutar(con, _prueba("B13").sql)["filas"][0][0]
    assert proporcion == pytest.approx(0.75)
