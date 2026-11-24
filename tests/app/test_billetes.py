"""Treemap de billetes del mapa general (D-038), con datos sintéticos."""

import math

import pytest

from ojo_ciudadano.app import billetes


def test_treemap_reparte_el_area_en_proporcion_y_sin_salirse():
    valores = [60.0, 25.0, 10.0, 5.0]
    rects = billetes.treemap(valores, 0, 0, 1000, 500)
    assert len(rects) == len(valores)
    area_total = 1000 * 500
    for valor, (x, y, ancho, alto) in zip(valores, rects, strict=True):
        assert ancho * alto == pytest.approx(area_total * valor / sum(valores))
        assert x >= -1e-6 and y >= -1e-6
        assert x + ancho <= 1000 + 1e-6 and y + alto <= 500 + 1e-6


def test_treemap_vacio():
    assert billetes.treemap([], 0, 0, 100, 100) == []


def test_valor_billete_es_redondo_y_da_unos_cientos_de_billetes():
    valor = billetes.valor_billete(33_296e6)
    assert valor == 100e6
    assert billetes.valor_billete(160e6, objetivo=160) == 1e6
    assert billetes.texto_valor(100e6) == "100 millones de €"
    assert billetes.texto_valor(1e6) == "1 millón de €"


def test_rejilla_caben_todos_los_billetes():
    columnas, filas, alto = billetes.rejilla(12.4, 400, 200)
    assert columnas * filas >= 13
    assert columnas * alto * billetes.PROPORCION <= 400 + 1e-6
    assert filas * alto <= 200 + 1e-6


def test_svg_cuenta_billetes_y_grises_segun_lo_gastado():
    bloques = [billetes.Bloque(id="a", nombre="A", importe=10e6, gastado=0.7)]
    svg = billetes.svg_treemap(bloques, valor=1e6)
    assert svg.count('href="#billete"') == 10
    assert svg.count("b vacio") == 3


def test_svg_trozo_de_billete_y_textos_escapados():
    bloques = [billetes.Bloque(id="x", nombre="<Empresa & Cía>", importe=2.5e6)]
    svg = billetes.svg_treemap(bloques, valor=1e6)
    assert svg.count('href="#billete"') == math.ceil(2.5)
    assert 'overflow="hidden"' in svg  # el medio billete se recorta
    assert "<Empresa" not in svg and "&lt;Empresa &amp; Cía&gt;" in svg


def test_cuota_de_cada_100():
    assert billetes.de_cada_100(39, 100) == "39 € de cada 100"
    assert billetes.de_cada_100(0.2, 100) == "menos de 1 € de cada 100"
