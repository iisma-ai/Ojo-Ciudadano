"""Preguntas guiadas: las preguntas de demo del asistente con su consulta verificada.

Cada respuesta muestra qué cubre, la consulta SQL usada y el enlace a la fuente. Es también
la respuesta de respaldo de la demo mientras no esté conectado el modelo de lenguaje (D-010).
"""

import streamlit as st

from ojo_ciudadano.app import buscador, graficos, textos
from ojo_ciudadano.app.conexion import conexion
from ojo_ciudadano.app.tablas import mostrar_resultado
from ojo_ciudadano.asistente import sql_seguro
from ojo_ciudadano.asistente.consultas_demo import CONSULTAS_DEMO

st.header("Preguntas guiadas")
st.caption(
    "Preguntas frecuentes respondidas con consultas públicas sobre los datos oficiales. "
    "Cada respuesta indica qué cubre y qué no, y enseña la consulta SQL para comprobarla."
)

consulta = st.selectbox("Pregunta", CONSULTAS_DEMO, format_func=lambda c: c.pregunta)

parametros = {}
if "consejeria" in consulta.parametros:
    opciones = sql_seguro.ejecutar(
        conexion(),
        "SELECT DISTINCT consejeria FROM organo WHERE consejeria IS NOT NULL ORDER BY 1",
    )["filas"]
    parametros["consejeria"] = st.selectbox("Consejería", [f[0] for f in opciones])
if "empresa" in consulta.parametros:
    empresa = buscador.empresa("preguntas_empresa", "Empresa", valor="nif")
    buscador.esperar(empresa, "Escribe las primeras letras de la empresa y elígela de la lista.")
    parametros["empresa"] = empresa

resultado = sql_seguro.ejecutar(conexion(), consulta.sql, parametros)

figura, frase = graficos.automatico(resultado)
if frase:
    st.markdown(frase)
if figura is not None:
    st.plotly_chart(figura, config=graficos.CONFIG)
st.caption(consulta.nota)

st.markdown("**Los datos, con su enlace a la fuente**")
mostrar_resultado(resultado)

with st.expander("Consulta SQL usada"):
    st.code(consulta.sql.strip(), language="sql")
    if parametros:
        st.caption(f"Parámetros: {parametros}")
st.caption(textos.FUENTES)
