"""Ficha de empresa: cuánto ha recibido, de quién y con qué señales (D-023, A-05).

Primero se ve (cifras, mapa de áreas por organismo, contratos por año, señales), luego se lee
(lista de contratos desplegables). Solo personas jurídicas y UTE sin personas físicas (D-007).
"""

import streamlit as st

from ojo_ciudadano.app import (
    buscador,
    datos,
    datos_contexto,
    datos_flujos,
    graficos,
    senales,
    textos,
)
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

# Desde el buscador de la portada se llega con la empresa en la dirección (?empresa=…); lo que
# se elija aquí manda solo si se acaba de elegir (D-058).
elegida = buscador.con_direccion(
    buscador.empresa("buscar_empresa", "Buscar empresa o entidad"), "empresa", "buscar_empresa"
)
buscador.esperar(
    elegida,
    "Escribe las primeras letras del nombre (o el NIF) y elige una empresa de la lista. "
    "Solo aparecen empresas y entidades con contratos o subvenciones, no particulares.",
)
ficha = datos.ficha_empresa(con, elegida)
if ficha is None:
    st.stop()
id_ = ficha["adjudicatario_id"]

st.subheader(ficha["nombre"])
st.caption(f"NIF {ficha['nif']}" if ficha["nif"] else "Unión temporal de empresas")
publico = datos_flujos.sector_publico(con, ficha["nif"], ficha["nombre"])
if publico:
    fuente_invente = (
        f"Fuente: [Inventario de Entes del Sector Público (INVENTE)]({publico['url_origen']}), "
        f"Intervención General de la Administración del Estado, descargado el "
        f"{publico['fecha_descarga']}."
    )
    if publico["nombre_compatible"]:
        st.info(
            f"**Ente del sector público**, no una empresa privada: {publico['forma_juridica']}"
            f" ({publico['administracion'] or 'administración sin indicar'}). Los contratos "
            f"entre entes públicos tienen otras reglas. {fuente_invente}",
            icon=":material/account_balance:",
        )
    else:
        st.caption(
            f"El NIF de esta ficha corresponde en el inventario del sector público a "
            f"«{publico['nombre']}» ({publico['forma_juridica']}). Puede ser un nombre "
            f"abreviado o un error de NIF en la fuente de los contratos. {fuente_invente}"
        )

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

# --- Registros de la Comunidad (D-024) ---
registros = (
    datos_contexto.registros_de_empresa(con, ficha["nif"])
    if datos_contexto.hay_contexto(con)
    else []
)
if registros:
    st.subheader("En qué registros de la Comunidad figura")
    for r in registros:
        nombre = datos_contexto.NOMBRE_REGISTRO[r["registro"]]
        detalle = f" ({r['detalle']})" if r["detalle"] else ""
        st.markdown(
            f"- [{nombre}]({r['url_origen']}){detalle} · descargado el {r['fecha_descarga']}"
        )
    st.caption(textos.AVISO_REGISTROS)

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

# --- Contratos por año, señales y contratos (solo si tiene contratos) ---
if not ficha["n_contratos"]:
    st.markdown(
        "No tiene contratos en nuestros datos: aparece por sus subvenciones o por los encargos "
        "que recibe como medio propio."
    )
else:
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

# --- Encargos recibidos como medio propio (D-028) ---
encargos = datos_flujos.encargos_empresa(con, id_)
if encargos:
    st.subheader("Encargos recibidos como medio propio")
    st.markdown(
        f"**{textos.numero(encargos['n_encargos'])} encargos** por "
        f"**{textos.euros(encargos['importe'], 'con IVA')}** de "
        f"{textos.numero(len(encargos['por_organo']))} organismos."
    )
    for o in encargos["por_organo"][:10]:
        st.markdown(
            f"- {o['organo']}: {textos.euros(o['importe'], 'con IVA')} "
            f"({textos.numero(o['n_encargos'])})"
        )
    st.caption(
        textos.AVISO_ENCARGOS
        + " Fuente: [Portal de la Contratación Pública de la Comunidad de Madrid]"
        "(https://contratos-publicos.comunidad.madrid/contratos), datos descargados el "
        f"{encargos['fecha_descarga']}. El detalle de cada encargo está en la ficha del organismo."
    )
