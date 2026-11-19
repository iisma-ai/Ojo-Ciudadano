"""Panel de alertas: contratos con más indicadores de riesgo activados."""

import streamlit as st

from ojo_ciudadano.app import datos, textos
from ojo_ciudadano.app.conexion import conexion

st.header("Panel de alertas")
st.write("Contratos ordenados por la proporción de indicadores de riesgo activados.")

col1, col2 = st.columns(2)
min_aplicables = col1.slider("Mínimo de indicadores aplicables", 1, 5, 3)
indicador = col2.selectbox(
    "Solo con este indicador activado",
    [None, *textos.NOMBRES_INDICADOR],
    format_func=lambda i: "Todos" if i is None else f"{i} · {textos.NOMBRES_INDICADOR[i]}",
)

filas = datos.alertas(conexion(), min_aplicables, indicador)
st.caption(
    f"{len(filas)} contratos mostrados. Con pocos indicadores aplicables la puntuación "
    "es menos fiable: se muestra cuántos se pudieron calcular."
)

for fila in filas:
    titulo = fila["titulo"] or fila["contrato_id"]
    with st.expander(f"{fila['puntuacion']:.0%} · {titulo[:90]} · {fila['organo']}"):
        st.write(
            f"{fila['n_activados']} de {fila['n_aplicables']} indicadores aplicables activados "
            f"· {fila['tipo_contrato'] or 'tipo no indicado'} · {fila['procedimiento'] or ''} "
            f"· {fila['anio'] or 'sin fecha'}"
        )
        for m in datos.motivos(conexion(), fila["contrato_id"]):
            nombre = textos.NOMBRES_INDICADOR.get(m["indicador"], m["indicador"])
            valor = "—" if m["valor"] is None else format(m["valor"], ".3g")
            st.markdown(f"- **{m['indicador']} · {nombre}** (valor {valor}): {m['motivo']}")
        st.link_button("Ver el expediente en la fuente oficial", fila["url_origen"])
