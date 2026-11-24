"""El ojo 3D de la presentación en la entrada de la web (D-043).

Usa el mismo código que la presentación (`presentacion/ojo3d.js`, bola de cristal con refracción,
iris de luz y pupila, y `presentacion/agua.js` para el entorno de reflejos y el color del agua)
con Three.js y la misma iluminación y tono de imagen que la presentación. El ojo es la fuente de
luz: lleva un núcleo blanco. En 3 s aparece, se acerca un poco y sube alejándose hacia arriba
(así también se ve en el móvil); al apartarse, su núcleo se enciende y la luz baja sobre la
página, como los rayos que vienen de arriba.

La capa oscura, la luz y el nombre son CSS (`static/intro.html`); este componente pone el lienzo
3D dentro de esa capa y da la salida a sus animaciones cuando el ojo está listo. Si Three.js no
carga en 1,2 s (sin red, sin WebGL), se usa el ojo plano de `ojo_cristal.py`. Al terminar se
libera WebGL y se quita el lienzo: después no queda nada en marcha.
"""

from pathlib import Path

import streamlit as st

THREE = "https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js"  # la de la presentación
PRESENTACION = Path(__file__).resolve().parents[3] / "presentacion"
OJO = PRESENTACION / "ojo3d.js"
AGUA = PRESENTACION / "agua.js"

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

const modulo = async (fuente) => {
  const codigo = fuente.replace(/import \\* as THREE from ["']three["'];?/,
                                'const THREE = globalThis.__ocThree;');
  const url = URL.createObjectURL(new Blob([codigo], { type: 'text/javascript' }));
  try { return await import(url); } finally { URL.revokeObjectURL(url); }
};

// Luz redonda (núcleo del ojo y destello), como el brillo de la presentación
function luzRedonda(THREE) {
  const c = document.createElement('canvas');
  c.width = c.height = 256;
  const g = c.getContext('2d');
  const d = g.createRadialGradient(128, 128, 0, 128, 128, 128);
  d.addColorStop(0, 'rgba(255,255,255,1)');
  d.addColorStop(0.14, 'rgba(225,246,255,.92)');
  d.addColorStop(0.38, 'rgba(140,200,255,.38)');
  d.addColorStop(0.7, 'rgba(70,140,240,.1)');
  d.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = d;
  g.fillRect(0, 0, 256, 256);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

async function arrancar(data, capa, empezar) {
  const THREE = await import(data.three);
  globalThis.__ocThree = THREE;
  const { crearOjo } = await modulo(data.ojo);
  const Agua = data.agua ? await modulo(data.agua) : null;

  const lienzo = document.createElement('canvas');
  lienzo.className = 'oc-intro-3d';
  const ancho = innerWidth, alto = innerHeight;
  const render = new THREE.WebGLRenderer({ canvas: lienzo, alpha: true, antialias: true });
  render.setPixelRatio(Math.min(devicePixelRatio, 1.5));
  render.setSize(ancho, alto, false);
  render.outputColorSpace = THREE.SRGBColorSpace;
  render.toneMapping = THREE.NeutralToneMapping;  // como la presentación: conserva los azules
  render.toneMappingExposure = 1.15;
  const escena = new THREE.Scene();
  if (Agua) escena.environment = Agua.entorno(render);
  escena.add(new THREE.HemisphereLight(0xa8ecff, 0x021020, 1.1));
  const sol = new THREE.DirectionalLight(0xe6f9ff, 2.6);
  sol.position.set(4, 20, 10);
  escena.add(sol);
  const camara = new THREE.PerspectiveCamera(35, ancho / alto, 0.1, 100);
  camara.position.set(0, 0, 6);
  // agua de cerca de la superficie, con luz: el cristal refleja un mar claro y el ojo se ve claro
  const agua = new THREE.Color('#13406b');
  if (Agua) Agua.colorProfundidad(0.15, agua);
  const ojo = crearOjo(agua);
  escena.add(ojo.grupo);

  // el ojo es la fuente de luz: núcleo blanco siempre y destello que se abre al apartarse
  const textura = luzRedonda(THREE);
  const foco = (opacidad) => {
    const m = new THREE.SpriteMaterial({ map: textura, transparent: true, opacity: opacidad,
      blending: THREE.AdditiveBlending, depthTest: false, depthWrite: false, toneMapped: false });
    const s = new THREE.Sprite(m);
    s.renderOrder = 30;
    s.position.z = 0.6;
    ojo.grupo.add(s);
    return s;
  };
  const nucleo = foco(0.6), destello = foco(0), aura = foco(0.35);
  aura.scale.setScalar(3.4);
  render.render(escena, camara);  // compila los sombreadores antes de enseñarlo

  if (!empezar(false)) { render.dispose(); render.forceContextLoss(); return; }
  capa.insertBefore(lienzo, capa.querySelector('.oc-intro-nombre'));

  const mirada = new THREE.Vector3();
  const alEspectador = new THREE.Vector3(0, 0, 6), alaPagina = new THREE.Vector3(0, -7, 3);
  const inicio = performance.now();
  let antes = inicio;
  const cuadro = (ahora) => {
    const t = (ahora - inicio) / 1000;
    const dt = Math.min((ahora - antes) / 1000, 0.05);
    antes = ahora;
    if (t > 3.05 || !lienzo.isConnected) {
      render.dispose();
      render.forceContextLoss();
      textura.dispose();
      lienzo.remove();
      return;
    }
    // aparece (0-0,9 s), se acerca (0,9-1,5 s) y sube alejándose (1,5-2,7 s)
    const aparece = tramo(t, 0, 0.9), acerca = tramo(t, 0.9, 1.5), sube = tramo(t, 1.5, 2.7);
    const enciende = tramo(t, 1.35, 2.1), apaga = tramo(t, 2.45, 3.0);
    ojo.grupo.scale.setScalar(0.55 * (0.75 + 0.25 * aparece));
    ojo.grupo.position.set(0, 2.3 * sube, 1.1 * acerca - 4.6 * sube);
    mirada.copy(alEspectador).lerp(alaPagina, tramo(t, 1.3, 2.3));  // mira hacia la página
    ojo.dilatar(1 + 0.35 * enciende);
    // la luz del núcleo: presente desde que aparece; al apartarse se enciende y se abre
    nucleo.scale.setScalar(1.1 + 0.7 * enciende);
    nucleo.material.opacity = (0.45 + 0.3 * enciende) * aparece * (1 - 0.6 * apaga);
    aura.material.opacity = (0.3 + 0.25 * enciende) * aparece * (1 - apaga);
    destello.scale.setScalar(1 + 7 * enciende);
    destello.material.opacity = 0.42 * enciende * (1 - apaga);  // suave: ilumina sin deslumbrar
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
    agua = AGUA.read_text(encoding="utf-8") if AGUA.exists() else ""
    _componente(data={"ojo": ojo, "agua": agua, "three": THREE}, key="intro_3d")
