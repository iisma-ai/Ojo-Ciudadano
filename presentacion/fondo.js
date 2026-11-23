/* Fondo submarino: agua que se oscurece al bajar, rayos de luz, particulas y burbujas que suben. */
(function () {
  const lienzo = document.getElementById("fondo");
  const g = lienzo.getContext("2d");
  let W = 0;
  let H = 0;

  // Color de arriba y de abajo del agua segun la profundidad (0 superficie, 1 fondo)
  const ARRIBA = [[56, 200, 222], [30, 138, 186], [14, 78, 128], [10, 44, 84], [6, 22, 52]];
  const ABAJO = [[22, 124, 166], [13, 88, 134], [9, 52, 98], [6, 28, 64], [4, 13, 32]];

  let prof = 0;
  let profObjetivo = 0;
  const rayos = Array.from({ length: 9 }, (_, i) => ({
    x: (i + 0.5) / 9 + (Math.random() - 0.5) * 0.08,
    ancho: 0.04 + Math.random() * 0.07,
    inclin: -0.25 + Math.random() * 0.12,
    vel: 0.15 + Math.random() * 0.3,
    fase: Math.random() * 6.28,
  }));
  const motas = Array.from({ length: 150 }, () => nuevaMota(true));
  const burbujas = [];

  function mezcla(paleta, p) {
    const t = Math.min(Math.max(p, 0), 1) * (paleta.length - 1);
    const i = Math.min(Math.floor(t), paleta.length - 2);
    const f = t - i;
    return paleta[i].map((v, k) => Math.round(v + (paleta[i + 1][k] - v) * f));
  }

  function nuevaMota(inicial) {
    return {
      x: Math.random(),
      y: inicial ? Math.random() : 1.02,
      r: 0.6 + Math.random() * 1.8,
      vy: -0.004 - Math.random() * 0.012,
      vx: (Math.random() - 0.5) * 0.004,
      a: 0.15 + Math.random() * 0.45,
    };
  }

  function nuevaBurbuja(rapida) {
    return {
      x: Math.random() * W,
      y: H + 30,
      r: 3 + Math.random() * (rapida ? 22 : 14),
      vy: (rapida ? 140 : 40) + Math.random() * (rapida ? 220 : 70),
      fase: Math.random() * 6.28,
      bal: 8 + Math.random() * 22,
    };
  }

  function ajustar() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = window.innerWidth;
    H = window.innerHeight;
    lienzo.width = W * dpr;
    lienzo.height = H * dpr;
    lienzo.style.width = `${W}px`;
    lienzo.style.height = `${H}px`;
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function dibujar(t, dt) {
    prof += (profObjetivo - prof) * Math.min(1, dt * 1.6);
    const a = mezcla(ARRIBA, prof);
    const b = mezcla(ABAJO, prof);
    const fondo = g.createLinearGradient(0, 0, 0, H);
    fondo.addColorStop(0, `rgb(${a})`);
    fondo.addColorStop(1, `rgb(${b})`);
    g.globalCompositeOperation = "source-over";
    g.fillStyle = fondo;
    g.fillRect(0, 0, W, H);

    // rayos de luz que se apagan al bajar
    g.globalCompositeOperation = "lighter";
    const intensidad = 0.02 + 0.13 * Math.pow(1 - prof, 1.6);
    for (const r of rayos) {
      const balanceo = Math.sin(t * r.vel + r.fase) * 0.03;
      const x0 = (r.x + balanceo) * W;
      const w = r.ancho * W;
      const dx = r.inclin * H;
      const grad = g.createLinearGradient(0, 0, 0, H);
      grad.addColorStop(0, `rgba(190,245,255,${intensidad * 1.6})`);
      grad.addColorStop(0.55, `rgba(150,225,255,${intensidad * 0.5})`);
      grad.addColorStop(1, "rgba(150,225,255,0)");
      g.fillStyle = grad;
      g.beginPath();
      g.moveTo(x0 - w * 0.2, 0);
      g.lineTo(x0 + w * 0.2, 0);
      g.lineTo(x0 + w + dx, H);
      g.lineTo(x0 - w + dx, H);
      g.closePath();
      g.fill();
    }

    // particulas en suspension
    for (const m of motas) {
      m.x += m.vx * dt;
      m.y += m.vy * dt;
      if (m.y < -0.02) Object.assign(m, nuevaMota(false));
      g.fillStyle = `rgba(210,240,255,${m.a * (0.35 + 0.4 * prof)})`;
      g.beginPath();
      g.arc(m.x * W, m.y * H, m.r, 0, 6.283);
      g.fill();
    }

    // burbujas que suben
    g.globalCompositeOperation = "source-over";
    if (Math.random() < dt * 1.4) burbujas.push(nuevaBurbuja(false));
    for (let i = burbujas.length - 1; i >= 0; i--) {
      const u = burbujas[i];
      u.y -= u.vy * dt;
      const x = u.x + Math.sin(t * 1.3 + u.fase) * u.bal;
      if (u.y < -40) {
        burbujas.splice(i, 1);
        continue;
      }
      const rel = g.createRadialGradient(x - u.r * 0.35, u.y - u.r * 0.35, u.r * 0.1, x, u.y, u.r);
      rel.addColorStop(0, "rgba(255,255,255,0.28)");
      rel.addColorStop(0.7, "rgba(190,235,255,0.06)");
      rel.addColorStop(1, "rgba(220,245,255,0.45)");
      g.fillStyle = rel;
      g.beginPath();
      g.arc(x, u.y, u.r, 0, 6.283);
      g.fill();
      g.strokeStyle = "rgba(230,250,255,0.35)";
      g.lineWidth = 1;
      g.stroke();
    }

    // viñeta: oscurece los bordes
    const vig = g.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 0.95);
    vig.addColorStop(0, "rgba(0,8,24,0)");
    vig.addColorStop(1, `rgba(0,8,24,${0.35 + 0.25 * prof})`);
    g.fillStyle = vig;
    g.fillRect(0, 0, W, H);
  }

  let previo = performance.now();
  function bucle(ahora) {
    const dt = Math.min((ahora - previo) / 1000, 0.05);
    previo = ahora;
    dibujar(ahora / 1000, dt);
    requestAnimationFrame(bucle);
  }

  window.Fondo = {
    setProfundidad(p) {
      profObjetivo = p;
    },
    rafaga(n) {
      for (let i = 0; i < n; i++) setTimeout(() => burbujas.push(nuevaBurbuja(true)), i * 45);
    },
  };

  window.addEventListener("resize", ajustar);
  ajustar();
  requestAnimationFrame(bucle);
})();
