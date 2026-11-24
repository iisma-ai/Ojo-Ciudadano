"""Interfaz de Ojo Ciudadano.

Uso: uv run streamlit run src/ojo_ciudadano/app/main.py

Identidad visual (logo, paleta y reglas) en docs/marca.md; el tema está en .streamlit/config.toml.
Sin emojis: los iconos son de Material Symbols (`:material/nombre:`).
"""

import base64
from pathlib import Path

import streamlit as st

from ojo_ciudadano.app import datos, datos_contexto, ojo_cristal, textos
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

# Web ligera (D-043): sin barra lateral. Arriba, una barra con el logo, los botones de las
# partes principales y «Menú» con todas las pantallas; abajo del todo, el pie con el aviso, la
# metodología, las fuentes y las fechas de descarga.
INICIO = st.Page("paginas/inicio.py", title="Inicio", icon=":material/home:", default=True)
DINERO = st.Page(
    "paginas/mapa_general.py",
    title="A dónde va el dinero",
    icon=":material/payments:",
    url_path="mapa_general",
)
REVISAR = st.Page("paginas/alertas.py", title="Contratos a revisar", icon=":material/flag:")
ATIPICOS = st.Page(
    "paginas/atipicos.py", title="Contratos atípicos", icon=":material/scatter_plot:"
)
MAPA = st.Page("paginas/mapa.py", title="Mapa del dinero", icon=":material/account_tree:")
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


def intro() -> None:
    """Animación de entrada (3 s), solo la primera vez que se abre la web en la sesión."""
    if not st.session_state.get("intro_vista"):
        st.session_state["intro_vista"] = True
        st.html(INTRO)


def barra_superior() -> None:
    """Logo, botones de las partes principales y el menú con todas las pantallas."""
    with st.container(key="barra", horizontal=True, vertical_alignment="center", gap="small"):
        st.html(
            f'<div class="oc-marca"><img src="{LOGO}" alt="" width="30" height="30">'
            "<span>Ojo <b>Ciudadano</b></span></div>"
        )
        for pagina in PRINCIPALES:
            st.page_link(pagina, label=pagina.title, icon=pagina.icon)
        with st.popover("Menú", icon=":material/menu:"):
            for seccion, lista in SECCIONES.items():
                if seccion:
                    st.caption(seccion)
                for pagina in lista:
                    st.page_link(pagina, label=pagina.title, icon=pagina.icon)


# Notas de una pantalla concreta que también van al pie.
NOTAS_PIE = {ATIPICOS.url_path: ("Cómo se calculan los contratos atípicos", textos.AVISO_ATIPICOS)}


def pie(pagina) -> None:
    """Aviso, metodología, fuentes y fechas, abajo del todo en todas las pantallas."""
    with st.container(key="pie"):
        st.divider()
        st.caption(textos.AVISO_CORTO)
        if pagina.url_path in NOTAS_PIE:
            titulo, nota = NOTAS_PIE[pagina.url_path]
            with st.expander(titulo, icon=":material/info:"):
                st.markdown(nota)
        with st.expander("Aviso legal, metodología y fuentes", icon=":material/info:"):
            st.markdown(textos.AVISO)
            st.markdown(textos.NOTA_SENAL)
            st.markdown("**Qué mide cada indicador**")
            st.markdown(textos.lista_indicadores())
            st.markdown(textos.FUENTES)
            st.caption(textos.PIE)
        st.caption(
            textos.fechas_descarga(
                datos.fechas_datos(conexion()) + datos_contexto.fechas_contexto(conexion())
            )
        )


paginas = st.navigation(SECCIONES, position="hidden")
intro()
barra_superior()
# El pie se dibuja antes que la pantalla y el CSS lo coloca al final (order): así sale también
# cuando la pantalla se para pronto (st.stop) esperando una elección o por falta de datos.
pie(paginas)
paginas.run()
