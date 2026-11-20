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
