"""Frascos de billetes y mascota del ojo para el mapa general (D-038).

En el mapa de nodos, cada nodo es un **frasco** que cabe **100 billetes**: el frasco de la
Comunidad está lleno y el de cada consejería lleva tantos billetes como euros recibe **de cada
100** de la Comunidad. Los billetes **grises** son lo que quedó sin gastar. Lo que no llega a un
billete se pinta como un trozo de billete.

La tarjeta del año lleva la mascota: el ojo del logo (docs/marca.md) con manos que sujetan
billetes. Se pinta con un componente de Streamlit (`components.v2`) sin interacción.
"""

import base64
import html
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


def rotulo(n: float) -> str:
    """Lo que pone la etiqueta del frasco: «39 €», «<1 €» (de cada 100, lo dice la leyenda)."""
    return "<1 €" if n < 0.5 else f"{round(n)} €"


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


# Silueta del frasco: hombros redondeados que bajan del cuello a un cuerpo ancho de fondo curvo.
SILUETA = (
    "M36 20 C36 24 33 25 27 26 C19 27.5 15 32 15 40 L15 84 C15 92 21 97 29 97 L71 97 "
    "C79 97 85 92 85 84 L85 40 C85 32 81 27.5 73 26 C67 25 64 24 64 20 Z"
)
DEFS_FRASCO = (
    "<defs>"
    # cristal: bordes más claros (como un vidrio de verdad) y el centro oscuro y transparente
    '<linearGradient id="frV" x1="0" x2="1"><stop offset="0" stop-color="#cfeeff" '
    'stop-opacity=".34"/><stop offset=".14" stop-color="#cfeeff" stop-opacity=".06"/>'
    '<stop offset=".8" stop-color="#cfeeff" stop-opacity=".04"/><stop offset="1" '
    'stop-color="#cfeeff" stop-opacity=".26"/></linearGradient>'
    # tapa azul de la marca, con volumen
    '<linearGradient id="frT" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8CC2FF"/>'
    '<stop offset=".45" stop-color="#3D8BFD"/><stop offset="1" stop-color="#1F5FBF"/>'
    "</linearGradient>"
    # reflejo largo del lado izquierdo
    '<linearGradient id="frR" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" '
    'stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
    # brillo de cada billete (más claro arriba)
    '<linearGradient id="frB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" '
    'stop-opacity=".28"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>'
    '<clipPath id="frC"><path d="' + SILUETA + '"/></clipPath>'
    "</defs>"
)


def svg_frasco(
    n: float, gastado: float | None = None, centro: bool = False, etiqueta: str | None = None
) -> str:
    """SVG de un frasco de cristal con `n` billetes apilados (como mucho 100) y, si se da, una
    etiqueta pegada arriba con los euros que recibe. Con la estética de la presentación: cristal
    con los bordes claros y reflejos suaves, tapa azul de la marca y billetes con brillo."""
    n = min(max(n, 0.0), float(CAPACIDAD))
    filas = CAPACIDAD // COLUMNAS
    x0, ancho = 19.0, 62.0  # interior del frasco
    abajo, alto = 93.0, 46.0  # los billetes se apilan por debajo de la etiqueta
    paso_x, paso_y = ancho / COLUMNAS, alto / filas
    billetes = []
    for k, (fraccion, color) in enumerate(_piezas(n, gastado)):
        fila, columna = divmod(k, COLUMNAS)
        x = x0 + columna * paso_x + 0.45
        y = abajo - (fila + 1) * paso_y + 0.3
        w = (paso_x - 0.9) * fraccion
        h = paso_y - 0.6
        billetes.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx=".8" '
            f'fill="{color}"/><rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
            'rx=".8" fill="url(#frB)"/>'
        )
    papel = ""
    if etiqueta:
        papel = (
            '<rect x="24" y="31" width="52" height="19" rx="5" fill="#0B2236" fill-opacity=".35"/>'
            '<rect x="24" y="30" width="52" height="19" rx="5" fill="#F7F1DF"/>'
            '<rect x="24" y="30" width="52" height="5" rx="2.5" fill="#fff" fill-opacity=".5"/>'
            f'<text x="50" y="44.5" text-anchor="middle" font-family="Outfit, Arial, sans-serif" '
            f'font-size="14" font-weight="700" fill="#0B2236">{html.escape(etiqueta)}</text>'
        )
    borde = 0.7 if centro else 0.5
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">'
        + DEFS_FRASCO
        # sombra suave en el suelo
        + '<ellipse cx="50" cy="97.5" rx="30" ry="2.2" fill="#000814" fill-opacity=".45"/>'
        # cuerpo: fondo oscuro para que las líneas del mapa no se vean a través del cristal
        + f'<path d="{SILUETA}" fill="#071A2D" fill-opacity=".92"/>'
        + '<g clip-path="url(#frC)">'
        + "".join(billetes)
        # luz que entra por el cristal y reflejos: uno largo a la izquierda y otro corto
        + '<rect x="0" y="0" width="100" height="100" fill="url(#frV)"/>'
        + '<path d="M20.5 40 C20.5 34 23 31 27 30 L27 86 C23 85 20.5 82 20.5 78 Z" '
        'fill="url(#frR)" fill-opacity=".75"/>'
        + '<rect x="76" y="38" width="3" height="14" rx="1.5" fill="#fff" fill-opacity=".22"/>'
        + "</g>"
        # borde del cristal, fino y claro
        + f'<path d="{SILUETA}" fill="none" stroke="#e6f6ff" stroke-opacity="{borde}" '
        f'stroke-width="{2 if centro else 1.6}"/>'
        # cuello y tapa de rosca
         + '<rect x="35" y="15" width="30" height="7" rx="2" fill="#cfeeff" fill-opacity=".12" '
        'stroke="#e6f6ff" stroke-opacity=".45" stroke-width="1.2"/>'
        + '<rect x="31" y="4" width="38" height="12" rx="4" fill="url(#frT)"/>'
        + '<rect x="31" y="11" width="38" height="1.4" fill="#16418A" fill-opacity=".55"/>'
        + '<rect x="34" y="5.5" width="20" height="2.4" rx="1.2" fill="#fff" fill-opacity=".5"/>'
        + papel
        + "</svg>"
    )


def imagen_frasco(n: float, gastado: float | None = None, centro: bool = False) -> str:
    """El frasco como data URI, con su etiqueta de euros, para la imagen de un nodo del mapa."""
    svg = svg_frasco(n, gastado, centro, etiqueta=rotulo(n))
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def leyenda_frascos(con_gasto: bool) -> str:
    """Leyenda en HTML: un frasco de muestra y qué es cada billete."""
    frasco = svg_frasco(39, 0.9, etiqueta="39 €").replace(
        'width="100" height="100"', 'width="44" height="44"'
    )
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
    partes.append('<span class="oc-ley">La etiqueta: euros que recibe de cada 100</span>')
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
        fill-opacity=".92" font-family="Outfit, sans-serif">€</text>
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


# Animaciones de la mascota (en la tarjeta del mapa y en la portada). Quietas con «reducir
# movimiento».
# Fluidez (D-041): las animaciones dentro de un SVG no van a la tarjeta gráfica; el navegador
# vuelve a pintar el dibujo en cada fotograma. Por eso la mascota se mueve unas vueltas al
# llegar (unos 10 s) y se queda quieta; al pasar el ratón por encima vuelve a moverse.
# `contain` limita el repintado a su recuadro.
VUELTAS_OJO = 4
CSS_OJO = f"""
.oc-ojo {{ width:210px; max-width:42vw; height:auto; flex:0 0 auto; contain:layout paint; }}
.oc-salta {{ animation:salta 2.6s ease-in-out {VUELTAS_OJO}; transform-origin:110px 210px; }}
.abanico {{ animation:abanico 2.6s ease-in-out {VUELTAS_OJO}; transform-origin:40px 78px; }}
.saluda {{ animation:saluda 1.6s ease-in-out {VUELTAS_OJO + 2}; transform-origin:160px 150px; }}
.pupila {{ animation:mira 6s ease-in-out 2; transform-box:fill-box;
  transform-origin:center; }}
.cae {{ animation:cae 4.2s linear 2; opacity:0; }}
.oc-ojo:hover .oc-salta, .oc-ojo:hover .abanico, .oc-ojo:hover .saluda,
.oc-ojo:hover .pupila, .oc-ojo:hover .cae {{ animation-iteration-count:infinite; }}
@keyframes salta {{ 0%,100% {{ transform:translateY(0) }} 50% {{ transform:translateY(-7px) }} }}
@keyframes abanico {{ 0%,100% {{ transform:rotate(-4deg) }} 50% {{ transform:rotate(4deg) }} }}
@keyframes saluda {{ 0%,100% {{ transform:rotate(0) }} 50% {{ transform:rotate(-12deg) }} }}
@keyframes mira {{ 0%,30%,100% {{ transform:translate(0,0) }}
  40%,55% {{ transform:translate(-6px,-3px) }} 65%,85% {{ transform:translate(7px,-4px) }} }}
@keyframes cae {{ 0% {{ transform:translateY(-10px); opacity:0 }} 15% {{ opacity:.9 }}
  85% {{ opacity:.9 }} 100% {{ transform:translateY(150px); opacity:0 }} }}
@media (prefers-reduced-motion: reduce) {{
  .oc-salta, .abanico, .saluda, .pupila,
  .oc-ojo:hover .oc-salta, .oc-ojo:hover .abanico, .oc-ojo:hover .saluda,
  .oc-ojo:hover .pupila {{ animation:none; }}
  .cae, .oc-ojo:hover .cae {{ animation:none; opacity:.8; }} }}
"""


# --------------------------------------------------------------------------- portada
COLOR_SENAL = "#7DB3FF"  # señales en azul de cristal (D-042, docs/marca.md); nunca rojo
VACIO = "#33415C"


def svg_cuadricula(n: float, que: str = "tienen esta señal", lado: int = 14, hueco: int = 3) -> str:
    """Cuadrícula de 100 contratos: los `n` primeros en azul claro (los que tienen la señal) y
    el resto en gris. Si `n` no llega a 1, el primer cuadrado se pinta a medias para que se vea
    que hay alguno."""
    n = min(max(n, 0.0), 100.0)
    llenos = round(n)
    total = 10 * lado + 9 * hueco
    piezas = []
    for k in range(100):
        fila, columna = divmod(k, 10)
        x, y = columna * (lado + hueco), fila * (lado + hueco)
        color = COLOR_SENAL if k < llenos else VACIO
        piezas.append(
            f'<rect x="{x}" y="{y}" width="{lado}" height="{lado}" rx="3" fill="{color}"/>'
        )
        if k == 0 and llenos == 0 and n > 0:
            piezas.append(
                f'<rect x="{x}" y="{y}" width="{lado / 2}" height="{lado}" rx="2" '
                f'fill="{COLOR_SENAL}"/>'
            )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total} {total}" width="{total}" '
        f'height="{total}" role="img" aria-label="{texto_de_100_contratos(n, que)}">'
        + "".join(piezas)
        + "</svg>"
    )


def cifra_de_100(n: float) -> str:
    """«39», o «menos de 1» si hay alguno pero no llega a uno de cada 100."""
    return "menos de 1" if 0 < n < 0.5 else str(round(n))


def texto_de_100_contratos(n: float, que: str = "tienen esta señal") -> str:
    """«39 de cada 100 contratos tienen una sola oferta»."""
    return f"{cifra_de_100(n)} de cada 100 contratos {que}"


def _icono(contenido: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" '
        f'aria-hidden="true">{contenido}</svg>'
    )


ICONOS_PUERTA = {
    "dinero": svg_frasco(39, 0.95, etiqueta="39 €").replace(
        'width="100" height="100"', 'width="64" height="64" aria-hidden="true"'
    ),
    # lupa sobre un contrato con una banderita del color de las señales
    "revisar": _icono(
        '<rect x="8" y="6" width="34" height="44" rx="5" fill="#0B2236" stroke="#9FB6CC" '
        'stroke-width="2.5"/><rect x="15" y="16" width="20" height="3" rx="1.5" fill="#9FB6CC"/>'
        '<rect x="15" y="24" width="16" height="3" rx="1.5" fill="#9FB6CC"/>'
        f'<path d="M36 8 v10 l5 -3 l5 3 v-10z" fill="{COLOR_SENAL}"/>'
        '<circle cx="38" cy="38" r="12" fill="#0B2236" fill-opacity=".6" stroke="#E7ECF3" '
        'stroke-width="4"/><path d="M47 47 L57 57" stroke="#E7ECF3" stroke-width="6" '
        'stroke-linecap="round"/>'
    ),
    # edificio de una empresa y edificio público
    "buscar": _icono(
        '<rect x="6" y="20" width="24" height="38" rx="3" fill="#0B2236" stroke="#9FB6CC" '
        'stroke-width="2.5"/><path d="M34 26 L47 16 L60 26 Z" fill="#7DB3FF"/>'
        '<rect x="35" y="26" width="24" height="32" rx="2" fill="#0B2236" stroke="#7DB3FF" '
        'stroke-width="2.5"/><rect x="39" y="32" width="3" height="20" fill="#7DB3FF"/>'
        '<rect x="46" y="32" width="3" height="20" fill="#7DB3FF"/>'
        '<rect x="53" y="32" width="3" height="20" fill="#7DB3FF"/>'
        + "".join(
            f'<rect x="{x}" y="{y}" width="5" height="5" rx="1" fill="#9FB6CC"/>'
            for x in (11, 20)
            for y in (27, 36, 45)
        )
    ),
    # bocadillo con la pupila del logo
    "asistente": _icono(
        '<path d="M8 10 h48 a6 6 0 0 1 6 6 v24 a6 6 0 0 1 -6 6 h-28 l-12 10 v-10 h-8 '
        'a6 6 0 0 1 -6 -6 v-24 a6 6 0 0 1 6 -6z" fill="#0B2236" stroke="#E7ECF3" '
        f'stroke-width="3"/><circle cx="32" cy="28" r="7" fill="{PUPILA}"/>'
        '<circle cx="18" cy="28" r="3.5" fill="#9FB6CC"/><circle cx="46" cy="28" r="3.5" '
        'fill="#9FB6CC"/>'
    ),
}


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


# --------------------------------------------------------------------------- contratos menores
def _documento(ancho: int, color: str, trazo: str) -> str:
    """Icono de un contrato: una hoja con la esquina doblada y unas líneas de texto."""
    alto = round(ancho * 1.3)
    return (
        f'<svg viewBox="0 0 40 52" width="{ancho}" height="{alto}" aria-hidden="true">'
        f'<path d="M3 3 h24 l10 10 v36 h-34 z" fill="{color}" stroke="{trazo}" '
        'stroke-width="2" stroke-linejoin="round"/>'
        f'<path d="M27 3 v10 h10" fill="none" stroke="{trazo}" stroke-width="2" '
        'stroke-linejoin="round"/>'
        + "".join(
            f'<rect x="9" y="{y}" width="{w}" height="2.6" rx="1.3" fill="{trazo}" '
            'fill-opacity=".7"/>'
            for y, w in ((20, 20), (27, 22), (34, 16), (41, 19))
        )
        + "</svg>"
    )


def html_menores(detalle: dict, ventana: list[dict], contrato_id: str) -> str:
    """E-03 (D-042): un contrato grande con la suma de los contratos menores y el máximo de un
    contrato menor, y debajo un icono por cada contrato menor (este, en azul). Al pasar el ratón
    por un icono se ve su precio, su fecha y su título."""
    suma = sum(c["importe"] for c in ventana)
    veces = suma / detalle["umbral"] if detalle["umbral"] else 0
    iconos = []
    for c in ventana:
        es_este = c["contrato_id"] == contrato_id
        pista = f"{textos.euros(c['importe'])} · {c['fecha'].strftime('%d/%m/%Y')}" + (
            " · este contrato" if es_este else ""
        )
        titulo = html.escape((c["titulo"] or "")[:110])
        iconos.append(
            f'<div class="oc-menor{" este" if es_este else ""}" tabindex="0" '
            f'title="{html.escape(pista)}">'
            + _documento(
                34, "#2F6FD6" if es_este else "#33415C", "#E7ECF3" if es_este else "#93A1B8"
            )
            + ('<span class="oc-este">este</span>' if es_este else "")
            + f'<div class="oc-pista"><b>{html.escape(pista)}</b>'
            + (f"<br>{titulo}" if titulo else "")
            + "</div></div>"
        )
    return f"""
<style>
.oc-r03 {{ font-family: Outfit, sans-serif; color: #E7ECF3; }}
.oc-grande {{ display: flex; gap: 16px; align-items: center; padding: 12px 14px;
  border-radius: 12px; background: rgba(125,179,255,.08); border: 1px solid rgba(125,179,255,.3); }}
.oc-grande p {{ margin: 0; line-height: 1.45; }}
.oc-suma {{ font-size: 1.05rem; }}
.oc-suma b {{ font-size: 1.35rem; color: #fff; }}
.oc-max {{ color: #B9C6D8; font-size: .95rem; }}
.oc-veces {{ color: #7DB3FF; font-size: .9rem; font-weight: 600; }}
.oc-titulo-menores {{ margin: 14px 0 8px; color: #B9C6D8; font-size: .95rem; }}
.oc-iconos {{ display: flex; flex-wrap: wrap; gap: 10px; }}
.oc-menor {{ position: relative; display: flex; flex-direction: column; align-items: center;
  cursor: default; outline: none; transition: transform .15s; }}
.oc-menor:hover, .oc-menor:focus-visible {{ transform: translateY(-3px); }}
.oc-este {{ font-size: .72rem; color: #7DB3FF; font-weight: 600; margin-top: 2px; }}
.oc-pista {{ visibility: hidden; opacity: 0; position: absolute; bottom: calc(100% + 8px);
  left: 50%; transform: translateX(-50%); width: max-content; max-width: 240px; z-index: 5;
  background: #0B2236; border: 1px solid rgba(170,225,255,.35); border-radius: 8px;
  padding: 7px 10px; font-size: .8rem; line-height: 1.35; color: #B9C6D8;
  box-shadow: 0 8px 22px rgba(0,8,22,.55); transition: opacity .12s; pointer-events: none; }}
.oc-pista b {{ color: #fff; }}
.oc-menor:hover .oc-pista, .oc-menor:focus-visible .oc-pista {{ visibility: visible; opacity: 1; }}
</style>
<div class="oc-r03">
  <div class="oc-grande">
    {_documento(56, "#0B2236", "#7DB3FF")}
    <div>
      <p class="oc-suma">Suma de los contratos menores: <b>{textos.euros(suma)}</b></p>
      <p class="oc-max">Máximo de un contrato menor: {textos.euros(detalle["umbral"])}</p>
      <p class="oc-veces">{f"{veces:.1f}".replace(".", ",").removesuffix(",0")} veces el máximo</p>
    </div>
  </div>
  <p class="oc-titulo-menores">Contratos menores ({len(ventana)}) · pasa el ratón por cada uno
    para ver su precio</p>
  <div class="oc-iconos">{"".join(iconos)}</div>
</div>"""


# --------------------------------------------------------------------------- componente
CSS = """
.oc-leyenda { display: flex; flex-wrap: wrap; gap: 8px 24px; align-items: center;
  font-family: Outfit, sans-serif; font-size: .9rem; color: #B9C6D8; margin: 2px 0 6px; }
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
