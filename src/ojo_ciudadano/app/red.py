"""Mapa de nodos arrastrable, al estilo de Neo4j (D-026).

Cada nodo es un círculo: su **tamaño** es el dinero, su **color** (más claro cuanto más dinero)
también, y el **relleno** muestra qué parte se ha gastado (el resto queda en gris). Todas las
líneas son iguales. Se pueden mover los nodos y arrastran a los que están conectados; no hay
zoom. Usa `streamlit-agraph` (vis-network). Los nodos devuelven su identificador al pulsarlos.
"""

import base64
import math
import textwrap
from dataclasses import dataclass, field

from streamlit_agraph import Config, Edge, Node, agraph

from ojo_ciudadano.app.graficos import TEXTO
from ojo_ciudadano.app.textos import euros

FONDO = "#041627"
VACIO = "#33415C"  # parte sin gastar (gris azulado; contraste con el fondo)
LINEA = "#4F9CC0"  # líneas de agua
BORDE = "#E7ECF3"
COLOR_POCO = (0x1F, 0x5F, 0xBF)  # azul oscuro: poco dinero
COLOR_MUCHO = (0x8C, 0xC2, 0xFF)  # azul claro: mucho dinero
RADIO_MAX = 64  # radio del círculo central (la Comunidad o la consejería)


@dataclass
class NodoRed:
    """Un nodo del mapa. `llenado` es la proporción gastada (0 a 1) o None si no se conoce."""

    id: str
    etiqueta: str
    importe: float
    llenado: float | None = None
    detalle: str = ""
    titulo: str | None = None  # nombre completo, para el cuadro que sale al pasar el ratón
    centro: bool = False
    grupo: str = "ent"  # escala de tamaño y color propia: ent, con o agr
    x: float | None = None  # posición inicial (diseño radial); None = que la decida la física
    y: float | None = None
    color: str | None = None  # fuerza un color (p. ej. el nodo central)
    extra: dict = field(default_factory=dict)


def envolver(texto: str, ancho: int = 18) -> str:
    """Parte un texto largo en líneas (con saltos de línea, no etiquetas HTML)."""
    return chr(10).join(textwrap.wrap(texto, ancho, break_long_words=False)) or texto


def _mezcla(t: float) -> str:
    t = min(max(t, 0.0), 1.0)
    r, g, b = (round(a + (c - a) * t) for a, c in zip(COLOR_POCO, COLOR_MUCHO, strict=True))
    return f"#{r:02X}{g:02X}{b:02X}"


def svg_nodo(color: str, llenado: float | None, centro: bool = False) -> str:
    """Burbuja de cristal (data URI): el líquido en `color` sube hasta lo gastado, con una ola
    arriba, y el resto queda como cristal gris azulado. Reflejos y borde de luz encima."""
    lado = 100
    base = VACIO if llenado is not None else color
    borde = 0.95 if centro else 0.7
    parte = ""
    if llenado is not None:
        nivel = lado * (1 - min(max(llenado, 0.0), 1.0))
        ola = (
            f'<path d="M0 {nivel:.1f} Q12.5 {nivel - 3:.1f} 25 {nivel:.1f} T50 {nivel:.1f} '
            f'T75 {nivel:.1f} T100 {nivel:.1f} V{nivel + 4:.1f} H0 Z" fill="url(#l)"/>'
        )
        parte = (
            f'<g clip-path="url(#c)"><rect x="0" y="{nivel + 2:.1f}" width="{lado}" '
            f'height="{lado - nivel:.1f}" fill="url(#l)"/>{ola}'
            f'<path d="M0 {nivel:.1f} Q12.5 {nivel - 3:.1f} 25 {nivel:.1f} T50 {nivel:.1f} '
            f'T75 {nivel:.1f} T100 {nivel:.1f}" fill="none" stroke="#fff" stroke-opacity=".55" '
            'stroke-width="1.5"/></g>'
        )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{lado}" height="{lado}" '
        f'viewBox="0 0 {lado} {lado}"><defs>'
        '<clipPath id="c"><circle cx="50" cy="50" r="46"/></clipPath>'
        f'<linearGradient id="l" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{color}" '
        f'stop-opacity=".95"/><stop offset="1" stop-color="{color}" stop-opacity=".6"/>'
        "</linearGradient>"
        '<radialGradient id="v" cx="38%" cy="32%" r="75%"><stop offset="0" stop-color="#fff" '
        'stop-opacity=".1"/><stop offset=".72" stop-color="#bfe6ff" stop-opacity=".04"/>'
        '<stop offset="1" stop-color="#e6f8ff" stop-opacity=".42"/></radialGradient>'
        '<linearGradient id="b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" '
        f'stop-opacity="{borde}"/><stop offset=".5" stop-color="#fff" stop-opacity=".08"/>'
        '<stop offset="1" stop-color="#9fe8ff" stop-opacity=".55"/></linearGradient>'
        "</defs>"
        f'<circle cx="50" cy="50" r="46" fill="{base}"/>{parte}'
        '<circle cx="50" cy="50" r="46" fill="url(#v)"/>'
        f'<circle cx="50" cy="50" r="46" fill="none" stroke="url(#b)" '
        f'stroke-width="{3 if centro else 2}"/>'
        '<ellipse cx="34" cy="22" rx="15" ry="6.5" fill="#fff" fill-opacity=".55" '
        'transform="rotate(-30 34 22)"/>'
        '<ellipse cx="70" cy="78" rx="6" ry="2.2" fill="#fff" fill-opacity=".3" '
        'transform="rotate(-30 70 78)"/>'
        "</svg>"
    )
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def _titulo(n: NodoRed) -> str:
    lineas = [n.titulo or n.etiqueta.replace("\n", " "), euros(n.importe)]
    if n.llenado is not None:
        lineas.append(f"Gastado: {round(100 * n.llenado)} %")
    if n.detalle:
        lineas.append(n.detalle)
    return "\n".join(lineas)


# Radio mínimo y máximo de cada grupo de nodos: cada grupo tiene su propia escala de tamaño y de
# color (los contratos de una consejería no se comparan con el dinero de la consejería).
ESCALAS = {"ent": (18.0, 56.0), "con": (10.0, 30.0), "agr": (14.0, 34.0)}


def posiciones_radiales(
    n: int, radio: float, inicio: float = -math.pi / 2
) -> list[tuple[float, float]]:
    """`n` puntos repartidos por igual en una circunferencia alrededor del origen."""
    return [
        (
            radio * math.cos(inicio + 2 * math.pi * i / n),
            radio * math.sin(inicio + 2 * math.pi * i / n),
        )
        for i in range(n)
    ]


def alternar_tamanos(items: list) -> list:
    """Ordena de mayor a menor y los intercala (grande, pequeño, grande…) para que dos círculos
    grandes no queden pegados en la circunferencia."""
    ordenados = list(items)
    resultado = []
    while ordenados:
        resultado.append(ordenados.pop(0))
        if ordenados:
            resultado.append(ordenados.pop())
    return resultado


def configuracion(alto: int = 720) -> Config:
    """Física suave que parte del diseño radial: al arrastrar un nodo tiran los conectados y al
    soltar vuelve a asentarse cerca de donde estaba."""
    cfg = Config(height=alto, width=1000, directed=True, physics=True)
    cfg.width = "100%"
    cfg.physics = {
        "enabled": True,
        "solver": "forceAtlas2Based",
        "forceAtlas2Based": {
            "gravitationalConstant": -4,
            "centralGravity": 0.0,
            "springLength": 120,
            "springConstant": 0.09,
            "damping": 0.8,
            "avoidOverlap": 1.0,
        },
        "maxVelocity": 30,
        "minVelocity": 0.6,
        "stabilization": {"enabled": False},
    }
    cfg.layout = {"randomSeed": 7, "improvedLayout": False}
    cfg.interaction = {
        "zoomView": False,  # sin zoom: solo se mueven los nodos
        "dragView": False,
        "dragNodes": True,
        "hover": True,
        "tooltipDelay": 120,
        "selectConnectedEdges": False,
        "hoverConnectedEdges": False,
    }
    cfg.edges = {
        "width": 2,  # todas las líneas iguales
        "color": {"color": LINEA, "highlight": LINEA, "hover": LINEA},
        "arrows": {"to": {"enabled": True, "scaleFactor": 0.5}},
        "smooth": {"enabled": True, "type": "continuous"},
        "selectionWidth": 0,
        "hoverWidth": 0,
    }
    return cfg


def _escala(nodos: list[NodoRed], grupo: str) -> tuple[float, float]:
    """Mayor y menor importe de un grupo (sin los nodos con color propio)."""
    valores = [n.importe for n in nodos if n.grupo == grupo and not n.centro and n.color is None]
    valores = valores or [n.importe for n in nodos if n.grupo == grupo and not n.centro]
    positivos = [v for v in valores if v > 0]
    return max(valores, default=0.0), min(positivos, default=0.0)


def mapa(
    nodos: list[NodoRed],
    enlaces: list[tuple],
    alto: int = 720,
) -> str | None:
    """Dibuja el mapa y devuelve el `id` del nodo pulsado (None si no se ha pulsado ninguno).
    Cada enlace es `(origen, destino)` o `(origen, destino, longitud)`."""
    if not nodos:
        return None
    escalas = {g: _escala(nodos, g) for g in {n.grupo for n in nodos}}
    elementos = []
    for n in nodos:
        minimo_r, maximo_r = ESCALAS.get(n.grupo, ESCALAS["ent"])
        maximo, minimo = escalas[n.grupo]
        if n.centro:
            radio = RADIO_MAX + 6
            color = n.color or _mezcla(1.0)
        else:
            if maximo <= 0 or n.importe <= 0:
                radio = minimo_r
            else:
                radio = minimo_r + (maximo_r - minimo_r) * math.sqrt(min(n.importe / maximo, 1.0))
            t = 0.5 if maximo == minimo else max((n.importe - minimo) / (maximo - minimo), 0)
            color = n.color or _mezcla(math.sqrt(max(t, 0.0)))
        posicion = {} if n.x is None or n.y is None else {"x": n.x, "y": n.y}
        elementos.append(
            Node(
                id=n.id,
                label=n.etiqueta,
                title=_titulo(n),
                shape="image",
                image=svg_nodo(color, n.llenado, n.centro),
                size=radio,
                mass=6 if n.centro else 1,
                font={
                    "color": TEXTO,
                    "size": 15 if n.centro else (11 if n.grupo != "ent" else 13),
                    "face": "Inter, sans-serif",
                    "strokeWidth": 4,
                    "strokeColor": FONDO,
                    "multi": False,
                },
                fixed={"x": True, "y": True} if n.centro else False,
                shapeProperties={"useBorderWithImage": False},
                **posicion,
            )
        )
    lineas = []
    for e in enlaces:
        largo = {"length": e[2]} if len(e) > 2 else {}
        lineas.append(Edge(source=e[0], target=e[1], color=LINEA, width=2, **largo))
    return agraph(nodes=elementos, edges=lineas, config=configuracion(alto))


def leyenda_texto() -> str:
    return (
        "Cada círculo es una entidad: cuanto **más grande y más claro**, más dinero. "
        "La parte **de color** es lo gastado y la **gris**, lo que queda sin gastar. "
        "Puedes arrastrar los círculos; los conectados se mueven con ellos. Pulsa uno para ver más."
    )
