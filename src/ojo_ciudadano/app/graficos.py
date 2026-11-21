"""Gráficos de la interfaz (D-023, estudios E-01 a E-06 de docs/11-accesibilidad.md).

Un gráfico por señal, pensado para lo que mide. Reglas comunes (docs/marca.md):
- «Este contrato» o «esta empresa» en azul; el contexto, en gris azulado.
- Fondo transparente, tipografía Inter, rejilla discreta, sin barra de herramientas.
- Cada gráfico va con una frase que dice lo mismo en texto (texto alternativo).
Las funciones reciben los diccionarios de `app.datos` y devuelven una figura de Plotly.
"""

import math
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

# Paleta categórica para distinguir entidades (organismos en el mapa del dinero), en orden fijo.
# Validada sobre el fondo #0B1120 con el validador de la guía de visualización (luminosidad,
# croma, separación para daltonismo y contraste). Del 8.º en adelante, gris.
CATEGORICOS = ["#3987E5", "#D95926", "#199E70", "#C98500", "#D55181", "#0CA30C", "#9085E9"]
GRIS_OTROS = "#5B6B86"


def color_categorico(posicion: int) -> str:
    return CATEGORICOS[posicion] if posicion < len(CATEGORICOS) else GRIS_OTROS


def transparente(color: str, alfa: float) -> str:
    """«#RRGGBB» → «rgba(r, g, b, alfa)»."""
    r, g, b = (int(color[i : i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r}, {g}, {b}, {alfa})"


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


# --- Ficha de empresa (A-05) ---


def partir(texto: str, ancho: int = 22) -> str:
    """Parte un nombre largo en líneas (<br>) para que quepa en una caja estrecha."""
    lineas, actual = [], ""
    for palabra in texto.split():
        if actual and len(actual) + 1 + len(palabra) > ancho:
            lineas.append(actual)
            actual = palabra
        else:
            actual = f"{actual} {palabra}".strip()
    lineas.append(actual)
    return "<br>".join(lineas)


def reparto_organismos(
    filas: list[dict],
    maximo: int = 12,
    campo: str = "organo",
    otros: str = "organismos",
    gris: tuple[str, ...] = (),
    agrupar_resto: bool = True,
) -> go.Figure:
    """Mapa de áreas (área = importe): de qué organismos tiene contratos una empresa, o a qué
    empresas adjudica un organismo (`campo="nombre"`). Un color por entidad; a partir del
    `maximo`, agrupadas en «Otros N …». Las de `gris` (p. ej. el agregado de personas
    físicas) van siempre en gris."""
    filas = sorted(filas, key=lambda f: f["importe"], reverse=True)
    principales, resto = filas[:maximo], filas[maximo:]
    if not agrupar_resto:
        resto = []
    etiquetas = [f[campo] for f in principales]
    valores = [f["importe"] for f in principales]
    numeros = [f["n"] for f in principales]
    if resto:
        etiquetas.append(f"Otros {len(resto)} {otros}")
        valores.append(sum(f["importe"] for f in resto))
        numeros.append(sum(f["n"] for f in resto))
    colores, n = [], 0
    for e in etiquetas[: len(principales)]:
        if e in gris:
            colores.append(GRIS_OTROS)
        else:
            colores.append(color_categorico(n))
            n += 1
    if resto:
        colores.append(GRIS_OTROS)
    figura = go.Figure(
        go.Treemap(
            labels=etiquetas,
            text=[partir(e) for e in etiquetas],
            parents=[""] * len(etiquetas),
            values=valores,
            customdata=numeros,
            marker={"colors": colores, "line": {"color": "#0B1120", "width": 2}},
            texttemplate="<b>%{text}</b><br>%{value:,.0f} €",
            hovertemplate="%{label}<br>%{value:,.0f} € en %{customdata} contratos o "
            "concesiones<extra></extra>",
            textfont={"color": "#FFFFFF", "size": 13},
            tiling={"pad": 2},
        )
    )
    return _tema(figura, alto=380)


def contratos_por_anio(tendencia: list[dict]) -> go.Figure:
    """Contratos de cada año, separando los que tienen alguna señal (en ámbar)."""
    anios = [str(t["anio"]) for t in tendencia]
    con_senal = [t["n_con_alertas"] for t in tendencia]
    sin_senal = [t["n_contratos"] - t["n_con_alertas"] for t in tendencia]
    figura = go.Figure()
    figura.add_bar(
        x=anios,
        y=sin_senal,
        name="Sin señales",
        marker={"color": GRIS},
        hovertemplate="%{x}: %{y:,.0f} contratos sin señales<extra></extra>",
    )
    figura.add_bar(
        x=anios,
        y=con_senal,
        name="Con alguna señal",
        marker={"color": AMBAR},
        hovertemplate="%{x}: %{y:,.0f} contratos con alguna señal<extra></extra>",
    )
    figura.update_layout(barmode="stack")
    figura.update_yaxes(title="Contratos", tickformat=",.0f")
    figura.update_xaxes(type="category")
    figura = _tema(figura, alto=260)
    figura.update_layout(showlegend=True, legend={"orientation": "h", "y": 1.12, "x": 0})
    return figura


def senales_de_empresa(filas: list[dict], nombres: dict[str, str]) -> go.Figure:
    """Barras horizontales: en cuántos contratos se encontró cada señal."""
    filas = sorted(filas, key=lambda f: f["n"])
    figura = go.Figure(
        go.Bar(
            y=[nombres.get(f["indicador"], f["indicador"]) for f in filas],
            x=[f["n"] for f in filas],
            orientation="h",
            marker={"color": AMBAR, "cornerradius": 4},
            text=[f"{f['n']:,}".replace(",", ".") for f in filas],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}: %{x:,.0f} contratos<extra></extra>",
        )
    )
    figura.update_xaxes(visible=False, range=[0, max(f["n"] for f in filas) * 1.18])
    return _tema(figura, alto=60 + 36 * len(filas))


# --- Ficha de organismo (A-06) ---


def comparacion_senales(filas: list[dict], nombres: dict[str, str]) -> go.Figure:
    """Un punto por señal: en qué proporción de sus contratos la tiene el organismo (azul)
    frente al conjunto de organismos (gris), unidos por una línea."""
    filas = sorted(filas, key=lambda f: f["indicador"], reverse=True)
    etiquetas = [nombres.get(f["indicador"], f["indicador"]) for f in filas]
    figura = go.Figure()
    for etiqueta, f in zip(etiquetas, filas, strict=True):
        figura.add_scatter(
            x=[f["pct_global"], f["pct_organo"]],
            y=[etiqueta, etiqueta],
            mode="lines",
            line={"color": REJILLA, "width": 4},
            hoverinfo="skip",
            showlegend=False,
        )
    figura.add_scatter(
        x=[f["pct_global"] for f in filas],
        y=etiquetas,
        mode="markers",
        name="Todos los organismos",
        marker={
            "color": GRIS_CLARO,
            "size": 11,
            "symbol": "line-ns",
            "line": {"width": 3, "color": GRIS_CLARO},
        },
        hovertemplate="Todos los organismos: %{x:.1%}<extra></extra>",
    )
    figura.add_scatter(
        x=[f["pct_organo"] for f in filas],
        y=etiquetas,
        mode="markers",
        name="Este organismo",
        marker={"color": AZUL, "size": 13, "line": {"width": 2, "color": "#0B1120"}},
        customdata=[[f["activados"], f["aplicables"]] for f in filas],
        hovertemplate="Este organismo: %{x:.1%} (%{customdata[0]:,} de %{customdata[1]:,} "
        "contratos)<extra></extra>",
    )
    figura.update_xaxes(tickformat=".0%", rangemode="tozero", title="Contratos con la señal")
    figura = _tema(figura, alto=110 + 42 * len(filas))
    figura.update_layout(
        showlegend=True,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
        margin={"t": 40},
    )
    return figura


def procedimientos(filas: list[dict], nombres: dict[str, str], maximo: int = 6) -> go.Figure:
    """Barras horizontales: cuántos contratos ha hecho el organismo por cada vía."""
    # Se suman los procedimientos con el mismo nombre llano (p. ej. las dos formas de escribir
    # «contrato menor» en las fuentes) y lo que no entra en los `maximo` va a «Otras vías».
    por_nombre: dict[str, int] = {}
    for f in filas:
        nombre = nombres.get(f["procedimiento"], f["procedimiento"])
        por_nombre[nombre] = por_nombre.get(nombre, 0) + f["n_contratos"]
    ordenados = sorted(
        ((n, c) for n, c in por_nombre.items() if n != "Otras vías"),
        key=lambda p: p[1],
        reverse=True,
    )
    datos_ = ordenados[:maximo]
    resto = por_nombre.get("Otras vías", 0) + sum(c for _, c in ordenados[maximo:])
    if resto:
        datos_.append(("Otras vías", resto))
    datos_.reverse()
    figura = go.Figure(
        go.Bar(
            y=[d[0] for d in datos_],
            x=[d[1] for d in datos_],
            orientation="h",
            marker={"color": AZUL, "cornerradius": 4},
            text=[f"{d[1]:,}".replace(",", ".") for d in datos_],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}: %{x:,.0f} contratos<extra></extra>",
        )
    )
    figura.update_xaxes(visible=False, range=[0, max(d[1] for d in datos_) * 1.2])
    return _tema(figura, alto=60 + 36 * len(datos_))


# --- Mapa del dinero (A-07) ---


def empaquetar(radios: list[float], separacion: float = 0.04) -> list[tuple[float, float]]:
    """Coloca círculos de mayor a menor lo más cerca posible del centro sin que se solapen
    (búsqueda en espiral). Devuelve el centro de cada uno, en el orden recibido."""
    colocados: list[tuple[float, float, float]] = []
    for r in radios:
        if not colocados:
            colocados.append((0.0, 0.0, r))
            continue
        distancia, paso = 0.0, max(r * 0.15, 0.02)
        while True:
            angulos = 90
            libre = None
            for k in range(angulos):
                angulo = 2 * math.pi * k / angulos
                x, y = distancia * math.cos(angulo), distancia * math.sin(angulo)
                if all(
                    math.hypot(x - cx, y - cy) >= cr + r + separacion for cx, cy, cr in colocados
                ):
                    libre = (x, y)
                    break
            if libre:
                colocados.append((*libre, r))
                break
            distancia += paso
    return [(x, y) for x, y, _ in colocados]


def _circulo(figura: go.Figure, x: float, y: float, r: float, color: str) -> None:
    figura.add_shape(
        type="circle",
        x0=x - r,
        y0=y - r,
        x1=x + r,
        y1=y + r,
        fillcolor=color,
        line={"color": "#0B1120", "width": 2},
        layer="below",
    )


def _lienzo(figura: go.Figure, limite: float, alto: int) -> go.Figure:
    figura.update_xaxes(visible=False, range=[-limite, limite])
    figura.update_yaxes(visible=False, range=[-limite, limite], scaleanchor="x")
    return _tema(figura, alto=alto)


def burbujas_organismos(filas: list[dict]) -> go.Figure:
    """Burbujas empaquetadas de los organismos que más adjudican: área = importe, un color por
    organismo. El nombre va dentro de las burbujas grandes; todas tienen el detalle al pasar
    el ratón."""
    maximo = max(f["importe"] for f in filas)
    radios = [math.sqrt(f["importe"] / maximo) for f in filas]
    centros = empaquetar(radios)
    figura = go.Figure()
    for i, (f, r, (x, y)) in enumerate(zip(filas, radios, centros, strict=True)):
        _circulo(figura, x, y, r, color_categorico(i))
        # Nombre dentro solo si cabe; el resto se ve al pasar el ratón y en la lista.
        if r > 0.6:
            figura.add_annotation(
                x=x,
                y=y,
                text=f"<b>{partir(f['organo'], 14)}</b><br>{euros(f['importe'])}",
                showarrow=False,
                font={"color": "#FFFFFF", "size": 12},
            )
        else:
            figura.add_annotation(
                x=x,
                y=y,
                text=f"<b>{i + 1}</b>",
                showarrow=False,
                font={"color": "#FFFFFF", "size": 11 if r > 0.25 else 9},
            )
    figura.add_scatter(
        x=[c[0] for c in centros],
        y=[c[1] for c in centros],
        mode="markers",
        marker={
            "size": [max(8, 90 * r) for r in radios],
            "color": "rgba(0,0,0,0)",
            "line": {"width": 0},
        },
        customdata=[[f["organo"], f["importe"], f["n_contratos"]] for f in filas],
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]:,.0f} € en "
        "%{customdata[2]:,} contratos o concesiones<extra></extra>",
    )
    extension = max(math.hypot(x, y) + r for (x, y), r in zip(centros, radios, strict=True))
    return _lienzo(figura, extension * 1.03, 560)


def red_organismo(organo: str, filas: list[dict], total: float | None = None) -> go.Figure:
    """Red de un organismo: el organismo en el centro y sus empresas alrededor. El área de cada
    burbuja y el grosor de cada línea son el importe; un color por empresa."""
    filas = sorted(filas, key=lambda f: f["importe"], reverse=True)
    maximo = max(f["importe"] for f in filas)
    n = len(filas)
    distancia = 3.2
    figura = go.Figure()
    puntos = []
    for i, f in enumerate(filas):
        angulo = math.pi / 2 - 2 * math.pi * i / n
        x, y = distancia * math.cos(angulo), distancia * math.sin(angulo)
        proporcion = f["importe"] / maximo
        figura.add_shape(
            type="line",
            x0=0,
            y0=0,
            x1=x,
            y1=y,
            line={
                "color": transparente(color_categorico(i), 0.55),
                "width": 2 + 14 * proporcion,
            },
            layer="below",
        )
        puntos.append((x, y, 0.22 + 0.5 * math.sqrt(proporcion), angulo, f, i))
    _circulo(figura, 0, 0, 1.0, AZUL)
    figura.add_annotation(
        x=0,
        y=0,
        text=f"<b>{partir(organo, 16)}</b>" + (f"<br>{euros(total)}" if total else ""),
        showarrow=False,
        font={"color": "#FFFFFF", "size": 12},
    )
    for x, y, r, angulo, f, i in puntos:
        _circulo(figura, x, y, r, color_categorico(i))
        # Etiqueta hacia fuera, en la dirección de la burbuja, para no pisar a las vecinas.
        coseno, seno = math.cos(angulo), math.sin(angulo)
        lado = "left" if coseno > 0.3 else "right" if coseno < -0.3 else "center"
        figura.add_annotation(
            x=x + (r + 0.15) * coseno,
            y=y + (r + 0.15) * seno,
            text=f"{partir(f['empresa'], 24)}<br><b>{euros(f['importe'])}</b>",
            showarrow=False,
            xanchor=lado,
            yanchor="bottom" if seno > 0.7 else "top" if seno < -0.7 else "middle",
            align=lado if lado != "center" else "center",
            font={"color": TEXTO, "size": 11},
        )
    figura.add_scatter(
        x=[p[0] for p in puntos],
        y=[p[1] for p in puntos],
        mode="markers",
        marker={
            "size": [max(10, 60 * p[2]) for p in puntos],
            "color": "rgba(0,0,0,0)",
            "line": {"width": 0},
        },
        customdata=[[p[4]["empresa"], p[4]["importe"], p[4]["n_contratos"]] for p in puntos],
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]:,.0f} € en "
        "%{customdata[2]:,} contratos o concesiones<extra></extra>",
    )
    figura.update_xaxes(visible=False, range=[-7.5, 7.5])
    figura.update_yaxes(visible=False, range=[-5.0, 5.0], scaleanchor="x")
    return _tema(figura, alto=640)


def flujos_sankey(filas: list[dict]) -> go.Figure:
    """Diagrama de flujos organismo → empresa (vista avanzada del mapa del dinero). Cada
    organismo con su color y sus flujos del mismo color; las empresas en gris claro."""
    organos = list(dict.fromkeys(f["organo"] for f in filas))
    empresas = list(dict.fromkeys(f["empresa"] for f in filas))
    figura = go.Figure(
        go.Sankey(
            node={
                "label": organos + empresas,
                "pad": 14,
                "thickness": 14,
                "line": {"width": 0},
                "color": [color_categorico(i) for i in range(len(organos))]
                + [GRIS_CLARO] * len(empresas),
            },
            link={
                "source": [organos.index(f["organo"]) for f in filas],
                "target": [len(organos) + empresas.index(f["empresa"]) for f in filas],
                "value": [f["importe"] for f in filas],
                "color": [
                    transparente(color_categorico(organos.index(f["organo"])), 0.35) for f in filas
                ],
            },
            textfont={"color": TEXTO, "size": 12, "shadow": "none"},
        )
    )
    return _tema(figura, alto=600)
