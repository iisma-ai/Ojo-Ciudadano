/* Motor 3D de la presentacion. Lee DIAPOSITIVAS (diapositivas.js), monta cada diapositiva a una
 * profundidad distinta del mar y baja la camara de una a otra. Los textos son HTML encima del 3D. */
import * as THREE from "three";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";
import * as Agua from "./agua.js";
import { crearOjo } from "./ojo3d.js";

const K = 108; // pixeles del escenario de 1920 x 1080 por unidad 3D
const SEP = 17; // distancia vertical entre diapositivas
const FOV = 40;
const D0 = 5 / Math.tan(THREE.MathUtils.degToRad(FOV / 2)); // camara que ve justo 1080 px de alto
const Z_OJO = 2.5;

const TONOS = {
  azul: ["#6fb0ff", "#1b6fe0", "#041c4a"],
  ambar: ["#ffd27a", "#e0a032", "#4a2a02"],
  agua: ["#8fdcff", "#1a8fd0", "#042a52"],
};

// ---------- Render ----------
const lienzo = document.getElementById("lienzo");
const capa = document.getElementById("capa");
let renderer;
try {
  renderer = new THREE.WebGLRenderer({ canvas: lienzo, antialias: true, powerPreference: "high-performance" });
} catch (err) {
  document.getElementById("cortina").textContent = "Este navegador no puede mostrar gráficos 3D (WebGL).";
  throw err;
}
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
renderer.toneMapping = THREE.NeutralToneMapping; // conserva el tono de los azules (ACES los vuelve morados)
renderer.toneMappingExposure = 1.05;

const escena = new THREE.Scene();
const camara = new THREE.PerspectiveCamera(FOV, 16 / 9, 0.1, 400);
escena.environment = Agua.entorno(renderer);
const colorAgua = new THREE.Color();
escena.fog = new THREE.FogExp2(colorAgua, 0.02);
escena.background = colorAgua;

const cielo = new THREE.HemisphereLight(0xa8ecff, 0x021020, 1.1);
const sol = new THREE.DirectionalLight(0xe6f9ff, 2.6);
escena.add(cielo, sol, sol.target);

const rayos = Agua.crearRayos();
const superficie = Agua.crearSuperficie(8.5);
const nieve = Agua.crearNieve();
const burbujitas = Agua.crearBurbujitas();
escena.add(rayos.grupo, superficie.malla, nieve.puntos, burbujitas.malla);

const compositor = new EffectComposer(renderer);
compositor.addPass(new RenderPass(escena, camara));
const brillo = new UnrealBloomPass(new THREE.Vector2(1, 1), 0.55, 0.7, 0.82);
compositor.addPass(brillo);
compositor.addPass(new OutputPass());
const final = new ShaderPass(Agua.PasoFinal);
compositor.addPass(final);

// ---------- Materiales compartidos ----------
const GEO = new THREE.SphereGeometry(1, 72, 54);
const GEO_TAPA = new THREE.CircleGeometry(1, 64).rotateX(-Math.PI / 2);
// Cristal: solo sus reflejos se suman encima (difuso negro y mezcla aditiva), asi lo de dentro
// conserva su color y el borde brilla mas que el centro, como un cristal de verdad.
const VIDRIO = new THREE.MeshPhysicalMaterial({
  color: 0x000000,
  roughness: 0.07,
  metalness: 0,
  clearcoat: 1,
  clearcoatRoughness: 0.02,
  iridescence: 0.6,
  iridescenceIOR: 1.3,
  iridescenceThicknessRange: [180, 520],
  specularIntensity: 1,
  envMapIntensity: 2.4,
  transparent: true,
  depthWrite: false,
  blending: THREE.AdditiveBlending,
});
const VIDRIO_LENTE = VIDRIO.clone();
VIDRIO_LENTE.iridescence = 0.3;
// Con mezcla aditiva la niebla debe apagar el reflejo (ir a negro), no sumarle el color del agua
export function nieblaANegro(material) {
  material.onBeforeCompile = (s) => {
    s.fragmentShader = s.fragmentShader.replace(
      "#include <fog_fragment>",
      `#ifdef USE_FOG
        float fogFactor = 1.0 - exp(-fogDensity * fogDensity * vFogDepth * vFogDepth);
        gl_FragColor.rgb *= 1.0 - fogFactor;
      #endif`,
    );
  };
  return material;
}
nieblaANegro(VIDRIO);
nieblaANegro(VIDRIO_LENTE);

const U = {
  uT: { value: 0 },
  uLuz: { value: 1 },
  uFogColor: { value: colorAgua },
  uFogDensity: { value: 0.02 },
};
const NIEBLA_GLSL = `
  vec3 conNiebla(vec3 c, vec3 w){
    float d = length(w - cameraPosition);
    float f = 1. - exp(-uFogDensity * uFogDensity * d * d);
    return mix(c, uFogColor, f);
  }`;

function materialLiquido(tono) {
  const [a, b, c] = TONOS[tono] || TONOS.agua;
  return new THREE.ShaderMaterial({
    uniforms: {
      ...U,
      uNivel: { value: -1.1 },
      uC1: { value: new THREE.Color(a) },
      uC2: { value: new THREE.Color(b) },
      uC3: { value: new THREE.Color(c) },
    },
    side: THREE.DoubleSide,
    vertexShader: `varying vec3 vP; varying vec3 vW; varying vec3 vN;
      void main(){
        vP = position;
        vec4 w = modelMatrix * vec4(position, 1.);
        vW = w.xyz;
        vN = normalize(mat3(modelMatrix) * normal);
        gl_Position = projectionMatrix * viewMatrix * w;
      }`,
    fragmentShader: `uniform float uT, uLuz, uNivel, uFogDensity; uniform vec3 uC1, uC2, uC3, uFogColor;
      varying vec3 vP; varying vec3 vW; varying vec3 vN;
      ${NIEBLA_GLSL}
      void main(){
        float ola = sin(vP.x * 6. + uT * 1.7) * .018 + sin(vP.z * 5. + uT * 1.3) * .014;
        if (vP.y > uNivel + ola) discard;
        vec3 n = gl_FrontFacing ? vN : -vN;
        vec3 v = normalize(cameraPosition - vW);
        float h = (vP.y + 1.) * .5;
        vec3 c = mix(uC3, uC2, smoothstep(0., .75, h));
        c = mix(c, uC1, smoothstep(uNivel - .18, uNivel, vP.y) * .55);
        float luz = .45 + .55 * max(dot(n, normalize(vec3(.3, 1., .4))), 0.);
        float ondas = sin(vP.y * 6. + uT * .8) * 1.4;
        float causticas = pow(clamp(1. - abs(sin(vP.x * 7. + ondas + uT * .5)), 0., 1.), 10.)
                        + pow(clamp(1. - abs(sin(vP.z * 6. - ondas * .8 - uT * .4)), 0., 1.), 10.);
        float fres = pow(clamp(1. - abs(dot(n, v)), 0., 1.), 2.5);
        float nucleo = pow(clamp(abs(dot(n, v)), 0., 1.), 2.) * .35;
        c = c * luz * (gl_FrontFacing ? 1. : .6) * uLuz + causticas * uC1 * .07 * uLuz + fres * uC1 * .45 + uC2 * nucleo * uLuz;
        gl_FragColor = vec4(conNiebla(c * 1.05, vW), 1.);
      }`,
  });
}

function materialTapa(mLiquido) {
  return new THREE.ShaderMaterial({
    uniforms: mLiquido.uniforms,
    side: THREE.DoubleSide,
    vertexShader: `varying vec3 vW; varying vec2 vQ;
      void main(){ vQ = position.xz; vec4 w = modelMatrix * vec4(position, 1.); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }`,
    fragmentShader: `uniform float uT, uLuz, uFogDensity; uniform vec3 uC1, uC2, uFogColor; varying vec3 vW; varying vec2 vQ;
      ${NIEBLA_GLSL}
      void main(){
        float r = length(vQ);
        float onda = .5 + .5 * sin(r * 22. - uT * 2.2);
        vec3 c = mix(uC2, uC1, .25 + .2 * onda) * (.6 + .5 * uLuz);
        gl_FragColor = vec4(conNiebla(c, vW), 1.);
      }`,
  });
}

const MAT_ENLACE = () =>
  new THREE.ShaderMaterial({
    uniforms: { uT: U.uT, uProg: { value: 0 } },
    vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.); }`,
    fragmentShader: `uniform float uT, uProg; varying vec2 vUv;
      void main(){
        if (vUv.x > uProg) discard;
        float pulso = smoothstep(.82, 1., sin(vUv.x * 36. - uT * 4.) * .5 + .5);
        float a = .55 + pulso * .9;
        gl_FragColor = vec4(vec3(.65, .9, 1.) * (1. + pulso * 2.5) * a, a);
      }`,
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
  });

// ---------- Coordenadas: escenario 1920 x 1080 -> mundo ----------
const yDiapo = (i) => -i * SEP;
function aMundo(i, x, y, z = 0) {
  const f = (D0 - z) / D0;
  return new THREE.Vector3(((x - 960) / K) * f, (-(y - 540) / K) * f + yDiapo(i), z);
}
const radioMundo = (rpx, z = 0) => (rpx / K) * ((D0 - z) / D0);

// ---------- Construccion ----------
const items = [];
const ojo = crearOjo(colorAgua);
escena.add(ojo.grupo);

function texturaVacia() {
  const c = document.createElement("canvas");
  c.width = c.height = 512;
  const g = c.getContext("2d");
  const f = g.createRadialGradient(200, 170, 20, 256, 256, 300);
  f.addColorStop(0, "#1f5a9a");
  f.addColorStop(1, "#06152e");
  g.fillStyle = f;
  g.fillRect(0, 0, 512, 512);
  g.strokeStyle = "rgba(160,210,255,0.12)";
  for (let x = 0; x < 512; x += 32) {
    g.beginPath();
    g.moveTo(x, 0);
    g.lineTo(x, 512);
    g.moveTo(0, x);
    g.lineTo(512, x);
    g.stroke();
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

function texturaMedio(src, etiqueta) {
  if (!src) return texturaVacia();
  if (/\.(mp4|webm)$/i.test(src)) {
    const v = document.createElement("video");
    Object.assign(v, { src, muted: true, loop: true, playsInline: true, autoplay: true });
    v.play().catch(() => {});
    const t = new THREE.VideoTexture(v);
    t.colorSpace = THREE.SRGBColorSpace;
    return t;
  }
  const t = new THREE.TextureLoader().load(src);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

function etiquetaHtml(html, clase) {
  const el = document.createElement("div");
  el.className = `t ${clase}`;
  el.innerHTML = html;
  capa.appendChild(el);
  return el;
}

function crearBurbuja(e, i) {
  const z = e.z || 0;
  const R = radioMundo(e.r, z);
  const grupo = new THREE.Group();
  grupo.position.copy(aMundo(i, e.x, e.y, z));
  const cont = new THREE.Group();
  grupo.add(cont);
  const mLiq = materialLiquido(e.tono);
  const liquido = new THREE.Mesh(GEO, mLiq);
  liquido.scale.setScalar(R * 0.955);
  const tapa = new THREE.Mesh(GEO_TAPA, materialTapa(mLiq));
  const vidrio = new THREE.Mesh(GEO, VIDRIO);
  vidrio.scale.setScalar(R);
  cont.add(liquido, tapa, vidrio);
  escena.add(grupo);
  const it = { tipo: "burbuja", e, i, grupo, cont, R, mLiq, tapa, nivel: -1.05, llenado: e.llenado ?? 0 };
  if (e.etiqueta || e.valor) {
    const dentro = Boolean(e.valor);
    it.dom = etiquetaHtml(
      (e.valor ? `<b>${e.valor}</b>` : "") + (e.etiqueta ? `<span>${e.etiqueta}</span>` : ""),
      dentro ? "etiqueta dentro" : "etiqueta",
    );
    it.ancla = aMundo(i, e.x, e.y, z);
    it.bajo = !dentro; // la etiqueta va debajo, a una distancia fija en pantalla
    it.tam = dentro ? Math.min(e.r * 0.2, 34) : 19;
  }
  return it;
}

function crearCaptura(e, i) {
  const R = radioMundo(e.r);
  const grupo = new THREE.Group();
  grupo.position.copy(aMundo(i, e.x, e.y));
  const cont = new THREE.Group();
  grupo.add(cont);
  const disco = new THREE.Mesh(
    new THREE.CircleGeometry(1, 96),
    new THREE.MeshBasicMaterial({ map: texturaMedio(e.src, e.etiqueta), toneMapped: false, fog: false }),
  );
  disco.scale.setScalar(R * 0.94);
  const vidrio = new THREE.Mesh(GEO, VIDRIO_LENTE);
  vidrio.scale.setScalar(R);
  cont.add(disco, vidrio);
  escena.add(grupo);
  const it = { tipo: "captura", e, i, grupo, cont, R };
  if (e.etiqueta) {
    it.dom = etiquetaHtml(`<span>${e.etiqueta}</span>`, "etiqueta");
    it.ancla = aMundo(i, e.x, e.y);
    it.bajo = true;
    it.tam = 24;
  }
  return it;
}

function crearEnlace(e, i, porId) {
  const a = porId[e.de];
  const b = porId[e.a];
  if (!a || !b) return null;
  const pa = aMundo(i, a.x, a.y, a.z || 0);
  const pb = aMundo(i, b.x, b.y, b.z || 0);
  const ra = radioMundo(a.r);
  const rb = radioMundo(b.r);
  const dir = pb.clone().sub(pa).normalize();
  const p1 = pa.clone().addScaledVector(dir, ra * 1.02);
  const p2 = pb.clone().addScaledVector(dir, -rb * 1.02);
  const medio = p1.clone().lerp(p2, 0.5).add(new THREE.Vector3(0, -0.35, 0.4));
  const curva = new THREE.QuadraticBezierCurve3(p1, medio, p2);
  const malla = new THREE.Mesh(new THREE.TubeGeometry(curva, 90, 0.022, 10), MAT_ENLACE());
  escena.add(malla);
  return { tipo: "enlace", e, i, malla, prog: 0 };
}

function crearLuz(i, cfgOjo) {
  const pos = aMundo(i, cfgOjo.x, cfgOjo.y, Z_OJO);
  const h = 17;
  const geo = new THREE.ConeGeometry(6, h, 96, 1, true);
  geo.translate(0, -h / 2, 0);
  const uniforms = { uT: U.uT, uI: { value: 0 } };
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
          float a = uI * pow(clamp(abs(dot(vN, vV)), 0., 1.), .7) * pow(1. - a0, 1.6) * rayas * smoothstep(0., .06, a0) * .75;
          gl_FragColor = vec4(vec3(.8, .95, 1.) * a, a);
        }`,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      side: THREE.DoubleSide,
    }),
  );
  cono.position.copy(pos);
  const foco = new THREE.SpotLight(0xd8f4ff, 0, 30, 0.55, 0.7, 1.2);
  foco.position.copy(pos);
  foco.target.position.set(pos.x, pos.y - 10, 0);
  escena.add(cono, foco, foco.target);
  return { tipo: "luz", i, cono, foco, uniforms, int: 0 };
}

// ---------- Paneles de cristal con datos y chat del asistente (HTML fijo en pantalla) ----------
function bloque(b) {
  if (b.kpis)
    return `<div class="kpis">${b.kpis.map(([v, t]) => `<div class="kpi"><b>${v}</b><span>${t}</span></div>`).join("")}</div>`;
  if (b.medidor) {
    const m = b.medidor;
    return `<div class="sub">${m.titulo}</div><div class="medidor"><i style="--v:${m.valor * 100}%"></i></div>` +
      `<div class="medidor-pie"><span>${m.izq || ""}</span><span>${m.der || ""}</span></div>`;
  }
  if (b.barras) {
    const max = b.barras.max ?? Math.max(...b.barras.filas.map((f) => f[1]));
    return `<div class="sub">${b.barras.titulo}</div>` + b.barras.filas
      .map(([et, v, txt], j) =>
        `<div class="barra"><span class="b-et">${et}</span><span class="b-pista"><i style="--v:${(v / max) * 100}%;--j:${j}"></i></span><span class="b-val">${txt}</span></div>`)
      .join("");
  }
  if (b.puntos) {
    let puntos = "";
    for (let j = 0; j < 100; j++) puntos += `<i class="${j < b.puntos.valor ? "lleno" : ""}" style="--j:${j}"></i>`;
    return `<div class="puntos-fila"><div class="puntos">${puntos}</div><div class="puntos-txt"><b>${b.puntos.valor}</b><span>${b.puntos.texto}</span></div></div>`;
  }
  if (b.senales)
    return `<div class="sub">${b.titulo || "Señales"}</div>` + b.senales
      .map(([nombre, activa, txt]) => `<div class="senal ${activa ? "activa" : ""}"><i></i><div><b>${nombre}</b>${txt ? `<span>${txt}</span>` : ""}</div></div>`)
      .join("");
  if (b.filas) return b.filas.map(([a, c]) => `<div class="fila"><span>${a}</span><b>${c}</b></div>`).join("");
  if (b.tarta) {
    // anillo: cada sector se dibuja creciendo, con su leyenda al lado
    const total = b.tarta.filas.reduce((s, f) => s + f[1], 0);
    const C = 2 * Math.PI * 40;
    let inicio = 0;
    const sectores = b.tarta.filas.map(([, v, , color], j) => {
      const largo = (v / total) * C;
      const s = `<circle class="seg" cx="50" cy="50" r="40" stroke="${color}" style="--l:${Math.max(largo - 1.2, 0.5)};--c:${C};--j:${j};stroke-dashoffset:${-inicio}"/>`;
      inicio += largo;
      return s;
    });
    const leyenda = b.tarta.filas
      .map(([nombre, , txt, color], j) => `<div class="ley" style="--j:${j}"><i style="background:${color}"></i><b>${nombre}</b><span>${txt}</span></div>`)
      .join("");
    const centro = b.tarta.centro || [];
    return `<div class="sub">${b.tarta.titulo || ""}</div><div class="tarta"><div class="anillo"><svg viewBox="0 0 100 100">` +
      `<circle cx="50" cy="50" r="40" class="pista"/>${sectores.join("")}</svg>` +
      `<div class="centro"><b>${centro[0] || ""}</b><span>${centro[1] || ""}</span></div></div><div class="leyenda">${leyenda}</div></div>`;
  }
  if (b.chips) return `<div class="chips">${b.chips.map((c) => `<span>${c}</span>`).join("")}</div>`;
  if (b.texto) return `<p>${b.texto}</p>`;
  return "";
}

function crearPanel(e, i) {
  let h = (e.etiqueta ? `<div class="p-etiqueta">${e.etiqueta}</div>` : "") + (e.titulo ? `<div class="p-titulo">${e.titulo}</div>` : "");
  let k = 0;
  for (const b of e.bloques || []) h += `<div class="bloque" style="--i:${k++}">${bloque(b)}</div>`;
  if (e.fuente) h += `<div class="bloque p-fuente" style="--i:${k}">${e.fuente}</div>`;
  return { tipo: "panel", i, dom: etiquetaHtml(h, "panel"), fijo: { x: e.x, y: e.y, ancho: e.ancho || 560 }, tam: 18 };
}

function crearChat(e, i) {
  const respuesta = e.respuesta.map((b, k) => `<div class="bloque" style="--i:${k}">${bloque(b)}</div>`).join("");
  const dom = etiquetaHtml(
    `<div class="chat-cab"><i></i>Asistente de Ojo Ciudadano</div>` +
      `<div class="pregunta"><span class="escrito"></span><span class="cursor"></span></div>` +
      `<div class="pensando"><i></i><i></i><i></i><span>Consultando los datos oficiales</span></div>` +
      `<div class="respuesta">${respuesta}</div>`,
    "panel chat",
  );
  return { tipo: "chat", i, dom, fijo: { x: e.x, y: e.y, ancho: e.ancho || 760 }, tam: 19, pregunta: e.pregunta };
}

// El chat escribe la pregunta, piensa y contesta; se reinicia si se vuelve atras
function animarChat(it, mostrar) {
  clearInterval(it.reloj1);
  clearTimeout(it.reloj2);
  const dom = it.dom;
  const escrito = dom.querySelector(".escrito");
  dom.classList.remove("pensando-on", "respondido");
  escrito.textContent = "";
  if (!mostrar) return;
  let k = 0;
  it.reloj2 = setTimeout(() => {
    it.reloj1 = setInterval(() => {
      escrito.textContent = it.pregunta.slice(0, ++k);
      if (k >= it.pregunta.length) {
        clearInterval(it.reloj1);
        dom.classList.add("pensando-on");
        it.reloj2 = setTimeout(() => {
          dom.classList.remove("pensando-on");
          dom.classList.add("respondido");
        }, 1400);
      }
    }, 32);
  }, 700);
}

const diapositivas = DIAPOSITIVAS.map((d, i) => {
  const porId = {};
  for (const e of d.elementos) if (e.id) porId[e.id] = e;
  let maxPaso = 0;
  const propios = [];
  const porPaso = {};
  for (const e of d.elementos) {
    let it = null;
    if (e.tipo === "burbuja") it = crearBurbuja(e, i);
    else if (e.tipo === "captura") it = crearCaptura(e, i);
    else if (e.tipo === "enlace") it = crearEnlace(e, i, porId);
    else if (e.tipo === "luz") it = crearLuz(i, d.ojo);
    else if (e.tipo === "niebla") it = { tipo: "niebla", i };
    else if (e.tipo === "foco") it = { tipo: "foco", i, de: porId[e.de], zoom: e.zoom || 1.6, sx: e.x ?? 600, sy: e.y ?? 540 };
    else if (e.tipo === "panel") it = crearPanel(e, i);
    else if (e.tipo === "chat") it = crearChat(e, i);
    else if (e.tipo === "texto") {
      it = { tipo: "texto", i, dom: etiquetaHtml(e.texto, e.clase || ""), ancla: aMundo(i, e.x, e.y), tam: e.tam || 40 };
      if (e.clase === "nota") it.tam *= 0.62;
    } else if (e.tipo === "cifra") {
      it = {
        tipo: "cifra",
        i,
        valor: e.valor,
        dom: etiquetaHtml(`<div class="num">0</div><div class="cap">${e.texto || ""}</div>`, "cifra"),
        ancla: aMundo(i, e.x, e.y),
        tam: 40,
      };
    }
    if (!it) continue;
    it.paso = e.paso || 0;
    it.hasta = e.hasta ?? null; // ultimo paso en que se ve (paneles y focos que se relevan)
    it.p = 0;
    it.objetivo = 0;
    it.espera = 0;
    (porPaso[it.paso] = porPaso[it.paso] || []).push(it);
    maxPaso = Math.max(maxPaso, it.paso);
    propios.push(it);
    items.push(it);
  }
  for (const lista of Object.values(porPaso)) lista.forEach((it, k) => (it.retardo = k * 0.08));
  return { cfg: d, maxPaso, items: propios };
});

// ---------- Estado y navegacion ----------
const progreso = document.getElementById("progreso");
diapositivas.forEach((_, i) => {
  const punto = document.createElement("i");
  punto.addEventListener("click", (ev) => {
    ev.stopPropagation();
    ir(i, 0);
  });
  progreso.appendChild(punto);
});

let actual = 0;
let paso = 0;
let profundidad = 0;
let niebla = 0;
let luz = 1;

function estado() {
  for (const it of items) {
    const enRango = it.i === actual && it.paso <= paso && (it.hasta === null || paso <= it.hasta);
    const visible = (it.i < actual && it.hasta === null) || enRango;
    if (visible && !it.objetivo) it.espera = it.retardo || 0;
    it.objetivo = visible ? 1 : 0;
    it.activo = enRango;
    if (it.dom) {
      const antes = it.dom.classList.contains("on");
      it.dom.classList.toggle("on", enRango);
      if (enRango && it.tipo === "cifra") contar(it);
      if (it.tipo === "chat" && antes !== enRango) animarChat(it, enRango);
    }
  }
  progreso.querySelectorAll("i").forEach((p, i) => p.classList.toggle("on", i === actual));
  history.replaceState(null, "", `#${actual + 1}`);
}

function contar(it) {
  if (it.contado) return;
  it.contado = true;
  const num = it.dom.querySelector(".num");
  const inicio = performance.now();
  (function bucle() {
    const t = Math.min((performance.now() - inicio) / 2800, 1);
    num.textContent = Math.round(it.valor * (1 - Math.pow(1 - t, 4))).toLocaleString("es-ES");
    if (t < 1) requestAnimationFrame(bucle);
  })();
}

function ir(i, p) {
  const nuevo = THREE.MathUtils.clamp(i, 0, diapositivas.length - 1);
  if (nuevo !== actual) burbujitas.rafaga(camY, 110);
  actual = nuevo;
  paso = Math.min(p, diapositivas[actual].maxPaso);
  estado();
}
const siguiente = () =>
  paso < diapositivas[actual].maxPaso ? ir(actual, paso + 1) : ir(actual + 1, 0);
const anterior = () =>
  paso > 0 ? ir(actual, paso - 1) : actual > 0 && ir(actual - 1, diapositivas[actual - 1].maxPaso);

window.addEventListener("keydown", (ev) => {
  if (["ArrowRight", "ArrowDown", "PageDown", " ", "Enter"].includes(ev.key)) {
    ev.preventDefault();
    siguiente();
  } else if (["ArrowLeft", "ArrowUp", "PageUp", "Backspace"].includes(ev.key)) {
    ev.preventDefault();
    anterior();
  } else if (ev.key === "Home") ir(0, 0);
  else if (ev.key === "End") ir(diapositivas.length - 1, 99);
  else if (ev.key.toLowerCase() === "f") {
    if (document.fullscreenElement) document.exitFullscreen();
    else document.documentElement.requestFullscreen();
  }
});
window.addEventListener("click", (ev) => (ev.clientX < window.innerWidth * 0.2 ? anterior() : siguiente()));
let toqueX = null;
window.addEventListener("touchstart", (ev) => (toqueX = ev.touches[0].clientX), { passive: true });
window.addEventListener("touchend", (ev) => {
  if (toqueX === null) return;
  const d = ev.changedTouches[0].clientX - toqueX;
  if (Math.abs(d) > 50) (d < 0 ? siguiente : anterior)();
  toqueX = null;
});

// raton: solo para ocultar el cursor cuando no se mueve (el ojo ya no lo sigue)
let temporizador;
window.addEventListener("mousemove", () => {
  document.body.classList.remove("quieto");
  clearTimeout(temporizador);
  temporizador = setTimeout(() => document.body.classList.add("quieto"), 2500);
});

// ---------- Tamano ----------
let D = D0;
let escalaTexto = 1;
function ajustar() {
  const W = window.innerWidth;
  const H = window.innerHeight;
  const aspecto = W / H;
  D = Math.max(D0, (1920 / K / 2) / (Math.tan(THREE.MathUtils.degToRad(FOV / 2)) * aspecto));
  camara.aspect = aspecto;
  camara.updateProjectionMatrix();
  renderer.setSize(W, H);
  compositor.setSize(W, H);
  final.uniforms.uRes.value.set(W, H);
  nieve.uniforms.uPx.value = H * 0.045;
  escalaTexto = (H / 1080) * (D0 / D);
  for (const it of items) {
    if (!it.dom) continue;
    it.dom.style.fontSize = `${it.tam * escalaTexto}px`;
    if (it.fijo) {
      // paneles: posicion del escenario 1920 x 1080 llevada a la pantalla (centrados en vertical)
      it.dom.style.left = `${W / 2 + (it.fijo.x - 960) * escalaTexto}px`;
      it.dom.style.top = `${H / 2 + (it.fijo.y - 540) * escalaTexto}px`;
      it.dom.style.width = `${it.fijo.ancho * escalaTexto}px`;
    }
  }
}
window.addEventListener("resize", ajustar);
ajustar();

// ---------- Bucle ----------
let camX = 0;
let camY = yDiapo(actual);
let camZ = D;
let velX = 0;
let velY = 0;
let velZ = 0;
const ojoPant = { x: null, y: null };
const vistazo = new THREE.Vector2(); // desvio de la mirada, en pixeles del escenario
const vistazoObj = new THREE.Vector2();
let proximoVistazo = 3;
let ojoEscala = 1;
const mirada = new THREE.Vector3();
const proyeccion = new THREE.Vector3();
const reloj = new THREE.Clock();
const suave = (dt, v) => 1 - Math.exp(-dt * v);
const salto = (x) => {
  const c = 1.5;
  return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2);
};

function cuadro() {
  const dt = Math.min(reloj.getDelta(), 0.05);
  const t = reloj.elapsedTime;
  const d = diapositivas[actual];

  // camara: muelle hacia la diapositiva actual y un leve balanceo
  // con un foco activo, la camara se acerca a esa burbuja y la deja en (sx, sy) de la pantalla
  let objX = 0;
  let objY = yDiapo(actual);
  let objZ = D;
  const foco = d.items.filter((it) => it.tipo === "foco" && it.activo).pop();
  if (foco && foco.de) {
    const B = aMundo(actual, foco.de.x, foco.de.y, foco.de.z || 0);
    objZ = D / foco.zoom;
    const k = objZ / (K * D0);
    objX = B.x - (foco.sx - 960) * k;
    objY = B.y + (foco.sy - 540) * k;
  }
  velX += ((objX - camX) * 6 - velX * 4.9) * dt;
  velY += ((objY - camY) * 7 - velY * 5.2) * dt;
  velZ += ((objZ - camZ) * 6 - velZ * 4.9) * dt;
  camX += velX * dt;
  camY += velY * dt;
  camZ += velZ * dt;
  camara.position.set(camX + Math.sin(t * 0.21) * 0.12, camY + Math.sin(t * 0.17) * 0.08, camZ);
  camara.lookAt(camX + Math.sin(t * 0.21) * 0.08, camY, camZ - D);
  camara.rotation.z = Math.sin(t * 0.13) * 0.006;

  // agua, niebla y luz segun la diapositiva y el paso
  profundidad += (d.cfg.profundidad - profundidad) * suave(dt, 1.2);
  const hayNiebla = d.items.some((it) => it.tipo === "niebla" && it.objetivo);
  const tieneLuz = d.items.find((it) => it.tipo === "luz");
  niebla += ((hayNiebla ? 1 : 0) - niebla) * suave(dt, 1.4);
  luz += ((tieneLuz && !tieneLuz.objetivo ? 0.18 : 1) - luz) * suave(dt, 1.6);
  Agua.colorProfundidad(profundidad, colorAgua);
  colorAgua.multiplyScalar(0.45 + 0.55 * luz);
  escena.fog.density = 0.013 + 0.012 * profundidad + niebla * 0.085;
  U.uFogDensity.value = escena.fog.density;
  U.uLuz.value = luz;
  U.uT.value = t;
  escena.environmentIntensity = 0.25 + 0.75 * luz;
  cielo.intensity = 1.1 * luz * (1.1 - profundidad * 0.5);
  sol.intensity = 2.6 * luz * (1 - profundidad * 0.6);
  sol.position.set(4, camY + 20, 10);
  sol.target.position.set(0, camY, 0);
  final.uniforms.uT.value = t;
  final.uniforms.uNiebla.value = niebla;

  rayos.uniforms.uT.value = t;
  rayos.uniforms.uI.value = (0.02 + 0.11 * Math.pow(1 - profundidad, 1.5)) * luz;
  rayos.grupo.position.set(0, camY + 6, 0);
  superficie.uniforms.uT.value = t;
  superficie.uniforms.uCam.value.copy(camara.position);
  nieve.uniforms.uT.value = t;
  nieve.uniforms.uCam.value.copy(camara.position);
  nieve.uniforms.uI.value = 0.6 + 0.4 * luz;
  burbujitas.uniforms.uI.value = 0.5 + 0.5 * luz;
  burbujitas.actualizar(dt, t, camY);

  // elementos: aparecen con un pequeño rebote; las burbujas se llenan
  for (const it of items) {
    if (it.objetivo && it.espera > 0) it.espera -= dt;
    else it.p = THREE.MathUtils.clamp(it.p + (it.objetivo ? dt * 0.9 : -dt * 1.8), 0, 1);
    const cerca = Math.abs(yDiapo(it.i) - camY) < 26;
    if (it.cont) {
      const s = it.objetivo ? salto(it.p) : it.p * it.p;
      it.grupo.visible = cerca && it.p > 0.001;
      it.cont.scale.setScalar(Math.max(s, 0.0001));
      it.cont.position.y = Math.sin(t * 0.6 + it.R * 7 + it.i) * 0.07;
      if (it.tipo === "burbuja") it.cont.rotation.y = t * 0.05; // las capturas siempre de frente
    }
    if (it.tipo === "burbuja") {
      const meta = it.objetivo ? -1 + 2 * it.llenado : -1.05;
      it.nivel += (meta - it.nivel) * suave(dt, it.objetivo ? 0.9 : 3);
      it.mLiq.uniforms.uNivel.value = it.nivel;
      const r = Math.sqrt(Math.max(0, 1 - it.nivel * it.nivel)) * it.R * 0.955;
      it.tapa.visible = r > 0.002 && it.nivel < 0.99;
      it.tapa.position.y = it.nivel * it.R * 0.955;
      it.tapa.scale.set(r, 1, r);
    } else if (it.tipo === "enlace") {
      it.malla.visible = cerca && it.p > 0;
      it.malla.material.uniforms.uProg.value = it.objetivo ? Math.min(it.p * 1.4, 1) : it.p;
    } else if (it.tipo === "luz") {
      it.int += ((it.objetivo ? 1 : 0) - it.int) * suave(dt, 2);
      it.uniforms.uI.value = it.int;
      it.foco.intensity = it.int * 260;
      it.cono.visible = it.int > 0.01;
    }
    if (it.dom && it.ancla) {
      proyeccion.copy(it.ancla);
      if (it.cont) proyeccion.y += it.cont.position.y;
      const centro = proyeccion.clone();
      proyeccion.project(camara);
      const x = (proyeccion.x * 0.5 + 0.5) * window.innerWidth;
      let y = (-proyeccion.y * 0.5 + 0.5) * window.innerHeight;
      if (it.bajo && it.R) {
        // radio de la burbuja en pantalla, para poner la etiqueta justo debajo
        const borde = centro.add(new THREE.Vector3(0, -it.R * it.cont.scale.x, 0)).project(camara);
        y = (-borde.y * 0.5 + 0.5) * window.innerHeight + it.tam * escalaTexto * 1.3;
      }
      if (it.tipo === "burbuja" || it.tipo === "captura") {
        it.dom.classList.toggle("tenue", Boolean(foco && foco.de && foco.de !== it.e));
      }
      it.dom.style.transform = `translate(${x}px, ${y}px) translate(-50%, -50%)`;
    }
  }

  // el ojo viaja con la camara y mira a donde dice la diapositiva (o al cursor)
  const o = d.cfg.ojo;
  // el ojo va a una distancia fija delante de la camara: siempre en su sitio de la pantalla
  const dist = D0 - Z_OJO;
  const radio = o.escala * 0.8 * (dist / D0);
  if (ojoPant.x === null) Object.assign(ojoPant, { x: o.x, y: o.y });
  ojoPant.x += (o.x - ojoPant.x) * suave(dt, 2.4);
  ojoPant.y += (o.y - ojoPant.y) * suave(dt, 2.4);
  ojoEscala += (radio - ojoEscala) * suave(dt, 2.4);
  const u = dist / (D0 * K);
  ojo.grupo.position.set(
    camX + (ojoPant.x - 960) * u,
    camY - (ojoPant.y - 540) * u + Math.sin(t * 0.8) * 0.06,
    camZ - dist,
  );
  ojo.grupo.scale.setScalar(ojoEscala);
  if (t > proximoVistazo) {
    // la mitad de las veces vuelve al centro; si no, echa un vistazo a un lado
    if (Math.random() < 0.5) vistazoObj.set(0, 0);
    else vistazoObj.set((Math.random() < 0.5 ? -1 : 1) * (260 + Math.random() * 420), (Math.random() - 0.5) * 420);
    proximoVistazo = t + 2.2 + Math.random() * 3.2;
  }
  vistazo.lerp(vistazoObj, suave(dt, 2.6));
  mirada
    .set(camX + (o.mira.x + vistazo.x - 960) * u * 2, camY - (o.mira.y + vistazo.y - 540) * u * 2, camZ - dist * 0.2)
    .lerp(camara.position, 0.35);
  ojo.dilatar(niebla > 0.5 ? 1.35 : tieneLuz && tieneLuz.objetivo ? 0.75 : 1);
  ojo.actualizar(dt, mirada);

  compositor.render(dt);
  requestAnimationFrame(cuadro);
}

// ---------- Arranque ----------
const inicial = Number(location.hash.slice(1)) - 1;
actual = Number.isInteger(inicial) && inicial >= 0 && inicial < diapositivas.length ? inicial : 0;
camY = yDiapo(actual);
camZ = D;
estado();
requestAnimationFrame(cuadro);
setTimeout(() => document.getElementById("cortina").classList.add("fuera"), 400);
setTimeout(() => document.getElementById("ayuda").classList.add("oculta"), 5000);

// acceso para depurar desde la consola
window.__oc = { escena, brillo, final, VIDRIO, items, compositor };
