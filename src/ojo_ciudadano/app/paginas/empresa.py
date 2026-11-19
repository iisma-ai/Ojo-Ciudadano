"""Ficha de empresa: lo recibido por un adjudicatario y sus indicadores de riesgo."""

import streamlit as st

from ojo_ciudadano.app import datos, textos
from ojo_ciudadano.app.conexion import conexion

st.header("Ficha de empresa")
st.caption("Busca por nombre o NIF. Solo se muestran personas jurídicas.")

texto = st.text_input("Empresa", placeholder="Nombre o NIF (mínimo 3 caracteres)")
encontradas = datos.buscar_empresas(conexion(), texto)
if texto and not encontradas:
    st.info("Sin resultados.")

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
        c3.metric(
            "Nivel medio de señales",
            f"{ficha['puntuacion_ponderada']:.0%}",
            help="Media ponderada de los indicadores de riesgo activados sobre los aplicables "
            "en sus contratos. No mide legalidad ni calidad de gestión; con pocos indicadores "
            "aplicables es poco fiable.",
        )
    st.caption(
        "Importes adjudicados: "
        f"{(ficha['importe_sin_iva'] or 0):,.0f} € sin IVA (Plataforma de Contratación) y "
        f"{(ficha['importe_con_iva'] or 0):,.0f} € con IVA (portal de la Comunidad). "
        "Son fuentes distintas y no se suman. " + textos.FUENTES
    )

    tendencia = datos.tendencia_empresa(conexion(), ficha["adjudicatario_id"])
    if tendencia:
        st.caption(
            "Evolución anual de la proporción de señales activadas; depende del número y tipo "
            "de contratos de cada año y no mide la conducta de la empresa."
        )
        st.bar_chart({str(t["anio"]): t["puntuacion_ponderada"] or 0 for t in tendencia})

    st.subheader("Contratos")
    contratos = datos.contratos_empresa(conexion(), ficha["adjudicatario_id"])
    if len(contratos) == 200:
        st.caption("Se muestran los 200 contratos con más señales e importe.")
    for fila in contratos:
        titulo = fila["titulo"] or fila["contrato_id"]
        cabecera = textos.encabezado_contrato(
            titulo, fila["n_activados"], fila["n_aplicables"], fila["organo"]
        )
        with st.expander(cabecera):
            st.write(
                f"{fila['n_activados']} de {fila['n_aplicables']} indicadores aplicables "
                f"activados · {fila['anio'] or 'sin fecha'} · {fila['importe']:,.0f} €"
            )
            for m in datos.motivos(conexion(), fila["contrato_id"]):
                nombre = textos.NOMBRES_INDICADOR.get(m["indicador"], m["indicador"])
                valor = textos.formatear_valor(m["indicador"], m["valor"])
                st.markdown(f"- **{m['indicador']} · {nombre}** (valor: {valor}): {m['motivo']}")
            if fila["url_origen"]:
                st.link_button("Ver el expediente en la fuente oficial", fila["url_origen"])
            else:
                st.caption("Sin enlace oficial disponible para este contrato.")
