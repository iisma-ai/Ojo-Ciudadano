import json
from datetime import date
from pathlib import Path

import duckdb
from test_carga import _placsp, _portal

from ojo_ciudadano.ingesta import bdns
from ojo_ciudadano.modelo import carga

HOY = date(2026, 11, 20)
SAL = b"sal-de-prueba"
ESQUEMA = Path(__file__).parent.parent / "sql" / "esquema"


def _fila(cod, beneficiario, id_persona, importe, nivel2="COMUNIDAD DE MADRID", organo=None):
    return {
        "codConcesion": cod,
        "fechaConcesion": "2025-05-10",
        "beneficiario": beneficiario,
        "idPersona": id_persona,
        "importe": importe,
        "ayudaEquivalente": importe,
        "instrumento": "SUBVENCIÓN y ENTREGA DINERARIA SIN CONTRAPRESTACIÓN ",
        "idConvocatoria": 1,
        "numeroConvocatoria": "999001",
        "convocatoria": "Ayudas de prueba",
        "urlBR": "https://ejemplo.test/bases",
        "nivel1": "AUTONOMICA",
        "nivel2": nivel2,
        "nivel3": organo or "HOSPITAL DE EJEMPLO",
    }


def _mes(tmp_path):
    filas = [
        _fila("SB1", "B11111111 EMPRESA UNO, S.L.", 10, 5000.0),
        _fila("SB2", "***1234** NOMBRE APELLIDO", 20, 300.0, organo="CONSEJERÍA DE PRUEBAS"),
        _fila("SB3", "***1234** NOMBRE APELLIDO", 20, 200.0),
        _fila("SB4", "***9999** OTRA PERSONA", 21, 100.0),
        _fila("SB5", "B22222222 FUERA SL", 30, 1.0, nivel2="COMUNIDAD FORAL DE NAVARRA"),
        _fila("SB1", "B11111111 EMPRESA UNO, S.L.", 10, 5000.0),  # repetida
    ]
    ruta = tmp_path / "2025-05.json"
    ruta.write_text(json.dumps(filas, ensure_ascii=False), encoding="utf-8")
    return ruta


def test_separar_beneficiario():
    assert bdns.separar_beneficiario("B11111111 EMPRESA UNO, S.L.") == (
        "B11111111",
        "EMPRESA UNO, S.L.",
    )
    assert bdns.separar_beneficiario("***1234** NOMBRE") == ("***1234**", "NOMBRE")
    assert bdns.separar_beneficiario("ASOCIACION SIN NIF") == (None, "ASOCIACION SIN NIF")
    assert bdns.separar_beneficiario("  ") == (None, None)


def test_personas_fisicas_sin_nombre_ni_nif_y_con_seudonimo_por_id_persona(tmp_path):
    tablas = bdns.leer([_mes(tmp_path)], HOY, SAL)
    personas = tablas["beneficiarios"].filter(tipo_persona="fisica")
    assert personas.height == 2  # dos idPersona distintos aunque compartan NIF enmascarado
    assert personas["nombre"].null_count() == 2
    assert personas["nif"].null_count() == 2
    assert all(i.startswith("PF-") for i in personas["adjudicatario_id"])
    texto = json.dumps(tablas["concesiones"].to_dicts(), default=str)
    assert "APELLIDO" not in texto and "1234" not in texto


def test_concesiones_de_la_comunidad_sin_repetir_y_con_enlace(tmp_path):
    concesiones = bdns.leer([_mes(tmp_path)], HOY, SAL)["concesiones"]
    assert sorted(concesiones["concesion_id"]) == ["bdns:SB1", "bdns:SB2", "bdns:SB3", "bdns:SB4"]
    empresa = concesiones.filter(concesion_id="bdns:SB1").row(0, named=True)
    assert empresa["beneficiario_id"] == "B11111111"
    assert empresa["organo_id"] == "HOSPITAL DE EJEMPLO"
    assert empresa["url_origen"] == bdns.URL_CONVOCATORIA + "999001"
    assert empresa["instrumento"] == "SUBVENCIÓN y ENTREGA DINERARIA SIN CONTRAPRESTACIÓN"
    assert empresa["fecha_descarga"] == HOY


def test_la_carga_une_beneficiarios_y_organos_con_los_de_contratos(tmp_path):
    tablas = carga.unificar([_portal()], _placsp(), bdns.leer([_mes(tmp_path)], HOY, SAL))
    ruta = tmp_path / "base.duckdb"
    carga.escribir(tablas, ruta, ESQUEMA)
    con = duckdb.connect(str(ruta), read_only=True)
    # La empresa es la misma en contratos y subvenciones: un solo adjudicatario.
    assert con.execute(
        "SELECT count(*) FROM adjudicatario WHERE adjudicatario_id = 'B11111111'"
    ).fetchone() == (1,)
    total = con.execute(
        "SELECT sum(importe) FROM concesion WHERE beneficiario_id = 'B11111111'"
    ).fetchone()
    assert total == (5000.0,)
    # El órgano del contrato conserva su nombre; el nuevo de la BDNS se añade.
    nombres = dict(con.execute("SELECT organo_id, nombre FROM organo").fetchall())
    assert nombres["HOSPITAL DE EJEMPLO"] in ("Hospital de Ejemplo", "HOSPITAL DE EJEMPLO")
    assert "CONSEJERIA DE PRUEBAS" in nombres
    assert con.execute("SELECT count(*) FROM concesion").fetchone() == (4,)


def test_sin_bdns_la_carga_no_crea_concesiones(tmp_path):
    tablas = carga.unificar([_portal()], None)
    assert tablas["concesion"] is None


def test_organos_con_otro_nombre_en_la_bdns_usan_el_de_los_contratos():
    assert bdns.organo_id("SERVICIO MADRILEÑO DE SALUD (SERMAS)") == "SERVICIO MADRILENO DE SALUD"
    assert bdns.organo_id("CONSEJERÍA DE SANIDAD") == "CONSEJERIA DE SANIDAD"


def test_la_cache_no_guarda_nombres_de_personas():
    persona = bdns.minimizar(_fila("SB9", "***1234** NOMBRE APELLIDO", 20, 1.0))
    assert persona["beneficiario"] == "***1234**"
    extranjero = bdns.minimizar(_fila("SB8", "ZZ999 NOMBRE EXTRANJERO", 22, 1.0))
    assert extranjero["beneficiario"] == "ZZ999"
    empresa = bdns.minimizar(_fila("SB7", "B11111111 EMPRESA UNO, S.L.", 10, 1.0))
    assert empresa["beneficiario"] == "B11111111 EMPRESA UNO, S.L."


def test_nif_extranjero_o_erroneo_se_trata_como_persona():
    identidad = bdns.identificar_beneficiario("ZZ999 NOMBRE EXTRANJERO", 22, SAL)
    assert identidad["tipo_persona"] == "fisica"
    assert identidad["nombre"] is None and identidad["nif"] is None
