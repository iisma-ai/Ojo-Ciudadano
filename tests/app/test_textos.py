from ojo_ciudadano.app import textos


def test_cada_indicador_tiene_ayuda():
    assert set(textos.AYUDA_INDICADOR) == set(textos.NOMBRES_INDICADOR)
    assert "R-06 · " in textos.lista_indicadores()


def test_fechas_de_descarga_nombran_cada_fuente():
    texto = textos.fechas_descarga(
        [
            {"fuente": "placsp", "fecha": "2026-11-16"},
            {"fuente": "portal_cm", "fecha": "2026-11-17"},
        ]
    )
    assert "Plataforma de Contratación del Sector Público el 2026-11-16" in texto
    assert "Comunidad de Madrid el 2026-11-17" in texto


def test_sin_fechas_no_se_muestra_nada():
    assert textos.fechas_descarga([]) == ""


def test_nombre_grupo_de_anomalias():
    assert textos.nombre_grupo("placsp · menor · obras") == (
        "Plataforma de Contratación del Sector Público · contrato menor · obras"
    )
    assert textos.nombre_grupo("portal_cm · licitación · servicios").endswith(
        "· licitación · servicios"
    )


def test_pie_cumple_las_condiciones_de_reutilizacion():
    """P-03: cita de la BDNS con la fórmula de su aviso legal, sin sugerir patrocinio y
    diciendo quién disocia los datos personales."""
    assert "Intervención General de la Administración del Estado" in textos.FUENTES
    assert "no patrocinado ni apoyado" in textos.PIE
    assert "Ojo Ciudadano seudonimiza" in textos.PIE


def test_aviso_menores_recientes_cita_la_ley():
    assert "art. 63.4" in textos.AVISO_MENORES_RECIENTES
    assert "no indica que se contrate menos" in textos.AVISO_MENORES_RECIENTES


def test_contexto_de_senal_enlaza_a_sus_fuentes():
    assert set(textos.CONTEXTO_SENAL) <= set(textos.NOMBRES_INDICADOR)
    for frase in textos.CONTEXTO_SENAL.values():
        assert "](https://" in frase
    assert "45,5 %" in textos.lista_indicadores()


def test_pregunta_del_pliego_segun_las_senales():
    pregunta = textos.pregunta_pliego("placsp:1", ["R-02", "R-03"])
    assert "placsp:1" in pregunta and "sin publicidad" in pregunta and "página" in pregunta
    assert "objeto" in textos.pregunta_pliego("placsp:1", ["R-04"])
