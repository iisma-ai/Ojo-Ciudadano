"""Interfaz de Ojo Ciudadano.

Uso: uv run streamlit run src/ojo_ciudadano/app/main.py

Identidad visual (logo, paleta y reglas) en docs/marca.md; el tema está en .streamlit/config.toml.
Sin emojis: los iconos son de Material Symbols (`:material/nombre:`).
"""

from pathlib import Path

import streamlit as st

from ojo_ciudadano.app import datos, datos_contexto, textos
from ojo_ciudadano.app.conexion import conexion

ESTATICOS = Path(__file__).parent / "static"

st.set_page_config(
    page_title="Ojo Ciudadano",
    page_icon=str(ESTATICOS / "logo.svg"),
    layout="wide",
)
st.logo(
    str(ESTATICOS / "logo-horizontal.svg"), icon_image=str(ESTATICOS / "logo.svg"), size="large"
)
st.html(f"<style>{(ESTATICOS / 'estilo.css').read_text(encoding='utf-8')}</style>")


def barra_lateral() -> None:
    """Metodología, fuentes y fechas en la barra lateral, fuera del contenido principal."""
    with st.sidebar:
        st.caption(textos.AVISO_CORTO)
        with st.popover("Metodología y fuentes", icon=":material/info:", width="stretch"):
            st.markdown(textos.AVISO)
            st.markdown("**Qué mide cada indicador**")
            st.markdown(textos.lista_indicadores())
        st.caption(
            textos.fechas_descarga(
                datos.fechas_datos(conexion()) + datos_contexto.fechas_contexto(conexion())
            )
        )
        with st.expander("Aviso legal y fuentes"):
            st.caption(textos.PIE)


paginas = st.navigation(
    {
        "": [
            st.Page("paginas/inicio.py", title="Inicio", icon=":material/home:", default=True),
        ],
        "Señales": [
            st.Page(
                "paginas/alertas.py",
                title="Contratos a revisar",
                icon=":material/flag:",
            ),
            st.Page(
                "paginas/atipicos.py", title="Contratos atípicos", icon=":material/scatter_plot:"
            ),
        ],
        "Explorar": [
            st.Page("paginas/mapa.py", title="Mapa del dinero", icon=":material/account_tree:"),
            st.Page(
                "paginas/contexto.py",
                title="Presupuesto y contexto",
                icon=":material/account_balance_wallet:",
            ),
            st.Page("paginas/empresa.py", title="Ficha de empresa", icon=":material/domain:"),
            st.Page(
                "paginas/organo.py", title="Ficha de órgano", icon=":material/account_balance:"
            ),
        ],
        "Preguntar": [
            st.Page("paginas/preguntas.py", title="Preguntas guiadas", icon=":material/quiz:"),
            st.Page("paginas/asistente.py", title="Asistente", icon=":material/forum:"),
        ],
    }
)
barra_lateral()
paginas.run()
