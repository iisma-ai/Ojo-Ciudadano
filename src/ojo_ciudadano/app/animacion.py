"""Animaciones del asistente (D-037): la consulta mientras se ejecuta y el texto al escribirse.

Solo CSS, sin JavaScript: el navegador las mueve mientras Python ejecuta la consulta. Con
«reducir movimiento» activado en el sistema se quedan quietas (docs/11-accesibilidad.md).
Colores de docs/marca.md (variables --oc-* de static/estilo.css).
"""

import html
import time
from collections.abc import Iterator

from ojo_ciudadano.asistente import agente
from ojo_ciudadano.asistente.plano import DESCRIPCION, Plano

CSS = """
<style>
.oc-anim { border: 1px solid var(--oc-cristal-borde, #1e3a52); border-radius: 14px;
  padding: 14px 16px; margin: 4px 0 8px; background: rgba(11, 34, 54, 0.55);
  color: var(--oc-texto, #e7ecf3); font-size: 0.9rem; overflow: hidden; }
.oc-anim-titulo { font-weight: 600; margin-bottom: 10px; display: flex; gap: 8px;
  align-items: center; }
.oc-anim-titulo::before { content: ""; width: 9px; height: 9px; border-radius: 50%;
  background: var(--oc-cian, #38bdf8); animation: oc-latido 1.1s ease-in-out infinite; }
.oc-tablas { display: flex; flex-wrap: wrap; align-items: center; gap: 6px 0; }
.oc-tabla { min-width: 130px; max-width: 190px; border: 1px solid rgba(56, 189, 248, 0.45);
  border-radius: 10px; padding: 8px 10px; background: rgba(4, 22, 39, 0.7); opacity: 0;
  animation: oc-entra 0.45s ease-out forwards; animation-delay: calc(var(--i) * 0.35s); }
.oc-tabla-nombre { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.8rem;
  color: var(--oc-cian, #38bdf8); word-break: break-all; }
.oc-tabla-desc { font-size: 0.75rem; color: var(--oc-texto-suave, #9fb6cc); margin-bottom: 6px; }
.oc-filas span { display: block; height: 5px; margin: 4px 0; border-radius: 3px;
  background: linear-gradient(90deg, rgba(159, 182, 204, 0.15) 0%, rgba(56, 189, 248, 0.85) 50%,
  rgba(159, 182, 204, 0.15) 100%); background-size: 200% 100%;
  animation: oc-lee 1.4s linear infinite; }
.oc-filas span:nth-child(2) { animation-delay: 0.2s; width: 80%; }
.oc-filas span:nth-child(3) { animation-delay: 0.4s; width: 60%; }
.oc-union { display: flex; flex-direction: column; align-items: center; min-width: 70px;
  opacity: 0; animation: oc-entra 0.45s ease-out forwards;
  animation-delay: calc(var(--i) * 0.35s); }
.oc-union-clave { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.7rem;
  color: var(--oc-ambar, #f2b544); max-width: 110px; text-align: center; word-break: break-all; }
.oc-union-linea { width: 64px; height: 3px; margin-top: 3px;
  background: repeating-linear-gradient(90deg, var(--oc-ambar, #f2b544) 0 8px,
  transparent 8px 14px); background-size: 28px 3px; animation: oc-fluye 0.8s linear infinite; }
.oc-pasos { margin: 12px 0 0; padding-left: 20px; color: var(--oc-texto-suave, #9fb6cc);
  font-size: 0.8rem; }
.oc-pasos li { opacity: 0.35; animation: oc-paso 0.5s ease-out forwards;
  animation-delay: calc(0.6s + var(--i) * 0.45s); }
.oc-doc { display: flex; gap: 14px; align-items: center; }
.oc-hojas { position: relative; width: 56px; height: 70px; flex: none; }
.oc-hoja { position: absolute; inset: 0; border: 1px solid rgba(56, 189, 248, 0.5);
  border-radius: 6px; background: rgba(4, 22, 39, 0.85); }
.oc-hoja:nth-child(1) { transform: translate(8px, -6px); opacity: 0.4; }
.oc-hoja:nth-child(2) { transform: translate(4px, -3px); opacity: 0.7; }
.oc-hoja:nth-child(3)::after { content: ""; position: absolute; left: 6px; right: 6px;
  height: 2px; background: var(--oc-ambar, #f2b544); box-shadow: 0 0 8px var(--oc-ambar, #f2b544);
  animation: oc-escanea 1.3s ease-in-out infinite alternate; }
.oc-puntos span { display: inline-block; width: 7px; height: 7px; margin-right: 5px;
  border-radius: 50%; background: var(--oc-cian, #38bdf8); animation: oc-salta 1s infinite; }
.oc-puntos span:nth-child(2) { animation-delay: 0.15s; }
.oc-puntos span:nth-child(3) { animation-delay: 0.3s; }
@keyframes oc-entra { from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: none; } }
@keyframes oc-lee { from { background-position: 200% 0; } to { background-position: -200% 0; } }
@keyframes oc-fluye { from { background-position: 0 0; } to { background-position: 28px 0; } }
@keyframes oc-paso { to { opacity: 1; color: var(--oc-texto, #e7ecf3); } }
@keyframes oc-escanea { from { top: 8px; } to { top: 58px; } }
@keyframes oc-latido { 50% { transform: scale(0.6); opacity: 0.5; } }
@keyframes oc-salta { 50% { transform: translateY(-5px); opacity: 0.5; } }
@media (prefers-reduced-motion: reduce) {
  .oc-anim *, .oc-anim *::before, .oc-anim *::after, .oc-anim-titulo::before {
    animation: none !important; opacity: 1 !important; }
}
</style>
"""

MAX_TABLAS = 6


def _caja(titulo: str, cuerpo: str, etiqueta: str) -> str:
    return (
        f'{CSS}<div class="oc-anim" role="status" aria-live="polite" '
        f'aria-label="{html.escape(etiqueta)}"><div class="oc-anim-titulo">'
        f"{html.escape(titulo)}</div>{cuerpo}</div>"
    )


def consulta(plano: Plano, titulo: str = "Consultando la base de datos") -> str:
    """Tablas que se leen, uniones entre ellas (con su clave) y los pasos de la consulta."""
    reales = [t for t in plano.tablas if t not in plano.intermedias][:MAX_TABLAS]
    claves = {(a, b): clave for a, b, clave in plano.uniones}
    piezas, i = [], 0
    for posicion, tabla in enumerate(reales):
        if posicion:
            anterior = reales[posicion - 1]
            clave = claves.get((anterior, tabla)) or claves.get((tabla, anterior))
            clave = clave or next((c for a, b, c in plano.uniones if b == tabla), "")
            piezas.append(
                f'<div class="oc-union" style="--i:{i}"><span class="oc-union-clave">'
                f'{html.escape(clave)}</span><span class="oc-union-linea"></span></div>'
            )
            i += 1
        descripcion = DESCRIPCION.get(tabla, "")
        piezas.append(
            f'<div class="oc-tabla" style="--i:{i}"><div class="oc-tabla-nombre">'
            f'{html.escape(tabla)}</div><div class="oc-tabla-desc">{html.escape(descripcion)}'
            '</div><div class="oc-filas"><span></span><span></span><span></span></div></div>'
        )
        i += 1
    pasos = "".join(
        f'<li style="--i:{n}">{html.escape(paso)}</li>' for n, paso in enumerate(plano.pasos)
    )
    cuerpo = f'<div class="oc-tablas">{"".join(piezas)}</div><ol class="oc-pasos">{pasos}</ol>'
    etiqueta = f"{titulo}: " + ", ".join(reales)
    return _caja(titulo, cuerpo, etiqueta)


def documento(titulo: str, detalle: str) -> str:
    """Páginas de un PDF que se recorren (pliegos, resoluciones, catálogo, títulos)."""
    cuerpo = (
        '<div class="oc-doc"><div class="oc-hojas"><div class="oc-hoja"></div>'
        '<div class="oc-hoja"></div><div class="oc-hoja"></div></div>'
        f"<div>{html.escape(detalle)}</div></div>"
    )
    return _caja(titulo, cuerpo, f"{titulo}. {detalle}")


def pensando(detalle: str = "Eligiendo qué datos consultar para responder.") -> str:
    cuerpo = (
        '<div class="oc-puntos"><span></span><span></span><span></span></div>'
        f'<div class="oc-tabla-desc" style="margin-top:8px">{html.escape(detalle)}</div>'
    )
    return _caja("Pensando la respuesta", cuerpo, "Pensando la respuesta")


def de_llamada(con, llamada) -> str:
    """La animación que corresponde a cada herramienta del agente."""
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


SEGUNDOS_ESCRITURA = 2.5  # lo que tarda como mucho en escribirse una respuesta


def escribir(texto: str) -> Iterator[str]:
    """El texto palabra a palabra para `st.write_stream`: parece que se escribe. Las
    respuestas largas van más rápido, para no hacer esperar."""
    palabras = texto.split(" ")
    pausa = min(0.035, SEGUNDOS_ESCRITURA / max(len(palabras), 1))
    for n, palabra in enumerate(palabras):
        yield palabra if n == 0 else " " + palabra
        time.sleep(pausa)
