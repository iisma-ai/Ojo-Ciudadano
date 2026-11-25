"""RAG documental (D-030, bloques B y C): pliegos y resoluciones, sin red ni PDF reales.

Los PDF se simulan con su caché: un fichero que empieza por «%PDF-» y, al lado, el JSON con el
texto de cada página, que es lo que lee `ingesta.documentos.paginas`.
"""

import json
from datetime import date

import pytest

from ojo_ciudadano.asistente import agente, bateria, documentos, openrouter
from ojo_ciudadano.asistente.agente import (
    LlamadaBuscarDocumento,
    LlamadaBuscarResoluciones,
    TextoFinal,
)
from ojo_ciudadano.ingesta import documentos as pdf

URL_PCAP = "https://contratos-publicos.comunidad.madrid/sites/default/files/PCON/pcap_1.pdf"
URL_PPT = "https://contratos-publicos.comunidad.madrid/sites/default/files/PCON/ppt_1.pdf"
URL_RES = "https://www.comunidad.madrid/tacp/file/1/download?token=a"
URL_RES2 = "https://www.comunidad.madrid/tacp/file/2/download?token=b"

PCAP = [
    "Índice. Capítulo I. Características del contrato.",
    "Cláusula 1. Procedimiento negociado sin publicidad por ausencia de competencia por "
    "razones técnicas, artículo 168.a.2 de la LCSP.",
    "Cláusula 5. Solvencia económica: volumen anual de negocios de 200.000 euros.",
]
PPT = ["Prescripciones técnicas del mantenimiento de jardines.", "Horario de los trabajos."]
RES = [
    "Recurso nº 1/2026. Resolución nº 1/2026. Contra los pliegos del contrato «Servicio de "
    "mantenimiento de las zonas ajardinadas del hospital universitario».",
    "Fundamentos. Los criterios de adjudicación sujetos a juicio de valor carecen de "
    "parámetros. Firma la representante con DNI 12345678Z.",
]
RES2 = ["Recurso nº 2/2026. Se inadmite el recurso por extemporáneo, fuera de plazo."]


def _cachear(carpeta, url, tipo, paginas):
    ruta = pdf.ruta_local(url, tipo, carpeta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_bytes(b"%PDF-1.4 prueba")
    ruta.with_suffix(".json").write_text(json.dumps(paginas), encoding="utf-8")
    return ruta


@pytest.fixture
def carpeta(tmp_path, monkeypatch):
    _cachear(tmp_path, URL_PCAP, "pliegos", PCAP)
    _cachear(tmp_path, URL_PPT, "pliegos", PPT)
    _cachear(tmp_path, URL_RES, "tacpcm", [pdf.ocultar_identificadores(p) for p in RES])
    _cachear(tmp_path, URL_RES2, "tacpcm", RES2)
    monkeypatch.setattr(pdf, "CARPETA", tmp_path)
    monkeypatch.setattr(documentos, "_paginas_de", _paginas_en(tmp_path))
    return tmp_path


def _paginas_en(carpeta):
    def leer(documento, _carpeta=None):
        ruta = pdf.descargar(
            documento["url_documento"], documentos.CARPETA_TIPO[documento["tipo"]], carpeta
        )
        return pdf.paginas(ruta), pdf.fecha_descarga(ruta).isoformat()

    return leer


@pytest.fixture
def con(base, carpeta):
    base.contrato("placsp:1", titulo="Mantenimiento de jardines", procedimiento="Abierto")
    base.contrato("portal_cm:9", fuente="portal_cm", duplicado_de="placsp:1")
    base.contrato("portal_cm:menor", fuente="portal_cm", es_menor=True)
    for orden, (tipo, url) in enumerate((("pcap", URL_PCAP), ("ppt", URL_PPT)), start=1):
        base._insertar(
            "contrato_documento",
            {
                "contrato_id": "placsp:1",
                "orden": orden,
                "tipo": tipo,
                "nombre": url.rsplit("/", 1)[-1],
                "url_documento": url,
                "fuente": "placsp",
                "url_origen": "https://ejemplo.test/placsp:1",
                "fecha_descarga": date(2026, 11, 23),
            },
        )
    for numero, tipo, url in (
        ("1/2026", "Estimatoria", URL_RES),
        ("2/2026", "Inadmisión", URL_RES2),
    ):
        base._insertar(
            "recurso_especial",
            {
                "resolucion_id": f"tacpcm:{numero}",
                "numero": numero,
                "fecha": date(2026, 1, 10),
                "procedencia": "Hospitales",
                "tipo_resolucion": tipo,
                "acto_recurrido": "Pliegos",
                "fuente": "tacpcm",
                "url_origen": f"https://www.comunidad.madrid/tacp/resolucion/{numero}",
                "url_documento": url,
                "fecha_descarga": date(2026, 11, 23),
            },
        )
    documentos.construir_resoluciones(base.con, carpeta)
    return base.con


# ------------------------------------------------------------------ descarga y texto


def test_solo_baja_pdf_de_portales_oficiales(tmp_path):
    with pytest.raises(pdf.DocumentoNoDisponible):
        pdf.descargar("https://ejemplo.com/pliego.pdf", "pliegos", tmp_path)
    with pytest.raises(pdf.DocumentoNoDisponible):
        pdf.descargar("http://contratos-publicos.comunidad.madrid/x.pdf", "pliegos", tmp_path)
    assert pdf._permitida("https://contratos-publicos.comunidad.madrid/sites/x.pdf")
    assert not pdf._permitida("https://comunidad.madrid.ejemplo.com/x.pdf")


def test_tapa_dni_y_nie_con_y_sin_separadores():
    texto = pdf.ocultar_identificadores("DNI 12345678Z, 12.345.678-Z y NIE X1234567L; CP 28010")
    assert "12345678" not in texto and "X1234567" not in texto
    assert texto.count(pdf.OCULTO) == 3 and "28010" in texto
    assert not bateria.PATRON_DNI.search(texto)


def test_paginas_usa_la_cache(carpeta):
    ruta = pdf.ruta_local(URL_PCAP, "pliegos", carpeta)
    assert pdf.paginas(ruta) == PCAP


# ------------------------------------------------------------------------- búsqueda


def test_mejores_paginas_y_extracto():
    assert documentos.mejores_paginas(PCAP, "¿qué solvencia económica pide?")[0] == 2
    assert documentos.mejores_paginas(PCAP, "sin publicidad razones técnicas")[0] == 1
    assert documentos.mejores_paginas(PCAP, "de la el") == []  # solo palabras vacías
    largo = "relleno " * 400 + "la solvencia económica exigida" + " relleno" * 400
    trozo = documentos.extracto(largo, ["solvencia"], largo=200)
    assert "solvencia" in trozo and trozo.startswith("…") and len(trozo) < 220


def test_busca_en_los_pliegos_del_contrato(con, carpeta):
    r = documentos.buscar_en_documento(con, "placsp:1", "supuesto sin publicidad", carpeta=carpeta)
    assert r["documento"] == "placsp:1" and r["columnas"] == documentos.COLUMNAS
    primera = dict(zip(r["columnas"], r["filas"][0], strict=True))
    assert primera["pagina"] == 2 and "168.a.2" in primera["extracto"]
    assert primera["enlace_pagina"] == f"{URL_PCAP}#page=2"
    assert primera["documento"].startswith("Pliego de cláusulas administrativas particulares")
    assert r["fuente"] == documentos.NOMBRE_PLACSP and r["fecha_descarga"]
    solo_ppt = documentos.buscar_en_documento(con, "placsp:1", "jardines", "ppt", carpeta)
    assert {f[0].split(" · ")[0] for f in solo_ppt["filas"]} == {documentos.TIPOS["ppt"]}


def test_licitacion_del_portal_duplicada_usa_los_pliegos_de_placsp(con, carpeta):
    r = documentos.buscar_en_documento(con, "portal_cm:9", "solvencia", carpeta=carpeta)
    assert r["filas"] and r["documentos"][0]["url_documento"] == URL_PCAP


def test_sin_pliegos_lo_dice(con, carpeta):
    with pytest.raises(documentos.DocumentoNoDisponible, match="No hay documentos"):
        documentos.buscar_en_documento(con, "portal_cm:menor", "solvencia", carpeta=carpeta)
    with pytest.raises(documentos.DocumentoNoDisponible, match="vacía"):
        documentos.buscar_en_documento(con, "placsp:1", "  de la ", carpeta=carpeta)


def test_resolucion_concreta_con_dni_tapado(con, carpeta):
    r = documentos.buscar_en_documento(con, "tacpcm:1/2026", "juicio de valor", carpeta=carpeta)
    texto = json.dumps(r["filas"], ensure_ascii=False)
    assert "juicio de valor" in texto and "12345678" not in texto
    assert r["fuente"] == documentos.NOMBRE_TACPCM


def test_busca_en_todas_las_resoluciones(con):
    assert documentos.resoluciones_disponibles(con)
    r = documentos.buscar_resoluciones(con, "criterios juicio de valor")
    filas = [dict(zip(r["columnas"], f, strict=True)) for f in r["filas"]]
    assert [f["resolucion"] for f in filas] == ["1/2026"]
    assert filas[0]["pagina"] == 2 and filas[0]["enlace_pagina"].endswith("#page=2")
    assert r["resoluciones_indexadas"] == 2


def test_filtro_estimatoria_no_trae_inadmisiones(con):
    assert documentos.buscar_resoluciones(con, "recurso", "Estimatoria")["filas"][0][0] == "1/2026"
    inadmitidas = documentos.buscar_resoluciones(con, "recurso", "Inadmisión")["filas"]
    assert [f[0] for f in inadmitidas] == ["2/2026"]


def test_sin_indice_de_resoluciones_lo_dice(base):
    with pytest.raises(documentos.DocumentoNoDisponible, match="no está disponible"):
        documentos.buscar_resoluciones(base.con, "criterios")


# ----------------------------------------------------------------------------- agente


def test_el_agente_lee_el_pliego_y_lo_marca_como_datos(con):
    salidas = [
        LlamadaBuscarDocumento("placsp:1", "sin publicidad razones técnicas", "pcap"),
        TextoFinal(
            "Según el pliego de cláusulas administrativas (pág. 2), alega ausencia de "
            "competencia por razones técnicas. Fuente: Plataforma de Contratación del Sector "
            "Público (pliego, pág. 2), descargado el 2026-11-23."
        ),
    ]
    recibidos = []

    def modelo(sistema, mensajes):
        recibidos.append((sistema, [dict(m) for m in mensajes]))
        return salidas.pop(0)

    r = agente.responder(con, modelo, "¿Qué supuesto alega el pliego de placsp:1?")
    assert r.retencion is None and r.errores == []
    assert r.consultas[0]["documento"] == "placsp:1"
    sistema, mensajes = recibidos[1]
    assert "Pliegos y resoluciones del Tribunal" in sistema
    assert mensajes[-1]["contenido"].startswith("Extractos de documentos oficiales")
    assert mensajes[-2]["argumentos"] == {
        "identificador": "placsp:1",
        "consulta": "sin publicidad razones técnicas",
        "tipo": "pcap",
    }
    evaluacion = bateria.evaluar_respuesta(
        con,
        bateria.PreguntaPrueba("X", "p", "documento", "c", documento="placsp:1"),
        r.consultas,
        r.texto,
    )
    assert evaluacion["datos_ok"] and evaluacion["avisos"] == []


def test_el_error_de_documento_vuelve_al_modelo(con):
    salidas = [
        LlamadaBuscarDocumento("portal_cm:menor", "solvencia"),
        LlamadaBuscarResoluciones("juicio de valor", "Estimatoria"),
        TextoFinal("Ese contrato no tiene pliegos enlazados. La resolución 1/2026 (pág. 2)…"),
    ]
    r = agente.responder(con, lambda s, m: salidas.pop(0), "¿Qué dice el pliego?")
    assert len(r.errores) == 1 and "No hay documentos" in r.errores[0]
    assert r.consultas[0]["documento"] == "resoluciones"


def test_openrouter_traduce_las_herramientas_de_documentos():
    def respuesta(nombre, argumentos):
        llamada = {"function": {"name": nombre, "arguments": json.dumps(argumentos)}}
        return {"choices": [{"message": {"tool_calls": [llamada]}}]}

    assert openrouter.interpretar(
        respuesta("buscar_en_documento", {"identificador": "placsp:1", "consulta": "solvencia"})
    ) == LlamadaBuscarDocumento("placsp:1", "solvencia", None)
    assert openrouter.interpretar(
        respuesta("buscar_resoluciones", {"consulta": "plazo", "tipo_resolucion": "Estimatoria"})
    ) == LlamadaBuscarResoluciones("plazo", "Estimatoria")
    llamada = agente.mensaje_llamada(LlamadaBuscarResoluciones("plazo"))
    assert llamada == {
        "rol": "llamada",
        "herramienta": "buscar_resoluciones",
        "argumentos": {"consulta": "plazo"},
    }


def test_el_texto_de_documentos_no_es_consultable_por_sql(con):
    from ojo_ciudadano.asistente import sql_seguro

    assert "contrato_documento" in sql_seguro.TABLAS_PERMITIDAS
    assert documentos.TABLA_RESOLUCIONES not in sql_seguro.TABLAS_PERMITIDAS
    with pytest.raises(sql_seguro.SQLNoPermitido):
        sql_seguro.validar(con, f"SELECT texto FROM {documentos.TABLA_RESOLUCIONES}")


# ------------------------------------------------- revisión legal (D-032): personas y cifras


def test_tapa_nombres_con_tratamiento_y_firmas():
    texto = pdf.ocultar_personas(
        "D. Juan Pérez García, en nombre y representación de ACME, S.L., y Dña. Ana de la "
        "Fuente López recurren.\nFdo.: Pedro Ruiz Gómez\nEl Tribunal resuelve."
    )
    minusculas = pdf.ocultar_personas("formulado por doña Isabel García Díaz contra el acuerdo")
    assert "Isabel" not in minusculas and "contra el acuerdo" in minusculas
    assert texto.startswith("D. [nombre oculto], en nombre y representación de ACME, S.L.")
    assert "Dña. [nombre oculto] recurren" in texto
    assert "Pérez" not in texto and "Fuente" not in texto and "Ruiz" not in texto
    assert "Fdo.: [firma oculta]" in texto and "El Tribunal resuelve." in texto


def test_la_cache_antigua_tambien_se_tapa(tmp_path):
    ruta = _cachear(tmp_path, URL_RES, "tacpcm", ["Recurre D. Juan Pérez, con DNI 12345678Z."])
    (pagina,) = pdf.paginas(ruta)
    assert "Juan" not in pagina and "12345678" not in pagina


def test_no_busca_personas_en_los_documentos(con, carpeta):
    for consulta in ("D. Juan Pérez", "12345678Z"):
        with pytest.raises(documentos.DocumentoNoDisponible, match="no por personas"):
            documentos.buscar_resoluciones(con, consulta)
        with pytest.raises(documentos.DocumentoNoDisponible, match="no por personas"):
            documentos.buscar_en_documento(con, "placsp:1", consulta, carpeta=carpeta)


def test_pagina_con_posible_persona_fisica_no_se_muestra():
    pagina = "El licitador, que actúa en nombre propio, recurre la exclusión por la solvencia."
    assert documentos.extracto(pagina, ["solvencia"]) == documentos.EXTRACTO_OCULTO


def test_cifras_que_no_estan_en_los_extractos_se_retienen(con):
    def responde(texto):
        salidas = [LlamadaBuscarDocumento("placsp:1", "solvencia económica"), TextoFinal(texto)]
        return agente.responder(con, lambda s, m: salidas.pop(0), "¿Qué solvencia pide?")

    bien = responde("Pide un volumen de negocios de 200.000 € (pág. 3). Fuente: …")
    assert bien.retencion is None
    mal = responde("Pide un volumen de negocios de 350.000 € (pág. 3). Fuente: …")
    assert mal.retencion == agente.RETENCION_CIFRAS
    assert "Da cifras que no están en los extractos" in mal.avisos
