"""Contratos atípicos respecto a contratos similares (detección de anomalías, D-021)."""

import streamlit as st

from ojo_ciudadano.app import datos, graficos, textos
from ojo_ciudadano.app.conexion import conexion

st.header("Contratos atípicos")
st.caption(
    "Contratos que se alejan de otros similares según un modelo de aprendizaje automático. "
    "Señal experimental, aparte de los indicadores: atípico no significa irregular."
)
with st.expander("Cómo se calcula", icon=":material/info:"):
    st.markdown(textos.AVISO_ATIPICOS)

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
    if len(titulo) > 110:
        titulo = titulo[:107].rstrip() + "…"
    desplegable = st.expander(
        f"**{titulo}**  \n:gray[{fila['organo']}]",
        key=f"atipico-{fila['contrato_id']}",
        on_change="rerun",
    )
    with desplegable:
        st.markdown(f"**Por qué se aleja:** {fila['motivo']}")
        if not desplegable.open:
            continue
        pares = datos.pares_anomalia(con, fila["contrato_id"])
        if pares and pares["pares"]:
            variables = (fila["variables"] or "").split(", ")
            st.plotly_chart(
                graficos.atipico(pares, variables),
                config=graficos.CONFIG,
                key=f"grafico-atipico-{fila['contrato_id']}",
            )
            st.caption(
                f"El punto azul es este contrato; los grises, una muestra de los "
                f"{textos.numero(fila['n_grupo'])} contratos de «"
                f"{textos.nombre_grupo(fila['grupo'])}». Está más alejado de ellos que el "
                f"{textos.porcentaje(fila['puntuacion'], 1)} (posición relativa, no una "
                "probabilidad)."
            )
        if fila["adjudicatarios"]:
            st.caption(f"Adjudicataria: {fila['adjudicatarios']}")
        if fila["url_origen"]:
            st.link_button(
                "Ver el expediente oficial", fila["url_origen"], icon=":material/open_in_new:"
            )
        else:
            st.caption("Sin enlace oficial disponible para este contrato.")
