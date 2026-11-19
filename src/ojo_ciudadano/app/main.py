"""Interfaz de Ojo Ciudadano.

Uso: uv run streamlit run src/ojo_ciudadano/app/main.py
"""

import streamlit as st

from ojo_ciudadano.app import datos, textos
from ojo_ciudadano.app.conexion import conexion

st.set_page_config(page_title="Ojo Ciudadano", page_icon="👁️", layout="wide")


def cabecera() -> None:
    st.title("Ojo Ciudadano")
    st.caption(f"Datos descargados el {datos.fecha_datos(conexion())}. {textos.PIE}")
    st.info(textos.AVISO_CORTO)
    with st.expander("Metodología y fuentes", expanded=False):
        st.markdown(textos.AVISO)


paginas = st.navigation(
    [
        st.Page("paginas/alertas.py", title="Panel de alertas", default=True),
        st.Page("paginas/empresa.py", title="Ficha de empresa"),
        st.Page("paginas/organo.py", title="Ficha de órgano"),
        st.Page("paginas/mapa.py", title="Mapa del dinero"),
    ]
)
cabecera()
paginas.run()
