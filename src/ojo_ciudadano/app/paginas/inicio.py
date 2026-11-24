"""Portada para el ciudadano (D-023, D-039).

En cinco segundos: el logo y una frase, un buscador que lleva a la ficha de una empresa o
de un organismo y cuatro puertas grandes (sin subtítulo ni línea de cifras: poco texto).
Debajo, las señales que
buscamos en formato «de cada 100 contratos», con la explicación en un botón. El aviso de que
una señal no prueba nada queda en el icono de las señales; las fuentes, en el pie (D-043).
"""

from pathlib import Path

import streamlit as st

from ojo_ciudadano.app import billetes, buscador, datos, textos
from ojo_ciudadano.app.conexion import conexion

# Solo el logo (D-043); la mascota con billetes queda en el «Mapa del dinero».
LOGO = (Path(__file__).parents[1] / "static" / "logo.svg").read_text(encoding="utf-8")

PUERTAS = [
    (
        "dinero",
        "paginas/mapa_general.py",
        "¿A dónde va el dinero?",
        "Cuánto tiene la Comunidad y cuánto se lleva cada consejería.",
    ),
    (
        "revisar",
        "paginas/alertas.py",
        "Contratos a revisar",
        "Los contratos con más señales, cada una explicada.",
    ),
    (
        "buscar",
        "paginas/empresa.py",
        "Busca una empresa o un organismo",
        "Qué contratos y subvenciones tiene y de quién.",
    ),
    (
        "asistente",
        "paginas/asistente.py",
        "Pregúntale al asistente",
        "Escribe tu pregunta y te responde con la fuente.",
    ),
]

# Tarjetas enteras pulsables: el enlace de cada puerta se estira sobre toda la tarjeta.
ESTILO = """
<style>
[class*="st-key-puerta_"] { position: relative; transition: transform .18s, border-color .18s; }
[class*="st-key-puerta_"]:hover { transform: translateY(-3px);
  border-color: rgba(170,225,255,.55) !important; }
[class*="st-key-puerta_"] [data-testid="stPageLink"] a::after {
  content: ""; position: absolute; inset: 0; }
[class*="st-key-puerta_"] [data-testid="stPageLink"] a p { font-size: 1.12rem;
  font-weight: 650; white-space: normal; overflow: visible; text-overflow: clip;
  line-height: 1.3; }
/* Todas las tarjetas, del mismo tamaño: rellenan la altura de su fila (la columna ya se estira)
   y el botón de cada señal queda abajo. */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-puerta_"]) { flex: 1 1 auto; }
.st-key-senales { display: grid !important; grid-template-columns: repeat(3, minmax(0, 1fr));
  grid-auto-rows: 1fr; gap: 1.5rem; align-items: stretch !important; }
.st-key-senales > [data-testid="stLayoutWrapper"] { align-self: stretch !important;
  height: auto !important; }
@media (max-width: 900px) { .st-key-senales { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 600px) { .st-key-senales { grid-template-columns: 1fr; } }
[class*="st-key-puerta_"], [class*="st-key-senal_"] { height: 100%; }
[class*="st-key-senal_"] > div:last-child { margin-top: auto; }
[class*="st-key-puerta_"] [data-testid="stPageLink"] a { padding-left: 0; }
[class*="st-key-puerta_"], [class*="st-key-senal_"] { padding: 1.25rem 1.35rem !important; }
</style>
"""


@st.cache_data(show_spinner=False, ttl=3600)
def _conteo() -> dict:
    return datos.conteo_senales(conexion())


def bienvenida() -> None:
    contenido = f"""
<style>
.oc-bienvenida {{ display:flex; gap:clamp(24px, 4vw, 56px); align-items:center; flex-wrap:wrap;
  font-family:Inter, sans-serif; color:#E7ECF3; padding:16px 0 8px; }}
.oc-bienvenida .texto {{ flex:1 1 420px; min-width:0; max-width:900px; }}
.oc-bienvenida h1 {{ font-size:clamp(2.2rem, 3.6vw, 3.5rem); line-height:1.1; margin:0 0 16px;
  font-weight:700;
  letter-spacing:-.02em; background:linear-gradient(180deg,#fff,#9FCBFF);
  -webkit-background-clip:text; background-clip:text; color:transparent; }}
.oc-bienvenida p {{ font-size:clamp(1.1rem, 1.4vw, 1.3rem); color:#B9C6D8; margin:0;
  line-height:1.5; }}
.oc-bienvenida .oc-logo {{ width:clamp(110px, 12vw, 176px); height:auto; flex:0 0 auto;
  filter:drop-shadow(0 0 26px rgba(56,189,248,.35)); }}
@media (max-width:640px) {{ .oc-bienvenida h1 {{ font-size:1.9rem; }} }}
</style>
<div class="oc-bienvenida">
  {LOGO.replace("<svg ", '<svg class="oc-logo" ', 1)}
  <div class="texto">
    <h1>Mira en qué se gasta tu dinero la Comunidad de Madrid</h1>
  </div>
</div>"""
    billetes.pintar(contenido, clave="inicio_bienvenida")


def puertas() -> None:
    columnas = st.columns(len(PUERTAS), gap="medium")
    for columna, (clave, pagina, titulo, frase) in zip(columnas, PUERTAS, strict=True):
        with columna.container(border=True, key=f"puerta_{clave}"):
            billetes.pintar(billetes.ICONOS_PUERTA[clave], clave=f"icono_{clave}")
            st.page_link(pagina, label=titulo)
            st.caption(frase)


def senales() -> None:
    st.subheader(
        "Qué señales buscamos",
        help="**Una señal no prueba nada irregular:** indica dónde merece la pena mirar con "
        "más detalle.",
        anchor=False,
    )
    conteo = _conteo()
    # Las seis tarjetas van en una sola rejilla (CSS) con filas iguales: así miden lo mismo.
    with st.container(key="senales"):
        for indicador in textos.SENAL_CORTA:
            c = conteo.get(indicador)
            if not c or not c["comprobados"]:
                continue
            n = 100 * c["encontrados"] / c["comprobados"]
            with st.container(border=True, key=f"senal_{indicador}"):
                st.markdown(f"{textos.ICONO_SENAL[indicador]} **{textos.SENAL_CORTA[indicador]}**")
                que = textos.SENAL_DE_100[indicador]
                billetes.pintar(
                    billetes.svg_cuadricula(n, que)
                    + '<p style="font-family:Inter,sans-serif;color:#E7ECF3;font-size:1.05rem;'
                    "line-height:1.5;"
                    f'margin:.5rem 0 0"><b style="font-size:1.6rem;color:{billetes.COLOR_SENAL}">'
                    f"{billetes.cifra_de_100(n)}</b> de cada 100 contratos {que}</p>",
                    clave=f"cuadricula_{indicador}",
                )
                with st.popover("¿Qué significa?", icon=":material/help:", width="stretch"):
                    st.markdown(textos.SENAL_FRASE[indicador])
                    st.caption(
                        f"Se pudo comprobar en {textos.numero(c['comprobados'])} contratos (los "
                        f"que traen los datos necesarios); {textos.numero(c['encontrados'])} "
                        "tienen la señal. El «de cada 100» se cuenta sobre los comprobados."
                    )


# ------------------------------------------------------------------------------ pantalla
con = conexion()
st.html(ESTILO)

bienvenida()

elegido = buscador.todo("inicio_buscar")
if elegido:
    tipo, ident = elegido
    destino = "paginas/empresa.py" if tipo == "empresa" else "paginas/organo.py"
    st.switch_page(destino, query_params={tipo: ident})

puertas()

senales()
