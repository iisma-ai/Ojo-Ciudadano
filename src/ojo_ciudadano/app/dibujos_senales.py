"""Dibujos de las señales de un contrato, con el estilo de la web (D-060).

Mismo concepto que los gráficos de antes (estudios E-01 a E-06, D-042), con el lenguaje de la
presentación y de la web: tubos y burbujas de cristal llenos de líquido. «Este contrato» o «esta
empresa» va en azul vivo; el contexto, en gris azulado. Cada dibujo es un SVG propio dentro de
un poco de HTML, que se pinta con `billetes.pintar`, y lleva una descripción (`aria-label`) y la
cifra de cada elemento al pasar el ratón (`<title>`).

Las funciones reciben los diccionarios de `app.datos` y devuelven el HTML como texto. Los textos
que vienen de la base (nombres de empresas) se escapan aquí.
"""

import hashlib
import html

from ojo_ciudadano.app.textos import euros, numero, porcentaje

# Líquidos: (claro arriba, color, oscuro abajo)
LIQUIDO = {
    "azul": ("#9CC7FF", "#3D8BFD", "#1F5FBF"),  # este contrato, esta empresa
    "gris": ("#9FB0C8", "#5B6B86", "#3A4862"),  # el contexto
    "claro": ("#E1EEFF", "#9CC7FF", "#6FA4E8"),  # tramo intermedio (modificaciones hasta el 20 %)
}
TEXTO = "#E7ECF3"
SUAVE = "#9FB6CC"
AZUL_TEXTO = "#7DB3FF"
BORDE = "rgba(220, 240, 255, 0.5)"
ZONA = "rgba(125, 179, 255, 0.16)"  # tramos de la regla donde salta una señal

CSS = """
<style>
.oc-dib { font-family: Inter, sans-serif; color: #E7ECF3; }
.oc-dib svg { display: block; width: 100%; height: auto; max-width: 560px; overflow: visible; }
.oc-dib text { font-family: Inter, sans-serif; }
.oc-liq { transform-box: fill-box; animation: oc-sube 1.1s cubic-bezier(.2,.8,.2,1) both; }
.oc-liq.v { transform-origin: bottom; }
.oc-liq.h { transform-origin: left; animation-name: oc-crece; }
.oc-dib g[tabindex] { outline: none; }
.oc-dib g[tabindex]:hover .oc-vidrio, .oc-dib g[tabindex]:focus-visible .oc-vidrio {
  stroke: #fff; stroke-opacity: .85; }
@keyframes oc-sube { from { transform: scaleY(0); } to { transform: scaleY(1); } }
@keyframes oc-crece { from { transform: scaleX(0); } to { transform: scaleX(1); } }
@media (prefers-reduced-motion: reduce) { .oc-liq { animation: none; } }
.oc-dib-pie { display: flex; flex-wrap: wrap; gap: 4px 18px; margin-top: 8px;
  font-size: .85rem; color: #9FB6CC; }
.oc-dib-pie i { display: inline-block; width: 12px; height: 12px; border-radius: 50%;
  margin-right: 6px; vertical-align: -1px; border: 1px solid rgba(220,240,255,.5); }
</style>
"""


def _uid(*partes) -> str:
    """Sufijo para los id de un dibujo (gradientes y recortes), distinto en cada dibujo."""
    return hashlib.md5(repr(partes).encode()).hexdigest()[:8]


def _defs(uid: str) -> str:
    """Degradados de los líquidos (vertical y horizontal) y de la burbuja."""
    piezas = []
    for nombre, (claro, medio, oscuro) in LIQUIDO.items():
        for eje, (x2, y2) in (("v", (0, 1)), ("h", (0, 1))):
            piezas.append(
                f'<linearGradient id="{nombre}{eje}{uid}" x1="0" y1="0" x2="{x2}" y2="{y2}">'
                f'<stop offset="0" stop-color="{claro}"/><stop offset=".35" stop-color="{medio}"/>'
                f'<stop offset="1" stop-color="{oscuro}"/></linearGradient>'
            )
    piezas.append(
        f'<radialGradient id="burbuja{uid}" cx=".38" cy=".32" r=".75">'
        '<stop offset="0" stop-color="#EAF4FF"/><stop offset=".35" stop-color="#7DB3FF"/>'
        '<stop offset="1" stop-color="#1F5FBF"/></radialGradient>'
        f'<radialGradient id="burbujagris{uid}" cx=".38" cy=".32" r=".75">'
        '<stop offset="0" stop-color="#DDE5F0"/><stop offset=".4" stop-color="#93A1B8"/>'
        '<stop offset="1" stop-color="#4A5872"/></radialGradient>'
        f'<radialGradient id="halo{uid}"><stop offset="0" stop-color="#3D8BFD" '
        'stop-opacity=".45"/><stop offset="1" stop-color="#3D8BFD" stop-opacity="0"/>'
        "</radialGradient>"
    )
    return "<defs>" + "".join(piezas) + "</defs>"


def _svg(ancho: int, alto: int, uid: str, descripcion: str, contenido: str) -> str:
    return (
        f'<svg viewBox="0 0 {ancho} {alto}" role="img" aria-label="{html.escape(descripcion)}" '
        f'xmlns="http://www.w3.org/2000/svg">{_defs(uid)}{contenido}</svg>'
    )


def _texto(x, y, texto, tam=12, color=SUAVE, ancla="middle", peso=400) -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="{tam}" fill="{color}" text-anchor="{ancla}" '
        f'font-weight="{peso}">{html.escape(texto)}</text>'
    )


def _tubo(x, y, w, h, tramos, uid, clave, titulo, horizontal=False) -> str:
    """Un tubo de cristal de w × h con su líquido. `tramos`: [(largo en px, líquido)] desde el
    fondo (abajo, o la izquierda si es horizontal). Al pasar el ratón, `titulo`."""
    rx = min(w, h) / 2 if horizontal else min(w / 2, 12)
    recorte = f"r{clave}{uid}"
    eje = "h" if horizontal else "v"
    liquido = []
    hecho = 0.0
    for largo, nombre in tramos:
        if largo <= 0:
            continue
        relleno = f"url(#{nombre}{eje}{uid})"
        if horizontal:
            liquido.append(
                f'<rect x="{x + hecho:.1f}" y="{y}" width="{largo:.1f}" height="{h}" '
                f'fill="{relleno}"/>'
            )
        else:
            liquido.append(
                f'<rect x="{x}" y="{y + h - hecho - largo:.1f}" width="{w}" height="{largo:.1f}" '
                f'fill="{relleno}"/>'
            )
        hecho += largo
    # superficie del líquido: una línea de luz
    if hecho > 0:
        if horizontal:
            liquido.append(
                f'<rect x="{x + hecho - 2:.1f}" y="{y}" width="2" height="{h}" fill="#fff" '
                'fill-opacity=".45"/>'
            )
        else:
            liquido.append(
                f'<rect x="{x}" y="{y + h - hecho:.1f}" width="{w}" height="2" fill="#fff" '
                'fill-opacity=".45"/>'
            )
    if horizontal:
        reflejo = (
            f'<rect x="{x + rx:.1f}" y="{y + h * 0.18:.1f}" width="{max(w - 2 * rx, 0):.1f}" '
            f'height="{h * 0.16:.1f}" rx="{h * 0.08:.1f}" fill="#fff" fill-opacity=".22"/>'
        )
    else:
        reflejo = (
            f'<rect x="{x + w * 0.18:.1f}" y="{y + 6}" width="{w * 0.14:.1f}" '
            f'height="{max(h - 12, 0):.1f}" rx="{w * 0.07:.1f}" fill="#fff" fill-opacity=".2"/>'
        )
    return (
        f'<g tabindex="0"><title>{html.escape(titulo)}</title>'
        f'<clipPath id="{recorte}"><rect x="{x}" y="{y}" width="{w}" height="{h}" '
        f'rx="{rx:.1f}"/></clipPath>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx:.1f}" fill="#cfeeff" '
        'fill-opacity=".05"/>'
        f'<g clip-path="url(#{recorte})"><g class="oc-liq {eje}">{"".join(liquido)}</g>'
        f"{reflejo}</g>"
        f'<rect class="oc-vidrio" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx:.1f}" '
        f'fill="none" stroke="{BORDE}" stroke-width="1.3"/></g>'
    )


def _pie(*partes: tuple[str, str]) -> str:
    """Leyenda bajo el dibujo: (color, texto)."""
    return (
        '<div class="oc-dib-pie">'
        + "".join(f'<span><i style="background:{c}"></i>{html.escape(t)}</span>' for c, t in partes)
        + "</div>"
    )


def _envolver(svg: str, pie: str = "") -> str:
    return f'{CSS}<div class="oc-dib">{svg}{pie}</div>'


# --------------------------------------------------------------------------- R-01
def ofertas(detalle: dict) -> str:
    """E-01: cuántos contratos parecidos recibieron 1, 2, 3… ofertas, como tubos de cristal;
    el de las ofertas de este contrato, en azul y con la etiqueta «Este contrato»."""
    filas = detalle["distribucion"]
    uid = _uid("r01", filas, detalle["ofertas"])
    este = min(detalle["ofertas"], 10)
    maximo = max((c for _, c in filas), default=0) or 1
    ancho, alto_tubo, arriba = 420, 130, 46
    paso = ancho / max(len(filas), 1)
    w = min(30.0, paso * 0.56)
    piezas = []
    for k, (n, cuantos) in enumerate(filas):
        x = k * paso + (paso - w) / 2
        nivel = max(alto_tubo * cuantos / maximo, 3 if cuantos else 0)
        es_este = n == este
        nombre = "10 o más" if n == 10 else str(n)
        oferta = "oferta" if n == 1 else "ofertas"
        piezas.append(
            _tubo(
                x,
                arriba,
                w,
                alto_tubo,
                [(nivel, "azul" if es_este else "gris")],
                uid,
                k,
                f"{nombre} {oferta}: {numero(cuantos)} contratos"
                + (" (este contrato)" if es_este else ""),
            )
        )
        centro = x + w / 2
        piezas.append(
            _texto(
                centro,
                arriba + alto_tubo - nivel - 6,
                numero(cuantos),
                11,
                TEXTO if es_este else SUAVE,
            )
        )
        piezas.append(
            _texto(
                centro,
                arriba + alto_tubo + 18,
                "10+" if n == 10 else str(n),
                13,
                AZUL_TEXTO if es_este else SUAVE,
                peso=600 if es_este else 400,
            )
        )
        if es_este:
            piezas.append(
                f'<rect x="{centro - 46:.1f}" y="6" width="92" height="22" rx="11" '
                'fill="rgba(61,139,253,.22)" stroke="rgba(125,179,255,.6)"/>'
                + _texto(centro, 21, "Este contrato", 12, TEXTO, peso=600)
            )
    piezas.append(_texto(ancho / 2, arriba + alto_tubo + 40, "Ofertas recibidas", 12))
    descripcion = (
        f"Contratos parecidos según las ofertas que recibieron. Este contrato recibió "
        f"{detalle['ofertas']}."
    )
    svg = _svg(ancho, arriba + alto_tubo + 48, uid, descripcion, "".join(piezas))
    return _envolver(
        svg,
        _pie((LIQUIDO["azul"][1], "Este contrato"), (LIQUIDO["gris"][1], "Contratos parecidos")),
    )


# --------------------------------------------------------------------------- R-02
def sin_anuncio(detalle: dict) -> str:
    """E-02: del dinero del organismo, cuánto se adjudicó sin anuncio público. Una burbuja de
    cristal llena hasta los euros de cada 100 que fueron sin anuncio."""
    total = detalle["sin_anuncio"] + detalle["con_anuncio"]
    parte = detalle["sin_anuncio"] / total if total else 0
    uid = _uid("r02", total, parte)
    cx, cy, r = 90, 90, 78
    nivel = 2 * r * parte
    de_cada = round(100 * parte)
    burbuja = (
        f'<g tabindex="0"><title>Sin anuncio público: {html.escape(euros(detalle["sin_anuncio"]))} '
        f"({porcentaje(parte)})</title>"
        f'<clipPath id="c{uid}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#cfeeff" fill-opacity=".05"/>'
        f'<g clip-path="url(#c{uid})"><g class="oc-liq v">'
        f'<rect x="{cx - r}" y="{cy + r - nivel:.1f}" width="{2 * r}" height="{nivel:.1f}" '
        f'fill="url(#azulv{uid})"/>'
        f'<rect x="{cx - r}" y="{cy + r - nivel:.1f}" width="{2 * r}" height="2" fill="#fff" '
        'fill-opacity=".5"/></g>'
        f'<ellipse cx="{cx - r * 0.42:.1f}" cy="{cy - r * 0.45:.1f}" rx="{r * 0.2:.1f}" '
        f'ry="{r * 0.32:.1f}" transform="rotate(35 {cx - r * 0.42:.1f} {cy - r * 0.45:.1f})" '
        'fill="#fff" fill-opacity=".22"/></g>'
        f'<circle class="oc-vidrio" cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{BORDE}" '
        'stroke-width="1.5"/></g>'
    )
    cifras = (
        f'<text x="186" y="82" font-size="46" font-weight="200" fill="{TEXTO}">{de_cada} €</text>'
        + _texto(188, 106, "de cada 100 € sin anuncio público", 12, TEXTO, "start")
        + _texto(188, 132, f"{100 - de_cada} € con anuncio público", 12, SUAVE, "start")
    )
    descripcion = f"De cada 100 € del organismo, {de_cada} se adjudicaron sin anuncio público."
    svg = _svg(420, 180, uid, descripcion, burbuja + cifras)
    return _envolver(
        svg,
        _pie((LIQUIDO["azul"][1], "Sin anuncio público"), ("transparent", "Con anuncio público")),
    )


# --------------------------------------------------------------------------- R-04
def reparto(detalle: dict) -> str:
    """E-04 (D-042): de cada 100 € que el organismo adjudica en este tipo de contrato, cuántos
    se lleva cada empresa. Un tubo por empresa (la de este contrato en azul) y una línea en «la
    mitad», donde salta la señal."""
    total = detalle["total"] or 1
    partes = detalle["partes"]
    uid = _uid("r04", [(p["nombre"], p["importe"]) for p in partes])
    ancho, x0, x1, fila, arriba = 420, 160, 382, 34, 26
    largo = x1 - x0
    piezas = []
    for k, p in enumerate(partes):
        y = arriba + k * fila
        de_cada = 100 * p["importe"] / total
        nombre = p["nombre"] if len(p["nombre"]) <= 20 else p["nombre"][:19] + "…"
        color = TEXTO if p["es_este"] else SUAVE
        piezas.append(
            _texto(x0 - 10, y + 15, nombre, 12, color, "end", 600 if p["es_este"] else 400)
        )
        piezas.append(
            _tubo(
                x0,
                y + 3,
                largo,
                16,
                [(max(largo * de_cada / 100, 3), "azul" if p["es_este"] else "gris")],
                uid,
                k,
                f"{p['nombre']}: {euros(p['importe'])} ({round(de_cada)} de cada 100 €)",
                horizontal=True,
            )
        )
        piezas.append(_texto(x1 + 8, y + 15, f"{round(de_cada)} €", 12, color, "start", 600))
    abajo = arriba + len(partes) * fila
    mitad = x0 + largo / 2
    piezas.append(
        f'<line x1="{mitad}" y1="{arriba - 6}" x2="{mitad}" y2="{abajo}" stroke="{TEXTO}" '
        'stroke-opacity=".55" stroke-width="1.5" stroke-dasharray="3 4"/>'
        + _texto(mitad, arriba - 11, "la mitad", 11, TEXTO)
    )
    quien = partes[0]["nombre"] if partes else ""
    descripcion = f"Reparto del dinero del organismo entre empresas; la mayor parte, {quien}."
    return _envolver(_svg(ancho, abajo + 6, uid, descripcion, "".join(piezas)))


# --------------------------------------------------------------------------- R-05
def tramos_subida(adjudicado: float, modificaciones: float) -> tuple[float, float]:
    """(modificaciones hasta el 20 % del precio, lo que pasa del 20 %)."""
    hasta_20 = min(modificaciones, 0.2 * adjudicado)
    return hasta_20, max(modificaciones - 0.2 * adjudicado, 0)


def subida(detalle: dict) -> str:
    """E-05 (D-042): «antes y después». Un vaso con el precio adjudicado y otro con el precio
    tras las modificaciones, que sube en dos tramos (hasta el 20 % y lo que pasa del 20 %), con
    la línea del +20 % y la subida en grande."""
    adjudicado = detalle["adjudicado"] or 0
    modificaciones = detalle["modificaciones"] or 0
    hasta_20, encima_20 = tramos_subida(adjudicado, modificaciones)
    uid = _uid("r05", adjudicado, modificaciones)
    techo = (adjudicado + modificaciones) * 1.12 or 1
    alto, arriba, w = 170.0, 40.0, 70
    escala = alto / techo
    xs = (110, 250)
    piezas = [
        _tubo(
            xs[0],
            arriba,
            w,
            alto,
            [(adjudicado * escala, "gris")],
            uid,
            0,
            f"Precio adjudicado: {euros(adjudicado)}",
        ),
        _tubo(
            xs[1],
            arriba,
            w,
            alto,
            [
                (adjudicado * escala, "gris"),
                (hasta_20 * escala, "claro"),
                (encima_20 * escala, "azul"),
            ],
            uid,
            1,
            f"Con modificaciones: {euros(adjudicado + modificaciones)} (+{euros(modificaciones)})",
        ),
    ]
    y20 = arriba + alto - adjudicado * 1.2 * escala
    piezas.append(
        f'<line x1="{xs[0] - 14}" y1="{y20:.1f}" x2="{xs[1] + w + 14}" y2="{y20:.1f}" '
        f'stroke="{TEXTO}" stroke-opacity=".55" stroke-width="1.5" stroke-dasharray="3 4"/>'
        + _texto(xs[0] - 20, y20 + 4, "+20 %", 11, TEXTO, "end")
    )
    if adjudicado:
        y_cima = arriba + alto - (adjudicado + modificaciones) * escala
        piezas.append(
            f'<text x="{xs[1] + w / 2}" y="{y_cima - 10:.1f}" font-size="22" font-weight="600" '
            f'fill="{TEXTO}" text-anchor="middle">+{porcentaje(modificaciones / adjudicado)}</text>'
        )
    for x, nombre in zip(xs, ("Precio adjudicado", "Con modificaciones"), strict=True):
        piezas.append(_texto(x + w / 2, arriba + alto + 20, nombre, 12))
    piezas.append(_texto(xs[0] + w / 2, arriba + alto + 36, euros(adjudicado), 12, TEXTO))
    piezas.append(
        _texto(xs[1] + w / 2, arriba + alto + 36, euros(adjudicado + modificaciones), 12, TEXTO)
    )
    descripcion = (
        f"El precio pasó de {euros(adjudicado)} a {euros(adjudicado + modificaciones)} con las "
        "modificaciones."
    )
    svg = _svg(420, arriba + alto + 44, uid, descripcion, "".join(piezas))
    return _envolver(
        svg,
        _pie(
            (LIQUIDO["gris"][1], "Precio adjudicado"),
            (LIQUIDO["claro"][1], "Modificaciones hasta el 20 %"),
            (LIQUIDO["azul"][1], "Por encima del 20 %"),
        ),
    )


# --------------------------------------------------------------------------- R-06
def rebaja(detalle: dict, habitual: float | None = None) -> str:
    """E-06 (D-042): una regla de cristal de la rebaja (de «por encima del precio» a «más de la
    mitad») con las dos zonas donde salta la señal, la burbuja de este contrato y, si se conoce,
    una burbuja gris con la rebaja habitual en contratos parecidos. Rebaja en tanto por uno."""
    presupuesto = detalle["presupuesto"] or 0
    adjudicado = detalle["adjudicado"] or 0
    baja = 1 - adjudicado / presupuesto if presupuesto else 0
    minimo = min(-0.1, baja - 0.08)
    maximo = max(0.6, baja + 0.08)
    uid = _uid("r06", baja, habitual)
    x0, x1, y, h = 24.0, 396.0, 70.0, 22.0

    def a_x(v: float) -> float:
        return x0 + (v - minimo) / (maximo - minimo) * (x1 - x0)

    piezas = [
        f'<clipPath id="g{uid}"><rect x="{x0}" y="{y}" width="{x1 - x0}" height="{h}" '
        f'rx="{h / 2}"/></clipPath>'
        f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="{h}" rx="{h / 2}" fill="#cfeeff" '
        'fill-opacity=".05"/>'
        f'<g clip-path="url(#g{uid})">'
        f'<rect x="{x0}" y="{y}" width="{a_x(0.005) - x0:.1f}" height="{h}" fill="{ZONA}"/>'
        f'<rect x="{a_x(0.5):.1f}" y="{y}" width="{x1 - a_x(0.5):.1f}" height="{h}" '
        f'fill="{ZONA}"/>'
        f'<rect x="{x0 + h / 2}" y="{y + 4}" width="{x1 - x0 - h}" height="4" rx="2" fill="#fff" '
        'fill-opacity=".2"/></g>'
        f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="{h}" rx="{h / 2}" fill="none" '
        f'stroke="{BORDE}" stroke-width="1.3"/>',
        _texto((x0 + a_x(0.005)) / 2, y + h + 34, "casi sin rebaja", 11),
        _texto((a_x(0.5) + x1) / 2, y + h + 34, "rebaja muy alta", 11),
    ]
    marca = 0.0
    while marca <= maximo + 1e-9:
        if marca >= minimo:
            piezas.append(_texto(a_x(marca), y + h + 16, porcentaje(marca), 10))
        marca += 0.2
    if habitual is not None:
        xh = a_x(habitual)
        piezas.append(
            f'<g tabindex="0"><title>Rebaja habitual en contratos parecidos: '
            f"{porcentaje(habitual, 1)}</title>"
            f'<circle cx="{xh:.1f}" cy="{y + h / 2}" r="8" fill="url(#burbujagris{uid})" '
            f'stroke="{BORDE}"/></g>'
            + _texto(xh, y - 12, f"Lo habitual: {porcentaje(habitual)}", 11)
        )
    xb = a_x(baja)
    etiqueta = (
        f"Este contrato: {porcentaje(baja, 1)}"
        if baja >= 0
        else f"Este contrato: {porcentaje(-baja)} por encima"
    )
    tercio = (maximo - minimo) / 3
    ancla = "start" if baja < minimo + tercio else ("end" if baja > maximo - tercio else "middle")
    desplaza = {"start": -12, "end": 12, "middle": 0}[ancla]
    piezas.append(
        f'<circle cx="{xb:.1f}" cy="{y + h / 2}" r="26" fill="url(#halo{uid})"/>'
        f'<g tabindex="0"><title>Rebaja de este contrato: {porcentaje(baja, 1)}</title>'
        f'<circle cx="{xb:.1f}" cy="{y + h / 2}" r="13" fill="url(#burbuja{uid})" '
        'stroke="#E7ECF3" stroke-opacity=".8" stroke-width="1.5"/></g>'
        f'<text x="{xb + desplaza:.1f}" y="{y - 34}" font-size="14" font-weight="600" '
        f'fill="{TEXTO}" text-anchor="{ancla}">{html.escape(etiqueta)}</text>'
    )
    return _envolver(_svg(420, y + h + 44, uid, etiqueta, "".join(piezas)))
