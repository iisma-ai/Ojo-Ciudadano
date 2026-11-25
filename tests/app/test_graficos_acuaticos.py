"""Estilo acuático de los gráficos de Plotly (D-055): cristal, burbujas y cuadro con nuestra letra."""

import plotly.graph_objects as go

from ojo_ciudadano.app import graficos


def test_barras_de_cristal_y_cuadro_con_nuestra_letra():
    figura = graficos._tema(go.Figure(go.Bar(x=[1, 2], y=["a", "b"], orientation="h")))
    barra = figura.data[0]
    assert barra.opacity == graficos.OPACIDAD_CRISTAL
    assert barra.marker.line.color == graficos.BORDE_CRISTAL
    assert figura.layout.barcornerradius == 6
    etiqueta = figura.layout.hoverlabel
    assert etiqueta.font.family.startswith("Inter")
    assert etiqueta.namelength == -1  # el nombre no se corta


def test_puntos_como_burbujas_sin_pisar_un_borde_propio():
    figura = go.Figure(
        [
            go.Scatter(x=[1], y=[1], mode="markers"),
            go.Scatter(x=[2], y=[2], mode="markers", marker={"line": {"color": "#fff"}}),
            go.Scatter(x=[1, 2], y=[1, 2], mode="lines"),
        ]
    )
    figura = graficos._tema(figura)
    assert figura.data[0].marker.gradient.type == "radial"
    assert figura.data[0].marker.line.color == graficos.BORDE_CRISTAL
    assert figura.data[1].marker.line.color == "#fff"
    assert figura.data[2].marker.gradient.type is None  # las líneas no cambian
    figura.to_json()  # Plotly acepta todo lo que se ha puesto
