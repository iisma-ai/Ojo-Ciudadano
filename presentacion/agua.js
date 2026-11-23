/* El mar: color de profundidad, reflejos del entorno, rayos de luz, superficie vista desde abajo,
 * particulas en suspension, burbujas que suben y el acabado de camara (posproceso). */
import * as THREE from "three";

// Color del agua de la superficie al fondo
const PALETA = ["#2b9bb0", "#15728f", "#0b4b6b", "#06304d", "#021526"].map((c) => new THREE.Color(c));

export function colorProfundidad(p, destino) {
  const t = THREE.MathUtils.clamp(p, 0, 1) * (PALETA.length - 1);
  const i = Math.min(Math.floor(t), PALETA.length - 2);
  return destino.copy(PALETA[i]).lerp(PALETA[i + 1], t - i);
}

// Entorno para los reflejos: luz arriba (la superficie), azul en el horizonte, oscuro abajo
export function entorno(renderer) {
  const s = new THREE.Scene();
  s.add(
    new THREE.Mesh(
      new THREE.SphereGeometry(50, 64, 32),
      new THREE.ShaderMaterial({
        side: THREE.BackSide,
        vertexShader: `varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.); }`,
        fragmentShader: `varying vec3 vP;
          void main(){
            float y = vP.y;
            vec3 hondo = vec3(.004,.025,.05), medio = vec3(.03,.2,.3), alto = vec3(.55,.9,1.);
            vec3 c = y < 0. ? mix(medio, hondo, -y) : mix(medio, alto, pow(y, 1.6));
            float celdas = pow(abs(sin(vP.x * 18.) * sin(vP.z * 18.)), 6.) * smoothstep(.35, .95, y);
            c += celdas * .15;
            gl_FragColor = vec4(c, 1.);
          }`,
      }),
    ),
  );
  // manchas de luz suaves (sol filtrado por la superficie): brillos redondeados en el cristal
  const brillo = new THREE.ShaderMaterial({
    side: THREE.DoubleSide,
    vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.); }`,
    fragmentShader: `varying vec2 vUv; void main(){ float d = length(vUv - .5) * 2.; gl_FragColor = vec4(vec3(2.6, 3., 3.2) * pow(clamp(1. - d, 0., 1.), 2.), 1.); }`,
  });
  for (const [x, y, z, w] of [[-14, 30, 14, 26], [18, 18, 8, 12], [0, 40, -10, 34]]) {
    const mancha = new THREE.Mesh(new THREE.PlaneGeometry(w, w * 0.6), brillo);
    mancha.position.set(x, y, z);
    mancha.lookAt(0, 0, 0);
    s.add(mancha);
  }
  const pm = new THREE.PMREMGenerator(renderer);
  const textura = pm.fromScene(s, 0.015).texture;
  pm.dispose();
  return textura;
}

const VS_SIMPLE = `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.); }`;

// Rayos de sol que bajan desde la superficie; se apagan al bajar
export function crearRayos() {
  const grupo = new THREE.Group();
  const comunes = { uT: { value: 0 }, uI: { value: 0.3 } };
  const geo = new THREE.PlaneGeometry(1, 1);
  for (let i = 0; i < 11; i++) {
    const m = new THREE.Mesh(
      geo,
      new THREE.ShaderMaterial({
        uniforms: { ...comunes, uS: { value: Math.random() } },
        vertexShader: VS_SIMPLE,
        fragmentShader: `varying vec2 vUv; uniform float uT, uI, uS;
          void main(){
            float borde = pow(sin(3.14159 * vUv.x), 2.);
            float alto = pow(smoothstep(0., 1., vUv.y), 1.8);
            float parpadeo = .55 + .45 * sin(uT * (.4 + uS * .5) + uS * 30. + vUv.x * 5.);
            float a = borde * alto * parpadeo * uI;
            gl_FragColor = vec4(vec3(.7, .95, 1.) * a, a);
          }`,
        transparent: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
      }),
    );
    m.scale.set(1 + Math.random() * 3.2, 46, 1);
    m.position.set(-24 + (48 * (i + Math.random() * 0.6)) / 11, 0, -8 - Math.random() * 26);
    m.rotation.z = -0.22 + Math.random() * 0.1;
    grupo.add(m);
  }
  return { grupo, uniforms: comunes };
}

// La superficie del mar vista desde abajo
export function crearSuperficie(altura) {
  const geo = new THREE.PlaneGeometry(700, 700, 1, 1);
  geo.rotateX(Math.PI / 2);
  const uniforms = { uT: { value: 0 }, uCam: { value: new THREE.Vector3() }, uI: { value: 1 } };
  const m = new THREE.Mesh(
    geo,
    new THREE.ShaderMaterial({
      uniforms,
      vertexShader: `varying vec3 vW; void main(){ vec4 w = modelMatrix * vec4(position, 1.); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }`,
      fragmentShader: `varying vec3 vW; uniform float uT, uI; uniform vec3 uCam;
        float ola(vec2 p){
          return sin(p.x * .9 + uT * .8) * .5 + sin(p.y * 1.3 - uT * .6) * .5
               + sin((p.x + p.y) * .7 + uT * 1.1) * .5 + sin(length(p) * 1.6 - uT * 1.3) * .3;
        }
        void main(){
          vec2 p = vW.xz;
          float n = ola(p) + ola(p * 2.7 + 7.) * .45 + ola(p * 6.1 - 3.) * .2;
          float d = length(vW.xz - uCam.xz);
          vec3 c = mix(vec3(1.5, 1.9, 1.95), vec3(.12, .5, .6), smoothstep(3., 60., d));
          c *= .6 + .22 * n;
          c += pow(max(n, 0.), 6.) * .25 * (1. - smoothstep(5., 40., d));
          float a = (1. - smoothstep(30., 160., d)) * uI;
          gl_FragColor = vec4(c * a, a);
        }`,
      transparent: true,
      depthWrite: false,
      side: THREE.DoubleSide,
    }),
  );
  m.position.y = altura;
  return { malla: m, uniforms };
}

// Particulas en suspension (nieve marina) en un volumen infinito alrededor de la camara
export function crearNieve() {
  const N = 2400;
  const pos = new Float32Array(N * 3);
  const r = new Float32Array(N);
  for (let i = 0; i < N; i++) {
    pos[i * 3] = (Math.random() - 0.5) * 44;
    pos[i * 3 + 1] = (Math.random() - 0.5) * 26;
    pos[i * 3 + 2] = -28 + Math.random() * 36;
    r[i] = Math.random();
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  geo.setAttribute("aR", new THREE.BufferAttribute(r, 1));
  const uniforms = { uT: { value: 0 }, uCam: { value: new THREE.Vector3() }, uPx: { value: 20 }, uI: { value: 1 } };
  const puntos = new THREE.Points(
    geo,
    new THREE.ShaderMaterial({
      uniforms,
      vertexShader: `uniform vec3 uCam; uniform float uT, uPx; attribute float aR; varying float vA;
        void main(){
          vec3 p = position;
          p.y += uT * (.04 + aR * .07);
          p.x += sin(uT * .3 + aR * 20.) * .35;
          vec3 caja = vec3(44., 26., 36.);
          vec3 c = uCam + vec3(0., 0., -10.);
          p = mod(p - c + caja * .5, caja) - caja * .5 + c;
          vec4 mv = modelViewMatrix * vec4(p, 1.);
          gl_PointSize = (1.2 + aR * aR * 4.) * uPx / -mv.z;
          vA = (.2 + .55 * aR) * smoothstep(42., 6., -mv.z) * smoothstep(.5, 3., -mv.z);
          gl_Position = projectionMatrix * mv;
        }`,
      fragmentShader: `varying float vA; uniform float uI;
        void main(){
          float a = smoothstep(.5, 0., length(gl_PointCoord - .5)) * vA * uI;
          gl_FragColor = vec4(vec3(.78, .92, 1.) * a, a);
        }`,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    }),
  );
  puntos.frustumCulled = false;
  return { puntos, uniforms };
}

// Burbujas de aire que suben (plateadas por el borde, como en el agua de verdad)
export function crearBurbujitas() {
  const N = 260;
  const uniforms = { uI: { value: 1 } };
  const malla = new THREE.InstancedMesh(
    new THREE.SphereGeometry(1, 20, 14),
    new THREE.ShaderMaterial({
      uniforms,
      vertexShader: `varying vec3 vN; varying vec3 vV;
        void main(){
          vec4 mv = modelViewMatrix * instanceMatrix * vec4(position, 1.);
          vN = normalize(normalMatrix * mat3(instanceMatrix) * normal);
          vV = normalize(-mv.xyz);
          gl_Position = projectionMatrix * mv;
        }`,
      fragmentShader: `varying vec3 vN; varying vec3 vV; uniform float uI;
        void main(){
          float f = 1. - max(dot(vN, vV), 0.);
          float borde = pow(f, 2.4);
          float brillo = pow(max(dot(vN, normalize(vec3(-.4, .65, .65))), 0.), 50.);
          float a = clamp(borde * .9 + brillo, 0., 1.) * uI;
          gl_FragColor = vec4(mix(vec3(.62, .86, 1.), vec3(1.6), brillo), a);
        }`,
      transparent: true,
      depthWrite: false,
    }),
    N,
  );
  malla.frustumCulled = false;
  const d = Array.from({ length: N }, () => ({ x: 0, y: 0, z: 0, r: 0, v: 0, f: Math.random() * 6.28, extra: 0 }));
  const m = new THREE.Matrix4();
  const q = new THREE.Quaternion();
  const s = new THREE.Vector3();
  const p = new THREE.Vector3();

  function nacer(b, camY, abajo) {
    b.x = (Math.random() - 0.5) * 34;
    b.z = -18 + Math.random() * 24;
    b.y = abajo ? camY - 11 - Math.random() * 4 : camY + (Math.random() - 0.5) * 22;
    b.r = 0.015 + Math.pow(Math.random(), 3) * 0.12;
    b.v = 0.7 + Math.random() * 1.2 + b.r * 6;
  }
  let iniciado = false;
  return {
    malla,
    uniforms,
    rafaga(camY, n = 90) {
      for (let i = 0; i < n; i++) {
        const b = d[Math.floor(Math.random() * N)];
        nacer(b, camY, true);
        b.extra = 4 + Math.random() * 6;
      }
    },
    actualizar(dt, t, camY) {
      for (let i = 0; i < N; i++) {
        const b = d[i];
        if (!iniciado) nacer(b, camY, false);
        b.extra *= Math.exp(-dt * 0.9);
        b.y += b.v * (1 + b.extra) * dt;
        if (b.y > camY + 12 || b.y < camY - 17) nacer(b, camY, true);
        p.set(b.x + Math.sin(t * 2.1 + b.f) * b.r * 2.5, b.y, b.z);
        s.set(b.r, b.r * (0.9 + 0.08 * Math.sin(t * 9 + b.f)), b.r);
        m.compose(p, q, s);
        malla.setMatrixAt(i, m);
      }
      iniciado = true;
      malla.instanceMatrix.needsUpdate = true;
    },
  };
}

// Acabado de camara: ondulacion del agua, aberracion cromatica, niebla, viñeta y grano
export const PasoFinal = {
  uniforms: {
    tDiffuse: { value: null },
    uT: { value: 0 },
    uNiebla: { value: 0 },
    uRes: { value: new THREE.Vector2(1, 1) },
  },
  vertexShader: VS_SIMPLE,
  fragmentShader: `uniform sampler2D tDiffuse; uniform float uT, uNiebla; uniform vec2 uRes; varying vec2 vUv;
    float azar(vec2 p){ return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
    void main(){
      vec2 uv = vUv + vec2(sin(vUv.y * 22. + uT * 1.1), cos(vUv.x * 17. + uT * .9)) * .0008;
      vec2 d = uv - .5;
      float ca = .0015 + .004 * dot(d, d);
      vec3 c = vec3(texture2D(tDiffuse, uv + d * ca).r, texture2D(tDiffuse, uv).g, texture2D(tDiffuse, uv - d * ca).b);
      float l = dot(c, vec3(.299, .587, .114));
      c = mix(c, vec3(l) * vec3(.5, .68, .8), uNiebla * .6);
      c *= mix(.3, 1., smoothstep(1.08, .28, length(d * vec2(1.2, 1.))));
      c += (azar(uv * uRes + fract(uT) * 91.) - .5) * .04;
      gl_FragColor = vec4(c, 1.);
    }`,
};
