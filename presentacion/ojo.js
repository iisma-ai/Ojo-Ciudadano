/* El ojo que acompana toda la presentacion: mira, parpadea y cambia de sitio entre diapositivas. */
(function () {
  const contenedor = document.getElementById("ojo");
  const ALMENDRA = "M -120 0 C -70 -80 70 -80 120 0 C 70 80 -70 80 -120 0 Z";

  contenedor.innerHTML = `
    <svg viewBox="-150 -110 300 220" width="400" height="293" aria-label="Ojo Ciudadano">
      <defs>
        <clipPath id="ojo-recorte"><path d="${ALMENDRA}"/></clipPath>
        <radialGradient id="ojo-esclera" cx="50%" cy="42%" r="70%">
          <stop offset="0" stop-color="#ffffff"/>
          <stop offset="0.6" stop-color="#e3ecf8"/>
          <stop offset="1" stop-color="#9fb2cf"/>
        </radialGradient>
        <radialGradient id="ojo-iris" cx="50%" cy="46%" r="55%">
          <stop offset="0" stop-color="#bcdcff"/>
          <stop offset="0.45" stop-color="#3D8BFD"/>
          <stop offset="0.9" stop-color="#16408f"/>
          <stop offset="1" stop-color="#0c2a63"/>
        </radialGradient>
        <linearGradient id="ojo-sombra" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#05122e" stop-opacity="0.55"/>
          <stop offset="0.4" stop-color="#05122e" stop-opacity="0"/>
          <stop offset="0.85" stop-color="#05122e" stop-opacity="0"/>
          <stop offset="1" stop-color="#05122e" stop-opacity="0.25"/>
        </linearGradient>
        <radialGradient id="ojo-halo" cx="50%" cy="50%" r="50%">
          <stop offset="0" stop-color="#7DB3FF" stop-opacity="0.55"/>
          <stop offset="1" stop-color="#7DB3FF" stop-opacity="0"/>
        </radialGradient>
        <filter id="ojo-sombra-suelta" x="-20%" y="-20%" width="140%" height="160%">
          <feDropShadow dx="0" dy="14" stdDeviation="12" flood-color="#00112e" flood-opacity="0.55"/>
        </filter>
      </defs>
      <ellipse class="ojo-halo" cx="0" cy="0" rx="150" ry="100" fill="url(#ojo-halo)"/>
      <g id="ojo-parpado" style="transform-origin: 0 0">
        <g filter="url(#ojo-sombra-suelta)">
          <path d="${ALMENDRA}" fill="url(#ojo-esclera)"/>
        </g>
        <g clip-path="url(#ojo-recorte)">
          <g id="ojo-iris-grupo">
            <circle r="52" fill="url(#ojo-iris)"/>
            <circle r="52" fill="none" stroke="#0a2559" stroke-width="3" opacity="0.7"/>
            <circle r="23" fill="#030a1a"/>
            <circle cx="-15" cy="-19" r="10" fill="#fff" opacity="0.92"/>
            <circle cx="17" cy="14" r="4.5" fill="#fff" opacity="0.55"/>
          </g>
          <rect x="-125" y="-85" width="250" height="170" fill="url(#ojo-sombra)"/>
        </g>
        <path d="${ALMENDRA}" fill="none" stroke="#E7ECF3" stroke-width="9" stroke-linejoin="round" stroke-linecap="round"/>
      </g>
    </svg>`;

  const iris = contenedor.querySelector("#ojo-iris-grupo");
  const parpado = contenedor.querySelector("#ojo-parpado");
  let mirada = { x: 0, y: 0 };
  let actual = { x: 0, y: 0 };

  // Hacia donde mira: un punto del escenario. El ojo calcula el desvio de la pupila.
  window.Ojo = {
    ponerMirada(ojo, objetivo) {
      const dx = objetivo.x - ojo.x;
      const dy = objetivo.y - ojo.y;
      const dist = Math.hypot(dx, dy) || 1;
      const f = Math.min(1, dist / 350);
      mirada = { x: (dx / dist) * f * 40, y: (dy / dist) * f * 17 };
    },
  };

  function parpadear() {
    parpado.animate(
      [{ transform: "scaleY(1)" }, { transform: "scaleY(0.06)" }, { transform: "scaleY(1)" }],
      { duration: 220, easing: "ease-in-out" },
    );
    setTimeout(parpadear, 3200 + Math.random() * 4200);
  }
  setTimeout(parpadear, 2500);

  function animar() {
    actual.x += (mirada.x - actual.x) * 0.08;
    actual.y += (mirada.y - actual.y) * 0.08;
    iris.setAttribute("transform", `translate(${actual.x.toFixed(2)} ${actual.y.toFixed(2)})`);
    requestAnimationFrame(animar);
  }
  requestAnimationFrame(animar);
})();
