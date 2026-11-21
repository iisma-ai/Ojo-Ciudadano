"""Ficha de empresa: cuánto ha recibido, de quién y con qué señales (D-023, A-05).

Primero se ve (cifras, mapa de áreas por organismo, contratos por año, señales), luego se lee
(lista de contratos desplegables). Solo personas jurídicas y UTE sin personas físicas (D-007).
"""

import streamlit as st

from ojo_ciudadano.app import datos, graficos, senales, textos
from ojo_ciudadano.app.conexion import conexion

FUENTES_REPARTO = {
    "placsp": "Contratos (Plataforma de Contratación, sin IVA)",
    "portal_cm": "Contratos (portal de la Comunidad, con IVA)",
    "bdns": "Subvenciones",
}
LIMITE_CONTRATOS = 30

con = conexion()
st.header("Ficha de empresa")
st.caption(
    "Qué contratos y subvenciones de la Comunidad de Madrid tiene una empresa o entidad, y de qué "
    "organismos."
)

texto = st.text_input("Buscar", placeholder="Nombre o NIF (mínimo 3 letras)")
encontradas = datos.buscar_empresas(con, texto)
if texto and not encontradas:
    st.info("No hay resultados. Solo se muestran empresas y entidades, no particulares.")
if not encontradas:
    st.stop()

elegida = st.selectbox(
    "Empresa",
    encontradas,
    format_func=lambda e: f"{e['nombre']} · {e['nif'] or e['adjudicatario_id']}",
)
ficha = datos.ficha_empresa(con, elegida["adjudicatario_id"])
if ficha is None:
    st.stop()
id_ = ficha["adjudicatario_id"]

st.subheader(ficha["nombre"])
st.caption(f"NIF {ficha['nif']}" if ficha["nif"] else "Unión temporal de empresas")

# --- Cifras ---
subvenciones = datos.subvenciones_empresa(con, id_)
cifras = st.columns(4)
cifras[0].metric("Contratos", textos.numero(ficha["n_contratos"]))
cifras[1].metric(
    "Contratos con alguna señal",
    textos.numero(ficha["n_con_alertas"]),
    help=textos.NOTA_SENAL,
)
importe_contratos = ficha["importe_sin_iva"] or ficha["importe_con_iva"]
cifras[2].metric(
    "Importe adjudicado (sin IVA)" if ficha["importe_sin_iva"] else "Importe adjudicado (con IVA)",
    textos.euros(importe_contratos),
    help="Plataforma de Contratación: "
    f"{textos.euros(ficha['importe_sin_iva'] or 0, 'sin IVA')}. Portal de la Comunidad: "
    f"{textos.euros(ficha['importe_con_iva'] or 0, 'con IVA')}. Son fuentes distintas "
    "y no se suman; la cifra grande es la de la Plataforma si la hay.",
)
cifras[3].metric(
    "Subvenciones",
    textos.euros(subvenciones[0]["importe_total"]) if subvenciones else "Ninguna",
)

# --- De quién recibe el dinero ---
st.subheader("De qué organismos")
reparto = datos.reparto_empresa(con, id_)
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
    filas = [r for r in reparto if r["fuente"] == fuente]
    st.caption(
        f"Cada rectángulo es un organismo; su tamaño, el importe adjudicado o concedido. "
        f"{len(filas)} organismos en total."
    )
    st.plotly_chart(graficos.reparto_organismos(filas), config=graficos.CONFIG)

# --- Contratos por año y señales ---
izquierda, derecha = st.columns(2)
tendencia = datos.tendencia_empresa(con, id_)
with izquierda:
    st.subheader("Contratos por año")
    if tendencia:
        st.plotly_chart(graficos.contratos_por_anio(tendencia), config=graficos.CONFIG)
        st.caption(textos.AVISO_MENORES_RECIENTES)
with derecha:
    st.subheader("Qué señales aparecen")
    senales_empresa = datos.senales_empresa(con, id_)
    if senales_empresa:
        st.plotly_chart(
            graficos.senales_de_empresa(senales_empresa, textos.SENAL_CORTA),
            config=graficos.CONFIG,
        )
        st.caption("Número de contratos de la empresa en los que se encontró cada señal.")
    else:
        st.markdown("No hemos encontrado ninguna señal en sus contratos.")

# --- Contratos ---
st.subheader("Sus contratos")
st.caption(
    f"Los {LIMITE_CONTRATOS} con más señales e importe. Pulsa uno para ver por qué tiene "
    "cada señal."
)
for fila in datos.contratos_empresa(con, id_, LIMITE_CONTRATOS):
    senales.tarjeta_contrato(con, fila, "empresa")

# --- Subvenciones ---
if subvenciones:
    st.subheader("Subvenciones")
    st.caption(
        "Fuente: [Base de Datos Nacional de Subvenciones]"
        "(https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones), datos descargados el "
        f"{subvenciones[0]['fecha_descarga']}. Cada enlace lleva a la convocatoria."
    )
    for sv in subvenciones:
        st.markdown(
            f"- [{sv['convocatoria'][:100]}]({sv['url_origen']}) · {sv['organo']} · "
            f"{textos.euros(sv['importe'])} en {sv['n_concesiones']} "
            f"{'concesión' if sv['n_concesiones'] == 1 else 'concesiones'}"
        )
