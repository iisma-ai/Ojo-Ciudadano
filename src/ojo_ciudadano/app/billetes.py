"""Treemap de billetes y figura del ciudadano para el mapa general (D-038).

Cada bloque es una consejería (o un contrato) y su **tamaño** es el dinero. Dentro se dibujan
billetes: **cada billete vale lo mismo en todo el gráfico** (p. ej. 100 millones de euros), así
que cuanto más dinero, más billetes; lo que no llega a un billete se pinta como un trozo de
billete. Los billetes **grises** son el dinero que quedó sin gastar.

Es un componente de Streamlit (`components.v2`): un SVG propio que devuelve el bloque pulsado.
Los textos que vienen de la base se escapan antes de entrar en el SVG.
"""

import html
import math
from dataclasses import dataclass

import streamlit as st

from ojo_ciudadano.app import textos

ANCHO, ALTO = 1000, 560  # unidades del lienzo (el SVG se adapta al ancho de la columna)
PROPORCION = 1.9  # ancho / alto de un billete
HUECO = 4  # separación entre bloques
MARGEN = 7  # margen interior del bloque
VERDES = ["#1E9E74", "#2BB386", "#178A66", "#3CC495", "#23A38C", "#33A86F"]
GRIS = "#33415C"  # dinero sin gastar (el mismo gris que el mapa de red)


@dataclass
class Bloque:
    """Un bloque del treemap. `gastado` es la proporción gastada (0 a 1) o None si no aplica."""

    id: str
    nombre: str
    importe: float
    gastado: float | None = None
    detalle: str = ""
    color: str | None = None


# --------------------------------------------------------------------------- diseño
def _peor(fila: list[float], lado: float) -> float:
    """Peor proporción (alargamiento) de una fila del treemap: cuanto más cerca de 1, mejor."""
    suma = sum(fila)
    return max(
        max(lado * lado * v / (suma * suma), (suma * suma) / (lado * lado * v)) for v in fila
    )


def treemap(valores: list[float], x: float, y: float, ancho: float, alto: float) -> list[tuple]:
    """Rectángulos (x, y, ancho, alto) con área proporcional a cada valor, en el mismo orden.

    Algoritmo «squarified» (Bruls, Huizing y van Wijk, 2000): va llenando filas a lo largo del
    lado corto mientras los rectángulos no se alarguen más. Los valores deben venir de mayor a
    menor y ser positivos.
    """
    total = sum(valores)
    if not valores or total <= 0:
        return []
    escala = ancho * alto / total
    areas = [v * escala for v in valores]
    rects: list[tuple] = []
    i = 0
    while i < len(areas):
        lado = min(ancho, alto)
        fila = [areas[i]]
        i += 1
        while i < len(areas) and _peor(fila + [areas[i]], lado) <= _peor(fila, lado):
            fila.append(areas[i])
            i += 1
        grosor = sum(fila) / lado
        posicion = 0.0
        for area in fila:
            largo = area / grosor
            if ancho >= alto:  # fila vertical a la izquierda
                rects.append((x, y + posicion, grosor, largo))
            else:  # fila horizontal arriba
                rects.append((x + posicion, y, largo, grosor))
            posicion += largo
        if ancho >= alto:
            x, ancho = x + grosor, ancho - grosor
        else:
            y, alto = y + grosor, alto - grosor
    return rects


def valor_billete(total: float, objetivo: int = 320) -> float:
    """Valor redondo de un billete (1, 2 o 5 por una potencia de 10) para que el gráfico entero
    tenga unos `objetivo` billetes."""
    ideal = total / objetivo
    potencia = 10 ** math.floor(math.log10(ideal))
    candidatos = [m * potencia for m in (1, 2, 5, 10)]
    return min(candidatos, key=lambda c: abs(math.log(c / ideal)))


def rejilla(n: float, ancho: float, alto: float) -> tuple[int, int, float]:
    """Columnas, filas y alto de billete que mejor caben en el rectángulo para `n` billetes
    (contando el trozo final como uno)."""
    piezas = max(math.ceil(n), 1)
    mejor = (1, piezas, 0.0)
    for columnas in range(1, piezas + 1):
        filas = math.ceil(piezas / columnas)
        alto_billete = min(ancho / (columnas * PROPORCION), alto / filas)
        if alto_billete > mejor[2]:
            mejor = (columnas, filas, alto_billete)
    return mejor


def texto_valor(valor: float) -> str:
    """«100 millones de €», «2 millones de €», «500.000 €»."""
    if valor >= 1_000_000_000:
        cifra = textos.numero(valor / 1_000_000_000)
        return f"{cifra} mil millones de €"
    if valor >= 1_000_000:
        cifra = f"{valor / 1_000_000:,.0f}".replace(",", ".")
        return f"{cifra} {'millón' if cifra == '1' else 'millones'} de €"
    return f"{valor:,.0f} €".replace(",", ".")


def de_cada_100(parte: float, total: float) -> str:
    cuota = 100 * parte / total if total else 0
    if cuota < 1:
        return "menos de 1 € de cada 100"
    return f"{cuota:.0f} € de cada 100"


# --------------------------------------------------------------------------- dibujo
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
  <rect x="9" y="27" width="16" height="1.6" rx=".8" fill="#fff" fill-opacity=".3"/>
  <rect x="51" y="11" width="16" height="1.6" rx=".8" fill="#fff" fill-opacity=".3"/>
</symbol>
"""


def _recortar(texto: str, caracteres: int) -> str:
    if len(texto) <= caracteres:
        return texto
    return texto[: max(caracteres - 1, 1)].rstrip() + "…"


def _billetes_bloque(bloque: Bloque, rect: tuple, valor: float, color: str, retraso: float) -> str:
    """Billetes de un bloque: los gastados en color, los no gastados en gris y el último,
    recortado si no llega a un billete entero."""
    x, y, ancho, alto = rect
    n = bloque.importe / valor
    if n <= 0:
        return ""
    columnas, filas, alto_b = rejilla(n, ancho - 2 * MARGEN, alto - 2 * MARGEN)
    ancho_b = alto_b * PROPORCION
    hueco = max(alto_b * 0.08, 0.6)
    origen_x = x + (ancho - columnas * ancho_b) / 2
    origen_y = y + (alto - filas * alto_b) / 2
    llenos = n if bloque.gastado is None else n * bloque.gastado
    piezas = []
    for k in range(math.ceil(n)):
        fila, columna = divmod(k, columnas)
        bx = origen_x + columna * ancho_b + hueco / 2
        by = origen_y + fila * alto_b + hueco / 2
        w, h = ancho_b - hueco, alto_b - hueco
        fraccion = min(n - k, 1.0)
        # Un billete cuenta como gastado si su mitad cae dentro de lo gastado.
        tono = color if k + fraccion / 2 <= llenos else GRIS
        clase = "b" if tono == color else "b vacio"
        uso = (
            f'<use href="#billete" class="{clase}" style="color:{tono};'
            f'animation-delay:{retraso + k * 0.004:.3f}s" '
            f'x="{bx:.1f}" y="{by:.1f}" width="{w:.1f}" height="{h:.1f}"/>'
        )
        if fraccion < 1:  # trozo de billete: se recorta por la derecha
            uso = (
                f'<svg x="{bx:.1f}" y="{by:.1f}" width="{w * fraccion:.1f}" height="{h:.1f}" '
                f'overflow="hidden">'
                + uso.replace(f'x="{bx:.1f}" y="{by:.1f}"', 'x="0" y="0"')
                + "</svg>"
            )
        piezas.append(uso)
    return "".join(piezas)


def _etiqueta(bloque: Bloque, rect: tuple, total: float, con_cuota: bool) -> str:
    """Nombre y cifra sobre un velo oscuro, solo si el bloque tiene sitio."""
    x, y, ancho, alto = rect
    if ancho < 92 or alto < 46:
        return ""
    grande = ancho >= 170 and alto >= 80
    tam_nombre, tam_cifra = (15, 12.5) if grande else (11.5, 10)
    nombre = html.escape(_recortar(bloque.nombre, int((ancho - 24) / (tam_nombre * 0.56))))
    cifra = textos.millones(bloque.importe)
    if grande and con_cuota:
        cifra += " · " + de_cada_100(bloque.importe, total)
    cifra = html.escape(_recortar(cifra, int((ancho - 24) / (tam_cifra * 0.55))))
    largo = max(len(nombre) * tam_nombre * 0.56, len(cifra) * tam_cifra * 0.55)
    ancho_velo = min(largo + 18, ancho - 12)
    alto_velo = tam_nombre + tam_cifra + 16
    vx, vy = x + 6, y + alto - alto_velo - 6
    return (
        f'<rect class="velo" x="{vx:.1f}" y="{vy:.1f}" width="{ancho_velo:.1f}" '
        f'height="{alto_velo:.1f}" rx="7"/>'
        f'<text class="nombre" x="{vx + 9:.1f}" y="{vy + tam_nombre + 4:.1f}" '
        f'font-size="{tam_nombre}">{nombre}</text>'
        f'<text class="cifra" x="{vx + 9:.1f}" y="{vy + tam_nombre + tam_cifra + 9:.1f}" '
        f'font-size="{tam_cifra}">{cifra}</text>'
    )


def svg_treemap(
    bloques: list[Bloque],
    valor: float,
    alto: int = ALTO,
    ancho: int = ANCHO,
    con_cuota: bool = True,
) -> str:
    """SVG del treemap de billetes. `valor` es lo que vale cada billete; `con_cuota` añade
    «X € de cada 100» (solo tiene sentido si los bloques suman un total con significado)."""
    bloques = sorted((b for b in bloques if b.importe > 0), key=lambda b: -b.importe)
    total = sum(b.importe for b in bloques)
    rects = treemap([b.importe for b in bloques], 0, 0, ancho, alto)
    partes = []
    for i, (bloque, rect) in enumerate(zip(bloques, rects, strict=True)):
        rx, ry, rw, rh = rect
        r = (rx + HUECO / 2, ry + HUECO / 2, max(rw - HUECO, 1), max(rh - HUECO, 1))
        color = bloque.color or VERDES[i % len(VERDES)]
        titulo = f"{bloque.nombre}: {textos.euros(bloque.importe)}"
        if con_cuota:
            titulo += f" ({de_cada_100(bloque.importe, total)})"
        if bloque.gastado is not None:
            titulo += f". Gastado: {textos.porcentaje(bloque.gastado)}"
        if bloque.detalle:
            titulo += f". {bloque.detalle}"
        partes.append(
            f'<g class="bloque" data-id="{html.escape(bloque.id)}" tabindex="0" role="button" '
            f'aria-label="{html.escape(titulo)}"><title>{html.escape(titulo)}</title>'
            f'<rect class="fondo" x="{r[0]:.1f}" y="{r[1]:.1f}" width="{r[2]:.1f}" '
            f'height="{r[3]:.1f}" rx="9"/>'
            + _billetes_bloque(bloque, r, valor, color, retraso=min(i * 0.05, 0.6))
            + _etiqueta(bloque, r, total, con_cuota)
            + "</g>"
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" '
        f'role="img" aria-label="Reparto del dinero en billetes"><defs>{BILLETE}</defs>'
        + "".join(partes)
        + "</svg>"
    )


CSS = """
.oc-billetes > svg { width: 100%; height: auto; display: block; overflow: visible; }
.bloque { cursor: pointer; outline: none; }
.bloque .fondo { fill: rgba(255,255,255,.035); stroke: rgba(170,225,255,.16); stroke-width: 1; }
.bloque:hover .fondo, .bloque:focus-visible .fondo {
  fill: rgba(125,179,255,.10); stroke: rgba(170,225,255,.65); stroke-width: 1.6; }
.bloque:hover .b:not(.vacio) { filter: brightness(1.18); }
.b { animation: aparece .45s ease-out both; }
.vacio { opacity: .75; }
.velo { fill: rgba(2,12,23,.72); stroke: rgba(170,225,255,.18); }
.nombre { fill: #E7ECF3; font-weight: 600; font-family: Inter, sans-serif; }
.cifra { fill: #B9D4F5; font-family: Inter, sans-serif; }
.oc-leyenda { display: flex; flex-wrap: wrap; gap: 8px 22px; align-items: center;
  font-family: Inter, sans-serif; font-size: .88rem; color: #B9C6D8; margin: 2px 0 10px; }
.oc-ley { display: inline-flex; align-items: center; gap: 8px; }
@keyframes aparece { from { opacity: 0; transform: translateY(-6px); } to { opacity: 1; } }
@media (prefers-reduced-motion: reduce) { .b { animation: none; } }
"""

JS = """
export default function (component) {
  const { data, setTriggerValue, parentElement } = component;
  let raiz = parentElement.querySelector('.oc-billetes');
  if (!raiz) {
    raiz = document.createElement('div');
    raiz.className = 'oc-billetes';
    parentElement.appendChild(raiz);
  }
  if (raiz.dataset.contenido !== data) {
    raiz.innerHTML = data;
    raiz.dataset.contenido = data;
  }
  raiz.querySelectorAll('.bloque').forEach((bloque) => {
    const elegir = () => setTriggerValue('elegido', bloque.dataset.id);
    bloque.onclick = elegir;
    bloque.onkeydown = (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); elegir(); }
    };
  });
}
"""

_componente = st.components.v2.component("ojo_billetes", css=CSS, js=JS)


def mostrar(
    bloques: list[Bloque],
    valor: float,
    clave: str,
    alto: int = ALTO,
    ancho: int = ANCHO,
    con_cuota: bool = True,
) -> str | None:
    """Pinta el treemap y devuelve el id del bloque pulsado en esta ejecución (o None).
    `ancho` y `alto` son unidades del lienzo: conviene que `ancho` se parezca a los píxeles de
    la columna para que los rótulos se lean a su tamaño."""
    resultado = _componente(
        data=svg_treemap(bloques, valor, alto, ancho, con_cuota),
        key=clave,
        on_elegido_change=lambda: None,
    )
    return getattr(resultado, "elegido", None)


def leyenda(valor: float, con_gasto: bool) -> str:
    """Leyenda en HTML: un billete de muestra, lo que vale y, si hay gasto, el gris."""
    muestra = (
        '<svg viewBox="0 0 76 40" width="38" height="20" style="color:{c}">'
        f"<defs>{BILLETE}</defs>"
        '<use href="#billete" width="76" height="40"/></svg>'
    )
    partes = [f'<span class="oc-ley">{muestra.format(c=VERDES[0])} = {texto_valor(valor)}</span>']
    if con_gasto:
        partes.append(
            f'<span class="oc-ley">{muestra.format(c=GRIS)} = dinero que quedó sin gastar</span>'
        )
    partes.append('<span class="oc-ley">Pulsa un bloque para ver qué hay dentro</span>')
    return '<div class="oc-leyenda">' + "".join(partes) + "</div>"


# --------------------------------------------------------------------------- el ciudadano
def svg_ciudadano() -> str:
    """Figura de una persona con los brazos en alto sujetando un abanico de billetes, mientras
    caen otros. Ilustración propia (sin parecido con ningún personaje)."""
    billete = '<use href="#billete-c" width="46" height="24" style="color:{c}"/>'
    abanico = "".join(
        f'<g transform="translate(110 54) rotate({giro}) translate(-23 {alto})">'
        + billete.format(c=color)
        + "</g>"
        for giro, alto, color in ((-28, -30, "#178A66"), (0, -34, "#2BB386"), (28, -30, "#1E9E74"))
    )
    return f"""
<svg class="oc-persona" viewBox="0 0 220 230" xmlns="http://www.w3.org/2000/svg"
     role="img" aria-label="Una persona sujeta un abanico de billetes">
  <defs>
    {BILLETE.replace('id="billete"', 'id="billete-c"')}
    <linearGradient id="cuerpo" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#7DB3FF"/><stop offset="1" stop-color="#2F6FD6"/>
    </linearGradient>
    <radialGradient id="cara" cx=".4" cy=".35" r=".8">
      <stop offset="0" stop-color="#F3F8FF"/><stop offset="1" stop-color="#BFD7F5"/>
    </radialGradient>
  </defs>
  <g class="cae" style="animation-delay:0s"><g transform="translate(20 10) rotate(-18)">
    {billete.format(c="#2BB386")}</g></g>
  <g class="cae" style="animation-delay:1.3s"><g transform="translate(160 0) rotate(14)">
    {billete.format(c="#1E9E74")}</g></g>
  <g class="cae" style="animation-delay:2.4s"><g transform="translate(170 70) rotate(-8)">
    {billete.format(c="#3CC495")}</g></g>
  <ellipse cx="110" cy="220" rx="52" ry="7" fill="#000" fill-opacity=".28"/>
  <g class="oc-salta">
    <g class="abanico">{abanico}
    </g>
    <path d="M78 128 Q64 92 90 62" stroke="url(#cuerpo)" stroke-width="13" fill="none"
          stroke-linecap="round"/>
    <path d="M142 128 Q156 92 130 62" stroke="url(#cuerpo)" stroke-width="13" fill="none"
          stroke-linecap="round"/>
    <circle cx="90" cy="60" r="8" fill="url(#cara)"/>
    <circle cx="130" cy="60" r="8" fill="url(#cara)"/>
    <rect x="76" y="118" width="68" height="74" rx="30" fill="url(#cuerpo)"/>
    <rect x="86" y="186" width="18" height="30" rx="9" fill="#2558B0"/>
    <rect x="116" y="186" width="18" height="30" rx="9" fill="#2558B0"/>
    <circle cx="110" cy="98" r="27" fill="url(#cara)"/>
    <g class="ojos">
      <circle cx="100" cy="96" r="3.6" fill="#0B2236"/>
      <circle cx="120" cy="96" r="3.6" fill="#0B2236"/>
    </g>
    <path d="M100 108 Q110 117 120 108" stroke="#0B2236" stroke-width="3" fill="none"
          stroke-linecap="round"/>
    <circle cx="93" cy="106" r="4" fill="#7DB3FF" fill-opacity=".45"/>
    <circle cx="127" cy="106" r="4" fill="#7DB3FF" fill-opacity=".45"/>
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


def pintar(contenido: str, clave: str) -> None:
    """Muestra HTML propio (con SVG) mediante el mismo componente, sin bloques pulsables."""
    _componente(data=contenido, key=clave)
