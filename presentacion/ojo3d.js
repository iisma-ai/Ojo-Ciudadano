/* El ojo: un globo ocular en 3D con esclera, iris de fibras, pupila que se dilata y cornea
 * transparente que refleja la luz. Mira hacia un punto girando el globo entero. */
import * as THREE from "three";

const AGUJERO = 0.55; // radio del hueco del iris en la esclera (globo de radio 1)
const Z_IRIS = 0.8;

function lienzo(tam) {
  const c = document.createElement("canvas");
  c.width = c.height = tam;
  return [c, c.getContext("2d")];
}

function texturaIris() {
  const [c, g] = lienzo(1024);
  const C = 512;
  const R = 512;
  const base = g.createRadialGradient(C, C, 0, C, C, R);
  base.addColorStop(0, "#000");
  base.addColorStop(0.33, "#2a1c08");
  base.addColorStop(0.38, "#9c7432");
  base.addColorStop(0.47, "#4f7fc9");
  base.addColorStop(0.56, "#2c6bd6");
  base.addColorStop(0.8, "#1a4aa0");
  base.addColorStop(0.93, "#0e2a63");
  base.addColorStop(1, "#040b1e");
  g.fillStyle = base;
  g.fillRect(0, 0, 1024, 1024);

  // fibras radiales
  const tonos = [[170, 210, 255], [95, 150, 240], [230, 240, 255], [20, 50, 120], [60, 110, 210]];
  for (let i = 0; i < 2600; i++) {
    const a = Math.random() * Math.PI * 2;
    const r0 = R * (0.35 + Math.random() * 0.12);
    const r1 = R * (0.55 + Math.random() * 0.42);
    const da = (Math.random() - 0.5) * 0.08;
    const t = r0 < R * 0.4 && Math.random() < 0.35 ? [215, 165, 80] : tonos[Math.floor(Math.random() * tonos.length)];
    g.strokeStyle = `rgba(${t},${0.05 + Math.random() * 0.22})`;
    g.lineWidth = 0.6 + Math.random() * 2;
    g.beginPath();
    g.moveTo(C + Math.cos(a) * r0, C + Math.sin(a) * r0);
    const rm = (r0 + r1) / 2;
    g.quadraticCurveTo(C + Math.cos(a + da) * rm, C + Math.sin(a + da) * rm, C + Math.cos(a) * r1, C + Math.sin(a) * r1);
    g.stroke();
  }
  // criptas
  for (let i = 0; i < 140; i++) {
    const a = Math.random() * Math.PI * 2;
    const r = R * (0.45 + Math.random() * 0.4);
    g.save();
    g.translate(C + Math.cos(a) * r, C + Math.sin(a) * r);
    g.rotate(a);
    g.fillStyle = `rgba(4,14,40,${0.2 + Math.random() * 0.3})`;
    g.beginPath();
    g.ellipse(0, 0, 6 + Math.random() * 16, 2 + Math.random() * 5, 0, 0, Math.PI * 2);
    g.fill();
    g.restore();
  }
  // collarete
  for (let i = 0; i < 500; i++) {
    const a = Math.random() * Math.PI * 2;
    const r = R * (0.48 + (Math.random() - 0.5) * 0.05);
    g.fillStyle = `rgba(200,225,255,${Math.random() * 0.25})`;
    g.fillRect(C + Math.cos(a) * r, C + Math.sin(a) * r, 3, 3);
  }
  // anillo limbal
  const limbo = g.createRadialGradient(C, C, R * 0.84, C, C, R);
  limbo.addColorStop(0, "rgba(2,8,25,0)");
  limbo.addColorStop(1, "rgba(2,8,25,0.95)");
  g.fillStyle = limbo;
  g.fillRect(0, 0, 1024, 1024);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 8;
  return tex;
}

function texturaEsclera() {
  const [c, g] = lienzo(1024);
  const C = 512;
  g.fillStyle = "#f3efe8";
  g.fillRect(0, 0, 1024, 1024);
  const sombra = g.createRadialGradient(C, C, 300, C, C, 512);
  sombra.addColorStop(0, "rgba(220,190,180,0)");
  sombra.addColorStop(1, "rgba(200,160,150,0.6)");
  g.fillStyle = sombra;
  g.fillRect(0, 0, 1024, 1024);
  // venitas desde el borde hacia el iris
  for (let i = 0; i < 46; i++) {
    let a = Math.random() * Math.PI * 2;
    let r = 500;
    let ancho = 1.8;
    g.strokeStyle = `rgba(170,45,45,${0.12 + Math.random() * 0.25})`;
    g.beginPath();
    g.moveTo(C + Math.cos(a) * r, C + Math.sin(a) * r);
    const fin = 320 + Math.random() * 120;
    while (r > fin) {
      r -= 6;
      a += (Math.random() - 0.5) * 0.05;
      g.lineTo(C + Math.cos(a) * r, C + Math.sin(a) * r);
    }
    g.lineWidth = ancho;
    g.stroke();
    ancho *= 0.7;
  }
  // transicion al iris y hueco
  const borde = g.createRadialGradient(C, C, AGUJERO * 512, C, C, AGUJERO * 512 + 50);
  borde.addColorStop(0, "rgba(70,85,110,0.55)");
  borde.addColorStop(1, "rgba(70,85,110,0)");
  g.fillStyle = borde;
  g.fillRect(0, 0, 1024, 1024);
  g.globalCompositeOperation = "destination-out";
  g.beginPath();
  g.arc(C, C, AGUJERO * 512, 0, Math.PI * 2);
  g.fill();
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 8;
  return tex;
}

export function crearOjo() {
  const grupo = new THREE.Group(); // posicion y escala
  const globo = new THREE.Group(); // giro de la mirada
  grupo.add(globo);

  // esclera con proyeccion plana desde delante (el iris queda en el centro)
  const geo = new THREE.SphereGeometry(1, 128, 96);
  const pos = geo.attributes.position;
  const uv = geo.attributes.uv;
  for (let i = 0; i < pos.count; i++) {
    const z = pos.getZ(i);
    if (z > 0) uv.setXY(i, 0.5 + pos.getX(i) * 0.5, 0.5 + pos.getY(i) * 0.5);
    else uv.setXY(i, 0.01, 0.01);
  }
  const esclera = new THREE.Mesh(
    geo,
    new THREE.MeshPhysicalMaterial({
      map: texturaEsclera(),
      alphaTest: 0.5,
      roughness: 0.35,
      clearcoat: 0.6,
      clearcoatRoughness: 0.12,
    }),
  );

  const iris = new THREE.Mesh(
    new THREE.CircleGeometry(AGUJERO + 0.03, 96),
    new THREE.MeshStandardMaterial({ roughness: 0.55, emissive: 0xffffff, emissiveIntensity: 0.22 }),
  );
  const texIris = texturaIris();
  iris.material.map = texIris;
  iris.material.emissiveMap = texIris;
  iris.position.z = Z_IRIS;

  const pupila = new THREE.Mesh(
    new THREE.CircleGeometry(0.2, 64),
    new THREE.MeshPhysicalMaterial({ color: 0x010204, roughness: 0.15, clearcoat: 1 }),
  );
  pupila.position.z = Z_IRIS + 0.004;

  // cornea: casquete transparente que sobresale
  const Rc = 0.7;
  const tita = Math.asin(AGUJERO / Rc + 0.02);
  const geoCornea = new THREE.SphereGeometry(Rc, 96, 48, 0, Math.PI * 2, 0, tita);
  geoCornea.rotateX(Math.PI / 2);
  geoCornea.translate(0, 0, Math.sqrt(1 - AGUJERO * AGUJERO) - Rc * Math.cos(tita) + 0.005);
  const cornea = new THREE.Mesh(
    geoCornea,
    // como el cristal de las burbujas: solo suma sus reflejos, asi la pupila queda negra
    new THREE.MeshPhysicalMaterial({
      color: 0x000000,
      roughness: 0,
      clearcoat: 1,
      specularIntensity: 1,
      envMapIntensity: 1.6,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      fog: false,
    }),
  );

  globo.add(esclera, iris, pupila, cornea);

  const auxiliar = new THREE.Object3D();
  const deseado = new THREE.Quaternion();
  let dilatacion = 1;
  let objetivoDilatacion = 1;
  let microsacada = new THREE.Vector3();
  let proxima = 1;

  return {
    grupo,
    dilatar(v) {
      objetivoDilatacion = v;
    },
    actualizar(dt, objetivo) {
      proxima -= dt;
      if (proxima < 0) {
        microsacada.set((Math.random() - 0.5) * 0.5, (Math.random() - 0.5) * 0.3, 0);
        proxima = 0.8 + Math.random() * 2.2;
      }
      grupo.updateMatrixWorld();
      auxiliar.position.setFromMatrixPosition(grupo.matrixWorld);
      auxiliar.lookAt(objetivo.clone().add(microsacada));
      deseado.copy(auxiliar.quaternion);
      globo.quaternion.slerp(deseado, 1 - Math.exp(-dt * 7));
      dilatacion += (objetivoDilatacion - dilatacion) * (1 - Math.exp(-dt * 2));
      const latido = 1 + Math.sin(performance.now() / 900) * 0.015;
      pupila.scale.setScalar(dilatacion * latido);
    },
  };
}
