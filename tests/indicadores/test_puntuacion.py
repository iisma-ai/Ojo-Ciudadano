import pytest

from ojo_ciudadano.indicadores import ejecutor


def resultado(base, contrato_id, indicador, activado):
    base.con.execute(
        "INSERT INTO indicador_resultado VALUES (?, ?, TRUE, ?, 1.0, NULL, 'https://x.test')",
        [contrato_id, indicador, activado],
    )


@pytest.fixture
def datos(base):
    base.con.execute(
        "CREATE TABLE indicador_resultado (contrato_id VARCHAR, indicador VARCHAR, "
        "aplicable BOOLEAN, activado BOOLEAN, valor DOUBLE, motivo VARCHAR, url_origen VARCHAR)"
    )
    return base


def contrato(base, cid, importe, adjudicatario="E1", organo="ORG", fecha="2025-03-01", **campos):
    base.contrato(
        cid,
        [{"adjudicatario_id": adjudicatario, "importe_sin_iva": importe}],
        organo_id=organo,
        fecha_contrato=fecha,
        **campos,
    )


def calcular(base):
    ejecutor.calcular_puntuacion(base.con)
    return base.con


def test_puntuacion_de_contrato_es_la_proporcion_de_aplicables_activados(datos):
    contrato(datos, "c1", 100)
    for indicador, activado in [("R-01", True), ("R-02", False), ("R-04", True), ("R-06", False)]:
        resultado(datos, "c1", indicador, activado)
    cursor = calcular(datos).execute("SELECT * FROM puntuacion_contrato")
    fila = dict(zip([d[0] for d in cursor.description], cursor.fetchone(), strict=True))
    assert fila["n_aplicables"] == 4
    assert fila["n_activados"] == 2
    assert fila["puntuacion"] == 0.5
    assert fila["indicadores_activados"] == "R-01, R-04"
    assert fila["anio"] == 2025


def test_contrato_sin_indicadores_aplicables_no_tiene_puntuacion(datos):
    contrato(datos, "c1", 100)
    assert calcular(datos).execute("SELECT count(*) FROM puntuacion_contrato").fetchone()[0] == 0


def test_organo_pondera_por_importe(datos):
    contrato(datos, "grande", 900)
    contrato(datos, "pequeno", 100)
    resultado(datos, "grande", "R-01", False)
    resultado(datos, "pequeno", "R-01", True)
    fila = (
        calcular(datos)
        .execute(
            "SELECT n_contratos, n_con_alertas, puntuacion_ponderada, puntuacion_media "
            "FROM puntuacion_organo WHERE organo_id = 'ORG'"
        )
        .fetchone()
    )
    assert fila == (2, 1, 0.1, 0.5)


def test_tendencia_por_anio(datos):
    contrato(datos, "a", 100, fecha="2024-05-01")
    contrato(datos, "b", 100, fecha="2025-05-01")
    resultado(datos, "a", "R-01", False)
    resultado(datos, "b", "R-01", True)
    filas = (
        calcular(datos)
        .execute("SELECT anio, puntuacion_ponderada FROM puntuacion_organo_anio ORDER BY anio")
        .fetchall()
    )
    assert filas == [(2024, 0.0), (2025, 1.0)]


def test_empresa_y_sin_fichas_de_personas_fisicas(datos):
    contrato(datos, "a", 100, adjudicatario="E1")
    datos.con.execute("INSERT INTO adjudicatario VALUES ('PF-abc', NULL, NULL, 'fisica')")
    datos.contrato(
        "b",
        [{"adjudicatario_id": "PF-abc", "importe_sin_iva": 100}],
        fecha_contrato="2025-03-01",
    )
    resultado(datos, "a", "R-01", True)
    resultado(datos, "b", "R-01", True)
    con = calcular(datos)
    assert con.execute("SELECT adjudicatario_id FROM puntuacion_empresa").fetchall() == [("E1",)]
    # El contrato de la persona física sí cuenta en el órgano.
    assert con.execute("SELECT n_contratos FROM puntuacion_organo").fetchone() == (2,)


def test_importe_cero_no_rompe_la_media_ponderada(datos):
    datos.contrato("c1", [{"adjudicatario_id": "E1"}], fecha_contrato="2025-01-01")
    resultado(datos, "c1", "R-01", True)
    fila = (
        calcular(datos)
        .execute("SELECT puntuacion_ponderada, puntuacion_media FROM puntuacion_organo")
        .fetchone()
    )
    assert fila == (None, 1.0)


def test_ente_del_sector_publico_sin_puntuacion_de_empresa(datos):
    contrato(datos, "a", 100, adjudicatario="E1")
    contrato(datos, "b", 100, adjudicatario="UNI")
    datos.con.execute(
        "UPDATE adjudicatario SET nif = 'Q2818014I', nombre = 'UNIVERSIDAD DE ALCALA' "
        "WHERE adjudicatario_id = 'UNI'"
    )
    datos.con.execute(
        "INSERT INTO entidad_sector_publico (nif, codigo_invente, nombre, fuente, url_origen, "
        "fecha_descarga) VALUES ('Q2818014I', 'INV1', 'Universidad de Alcalá', 'invente', 'https://x.test', "
        "DATE '2026-11-23')"
    )
    resultado(datos, "a", "R-01", True)
    resultado(datos, "b", "R-01", True)
    con = calcular(datos)
    filas = dict(
        con.execute(
            "SELECT adjudicatario_id, puntuacion_ponderada FROM puntuacion_empresa"
        ).fetchall()
    )
    assert filas == {"E1": 1.0, "UNI": None}  # conserva su ficha, sin puntuación
    assert con.execute(
        "SELECT sector_publico FROM puntuacion_empresa WHERE adjudicatario_id = 'UNI'"
    ).fetchone() == (True,)
    # Su contrato sí cuenta en el órgano.
    assert con.execute("SELECT n_contratos FROM puntuacion_organo").fetchone() == (2,)


def test_calcular_funciona_sin_las_tablas_de_contexto(datos):
    datos.con.execute("DROP TABLE entidad_sector_publico")
    datos.con.execute("DROP TABLE cpv")
    contrato(datos, "a", 100)
    resultado(datos, "a", "R-01", True)
    con = calcular(datos)
    assert con.execute("SELECT puntuacion_ponderada FROM puntuacion_empresa").fetchone() == (1.0,)
