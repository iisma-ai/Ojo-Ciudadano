import duckdb
import pytest

from ojo_ciudadano.asistente import sql_seguro
from ojo_ciudadano.asistente.consultas_demo import CONSULTAS_DEMO
from ojo_ciudadano.indicadores import ejecutor

PERMITIDAS = [
    "SELECT count(*) FROM contrato_unico",
    "FROM organo",
    "WITH x AS (SELECT * FROM organo) SELECT * FROM x",
    "SELECT * FROM organo o JOIN (SELECT * FROM adjudicatario) a ON true",
    "SELECT * FROM (VALUES (1)) v",
    "SELECT upper(nombre) FROM organo WHERE nombre IN (SELECT nombre FROM organo)",
]

RECHAZADAS = [
    "SELECT * FROM contrato",  # usar contrato_unico
    "SELECT 1; SELECT 2",
    "DELETE FROM organo",
    "DROP TABLE organo",
    "ATTACH 'otra.duckdb'",
    "COPY organo TO 'fuera.csv'",
    "INSTALL httpfs",
    "PRAGMA version",
    "SET threads = 1",
    "DESCRIBE organo",
    "SHOW TABLES",
    "SELECT * FROM read_csv('fichero.csv')",
    "SELECT * FROM glob('*')",
    "SELECT * FROM duckdb_settings()",
    "SELECT getenv('HOME')",
    "SELECT * FROM information_schema.tables",
    "SELECT * FROM tabla_inventada",
    "SELECT * FROM organo WHERE organo_id IN (SELECT organo_id FROM contrato)",
    "WITH x AS (SELECT 1) SELECT * FROM main.x",
]


@pytest.fixture
def con(base):
    base.contrato(
        "c1",
        [{"adjudicatario_id": "B12345678", "importe_sin_iva": 1000, "n_ofertas": 1}],
        procedimiento="Abierto",
        tipo_contrato="servicios",
        fecha_fin_plazo="2025-03-01",
    )
    base.menor("m1", "2025-05-01", 7000, adjudicatario="PF-abc")
    base.menor("m2", "2025-07-01", 7000, adjudicatario="PF-abc")
    base.menor("m3", "2025-08-01", 900, adjudicatario="B12345678")
    base.con.execute(
        "UPDATE adjudicatario SET tipo_persona = 'fisica', nif = NULL, nombre = NULL "
        "WHERE adjudicatario_id = 'PF-abc'"
    )
    base.con.execute(
        "UPDATE adjudicatario SET nombre = 'Servicios Ejemplo SL', nif = 'B12345678' "
        "WHERE adjudicatario_id = 'B12345678'"
    )
    base.con.execute("UPDATE organo SET consejeria = 'Consejería de Sanidad'")
    ejecutor.calcular_todos(base.con)
    return base.con


@pytest.mark.parametrize("sql", PERMITIDAS)
def test_consultas_de_lectura_permitidas(con, sql):
    sql_seguro.validar(con, sql)


@pytest.mark.parametrize("sql", RECHAZADAS)
def test_consultas_peligrosas_rechazadas(con, sql):
    with pytest.raises(sql_seguro.SQLNoPermitido):
        sql_seguro.validar(con, sql)


def test_la_conexion_no_lee_ficheros_aunque_falle_la_validacion(tmp_path):
    ruta = tmp_path / "base.duckdb"
    duckdb.connect(str(ruta)).close()
    (tmp_path / "secreto.csv").write_text("a\n1\n")
    con = sql_seguro.conexion_lectura(ruta)
    with pytest.raises(duckdb.Error):
        con.execute(f"SELECT * FROM read_csv('{tmp_path / 'secreto.csv'}')")
    with pytest.raises(duckdb.Error):
        con.execute("CREATE TABLE t (a INT)")


def test_resultado_oculta_seudonimos_y_respeta_el_limite(con):
    r = sql_seguro.ejecutar(con, "SELECT adjudicatario_id FROM adjudicatario ORDER BY 1", limite=1)
    assert r["recortado"]
    assert len(r["filas"]) == 1
    todo = sql_seguro.ejecutar(con, "SELECT adjudicatario_id FROM adjudicatario ORDER BY 1")
    assert [f[0] for f in todo["filas"]] == ["B12345678", sql_seguro.SEUDONIMO_VISIBLE]
    assert todo["sql"].startswith("SELECT")


@pytest.mark.parametrize("consulta", CONSULTAS_DEMO, ids=lambda c: c.pregunta[:30])
def test_consultas_demo_pasan_la_validacion(con, consulta):
    sql_seguro.validar(con, consulta.sql)


def test_menores_por_consejeria_agrega_personas_fisicas(con):
    from ojo_ciudadano.asistente.consultas_demo import MENORES_POR_CONSEJERIA as q

    r = sql_seguro.ejecutar(con, q.sql, {"consejeria": "sanidad"})
    filas = {f[0]: f for f in r["filas"]}
    agregadas = filas["Personas físicas o sin identificar (agregadas)"]
    assert agregadas[1] is None  # sin NIF
    assert agregadas[2] == 2
    assert filas["Servicios Ejemplo SL"][2] == 1


def test_recibido_por_empresa_separa_fuentes(con):
    from ojo_ciudadano.asistente.consultas_demo import RECIBIDO_POR_EMPRESA as q

    r = sql_seguro.ejecutar(con, q.sql, {"empresa": "b12345678"})
    filas = [dict(zip(r["columnas"], f, strict=True)) for f in r["filas"]]
    por_fuente = {f["fuente"].split()[0]: f for f in filas}
    assert por_fuente["Plataforma"]["importe_sin_iva"] == 1000
    assert por_fuente["Plataforma"]["importe_con_iva"] is None
    assert por_fuente["Portal"]["importe_con_iva"] == 900
    assert por_fuente["Portal"]["importe_sin_iva"] is None
    assert sql_seguro.ejecutar(con, q.sql, {"empresa": "PF-abc"})["filas"] == []


def test_recibido_por_empresa_no_muestra_nif_sin_verificar(con):
    from ojo_ciudadano.asistente.consultas_demo import RECIBIDO_POR_EMPRESA as q

    con.execute(
        "INSERT INTO adjudicatario VALUES ('1234567L', '1234567L', 'Nombre Apellido', 'otro')"
    )
    assert sql_seguro.ejecutar(con, q.sql, {"empresa": "Apellido"})["filas"] == []
