"""Panel de alertas: contratos con más indicadores de riesgo activados."""

import streamlit as st

from ojo_ciudadano.app import datos, textos
from ojo_ciudadano.app.conexion import conexion

st.header("Panel de alertas")
st.write(
    "Contratos con más señales de riesgo activadas respecto a las que se pudieron calcular. "
    "Una señal no es una irregularidad."
)

col1, col2 = st.columns(2)
min_aplicables = col1.slider("Mínimo de indicadores aplicables", 1, 5, 3)
indicador = col2.selectbox(
    "Solo con este indicador activado",
    [None, *textos.NOMBRES_INDICADOR],
    format_func=lambda i: "Todos" if i is None else f"{i} · {textos.NOMBRES_INDICADOR[i]}",
)
if indicador:
    st.caption(textos.AYUDA_INDICADOR[indicador])

filas = datos.alertas(conexion(), min_aplicables, indicador)
st.caption(
    f"{len(filas)} contratos mostrados. Con pocos indicadores aplicables la puntuación "
    "es menos fiable: se muestra cuántos se pudieron calcular."
)

for fila in filas:
    titulo = fila["titulo"] or fila["contrato_id"]
    cabecera = textos.encabezado_contrato(
        titulo, fila["n_activados"], fila["n_aplicables"], fila["organo"]
    )
    with st.expander(cabecera):
        st.write(
            f"Proporción de indicadores activados: {fila['puntuacion']:.0%} (no es una "
            "probabilidad) "
            f"· {fila['tipo_contrato'] or 'tipo no indicado'} · {fila['procedimiento'] or ''} "
            f"· {fila['anio'] or 'sin fecha'}"
        )
        for m in datos.motivos(conexion(), fila["contrato_id"]):
            nombre = textos.NOMBRES_INDICADOR.get(m["indicador"], m["indicador"])
            valor = textos.formatear_valor(m["indicador"], m["valor"])
            st.markdown(f"- **{m['indicador']} · {nombre}** (valor: {valor}): {m['motivo']}")
        anomalia = datos.anomalia_contrato(conexion(), fila["contrato_id"])
        if anomalia:
            st.markdown(
                f"- **Contrato atípico** respecto a {anomalia['n_grupo']} contratos similares "
                f"(señal experimental, no suma a la puntuación): {anomalia['motivo']}"
            )
        if fila["url_origen"]:
            st.link_button("Ver el expediente en la fuente oficial", fila["url_origen"])
        else:
            st.caption("Sin enlace oficial disponible para este contrato.")
