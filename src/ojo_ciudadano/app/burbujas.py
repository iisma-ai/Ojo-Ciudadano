"""Mapa de burbujas con la estética de la presentación (D-047).

Sustituye al dibujo de `streamlit-agraph` en la forma «Burbujas» del Mapa del dinero. Es un
componente propio (`components.v2`, corre en la página, sin iframe) que dibuja en un lienzo:

- cada burbuja es de cristal (borde que se aclara, efecto Fresnel) con líquido dentro que sube
  hasta lo gastado; la superficie del líquido se ve en perspectiva (una elipse) y ondula;
- al abrir el mapa el líquido sube desde el fondo, como en la presentación;
- las burbujas flotan un poco y por las líneas suben motas de luz (el dinero que va del centro a
  cada consejería);
- al pasar el ratón sale el cuadro con el nombre y las cifras; al pulsar, devuelve su `id`.

Sin tarjeta gráfica (D-044) o con «reducir movimiento», se dibuja quieto. Las posiciones, los
tamaños y los colores se calculan aquí, con las mismas escalas que `red.mapa`.
"""

import math

import streamlit as st

from ojo_ciudadano.app import red

CSS = """
.ocb-mapa { position: relative; width: 100%; font-family: Outfit, sans-serif; }
.ocb-mapa canvas { display: block; width: 100%; height: 100%; }
.ocb-tip { position: absolute; pointer-events: none; z-index: 5; max-width: 300px;
  padding: 10px 14px; border-radius: 12px; font-size: 13px; line-height: 1.45; color: #E7ECF3;
  background: rgba(8, 30, 50, 0.94); border: 1px solid rgba(170, 225, 255, 0.22);
  box-shadow: 0 10px 30px rgba(0, 8, 22, 0.5); opacity: 0; transition: opacity .15s ease;
  white-space: pre-line; }
.ocb-tip b { display: block; font-weight: 650; margin-bottom: 2px; }
"""

JS = r"""
const TAU = Math.PI * 2;

function mezcla(hex, otro, t) {
  const a = parseInt(hex.slice(1), 16), b = parseInt(otro.slice(1), 16);
  const c = [16, 8, 0].map((s) => Math.round(((a >> s) & 255) * (1 - t) + ((b >> s) & 255) * t));
  return `rgb(${c[0]},${c[1]},${c[2]})`;
}
function rgba(hex, al) {
  const a = parseInt(hex.slice(1), 16);
  return `rgba(${(a >> 16) & 255},${(a >> 8) & 255},${a & 255},${al})`;
}

function crear(raiz) {
  const caja = document.createElement('div');
  caja.className = 'ocb-mapa';
  const lienzo = document.createElement('canvas');
  const tip = document.createElement('div');
  tip.className = 'ocb-tip';
  caja.append(lienzo, tip);
  raiz.appendChild(caja);
  const g = lienzo.getContext('2d');
  const quieto = () =>
    document.documentElement.classList.contains('oc-sin-gpu') ||
    matchMedia('(prefers-reduced-motion: reduce)').matches;

  const s = { caja, lienzo, tip, g, datos: null, nodos: [], enlaces: [], ancho: 0, alto: 0,
              inicio: performance.now(), encima: null, sel: null, avisar: null, vivo: true };

  function ajustar() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    s.ancho = caja.clientWidth;
    s.alto = caja.clientHeight;
    lienzo.width = Math.round(s.ancho * dpr);
    lienzo.height = Math.round(s.alto * dpr);
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    colocar();
    if (quieto()) dibujar(performance.now());
  }

  // escala el diseño (coordenadas de Python) para que quepa con sus etiquetas
  function colocar() {
    if (!s.datos) return;
    const ns = s.datos.nodos;
    let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
    for (const n of ns) {
      const lineas = n.lineas.length;
      x0 = Math.min(x0, n.x - n.r - 40); x1 = Math.max(x1, n.x + n.r + 40);
      y0 = Math.min(y0, n.y - n.r - 6); y1 = Math.max(y1, n.y + n.r + 16 + 15 * lineas);
    }
    const k = Math.min((s.ancho - 20) / (x1 - x0), (s.alto - 20) / (y1 - y0), 1.6);
    const ox = s.ancho / 2 - ((x0 + x1) / 2) * k, oy = s.alto / 2 - ((y0 + y1) / 2) * k;
    const previos = new Map(s.nodos.map((n) => [n.id, n]));
    s.k = k;
    s.nodos = ns.map((n, i) => ({
      ...n, px: ox + n.x * k, py: oy + n.y * k, pr: Math.max(n.r * k, 7),
      fase: (i * 2.399) % TAU, zoom: previos.get(n.id)?.zoom ?? 1,
    }));
    const porId = new Map(s.nodos.map((n) => [n.id, n]));
    s.enlaces = s.datos.enlaces
      .map(([a, b]) => [porId.get(a), porId.get(b)])
      .filter((e) => e[0] && e[1]);
  }

  function posicion(n, t, mueve) {
    if (!mueve || n.centro) return [n.px, n.py];
    return [n.px + Math.sin(t * 0.00045 + n.fase) * 2.2, n.py + Math.cos(t * 0.0006 + n.fase) * 3];
  }

  function burbuja(n, x, y, r, nivel, t, mueve) {
    const c = n.color;
    // halo suave debajo (el «bloom» de la presentación)
    let h = g.createRadialGradient(x, y + r * 0.15, r * 0.6, x, y, r * 1.55);
    h.addColorStop(0, rgba(c, n.centro ? 0.18 : 0.1));
    h.addColorStop(1, rgba(c, 0));
    g.fillStyle = h;
    g.beginPath(); g.arc(x, y, r * 1.55, 0, TAU); g.fill();

    // cristal vacío: oscuro y translúcido
    h = g.createRadialGradient(x - r * 0.2, y - r * 0.25, r * 0.1, x, y, r);
    h.addColorStop(0, 'rgba(30, 60, 90, 0.35)');
    h.addColorStop(1, 'rgba(14, 34, 58, 0.72)');
    g.fillStyle = h;
    g.beginPath(); g.arc(x, y, r, 0, TAU); g.fill();

    // líquido hasta el nivel, con la superficie ondulada
    if (nivel > 0.004) {
      const ny = y + r - 2 * r * Math.min(nivel, 0.985);
      const amp = r * 0.035 * (mueve ? 1 : 0.6);
      const fase = mueve ? t * 0.0021 + n.fase : n.fase;
      g.save();
      g.beginPath(); g.arc(x, y, r - 0.6, 0, TAU); g.clip();
      g.beginPath();
      g.moveTo(x - r, ny);
      for (let i = 0; i <= 24; i++) {
        const px = x - r + (2 * r * i) / 24;
        const ola = Math.sin(i / 3.2 + fase) * amp + Math.sin(i / 1.7 - fase * 1.3) * amp * 0.4;
        g.lineTo(px, ny + ola);
      }
      g.lineTo(x + r, y + r); g.lineTo(x - r, y + r); g.closePath();
      h = g.createLinearGradient(0, ny, 0, y + r);
      h.addColorStop(0, mezcla(c, '#5a9dff', 0.3));
      h.addColorStop(0.45, mezcla(c, '#2f74f0', 0.45));
      h.addColorStop(1, mezcla(c, '#041627', 0.62));
      g.fillStyle = h;
      g.globalAlpha = 0.92;
      g.fill();
      g.globalAlpha = 1;
      // sombra del volumen: el líquido se oscurece hacia el borde de la esfera
      h = g.createRadialGradient(x, y, r * 0.45, x, y, r);
      h.addColorStop(0, 'rgba(2, 12, 24, 0)');
      h.addColorStop(1, 'rgba(2, 12, 24, 0.55)');
      g.fillStyle = h;
      g.fill();
      // la superficie vista desde un poco arriba: una elipse clara (si no está casi llena)
      const media = Math.sqrt(Math.max(r * r - (ny - y) * (ny - y), 0));
      if (nivel < 0.97 && media > r * 0.18) {
        g.beginPath();
        g.ellipse(x, ny, media * 0.97, media * 0.16, 0, 0, TAU);
        g.fillStyle = rgba(c, 0.38);
        g.fill();
        g.lineWidth = 1;
        g.strokeStyle = 'rgba(235, 248, 255, 0.55)';
        g.stroke();
      }
      g.restore();
    }

    // luz que atraviesa la burbuja y sale por abajo
    h = g.createRadialGradient(x, y + r * 0.78, 0, x, y + r * 0.78, r * 0.6);
    h.addColorStop(0, 'rgba(200, 235, 255, 0.22)');
    h.addColorStop(1, 'rgba(200, 235, 255, 0)');
    g.fillStyle = h;
    g.beginPath(); g.arc(x, y, r, 0, TAU); g.fill();

    // borde de cristal: se aclara hacia fuera (Fresnel), sin manchas de brillo
    h = g.createRadialGradient(x, y, r * 0.72, x, y, r);
    h.addColorStop(0, 'rgba(215, 242, 255, 0)');
    h.addColorStop(0.92, 'rgba(215, 242, 255, 0.26)');
    h.addColorStop(1, 'rgba(235, 250, 255, 0.5)');
    g.fillStyle = h;
    g.beginPath(); g.arc(x, y, r, 0, TAU); g.fill();
    // reflejo del cielo: un arco fino y suave arriba
    g.beginPath();
    g.arc(x, y, r * 0.84, Math.PI * 1.12, Math.PI * 1.55);
    g.strokeStyle = 'rgba(255, 255, 255, 0.28)';
    g.lineWidth = Math.max(r * 0.07, 1.2);
    g.lineCap = 'round';
    g.stroke();

    if (n.id === s.sel) {
      g.beginPath(); g.arc(x, y, r + 5, 0, TAU);
      g.strokeStyle = 'rgba(125, 211, 252, 0.9)'; g.lineWidth = 2; g.stroke();
    }
  }

  function etiqueta(n, x, y, r) {
    g.textAlign = 'center';
    g.textBaseline = 'top';
    g.shadowColor = 'rgba(2, 12, 24, 0.95)';
    g.shadowBlur = 6;
    let yy = y + r + 8;
    const tam = n.centro ? 15 : n.grupo === 'ent' ? 12.5 : 11;
    n.lineas.forEach((l, i) => {
      const cifra = i === n.lineas.length - 1 && /€$/.test(l);
      g.font = `${cifra ? 500 : 600} ${tam}px Outfit, sans-serif`;
      g.fillStyle = cifra ? '#9FCBFF' : '#E7ECF3';
      g.fillText(l, x, yy);
      yy += tam + 3;
    });
    g.shadowBlur = 0;
  }

  function dibujar(t) {
    const mueve = !quieto();
    g.clearRect(0, 0, s.ancho, s.alto);
    const sube = Math.min((t - s.inicio) / 1600, 1);
    const crecer = 1 - Math.pow(1 - sube, 3);
    const pos = new Map(s.nodos.map((n) => [n.id, posicion(n, t, mueve)]));

    // líneas: curvas suaves y motas de luz que van del centro hacia fuera
    for (const [a, b] of s.enlaces) {
      const [ax, ay] = pos.get(a.id), [bx, by] = pos.get(b.id);
      const mx = (ax + bx) / 2 + (by - ay) * 0.08, my = (ay + by) / 2 - (bx - ax) * 0.08;
      const lg = g.createLinearGradient(ax, ay, bx, by);
      lg.addColorStop(0, 'rgba(125, 190, 235, 0.45)');
      lg.addColorStop(1, 'rgba(125, 190, 235, 0.18)');
      g.strokeStyle = lg;
      g.lineWidth = 1.4;
      g.beginPath(); g.moveTo(ax, ay); g.quadraticCurveTo(mx, my, bx, by); g.stroke();
      if (mueve) {
        for (let k = 0; k < 2; k++) {
          const u = ((t * 0.00012 + a.fase * 0.1 + b.fase * 0.13 + k * 0.5) % 1 + 1) % 1;
          const px = (1 - u) * (1 - u) * ax + 2 * (1 - u) * u * mx + u * u * bx;
          const py = (1 - u) * (1 - u) * ay + 2 * (1 - u) * u * my + u * u * by;
          const al = Math.sin(u * Math.PI) * 0.85;
          const m = g.createRadialGradient(px, py, 0, px, py, 5);
          m.addColorStop(0, `rgba(210, 240, 255, ${al})`);
          m.addColorStop(1, 'rgba(210, 240, 255, 0)');
          g.fillStyle = m;
          g.beginPath(); g.arc(px, py, 5, 0, TAU); g.fill();
        }
      }
    }

    const orden = [...s.nodos].sort((a, b) => (a.centro - b.centro) || a.pr - b.pr);
    for (const n of orden) {
      const objetivo = n.id === s.encima ? 1.07 : 1;
      n.zoom += (objetivo - n.zoom) * (mueve ? 0.2 : 1);
      const [x, y] = pos.get(n.id);
      const r = n.pr * n.zoom * (0.6 + 0.4 * crecer);
      const nivel = (n.llenado == null ? 0.93 : n.llenado) * crecer;
      burbuja(n, x, y, r, nivel, t, mueve);
    }
    for (const n of orden) {
      const [x, y] = pos.get(n.id);
      etiqueta(n, x, y, n.pr * n.zoom);
    }
  }

  function bucle(t) {
    if (!s.vivo) return;
    if (!lienzo.isConnected) { s.vivo = false; return; }
    if (!quieto() || t - s.inicio < 1700) dibujar(t);
    requestAnimationFrame(bucle);
  }

  function bajo(ev) {
    const rc = lienzo.getBoundingClientRect();
    const x = ev.clientX - rc.left, y = ev.clientY - rc.top;
    let mejor = null;
    for (const n of s.nodos) {
      const d = Math.hypot(n.px - x, n.py - y);
      if (d <= n.pr + 4 && (!mejor || n.pr < mejor.pr)) mejor = n;
    }
    return [mejor, x, y];
  }
  lienzo.addEventListener('mousemove', (ev) => {
    const [n, x, y] = bajo(ev);
    s.encima = n ? n.id : null;
    lienzo.style.cursor = n ? 'pointer' : 'default';
    if (n) {
      tip.innerHTML = '';
      const b = document.createElement('b');
      b.textContent = n.titulo[0];
      tip.append(b, document.createTextNode(n.titulo.slice(1).join('\n')));
      const izq = Math.min(x + 16, s.ancho - 310);
      tip.style.left = `${Math.max(izq, 4)}px`;
      tip.style.top = `${Math.min(y + 16, s.alto - 90)}px`;
      tip.style.opacity = 1;
    } else {
      tip.style.opacity = 0;
    }
    if (quieto()) dibujar(performance.now());
  });
  lienzo.addEventListener('mouseleave', () => {
    s.encima = null; tip.style.opacity = 0;
    if (quieto()) dibujar(performance.now());
  });
  lienzo.addEventListener('click', (ev) => {
    const [n] = bajo(ev);
    if (!n || !s.avisar) return;
    s.sel = n.id;
    s.avisar(n.id);
    if (quieto()) dibujar(performance.now());
  });

  new ResizeObserver(ajustar).observe(caja);
  s.ajustar = ajustar;
  s.colocar = colocar;
  s.dibujar = dibujar;
  requestAnimationFrame(bucle);
  return s;
}

export default function (component) {
  const { data, parentElement, setTriggerValue } = component;
  let s = parentElement.__ocb;
  if (!s || !s.lienzo.isConnected) {
    s = crear(parentElement);
    parentElement.__ocb = s;
  }
  s.avisar = (id) => setTriggerValue('clic', id);
  const forma = data.nodos.map((n) => [n.id, n.x, n.y, n.r, n.llenado]);
  const firma = JSON.stringify([forma, data.alto]);
  s.caja.style.height = `${data.alto}px`;
  s.sel = data.seleccionado;
  if (s.firma !== firma) {
    const nuevo = !s.firma || s.datos?.nodos.length !== data.nodos.length;
    s.firma = firma;
    s.datos = data;
    if (nuevo) s.inicio = performance.now();
    s.ajustar();
  } else {
    s.datos = data;
  }
}
"""

_componente = st.components.v2.component("oc_mapa_burbujas", css=CSS, js=JS)


def _medidas(nodos: list[red.NodoRed]) -> list[tuple[float, str]]:
    """Radio y color de cada nodo, con las mismas escalas que `red.mapa`."""
    escalas = {g: red._escala(nodos, g) for g in {n.grupo for n in nodos}}
    medidas = []
    for n in nodos:
        minimo_r, maximo_r = red.ESCALAS.get(n.grupo, red.ESCALAS["ent"])
        maximo, minimo = escalas[n.grupo]
        if n.centro:
            radio, color = red.RADIO_MAX + 6, n.color or red._mezcla(1.0)
        else:
            if maximo <= 0 or n.importe <= 0:
                radio = minimo_r
            else:
                radio = minimo_r + (maximo_r - minimo_r) * math.sqrt(min(n.importe / maximo, 1.0))
            t = 0.5 if maximo == minimo else max((n.importe - minimo) / (maximo - minimo), 0)
            color = n.color or red._mezcla(math.sqrt(max(t, 0.0)))
        medidas.append((radio, color))
    return medidas


def mapa(
    nodos: list[red.NodoRed],
    enlaces: list[tuple],
    alto: int,
    clave: str,
    seleccionado: str | None = None,
) -> str | None:
    """Dibuja el mapa de burbujas y devuelve el `id` de la burbuja pulsada en esta ejecución
    (None si no se ha pulsado ninguna). Los nodos deben traer su posición (`x`, `y`)."""
    if not nodos:
        return None
    datos = {
        "alto": alto,
        "seleccionado": seleccionado,
        "nodos": [
            {
                "id": n.id,
                "x": n.x or 0.0,
                "y": n.y or 0.0,
                "r": radio,
                "color": color,
                "llenado": n.llenado,
                "centro": n.centro,
                "grupo": n.grupo,
                "lineas": [linea for linea in n.etiqueta.split("\n") if linea],
                "titulo": red._titulo(n).split("\n"),
            }
            for n, (radio, color) in zip(nodos, _medidas(nodos), strict=True)
        ],
        "enlaces": [[e[0], e[1]] for e in enlaces],
    }
    resultado = _componente(data=datos, key=clave, on_clic_change=lambda: None)
    return getattr(resultado, "clic", None)


def vista_previa(
    entidades: list[dict],
    principales: dict,
    textos_millones,
    n_entidades: int = 9,
    con_contratos: int = 4,
    por_consejeria: int = 2,
) -> tuple[list[red.NodoRed], list[tuple], dict[str, tuple]]:
    """Mapa pequeño para la portada (D-048): la Comunidad, sus consejerías con más dinero y los
    contratos más grandes de las primeras, en dos niveles. Devuelve nodos, enlaces y a qué
    lleva cada nodo al pulsarlo (`("ent", nombre)` o `("con", contrato_id)`)."""
    grandes = sorted([e for e in entidades if e["credito"]], key=lambda e: -e["credito"])[
        :n_entidades
    ]
    total = sum(e["credito"] for e in entidades if e["credito"])
    gastado = sum(e["gastado"] or 0 for e in entidades)
    nodos = [
        red.NodoRed(
            id="centro",
            etiqueta="Comunidad\nde Madrid",
            importe=total,
            llenado=(gastado / total) if total and gastado else None,
            centro=True,
            detalle="Todo el dinero del año",
            x=0,
            y=0,
        )
    ]
    enlaces: list[tuple] = []
    destinos: dict[str, tuple] = {"centro": ("todo", "")}
    radio = 240
    orden = red.alternar_tamanos(list(enumerate(grandes)))
    for (i, e), (x, y) in zip(orden, red.posiciones_radiales(len(orden), radio), strict=True):
        nombre = e["entidad"].replace("Consejería de ", "").replace("Consejería ", "")
        id_ent = f"ent:{i}"
        destinos[id_ent] = ("ent", e["entidad"])
        nodos.append(
            red.NodoRed(
                id=id_ent,
                etiqueta=red.envolver(nombre.split(",")[0], 14)
                + "\n"
                + textos_millones(e["credito"]),
                importe=e["credito"],
                llenado=e["llenado"],
                titulo=e["entidad"],
                x=x,
                y=y,
            )
        )
        enlaces.append(("centro", id_ent))
        if i >= con_contratos or not e["organo_id"]:
            continue
        hijos = principales.get(e["organo_id"], [])[:por_consejeria]
        angulo = math.atan2(y, x)
        for j, c in enumerate(hijos):
            desvio = (j - (len(hijos) - 1) / 2) * 0.32
            hx = (radio + 135) * math.cos(angulo + desvio)
            hy = (radio + 135) * math.sin(angulo + desvio)
            id_con = f"con:{c['contrato_id']}"
            destinos[id_con] = ("con", c["contrato_id"])
            # los contratos, solo con su importe: el nombre sale al pasar el ratón
            nodos.append(
                red.NodoRed(
                    id=id_con,
                    etiqueta=textos_millones(c["importe"]),
                    importe=c["importe"],
                    titulo=c["adjudicatarios"] or "Sin adjudicataria",
                    detalle=(c["titulo"] or "")[:110],
                    grupo="con",
                    x=hx,
                    y=hy,
                )
            )
            enlaces.append((id_ent, id_con))
    return nodos, enlaces, destinos
