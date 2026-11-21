"""Portada: qué es Ojo Ciudadano en diez segundos (D-023, tareas A-01 y A-02)."""

import streamlit as st

from ojo_ciudadano.app import datos, textos
from ojo_ciudadano.app.conexion import conexion

con = conexion()

st.title("Ojo Ciudadano")
st.markdown(f"<p class='oc-entrada'>{textos.PRESENTACION}</p>", unsafe_allow_html=True)

resumen = datos.resumen_portada(con)
cifras = st.columns(4)
cifras[0].metric("Contratos analizados", f"{resumen['n_contratos']:,}".replace(",", "."))
cifras[1].metric("Subvenciones", textos.numero(resumen["n_concesiones"]))
cifras[2].metric("Organismos", textos.numero(resumen["n_organos"]))
cifras[3].metric("Contratos con alguna señal", textos.numero(resumen["n_con_senales"]))
st.caption(
    "Contratos y subvenciones de la Comunidad de Madrid de 2023 a 2026, de fuentes oficiales."
)

st.subheader("Qué puedes hacer")
puertas = st.columns(3)
for columna, (pagina, titulo, icono, frase) in zip(
    puertas,
    [
        (
            "paginas/alertas.py",
            "Ver contratos a revisar",
            ":material/flag:",
            "Los contratos con más señales, cada una explicada con un gráfico.",
        ),
        (
            "paginas/empresa.py",
            "Buscar una empresa",
            ":material/domain:",
            "Cuánto ha recibido una empresa en contratos y subvenciones, y de quién.",
        ),
        (
            "paginas/organo.py",
            "Ver un organismo",
            ":material/account_balance:",
            "Cómo contrata una consejería, un hospital o una empresa pública.",
        ),
    ],
    strict=True,
):
    with columna.container(border=True):
        st.page_link(pagina, label=titulo, icon=icono)
        st.caption(frase)

st.subheader("Qué señales buscamos")
st.caption(textos.NOTA_SENAL)
conteo = datos.conteo_senales(con)
indicadores = list(textos.SENAL_CORTA)
for fila in range(0, len(indicadores), 3):
    columnas = st.columns(3)
    for columna, indicador in zip(columnas, indicadores[fila : fila + 3], strict=False):
        with columna.container(border=True):
            st.markdown(f"{textos.ICONO_SENAL[indicador]} **{textos.SENAL_CORTA[indicador]}**")
            st.caption(textos.SENAL_FRASE[indicador])
            c = conteo.get(indicador)
            if c and c["comprobados"]:
                st.progress(
                    c["encontrados"] / c["comprobados"],
                    text=f"{textos.numero(c['encontrados'])} de "
                    f"{textos.numero(c['comprobados'])} contratos comprobados",
                )
