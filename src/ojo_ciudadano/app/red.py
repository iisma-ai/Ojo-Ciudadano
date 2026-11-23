"""Mapa de nodos arrastrable, al estilo de Neo4j (D-026).

Cada nodo es un círculo: su **tamaño** es el dinero, su **color** (más claro cuanto más dinero)
también, y el **relleno** muestra qué parte se ha gastado (el resto queda en gris). Todas las
líneas son iguales. Se pueden mover los nodos y arrastran a los que están conectados; no hay
zoom. Usa `streamlit-agraph` (vis-network). Los nodos devuelven su identificador al pulsarlos.
"""

import base64
import math
from dataclasses import dataclass, field

from streamlit_agraph import Config, Edge, Node, agraph

from ojo_ciudadano.app.graficos import TEXTO
from ojo_ciudadano.app.textos import euros

FONDO = "#0B1120"
VACIO = "#33415C"  # parte sin gastar (gris azulado; contraste con el fondo)
LINEA = "#5B6B86"
BORDE = "#E7ECF3"
COLOR_POCO = (0x1F, 0x5F, 0xBF)  # azul oscuro: poco dinero
COLOR_MUCHO = (0x8C, 0xC2, 0xFF)  # azul claro: mucho dinero
RADIO_MIN, RADIO_MAX = 16, 64


@dataclass
class NodoRed:
    """Un nodo del mapa. `llenado` es la proporción gastada (0 a 1) o None si no se conoce."""

    id: str
    etiqueta: str
    importe: float
    llenado: float | None = None
    detalle: str = ""
    centro: bool = False
    color: str | None = None  # fuerza un color (p. ej. el nodo central)
    extra: dict = field(default_factory=dict)


def _mezcla(t: float) -> str:
    t = min(max(t, 0.0), 1.0)
    r, g, b = (round(a + (c - a) * t) for a, c in zip(COLOR_POCO, COLOR_MUCHO, strict=True))
    return f"#{r:02X}{g:02X}{b:02X}"


def _radio(importe: float, maximo: float) -> float:
    if maximo <= 0 or importe <= 0:
        return RADIO_MIN
    return RADIO_MIN + (RADIO_MAX - RADIO_MIN) * math.sqrt(min(importe / maximo, 1.0))


def svg_nodo(color: str, llenado: float | None, centro: bool = False) -> str:
    """Círculo con el relleno de abajo arriba en `color` y el resto en gris (data URI)."""
    lado = 100
    if llenado is None:
        relleno = lado  # sin dato de gasto: todo del color
        parte = ""
    else:
        relleno = lado * (1 - min(max(llenado, 0.0), 1.0))
        parte = ""
    base = VACIO if llenado is not None else color
    borde = BORDE if centro else "#9FB0CC"
    ancho = 5 if centro else 3
    if llenado is not None:
        parte = (
            f'<rect x="0" y="{relleno:.1f}" width="{lado}" height="{lado - relleno:.1f}" '
            f'fill="{color}" clip-path="url(#c)"/>'
        )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{lado}" height="{lado}" '
        f'viewBox="0 0 {lado} {lado}"><defs><clipPath id="c"><circle cx="50" cy="50" r="47"/>'
        f'</clipPath></defs><circle cx="50" cy="50" r="47" fill="{base}"/>{parte}'
        f'<circle cx="50" cy="50" r="47" fill="none" stroke="{borde}" stroke-width="{ancho}"/>'
        "</svg>"
    )
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def _titulo(n: NodoRed) -> str:
    lineas = [n.etiqueta, euros(n.importe)]
    if n.llenado is not None:
        lineas.append(f"Gastado: {round(100 * n.llenado)} %")
    if n.detalle:
        lineas.append(n.detalle)
    return "\n".join(lineas)


def configuracion(alto: int = 560) -> Config:
    """Física suave: los nodos se separan, las líneas tiran y todo se recoloca al arrastrar."""
    cfg = Config(height=alto, width=1000, directed=True, physics=True)
    cfg.width = "100%"
    cfg.physics = {
        "enabled": True,
        "solver": "forceAtlas2Based",
        "forceAtlas2Based": {
            "gravitationalConstant": -90,
            "centralGravity": 0.012,
            "springLength": 190,
            "springConstant": 0.07,
            "damping": 0.55,
            "avoidOverlap": 0.9,
        },
        "stabilization": {"enabled": True, "iterations": 160, "fit": True},
    }
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
        "arrows": {"to": {"enabled": True, "scaleFactor": 0.6}},
        "smooth": {"enabled": True, "type": "dynamic"},
        "selectionWidth": 0,
        "hoverWidth": 0,
    }
    return cfg


def mapa(
    nodos: list[NodoRed],
    enlaces: list[tuple[str, str]],
    alto: int = 560,
) -> str | None:
    """Dibuja el mapa y devuelve el `id` del nodo pulsado (None si no se ha pulsado ninguno)."""
    if not nodos:
        return None
    maximo = max((n.importe for n in nodos if not n.centro), default=0.0)
    minimo = min((n.importe for n in nodos if not n.centro and n.importe > 0), default=0.0)
    elementos = []
    for n in nodos:
        if n.centro:
            radio = RADIO_MAX + 14
            color = n.color or _mezcla(1.0)
        else:
            radio = _radio(n.importe, maximo)
            t = 0.5 if maximo == minimo else (n.importe - minimo) / (maximo - minimo)
            color = n.color or _mezcla(math.sqrt(max(t, 0.0)))
        elementos.append(
            Node(
                id=n.id,
                label=n.etiqueta,
                title=_titulo(n),
                shape="image",
                image=svg_nodo(color, n.llenado, n.centro),
                size=radio,
                font={
                    "color": TEXTO,
                    "size": 15 if n.centro else 13,
                    "face": "Inter, sans-serif",
                    "strokeWidth": 4,
                    "strokeColor": FONDO,
                    "multi": False,
                },
                fixed=False,
                shapeProperties={"useBorderWithImage": False},
            )
        )
    lineas = [Edge(source=a, target=b, color=LINEA, width=2) for a, b in enlaces]
    return agraph(nodes=elementos, edges=lineas, config=configuracion(alto))


def leyenda_texto() -> str:
    return (
        "Cada círculo es una entidad: cuanto **más grande y más claro**, más dinero. "
        "La parte **de color** es lo gastado y la **gris**, lo que queda sin gastar. "
        "Puedes arrastrar los círculos; los conectados se mueven con ellos. Pulsa uno para ver más."
    )
