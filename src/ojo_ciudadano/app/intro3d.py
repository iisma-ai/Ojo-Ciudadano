"""El ojo 3D de la presentación en la entrada de la web (D-043).

Usa el mismo código que la presentación (`presentacion/ojo3d.js`, bola de cristal con refracción,
iris de luz y pupila, y `presentacion/agua.js` para el entorno de reflejos y el color del agua)
con Three.js y la misma iluminación y tono de imagen que la presentación. El ojo es la fuente de
luz: lleva un núcleo blanco. En 3 s aparece, se acerca un poco y sube alejándose hasta cerca
del borde de arriba, donde se desvanece poco a poco (así también se ve en el móvil); al
apartarse, su núcleo se enciende y
despliega rayos de luz que bajan sobre la página y la aclaran poco a poco, como los rayos del
fondo, que vienen de arriba.

La capa oscura, la luz y el nombre son CSS (`static/intro.html`); este componente pone el lienzo
3D dentro de esa capa y da la salida a sus animaciones cuando el ojo está listo. Si Three.js no
carga en 1,2 s (sin red, sin WebGL), se usa el ojo plano de `ojo_cristal.py`. Al terminar se
libera WebGL y se quita el lienzo: después no queda nada en marcha.
"""

from pathlib import Path

import streamlit as st

# La versión de la presentación. Se carga en su forma «+esm» de jsDelivr, que resuelve las
# importaciones de «three» de los complementos de posproceso a esta misma copia.
THREE = "https://cdn.jsdelivr.net/npm/three@0.169.0/"
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

// Toda la luz se calcula en los sombreadores, sin texturas: es nítida a cualquier tamaño.
const VS = `varying vec2 vUv;
  void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.); }`;

// Brillo redondo (núcleo, aura y destello del ojo)
function crearBrillo(THREE, color, caida) {
  const uniforms = { uI: { value: 0 }, uC: { value: new THREE.Color(color) } };
  const malla = new THREE.Mesh(
    new THREE.PlaneGeometry(1, 1),
    new THREE.ShaderMaterial({
      uniforms,
      vertexShader: VS,
      fragmentShader: `varying vec2 vUv; uniform float uI; uniform vec3 uC;
        void main(){
          float d = length(vUv - .5) * 2.;
          float a = uI * pow(clamp(1. - d, 0., 1.), ${caida.toFixed(2)});
          gl_FragColor = vec4(uC, a);  // se suma uC * a
        }`,
      transparent: true,
      depthWrite: false,
      depthTest: false,
      blending: THREE.AdditiveBlending,
      toneMapped: false,
    }),
  );
  malla.renderOrder = 30;
  malla.position.z = 0.6;
  return { malla, uniforms };
}

// Cono de luz que sale del ojo hacia abajo: el mismo de la presentación (crearLuz en
// presentacion/escena3d.js), con el vértice en el ojo y rayas suaves que giran despacio.
function crearCono(THREE) {
  const h = 17;
  const geo = new THREE.ConeGeometry(6, h, 96, 1, true);
  geo.translate(0, -h / 2, 0);
  const uniforms = { uT: { value: 0 }, uI: { value: 0 } };
  const cono = new THREE.Mesh(
    geo,
    new THREE.ShaderMaterial({
      uniforms,
      vertexShader: `varying vec3 vP; varying vec3 vN; varying vec3 vV;
        void main(){
          vP = position;
          vec4 mv = modelViewMatrix * vec4(position, 1.);
          vN = normalize(normalMatrix * normal);
          vV = normalize(-mv.xyz);
          gl_Position = projectionMatrix * mv;
        }`,
      fragmentShader: `uniform float uT, uI; varying vec3 vP; varying vec3 vN; varying vec3 vV;
        void main(){
          float a0 = clamp(-vP.y / 17., 0., 1.);
          float ang = atan(vP.x, vP.z);
          float rayas = .82 + .18 * sin(ang * 9. + uT * .5) * sin(ang * 4. - uT * .3);
          float a = uI * pow(clamp(abs(dot(vN, vV)), 0., 1.), .7) * pow(1. - a0, 1.6) * rayas
            * smoothstep(0., .06, a0) * .75;
          gl_FragColor = vec4(vec3(.8, .95, 1.) * a, a);
        }`,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      side: THREE.DoubleSide,
    }),
  );
  return { cono, uniforms };
}

// Haces de luz: los rayos de sol de la presentación (crearRayos en presentacion/agua.js), con la
// raíz en el ojo. Empiezan todos hacia abajo y se abren poco a poco a los lados, como mucho a
// 66 grados de la vertical: nunca apuntan hacia arriba.
function crearHaces(THREE, n) {
  const grupo = new THREE.Group();
  const comunes = { uT: { value: 0 }, uI: { value: 0 } };
  const geo = new THREE.PlaneGeometry(1, 1);
  geo.translate(0, -0.5, 0);  // el borde de arriba, en el ojo
  let semilla = 7;
  const azar = () => { semilla = (semilla * 16807) % 2147483647; return semilla / 2147483647; };
  const haces = [];
  for (let i = 0; i < n; i++) {
    const m = new THREE.Mesh(
      geo,
      new THREE.ShaderMaterial({
        uniforms: { ...comunes, uS: { value: azar() } },
        vertexShader: VS,
        fragmentShader: `varying vec2 vUv; uniform float uT, uI, uS;
          void main(){
            float borde = pow(sin(3.14159 * vUv.x), 2.);
            float alto = pow(smoothstep(0., 1., vUv.y), 1.8);
            float parpadeo = .55 + .45 * sin(uT * (.4 + uS * .5) + uS * 30. + vUv.x * 5.);
            float a = borde * alto * parpadeo * uI;
            gl_FragColor = vec4(vec3(.55, .75, 1.) * a, a);
          }`,
        transparent: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
      }),
    );
    const angulo = (-1 + (2 * (i + 0.5)) / n) * 1.15 + (azar() - 0.5) * 0.08;
    m.userData = { angulo, ancho: 0.5 + azar() * 1.4, largo: 12 + azar() * 6 };
    grupo.add(m);
    haces.push(m);
  }
  return { grupo, uniforms: comunes, haces };
}

async function arrancar(data, capa, empezar) {
  const THREE = await import(data.three + '+esm');
  globalThis.__ocThree = THREE;
  // posproceso de la presentación: brillo (bloom) y salida de color; sin él todo sale más oscuro
  const pp = (f) => import(data.three + 'examples/jsm/postprocessing/' + f + '.js/+esm');
  const efectos = await Promise.all(['EffectComposer', 'RenderPass', 'UnrealBloomPass',
                                     'OutputPass'].map(pp)).catch(() => null);
  const { crearOjo } = await modulo(data.ojo);
  const Agua = data.agua ? await modulo(data.agua) : null;

  const lienzo = document.createElement('canvas');
  lienzo.className = 'oc-intro-3d';
  const ancho = innerWidth, alto = innerHeight;
  const render = new THREE.WebGLRenderer({ canvas: lienzo, alpha: true, antialias: true });
  // doble resolución (también en pantallas normales): el ojo y sus fibras salen nítidos
  const resolucion = Math.min(Math.max(devicePixelRatio, 1) * 2, 2.5);
  render.setPixelRatio(resolucion);
  render.setSize(ancho, alto, false);
  render.outputColorSpace = THREE.SRGBColorSpace;
  render.toneMapping = THREE.NeutralToneMapping;  // como la presentación: conserva los azules
  render.toneMappingExposure = 1.3;
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
  if (Agua) Agua.colorProfundidad(0, agua);
  agua.multiplyScalar(1.35);  // agua clara alrededor: el cristal no se ve oscuro
  const ojo = crearOjo(agua);
  escena.add(ojo.grupo);

  // el ojo es la fuente de luz: núcleo y aura desde que aparece, destello al encenderse
  const nucleo = crearBrillo(THREE, 0xeaf7ff, 2.4);
  const aura = crearBrillo(THREE, 0x8cc8ff, 1.6);
  const destello = crearBrillo(THREE, 0xc8ebff, 2.0);
  aura.malla.scale.setScalar(4.2);
  ojo.grupo.add(aura.malla, destello.malla, nucleo.malla);
  // la luz que despliega hacia abajo: cono y haces, en la posición del ojo (sin su escala)
  const luz = new THREE.Group();
  const cono = crearCono(THREE);
  const haces = crearHaces(THREE, 11);
  luz.add(cono.cono, haces.grupo);
  escena.add(luz);

  // el mar de la presentación (presentacion/agua.js), de principio a fin: rayos de sol muy
  // tenues y burbujas que suben; se ven más al aclararse. No se ve la superficie: estamos en el
  // fondo, donde todo es oscuro y la luz la pone el ojo. La nieve marina es la capa
  // CSS de static/intro.html: la de la presentación usa puntos de WebGL, que en algunas tarjetas
  // gráficas (comprobado en Windows) salen como cuadrados llenos.
  const mar = Agua ? {
    rayosSol: Agua.crearRayos(),
    burbujas: Agua.crearBurbujitas(),
  } : null;
  if (mar) {
    mar.rayosSol.grupo.position.set(0, 6, 0);
    mar.burbujas.malla.position.z = -8;  // que no pasen pegadas a la cámara
    // Burbujas: el sombreador de la presentación usa pow() y, en Windows (ANGLE), daba valores no
    // válidos que el brillo convertía en bloques cuadrados. El mismo dibujo (borde plateado y
    // reflejo arriba a la izquierda) sin pow(), con la normal normalizada y todo acotado; el
    // reflejo queda por debajo del umbral del brillo.
    const materialBurbujas = mar.burbujas.malla.material;
    materialBurbujas.fragmentShader = `varying vec3 vN; varying vec3 vV; uniform float uI;
      void main(){
        vec3 n = normalize(vN), v = normalize(vV);
        float f = clamp(1. - dot(n, v), 0., 1.);
        float borde = f * f * mix(1., f, .4);              // ~ f^2,4
        float d = clamp(dot(n, normalize(vec3(-.4, .65, .65))), 0., 1.);
        float d2 = d * d, d4 = d2 * d2, d8 = d4 * d4, d16 = d8 * d8, d32 = d16 * d16;
        float brillo = d32 * d16 * d2;                     // d^50
        float a = clamp(borde * .9 + brillo, 0., 1.) * uI;
        gl_FragColor = vec4(mix(vec3(.55, .75, 1.), vec3(.85), brillo), a);
      }`;
    materialBurbujas.needsUpdate = true;
    escena.add(mar.rayosSol.grupo, mar.burbujas.malla);
  }

  let dibujar = () => render.render(escena, camara);
  if (efectos) {
    const [{ EffectComposer }, { RenderPass }, { UnrealBloomPass }, { OutputPass }] = efectos;
    render.setClearColor(0x000000, 0);
    // con posproceso el suavizado de bordes del lienzo no cuenta: el destino lleva el suyo
    const destino = new THREE.WebGLRenderTarget(ancho * resolucion, alto * resolucion,
      { type: THREE.HalfFloatType, samples: 4 });
    const compositor = new EffectComposer(render, destino);
    compositor.setPixelRatio(resolucion);
    compositor.setSize(ancho, alto);
    compositor.addPass(new RenderPass(escena, camara));
    const brillo = new UnrealBloomPass(new THREE.Vector2(ancho, alto), 0.35, 0.7, 0.82);
    // El desenfoque del brillo escribe opacidad 1 en todo el lienzo y taparía la página: que
    // la opacidad sea la de la propia luz, así el brillo solo cubre donde hay luz.
    for (const m of brillo.separableBlurMaterials) {
      m.fragmentShader = m.fragmentShader.replace(
        'vec4(diffuseSum/weightSum, 1.0)',  // la línea exacta de Three.js 0.169.0
        'vec4(diffuseSum / weightSum,'
          + ' max(max(diffuseSum.r, diffuseSum.g), diffuseSum.b) / weightSum)');
      m.needsUpdate = true;
    }
    compositor.addPass(brillo);
    compositor.addPass(new OutputPass());
    dibujar = () => compositor.render();
  }
  dibujar();  // compila los sombreadores antes de enseñarlo

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
      lienzo.remove();
      return;
    }
    // aparece (0-0,9 s), se acerca (0,9-1,5 s) y sube alejándose hasta cerca del borde de
    // arriba (1,4-2,4 s); allí se desvanece poco a poco (1,95-3 s)
    const aparece = tramo(t, 0, 0.9), acerca = tramo(t, 0.9, 1.5);
    const sube = tramo(t, 1.4, 2.4);  // sube suave y llega arriba hacia 2,4 s
    const enciende = tramo(t, 1.3, 2.2), abre = tramo(t, 1.45, 2.75), apaga = tramo(t, 2.55, 3.0);
    ojo.grupo.scale.setScalar(0.47 * (0.75 + 0.25 * aparece));  // algo más pequeño
    // aparece y, ya arriba, se desvanece poco a poco (de 1,95 a 3 s) con su luz; con el
    // mismo reloj que el movimiento, para que se vea cómo se va apagando
    lienzo.style.opacity = (tramo(t, 0, 0.35) * (1 - tramo(t, 1.95, 3.0))).toFixed(3);
    ojo.grupo.position.set(0, 1.75 * sube, 1.1 * acerca - 3.1 * sube);  // visible sobre el título
    mirada.copy(alEspectador).lerp(alaPagina, tramo(t, 1.3, 2.3));  // mira hacia la página
    ojo.dilatar(1 + 0.35 * enciende);
    nucleo.malla.scale.setScalar(1.3 + 0.6 * enciende);
    nucleo.uniforms.uI.value = (0.4 + 0.3 * enciende) * aparece;
    aura.uniforms.uI.value = (0.07 + 0.08 * enciende) * aparece;  // halo discreto
    destello.malla.scale.setScalar(1.5 + 5 * enciende);
    destello.uniforms.uI.value = 0.3 * enciende * (1 - apaga);
    // la luz hacia abajo: empieza estrecha, recta hacia la página, y se abre a los lados
    luz.position.copy(ojo.grupo.position);
    luz.position.z -= 0.05;  // un poco detrás: el cristal tapa la raíz y parece salir del ojo
    cono.cono.scale.set(0.15 + 1.25 * abre, 0.35 + 0.65 * enciende, 0.15 + 1.25 * abre);
    cono.uniforms.uI.value = 0.5 * enciende * (1 - apaga);  // suave: se funde con la página
    cono.uniforms.uT.value = t;
    haces.uniforms.uI.value = 0.26 * enciende * (1 - apaga);
    haces.uniforms.uT.value = t * 2;
    for (const h of haces.haces) {
      const { angulo, ancho, largo } = h.userData;
      h.rotation.z = angulo * abre;
      h.scale.set(ancho * (0.4 + 0.6 * abre), largo * (0.3 + 0.7 * enciende), 1);
    }
    if (mar) {
      // de oscuro (0,2) a claro (1) mientras la página se desvela; se funde al final con el
      // fondo de la web, que tiene sus propios rayos y burbujas
      const claridad = (0.2 + 0.8 * tramo(t, 1.2, 2.8)) * (1 - tramo(t, 2.6, 3.0));
      mar.rayosSol.uniforms.uT.value = t;
      mar.rayosSol.uniforms.uI.value = 0.02 + 0.06 * claridad;  // del fondo: apenas llegan
      mar.burbujas.uniforms.uI.value = (0.55 + 0.45 * claridad) * (1 - tramo(t, 2.6, 3.0));
      mar.burbujas.actualizar(dt, t, 0);
    }
    ojo.actualizar(dt, mirada);
    dibujar();
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
