"""¿Dibuja el navegador con tarjeta gráfica? (D-044)

La entrada en 3D y el fondo animado van fluidos cuando el navegador usa la tarjeta gráfica
(también la integrada de casi cualquier portátil). Si no puede usarla, porque la aceleración por
hardware está desactivada, el controlador está bloqueado, o se usa por escritorio remoto o en una
máquina virtual, lo dibuja todo con el procesador y va a tirones.

La prueba pide a WebGL un contexto que falle si solo hay dibujo por software
(`failIfMajorPerformanceCaveat`) y mira el nombre del dibujador (SwiftShader, llvmpipe, Microsoft
Basic Render...). El resultado se guarda para la pestaña (`sessionStorage`, clave `oc-gpu`). Sin
tarjeta gráfica, la página lleva la clase `oc-sin-gpu`: la entrada usa el ojo plano en vez del 3D
y el fondo de rayos y burbujas se queda quieto (`static/estilo.css`).
"""

import streamlit as st

# Función de JavaScript compartida con la entrada (intro3d.py).
PRUEBA = """
const OC_SOFTWARE = /swiftshader|llvmpipe|softpipe|software|basic render|microsoft basic/i;

function ocHayGpu() {
  try {
    const guardado = sessionStorage.getItem('oc-gpu');
    if (guardado) return guardado === 'si';
  } catch (e) { /* sin almacenamiento: se prueba cada vez */ }
  let si = false;
  try {
    const lienzo = document.createElement('canvas');
    const opciones = { failIfMajorPerformanceCaveat: true };
    const gl = lienzo.getContext('webgl2', opciones) || lienzo.getContext('webgl', opciones);
    if (gl) {
      const info = gl.getExtension('WEBGL_debug_renderer_info');
      const nombre = info ? String(gl.getParameter(info.UNMASKED_RENDERER_WEBGL)) : '';
      si = !OC_SOFTWARE.test(nombre);
      const perder = gl.getExtension('WEBGL_lose_context');
      if (perder) perder.loseContext();
    }
  } catch (e) {
    si = false;
  }
  try { sessionStorage.setItem('oc-gpu', si ? 'si' : 'no'); } catch (e) { /* nada */ }
  return si;
}

function ocMarcarSinGpu() {
  document.documentElement.classList.add('oc-sin-gpu');
}
"""

JS = (
    PRUEBA
    + """
export default function () {
  if (globalThis.__ocGpuComprobada) return;  // una vez por carga de la página
  globalThis.__ocGpuComprobada = true;
  if (!ocHayGpu()) ocMarcarSinGpu();
}
"""
)

_componente = st.components.v2.component("oc_rendimiento", js=JS)


def detectar() -> None:
    """Hace la prueba en el navegador (una vez por carga) y marca la página si no hay tarjeta
    gráfica. No dibuja nada."""
    _componente(key="oc_rendimiento")
