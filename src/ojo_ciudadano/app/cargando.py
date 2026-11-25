"""Indicador de carga con nuestro ojo: el iris gira mientras se prepara algo (un gráfico).

Se pinta con `st.html` en un `st.empty()` y se sustituye por el resultado cuando está listo.
Solo anima `transform` y `opacity` (en el compositor) y respeta `prefers-reduced-motion`.
"""

import html as _html

from ojo_ciudadano.app import ojo_cristal

_OJO = ojo_cristal.imagenes()

ESTILO = """
<style>
.oc-cargando { display:flex; align-items:center; gap:16px; padding:22px 6px;
  font-family:Inter, sans-serif; color:#B9C6D8; font-size:1rem;
  animation: oc-cargando-entra .3s ease-out both; }
.oc-cargando .ojo { position:relative; width:54px; height:54px; flex:0 0 auto; }
.oc-cargando .ojo::before { content:""; position:absolute; inset:-30%; border-radius:50%;
  background:radial-gradient(circle, rgba(56,189,248,.32), transparent 65%);
  animation: oc-cargando-late 1.6s ease-in-out infinite; }
.oc-cargando .ojo img { position:absolute; inset:0; width:100%; height:100%; }
.oc-cargando .ojo .iris { animation: oc-cargando-gira 1.1s linear infinite; }
.oc-cargando .puntos i { display:inline-block; font-style:normal;
  animation: oc-cargando-punto 1.2s ease-in-out infinite; }
.oc-cargando .puntos i:nth-child(2) { animation-delay:.2s; }
.oc-cargando .puntos i:nth-child(3) { animation-delay:.4s; }
@keyframes oc-cargando-gira { to { transform: rotate(360deg); } }
@keyframes oc-cargando-late { 0%, 100% { opacity:.45; transform:scale(.92); }
  50% { opacity:1; transform:scale(1.05); } }
@keyframes oc-cargando-punto { 0%, 100% { opacity:.2; } 50% { opacity:1; } }
@keyframes oc-cargando-entra { from { opacity:0; } to { opacity:1; } }
@media (prefers-reduced-motion: reduce) {
  .oc-cargando .ojo .iris, .oc-cargando .ojo::before, .oc-cargando .puntos i { animation:none; }
}
</style>
"""


def html(texto: str) -> str:
    """El ojo girando con un texto al lado («Preparando el gráfico…»)."""
    return (
        ESTILO
        + '<div class="oc-cargando" role="status" aria-live="polite">'
        + f'<div class="ojo"><img class="iris" src="{_OJO["{iris}"]}" alt="">'
        + f'<img src="{_OJO["{cristal}"]}" alt=""></div>'
        + f'<span>{_html.escape(texto)}<span class="puntos"><i>.</i><i>.</i><i>.</i></span>'
        + "</span></div>"
    )
