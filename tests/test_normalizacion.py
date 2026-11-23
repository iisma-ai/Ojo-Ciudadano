from datetime import date

from ojo_ciudadano.normalizacion import nif, texto

SAL = b"sal-de-prueba"


def test_normalizar_nif_quita_prefijos_y_separadores():
    assert nif.normalizar_nif(" b-81.808.685 ") == "B81808685"
    assert nif.normalizar_nif("NIF: A28947117") == "A28947117"
    assert nif.normalizar_nif("ESB71350615") == "B71350615"
    assert nif.normalizar_nif("") is None
    assert nif.normalizar_nif(None) is None


def test_tipo_persona():
    assert nif.tipo_persona("B81808685") == "juridica"
    assert nif.tipo_persona("Q2866023A") == "juridica"
    assert nif.tipo_persona("12345678Z") == "fisica"
    assert nif.tipo_persona("X1234567L") == "fisica"
    assert nif.tipo_persona("***1234**") == "fisica"
    assert nif.tipo_persona("NL859153885B01") == "otro"
    # DNI sin el cero inicial y NIE con una cifra de más: personas físicas (D-007)
    assert nif.tipo_persona("1234567L") == "fisica"
    assert nif.tipo_persona("X12345678Z") == "fisica"
    assert nif.tipo_persona(None) == "desconocido"


def test_separar_nifs_de_una_ute():
    assert nif.separar_nifs("B82430596 / B83603191") == ["B82430596", "B83603191"]
    assert nif.separar_nifs("B74419714- A84664986-B87920476") == [
        "B74419714",
        "A84664986",
        "B87920476",
    ]
    assert nif.separar_nifs("b-81808685") == ["B81808685"]
    assert nif.separar_nifs(None) == []


def test_persona_fisica_queda_seudonimizada():
    identidad = nif.identificar("12345678Z", "Nombre Apellido Apellido", SAL)
    assert identidad["tipo_persona"] == "fisica"
    assert identidad["nif"] is None
    assert identidad["nombre"] is None
    assert identidad["adjudicatario_id"].startswith("PF-")
    assert "12345678" not in identidad["adjudicatario_id"]
    # El seudónimo es estable con la misma sal y cambia con otra.
    assert identidad["adjudicatario_id"] == nif.seudonimo("12345678Z", SAL)
    assert identidad["adjudicatario_id"] != nif.seudonimo("12345678Z", b"otra-sal")


def test_persona_juridica_conserva_nif_y_nombre():
    identidad = nif.identificar("b81808685", " EMPRESA DE PRUEBA, S.L. ", SAL)
    assert identidad == {
        "adjudicatario_id": "B81808685",
        "nif": "B81808685",
        "nombre": "EMPRESA DE PRUEBA, S.L.",
        "tipo_persona": "juridica",
    }


def test_ute_se_identifica_por_sus_miembros():
    identidad = nif.identificar("B83603191 / B82430596", "UTE PRUEBA", SAL)
    assert identidad["tipo_persona"] == "ute"
    assert identidad["adjudicatario_id"] == "UTE:B82430596+B83603191"


def test_importe_acepta_los_dos_formatos():
    assert texto.importe("3.630,00") == 3630.0
    assert texto.importe("539,96") == 539.96
    assert texto.importe("130680.0") == 130680.0
    assert texto.importe("33880") == 33880.0
    assert texto.importe("") is None
    assert texto.importe("n/d") is None


def test_fecha_larga():
    assert texto.fecha_larga("11 de febrero del 2026") == date(2026, 2, 11)
    assert texto.fecha_larga("01 de diciembre del 2015") == date(2015, 12, 1)
    assert texto.fecha_larga("31 de febrero del 2024") is None
    assert texto.fecha_larga("01 de enero del 0019") is None
    assert texto.fecha_larga(None) is None


def test_tipo_contrato_unifica_variantes():
    assert texto.tipo_contrato("Suministro") == "suministros"
    assert texto.tipo_contrato("SUMINISTROS") == "suministros"
    assert texto.tipo_contrato("Servicios") == "servicios"
    assert texto.tipo_contrato("obras") == "obras"
    assert texto.tipo_contrato("Concesión de servicios") == "concesion de servicios"


def test_entero():
    assert texto.entero("005") == 5
    assert texto.entero("") is None


def test_ute_con_persona_fisica_no_guarda_el_nombre():
    """D-007: el nombre de la UTE suele incluir el de la persona física."""
    identidad = nif.identificar("12345678Z - B83603191", "UTE NOMBRE APELLIDO - EMPRESA SL", SAL)
    assert identidad["tipo_persona"] == "fisica"
    assert identidad["nombre"] is None
    assert identidad["adjudicatario_id"].startswith("UTE:")
    assert "12345678Z" not in identidad["adjudicatario_id"]


def test_nif_extranjero_sin_forma_juridica_se_trata_como_persona_fisica():
    """D-007: entre los NIF extranjeros o erróneos hay particulares y empresarios individuales."""
    persona = nif.identificar("FR67382209765", "ANTOINE SCHMITT EI", SAL)
    assert persona["tipo_persona"] == "fisica"
    assert persona["nombre"] is None and persona["nif"] is None
    assert persona["adjudicatario_id"].startswith("PF-")
    empresa = nif.identificar("DE129360582", "BAYOOSOFT GmbH", SAL)
    assert empresa["tipo_persona"] == "otro"
    assert empresa["nombre"] == "BAYOOSOFT GmbH"


def test_filas_de_relleno_no_son_un_adjudicatario():
    # Casos reales de PLACSP y del portal: el NIF de la Comunidad o uno inventado con un
    # nombre que resume a varios adjudicatarios.
    for texto_nif, nombre in [
        ("S7800001E", "33 EMPRESAS ADJUDICATARIAS"),
        ("Q7850065I", "VER ORDEN DE ADJUDICACIÓN"),
        ("X000000E", "32 empresas adjudicatarias (PRIMERA ADJUDICACIÓN)"),
        ("VARIOSADJUDICATARIOS", "Varios adjudicatarios"),
        ("0000000000", "22 empresas adjudicatarias"),
        ("VERRESOLUCIÓNDEADJUDICACIÓN", "Ver Resolución de Adjudicación"),
        ("VARIOS", "VARIOS"),
    ]:
        identidad = nif.identificar(texto_nif, nombre, SAL)
        assert identidad["adjudicatario_id"] is None, texto_nif
        assert identidad["tipo_persona"] == "desconocido"
        assert identidad["nombre"] is None


def test_empresa_con_varios_en_el_nombre_no_es_relleno():
    identidad = nif.identificar("B10752806", "VARIOSMUNDOS S.L.", SAL)
    assert identidad["adjudicatario_id"] == "B10752806"
    assert nif.identificar("S7800001E", "Comunidad de Madrid", SAL)["tipo_persona"] == "juridica"
