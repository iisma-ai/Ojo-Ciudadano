"""El ojo de cristal de la presentación (presentacion/ojo3d.js), en SVG para la entrada de la web
(D-043).

La presentación lo pinta en 3D: una bola de vidrio con un iris de luz dentro (fibras, anillos y
una escala de lente) y una pupila de cristal oscuro. Aquí se dibujan dos capas planas que se
superponen: el iris, que gira despacio, y el cristal (brillos y borde), que queda quieto. Van
como imagen (data URI) porque `st.html` limpia los SVG en línea.
"""

import base64
import math
import random

C = 100  # centro del dibujo (viewBox de 200 x 200)


def _data_uri(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def svg_iris() -> str:
    """Halo azul, fibras de luz, anillos, escala de lente y pupila oscura."""
    azar = random.Random(7)  # siempre el mismo dibujo
    fibras = []
    for i in range(240):
        a = i / 240 * 2 * math.pi + azar.random() * 0.01
        r0, r1 = 33 + azar.random() * 6, 58 + azar.random() * 34
        color = f"rgb({120 + azar.randint(0, 80)},{180 + azar.randint(0, 60)},255)"
        fibras.append(
            f'<line x1="{C + math.cos(a) * r0:.1f}" y1="{C + math.sin(a) * r0:.1f}" '
            f'x2="{C + math.cos(a) * r1:.1f}" y2="{C + math.sin(a) * r1:.1f}" stroke="{color}" '
            f'stroke-opacity="{0.08 + azar.random() * 0.2:.2f}" '
            f'stroke-width="{0.35 + azar.random() * 0.4:.2f}"/>'
        )
    anillos = "".join(
        f'<circle cx="{C}" cy="{C}" r="{r}" fill="none" stroke="#AAD7FF" '
        f'stroke-opacity="{op}" stroke-width="{w}"/>'
        for r, w, op in ((35, 0.8, 0.9), (40, 0.3, 0.5), (59, 0.25, 0.35), (82, 0.45, 0.45))
    )
    escala = []
    for i in range(120):
        a = i / 120 * 2 * math.pi
        largo = 4.3 if i % 10 == 0 else 1.8
        escala.append(
            f'<line x1="{C + math.cos(a) * 85:.1f}" y1="{C + math.sin(a) * 85:.1f}" '
            f'x2="{C + math.cos(a) * (85 + largo):.1f}" y2="{C + math.sin(a) * (85 + largo):.1f}" '
            f'stroke="#BEE1FF" stroke-opacity="{0.6 if i % 10 == 0 else 0.3}" '
            'stroke-width="0.35"/>'
        )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">'
        "<defs>"
        '<radialGradient id="h"><stop offset=".3" stop-color="#5A96FF" stop-opacity=".6"/>'
        '<stop offset=".6" stop-color="#2864E6" stop-opacity=".35"/>'
        '<stop offset=".85" stop-color="#143CAA" stop-opacity=".12"/>'
        '<stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="p" cx=".42" cy=".4"><stop offset="0" stop-color="#0A2444"/>'
        '<stop offset=".7" stop-color="#030B18"/><stop offset="1" stop-color="#01050C"/>'
        "</radialGradient></defs>"
        f'<circle cx="{C}" cy="{C}" r="96" fill="url(#h)"/>'
        + "".join(fibras)
        + anillos
        + "".join(escala)
        + f'<circle cx="{C}" cy="{C}" r="31" fill="url(#p)" stroke="#AAD7FF" '
        'stroke-opacity=".55" stroke-width=".8"/>'
        "</svg>"
    )


def svg_cristal() -> str:
    """La bola de vidrio por encima: borde luminoso, brillo arriba a la izquierda, reflejo de
    la superficie abajo y el destello de la pupila."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">'
        "<defs>"
        '<radialGradient id="b"><stop offset=".72" stop-color="#C8F0FF" stop-opacity="0"/>'
        '<stop offset=".93" stop-color="#C8F0FF" stop-opacity=".16"/>'
        '<stop offset="1" stop-color="#E6F8FF" stop-opacity=".55"/></radialGradient>'
        '<radialGradient id="s" cx=".5" cy=".5"><stop offset="0" stop-color="#fff" '
        'stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>'
        "</radialGradient>"
        '<linearGradient id="r" x1="0" y1="0" x2="0" y2="1"><stop offset="0" '
        'stop-color="#7DD3FC" stop-opacity="0"/><stop offset="1" stop-color="#7DD3FC" '
        'stop-opacity=".35"/></linearGradient></defs>'
        '<circle cx="100" cy="100" r="98" fill="url(#b)"/>'
        '<ellipse cx="68" cy="52" rx="34" ry="20" transform="rotate(-28 68 52)" '
        'fill="url(#s)" opacity=".7"/>'
        '<path d="M38 132 Q100 186 162 132 Q100 170 38 132Z" fill="url(#r)"/>'
        '<circle cx="91" cy="90" r="6" fill="#fff" fill-opacity=".55"/>'
        '<circle cx="100" cy="100" r="98" fill="none" stroke="#DFF6FF" stroke-opacity=".45" '
        'stroke-width="1.2"/>'
        "</svg>"
    )


def imagenes() -> dict[str, str]:
    """Las dos capas como data URI, para la plantilla `static/intro.html`."""
    return {"{iris}": _data_uri(svg_iris()), "{cristal}": _data_uri(svg_cristal())}
