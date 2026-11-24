"""El ojo 3D de la presentación en la entrada de la web (D-043).

Usa el mismo código que la presentación (`presentacion/ojo3d.js`, bola de cristal con refracción,
iris de luz y pupila) con Three.js. En 3 s el ojo aparece, se acerca un poco y se va a la
izquierda alejándose, mientras su luz se abre sobre los datos de la derecha.

La capa oscura, la luz y el nombre son CSS (`static/intro.html`); este componente pone el lienzo
3D dentro de esa capa y da la salida a sus animaciones cuando el ojo está listo. Si Three.js no
carga en 1,2 s (sin red, sin WebGL), se usa el ojo plano de `ojo_cristal.py`. Al terminar se
libera WebGL y se quita el lienzo: después no queda nada en marcha.
"""

from pathlib import Path

import streamlit as st

THREE = "https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js"  # la de la presentación
OJO = Path(__file__).resolve().parents[3] / "presentacion" / "ojo3d.js"

JS = """
export default function (component) {
  const { data } = component;
  const capa = document.querySelector('.oc-intro');
  if (!capa || capa.dataset.empezada) return;
  capa.dataset.empezada = '1';
  let decidido = false;
  const empezar = (sin3d) => {
    if (decidido) return false;
    decidido = true;
    if (sin3d) capa.classList.add('sin3d');
    capa.classList.add('en-marcha');
    return true;
  };
  if (!data || !data.ojo || matchMedia('(prefers-reduced-motion: reduce)').matches) {
    empezar(true);
    return;
  }
  setTimeout(() => empezar(true), 1200);  // si el 3D tarda, el ojo plano
  arrancar(data, capa, empezar).catch(() => empezar(true));
}

const suave = (x) => { x = Math.min(Math.max(x, 0), 1); return x * x * (3 - 2 * x); };
const tramo = (t, a, b) => suave((t - a) / (b - a));

async function arrancar(data, capa, empezar) {
  const THREE = await import(data.three);
  globalThis.__ocThree = THREE;
  const fuente = data.ojo.replace(/import \\* as THREE from ["']three["'];?/,
                                  'const THREE = globalThis.__ocThree;');
  const url = URL.createObjectURL(new Blob([fuente], { type: 'text/javascript' }));
  const { crearOjo } = await import(url);
  URL.revokeObjectURL(url);

  const lienzo = document.createElement('canvas');
  lienzo.className = 'oc-intro-3d';
  const ancho = innerWidth, alto = innerHeight;
  const render = new THREE.WebGLRenderer({ canvas: lienzo, alpha: true, antialias: true });
  render.setPixelRatio(Math.min(devicePixelRatio, 1.5));
  render.setSize(ancho, alto, false);
  render.outputColorSpace = THREE.SRGBColorSpace;
  render.toneMapping = THREE.ACESFilmicToneMapping;
  const escena = new THREE.Scene();
  escena.add(new THREE.HemisphereLight(0x9fd8ff, 0x02101e, 1.4));
  const sol = new THREE.DirectionalLight(0xffffff, 1.6);
  sol.position.set(-2, 3, 4);
  escena.add(sol);
  const camara = new THREE.PerspectiveCamera(35, ancho / alto, 0.1, 100);
  camara.position.set(0, 0, 6);
  const ojo = crearOjo(new THREE.Color('#0b2a4d'));
  escena.add(ojo.grupo);
  render.render(escena, camara);  // compila los sombreadores antes de enseñarlo

  if (!empezar(false)) { render.dispose(); render.forceContextLoss(); return; }
  capa.insertBefore(lienzo, capa.querySelector('.oc-intro-nombre'));

  const mirada = new THREE.Vector3();
  const alViewer = new THREE.Vector3(0, 0, 6), alosDatos = new THREE.Vector3(6, 0.2, 2);
  const inicio = performance.now();
  let antes = inicio;
  const cuadro = (ahora) => {
    const t = (ahora - inicio) / 1000;
    const dt = Math.min((ahora - antes) / 1000, 0.05);
    antes = ahora;
    if (t > 3.05 || !lienzo.isConnected) {
      render.dispose();
      render.forceContextLoss();
      lienzo.remove();
      return;
    }
    // aparece (0-0,9 s), se acerca (0,9-1,5 s) y se va a la izquierda y al fondo (1,5-2,7 s)
    const aparece = tramo(t, 0, 0.9), acerca = tramo(t, 0.9, 1.5), vase = tramo(t, 1.5, 2.7);
    ojo.grupo.scale.setScalar(0.55 * (0.75 + 0.25 * aparece));
    ojo.grupo.position.set(-3.2 * vase, 0.15 * vase, 1.1 * acerca - 3.6 * vase);
    mirada.copy(alViewer).lerp(alosDatos, tramo(t, 1.3, 2.3));
    ojo.dilatar(1 + 0.35 * tramo(t, 1.0, 1.8));  // se abre al encender la luz
    ojo.actualizar(dt, mirada);
    render.render(escena, camara);
    requestAnimationFrame(cuadro);
  };
  requestAnimationFrame(cuadro);
}
"""

_componente = st.components.v2.component("ojo_intro_3d", js=JS)


def pintar() -> None:
    """Pone el ojo 3D en la capa de entrada (solo se llama la primera vez en la sesión)."""
    ojo = OJO.read_text(encoding="utf-8") if OJO.exists() else ""
    _componente(data={"ojo": ojo, "three": THREE}, key="intro_3d")
