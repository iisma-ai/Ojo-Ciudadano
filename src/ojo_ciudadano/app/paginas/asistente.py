"""Asistente: preguntas en lenguaje natural respondidas con SQL validado (docs/05-asistente.md).

Cada respuesta enseña las consultas usadas y sus resultados con enlace a la fuente. Mientras no
haya modelo de lenguaje conectado (D-010), la pantalla lo dice y remite a las preguntas guiadas.
"""

import streamlit as st

from ojo_ciudadano.app import textos
from ojo_ciudadano.app.conexion import conexion
from ojo_ciudadano.app.tablas import mostrar_resultado
from ojo_ciudadano.asistente import agente, bateria

# Qué se muestra en lugar de una respuesta retenida (agente.RETENCION_*).
RETENIDAS = {
    agente.RETENCION_DNI: (
        "Esta respuesta no se muestra porque podía contener datos de personas físicas, que la "
        "plataforma no publica (RGPD). Puedes preguntar por datos agregados."
    ),
    agente.RETENCION_LENGUAJE: (
        "Esta respuesta se ha retenido porque usaba expresiones que la plataforma no emplea. "
        "Ojo Ciudadano solo muestra indicadores de riesgo: señalan contratos que merecen "
        "revisión y no prueban ninguna irregularidad. Prueba a reformular la pregunta."
    ),
    agente.RETENCION_CIFRAS: (
        "Esta respuesta se ha retenido porque daba cifras sin haberlas consultado en la base. "
        "Prueba a reformular la pregunta."
    ),
}


def texto_visible(respuesta: agente.Respuesta) -> str:
    """Lo que ve la persona (y lo que vuelve al modelo en el historial)."""
    return RETENIDAS.get(respuesta.retencion, respuesta.texto)


st.header("Asistente")
st.write(
    "Pregunta en tus palabras sobre los contratos y las subvenciones de la Comunidad de Madrid. "
    "El asistente consulta los datos oficiales y te enseña la consulta y los datos que usa, "
    "con el enlace a la fuente, para que puedas comprobar la respuesta. Las respuestas las "
    "redacta automáticamente un modelo de lenguaje y pueden contener errores: compruébalas "
    "siempre en los datos y en el enlace oficial. No escribas datos personales en tus preguntas."
)
st.caption(textos.AVISO_CORTO)

modelo = agente.modelo_configurado()
if modelo is None:
    st.info(
        "El asistente todavía no está conectado a un modelo de lenguaje. Mientras tanto, las "
        "preguntas guiadas responden a las preguntas más frecuentes con consultas verificadas."
    )
    st.page_link("paginas/preguntas.py", label="Ir a las preguntas guiadas", icon="➡️")
    with st.expander("Ejemplos de preguntas que podrá responder"):
        st.markdown("\n".join(f"- {p.pregunta}" for p in bateria.BATERIA if p.sql))
    st.stop()


def mostrar_respuesta(respuesta: agente.Respuesta) -> None:
    if respuesta.retencion:
        st.warning(texto_visible(respuesta))
        return
    st.markdown(respuesta.texto)
    for numero, consulta in enumerate(respuesta.consultas, start=1):
        with st.expander(f"Datos de la consulta {numero}"):
            mostrar_resultado(consulta)
            if "fuente" not in consulta["columnas"]:
                st.caption(
                    "Esta consulta no incluye la columna de fuente: consulta las fuentes al pie "
                    "de la página."
                )
            if "contrato_id" in consulta["columnas"] and "url_origen" not in consulta["columnas"]:
                st.caption("Esta consulta no incluye el enlace oficial de cada contrato.")
            st.code(consulta["sql"].strip(), language="sql")
    st.caption(textos.AVISO_CORTO)


turnos = st.session_state.setdefault("turnos_asistente", [])
for pregunta, respuesta in turnos:
    st.chat_message("user").write(pregunta)
    with st.chat_message("assistant"):
        mostrar_respuesta(respuesta)

if pregunta := st.chat_input("Escribe tu pregunta"):
    st.chat_message("user").write(pregunta)
    historial = []
    for anterior, respuesta in turnos:
        historial += [
            {"rol": "usuario", "contenido": anterior},
            {"rol": "modelo", "contenido": texto_visible(respuesta)},
        ]
    with st.chat_message("assistant"):
        with st.spinner("Consultando los datos…"):
            respuesta = agente.responder(conexion(), modelo, pregunta, historial)
        mostrar_respuesta(respuesta)
    turnos.append((pregunta, respuesta))

st.caption(textos.FUENTES)
