"""Animaciones del asistente (D-037): el proceso de la consulta y el texto al escribirse.

El proceso de una consulta se queda en la respuesta: las tablas que se leen, cómo se unen (por
qué columna), los pasos (filtrar, agrupar, ordenar) y, al final, la tarjeta del resultado con
sus filas. La primera vez se anima una sola vez; en el historial se dibuja quieto, para que la
página no tenga animaciones repetidas. Solo CSS, sin JavaScript; con «reducir movimiento» en el
sistema todo está quieto (docs/11-accesibilidad.md). El CSS se carga una vez por página
(`CSS`). Colores de docs/marca.md (variables --oc-* de static/estilo.css).
"""

import html
import time
from collections.abc import Iterator

from ojo_ciudadano.asistente import agente
from ojo_ciudadano.asistente.plano import DESCRIPCION, Plano

PASO = 0.22  # segundos entre una pieza y la siguiente
MAX_TABLAS = 6

CSS = """
<style>
.oc-anim { border: 1px solid rgba(170, 225, 255, 0.16); border-radius: 14px;
  padding: 14px 16px; margin: 4px 0 10px; background: rgba(8, 34, 54, 0.72);
  color: #e7ecf3; font-size: 0.9rem; overflow: hidden; contain: content; }
.oc-anim-titulo { font-weight: 600; margin-bottom: 10px; display: flex; gap: 8px;
  align-items: center; }
.oc-anim-titulo::before { content: ""; width: 9px; height: 9px; border-radius: 50%;
  background: #38bdf8; }
.oc-vivo .oc-anim-titulo::before { animation: oc-latido 1.1s ease-in-out infinite; }
.oc-tablas { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 0; }
.oc-tabla { min-width: 128px; max-width: 190px; border: 1px solid rgba(56, 189, 248, 0.45);
  border-radius: 10px; padding: 8px 10px; background: rgba(4, 22, 39, 0.8); }
.oc-tabla-nombre { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.8rem;
  color: #38bdf8; word-break: break-all; }
.oc-tabla-desc { font-size: 0.75rem; color: #9fb6cc; }
.oc-filas { margin-top: 6px; }
.oc-filas span { display: block; height: 5px; margin: 4px 0; border-radius: 3px;
  background: rgba(159, 182, 204, 0.22); }
.oc-filas span:nth-child(2) { width: 80%; }
.oc-filas span:nth-child(3) { width: 60%; }
.oc-union { display: flex; flex-direction: column; align-items: center; min-width: 74px; }
.oc-union-clave { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.7rem;
  color: #f2b544; max-width: 110px; text-align: center; word-break: break-all; }
.oc-union-linea { width: 64px; height: 3px; margin-top: 3px; border-radius: 2px;
  background: #f2b544; transform-origin: left center; }
.oc-resultado { border: 1px solid rgba(242, 181, 68, 0.7); border-radius: 10px;
  padding: 8px 12px; background: rgba(242, 181, 68, 0.1); min-width: 120px; }
.oc-resultado b { color: #f2b544; font-size: 1.05rem; }
.oc-pasos { margin: 12px 0 0; padding-left: 20px; color: #9fb6cc; font-size: 0.8rem; }
.oc-pasos li.oc-hecho { color: #e7ecf3; }
/* Animación de una sola vez (solo la primera vez que se ve la respuesta). */
.oc-anima .oc-pieza { opacity: 0; animation: oc-entra 0.35s ease-out forwards;
  animation-delay: calc(var(--t) * 1s); }
.oc-anima .oc-union-linea { transform: scaleX(0); animation: oc-traza 0.35s ease-out forwards;
  animation-delay: calc(var(--t) * 1s); }
.oc-anima .oc-filas span { background: linear-gradient(90deg, rgba(159, 182, 204, 0.15) 0%,
  rgba(56, 189, 248, 0.85) 50%, rgba(159, 182, 204, 0.15) 100%); background-size: 200% 100%;
  animation: oc-lee 0.9s linear 2 forwards; animation-delay: calc(var(--t) * 1s); }
.oc-anima .oc-pasos li { opacity: 0.3; animation: oc-paso 0.3s ease-out forwards;
  animation-delay: calc(var(--t) * 1s); }
.oc-doc { display: flex; gap: 14px; align-items: center; }
.oc-hojas { position: relative; width: 56px; height: 70px; flex: none; }
.oc-hoja { position: absolute; inset: 0; border: 1px solid rgba(56, 189, 248, 0.5);
  border-radius: 6px; background: rgba(4, 22, 39, 0.85); }
.oc-hoja:nth-child(1) { transform: translate(8px, -6px); opacity: 0.4; }
.oc-hoja:nth-child(2) { transform: translate(4px, -3px); opacity: 0.7; }
.oc-hoja:nth-child(3)::after { content: ""; position: absolute; left: 6px; right: 6px; top: 8px;
  height: 2px; background: #f2b544; }
.oc-vivo .oc-hoja:nth-child(3)::after { animation: oc-escanea 1.3s ease-in-out infinite alternate; }
.oc-puntos span { display: inline-block; width: 7px; height: 7px; margin-right: 5px;
  border-radius: 50%; background: #38bdf8; animation: oc-salta 1s infinite; }
.oc-puntos span:nth-child(2) { animation-delay: 0.15s; }
.oc-puntos span:nth-child(3) { animation-delay: 0.3s; }
@keyframes oc-entra { from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: none; } }
@keyframes oc-traza { to { transform: scaleX(1); } }
@keyframes oc-lee { from { background-position: 200% 0; } to { background-position: -200% 0; } }
@keyframes oc-paso { to { opacity: 1; color: #e7ecf3; } }
@keyframes oc-escanea { from { transform: translateY(0); } to { transform: translateY(50px); } }
@keyframes oc-latido { 50% { transform: scale(0.6); opacity: 0.5; } }
@keyframes oc-salta { 50% { transform: translateY(-5px); opacity: 0.5; } }
@media (prefers-reduced-motion: reduce) {
  .oc-anim *, .oc-anim *::before, .oc-anim *::after {
    animation: none !important; opacity: 1 !important; transform: none !important; }
}
</style>
"""


def _caja(titulo: str, cuerpo: str, etiqueta: str, clase: str = "") -> str:
    return (
        f'<div class="oc-anim {clase}" role="status" aria-live="polite" '
        f'aria-label="{html.escape(etiqueta)}"><div class="oc-anim-titulo">'
        f"{html.escape(titulo)}</div>{cuerpo}</div>"
    )


def _piezas(plano: Plano) -> list[tuple[str, str, str]]:
    """(tipo, texto, descripción) en orden: tabla, unión, tabla… Solo tablas reales."""
    reales = [t for t in plano.tablas if t not in plano.intermedias][:MAX_TABLAS]
    claves = {(a, b): clave for a, b, clave in plano.uniones}
    piezas = []
    for posicion, tabla in enumerate(reales):
        if posicion:
            anterior = reales[posicion - 1]
            clave = claves.get((anterior, tabla)) or claves.get((tabla, anterior))
            clave = clave or next((c for _, b, c in plano.uniones if b == tabla), "y")
            piezas.append(("union", clave, ""))
        piezas.append(("tabla", tabla, DESCRIPCION.get(tabla, "")))
    return piezas


def duracion(plano: Plano) -> float:
    """Lo que tarda en dibujarse el proceso entero (para esperar antes de escribir)."""
    return PASO * (len(_piezas(plano)) + len(plano.pasos) + 1) + 0.35


def consulta(plano: Plano, filas: int | None = None, animar: bool = True) -> str:
    """El proceso de la consulta: tablas, uniones con su clave, pasos y el resultado."""
    piezas, t = [], 0.0
    for tipo, texto, descripcion in _piezas(plano):
        if tipo == "union":
            piezas.append(
                f'<div class="oc-union oc-pieza" style="--t:{t:.2f}"><span class="oc-union-clave">'
                f'{html.escape(texto)}</span><span class="oc-union-linea" style="--t:{t:.2f}">'
                "</span></div>"
            )
        else:
            piezas.append(
                f'<div class="oc-tabla oc-pieza" style="--t:{t:.2f}"><div class="oc-tabla-nombre">'
                f'{html.escape(texto)}</div><div class="oc-tabla-desc">{html.escape(descripcion)}'
                f'</div><div class="oc-filas" style="--t:{t:.2f}"><span style="--t:{t:.2f}">'
                f'</span><span style="--t:{t:.2f}"></span><span style="--t:{t:.2f}"></span></div>'
                "</div>"
            )
        t += PASO
    pasos = []
    for paso in plano.pasos:
        pasos.append(f'<li class="oc-hecho" style="--t:{t:.2f}">{html.escape(paso)}</li>')
        t += PASO
    if filas is not None:
        texto = "1 fila" if filas == 1 else f"{filas} filas"
        piezas.append(
            f'<div class="oc-union oc-pieza" style="--t:{t:.2f}"><span class="oc-union-clave">'
            f'resultado</span><span class="oc-union-linea" style="--t:{t:.2f}"></span></div>'
            f'<div class="oc-resultado oc-pieza" style="--t:{t + PASO:.2f}"><b>{texto}</b>'
            '<div class="oc-tabla-desc">listas para ver abajo</div></div>'
        )
    cuerpo = (
        f'<div class="oc-tablas">{"".join(piezas)}</div><ol class="oc-pasos">{"".join(pasos)}</ol>'
    )
    reales = [p[1] for p in _piezas(plano) if p[0] == "tabla"]
    etiqueta = "Cómo se ha consultado la base: " + ", ".join(reales)
    titulo = (
        "Cómo se ha consultado la base de datos"
        if filas is not None
        else "Consultando la base de datos"
    )
    return _caja(titulo, cuerpo, etiqueta, "oc-anima" if animar else "")


def documento(titulo: str, detalle: str) -> str:
    """Páginas de un PDF que se recorren (pliegos, resoluciones, catálogo, títulos)."""
    cuerpo = (
        '<div class="oc-doc"><div class="oc-hojas"><div class="oc-hoja"></div>'
        '<div class="oc-hoja"></div><div class="oc-hoja"></div></div>'
        f"<div>{html.escape(detalle)}</div></div>"
    )
    return _caja(titulo, cuerpo, f"{titulo}. {detalle}", "oc-vivo")


def pensando(detalle: str = "Eligiendo qué datos consultar para responder.") -> str:
    cuerpo = (
        '<div class="oc-puntos"><span></span><span></span><span></span></div>'
        f'<div class="oc-tabla-desc" style="margin-top:8px">{html.escape(detalle)}</div>'
    )
    return _caja("Pensando la respuesta", cuerpo, "Pensando la respuesta", "oc-vivo")


def de_llamada(con, llamada) -> str:
    """La animación que corresponde a cada herramienta del agente, mientras se usa."""
    from ojo_ciudadano.asistente.plano import plano_consulta

    if isinstance(llamada, agente.LlamadaSQL):
        return consulta(plano_consulta(con, llamada.sql))
    if isinstance(llamada, agente.LlamadaBuscarDocumento):
        return documento(
            "Leyendo los documentos oficiales",
            f"Buscando «{llamada.consulta}» en los documentos de {llamada.identificador}.",
        )
    if isinstance(llamada, agente.LlamadaBuscarResoluciones):
        return documento(
            "Leyendo las resoluciones del Tribunal",
            f"Buscando «{llamada.consulta}» en las resoluciones del Tribunal Administrativo de "
            "Contratación Pública de la Comunidad de Madrid.",
        )
    if isinstance(llamada, agente.LlamadaBuscarTexto):
        return documento(
            "Buscando en los títulos", f"Buscando «{llamada.consulta}» en los títulos."
        )
    if isinstance(llamada, agente.LlamadaBuscarConjunto):
        return documento(
            "Buscando en el catálogo de datos abiertos",
            f"Buscando conjuntos sobre «{llamada.consulta}».",
        )
    return documento(
        "Consultando un conjunto del catálogo de datos abiertos",
        f"Leyendo el conjunto «{getattr(llamada, 'conjunto', '')}».",
    )


SEGUNDOS_ESCRITURA = 1.5  # lo que tarda como mucho en escribirse una respuesta


def escribir(texto: str) -> Iterator[str]:
    """El texto por trozos para `st.write_stream`: parece que se escribe. Va por grupos de
    palabras para no mandar cientos de mensajes al navegador."""
    palabras = texto.split(" ")
    trozos = max(1, min(len(palabras), 40))  # como mucho 40 actualizaciones
    tamano = -(-len(palabras) // trozos)
    pausa = SEGUNDOS_ESCRITURA / trozos
    for inicio in range(0, len(palabras), tamano):
        trozo = " ".join(palabras[inicio : inicio + tamano])
        yield trozo if inicio == 0 else " " + trozo
        time.sleep(pausa)
