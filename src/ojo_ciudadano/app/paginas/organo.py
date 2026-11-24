"""Ficha de organismo: a quién adjudica, cómo contrata y cómo se compara (D-023, A-06).

Primero se ve (cifras, mapa de áreas por empresa, comparación por señal, vías de contratación,
contratos por año), luego se lee (contratos desplegables). Las personas físicas solo
aparecen agregadas (D-007).
"""

import streamlit as st

from ojo_ciudadano.app import (
    buscador,
    datos,
    datos_contexto,
    datos_flujos,
    datos_mapa,
    graficos,
    graficos_contexto,
    senales,
    textos,
)
from ojo_ciudadano.app.conexion import conexion

FUENTES_REPARTO = {
    "placsp": "Contratos (Plataforma de Contratación, sin IVA)",
    "portal_cm": "Contratos (portal de la Comunidad, con IVA)",
    "bdns": "Subvenciones",
}
LIMITE_CONTRATOS = 20

con = conexion()
st.header("Ficha de organismo")
st.caption("Cómo contrata una consejería, un hospital o una empresa pública, y a quién adjudica.")

# Desde el buscador de la portada se llega con el organismo en la dirección (?organo=…).
elegido = buscador.organo("buscar_organo", "Buscar organismo") or st.query_params.get("organo")
buscador.esperar(
    elegido,
    "Escribe las primeras letras del nombre y elige un organismo de la lista "
    "(consejería, hospital, empresa pública…).",
)
ficha = datos.ficha_organo(con, elegido)
if ficha is None:
    st.stop()
id_ = ficha["organo_id"]

st.subheader(ficha["nombre"])
if ficha["consejeria"]:
    st.caption(ficha["consejeria"])

# --- Cifras ---
subvenciones = datos.subvenciones_organo(con, id_)
cifras = st.columns(4)
cifras[0].metric("Contratos", textos.numero(ficha["n_contratos"]))
cifras[1].metric(
    "Contratos con alguna señal", textos.numero(ficha["n_con_alertas"]), help=textos.NOTA_SENAL
)
cifras[2].metric(
    "Importe adjudicado (sin IVA)" if ficha["importe_sin_iva"] else "Importe adjudicado (con IVA)",
    textos.euros(ficha["importe_sin_iva"] or ficha["importe_con_iva"]),
    help="Plataforma de Contratación: "
    f"{textos.euros(ficha['importe_sin_iva'] or 0, 'sin IVA')}. Portal de la Comunidad: "
    f"{textos.euros(ficha['importe_con_iva'] or 0, 'con IVA')}. Son fuentes distintas "
    "y no se suman; la cifra grande es la de la Plataforma si la hay.",
)
cifras[3].metric(
    "Subvenciones concedidas",
    textos.euros(subvenciones["importe"]) if subvenciones else "Ninguna",
)

# --- A quién adjudica ---
st.subheader("A quién adjudica")
reparto = datos.reparto_organo(con, id_)
fuentes = [f for f in FUENTES_REPARTO if any(r["fuente"] == f for r in reparto)]
if fuentes:
    fuente = (
        st.segmented_control(
            "Fuente",
            fuentes,
            default=max(
                fuentes, key=lambda f: sum(r["importe"] for r in reparto if r["fuente"] == f)
            ),
            format_func=FUENTES_REPARTO.get,
            label_visibility="collapsed",
        )
        or fuentes[0]
    )
    filas = sorted(
        (r for r in reparto if r["fuente"] == fuente), key=lambda r: r["importe"], reverse=True
    )
    principales = 20
    parte = sum(r["importe"] for r in filas[:principales]) / sum(r["importe"] for r in filas)
    st.caption(
        "Cada rectángulo es una empresa o entidad; su tamaño, el importe adjudicado o "
        f"concedido. Se muestran las {min(principales, len(filas))} con más importe, que suman "
        f"el {textos.porcentaje(parte)} del total ({textos.numero(len(filas))} en total). Las "
        "personas físicas van juntas en gris y sin nombre."
    )
    st.plotly_chart(
        graficos.reparto_organismos(
            filas,
            maximo=principales,
            campo="nombre",
            gris=(datos.AGREGADO_PERSONAS,),
            agrupar_resto=False,
        ),
        config=graficos.CONFIG,
    )
    st.caption(
        "Que una empresa reciba mucho de un organismo puede tener causas legítimas (mercado "
        "pequeño, proveedor único); no implica trato de favor."
    )

# --- Presupuesto (solo consejerías con datos liquidados, D-024) ---
ejecucion = datos_contexto.ejecucion_organo(con, id_) if datos_contexto.hay_contexto(con) else []
if ejecucion:
    ultimo = ejecucion[-1]
    st.subheader("Presupuesto de la consejería")
    st.markdown(
        f"En {ultimo['anio']}, esta consejería reconoció "
        f"**{textos.euros(ultimo['obligaciones'])}** de gasto sobre un crédito de "
        f"{textos.euros(ultimo['credito_actual'])}."
    )
    propia = next(
        (e for e in datos_mapa.reparto(con, ultimo["anio"])["entidades"] if e["organo_id"] == id_),
        None,
    )
    if propia and propia["gastado"]:
        k = st.columns(4)
        k[0].metric("Gastado sobre lo disponible", textos.porcentaje(propia["llenado"], 1))
        k[1].metric("Sin gastar", textos.millones(propia["sin_gastar"]))
        for columna, titulo, clave in (
            (k[2], "Contratos (Plataforma, sin IVA)", "contratos_plataforma"),
            (k[3], "Subvenciones concedidas", "subvenciones"),
        ):
            columna.metric(
                titulo,
                textos.millones(propia[clave]),
                delta=f"{textos.porcentaje((propia[clave] or 0) / propia['gastado'], 1)} del gasto",
                delta_color="off",
                help="Con fecha de "
                f"{ultimo['anio']}, de sus órganos, sobre el gasto reconocido de la consejería. "
                "Son fuentes distintas: orden de magnitud, no una resta.",
            )
    st.plotly_chart(graficos_contexto.ejecucion_organo(ejecucion), config=graficos.CONFIG)
    st.caption(
        f"Fuente: [Datos abiertos de la Comunidad de Madrid]({ultimo['url_origen']}). "
        + textos.AVISO_CONTEXTO
    )

# --- Comparación y vías ---
izquierda, derecha = st.columns(2)
with izquierda:
    st.subheader("Comparado con los demás")
    comparacion = datos.indicadores_organo(con, id_)
    if comparacion:
        st.plotly_chart(
            graficos.comparacion_senales(comparacion, textos.SENAL_CORTA), config=graficos.CONFIG
        )
        st.caption(
            "Proporción de sus contratos con cada señal (azul) frente a todos los organismos "
            "(gris). Depende del tipo de gasto: los hospitales, por ejemplo, compran mucho y "
            "a menudo."
        )
with derecha:
    st.subheader("Cómo contrata")
    vias = datos.procedimientos_organo(con, id_)
    if vias:
        st.plotly_chart(
            graficos.procedimientos(vias, textos.PROCEDIMIENTO_LLANO), config=graficos.CONFIG
        )
        st.caption("Número de contratos por cada vía de adjudicación.")

tendencia = datos.tendencia_organo(con, id_)
if tendencia:
    st.subheader("Contratos por año")
    st.plotly_chart(graficos.contratos_por_anio(tendencia), config=graficos.CONFIG)
    st.caption(textos.AVISO_MENORES_RECIENTES)

# --- Contratos ---
st.subheader("Contratos a revisar de este organismo")
contratos = datos.alertas(con, 3, None, LIMITE_CONTRATOS, organo_id=id_) or datos.alertas(
    con, 1, None, LIMITE_CONTRATOS, organo_id=id_
)
if contratos:
    st.caption("Los que tienen más señales. Pulsa uno para ver por qué.")
    for fila in contratos:
        senales.tarjeta_contrato(con, fila, "organo")
else:
    st.markdown("No hemos encontrado señales en sus contratos.")

# --- Subvenciones ---
if subvenciones:
    with st.expander(
        f"Subvenciones: {textos.numero(subvenciones['n_concesiones'])} concesiones por "
        f"{textos.euros(subvenciones['importe'])}",
        icon=":material/volunteer_activism:",
    ):
        st.caption(
            "Fuente: [Base de Datos Nacional de Subvenciones]"
            "(https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones), datos descargados "
            f"el {subvenciones['fecha_descarga']}. Las concesiones a personas físicas "
            f"({textos.numero(subvenciones['n_agregado'])}) solo se muestran sumadas. Cada "
            "enlace lleva a la convocatoria."
        )
        for cv in datos.convocatorias_organo(con, id_):
            titulo = (cv["convocatoria"] or "Convocatoria sin título")[:90]
            enlace = f"[{titulo}]({cv['url_origen']})" if cv["url_origen"] else titulo
            st.markdown(
                f"- {enlace}: {textos.euros(cv['importe'])} "
                f"({textos.numero(cv['n_concesiones'])} concesiones)"
            )

# --- Encargos a medios propios (D-028) ---
encargos = datos_flujos.encargos_organo(con, id_)
if encargos:
    with st.expander(
        f"Encargos a medios propios: {textos.numero(encargos['n_encargos'])} por "
        f"{textos.euros(encargos['importe'], 'con IVA')}",
        icon=":material/handshake:",
    ):
        st.caption(
            textos.AVISO_ENCARGOS
            + " Fuente: [Portal de la Contratación Pública de la Comunidad de Madrid]"
            "(https://contratos-publicos.comunidad.madrid/contratos), datos descargados el "
            f"{encargos['fecha_descarga']}. Cada enlace lleva a la ficha oficial del encargo."
        )
        st.markdown(
            "**A qué entidades:** "
            + "; ".join(f"{m} ({textos.euros(i)})" for m, i in encargos["por_medio_propio"][:5])
        )
        for e in encargos["lista"][:LIMITE_CONTRATOS]:
            titulo = (e["titulo"] or "Encargo sin título")[:90]
            st.markdown(
                f"- [{titulo}]({e['url_origen']}) · {e['medio_propio']} · "
                f"{textos.euros(e['importe'], 'con IVA')} · {e['anio']}"
            )
