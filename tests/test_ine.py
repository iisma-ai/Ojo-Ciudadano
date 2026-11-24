"""Población del INE para el reparto por habitante (D-038), sin red."""

import json

from ojo_ciudadano.ingesta import ine

# Fechas como las da la API del INE: medianoche hora de Madrid, en milisegundos.
SERIE = {
    "Data": [
        {"Fecha": 1735686000000, "Valor": 7113886.0},  # 2025-01-01
        {"Fecha": 1727733600000, "Valor": 7085755.0},  # 2024-10-01 (se ignora)
        {"Fecha": 1704063600000, "Valor": 7009268.0},  # 2024-01-01
    ]
}


def test_leer_serie_solo_1_de_enero():
    assert ine.leer_serie(json.dumps(SERIE)) == {2025: 7113886, 2024: 7009268}


def test_poblacion_desde_cache_y_ultimo_anio_disponible(tmp_path):
    (tmp_path / f"poblacion_{ine.SERIE}.json").write_text(json.dumps(SERIE), encoding="utf-8")
    serie = ine.poblacion(tmp_path, descargar_si_falta=False)
    assert serie["url_origen"].startswith("https://www.ine.es/")
    assert ine.del_anio(serie, 2025) == (2025, 7113886)
    assert ine.del_anio(serie, 2026) == (2025, 7113886)  # aún sin publicar: el último
    assert ine.del_anio(serie, 2020) is None


def test_sin_cache_ni_descarga(tmp_path):
    assert ine.poblacion(tmp_path, descargar_si_falta=False) is None
