/* El ojo de cristal: una esfera de vidrio con un iris de luz dentro (anillos y fibras que giran
 * despacio) y una pupila de cristal oscuro. No imita un ojo de verdad: es un objeto, una lente.
 * Mira hacia un punto girando la esfera entera. */
import * as THREE from "three";

function lienzo(tam) {
  const c = document.createElement("canvas");
  c.width = c.height = tam;
  return [c, c.getContext("2d")];
}

function textura(c) {
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  return t;
}

// Iris de luz: fondo transparente, fibras finas y anillos. Se suma (mezcla aditiva).
function texturaIris() {
  const [c, g] = lienzo(1024);
  const C = 512;
  const halo = g.createRadialGradient(C, C, 150, C, C, 512);
  halo.addColorStop(0, "rgba(90,150,255,0.55)");
  halo.addColorStop(0.45, "rgba(40,100,230,0.35)");
  halo.addColorStop(0.8, "rgba(20,60,170,0.12)");
  halo.addColorStop(1, "rgba(0,0,0,0)");
  g.fillStyle = halo;
  g.fillRect(0, 0, 1024, 1024);
  g.globalCompositeOperation = "lighter";
  for (let i = 0; i < 900; i++) {
    const a = (i / 900) * Math.PI * 2 + Math.random() * 0.01;
    const r0 = 170 + Math.random() * 30;
    const r1 = 300 + Math.random() * 170;
    g.strokeStyle = `rgba(${120 + Math.random() * 80},${180 + Math.random() * 60},255,${0.05 + Math.random() * 0.16})`;
    g.lineWidth = 0.8 + Math.random() * 1.2;
    g.beginPath();
    g.moveTo(C + Math.cos(a) * r0, C + Math.sin(a) * r0);
    g.lineTo(C + Math.cos(a) * r1, C + Math.sin(a) * r1);
    g.stroke();
  }
  for (const [r, w, al] of [[178, 3, 0.9], [205, 1.2, 0.5], [300, 1, 0.35], [420, 2, 0.45], [470, 1, 0.25]]) {
    g.strokeStyle = `rgba(170,215,255,${al})`;
    g.lineWidth = w;
    g.beginPath();
    g.arc(C, C, r, 0, Math.PI * 2);
    g.stroke();
  }
  // marcas del anillo exterior, como una escala de lente
  for (let i = 0; i < 120; i++) {
    const a = (i / 120) * Math.PI * 2;
    const largo = i % 10 === 0 ? 22 : 9;
    g.strokeStyle = `rgba(190,225,255,${i % 10 === 0 ? 0.6 : 0.3})`;
    g.lineWidth = 1.4;
    g.beginPath();
    g.moveTo(C + Math.cos(a) * 432, C + Math.sin(a) * 432);
    g.lineTo(C + Math.cos(a) * (432 + largo), C + Math.sin(a) * (432 + largo));
    g.stroke();
  }
  return textura(c);
}

// Segunda capa, más al fondo y girando al revés: da profundidad
function texturaAnillos() {
  const [c, g] = lienzo(512);
  const C = 256;
  for (let i = 0; i < 60; i++) {
    const a0 = Math.random() * Math.PI * 2;
    const r = 120 + Math.random() * 120;
    g.strokeStyle = `rgba(110,170,255,${0.08 + Math.random() * 0.25})`;
    g.lineWidth = 1 + Math.random() * 2.5;
    g.beginPath();
    g.arc(C, C, r, a0, a0 + 0.3 + Math.random() * 1.2);
    g.stroke();
  }
  return textura(c);
}

export function crearOjo(colorAgua) {
  const grupo = new THREE.Group(); // posicion y escala
  const globo = new THREE.Group(); // giro de la mirada
  grupo.add(globo);

  // Bola de cristal maciza: el rayo entra, cruza la esfera y sale (refraccion real, con un indice
  // distinto por color: dispersion). Lo que se ve a traves es el mar alrededor: la superficie
  // luminosa sale invertida abajo y el fondo oscuro arriba, como en una bola de cristal de verdad.
  const uniformes = { uT: { value: 0 }, uAgua: { value: colorAgua || new THREE.Color("#0b2a4d") } };
  const cristal = new THREE.Mesh(
    new THREE.SphereGeometry(1, 128, 96),
    new THREE.ShaderMaterial({
      uniforms: uniformes,
      vertexShader: `varying vec3 vP; varying vec3 vN; varying vec3 vC; varying float vR;
        void main(){
          vec4 w = modelMatrix * vec4(position, 1.);
          vP = w.xyz;
          vN = normalize(mat3(modelMatrix) * normal);
          vC = (modelMatrix * vec4(0., 0., 0., 1.)).xyz;
          vR = length((modelMatrix * vec4(1., 0., 0., 0.)).xyz);
          gl_Position = projectionMatrix * viewMatrix * w;
        }`,
      fragmentShader: `uniform float uT; uniform vec3 uAgua;
        varying vec3 vP; varying vec3 vN; varying vec3 vC; varying float vR;
        vec3 mar(vec3 d){
          float y = d.y;
          vec3 hondo = uAgua * .12;
          vec3 cielo = vec3(.32, .56, 1.05);
          vec3 c = y < 0. ? mix(uAgua * .8, hondo, smoothstep(0., .6, -y)) : mix(uAgua * .9, cielo, smoothstep(.3, 1., y));
          if (y > 0.) {
            vec2 p = d.xz / (y + .2) * 2.6;
            float n = sin(p.x * 2. + uT * .7) * sin(p.y * 2.3 - uT * .55) + sin((p.x + p.y) * 1.7 + uT) * .5;
            c += vec3(.75, .9, 1.1) * smoothstep(.7, 1.4, n) * .7 * smoothstep(.3, .8, y);
            c += vec3(3.) * pow(max(y, 0.), 60.);
          }
          return c;
        }
        vec3 atraviesa(vec3 V, vec3 N, float ior){
          vec3 r = refract(V, N, 1. / ior);
          float tt = -2. * dot(vP - vC, r);
          vec3 Q = vP + r * tt;
          vec3 Nq = normalize(Q - vC);
          vec3 s = refract(r, -Nq, ior);
          if (dot(s, s) < .01) s = reflect(r, -Nq); // reflexion total interna
          return s;
        }
        void main(){
          vec3 N = normalize(vN);
          vec3 V = normalize(vP - cameraPosition);
          float cosT = clamp(dot(-V, N), 0., 1.);
          float fres = .04 + .96 * pow(1. - cosT, 5.);
          vec3 trans = vec3(mar(atraviesa(V, N, 1.47)).r, mar(atraviesa(V, N, 1.5)).g, mar(atraviesa(V, N, 1.53)).b);
          vec3 refl = reflect(V, N);
          vec3 c = mix(trans * vec3(.85, .93, 1.) * (.45 + .55 * cosT), mar(refl), fres);
          c += vec3(2.4) * pow(max(dot(refl, normalize(vec3(-.35, .8, .45))), 0.), 220.);
          c += vec3(.8, .9, 1.) * pow(max(dot(refl, normalize(vec3(.5, .3, .8))), 0.), 90.) * .5;
          gl_FragColor = vec4(c, 1.);
        }`,
    }),
  );

  // borde fino de luz para que la esfera se lea sobre el agua oscura
  const borde = new THREE.Mesh(
    new THREE.SphereGeometry(1.001, 96, 64),
    new THREE.ShaderMaterial({
      vertexShader: `varying vec3 vN; varying vec3 vV;
        void main(){ vec4 mv = modelViewMatrix * vec4(position, 1.); vN = normalize(normalMatrix * normal); vV = normalize(-mv.xyz); gl_Position = projectionMatrix * mv; }`,
      fragmentShader: `varying vec3 vN; varying vec3 vV;
        void main(){
          float f = pow(clamp(1. - abs(dot(vN, vV)), 0., 1.), 4.);
          gl_FragColor = vec4(vec3(.75, .88, 1.) * f * .45, f * .45);
        }`,
      transparent: true,
      depthWrite: false,
      depthTest: false,
      blending: THREE.AdditiveBlending,
    }),
  );
  borde.renderOrder = 18;

  const capaIris = (tex, radio, z, fuerza) => {
    const m = new THREE.Mesh(
      new THREE.CircleGeometry(radio, 96),
      new THREE.MeshBasicMaterial({
        map: tex,
        color: new THREE.Color(fuerza, fuerza, fuerza),
        transparent: true,
        depthWrite: false,
        depthTest: false, // se pinta dentro del vidrio, por encima de la refraccion
        blending: THREE.AdditiveBlending,
        toneMapped: false,
        fog: false,
      }),
    );
    m.renderOrder = 10;
    m.position.z = z;
    return m;
  };
  const iris = capaIris(texturaIris(), 0.66, 0.42, 1.25);
  const anillos = capaIris(texturaAnillos(), 0.6, 0.2, 0.9);

  // pupila: una bola de cristal oscuro dentro del iris
  const pupila = new THREE.Mesh(
    new THREE.SphereGeometry(0.17, 48, 32),
    new THREE.MeshPhysicalMaterial({
      color: 0x030b1c,
      roughness: 0.05,
      metalness: 0.3,
      clearcoat: 1,
      envMapIntensity: 1.6,
      transparent: true,
      depthTest: false,
      fog: false,
    }),
  );
  pupila.renderOrder = 12;
  pupila.position.z = 0.44;

  globo.add(cristal, anillos, iris, pupila, borde);

  const auxiliar = new THREE.Object3D();
  const deseado = new THREE.Quaternion();
  let dilatacion = 1;
  let objetivoDilatacion = 1;
  const microsacada = new THREE.Vector3();
  let proxima = 1;

  return {
    grupo,
    dilatar(v) {
      objetivoDilatacion = v;
    },
    actualizar(dt, objetivo) {
      proxima -= dt;
      if (proxima < 0) {
        microsacada.set((Math.random() - 0.5) * 0.4, (Math.random() - 0.5) * 0.25, 0);
        proxima = 1 + Math.random() * 2.5;
      }
      grupo.updateMatrixWorld();
      auxiliar.position.setFromMatrixPosition(grupo.matrixWorld);
      auxiliar.lookAt(objetivo.clone().add(microsacada));
      deseado.copy(auxiliar.quaternion);
      globo.quaternion.slerp(deseado, 1 - Math.exp(-dt * 6));
      dilatacion += (objetivoDilatacion - dilatacion) * (1 - Math.exp(-dt * 2));
      pupila.scale.setScalar(dilatacion);
      uniformes.uT.value = performance.now() / 1000;
      iris.rotation.z += dt * 0.05;
      anillos.rotation.z -= dt * 0.11;
      iris.material.color.setScalar(1.15 + Math.sin(performance.now() / 1300) * 0.1);
    },
  };
}
