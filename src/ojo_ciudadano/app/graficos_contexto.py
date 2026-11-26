"""Gráficos del contexto presupuestario de la Comunidad de Madrid (D-024).

Mismas reglas que `app.graficos` (docs/marca.md): fondo transparente, paleta validada, sin barra
de herramientas y una frase en texto con cada gráfico (la pone la pantalla).
"""

import plotly.graph_objects as go

from ojo_ciudadano.app.graficos import AZUL, GRIS, GRIS_CLARO, _tema, color_categorico, partir
from ojo_ciudadano.app.graficos import CONFIG as GRAFICO_CONFIG  # noqa: F401 (lo usa la pantalla)
from ojo_ciudadano.app.textos import euros


def barras_horizontales(
    etiquetas: list[str], valores: list[float], formato=euros, color: str = AZUL, nombre: str = ""
) -> go.Figure:
    """Barras horizontales ordenadas de mayor a menor (la mayor arriba)."""
    pares = sorted(zip(etiquetas, valores, strict=True), key=lambda p: p[1])
    figura = go.Figure(
        go.Bar(
            x=[p[1] for p in pares],
            # nombres en líneas cortas: en el móvil, si no, se comen la barra o se cortan
            y=[partir(p[0], 28) for p in pares],
            orientation="h",
            marker={"color": color},
            text=[formato(p[1]) for p in pares],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}: %{text}<extra></extra>",
        )
    )
    figura.update_xaxes(visible=False)
    figura.update_yaxes(type="category", automargin=True)
    figura = _tema(figura, alto=max(220, 48 * len(pares) + 40))
    figura.update_layout(margin={"l": 10, "r": 120, "t": 10, "b": 10}, title=nombre or None)
    return figura


def ejecucion_organo(filas: list[dict]) -> go.Figure:
    """Crédito y obligaciones reconocidas de una consejería, año a año."""
    anios = [str(f["anio"]) for f in filas]
    figura = go.Figure()
    figura.add_bar(
        x=anios,
        y=[f["credito_actual"] for f in filas],
        name="Crédito actual",
        marker={"color": GRIS},
        hovertemplate="%{x}: %{y:,.0f} € de crédito<extra></extra>",
    )
    figura.add_bar(
        x=anios,
        y=[f["obligaciones"] for f in filas],
        name="Obligaciones reconocidas",
        marker={"color": AZUL},
        hovertemplate="%{x}: %{y:,.0f} € reconocidos<extra></extra>",
    )
    figura.update_layout(barmode="group")
    figura.update_yaxes(title="Euros", tickformat=",.0f")
    figura.update_xaxes(type="category")
    figura = _tema(figura, alto=280)
    figura.update_layout(showlegend=True, legend={"orientation": "h", "y": 1.14, "x": 0})
    return figura


def gasto_capitulos(filas: list[dict]) -> go.Figure:
    """Barras apiladas: en qué capítulo se reconoce el gasto cada año."""
    capitulos = sorted({f["capitulo"] for f in filas})
    figura = go.Figure()
    for i, capitulo in enumerate(capitulos):
        datos = [f for f in filas if f["capitulo"] == capitulo]
        figura.add_bar(
            x=[str(f["anio"]) for f in datos],
            y=[f["importe"] for f in datos],
            name=capitulo,
            marker={"color": color_categorico(i)},
            hovertemplate=capitulo + " %{x}: %{y:,.0f} €<extra></extra>",
        )
    figura.update_layout(barmode="stack")
    figura.update_yaxes(title="Euros", tickformat=",.0f")
    figura.update_xaxes(type="category")
    figura = _tema(figura, alto=380)
    figura.update_layout(showlegend=True, legend={"orientation": "h", "y": 1.2, "x": 0})
    return figura


def gastos_e_ingresos(filas: list[dict]) -> go.Figure:
    """Líneas: total de gastos y de ingresos de los presupuestos iniciales."""
    anios = [str(f["anio"]) for f in filas]
    figura = go.Figure()
    figura.add_scatter(
        x=anios,
        y=[f["gastos"] for f in filas],
        name="Gastos",
        mode="lines+markers",
        line={"color": AZUL},
        hovertemplate="Gastos %{x}: %{y:,.0f} €<extra></extra>",
    )
    figura.add_scatter(
        x=anios,
        y=[f["ingresos"] for f in filas],
        name="Ingresos",
        mode="lines+markers",
        line={"color": GRIS_CLARO, "dash": "dot"},
        hovertemplate="Ingresos %{x}: %{y:,.0f} €<extra></extra>",
    )
    figura.update_yaxes(title="Euros", tickformat=",.0f")
    figura.update_xaxes(type="category")
    figura = _tema(figura, alto=300)
    figura.update_layout(showlegend=True, legend={"orientation": "h", "y": 1.14, "x": 0})
    return figura


def convenios_por_anio(filas: list[dict]) -> go.Figure:
    """Convenios vigentes por año de firma, con y sin financiación indicada."""
    por_anio: dict[int, list[int]] = {}
    for f in filas:
        total = por_anio.setdefault(f["anio"], [0, 0])
        total[0] += f["n"] - f["n_con_financiacion"]
        total[1] += f["n_con_financiacion"]
    anios = sorted(por_anio)
    figura = go.Figure()
    figura.add_bar(
        x=[str(a) for a in anios],
        y=[por_anio[a][0] for a in anios],
        name="Sin financiación indicada",
        marker={"color": GRIS},
        hovertemplate="%{x}: %{y:,.0f} convenios<extra></extra>",
    )
    figura.add_bar(
        x=[str(a) for a in anios],
        y=[por_anio[a][1] for a in anios],
        name="Con financiación indicada",
        marker={"color": AZUL},
        hovertemplate="%{x}: %{y:,.0f} convenios<extra></extra>",
    )
    figura.update_layout(barmode="stack")
    figura.update_yaxes(title="Convenios", tickformat=",.0f")
    figura.update_xaxes(type="category")
    figura = _tema(figura, alto=280)
    figura.update_layout(showlegend=True, legend={"orientation": "h", "y": 1.14, "x": 0})
    return figura
