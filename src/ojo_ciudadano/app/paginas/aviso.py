"""Aviso legal, metodología y fuentes, en una pantalla propia (D-059).

Lo que antes iba en el pie y en la cabecera del asistente: qué significa una señal, qué mide cada
indicador, de dónde salen los datos (con sus fechas de descarga), cómo responde el asistente
(preguntas preparadas y modelo de lenguaje) y las preguntas que tienen respuesta preparada.
"""

import streamlit as st

from ojo_ciudadano.app import datos, datos_contexto, textos
from ojo_ciudadano.app.conexion import conexion
from ojo_ciudadano.asistente import respuestas_fijas

ASISTENTE = (
    "Puedes preguntar en tus palabras sobre los contratos y las subvenciones de la Comunidad de "
    "Madrid, sobre los datos de su catálogo de datos abiertos, sobre lo que dicen los pliegos de "
    "una licitación o sobre las resoluciones del Tribunal Administrativo de Contratación Pública. "
    "Las preguntas frecuentes tienen una respuesta preparada con una consulta comprobada de "
    "antemano; las demás las redacta un modelo de lenguaje, que puede equivocarse: comprueba "
    "siempre los datos y el enlace oficial que se muestran con cada respuesta. No escribas datos "
    "personales en tus preguntas."
)

st.header("Aviso legal, metodología y fuentes")
st.markdown(textos.AVISO_CORTO)
st.markdown(textos.AVISO)
st.markdown(textos.NOTA_SENAL)

st.subheader("Qué mide cada indicador")
st.markdown(textos.lista_indicadores())

st.subheader("El asistente")
st.markdown(ASISTENTE)
with st.expander("Preguntas con respuesta preparada", icon=":material/quiz:"):
    grupos: dict[str, list] = {}
    for fija in respuestas_fijas.FIJAS:
        grupos.setdefault(fija.grupo, []).append(fija)
    for grupo, fijas in grupos.items():
        st.markdown(f"**{grupo}**")
        st.markdown("\n".join(f"- {f.pregunta}" for f in fijas))

st.subheader("Fuentes")
st.markdown(textos.FUENTES)
st.caption(
    textos.fechas_descarga(
        datos.fechas_datos(conexion()) + datos_contexto.fechas_contexto(conexion())
    )
)
st.caption(textos.PIE)
