"""Contratos a revisar: los que tienen alguna señal, con un gráfico por señal (D-023, A-03).

Cada contrato es un desplegable: al pulsar en cualquier parte se abre con sus gráficos, que
solo se calculan entonces.
"""

import streamlit as st

from ojo_ciudadano.app import buscador, datos, senales, textos
from ojo_ciudadano.app.conexion import conexion

LIMITE = 30

con = conexion()
st.header("Contratos a revisar")
st.caption("Contratos en los que hemos encontrado alguna señal. " + textos.NOTA_SENAL)

conteo = datos.conteo_senales(con)
fila1 = st.columns([3, 3, 2])
texto = (
    fila1[0]
    .text_input("Buscar", placeholder="Palabra del título u organismo (vacuna, Metro, hospital…)")
    .strip()
)
elegidas = fila1[1].multiselect(
    "Qué se ha detectado",
    list(textos.SENAL_CORTA),
    help=textos.GLOSARIO["senal"],
    placeholder="Todas las señales",
    format_func=lambda i: (
        f"{textos.SENAL_CORTA[i]} ({textos.numero(conteo[i]['encontrados'])})"
        if i in conteo
        else textos.SENAL_CORTA[i]
    ),
)
todas = False
if len(elegidas) > 1:
    todas = (
        fila1[2].segmented_control(
            "Con",
            ["cualquiera", "todas"],
            default="cualquiera",
            format_func=lambda m: "Cualquiera de ellas" if m == "cualquiera" else "Todas a la vez",
        )
        == "todas"
    )
fila2 = st.columns([1, 2, 3])
anio_elegido = fila2[0].selectbox(
    "Año", [None, 2026, 2025, 2024, 2023], format_func=lambda a: "Todos" if a is None else str(a)
)
tipo = fila2[1].selectbox(
    "Tipo de contrato",
    [None, "servicios", "suministros", "obras"],
    format_func=lambda x: "Todos" if x is None else x.capitalize(),
)
orden = fila2[2].selectbox(
    "Ordenar por", list(textos.ORDEN_ALERTAS), format_func=textos.ORDEN_ALERTAS.get
)
fila3 = st.columns([1, 1, 1])
menores = fila3[0].toggle(
    "Incluir contratos menores",
    help="Los contratos menores son los de menos de 15.000 € (40.000 € en obras), sin IVA. "
    "Son muchos y en ellos solo se pueden comprobar dos señales.",
)
min_senales = fila3[1].selectbox(
    "Mínimo de señales", [1, 2, 3, 4], format_func=lambda n: f"{n} o más" if n > 1 else "1 o más"
)
cuantos = fila3[2].selectbox("Cuántos mostrar", [30, 60, 100])
with st.expander("Más filtros: organismo o empresa concretos", icon=":material/tune:"):
    organo_elegido = buscador.organo("revisar_organo", "Organismo")
    empresa_elegida = buscador.empresa("revisar_empresa", "Empresa")
for elegida in elegidas:
    st.caption(f"**{textos.SENAL_CORTA[elegida]}:** {textos.SENAL_FRASE[elegida]}")

# Sin menores, solo contratos en los que se han podido comprobar al menos 3 señales.
filas = datos.alertas(
    con,
    1 if menores else 3,
    None,
    cuantos,
    texto or None,
    anio_elegido,
    organo_elegido,
    indicadores=elegidas,
    todas=todas,
    orden=orden,
    min_activados=min_senales,
    tipo_contrato=tipo,
    adjudicatario_id=empresa_elegida,
)

if not filas:
    st.info("No hay contratos con estos filtros.")
    st.stop()

st.caption(
    f"{len(filas)} contratos, ordenados según «{textos.ORDEN_ALERTAS[orden].lower()}». "
    "Pulsa uno para ver por qué."
)

for fila in filas:
    senales.tarjeta_contrato(con, fila, "revisar")
