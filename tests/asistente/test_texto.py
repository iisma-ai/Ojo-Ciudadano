import duckdb
import pytest

from ojo_ciudadano.asistente import sql_seguro, texto
from ojo_ciudadano.indicadores import ejecutor


@pytest.fixture
def con(base):
    base.contrato(
        "placsp:1",
        [{"adjudicatario_id": "B1", "importe_sin_iva": 1000.0}],
        titulo="Servicio de ambulancias para el hospital",
        procedimiento="Abierto",
    )
    base.contrato(
        "portal_cm:2",
        [{"adjudicatario_id": "B2", "importe_con_iva": 500.0}],
        fuente="portal_cm",
        titulo="Transporte sanitario en AMBULANCIA",
        procedimiento="Abierto",
    )
    base.contrato("placsp:3", [{"adjudicatario_id": "B3"}], titulo="Limpieza de edificios")
    ejecutor.calcular_todos(base.con)
    texto.construir_en(base.con)
    return base.con


def test_encuentra_plurales_mayusculas_y_tildes(con):
    r = texto.buscar(con, "ambulancias", "contrato")
    assert {f[0] for f in r["filas"]} == {
        "Servicio de ambulancias para el hospital",
        "Transporte sanitario en AMBULANCIA",
    }
    assert "url_origen" in r["columnas"] and "fecha_descarga" in r["columnas"]
    assert r["busqueda"] == "ambulancias" and r["origen"] == "contrato"


def test_exige_todas_las_palabras(con):
    assert len(texto.buscar(con, "transporte ambulancia", "contrato")["filas"]) == 1
    assert texto.buscar(con, "ambulancia limpieza", "contrato")["filas"] == []


def test_resumen_por_fuente_sin_mezclar_iva(con):
    resumen = texto.buscar(con, "ambulancia", "contrato")["resumen"]
    filas = {f[0]: dict(zip(resumen["columnas"], f, strict=True)) for f in resumen["filas"]}
    placsp = filas["Plataforma de Contratación del Sector Público"]
    portal = filas["Portal de la Contratación Pública de la Comunidad de Madrid"]
    assert placsp["n"] == 1 and placsp["importe_sin_iva"] == 1000.0
    assert placsp["importe_con_iva"] is None
    assert portal["importe_con_iva"] == 500.0


def test_no_muestra_el_titulo_si_hay_una_persona_fisica(base):
    base.contrato(
        "portal_cm:7",
        [{"adjudicatario_id": "PF-abc", "importe_con_iva": 300.0}],
        fuente="portal_cm",
        titulo="Fisioterapia prestada por Don Fulano Pérez",
        procedimiento="Abierto",
    )
    base.contrato("placsp:8", [{"adjudicatario_id": "B9"}], titulo="Fisioterapia en el hospital")
    ejecutor.calcular_todos(base.con)
    texto.construir_en(base.con)
    r = texto.buscar(base.con, "fisioterapia", "contrato")
    titulos = {f[0] for f in r["filas"]}
    assert titulos == {texto.TITULO_OCULTO, "Fisioterapia en el hospital"}
    assert sum(f[1] for f in r["resumen"]["filas"]) == 2  # sigue contando


def test_la_consulta_es_un_parametro_no_sql(con):
    r = texto.buscar(con, "'); DROP TABLE contrato; --", "contrato")
    assert r["filas"] == []
    assert con.execute("SELECT count(*) FROM contrato").fetchall()[0][0] == 3


def test_origen_no_valido_o_sin_indice(con, base):
    with pytest.raises(texto.BusquedaNoDisponible, match="Origen no válido"):
        texto.buscar(con, "x", "contratos; DROP")
    with pytest.raises(texto.BusquedaNoDisponible, match="vacía"):
        texto.buscar(con, "  ", "contrato")
    vacia = duckdb.connect()
    with pytest.raises(texto.BusquedaNoDisponible, match="no está preparada"):
        texto.buscar(vacia, "x", "contrato")


def test_funciona_en_la_conexion_de_solo_lectura(tmp_path, base):
    ruta = tmp_path / "base.duckdb"
    escritura = duckdb.connect(str(ruta))
    escritura.execute(
        "CREATE TABLE contrato_unico AS SELECT * FROM (VALUES "
        "('placsp:9', 'Suministro de ambulancias', 'O1', 'placsp', 'https://x', "
        "DATE '2026-11-16')) t(contrato_id, titulo, organo_id, fuente, url_origen, "
        "fecha_descarga)"
    )
    escritura.execute(
        "CREATE TABLE convenio (convenio_id VARCHAR, titulo VARCHAR, "
        "organo_id VARCHAR, fuente VARCHAR, url_origen VARCHAR, fecha_descarga DATE)"
    )
    escritura.execute(
        "CREATE TABLE concesion (id_convocatoria VARCHAR, convocatoria VARCHAR, "
        "organo_id VARCHAR, url_origen VARCHAR, fecha_descarga DATE, "
        "concesion_id VARCHAR, importe DOUBLE)"
    )
    escritura.execute("CREATE TABLE organo (organo_id VARCHAR, nombre VARCHAR)")
    escritura.execute(
        "CREATE TABLE adjudicacion (contrato_id VARCHAR, importe_sin_iva DOUBLE, "
        "importe_con_iva DOUBLE)"
    )
    escritura.execute("CREATE TABLE adjudicatario (adjudicatario_id VARCHAR, tipo_persona VARCHAR)")
    escritura.execute("ALTER TABLE adjudicacion ADD COLUMN adjudicatario_id VARCHAR")
    escritura.execute("ALTER TABLE convenio ADD COLUMN n_firmantes INTEGER")
    escritura.execute("ALTER TABLE convenio ADD COLUMN entidades VARCHAR")
    texto.construir_en(escritura)
    escritura.close()
    lectura = sql_seguro.conexion_lectura(ruta)
    assert texto.buscar(lectura, "ambulancia", "contrato")["filas"][0][0] == (
        "Suministro de ambulancias"
    )
    with pytest.raises(duckdb.Error):
        lectura.execute("SET enable_external_access = true")
