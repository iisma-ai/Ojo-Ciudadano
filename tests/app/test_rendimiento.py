"""Sin tarjeta gráfica, entrada con el ojo plano y fondo quieto (D-044)."""

from pathlib import Path

from ojo_ciudadano.app import intro3d, rendimiento

CSS = (
    Path(__file__).parents[2] / "src" / "ojo_ciudadano" / "app" / "static" / "estilo.css"
).read_text(encoding="utf-8")


def test_la_prueba_descarta_el_dibujo_por_software():
    assert "failIfMajorPerformanceCaveat: true" in rendimiento.PRUEBA
    assert "swiftshader" in rendimiento.PRUEBA and "basic render" in rendimiento.PRUEBA
    assert "sessionStorage" in rendimiento.PRUEBA  # una prueba por pestaña


def test_la_entrada_usa_el_ojo_plano_sin_tarjeta_grafica():
    assert intro3d.JS.startswith(rendimiento.PRUEBA)
    antes_del_3d = intro3d.JS.split("setTimeout(() => empezar(true), 1200)")[0]
    assert "if (!ocHayGpu())" in antes_del_3d and "empezar(true)" in antes_del_3d


def test_sin_tarjeta_grafica_el_fondo_se_queda_quieto():
    regla = CSS.split("html.oc-sin-gpu .stApp::before")[1].split("}")[0]
    assert "animation: none" in regla
