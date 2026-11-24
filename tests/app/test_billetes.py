"""Frascos de billetes del mapa general (D-038), con datos sintéticos."""

import base64

from ojo_ciudadano.app import billetes


def _billetes(svg: str) -> list[str]:
    """Colores de los billetes del frasco (rectángulos con color de billete)."""
    colores = (*billetes.VERDES, billetes.GRIS)
    return [c for c in colores for _ in range(svg.count(f'fill="{c}"/>'))]


def test_billetes_de_cada_100():
    assert billetes.billetes_de_cada_100(39, 100) == 39
    assert billetes.billetes_de_cada_100(150, 100) == 100  # nunca se sale del frasco
    assert billetes.billetes_de_cada_100(5, 0) == 0
    assert billetes.texto_de_cada_100(38.6) == "39 de cada 100 €"
    assert billetes.texto_de_cada_100(0.2) == "menos de 1 de cada 100 €"


def test_frasco_lleva_un_billete_por_cada_euro_de_cada_100():
    assert len(_billetes(billetes.svg_frasco(39))) == 39
    assert len(_billetes(billetes.svg_frasco(100))) == 100
    assert len(_billetes(billetes.svg_frasco(0))) == 0


def test_frasco_grises_segun_lo_gastado():
    colores = _billetes(billetes.svg_frasco(10, gastado=0.7))
    assert colores.count(billetes.GRIS) == 3
    assert len(colores) == 10


def test_trozo_de_billete():
    svg = billetes.svg_frasco(2.5)
    assert len(_billetes(svg)) == 3  # dos enteros y medio
    anchos = [float(t.split('"')[0]) for t in svg.split('width="')[1:]]
    assert min(anchos) < max(a for a in anchos if a < 20)  # el último es más estrecho


def test_imagen_es_data_uri_de_svg():
    imagen = billetes.imagen_frasco(12, 0.5, centro=True)
    assert imagen.startswith("data:image/svg+xml;base64,")
    assert base64.b64decode(imagen.split(",", 1)[1]).startswith(b"<svg")


def test_mascota_es_el_ojo_del_logo():
    svg = billetes.svg_ojo()
    assert "M102 72 C98 38 80 15 46 15" in svg  # mismo trazo que static/logo.svg
    assert billetes.PUPILA in svg
