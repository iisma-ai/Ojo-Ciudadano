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
GRIS = "#5B6B86"  # contraste 3,5:1 con el fondo (WCAG 1.4.11, gráficos)
GRIS_CLARO = "#93A1B8"
TEXTO = "#E7ECF3"
# Separación entre sectores y rectángulos, y borde de los puntos: líneas claras y casi
# transparentes (como cristal), nunca negras sobre el fondo de mar.
SEPARADOR = "rgba(220, 240, 255, 0.22)"
BRILLO = "rgba(235, 248, 255, 0.75)"
REJILLA = "#24314A"
# Señales en celeste (antes ámbar): en los gráficos solo lo atípico va en ámbar (D-055).
SENAL = "#38BDF8"

CONFIG = {"displayModeBar": False, "responsive": True}

# Paleta categórica para distinguir entidades (organismos, empresas), en orden fijo: solo azules
# y grises azulados (D-055), alternando claros y oscuros para que dos vecinos se distingan por
# luminosidad. El ámbar queda solo para lo atípico. Del 8.º en adelante, gris.
CATEGORICOS = ["#3D8BFD", "#9CC7FF", "#1E5BB8", "#38BDF8", "#6F86A6", "#2B6CB0", "#B4C3D6"]
GRIS_OTROS = "#4A5872"


def color_categorico(posicion: int) -> str:
    return CATEGORICOS[posicion] if posicion < len(CATEGORICOS) else GRIS_OTROS


def transparente(color: str, alfa: float) -> str:
    """«#RRGGBB» → «rgba(r, g, b, alfa)»."""
    r, g, b = (int(color[i : i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r}, {g}, {b}, {alfa})"


# Estilo acuático (D-055): rejilla casi invisible, barras de cristal (translúcidas, con borde claro
# y esquinas redondeadas) y puntos como burbujas (centro de color y borde que se aclara).
REJILLA_SUAVE = "rgba(170, 225, 255, 0.08)"
BORDE_CRISTAL = "rgba(220, 240, 255, 0.55)"
FONDO_BURBUJA = "rgba(9, 30, 50, 0.96)"  # el cuadro al pasar el ratón; su forma, en estilo.css
OPACIDAD_CRISTAL = 0.72
# Cada punto con degradado es un degradado SVG propio: en nubes grandes (la de atípicos tiene
# 1.500) el navegador va a tirones. Por encima de este número, puntos planos.
MAX_PUNTOS_BURBUJA = 50
# Lo atípico, en ámbar como en la presentación (tono «ambar» de presentacion/escena3d.js).
ATIPICO_LUZ = "#FFD27A"
ATIPICO_TONO = "#E0A032"


def _cristal(figura: go.Figure) -> None:
    """Barras de cristal y puntos-burbuja en las trazas que ya tiene la figura."""
    figura.update_traces(
        selector={"type": "bar"},
        opacity=OPACIDAD_CRISTAL,
        marker_line={"color": BORDE_CRISTAL, "width": 1},
    )
    for traza in figura.data:
        if traza.type == "treemap":
            _treemap_de_cristal(traza)
            continue
        if traza.type != "scatter" or "markers" not in (traza.mode or ""):
            continue
        if len(traza.x or ()) > MAX_PUNTOS_BURBUJA or traza.marker.gradient.type is not None:
            continue  # nube grande, o ya trae su propio degradado (el atípico)
        traza.marker.gradient = {"type": "radial", "color": "rgba(225, 245, 255, 0.85)"}
        if traza.marker.line.color is None:
            traza.marker.line = {"color": BORDE_CRISTAL, "width": 1}


def _treemap_de_cristal(traza) -> None:
    """Rectángulos de cristal: el color de cada uno, translúcido, con borde claro, esquinas
    redondeadas y algo de aire entre ellos (como las tarjetas de la web)."""
    colores = traza.marker.colors
    if colores:
        traza.marker.colors = [
            transparente(c, 0.5) if isinstance(c, str) and c.startswith("#") else c for c in colores
        ]
    traza.marker.line = {"color": BORDE_CRISTAL, "width": 1.2}
    traza.marker.cornerradius = 8
    traza.tiling.pad = 4
    traza.textfont.family = "Inter, sans-serif"


def _tema(figura: go.Figure, alto: int = 240) -> go.Figure:
    figura.update_layout(
        height=alto,
        margin={"l": 10, "r": 10, "t": 24, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, sans-serif", "color": TEXTO, "size": 13},
        showlegend=False,
        # el cuadro al pasar el ratón, con nuestra letra; el resto de su forma, en estilo.css
        hoverlabel={
            "bgcolor": FONDO_BURBUJA,
            "bordercolor": FONDO_BURBUJA,
            "font": {"family": "Inter, sans-serif", "color": TEXTO, "size": 14},
            "align": "left",
            "namelength": -1,
        },
        bargap=0.25,
        barcornerradius=6,
        separators=",.",  # formato español: 1.234,5
    )
    for actualizar in (figura.update_xaxes, figura.update_yaxes):
        actualizar(
            gridcolor=REJILLA_SUAVE,
            zeroline=False,
            linecolor=REJILLA_SUAVE,
            automargin=True,
            tickfont={"color": GRIS_CLARO},
        )
    _cristal(figura)
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
    # «Este contrato» también con texto: el color no puede ser la única pista (A-10).
    este = (
        etiquetas[x.index(min(detalle["ofertas"], 10))]
        if min(detalle["ofertas"], 10) in x
        else None
    )
    if este is not None:
        figura.add_annotation(
            x=este,
            y=y[etiquetas.index(este)],
            text="Este contrato",
            showarrow=True,
            arrowcolor=AZUL,
            font={"color": AZUL},
            yshift=4,
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


def ventana_doce_meses(contratos: list[dict]) -> list[dict]:
    """Los contratos menores de los 12 meses en los que más suman (la ventana de R-03)."""
    if not contratos:
        return []
    sumas = suma_doce_meses(contratos)
    fin = contratos[sumas.index(max(sumas))]["fecha"]
    desde = fin - timedelta(days=364)
    return [c for c in contratos if desde <= c["fecha"] <= fin]


def reparto(detalle: dict) -> go.Figure:
    """E-04 (D-042): de cada 100 € que el organismo adjudica en este tipo de contrato, cuántos
    se lleva cada empresa. Ranking de barras con la empresa de este contrato en azul y una línea
    en «la mitad», que es donde salta la señal."""
    total = detalle["total"] or 1
    partes = detalle["partes"]
    nombres = [p["nombre"] if len(p["nombre"]) <= 30 else p["nombre"][:29] + "…" for p in partes]
    de_cada_100 = [100 * p["importe"] / total for p in partes]
    figura = go.Figure(
        go.Bar(
            y=nombres,
            x=de_cada_100,
            orientation="h",
            marker={
                "color": [AZUL if p["es_este"] else GRIS for p in partes],
                "line": {"color": SEPARADOR, "width": 1},
                "cornerradius": 4,
            },
            text=[f"{round(v)} €" for v in de_cada_100],
            textposition="outside",
            textfont={"color": TEXTO, "size": 13},
            cliponaxis=False,
            customdata=[p["importe"] for p in partes],
            hovertemplate="%{y}: %{customdata:,.0f} € (%{x:.0f} de cada 100 €)<extra></extra>",
        )
    )
    figura.add_vline(
        x=50,
        line={"color": GRIS_CLARO, "dash": "dot", "width": 2},
        annotation_text="la mitad",
        annotation_font_color=GRIS_CLARO,
        annotation_position="top",
    )
    figura.update_xaxes(range=[0, 108], visible=False)
    figura.update_yaxes(autorange="reversed", tickfont={"size": 12})
    figura = _tema(figura, alto=60 + 34 * len(partes))
    figura.update_layout(showlegend=False, bargap=0.35)
    return figura


def subida(detalle: dict) -> go.Figure:
    """E-05 (D-042): «antes y después». Una columna con el precio adjudicado y otra con el
    precio tras las modificaciones, que crece en dos tramos (hasta el 20 % y lo que pasa del
    20 %), con la línea del +20 % y la subida en grande."""
    adjudicado = detalle["adjudicado"] or 0
    modificaciones = detalle["modificaciones"] or 0
    hasta_20 = min(modificaciones, 0.2 * adjudicado)
    encima_20 = max(modificaciones - 0.2 * adjudicado, 0)
    columnas = ["Precio adjudicado", "Con modificaciones"]
    figura = go.Figure()
    figura.add_bar(
        x=columnas,
        y=[adjudicado, adjudicado],
        name="Precio adjudicado",
        marker={"color": GRIS, "cornerradius": 4},
        text=[euros(adjudicado), ""],
        textposition="inside",
        hovertemplate="Precio adjudicado: %{y:,.0f} €<extra></extra>",
    )
    figura.add_bar(
        x=columnas,
        y=[0, hasta_20],
        name="Modificaciones hasta el 20 %",
        marker={"color": "#7DB3FF"},
        hovertemplate="Modificaciones hasta el 20 %: %{y:,.0f} €<extra></extra>",
    )
    figura.add_bar(
        x=columnas,
        y=[0, encima_20],
        name="Por encima del 20 %",
        marker={"color": AZUL, "cornerradius": 4},
        hovertemplate="Por encima del 20 %: %{y:,.0f} €<extra></extra>",
    )
    figura.add_hline(
        y=adjudicado * 1.2,
        line={"color": GRIS_CLARO, "dash": "dot", "width": 2},
        annotation_text="+20 %",
        annotation_font_color=GRIS_CLARO,
        annotation_position="top left",
    )
    if adjudicado:
        figura.add_annotation(
            x=columnas[1],
            y=adjudicado + modificaciones,
            text=f"<b>+{porcentaje(modificaciones / adjudicado)}</b>",
            showarrow=False,
            yshift=16,
            font={"size": 20, "color": TEXTO},
        )
    figura.update_layout(
        barmode="stack",
        bargap=0.45,
        legend={"orientation": "h", "y": -0.18, "font": {"size": 11}},
    )
    figura.update_yaxes(visible=False, range=[0, (adjudicado + modificaciones) * 1.18])
    figura = _tema(figura, alto=320)
    figura.update_layout(showlegend=True, legend={"orientation": "h", "y": -0.12})
    return figura


ZONA_SENAL = "rgba(125, 179, 255, 0.16)"  # zonas de la regla donde salta una señal


def rebaja(detalle: dict, habitual: float | None = None) -> go.Figure:
    """E-06 (D-042): una regla de la rebaja (de «por encima del precio» a «más de la mitad»)
    con las dos zonas donde salta la señal sombreadas, el marcador de este contrato y, si se
    conoce, el de la rebaja habitual en contratos parecidos. Rebaja en tanto por uno."""
    presupuesto = detalle["presupuesto"] or 0
    adjudicado = detalle["adjudicado"] or 0
    baja = 1 - adjudicado / presupuesto if presupuesto else 0
    minimo = min(-0.1, baja - 0.08)
    maximo = max(0.6, baja + 0.08)
    figura = go.Figure()
    for x0, x1, texto in ((minimo, 0.005, "casi sin rebaja"), (0.5, maximo, "rebaja muy alta")):
        figura.add_vrect(
            x0=x0,
            x1=x1,
            fillcolor=ZONA_SENAL,
            line_width=0,
            annotation_text=texto,
            annotation_position="bottom",
            annotation_font={"color": GRIS_CLARO, "size": 11},
        )
    figura.add_shape(
        type="line", x0=minimo, x1=maximo, y0=0, y1=0, line={"color": GRIS, "width": 3}
    )
    if habitual is not None:
        figura.add_scatter(
            x=[habitual],
            y=[0],
            mode="markers+text",
            marker={"symbol": "line-ns", "size": 22, "line": {"width": 3, "color": GRIS_CLARO}},
            text=[f"Lo habitual: {porcentaje(habitual)}"],
            textposition="bottom center",
            textfont={"color": GRIS_CLARO, "size": 12},
            hovertemplate="Rebaja habitual en contratos parecidos: %{x:.1%}<extra></extra>",
        )
    etiqueta = (
        f"Este contrato: {porcentaje(baja, 1)}"
        if baja >= 0
        else f"Este contrato: {porcentaje(-baja)} por encima"
    )
    figura.add_scatter(
        x=[baja],
        y=[0],
        mode="markers+text",
        marker={"size": 20, "color": AZUL, "line": {"width": 2, "color": TEXTO}},
        text=[f"<b>{etiqueta}</b>"],
        textposition=(
            "top right"
            if baja < minimo + (maximo - minimo) / 3
            else ("top left" if baja > minimo + 2 * (maximo - minimo) / 3 else "top center")
        ),
        textfont={"color": TEXTO, "size": 14},
        hovertemplate="Rebaja de este contrato: %{x:.1%}<extra></extra>",
    )
    figura.update_layout(showlegend=False)
    figura.update_xaxes(
        range=[minimo, maximo], tickformat=".0%", showgrid=False, zeroline=False, title=None
    )
    figura.update_yaxes(visible=False, range=[-1, 1])
    return _tema(figura, alto=190)


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
            marker={"colors": colores, "line": {"color": SEPARADOR, "width": 1}},
            texttemplate="<b>%{text}</b><br>%{value:,.0f} €",
            hovertemplate="%{label}<br>%{value:,.0f} € en %{customdata} contratos o "
            "concesiones<extra></extra>",
            textfont={"color": "#FFFFFF", "size": 13},
            tiling={"pad": 2},
        )
    )
    return _tema(figura, alto=380)


def contratos_por_anio(tendencia: list[dict]) -> go.Figure:
    """Contratos de cada año, separando los que tienen alguna señal (en celeste)."""
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
        marker={"color": SENAL},
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
            marker={"color": SENAL, "cornerradius": 4},
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
        marker={"color": AZUL, "size": 13, "line": {"width": 1.5, "color": BRILLO}},
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
        line={"color": SEPARADOR, "width": 1},
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


# --- Contratos atípicos (A-04, E-07) ---

NOMBRE_VARIABLE = {
    "importe": "Importe adjudicado (€)",
    "n_ofertas": "Número de ofertas",
    "baja": "Rebaja sobre el precio de salida",
    "modificaciones": "Modificaciones sobre el importe",
    "cuota": "Cuota de la empresa en el organismo",
    "menores_12m": "Contratos menores en 12 meses",
}
_PORCENTAJES = ("baja", "modificaciones", "cuota")


def _eje(figura: go.Figure, eje: str, variable: str, valores: list, este=None) -> None:
    ajustes = {"title": NOMBRE_VARIABLE.get(variable, variable)}
    positivos = [v for v in valores if v is not None and v > 0]
    if variable in _PORCENTAJES:
        ajustes["tickformat"] = ".0%"
        # Los valores erróneos de la fuente (rebajas de -5.000 %) aplastan el resto: el eje se
        # recorta a los percentiles 1-99, sin dejar nunca fuera a este contrato.
        ordenados = sorted(v for v in valores if v is not None)
        if len(ordenados) > 20:
            bajo = ordenados[len(ordenados) // 100]
            alto = ordenados[-(len(ordenados) // 100) - 1]
            if este is not None:
                bajo, alto = min(bajo, este), max(alto, este)
            margen = (alto - bajo) * 0.05 or 0.05
            ajustes["range"] = [bajo - margen, alto + margen]
    elif positivos and max(positivos) / max(min(positivos), 1e-9) > 1000:
        ajustes["type"] = "log"
    if variable == "importe":
        ajustes["tickformat"] = ",.0f"
    (figura.update_xaxes if eje == "x" else figura.update_yaxes)(**ajustes)


def atipico(detalle: dict, variables: list[str]) -> go.Figure:
    """E-07: el contrato atípico (ámbar, como en la presentación) frente a una muestra de
    contratos similares (gris), en las variables que más lo alejan. Con dos variables, nube de
    puntos; con una, histograma con la posición del contrato."""
    este, pares = detalle["este"], detalle["pares"]
    variables = [v for v in variables if v in NOMBRE_VARIABLE][:2] or ["importe"]
    figura = go.Figure()
    if len(variables) == 2:
        vx, vy = variables
        puntos = [p for p in pares if p[vx] is not None and p[vy] is not None]
        # la nube (hasta 1.500 puntos) con WebGL: en SVG tardaba en dibujarse
        figura.add_trace(
            go.Scattergl(
                x=[p[vx] for p in puntos],
                y=[p[vy] for p in puntos],
                mode="markers",
                name="Contratos similares",
                marker={"color": transparente(GRIS_CLARO, 0.35), "size": 6},
                hoverinfo="skip",
            )
        )
        # el atípico como la burbuja ámbar de la presentación: un halo que se apaga hacia fuera
        # y, encima, la burbuja de cristal con el borde más claro (dos puntos, sin 3D)
        figura.add_scatter(
            x=[este[vx]],
            y=[este[vy]],
            mode="markers",
            showlegend=False,
            hoverinfo="skip",
            cliponaxis=False,  # el halo puede salir del área del gráfico sin cortarse
            marker={
                "color": transparente(ATIPICO_LUZ, 0.5),
                "size": 46,
                "gradient": {"type": "radial", "color": transparente(ATIPICO_LUZ, 0.0)},
                "line": {"width": 0},
            },
        )
        figura.add_scatter(
            x=[este[vx]],
            y=[este[vy]],
            mode="markers",
            name="Este contrato (atípico)",
            cliponaxis=False,
            marker={
                "color": transparente(ATIPICO_TONO, 0.55),
                "size": 22,
                "gradient": {"type": "radial", "color": ATIPICO_LUZ},
                "line": {"width": 1.5, "color": "rgba(255, 236, 190, 0.95)"},
            },
            hovertemplate="Este contrato (atípico)<extra></extra>",
        )
        _eje(figura, "x", vx, [p[vx] for p in puntos] + [este[vx]], este[vx])
        _eje(figura, "y", vy, [p[vy] for p in puntos] + [este[vy]], este[vy])
    else:
        (v,) = variables
        valores = [p[v] for p in pares if p[v] is not None]
        figura.add_histogram(
            x=valores,
            name="Contratos similares",
            marker={"color": GRIS},
            nbinsx=40,
            hovertemplate="%{y} contratos<extra></extra>",
        )
        if este[v] is not None:
            figura.add_vline(
                x=este[v],
                line={"color": ATIPICO_TONO, "width": 3},
                annotation_text="Este contrato (atípico)",
                annotation_font_color=ATIPICO_LUZ,
                # a la izquierda de la línea: el atípico suele estar en el borde del eje
                annotation_position="top left",
            )
        _eje(figura, "x", v, valores + [este[v]], este[v])
        figura.update_yaxes(title="Contratos similares")
    figura = _tema(figura, alto=320)
    figura.update_layout(showlegend=True, legend={"orientation": "h", "y": 1.1, "x": 0})
    return figura


# --- Gráfico automático para respuestas de consultas (A-08) ---

_NO_ETIQUETA = {"nif", "fuente", "base_importe", "motivo", "url_origen", "tipo", "fecha_descarga"}
_PRIORIDAD_VALOR = (
    "proporcion",
    "modificaciones_sobre_adjudicado",
    "importe",
    "n_",
)
_NOMBRE_COLUMNA = {
    "proporcion_importe_alerta_r02": "Proporción del importe sin anuncio público",
    "modificaciones_sobre_adjudicado": "Modificaciones sobre lo adjudicado",
    "importe_con_iva": "Importe con IVA",
    "importe_sin_iva": "Importe sin IVA",
    "importe_total": "Importe total",
    "importe_concedido": "Importe concedido",
    "n_contratos": "Contratos",
    "n_contratos_o_concesiones": "Contratos o concesiones",
}


def _es_porcentaje(columna: str) -> bool:
    return columna.startswith("proporcion") or "_sobre_" in columna


def _valor_legible(columna: str, valor: float) -> str:
    if _es_porcentaje(columna):
        return porcentaje(valor, 1)
    if columna.startswith("importe"):
        return euros(valor)
    return f"{valor:,.0f}".replace(",", ".")


def automatico(resultado: dict) -> tuple[go.Figure | None, str | None]:
    """Elige un gráfico para el resultado de una consulta (columnas y filas de `sql_seguro`):
    barras por año si hay columna `anio`, o barras horizontales ordenadas (ranking) con la
    primera columna de texto y la primera numérica relevante. Devuelve también una frase que
    resume el gráfico. (None, None) si no hay nada que dibujar."""
    columnas, filas = resultado["columnas"], resultado["filas"]
    if not filas:
        return None, None
    numericas = [
        c
        for i, c in enumerate(columnas)
        if any(isinstance(f[i], int | float) and not isinstance(f[i], bool) for f in filas)
        and c != "anio"
    ]
    # Por año se cuentan contratos o concesiones: los importes de cada fuente tienen distinta
    # base y no saldrían todas en el mismo gráfico.
    prioridad = ("n_", *_PRIORIDAD_VALOR) if "anio" in columnas else _PRIORIDAD_VALOR
    valor = next((c for p in prioridad for c in numericas if c.startswith(p)), None)
    if valor is None:
        return None, None
    iv = columnas.index(valor)
    nombre_valor = _NOMBRE_COLUMNA.get(valor, valor.replace("_", " ").capitalize())

    if "anio" in columnas:
        ia = columnas.index("anio")
        serie = [columnas.index(c) for c in ("fuente", "tipo") if c in columnas]
        grupos: dict[str, dict] = {}
        for f in filas:
            if f[ia] is None or f[iv] is None:
                continue
            clave = " · ".join(str(f[i]) for i in serie) or nombre_valor
            grupos.setdefault(clave, {})[str(f[ia])] = (
                grupos.get(clave, {}).get(str(f[ia]), 0) + f[iv]
            )
        if not grupos:
            return None, None
        figura = go.Figure()
        for n, (clave, por_anio) in enumerate(grupos.items()):
            anios = sorted(por_anio)
            figura.add_bar(
                x=anios,
                y=[por_anio[a] for a in anios],
                name=clave,
                marker={"color": color_categorico(n)},
            )
        figura.update_layout(barmode="group")
        figura.update_xaxes(type="category", title="Año")
        figura.update_yaxes(title=nombre_valor, tickformat=",.0f")
        figura = _tema(figura, alto=320)
        figura.update_layout(showlegend=True, legend={"orientation": "h", "y": -0.25, "x": 0})
        return figura, f"{nombre_valor} por año."

    etiqueta = next(
        (
            c
            for i, c in enumerate(columnas)
            if c not in _NO_ETIQUETA and all(isinstance(f[i], str) or f[i] is None for f in filas)
        ),
        None,
    )
    if etiqueta is None:
        return None, None
    ie = columnas.index(etiqueta)
    filas = sorted((f for f in filas if f[iv] is not None), key=lambda f: f[iv], reverse=True)
    filas = filas[:12]
    if not filas:
        return None, None
    textos_ = [str(f[ie] or "Sin nombre") for f in filas]
    # Un mismo nombre puede salir una vez por fuente: se añade la fuente para distinguirlos.
    if len(set(textos_)) < len(textos_) and "fuente" in columnas:
        ifu = columnas.index("fuente")
        textos_ = [
            f"{t} ({'Plataforma' if 'Plataforma' in str(f[ifu]) else 'portal'})"
            for t, f in zip(textos_, filas, strict=True)
        ]
    nombres = [partir(t[:60] + ("…" if len(t) > 60 else ""), 40) for t in textos_]
    valores = [f[iv] for f in filas]
    figura = go.Figure(
        go.Bar(
            y=list(reversed(nombres)),
            x=list(reversed(valores)),
            orientation="h",
            marker={"color": [GRIS] * (len(valores) - 1) + [AZUL], "cornerradius": 4},
            text=[_valor_legible(valor, v) for v in reversed(valores)],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}<extra></extra>",
        )
    )
    figura.update_xaxes(visible=False, range=[0, max(valores) * 1.45])
    figura = _tema(figura, alto=80 + 34 * len(filas))
    primero = textos_[0] if len(textos_[0]) <= 90 else textos_[0][:87].rstrip() + "…"
    frase = (
        f"En primer lugar: **{primero}**, con {_valor_legible(valor, valores[0])} "
        f"({nombre_valor[0].lower() + nombre_valor[1:]})."
    )
    return figura, frase
