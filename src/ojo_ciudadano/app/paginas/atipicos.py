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

LIMITE = 100
con_errores = st.toggle(
    "Mostrar posibles errores de datos",
    help=textos.AYUDA_POSIBLES_ERRORES,
    value=False,
)
grupos = datos.grupos_anomalias(con)
with st.expander("Filtros y orden", icon=":material/tune:"):
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
    fila1 = st.columns(2)
    orden = fila1[0].selectbox(
        "Ordenar por", list(textos.ORDEN_ATIPICOS), format_func=textos.ORDEN_ATIPICOS.get
    )
    variable = fila1[1].selectbox(
        "Se aleja en",
        [None, *graficos.NOMBRE_VARIABLE],
        format_func=lambda v: "Cualquier variable" if v is None else graficos.NOMBRE_VARIABLE[v],
        help="La variable en la que el contrato más se aleja de sus pares.",
    )
    texto = st.text_input(
        "Buscar", placeholder="Organismo, empresa o título", help="Parte del nombre."
    ).strip()
    nivel = st.slider(
        "Nivel mínimo de lejanía",
        min_value=99.0,
        max_value=100.0,
        value=99.0,
        step=0.1,
        format="%.1f %%",
        help="Deja solo los contratos más alejados de sus pares que este porcentaje de ellos. "
        "El 99 % es el mínimo: todos los atípicos lo superan.",
    )
minimo = nivel / 100
activos = [
    etiqueta
    for etiqueta, activo in (
        ("grupo", grupo is not None),
        ("orden", orden != "mas_atipico"),
        ("variable", variable is not None),
        ("búsqueda", bool(texto)),
        ("nivel mínimo", nivel > 99.0),
    )
    if activo
]
if activos:
    st.caption("Filtros activos: " + ", ".join(activos) + ".")
filas = datos.atipicos(
    con,
    grupo,
    LIMITE,
    orden=orden,
    min_puntuacion=minimo,
    con_errores=con_errores,
    variable=variable,
    texto=texto or None,
)
agregados = datos.atipicos_agregados(con, grupo, minimo)
ocultos = 0 if con_errores else datos.atipicos_errores_ocultos(con, grupo, minimo)
if ocultos:
    st.info(textos.aviso_errores_ocultos(ocultos), icon=":material/visibility_off:")
if not filas:
    st.info("No hay contratos atípicos con estos filtros.")
    st.stop()
st.caption(
    (
        f"Se muestran los {LIMITE} primeros con estos filtros; afina con el grupo, el nivel "
        "mínimo o la búsqueda."
        if len(filas) == LIMITE
        else f"{len(filas)} contratos mostrados."
    )
    + (
        f" Otros {agregados} contratos atípicos de personas físicas u otros adjudicatarios "
        "sin ficha no se muestran uno a uno."
        if agregados and not texto and variable is None
        else ""
    )
)

for fila in filas:
    titulo = fila["titulo"] or fila["contrato_id"]
    if len(titulo) > 110:
        titulo = titulo[:107].rstrip() + "…"
    desplegable = st.expander(
        f"**{titulo}**  \n:gray[{fila['organo']}]"
        + ("  :orange[posible error de datos]" if fila["posible_error"] else ""),
        key=f"atipico-{fila['contrato_id']}",
        on_change="rerun",
    )
    with desplegable:
        if fila["posible_error"]:
            st.warning(
                "Posible error al introducir los datos en la fuente: "
                + textos.AYUDA_POSIBLES_ERRORES,
                icon=":material/error:",
            )
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
