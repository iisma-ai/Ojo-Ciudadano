"""Preguntas guiadas: las preguntas de demo del asistente con su consulta verificada.

Cada respuesta muestra qué cubre, la consulta SQL usada y el enlace a la fuente. Es también
la respuesta de respaldo de la demo mientras no esté conectado el modelo de lenguaje (D-010).
"""

import streamlit as st

from ojo_ciudadano.app import textos
from ojo_ciudadano.app.conexion import conexion
from ojo_ciudadano.asistente import sql_seguro
from ojo_ciudadano.asistente.consultas_demo import CONSULTAS_DEMO

st.header("Preguntas guiadas")
st.write(
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
    parametros["empresa"] = st.text_input(
        "Empresa", placeholder="Nombre o NIF (mínimo 3 caracteres)"
    ).strip()
    if len(parametros["empresa"]) < 3:
        st.stop()

resultado = sql_seguro.ejecutar(conexion(), consulta.sql, parametros)
st.info(consulta.nota)

# Proporciones en porcentaje y enlaces clicables.
columnas_pct = [c for c in resultado["columnas"] if c.startswith(("proporcion", "modificaciones_"))]
filas = []
for fila in resultado["filas"]:
    registro = dict(zip(resultado["columnas"], fila, strict=True))
    for c in columnas_pct:
        if registro[c] is not None:
            registro[c] = 100 * registro[c]
    filas.append(registro)

if not filas:
    st.write("Sin resultados para esta pregunta.")
else:
    configuracion = {c: st.column_config.NumberColumn(format="%.1f %%") for c in columnas_pct}
    configuracion["url_origen"] = st.column_config.LinkColumn(
        "Expediente oficial", display_text="Ver ficha"
    )
    for c in resultado["columnas"]:
        if c.startswith("importe"):
            configuracion[c] = st.column_config.NumberColumn(format="localized")
    st.dataframe(filas, column_config=configuracion, hide_index=True)
    if resultado["recortado"]:
        st.caption(f"Se muestran las primeras {sql_seguro.LIMITE_FILAS} filas.")

with st.expander("Consulta SQL usada"):
    st.code(consulta.sql.strip(), language="sql")
    if parametros:
        st.caption(f"Parámetros: {parametros}")
st.caption(textos.AVISO_CORTO + " " + textos.FUENTES)
