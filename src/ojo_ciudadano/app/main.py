"""Interfaz de Ojo Ciudadano.

Uso: uv run streamlit run src/ojo_ciudadano/app/main.py

Identidad visual (logo, paleta y reglas) en docs/marca.md; el tema está en .streamlit/config.toml.
Sin emojis: los iconos son de Material Symbols (`:material/nombre:`).
"""

import base64
from pathlib import Path

import streamlit as st

from ojo_ciudadano.app import (
    datos,
    datos_contexto,
    intro3d,
    ojo_cristal,
    rendimiento,
    textos,
)
from ojo_ciudadano.app.conexion import conexion

ESTATICOS = Path(__file__).parent / "static"

st.set_page_config(
    page_title="Ojo Ciudadano",
    page_icon=str(ESTATICOS / "logo.svg"),
    layout="wide",
)
st.html(f"<style>{(ESTATICOS / 'estilo.css').read_text(encoding='utf-8')}</style>")


# st.html limpia los SVG en línea: el logo va como imagen (data URI).
LOGO = (
    "data:image/svg+xml;base64," + base64.b64encode((ESTATICOS / "logo.svg").read_bytes()).decode()
)
INTRO = (ESTATICOS / "intro.html").read_text(encoding="utf-8")
for marca, imagen in ojo_cristal.imagenes().items():  # el ojo de cristal de la presentación
    INTRO = INTRO.replace(marca, imagen)

# Web ligera (D-043): sin barra lateral. Arriba, una barra con el nombre, los botones de las
# partes principales y «Explorar» con el resto de pantallas; abajo del todo, el pie con el aviso, la
# metodología, las fuentes y las fechas de descarga.
INICIO = st.Page("paginas/inicio.py", title="Inicio", icon=":material/home:", default=True)
DINERO = st.Page(
    "paginas/mapa_general.py",
    title="Mapa del dinero",
    icon=":material/payments:",
    url_path="mapa_general",
)
REVISAR = st.Page("paginas/alertas.py", title="Contratos a revisar", icon=":material/flag:")
ATIPICOS = st.Page(
    "paginas/atipicos.py", title="Contratos atípicos", icon=":material/scatter_plot:"
)
MAPA = st.Page("paginas/mapa.py", title="Red del dinero", icon=":material/account_tree:")
CONTEXTO = st.Page(
    "paginas/contexto.py",
    title="Presupuesto y contexto",
    icon=":material/account_balance_wallet:",
)
EMPRESA = st.Page("paginas/empresa.py", title="Ficha de empresa", icon=":material/domain:")
ORGANO = st.Page("paginas/organo.py", title="Ficha de órgano", icon=":material/account_balance:")
ASISTENTE = st.Page("paginas/asistente.py", title="Asistente", icon=":material/forum:")

SECCIONES = {
    "": [INICIO, DINERO],
    "Señales": [REVISAR, ATIPICOS],
    "Explorar": [MAPA, CONTEXTO, EMPRESA, ORGANO],
    "Preguntar": [ASISTENTE],
}
PRINCIPALES = [INICIO, DINERO, REVISAR, ASISTENTE]  # los botones de la barra
# «Explorar» solo lleva lo que no está en la barra. Atípicos no tiene botón arriba: va aquí para
# que se pueda llegar a ella.
EXPLORAR = [*SECCIONES["Explorar"], ATIPICOS]


def intro() -> None:
    """Animación de entrada (3 s), solo la primera vez que se abre la web en la sesión."""
    if not st.session_state.get("intro_vista"):
        st.session_state["intro_vista"] = True
        st.html(INTRO)
        intro3d.pintar()


def marcar_seccion(pagina) -> None:
    """Resalta en la cápsula el botón de la pantalla abierta (o «Explorar» si es una de las
    suyas). Streamlit no marca el enlace activo con un atributo estable, pero aquí se sabe qué
    pantalla está abierta. El estilo va antes de la cabecera, para no contar como un botón."""
    rutas = [p.url_path for p in PRINCIPALES]
    posicion = rutas.index(pagina.url_path) + 1 if pagina.url_path in rutas else len(rutas) + 1
    st.html(
        "<style>"
        f".st-key-nav > div:nth-child({posicion}) [data-testid='stPageLink-NavLink'],"
        f".st-key-nav > div:nth-child({posicion}) [data-testid='stPopover'] button {{"
        "background: linear-gradient(135deg, #3d8bfd, #22b5d8) !important;"
        "box-shadow: 0 4px 14px rgba(61,139,253,.35), inset 0 1px 0 rgba(255,255,255,.3)"
        " !important; }"
        f".st-key-nav > div:nth-child({posicion}) * {{ color: #fff !important; }}"
        "</style>"
    )


def barra_superior(pagina) -> None:
    """Logo, botones de las partes principales y «Explorar» con el resto de pantallas."""
    with st.container(key="barra", horizontal=True, vertical_alignment="center", gap="small"):
        # En el Inicio, solo el nombre: el logo va junto al título (D-051). En las demás, con él.
        icono = (
            ""
            if pagina.url_path == INICIO.url_path
            else f'<img src="{LOGO}" alt="" width="32" height="32">'
        )
        st.html(f'<div class="oc-marca">{icono}<span>Ojo <b>Ciudadano</b></span></div>')
        # los botones, juntos en una cápsula a la derecha (D-045)
        with st.container(
            key="nav", horizontal=True, vertical_alignment="center", gap=None, width="content"
        ):
            for pagina in PRINCIPALES:
                st.page_link(pagina, label=pagina.title, icon=pagina.icon)
            with st.popover("Explorar", icon=":material/explore:"):
                for pagina in EXPLORAR:
                    st.page_link(pagina, label=pagina.title, icon=pagina.icon)


# Notas de una pantalla concreta que también van al pie.
NOTAS_PIE = {ATIPICOS.url_path: ("Cómo se calculan los contratos atípicos", textos.AVISO_ATIPICOS)}


def pie(pagina) -> None:
    """Pie sencillo (D-047): el desplegable del aviso legal (con todo lo demás dentro) y, lo
    último y centrado, el logo con el nombre. En el Inicio, solo el logo."""
    with st.container(key="pie"):
        rendimiento.detectar()  # sin tarjeta gráfica, fondo quieto (D-044); no dibuja nada
        if pagina.url_path != INICIO.url_path:
            with st.expander("Aviso legal, metodología y fuentes", icon=":material/info:"):
                st.markdown(textos.AVISO_CORTO)
                if pagina.url_path in NOTAS_PIE:
                    titulo, nota = NOTAS_PIE[pagina.url_path]
                    st.markdown(f"**{titulo}**")
                    st.markdown(nota)
                st.markdown(textos.AVISO)
                st.markdown(textos.NOTA_SENAL)
                st.markdown("**Qué mide cada indicador**")
                st.markdown(textos.lista_indicadores())
                st.markdown(textos.FUENTES)
                st.caption(
                    textos.fechas_descarga(
                        datos.fechas_datos(conexion()) + datos_contexto.fechas_contexto(conexion())
                    )
                )
                st.caption(textos.PIE)
        st.html(
            f'<div class="oc-marca oc-marca-pie"><img src="{LOGO}" alt="" width="34" height="34">'
            "<span>Ojo <b>Ciudadano</b></span></div>"
        )


paginas = st.navigation(SECCIONES, position="hidden")
intro()
marcar_seccion(paginas)
barra_superior(paginas)
# El pie se dibuja antes que la pantalla y el CSS lo coloca al final (order): así sale también
# cuando la pantalla se para pronto (st.stop) esperando una elección o por falta de datos.
pie(paginas)
paginas.run()
