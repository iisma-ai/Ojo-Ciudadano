"""Ficha de empresa: lo recibido por un adjudicatario y sus indicadores de riesgo."""

import streamlit as st

from ojo_ciudadano.app import datos, textos
from ojo_ciudadano.app.conexion import conexion

st.header("Ficha de empresa")
st.caption("Busca por nombre o NIF. No hay fichas de personas físicas.")

texto = st.text_input("Empresa", placeholder="Nombre o NIF (mínimo 3 caracteres)")
encontradas = datos.buscar_empresas(conexion(), texto)
if texto and not encontradas:
    st.info("Sin resultados. Las personas físicas no tienen ficha.")

elegida = st.selectbox(
    "Resultados",
    encontradas,
    format_func=lambda e: (
        f"{e['nombre']} ({e['nif'] or e['adjudicatario_id']}) · {e['n_contratos']} contratos"
    ),
)

if elegida:
    ficha = datos.ficha_empresa(conexion(), elegida["adjudicatario_id"])
    st.subheader(ficha["nombre"])
    c1, c2, c3 = st.columns(3)
    c1.metric("Contratos", f"{ficha['n_contratos']:,}".replace(",", "."))
    c2.metric("Con alguna alerta", f"{ficha['n_con_alertas']:,}".replace(",", "."))
    if ficha["puntuacion_ponderada"] is not None:
        c3.metric("Puntuación ponderada", f"{ficha['puntuacion_ponderada']:.0%}")
    st.caption(
        "Importes adjudicados: "
        f"{(ficha['importe_sin_iva'] or 0):,.0f} € sin IVA (Plataforma de Contratación) y "
        f"{(ficha['importe_con_iva'] or 0):,.0f} € con IVA (portal de la Comunidad). "
        "Son fuentes distintas y no se suman."
    )

    tendencia = datos.tendencia_empresa(conexion(), ficha["adjudicatario_id"])
    if tendencia:
        st.bar_chart({str(t["anio"]): t["puntuacion_ponderada"] or 0 for t in tendencia})

    st.subheader("Contratos")
    for fila in datos.contratos_empresa(conexion(), ficha["adjudicatario_id"]):
        titulo = fila["titulo"] or fila["contrato_id"]
        with st.expander(f"{fila['puntuacion']:.0%} · {titulo[:90]} · {fila['organo']}"):
            st.write(
                f"{fila['n_activados']} de {fila['n_aplicables']} indicadores aplicables "
                f"activados · {fila['anio'] or 'sin fecha'} · {fila['importe']:,.0f} €"
            )
            for m in datos.motivos(conexion(), fila["contrato_id"]):
                nombre = textos.NOMBRES_INDICADOR.get(m["indicador"], m["indicador"])
                st.markdown(f"- **{m['indicador']} · {nombre}**: {m['motivo']}")
            st.link_button("Ver el expediente en la fuente oficial", fila["url_origen"])
