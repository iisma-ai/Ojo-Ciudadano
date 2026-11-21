"""Contratos atípicos respecto a contratos similares (detección de anomalías, D-021)."""

import streamlit as st

from ojo_ciudadano.app import datos, textos
from ojo_ciudadano.app.conexion import conexion

st.header("Contratos atípicos")
st.write(
    "Contratos que se alejan de otros similares según un modelo de aprendizaje automático. "
    "Es una señal experimental, distinta de los indicadores de riesgo."
)
st.info(textos.AVISO_ATIPICOS)

con = conexion()
if not datos.hay_anomalias(con):
    st.warning(
        "La base no tiene todavía la detección de anomalías. Se calcula con "
        "`uv run python -m ojo_ciudadano.anomalias.deteccion`."
    )
    st.stop()

grupos = datos.grupos_anomalias(con)
grupo = st.selectbox(
    "Grupo de contratos similares",
    [None, *(g["grupo"] for g in grupos)],
    format_func=lambda g: (
        "Todos"
        if g is None
        else next(
            f"{textos.nombre_grupo(g)} ({x['n_atipicos']} atípicos de {x['n_grupo']} contratos)"
            for x in grupos
            if x["grupo"] == g
        )
    ),
)

LIMITE = 100
filas = datos.atipicos(con, grupo, LIMITE)
agregados = datos.atipicos_agregados(con, grupo)
st.caption(
    (
        f"Se muestran los {LIMITE} más alejados de sus pares; elige un grupo para ver el resto."
        if len(filas) == LIMITE
        else f"{len(filas)} contratos mostrados, los más alejados de sus pares primero."
    )
    + (
        f" Otros {agregados} contratos atípicos de personas físicas u otros adjudicatarios "
        "sin ficha no se muestran uno a uno."
        if agregados
        else ""
    )
)

for fila in filas:
    titulo = fila["titulo"] or fila["contrato_id"]
    with st.expander(f"{titulo} · {fila['organo']}"):
        st.write(
            f"Comparado con {fila['n_grupo']} contratos de «{textos.nombre_grupo(fila['grupo'])}». "
            f"Más alejado de sus pares que el {fila['puntuacion']:.1%} de ellos "
            "(posición relativa, no una probabilidad)."
        )
        if fila["adjudicatarios"]:
            st.write(f"Adjudicatario: {fila['adjudicatarios']}")
        st.markdown(f"**Por qué se aleja:** {fila['motivo']}")
        if fila["url_origen"]:
            st.link_button("Ver el expediente en la fuente oficial", fila["url_origen"])
        else:
            st.caption("Sin enlace oficial disponible para este contrato.")
