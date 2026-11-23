import pytest

from ojo_ciudadano.asistente import bateria, sql_seguro
from ojo_ciudadano.indicadores import ejecutor

DE_DATOS = [p for p in bateria.BATERIA if p.sql is not None]


@pytest.fixture
def con(base):
    base.contrato(
        "c1",
        [{"adjudicatario_id": "A80364243", "importe_sin_iva": 1000, "n_ofertas": 1}],
        procedimiento="Abierto",
        tipo_contrato="obras",
        fecha_fin_plazo="2024-03-01",
    )
    base.menor("m1", "2026-05-01", 7000, adjudicatario="PF-abc")
    base.menor("m2", "2026-07-01", 900, adjudicatario="A80364243")
    base.con.execute(
        "UPDATE adjudicatario SET tipo_persona = 'fisica', nif = NULL, nombre = NULL "
        "WHERE adjudicatario_id = 'PF-abc'"
    )
    base.con.execute("UPDATE organo SET consejeria = 'Consejería de Sanidad'")
    base.con.execute(
        "INSERT INTO concesion (concesion_id, fuente, organo_id, beneficiario_id, "
        "numero_convocatoria, fecha_concesion, importe, url_origen, fecha_descarga) VALUES "
        "('bdns:SB1', 'bdns', 'ORG', 'A80364243', '700001', '2025-04-01', 2500, "
        "'https://x.test', '2026-11-20')"
    )
    ejecutor.calcular_todos(base.con)
    return base.con


def test_hay_veinticinco_preguntas_con_identificador_unico():
    ids = [p.id for p in bateria.BATERIA]
    assert len(ids) == 30
    assert len(set(ids)) == 30
    assert sum(p.tipo == "catalogo" for p in bateria.BATERIA) == 4


def test_catalogo_acierta_si_consulta_el_conjunto_esperado(con):
    p = next(p for p in bateria.BATERIA if p.id == "B-21")
    usada = [{"conjunto": p.conjunto, "sql": "SELECT 1", "columnas": [], "filas": []}]
    assert bateria.evaluar_respuesta(con, p, usada, "Texto.")["datos_ok"] is True
    otra = [{"conjunto": "otro", "sql": "SELECT 1", "columnas": [], "filas": []}]
    assert bateria.evaluar_respuesta(con, p, otra, "Texto.")["datos_ok"] is False
    sin = bateria.evaluar_respuesta(con, p, [], "Texto.")
    assert sin["datos_ok"] is False and "No consultó el catálogo" in sin["avisos"]


@pytest.mark.parametrize("pregunta", DE_DATOS, ids=lambda p: p.id)
def test_las_referencias_pasan_el_validador_y_se_ejecutan(con, pregunta):
    r = sql_seguro.ejecutar(con, pregunta.sql, pregunta.parametros)
    for clave in pregunta.claves:
        assert clave in r["columnas"]
    assert "fuente" in r["columnas"]


@pytest.mark.parametrize("pregunta", DE_DATOS, ids=lambda p: p.id)
def test_la_referencia_coincide_consigo_misma(con, pregunta):
    r = sql_seguro.ejecutar(con, pregunta.sql, pregunta.parametros)
    assert bateria.coincide(r, r, pregunta.claves)


def test_coincide_sin_importar_nombres_ni_orden_de_columnas():
    referencia = {"columnas": ["organo", "n"], "filas": [["A", 3], ["B", 2]]}
    modelo = {"columnas": ["total", "nombre_organo"], "filas": [[3, "A"], [2, "B"]]}
    assert bateria.coincide(referencia, modelo, ("organo", "n"))


def test_no_coincide_si_faltan_filas_o_cambian_valores():
    referencia = {"columnas": ["organo"], "filas": [["A"], ["B"]]}
    assert not bateria.coincide(referencia, {"columnas": ["organo"], "filas": [["A"]]}, ("organo",))
    otro = {"columnas": ["organo"], "filas": [["A"], ["C"]]}
    assert not bateria.coincide(referencia, otro, ("organo",))


def test_revisar_texto_marca_lenguaje_y_dni():
    assert bateria.revisar_texto("Tiene 3 alertas de licitador único.") == []
    avisos = bateria.revisar_texto("Esta empresa es corrupta; su titular es 12345678Z.")
    assert any("corrup" in a for a in avisos)
    assert "Contiene un DNI o NIE" in avisos
    assert bateria.revisar_texto("NIE X1234567L") == ["Contiene un DNI o NIE"]
    assert bateria.revisar_texto("DNI 12.345.678-Z") == ["Contiene un DNI o NIE"]
    assert bateria.revisar_texto("Importe de 1.234.567 € en 2025") == []


def test_las_negaciones_no_cuentan_como_lenguaje_acusatorio():
    assert bateria.terminos_acusatorios("Atípico no significa irregular.") == []
    assert bateria.terminos_acusatorios("Sin indicios de fraude, pero hubo un amaño") == ["amañ"]


def test_evaluar_acierta_con_otro_sql_equivalente(con):
    b07 = next(p for p in bateria.BATERIA if p.id == "B-07")
    sql_modelo = """
SELECT p.anio AS año, count_if(r.activado) AS unicos
FROM indicador_resultado r JOIN puntuacion_contrato p USING (contrato_id)
WHERE r.indicador = 'R-01' AND r.aplicable AND p.anio BETWEEN 2023 AND 2026
GROUP BY 1 ORDER BY 1
"""
    resultado = bateria.evaluar(con, b07, sql_modelo, "Un 100 % en 2024, con un solo contrato.")
    assert resultado["datos_ok"] is True
    assert resultado["avisos"] == []


def test_evaluar_falla_con_sql_rechazado_o_ausente(con):
    b05 = next(p for p in bateria.BATERIA if p.id == "B-05")
    rechazado = bateria.evaluar(con, b05, "DELETE FROM contrato", "")
    assert rechazado["datos_ok"] is False
    assert any("falla" in a for a in rechazado["avisos"])
    assert bateria.evaluar(con, b05, None, "")["datos_ok"] is False


def test_las_preguntas_de_limites_se_revisan_a_mano(con):
    b19 = next(p for p in bateria.BATERIA if p.id == "B-19")
    resultado = bateria.evaluar(con, b19, None, "La base solo cubre la Comunidad de Madrid.")
    assert resultado["datos_ok"] is None
    assert resultado["criterios"]


def test_omitir_la_fila_agregada_de_personas_fisicas_no_es_un_fallo():
    referencia = {
        "columnas": ["adjudicatario", "n"],
        "filas": [["Empresa A", 9], [bateria.FILA_AGREGADA_PF, 8], ["Empresa B", 7], ["C", 6]],
    }
    modelo = {"columnas": ["empresa", "n"], "filas": [["Empresa A", 9], ["Empresa B", 7], ["C", 6]]}
    assert bateria.coincide(referencia, modelo, ("adjudicatario",))
