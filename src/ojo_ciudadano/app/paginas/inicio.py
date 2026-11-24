"""Portada (D-023, D-039, D-048): una página de bienvenida amable, no un panel.

De arriba abajo, con poco texto:
1. El logo y la frase, centrados, y el buscador (más estrecho) que lleva a la ficha de una
   empresa o de un organismo.
2. Lo que hace Ojo Ciudadano: a la izquierda tres frases cortas; a la derecha, un mapa de
   burbujas vivo (el de la presentación) con la Comunidad, sus consejerías y sus contratos más
   grandes. Cada burbuja lleva a su ficha en el Mapa del dinero.
3. «Qué ofrecemos»: tres puertas (Mapa del dinero, Contratos a revisar, Asistente).
4. El asistente de IA, con el ojo de cristal de la presentación.
5. «Contratos que destacan»: tres señales contadas en dinero, cada una con su propio dibujo.
   El aviso de que una señal no prueba nada va con ellas; las fuentes, en el pie (D-043).
"""

import html
from pathlib import Path

import streamlit as st

from ojo_ciudadano.app import billetes, burbujas, buscador, datos, datos_mapa, ojo_cristal, textos
from ojo_ciudadano.app.conexion import conexion

OJO = ojo_cristal.imagenes()
LOGO = (Path(__file__).parents[1] / "static" / "logo.svg").read_text(encoding="utf-8")

# Iconos de las puertas (SVG propios, sin emojis, D-022)
ICONO_MAPA = (
    '<svg viewBox="0 0 64 64" width="64" height="64" aria-hidden="true">'
    '<defs><radialGradient id="pm" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#9FCBFF"/>'
    '<stop offset="1" stop-color="#1F5FBF"/></radialGradient></defs>'
    '<path d="M30 34 L13 18 M30 34 L52 16 M30 34 L48 52" stroke="#4F9CC0" stroke-width="2"/>'
    '<circle cx="30" cy="34" r="13" fill="url(#pm)" stroke="#E6F6FF" stroke-opacity=".6"/>'
    '<circle cx="13" cy="18" r="7" fill="url(#pm)" stroke="#E6F6FF" stroke-opacity=".5"/>'
    '<circle cx="52" cy="16" r="8" fill="url(#pm)" stroke="#E6F6FF" stroke-opacity=".5"/>'
    '<circle cx="48" cy="52" r="6" fill="url(#pm)" stroke="#E6F6FF" stroke-opacity=".5"/></svg>'
)
PUERTAS = [
    (
        "dinero",
        "paginas/mapa_general.py",
        "Mapa del dinero",
        "Cuánto tiene la Comunidad, cuánto se lleva cada consejería y a quién contrata.",
        ICONO_MAPA,
    ),
    (
        "revisar",
        "paginas/alertas.py",
        "Contratos a revisar",
        "Los contratos con más señales, cada una explicada.",
        billetes.ICONOS_PUERTA["revisar"],
    ),
    (
        "asistente",
        "paginas/asistente.py",
        "Asistente de IA",
        "Pregunta como hablas y te responde con los datos y su fuente.",
        billetes.ICONOS_PUERTA["asistente"],
    ),
]

ESTILO = """
<style>
.oc-sec { text-align:center; margin: 4.5rem 0 1.6rem; font-family: Inter, sans-serif; }
.oc-sec small { display:block; color:#7DB3FF; font-size:.82rem; font-weight:600;
  letter-spacing:.14em; text-transform:uppercase; margin-bottom:.5rem; }
.oc-sec h2 { margin:0; font-size:clamp(1.7rem, 2.6vw, 2.4rem); font-weight:700;
  letter-spacing:-.02em; color:#E7ECF3; padding:0; font-weight:700 !important; }
/* buscador del Inicio, más estrecho y centrado */
.st-key-inicio_busqueda { max-width: 760px; margin: 0 auto; width: 100%;
  background: none !important; border: none !important; box-shadow: none !important;
  padding: 0 !important; transform: none !important; }
/* puertas: tarjetas enteras pulsables */
[class*="st-key-puerta_"] { position: relative; transition: transform .18s, border-color .18s;
  height: 100%; padding: 1.5rem 1.5rem !important; }
[class*="st-key-puerta_"]:hover { transform: translateY(-3px);
  border-color: rgba(170,225,255,.55) !important; }
[class*="st-key-puerta_"] [data-testid="stPageLink"] a::after {
  content: ""; position: absolute; inset: 0; }
[class*="st-key-puerta_"] [data-testid="stPageLink"] a { padding-left: 0; }
[class*="st-key-puerta_"] [data-testid="stPageLink"] a p { font-size: 1.2rem;
  font-weight: 650; white-space: normal; line-height: 1.3; }
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-puerta_"]) { flex: 1 1 auto; }
/* contratos que destacan */
[class*="st-key-destaca_"] { height: 100%; padding: 1.5rem !important; }
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-destaca_"]) { flex: 1 1 auto; }
/* enlaces de acción como botones-cápsula */
.st-key-ver_revisar, .st-key-ir_asistente { background:none !important; border:none !important;
  box-shadow:none !important; padding:0 !important; transform:none !important; }
.st-key-ver_revisar { align-items:center !important; margin-top: 1rem; }
.st-key-ver_revisar [data-testid="stPageLink"] a,
.st-key-ir_asistente [data-testid="stPageLink"] a {
  display:inline-flex; padding:.7rem 1.4rem; border-radius:999px;
  background:linear-gradient(135deg,#3d8bfd,#22b5d8);
  box-shadow:0 6px 20px rgba(61,139,253,.35), inset 0 1px 0 rgba(255,255,255,.3); }
.st-key-ver_revisar [data-testid="stPageLink"] a *,
.st-key-ir_asistente [data-testid="stPageLink"] a * {
  color:#fff !important; font-weight:600; }
</style>
"""


@st.cache_data(show_spinner=False, ttl=3600)
def _destacados() -> dict:
    return datos.destacados_portada(conexion())


@st.cache_data(show_spinner=False, ttl=3600)
def _mapa() -> dict | None:
    """Datos del mapa de la portada: el último año con gasto publicado."""
    periodos = datos_mapa.periodos(conexion())
    anio = next((p["anio"] for p in periodos if p["liquidado"]), None)
    if anio is None:
        return None
    reparto = datos_mapa.reparto(conexion(), anio)
    return {
        "anio": anio,
        "url_origen": reparto["url_origen"],
        "entidades": reparto["entidades"],
        "principales": datos_mapa.contratos_principales(conexion(), anio, 2),
    }


# ------------------------------------------------------------------------------ 1. cabecera
def bienvenida() -> None:
    contenido = """
<style>
.oc-bienvenida { display:flex; align-items:center; justify-content:center; gap:28px;
  font-family:Inter, sans-serif; padding: 28px 0 22px; }
.oc-bienvenida .oc-logo { width:clamp(84px, 9vw, 132px); height:auto; flex:none;
  filter:drop-shadow(0 0 26px rgba(56,189,248,.4)); }
.oc-bienvenida h1 { font-size:clamp(2.3rem, 4.2vw, 3.9rem); line-height:1.08; margin:0;
  font-weight:750; letter-spacing:-.03em; max-width: 16ch;
  background:linear-gradient(180deg,#fff 20%,#9FCBFF); -webkit-background-clip:text;
  background-clip:text; color:transparent; }
</style>
<div class="oc-bienvenida">
  LOGO_AQUI
  <h1>Mira en qué se gasta tu dinero la Comunidad de Madrid</h1>
</div>"""
    contenido = contenido.replace("LOGO_AQUI", LOGO.replace("<svg ", '<svg class="oc-logo" ', 1))
    billetes.pintar(contenido, clave="inicio_bienvenida")


# ------------------------------------------------------------------------------ 2. qué hace
PUNTOS = [
    ("Sigue el dinero", "De la Comunidad a cada consejería, y de ahí a cada empresa."),
    ("Mira las señales", "Contratos que se salen de lo normal, cada uno explicado."),
    ("Pregunta a la IA", "Un asistente que te guía por los datos y te da la fuente."),
]


def que_hace() -> None:
    # el mapa a la izquierda y el texto a la derecha, juntos (D-050)
    _, derecha, izquierda, _ = st.columns([1, 6, 5, 1], vertical_alignment="center", gap="small")
    puntos = "".join(
        f'<li><span class="n">{i}</span><div><b>{titulo}</b><p>{frase}</p></div></li>'
        for i, (titulo, frase) in enumerate(PUNTOS, start=1)
    )
    with izquierda:
        billetes.pintar(
            f"""
<style>
.oc-hace {{ font-family:Inter, sans-serif; color:#E7ECF3; }}
.oc-hace small {{ color:#7DB3FF; font-size:.82rem; font-weight:600; letter-spacing:.14em;
  text-transform:uppercase; }}
.oc-hace h2 {{ font-size:clamp(1.8rem, 2.8vw, 2.6rem); line-height:1.12; margin:.4rem 0 1.6rem;
  font-weight:700; letter-spacing:-.02em; }}
.oc-hace h2 em {{ font-style:normal; color:#7DB3FF; }}
.oc-hace ul {{ list-style:none; padding:0; margin:0; display:grid; gap:1.1rem; }}
.oc-hace li {{ display:flex; gap:14px; align-items:flex-start; }}
.oc-hace .n {{ flex:none; width:34px; height:34px; border-radius:50%; display:grid;
  place-items:center; font-weight:700; color:#fff; font-size:.95rem;
  background:radial-gradient(circle at 35% 30%, #9FCBFF, #1F5FBF);
  box-shadow:0 0 18px rgba(56,189,248,.35), inset 0 1px 0 rgba(255,255,255,.4); }}
.oc-hace b {{ font-size:1.12rem; }}
.oc-hace p {{ margin:.15rem 0 0; color:#9FB6CC; font-size:1rem; line-height:1.45; }}
</style>
<div class="oc-hace"><small>Datos públicos</small>
<h2>Siempre fueron públicos.<br><em>Ahora, por fin, accesibles.</em></h2>
<ul>{puntos}</ul></div>""",
            clave="inicio_hace",
        )
    with derecha:
        mapa = _mapa()
        if mapa is None:
            return
        nodos, enlaces, destinos = burbujas.vista_previa(
            mapa["entidades"], mapa["principales"], textos.millones, n_entidades=8, con_contratos=3
        )
        pulsado = burbujas.mapa(nodos, enlaces, alto=560, clave="inicio_mapa")
        if pulsado and pulsado in destinos:
            tipo, referencia = destinos[pulsado]
            st.session_state["mg_sel"] = None if tipo == "todo" else (tipo, referencia)
            st.session_state["mg_anio"] = mapa["anio"]
            st.switch_page("paginas/mapa_general.py")


# ------------------------------------------------------------------------------ 3. puertas
def seccion(antetitulo: str, titulo: str) -> None:
    st.html(f'<div class="oc-sec"><small>{antetitulo}</small><h2>{titulo}</h2></div>')


def puertas() -> None:
    seccion("Qué ofrecemos", "Tres formas de mirar el gasto público")
    columnas = st.columns(len(PUERTAS), gap="medium")
    for columna, (clave, pagina, titulo, frase, icono) in zip(columnas, PUERTAS, strict=True):
        with columna.container(border=True, key=f"puerta_{clave}"):
            billetes.pintar(icono, clave=f"icono_{clave}")
            st.page_link(pagina, label=titulo)
            st.caption(frase)


# ------------------------------------------------------------------------------ 4. asistente
def asistente() -> None:
    seccion("Asistente de IA", "Pregunta como hablas")
    ojo, texto = st.columns([2, 3], vertical_alignment="center", gap="large")
    with ojo:
        billetes.pintar(
            f"""
<style>
.oc-ojo {{ position:relative; width:min(100%, 300px); aspect-ratio:1; margin:0 auto; }}
.oc-ojo::before {{ content:""; position:absolute; inset:-14%; border-radius:50%;
  background:radial-gradient(circle, rgba(56,189,248,.28), transparent 62%); }}
.oc-ojo img {{ position:absolute; inset:0; width:100%; height:100%; }}
.oc-ojo .iris {{ animation: oc-ojo-gira 40s linear infinite; }}
@keyframes oc-ojo-gira {{ to {{ transform: rotate(360deg); }} }}
@media (prefers-reduced-motion: reduce) {{ .oc-ojo .iris {{ animation:none; }} }}
html.oc-sin-gpu .oc-ojo .iris {{ animation:none; }}
</style>
<div class="oc-ojo" role="img" aria-label="El ojo de Ojo Ciudadano">
  <img class="iris" src="{OJO["{iris}"]}" alt=""><img src="{OJO["{cristal}"]}" alt="">
</div>""",
            clave="inicio_ojo",
        )
    with texto:
        billetes.pintar(
            """
<style>
.oc-ia { font-family:Inter, sans-serif; color:#E7ECF3; }
.oc-ia p { font-size:1.15rem; color:#B9C6D8; line-height:1.55; margin:0 0 1.2rem; max-width:34em; }
.oc-ia .chat { display:grid; gap:.6rem; max-width:34em; }
.oc-ia .q { justify-self:end; padding:.7rem 1rem; border-radius:18px 18px 4px 18px;
  background:linear-gradient(135deg,#3d8bfd,#22b5d8); color:#fff; font-size:.98rem; }
.oc-ia .r { justify-self:start; padding:.7rem 1rem; border-radius:18px 18px 18px 4px;
  background:rgba(255,255,255,.06); border:1px solid rgba(170,225,255,.18); font-size:.98rem;
  color:#E7ECF3; }
.oc-ia .r small { display:block; color:#7DB3FF; margin-top:.3rem; font-size:.78rem; }
</style>
<div class="oc-ia">
<p>Un asistente de IA que busca en los datos oficiales por ti y te responde con su fuente.</p>
<div class="chat">
  <div class="q">¿Qué organismos adjudicaron más dinero en 2025?</div>
  <div class="r">Te enseño los diez primeros, con lo que adjudicó cada uno.
    <small>Fuente: Plataforma de Contratación del Sector Público</small></div>
</div></div>""",
            clave="inicio_ia",
        )
        with st.container(key="ir_asistente"):
            st.page_link(
                "paginas/asistente.py", label="Hablar con el asistente", icon=":material/forum:"
            )


# ------------------------------------------------------------------------------ 5. destacados
ESTILO_TARJETA = """
<style>
.oc-dest { font-family:Inter, sans-serif; color:#E7ECF3; display:flex; flex-direction:column;
  gap:.9rem; }
.oc-dest h3 { font-size:1.15rem; margin:0; font-weight:650; padding:0; color:#E7ECF3; }
.oc-dest .cifra { font-size:clamp(2.2rem, 3vw, 2.9rem); font-weight:750; letter-spacing:-.02em;
  line-height:1; background:linear-gradient(180deg,#fff,#7DB3FF); -webkit-background-clip:text;
  background-clip:text; color:transparent; }
.oc-dest p { margin:0; color:#B9C6D8; font-size:1rem; line-height:1.5; }
.oc-dest p b { color:#fff; }
.oc-dest svg { display:block; width:100%; height:auto; }
.oc-dest .pie { color:#8FA7BF; font-size:.82rem; }
</style>
"""


def tarjeta_una_oferta(d: dict) -> str:
    parte = d["importe"] / d["total"] if d["total"] else 0
    n100 = round(100 * d["contratos"] / d["comprobados"]) if d["comprobados"] else 0
    ancho = 300
    return (
        ESTILO_TARJETA
        + f"""<div class="oc-dest"><h3>Una sola oferta</h3>
<div class="cifra">{textos.millones(d["importe"])}</div>
<p>se adjudicaron con <b>una sola empresa compitiendo</b>: sin otra oferta con la que comparar
el precio.</p>
<svg viewBox="0 0 {ancho} 54" role="img" aria-label="{round(100 * parte)} % del dinero">
<defs><linearGradient id="u1" x1="0" x2="1"><stop offset="0" stop-color="#2f7cf0"/>
<stop offset="1" stop-color="#38bdf8"/></linearGradient></defs>
<rect x="0" y="8" width="{ancho}" height="22" rx="11" fill="#cfeeff" fill-opacity=".1"
  stroke="#aae1ff" stroke-opacity=".3"/>
<rect x="0" y="8" width="{ancho * parte:.1f}" height="22" rx="11" fill="url(#u1)"/>
<text x="0" y="50" fill="#9FB6CC" font-size="11" font-family="Inter">{round(100 * parte)} % del
dinero</text>
<text x="{ancho}" y="50" fill="#9FB6CC" font-size="11" font-family="Inter" text-anchor="end">
de {textos.millones(d["total"])}</text></svg>
<p class="pie">{n100} de cada 100 contratos donde se pudo comprobar.</p></div>"""
    )


def tarjeta_modificaciones(d: dict, comparada: dict | None, anio: int | None) -> str:
    subida = d["subida"]
    sube = round(100 * subida / d["adjudicado"]) if d["adjudicado"] else 0
    dibujo, frase = "", ""
    if comparada:
        otra = comparada["credito"]
        nombre = html.escape(
            comparada["entidad"].replace("Consejería de ", "").replace("Consejería ", "")
        )
        # dos barras con la misma escala: lo que subieron frente al presupuesto de la consejería
        maximo = max(subida, otra)
        filas = []
        for k, (valor, etiqueta, color) in enumerate(
            (
                (subida, "más por modificaciones", "url(#m1)"),
                (otra, f"presupuesto de {nombre[:30]}", "url(#m2)"),
            )
        ):
            y = 8 + k * 58
            ancho = 300 * valor / maximo
            cifra = ("+" if k == 0 else "") + textos.millones(valor)
            filas.append(
                f'<text x="0" y="{y + 12}" fill="#E7ECF3" font-size="13" font-weight="700" '
                f'font-family="Inter">{cifra}<tspan fill="#9FB6CC" font-weight="400" '
                f'font-size="11.5"> {etiqueta}</tspan></text>'
                f'<rect x="0" y="{y + 20}" width="300" height="16" rx="8" fill="#cfeeff" '
                'fill-opacity=".08" stroke="#aae1ff" stroke-opacity=".22"/>'
                f'<rect x="0" y="{y + 20}" width="{ancho:.1f}" height="16" rx="8" fill="{color}"/>'
            )
        dibujo = (
            '<svg viewBox="0 0 300 118" role="img" aria-label="'
            f'{textos.millones(subida)} frente a {textos.millones(otra)}">'
            '<defs><linearGradient id="m1" x1="0" x2="1"><stop offset="0" stop-color="#22b5d8"/>'
            '<stop offset="1" stop-color="#7de3ff"/></linearGradient>'
            '<linearGradient id="m2" x1="0" x2="1"><stop offset="0" stop-color="#1f5fbf"/>'
            '<stop offset="1" stop-color="#3d8bfd"/></linearGradient></defs>'
            + "".join(filas)
            + "</svg>"
        )
        verbo = "casi todo lo que tuvo" if subida < otra else "más de lo que tuvo"
        frase = f"<p>Es {verbo} <b>{nombre}</b> en todo {anio}.</p>"
    return (
        ESTILO_TARJETA
        + f"""<div class="oc-dest"><h3>Modificaciones de más del 20 %</h3>
<div class="cifra">+{textos.millones(subida)}</div>
<p>de más costaron {textos.numero(d["contratos"])} contratos tras modificarse: un
<b>{sube} %</b> sobre lo adjudicado.</p>{dibujo}{frase}</div>"""
    )


def tarjeta_concentracion(d: dict) -> str:
    """Anillo en dos partes bien separadas: lo que se lleva una empresa y lo que queda para las
    demás, con los extremos rectos para que se vea dónde acaba cada parte."""
    p = round(100 * d["parte"])
    hueco = 1.2  # separación entre las dos partes (en % de la circunferencia)
    resto = 100 - p
    return (
        ESTILO_TARJETA
        + f"""<div class="oc-dest"><h3>Una empresa concentra el gasto</h3>
<svg viewBox="0 0 300 124" role="img" aria-label="{p} de cada 100 euros a una sola empresa">
<defs><linearGradient id="u3" x1="0" x2="1"><stop offset="0" stop-color="#2f7cf0"/>
<stop offset="1" stop-color="#38bdf8"/></linearGradient></defs>
<g transform="translate(62 62) rotate(-90)">
<circle r="44" fill="none" stroke="url(#u3)" stroke-width="18" pathLength="100"
  stroke-dasharray="{p - hueco:.1f} {100 - p + hueco:.1f}" stroke-dashoffset="{-hueco / 2:.1f}"/>
<circle r="44" fill="none" stroke="#F2B544" stroke-width="18" pathLength="100"
  stroke-dasharray="{max(resto - hueco, 0.6):.1f} {100 - resto + hueco:.1f}"
  stroke-dashoffset="{-(p + hueco / 2):.1f}"/></g>
<text x="62" y="69" text-anchor="middle" fill="#fff" font-size="21" font-weight="750"
  font-family="Inter">{p} %</text>
<rect x="132" y="38" width="12" height="12" rx="3" fill="url(#u3)"/>
<text x="152" y="48" fill="#E7ECF3" font-size="13" font-family="Inter" font-weight="600">
{p} € para una empresa</text>
<rect x="132" y="66" width="12" height="12" rx="3" fill="#F2B544"/>
<text x="152" y="76" fill="#9FB6CC" font-size="13" font-family="Inter">
{resto} € para el resto</text>
<text x="132" y="104" fill="#8FA7BF" font-size="11" font-family="Inter">de cada 100 €
adjudicados</text></svg>
<p>En <b>{html.escape(d["organo"])}</b>, una sola empresa se lleva casi todo lo adjudicado en
un mismo tipo de contrato.</p></div>"""
    )


def destacados() -> None:
    seccion("Contratos que destacan", "Lo que los datos dejan ver")
    d = _destacados()
    mapa = _mapa()
    comparada = None
    if mapa:
        subida = d["modificaciones"]["subida"]
        candidatas = [e for e in mapa["entidades"] if e["credito"] and "Consejería" in e["entidad"]]
        if candidatas:
            comparada = min(candidatas, key=lambda e: abs(e["credito"] - subida))
    tarjetas = [
        ("una_oferta", tarjeta_una_oferta(d["una_oferta"])),
        (
            "modificaciones",
            tarjeta_modificaciones(d["modificaciones"], comparada, mapa and mapa["anio"]),
        ),
    ]
    if d["concentracion"]:
        tarjetas.append(("concentracion", tarjeta_concentracion(d["concentracion"])))
    columnas = st.columns(len(tarjetas), gap="medium")
    for columna, (clave, contenido) in zip(columnas, tarjetas, strict=True):
        with columna.container(border=True, key=f"destaca_{clave}"):
            billetes.pintar(contenido, clave=f"destacado_{clave}")
    with st.container(key="ver_revisar"):
        st.page_link(
            "paginas/alertas.py", label="Ver los contratos a revisar", icon=":material/flag:"
        )


# ------------------------------------------------------------------------------ pantalla
con = conexion()
st.html(ESTILO)

bienvenida()
st.html('<div style="height:2rem"></div>')
que_hace()

# el buscador, debajo del mapa y antes de «Qué ofrecemos» (D-051)
st.html('<div style="height:2.5rem"></div>')
with st.container(key="inicio_busqueda"):
    elegido = buscador.todo("inicio_buscar")
if elegido:
    tipo, ident = elegido
    # se olvida la búsqueda: si no, al volver al Inicio llevaría otra vez a la misma ficha
    st.session_state.pop("inicio_buscar", None)
    destino = "paginas/empresa.py" if tipo == "empresa" else "paginas/organo.py"
    st.switch_page(destino, query_params={tipo: ident})

puertas()
asistente()
destacados()
