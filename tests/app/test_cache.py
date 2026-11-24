"""Caché de consultas de las pantallas: fuera de Streamlit consulta directamente."""

from ojo_ciudadano.app import cache


def test_fuera_de_la_web_consulta_la_base_que_se_le_pasa(base):
    assert cache.filas(base.con, "SELECT nombre FROM organo WHERE organo_id = ?", ["ORG"]) == [
        {"nombre": "Órgano"}
    ]
