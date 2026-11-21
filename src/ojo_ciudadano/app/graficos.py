"""Gráficos de la interfaz (D-023, estudios E-01 a E-06 de docs/11-accesibilidad.md).

Un gráfico por señal, pensado para lo que mide. Reglas comunes (docs/marca.md):
- «Este contrato» o «esta empresa» en azul; el contexto, en gris azulado.
- Fondo transparente, tipografía Inter, rejilla discreta, sin barra de herramientas.
- Cada gráfico va con una frase que dice lo mismo en texto (texto alternativo).
Las funciones reciben los diccionarios de `app.datos` y devuelven una figura de Plotly.
"""

from datetime import timedelta

import plotly.graph_objects as go

from ojo_ciudadano.app.textos import euros, porcentaje

AZUL = "#3D8BFD"
GRIS = "#4A5A75"
GRIS_CLARO = "#93A1B8"
TEXTO = "#E7ECF3"
REJILLA = "#24314A"
AMBAR = "#F2B544"

CONFIG = {"displayModeBar": False, "responsive": True}


def _tema(figura: go.Figure, alto: int = 240) -> go.Figure:
    figura.update_layout(
        height=alto,
        margin={"l": 10, "r": 10, "t": 24, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, sans-serif", "color": TEXTO, "size": 13},
        showlegend=False,
        hoverlabel={"bgcolor": "#131C2E", "bordercolor": REJILLA, "font": {"color": TEXTO}},
        bargap=0.25,
        separators=",.",  # formato español: 1.234,5
    )
    figura.update_xaxes(gridcolor=REJILLA, zeroline=False, linecolor=REJILLA, automargin=True)
    figura.update_yaxes(gridcolor=REJILLA, zeroline=False, linecolor=REJILLA, automargin=True)
    return figura


def ofertas(detalle: dict) -> go.Figure:
    """E-01: cuántos contratos parecidos recibieron 1, 2, 3… ofertas; la barra de este
    contrato en azul."""
    x = [n for n, _ in detalle["distribucion"]]
    y = [c for _, c in detalle["distribucion"]]
    etiquetas = ["10 o más" if n == 10 else str(n) for n in x]
    colores = [AZUL if n == min(detalle["ofertas"], 10) else GRIS for n in x]
    figura = go.Figure(
        go.Bar(
            x=etiquetas,
            y=y,
            marker={"color": colores, "cornerradius": 4},
            hovertemplate="%{x} ofertas: %{y} contratos<extra></extra>",
        )
    )
    figura.update_xaxes(title="Ofertas recibidas", type="category")
    figura.update_yaxes(title="Contratos parecidos")
    return _tema(figura)


def sin_anuncio(detalle: dict) -> go.Figure:
    """E-02: del dinero del organismo, cuánto se adjudicó sin anuncio público."""
    total = detalle["sin_anuncio"] + detalle["con_anuncio"]
    partes = [
        ("Sin anuncio público", detalle["sin_anuncio"], AZUL),
        ("Con anuncio público", detalle["con_anuncio"], GRIS),
    ]
    figura = go.Figure()
    for nombre, valor, color in partes:
        figura.add_bar(
            y=[""],
            x=[valor],
            orientation="h",
            name=nombre,
            marker={"color": color},
            hovertemplate=f"{nombre}: %{{x:,.0f}} €<extra></extra>",
        )
        figura.data[-1].name = f"{nombre} ({porcentaje(valor / total)})" if total else nombre
    figura.update_layout(barmode="stack")
    figura.update_xaxes(visible=False)
    figura.update_yaxes(visible=False)
    figura = _tema(figura, alto=120)
    figura.update_layout(
        showlegend=True,
        legend={"orientation": "h", "y": -0.15, "x": 0, "traceorder": "normal"},
    )
    return figura


def suma_doce_meses(contratos: list[dict]) -> list[float]:
    """Para cada contrato menor, la suma de los de los 12 meses anteriores (incluido él):
    la misma ventana que usa R-03."""
    sumas = []
    for c in contratos:
        desde = c["fecha"] - timedelta(days=364)
        sumas.append(sum(o["importe"] for o in contratos if desde <= o["fecha"] <= c["fecha"]))
    return sumas


def menores(detalle: dict, contrato_id: str) -> go.Figure:
    """E-03: cada contrato menor como un punto (tamaño = importe) y la línea de lo que suman
    los últimos 12 meses frente al límite legal."""
    contratos = detalle["contratos"]
    fechas = [c["fecha"] for c in contratos]
    sumas = suma_doce_meses(contratos)
    figura = go.Figure()
    figura.add_scatter(
        x=fechas,
        y=sumas,
        mode="lines+markers",
        line={"color": GRIS_CLARO, "width": 2, "shape": "hv"},
        marker={
            "size": [16 if c["contrato_id"] == contrato_id else 8 for c in contratos],
            "color": [AZUL if c["contrato_id"] == contrato_id else GRIS_CLARO for c in contratos],
            "line": {"width": 2, "color": "#0B1120"},
        },
        customdata=[[c["importe"], c["titulo"] or ""] for c in contratos],
        hovertemplate=(
            "%{x|%d/%m/%Y}: contrato de %{customdata[0]:,.0f} €<br>"
            "Suma de los 12 meses anteriores: %{y:,.0f} €<br>%{customdata[1]}<extra></extra>"
        ),
    )
    figura.add_hline(
        y=detalle["umbral"],
        line={"color": AMBAR, "dash": "dash", "width": 2},
        annotation_text=f"Límite: {euros(detalle['umbral'])}",
        annotation_font_color=AMBAR,
        annotation_position="top left",
    )
    figura.update_yaxes(title="Suma en 12 meses (€ con IVA)", rangemode="tozero", tickformat=",.0f")
    figura.update_xaxes(tickformat="%m/%Y")
    return _tema(figura, alto=280)


def reparto(detalle: dict) -> go.Figure:
    """E-04: cómo se reparte el dinero del organismo en este tipo de contrato; la empresa de
    este contrato en azul."""
    partes = detalle["partes"]
    figura = go.Figure(
        go.Pie(
            labels=[
                f"{p['nombre']} ({porcentaje(p['importe'] / detalle['total'])})" for p in partes
            ],
            values=[p["importe"] for p in partes],
            hole=0.62,
            sort=False,
            direction="clockwise",
            marker={
                "colors": [AZUL if p["es_este"] else GRIS for p in partes],
                "line": {"color": "#0B1120", "width": 2},
            },
            textinfo="none",
            hovertemplate="%{label}: %{value:,.0f} € (%{percent})<extra></extra>",
        )
    )
    if detalle["cuota"] is not None:
        figura.add_annotation(
            text=f"<b>{porcentaje(detalle['cuota'])}</b>",
            showarrow=False,
            font={"size": 22, "color": TEXTO},
        )
    figura.update_layout(showlegend=True, legend={"font": {"size": 12}})
    figura = _tema(figura, alto=260)
    figura.update_layout(showlegend=True)
    return figura


def subida(detalle: dict) -> go.Figure:
    """E-05: precio adjudicado y lo que se añadió después, con la referencia del 20 %."""
    adjudicado = detalle["adjudicado"] or 0
    modificaciones = detalle["modificaciones"] or 0
    figura = go.Figure()
    figura.add_bar(
        y=[""],
        x=[adjudicado],
        orientation="h",
        marker={"color": GRIS},
        text="Precio adjudicado",
        textposition="inside",
        hovertemplate="Adjudicado: %{x:,.0f} €<extra></extra>",
    )
    figura.add_bar(
        y=[""],
        x=[modificaciones],
        orientation="h",
        marker={"color": AZUL},
        text=f"+{porcentaje(modificaciones / adjudicado)}" if adjudicado else "",
        textposition="inside",
        hovertemplate="Añadido después: %{x:,.0f} €<extra></extra>",
    )
    figura.add_vline(
        x=adjudicado * 1.2,
        line={"color": AMBAR, "dash": "dash", "width": 2},
        annotation_text="+20 %",
        annotation_font_color=AMBAR,
        annotation_position="top",
        annotation_yshift=6,
    )
    figura.update_layout(barmode="stack")
    figura.update_xaxes(title="Euros (con IVA)", tickformat=",.0f")
    figura.update_yaxes(visible=False)
    return _tema(figura, alto=140)


def rebaja(detalle: dict) -> go.Figure:
    """E-06: precio de salida frente al adjudicado."""
    presupuesto = detalle["presupuesto"] or 0
    adjudicado = detalle["adjudicado"] or 0
    figura = go.Figure(
        go.Bar(
            y=["Precio de salida", "Precio adjudicado"],
            x=[presupuesto, adjudicado],
            orientation="h",
            marker={"color": [GRIS, AZUL], "cornerradius": 4},
            text=[f"Precio de salida: {euros(presupuesto)}", f"Adjudicado: {euros(adjudicado)}"],
            textposition="inside",
            insidetextanchor="start",
            hovertemplate="%{y}: %{x:,.0f} €<extra></extra>",
        )
    )
    figura.update_xaxes(visible=False)
    figura.update_yaxes(autorange="reversed", visible=False)
    return _tema(figura, alto=120)
