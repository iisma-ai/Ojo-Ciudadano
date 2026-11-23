/* Motor de la presentacion: construye las diapositivas a partir de diapositivas.js y las navega. */
(function () {
  const ANCHO = 1920;
  const ALTO = 1080;
  const escenario = document.getElementById("escenario");
  const contenedor = document.getElementById("diapositivas");
  const ojoEl = document.getElementById("ojo");
  const progreso = document.getElementById("progreso");

  const TONOS = {
    azul: ["#b4d3ff", "#3D8BFD", "#1b4f9e"],
    ambar: ["#ffe3a6", "#F2B544", "#a8700f"],
    agua: ["#b0f3fb", "#33bad6", "#14708f"],
  };
  let uid = 0;

  // ---------- Burbuja de cristal con agua dentro ----------
  function ondas(r) {
    const periodo = Math.max(r * 0.9, 30);
    const amp = Math.max(2.5, r * 0.045);
    const fin = 2 * r + periodo * 2;
    let d = `M ${-2 * r} 0`;
    for (let x = -2 * r; x <= fin; x += 4) {
      d += ` L ${x} ${(Math.sin((x / periodo) * 2 * Math.PI) * amp).toFixed(2)}`;
    }
    return { d: `${d} L ${fin} ${3 * r} L ${-2 * r} ${3 * r} Z`, periodo, amp };
  }

  function svgBurbuja(e) {
    const n = ++uid;
    const r = e.r;
    const p = 8;
    const [claro, medio, oscuro] = TONOS[e.tono || "agua"];
    const llenado = Math.min(Math.max(e.llenado ?? 0, 0), 1);
    const { d, periodo, amp } = ondas(r);
    const fin = llenado >= 0.99 ? -r - amp * 2 : r - 2 * r * llenado;
    return `
      <svg class="burbuja-svg" viewBox="${-r - p} ${-r - p} ${2 * r + 2 * p} ${2 * r + 2 * p}"
           width="${2 * r + 2 * p}" height="${2 * r + 2 * p}" style="--per:${periodo}px;--ini:${r + amp}px;--fin:${fin}px">
        <defs>
          <clipPath id="cp${n}"><circle r="${r - 1.5}"/></clipPath>
          <radialGradient id="vi${n}" cx="36%" cy="30%" r="80%">
            <stop offset="0" stop-color="#ffffff" stop-opacity="0.06"/>
            <stop offset="0.7" stop-color="#bfe8ff" stop-opacity="0.1"/>
            <stop offset="1" stop-color="#e6f8ff" stop-opacity="0.34"/>
          </radialGradient>
          <linearGradient id="ag${n}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="${2 * r}">
            <stop offset="0" stop-color="${claro}" stop-opacity="0.92"/>
            <stop offset="0.35" stop-color="${medio}" stop-opacity="0.95"/>
            <stop offset="1" stop-color="${oscuro}" stop-opacity="0.98"/>
          </linearGradient>
          <linearGradient id="br${n}" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stop-color="#ffffff" stop-opacity="0.85"/>
            <stop offset="0.5" stop-color="#ffffff" stop-opacity="0.12"/>
            <stop offset="1" stop-color="#ffffff" stop-opacity="0.5"/>
          </linearGradient>
        </defs>
        <circle r="${r}" fill="rgba(8,30,60,0.28)"/>
        <g clip-path="url(#cp${n})">
          <g class="nivel">
            <path class="onda onda-atras" d="${d}" fill="${medio}" opacity="0.45"/>
            <path class="onda" d="${d}" fill="url(#ag${n})"/>
          </g>
        </g>
        <circle r="${r}" fill="url(#vi${n})"/>
        <circle r="${r - 0.8}" fill="none" stroke="url(#br${n})" stroke-width="${Math.max(1.6, r * 0.03)}"/>
        <ellipse cx="${-r * 0.36}" cy="${-r * 0.55}" rx="${r * 0.3}" ry="${r * 0.13}" fill="#fff" opacity="0.6" transform="rotate(-32 ${-r * 0.36} ${-r * 0.55})"/>
        <ellipse cx="${r * 0.45}" cy="${r * 0.55}" rx="${r * 0.12}" ry="${r * 0.05}" fill="#fff" opacity="0.35" transform="rotate(-32 ${r * 0.45} ${r * 0.55})"/>
      </svg>`;
  }

  function nodoBurbuja(e) {
    const caja = document.createElement("div");
    caja.className = "burbuja";
    caja.innerHTML = svgBurbuja(e);
    if (e.etiqueta || e.valor) {
      const t = document.createElement("div");
      t.className = "burbuja-texto";
      const fuente = Math.min(Math.max(e.r * 0.2, 15), 34);
      t.style.fontSize = `${fuente}px`;
      t.style.maxWidth = `${e.r * 1.5}px`;
      t.innerHTML = (e.valor ? `<strong style="font-size:${Math.min(e.r * 0.3, 54)}px">${e.valor}</strong>` : "") +
        (e.etiqueta ? `<span>${e.etiqueta}</span>` : "");
      caja.appendChild(t);
    }
    return caja;
  }

  function nodoCaptura(e) {
    const caja = document.createElement("div");
    caja.className = "captura";
    caja.style.setProperty("--r", `${e.r}px`);
    const d = 2 * e.r;
    const medio = !e.src
      ? '<div class="captura-vacia"></div>'
      : /\.(mp4|webm)$/i.test(e.src)
        ? `<video src="${e.src}" autoplay muted loop playsinline></video>`
        : `<img src="${e.src}" alt="${e.etiqueta || ""}">`;
    caja.innerHTML = `<div class="captura-burbuja" style="width:${d}px;height:${d}px">${medio}<i class="brillo"></i></div>` +
      (e.etiqueta ? `<div class="captura-etiqueta">${e.etiqueta}</div>` : "");
    return caja;
  }

  function nodoCifra(e) {
    const caja = document.createElement("div");
    caja.className = "cifra";
    caja.innerHTML = `<div class="cifra-num" data-valor="${e.valor}">0</div><div class="cifra-texto">${e.texto || ""}</div>`;
    return caja;
  }

  // Linea de agua entre dos burbujas, de borde a borde
  function nodoEnlace(e, burbujas) {
    const a = burbujas[e.de];
    const b = burbujas[e.a];
    if (!a || !b) return null;
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    const dist = Math.hypot(dx, dy);
    const ux = dx / dist;
    const uy = dy / dist;
    const x1 = a.x + ux * (a.r + 4);
    const y1 = a.y + uy * (a.r + 4);
    const x2 = b.x - ux * (b.r + 4);
    const y2 = b.y - uy * (b.r + 4);
    const caja = document.createElement("div");
    caja.className = "enlace";
    caja.innerHTML = `<svg viewBox="0 0 ${ANCHO} ${ALTO}" width="${ANCHO}" height="${ALTO}">
      <line class="enlace-base" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" pathLength="1"/>
      <line class="enlace-flujo" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/></svg>`;
    return caja;
  }

  function nodoSimple(clase, html) {
    const caja = document.createElement("div");
    caja.className = clase;
    if (html) caja.innerHTML = html;
    return caja;
  }

  // ---------- Construccion de las diapositivas ----------
  const diapositivas = DIAPOSITIVAS.map((d) => {
    const seccion = document.createElement("section");
    seccion.className = "diapositiva";
    const burbujas = {};
    for (const e of d.elementos) if (e.tipo === "burbuja" || e.tipo === "captura") burbujas[e.id] = e;
    const porPaso = {};
    let maxPaso = 0;
    for (const e of d.elementos) {
      let nodo;
      if (e.tipo === "burbuja") nodo = nodoBurbuja(e);
      else if (e.tipo === "captura") nodo = nodoCaptura(e);
      else if (e.tipo === "cifra") nodo = nodoCifra(e);
      else if (e.tipo === "enlace") nodo = nodoEnlace(e, burbujas);
      else if (e.tipo === "niebla") nodo = nodoSimple("niebla");
      else if (e.tipo === "luz") nodo = nodoSimple("haz");
      else if (e.tipo === "texto") {
        nodo = nodoSimple(`texto ${e.clase || ""}`, e.texto);
        nodo.style.fontSize = `${e.tam || 40}px`;
      }
      if (!nodo) continue;
      nodo.classList.add("el", `tipo-${e.tipo}`);
      if (e.x !== undefined && e.tipo !== "enlace") {
        nodo.style.left = `${e.x}px`;
        nodo.style.top = `${e.y}px`;
      }
      if (e.tipo === "burbuja" || e.tipo === "captura") {
        nodo.style.setProperty("--flota", `${5 + Math.random() * 5}s`);
        nodo.style.setProperty("--desfase", `${-Math.random() * 6}s`);
      }
      nodo.dataset.paso = e.paso || 0;
      const k = e.paso || 0;
      (porPaso[k] = porPaso[k] || []).push(nodo);
      maxPaso = Math.max(maxPaso, k);
      seccion.appendChild(nodo);
    }
    // los elementos del mismo paso salen escalonados
    for (const lista of Object.values(porPaso)) {
      lista.forEach((n, i) => n.style.setProperty("--retardo", `${i * 0.09}s`));
    }
    contenedor.appendChild(seccion);
    return { cfg: d, seccion, maxPaso, contados: false };
  });

  diapositivas.forEach((_, i) => {
    const punto = document.createElement("i");
    punto.addEventListener("click", () => ir(i, 0));
    progreso.appendChild(punto);
  });

  // ---------- Estado y navegacion ----------
  let actual = -1;
  let paso = 0;
  let objetivoMirada = { x: 960, y: 540 };

  function contar(nodo) {
    const num = nodo.querySelector(".cifra-num");
    if (!num || num.dataset.hecho) return;
    num.dataset.hecho = "1";
    const total = Number(num.dataset.valor);
    const inicio = performance.now();
    const duracion = 2600;
    (function paso_() {
      const t = Math.min((performance.now() - inicio) / duracion, 1);
      const v = Math.round(total * (1 - Math.pow(1 - t, 4)));
      num.textContent = v.toLocaleString("es-ES");
      if (t < 1) requestAnimationFrame(paso_);
    })();
  }

  function pintar(rafaga) {
    const d = diapositivas[actual];
    diapositivas.forEach((s, i) => {
      s.seccion.classList.toggle("activa", i === actual);
      s.seccion.classList.toggle("antes", i < actual);
      s.seccion.classList.toggle("despues", i > actual);
    });
    for (const nodo of d.seccion.querySelectorAll(".el")) {
      const visible = Number(nodo.dataset.paso) <= paso;
      nodo.classList.toggle("visible", visible);
      if (visible && nodo.classList.contains("cifra")) contar(nodo);
    }
    const hayLuz = d.seccion.querySelector(".haz.visible");
    d.seccion.classList.toggle("iluminada", Boolean(hayLuz));
    d.seccion.classList.toggle("con-luz", Boolean(d.seccion.querySelector(".haz")));
    progreso.querySelectorAll("i").forEach((p, i) => p.classList.toggle("on", i === actual));
    if (rafaga) window.Fondo.rafaga(rafaga);
    history.replaceState(null, "", `#${actual + 1}`);
  }

  function colocarOjo() {
    const o = diapositivas[actual].cfg.ojo;
    ojoEl.style.transform = `translate(${o.x - 200}px, ${o.y - 146}px) scale(${o.escala})`;
    objetivoMirada = o.mira;
    window.Ojo.ponerMirada(o, o.mira);
    window.Fondo.setProfundidad(diapositivas[actual].cfg.profundidad);
    // el rayo de luz sale del ojo
    for (const haz of diapositivas[actual].seccion.querySelectorAll(".haz")) {
      haz.style.left = `${o.x}px`;
      haz.style.top = `${o.y}px`;
    }
  }

  function ir(i, p) {
    const nuevo = Math.min(Math.max(i, 0), diapositivas.length - 1);
    const cambia = nuevo !== actual;
    actual = nuevo;
    paso = Math.min(p, diapositivas[actual].maxPaso);
    if (cambia) colocarOjo();
    pintar(cambia ? 26 : 8);
  }

  function siguiente() {
    if (paso < diapositivas[actual].maxPaso) ir(actual, paso + 1);
    else if (actual < diapositivas.length - 1) ir(actual + 1, 0);
  }

  function anterior() {
    if (paso > 0) ir(actual, paso - 1);
    else if (actual > 0) ir(actual - 1, diapositivas[actual - 1].maxPaso);
  }

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
  window.addEventListener("click", (ev) => {
    if (ev.target.closest("#progreso")) return;
    if (ev.clientX < window.innerWidth * 0.2) anterior();
    else siguiente();
  });
  let toqueX = null;
  window.addEventListener("touchstart", (ev) => (toqueX = ev.touches[0].clientX), { passive: true });
  window.addEventListener("touchend", (ev) => {
    if (toqueX === null) return;
    const d = ev.changedTouches[0].clientX - toqueX;
    if (Math.abs(d) > 50) (d < 0 ? siguiente : anterior)();
    toqueX = null;
  });

  // ---------- Escala del escenario, mirada con el raton y cursor ----------
  let escala = 1;
  function ajustar() {
    escala = Math.min(window.innerWidth / ANCHO, window.innerHeight / ALTO);
    escenario.style.transform = `translate(-50%, -50%) scale(${escala})`;
  }
  window.addEventListener("resize", ajustar);
  ajustar();

  let ultimoMovimiento = 0;
  let temporizador;
  window.addEventListener("mousemove", (ev) => {
    document.body.classList.remove("quieto");
    clearTimeout(temporizador);
    temporizador = setTimeout(() => document.body.classList.add("quieto"), 2500);
    const caja = escenario.getBoundingClientRect();
    const punto = { x: (ev.clientX - caja.left) / escala, y: (ev.clientY - caja.top) / escala };
    const o = diapositivas[actual].cfg.ojo;
    window.Ojo.ponerMirada(o, punto);
    ultimoMovimiento = performance.now();
    // paralaje suave del mundo
    escenario.style.setProperty("--px", `${(0.5 - ev.clientX / window.innerWidth) * 14}px`);
    escenario.style.setProperty("--py", `${(0.5 - ev.clientY / window.innerHeight) * 10}px`);
  });
  setInterval(() => {
    // si el cursor lleva quieto un rato, el ojo vuelve a mirar donde dice la diapositiva
    if (performance.now() - ultimoMovimiento > 2800 && actual >= 0) {
      window.Ojo.ponerMirada(diapositivas[actual].cfg.ojo, objetivoMirada);
    }
  }, 500);

  const inicial = Number(location.hash.slice(1)) - 1;
  ir(Number.isInteger(inicial) && inicial >= 0 ? inicial : 0, 0);
  document.body.classList.add("listo");
  setTimeout(() => document.getElementById("ayuda").classList.add("oculta"), 5000);
})();
