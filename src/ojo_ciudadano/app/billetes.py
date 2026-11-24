"""Frascos de billetes y mascota del ojo para el mapa general (D-038).

En el mapa de nodos, cada nodo es un **frasco** que cabe **100 billetes**: el frasco de la
Comunidad está lleno y el de cada consejería lleva tantos billetes como euros recibe **de cada
100** de la Comunidad. Los billetes **grises** son lo que quedó sin gastar. Lo que no llega a un
billete se pinta como un trozo de billete.

La tarjeta del año lleva la mascota: el ojo del logo (docs/marca.md) con manos que sujetan
billetes. Se pinta con un componente de Streamlit (`components.v2`) sin interacción.
"""

import base64
import math

import streamlit as st

from ojo_ciudadano.app import textos

CAPACIDAD = 100  # billetes que caben en un frasco
COLUMNAS = 5  # billetes por fila dentro del frasco
VERDES = ("#1E9E74", "#33B88C")  # filas alternas, para que se vean los billetes apilados
GRIS = "#5A6B86"  # sin gastar (algo más claro que el gris del mapa para verse tras el cristal)
TINTA = "#E7ECF3"  # trazo del logo
PUPILA = "#3D8BFD"  # pupila del logo


# --------------------------------------------------------------------------- cuentas
def billetes_de_cada_100(parte: float, total: float) -> float:
    """Cuántos billetes de cada 100 corresponden a `parte` (entre 0 y 100)."""
    if not total or total <= 0 or not parte or parte <= 0:
        return 0.0
    return min(CAPACIDAD * parte / total, float(CAPACIDAD))


def texto_de_cada_100(n: float) -> str:
    """«39 de cada 100 €», «menos de 1 de cada 100 €»."""
    if n < 0.5:
        return "menos de 1 de cada 100 €"
    return f"{round(n)} de cada 100 €"


def texto_corto(n: float) -> str:
    """Rótulo bajo el frasco: «39 €», «menos de 1 €» (de cada 100, lo dice la leyenda)."""
    return "menos de 1 €" if n < 0.5 else f"{round(n)} €"


# --------------------------------------------------------------------------- frasco
def _piezas(n: float, gastado: float | None) -> list[tuple[float, str]]:
    """(fracción, color) de cada billete, de abajo arriba: primero los gastados en verde y
    encima los no gastados en gris. `gastado` es la proporción gastada o None."""
    llenos = n if gastado is None else n * min(max(gastado, 0.0), 1.0)
    piezas = []
    for k in range(math.ceil(n)):
        fraccion = min(n - k, 1.0)
        fila = k // COLUMNAS
        verde = k + fraccion / 2 <= llenos
        piezas.append((fraccion, VERDES[fila % 2] if verde else GRIS))
    return piezas


def svg_frasco(n: float, gastado: float | None = None, centro: bool = False) -> str:
    """SVG de un frasco de cristal con `n` billetes apilados (como mucho 100)."""
    n = min(max(n, 0.0), float(CAPACIDAD))
    filas = CAPACIDAD // COLUMNAS
    x0, ancho = 21.0, 58.0  # interior del frasco
    abajo, alto = 90.0, 64.0
    paso_x, paso_y = ancho / COLUMNAS, alto / filas
    billetes = []
    for k, (fraccion, color) in enumerate(_piezas(n, gastado)):
        fila, columna = divmod(k, COLUMNAS)
        x = x0 + columna * paso_x + 0.5
        y = abajo - (fila + 1) * paso_y + 0.35
        billetes.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{(paso_x - 1) * fraccion:.2f}" '
            f'height="{paso_y - 0.7:.2f}" rx=".6" fill="{color}"/>'
        )
    borde = 0.75 if centro else 0.5
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">'
        # tapa metálica y cuello
        '<rect x="31" y="3" width="38" height="10" rx="3" fill="#9FB4CC"/>'
        '<rect x="31" y="3" width="38" height="4" rx="2" fill="#fff" fill-opacity=".35"/>'
        '<rect x="35" y="12" width="30" height="7" rx="2" fill="#dff4ff" fill-opacity=".10" '
        'stroke="#e6f6ff" stroke-opacity=".45" stroke-width="1.5"/>'
        # cuerpo de cristal
        # fondo oscuro para que las líneas del mapa no se vean a través del cristal
        '<rect x="14" y="18" width="72" height="79" rx="17" fill="#0A1E33" fill-opacity=".94"/>'
        '<rect x="14" y="18" width="72" height="79" rx="17" fill="#dff4ff" fill-opacity=".07"/>'
        + "".join(billetes)
        + '<rect x="19" y="25" width="5" height="62" rx="2.5" fill="#fff" fill-opacity=".13"/>'
        f'<rect x="14" y="18" width="72" height="79" rx="17" fill="none" stroke="#e6f6ff" '
        f'stroke-opacity="{borde}" stroke-width="{2.4 if centro else 2}"/>'
        "</svg>"
    )


def imagen_frasco(n: float, gastado: float | None = None, centro: bool = False) -> str:
    """El frasco como data URI, para usarlo de imagen de un nodo del mapa."""
    svg = svg_frasco(n, gastado, centro)
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def leyenda_frascos(con_gasto: bool) -> str:
    """Leyenda en HTML: un frasco de muestra y qué es cada billete."""
    frasco = svg_frasco(39, 0.9).replace('width="100" height="100"', 'width="44" height="44"')
    verde = (
        f'<svg width="26" height="12" viewBox="0 0 26 12"><rect width="26" height="12" rx="2" '
        f'fill="{VERDES[0]}"/></svg>'
    )
    gris = verde.replace(VERDES[0], GRIS)
    partes = [
        f'<span class="oc-ley">{frasco} En cada frasco caben 100 billetes</span>',
        f'<span class="oc-ley">{verde} 1 billete = 1 € de cada 100</span>',
    ]
    if con_gasto:
        partes.append(f'<span class="oc-ley">{gris} sin gastar</span>')
    partes.append('<span class="oc-ley">Bajo cada frasco: euros que recibe de cada 100</span>')
    return '<div class="oc-leyenda">' + "".join(partes) + "</div>"


# --------------------------------------------------------------------------- mascota
BILLETE = """
<symbol id="billete" viewBox="0 0 76 40">
  <rect x=".5" y=".5" width="75" height="39" rx="4" fill="currentColor"/>
  <rect x=".5" y=".5" width="75" height="19" rx="4" fill="#fff" fill-opacity=".10"/>
  <rect x="3.5" y="3.5" width="69" height="33" rx="2.5" fill="none" stroke="#fff"
        stroke-opacity=".38" stroke-width="1.2"/>
  <circle cx="38" cy="20" r="10.5" fill="#fff" fill-opacity=".16" stroke="#fff"
          stroke-opacity=".45" stroke-width="1.2"/>
  <text x="38" y="25" text-anchor="middle" font-size="14" font-weight="700" fill="#fff"
        fill-opacity=".92" font-family="Inter, sans-serif">€</text>
  <circle cx="11" cy="11" r="3.2" fill="#fff" fill-opacity=".28"/>
  <circle cx="65" cy="29" r="3.2" fill="#fff" fill-opacity=".28"/>
</symbol>
"""


def svg_ojo() -> str:
    """La mascota: el ojo del logo (mismo trazo y misma pupila) con dos brazos. Uno levanta un
    abanico de billetes y el otro saluda, mientras caen billetes. La pupila mira a los lados."""
    billete = '<use href="#billete" width="46" height="24" style="color:{c}"/>'
    abanico = "".join(
        f'<g transform="translate(40 70) rotate({giro}) translate(-23 -34)">'
        + billete.format(c=color)
        + "</g>"
        for giro, color in ((-38, "#178A66"), (-12, "#2BB386"), (14, "#1E9E74"))
    )
    cae = "".join(
        f'<g class="cae" style="animation-delay:{retraso}s"><g transform="translate({x} {y}) '
        f'rotate({giro})">{billete.format(c=color)}</g></g>'
        for x, y, giro, retraso, color in (
            (96, 4, -14, 0, "#2BB386"),
            (168, 14, 12, 1.4, "#1E9E74"),
            (122, 40, -6, 2.6, "#3CC495"),
        )
    )
    return f"""
<svg class="oc-ojo" viewBox="0 0 230 215" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-label="El ojo de Ojo Ciudadano levanta un abanico de billetes y saluda">
  <defs>{BILLETE}</defs>
  {cae}
  <ellipse cx="116" cy="204" rx="56" ry="7" fill="#000" fill-opacity=".28"/>
  <g class="oc-salta">
    <g class="abanico">{abanico}</g>
    <path d="M73 128 Q42 124 40 82" stroke="{TINTA}" stroke-width="8" fill="none"
          stroke-linecap="round"/>
    <circle cx="40" cy="78" r="9.5" fill="{TINTA}"/>
    <g class="saluda">
      <path d="M160 150 Q194 146 198 112" stroke="{TINTA}" stroke-width="8" fill="none"
            stroke-linecap="round"/>
      <circle cx="198" cy="106" r="9.5" fill="{TINTA}"/>
      <circle cx="190" cy="98" r="4" fill="{TINTA}"/>
    </g>
    <g transform="translate(57 72)">
      <path d="M102 72 C98 38 80 15 46 15 L16 15 L16 62 C16 90 34 104 68 105" fill="none"
            stroke="{TINTA}" stroke-width="13" stroke-linecap="round" stroke-linejoin="round"/>
      <circle class="pupila" cx="55" cy="67" r="13" fill="{PUPILA}"/>
    </g>
  </g>
</svg>"""


def svg_habitantes(millones_hab: float) -> str:
    """Fila de figuritas: una por cada millón de habitantes (la última, recortada)."""
    figura = '<circle cx="9" cy="6" r="5"/><rect x="2" y="12.5" width="14" height="17" rx="6.5"/>'
    piezas = []
    for k in range(math.ceil(millones_hab)):
        fraccion = min(millones_hab - k, 1.0)
        piezas.append(
            f'<svg x="{k * 22}" y="0" width="{18 * fraccion:.1f}" height="30" overflow="hidden">'
            f'<g fill="#7DB3FF">{figura}</g></svg>'
        )
    ancho = math.ceil(millones_hab) * 22
    return (
        f'<svg viewBox="0 0 {ancho} 30" width="{ancho}" height="30" role="img" '
        f'aria-label="{textos.numero(millones_hab * 1_000_000)} de habitantes">'
        + "".join(piezas)
        + "</svg>"
    )


# --------------------------------------------------------------------------- componente
CSS = """
.oc-leyenda { display: flex; flex-wrap: wrap; gap: 8px 24px; align-items: center;
  font-family: Inter, sans-serif; font-size: .9rem; color: #B9C6D8; margin: 2px 0 6px; }
.oc-ley { display: inline-flex; align-items: center; gap: 8px; }
"""

JS = """
export default function (component) {
  const { data, parentElement } = component;
  let raiz = parentElement.querySelector('.oc-html');
  if (!raiz) {
    raiz = document.createElement('div');
    raiz.className = 'oc-html';
    parentElement.appendChild(raiz);
  }
  if (raiz.dataset.contenido !== data) {
    raiz.innerHTML = data;
    raiz.dataset.contenido = data;
  }
}
"""

_componente = st.components.v2.component("ojo_billetes", css=CSS, js=JS)


def pintar(contenido: str, clave: str) -> None:
    """Muestra HTML propio con SVG (st.html no deja usar `<use>`). El contenido lo genera el
    código; los textos que vengan de la base deben llegar ya escapados."""
    _componente(data=contenido, key=clave)
