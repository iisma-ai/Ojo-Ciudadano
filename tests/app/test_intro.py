"""Animación de entrada de la web (D-043): corta, suave y sin repintar."""

import re
from pathlib import Path

INTRO = (
    Path(__file__).parents[2] / "src" / "ojo_ciudadano" / "app" / "static" / "intro.html"
).read_text(encoding="utf-8")


def test_dura_un_segundo_y_medio_y_no_se_repite():
    duraciones = {float(d) for d in re.findall(r"animation:\s*[\w-]+\s+([\d.]+)s", INTRO)}
    assert duraciones == {1.5}
    assert "infinite" not in INTRO


def test_solo_anima_opacidad_y_transformaciones():
    for bloque in re.findall(r"@keyframes[^{]+\{(.*?)\}\s*\}", INTRO, flags=re.S):
        propiedades = set(re.findall(r"([a-z-]+)\s*:", bloque))
        assert propiedades <= {"opacity", "transform", "visibility"}, propiedades


def test_no_bloquea_ni_se_muestra_con_movimiento_reducido():
    assert "pointer-events: none" in INTRO
    assert "prefers-reduced-motion" in INTRO
    assert "{logo}" in INTRO and "<script" not in INTRO
