"""Animación de entrada de la web (D-043): corta, suave y sin repintar."""

import re
from pathlib import Path

INTRO = (
    Path(__file__).parents[2] / "src" / "ojo_ciudadano" / "app" / "static" / "intro.html"
).read_text(encoding="utf-8")


def test_dura_tres_segundos_y_no_se_repite():
    duraciones = {float(d) for d in re.findall(r"animation:\s*[\w-]+\s+([\d.]+)s", INTRO)}
    assert duraciones == {3.0}
    assert "infinite" not in INTRO


def test_solo_anima_opacidad_y_transformaciones():
    for bloque in re.findall(r"@keyframes[^{]+\{(.*?)\}\s*\}", INTRO, flags=re.S):
        propiedades = set(re.findall(r"([a-z-]+)\s*:", bloque))
        assert propiedades <= {"opacity", "transform", "visibility"}, propiedades


def test_no_bloquea_ni_se_muestra_con_movimiento_reducido():
    assert "pointer-events: none" in INTRO
    assert "prefers-reduced-motion" in INTRO
    assert "{iris}" in INTRO and "{cristal}" in INTRO and "<script" not in INTRO


def test_el_ojo_de_cristal_son_dos_imagenes_svg():
    from ojo_ciudadano.app import ojo_cristal

    imagenes = ojo_cristal.imagenes()
    assert set(imagenes) == {"{iris}", "{cristal}"}
    assert all(i.startswith("data:image/svg+xml;base64,") for i in imagenes.values())
    assert ojo_cristal.svg_iris() == ojo_cristal.svg_iris()  # siempre el mismo dibujo
