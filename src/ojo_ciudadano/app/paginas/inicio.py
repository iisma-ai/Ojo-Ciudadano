"""Portada para el ciudadano (D-023, D-039).

En cinco segundos: la mascota y una frase, un buscador que lleva a la ficha de una empresa o
de un organismo, cuatro puertas grandes y las cifras en una línea. Debajo, las señales que
buscamos en formato «de cada 100 contratos», con la explicación en un botón. El aviso de que
una señal no prueba nada queda visible; las fuentes, en el botón «Fuentes».
"""

import streamlit as st

from ojo_ciudadano.app import billetes, buscador, datos, datos_contexto, textos
from ojo_ciudadano.app.conexion import conexion

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
[class*="st-key-puerta_"] { height: 100%; }
[class*="st-key-puerta_"] [data-testid="stPageLink"] a { padding-left: 0; }
.oc-cifras { color: #9FB6CC; font-size: .98rem; margin: .2rem 0 .4rem; }
.oc-cifras b { color: #E7ECF3; }
</style>
"""


@st.cache_data(show_spinner=False, ttl=3600)
def _resumen() -> dict:
    return datos.resumen_portada(conexion())


@st.cache_data(show_spinner=False, ttl=3600)
def _conteo() -> dict:
    return datos.conteo_senales(conexion())


def bienvenida() -> None:
    contenido = f"""
<style>
{billetes.CSS_OJO}
.oc-bienvenida {{ display:flex; gap:26px; align-items:center; flex-wrap:wrap;
  font-family:Inter, sans-serif; color:#E7ECF3; }}
.oc-bienvenida .texto {{ flex:1 1 380px; min-width:0; }}
.oc-bienvenida h1 {{ font-size:2.6rem; line-height:1.15; margin:0 0 12px; font-weight:700;
  letter-spacing:-.02em; background:linear-gradient(180deg,#fff,#9FCBFF);
  -webkit-background-clip:text; background-clip:text; color:transparent; }}
.oc-bienvenida p {{ font-size:1.15rem; color:#B9C6D8; margin:0; }}
.oc-bienvenida .oc-ojo {{ width:190px; }}
@media (max-width:640px) {{ .oc-bienvenida h1 {{ font-size:1.9rem; }} }}
</style>
<div class="oc-bienvenida">
  {billetes.svg_ojo()}
  <div class="texto">
    <h1>Mira en qué se gasta tu dinero la Comunidad de Madrid</h1>
    <p>Contratos y subvenciones de 2023 a 2026, sacados de fuentes oficiales.</p>
  </div>
</div>"""
    billetes.pintar(contenido, clave="inicio_bienvenida")


def puertas() -> None:
    columnas = st.columns(len(PUERTAS))
    for columna, (clave, pagina, titulo, frase) in zip(columnas, PUERTAS, strict=True):
        with columna.container(border=True, key=f"puerta_{clave}"):
            billetes.pintar(billetes.ICONOS_PUERTA[clave], clave=f"icono_{clave}")
            st.page_link(pagina, label=titulo)
            st.caption(frase)


def senales() -> None:
    st.subheader("Qué señales buscamos")
    st.markdown(
        "**Una señal no prueba nada irregular:** indica dónde merece la pena mirar con más detalle."
    )
    conteo = _conteo()
    indicadores = list(textos.SENAL_CORTA)
    for inicio in range(0, len(indicadores), 3):
        columnas = st.columns(3)
        for columna, indicador in zip(columnas, indicadores[inicio : inicio + 3], strict=False):
            c = conteo.get(indicador)
            if not c or not c["comprobados"]:
                continue
            n = 100 * c["encontrados"] / c["comprobados"]
            with columna.container(border=True, key=f"senal_{indicador}"):
                st.markdown(f"{textos.ICONO_SENAL[indicador]} **{textos.SENAL_CORTA[indicador]}**")
                que = textos.SENAL_DE_100[indicador]
                billetes.pintar(
                    billetes.svg_cuadricula(n, que)
                    + '<p style="font-family:Inter,sans-serif;color:#E7ECF3;font-size:1.05rem;'
                    f'margin:.5rem 0 0"><b style="font-size:1.6rem;color:{billetes.AMBAR}">'
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

_, info = st.columns([6, 1])
with info.popover("Fuentes", icon=":material/info:", width="stretch"):
    st.markdown(textos.AVISO)
    st.markdown(textos.NOTA_SENAL)
    st.markdown(textos.FUENTES)
    st.caption(
        textos.fechas_descarga(datos.fechas_datos(con) + datos_contexto.fechas_contexto(con))
    )

bienvenida()

elegido = buscador.todo("inicio_buscar")
if elegido:
    tipo, ident = elegido
    destino = "paginas/empresa.py" if tipo == "empresa" else "paginas/organo.py"
    st.switch_page(destino, query_params={tipo: ident})

puertas()

resumen = _resumen()
st.html(
    '<p class="oc-cifras">'
    f"<b>{textos.numero(resumen['n_contratos'])}</b> contratos · "
    f"<b>{textos.numero(resumen['n_concesiones'])}</b> subvenciones · "
    f"<b>{textos.numero(resumen['n_organos'])}</b> organismos · de fuentes oficiales"
    "</p>"
)

senales()
