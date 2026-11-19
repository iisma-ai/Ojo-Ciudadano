"""Ficha de órgano: cómo contrata un órgano y cómo se compara con los demás."""

import streamlit as st

from ojo_ciudadano.app import datos, textos
from ojo_ciudadano.app.conexion import conexion

st.header("Ficha de órgano")

texto = st.text_input("Órgano", placeholder="Nombre (vacío: los de más contratos)")
encontrados = datos.buscar_organos(conexion(), texto)
elegido = st.selectbox(
    "Resultados",
    encontrados,
    format_func=lambda o: f"{o['nombre']} · {o['n_contratos']} contratos",
)

if elegido:
    ficha = datos.ficha_organo(conexion(), elegido["organo_id"])
    st.subheader(ficha["nombre"])
    if ficha["consejeria"]:
        st.caption(f"Consejería: {ficha['consejeria']}")
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
    if ficha["percentil"] is not None:
        st.caption(
            f"Su puntuación es igual o superior a la del {ficha['percentil']:.0%} de los "
            f"{ficha['n_comparables']} órganos con al menos 100 contratos puntuados. "
            "Es una comparación entre órganos, no una valoración de su gestión: depende "
            "del tipo de gasto (p. ej. los hospitales compran de forma recurrente)."
        )
    st.caption(
        "Importes adjudicados: "
        f"{(ficha['importe_sin_iva'] or 0):,.0f} € sin IVA (Plataforma de Contratación) y "
        f"{(ficha['importe_con_iva'] or 0):,.0f} € con IVA (portal de la Comunidad). "
        "Son fuentes distintas y no se suman. " + textos.FUENTES
    )

    st.subheader("Indicadores frente al conjunto de órganos")
    for i in datos.indicadores_organo(conexion(), ficha["organo_id"]):
        nombre = textos.NOMBRES_INDICADOR.get(i["indicador"], i["indicador"])
        st.write(
            f"**{i['indicador']} · {nombre}**: {i['pct_organo']:.1%} de {i['aplicables']} "
            f"contratos aplicables activados (en total: {i['pct_global']:.1%})"
        )

    tendencia = datos.tendencia_organo(conexion(), ficha["organo_id"])
    if tendencia:
        st.subheader("Evolución anual de la puntuación")
        st.caption(
            "Proporción anual de señales activadas; depende del número y tipo de contratos de "
            "cada año y no mide la gestión del órgano."
        )
        st.bar_chart({str(t["anio"]): t["puntuacion_ponderada"] or 0 for t in tendencia})

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Procedimientos")
        for p in datos.procedimientos_organo(conexion(), ficha["organo_id"]):
            st.write(f"{p['procedimiento']}: {p['n_contratos']:,}".replace(",", "."))
    with col_b:
        st.subheader("Empresas con más contratos adjudicados (recuento)")
        st.caption(
            "Que una empresa concentre contratos en un órgano es una señal de dependencia que "
            "puede tener causas legítimas (mercado reducido, exclusividad); no implica trato "
            "de favor."
        )
        for e in datos.proveedores_organo(conexion(), ficha["organo_id"]):
            st.write(
                f"{e['nombre']} ({e['nif']}): {e['n_contratos']:,} contratos".replace(",", ".")
            )
    st.caption("Las personas físicas no aparecen: no hay fichas ni listados individuales.")
