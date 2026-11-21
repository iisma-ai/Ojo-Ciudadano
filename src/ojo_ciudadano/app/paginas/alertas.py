"""Contratos a revisar: los que tienen alguna señal, con un gráfico por señal (D-023, A-03).

Cada contrato es un desplegable: al pulsar en cualquier parte se abre con sus gráficos, que
solo se calculan entonces.
"""

import streamlit as st

from ojo_ciudadano.app import datos, senales, textos
from ojo_ciudadano.app.conexion import conexion

LIMITE = 30

con = conexion()
st.header("Contratos a revisar")
st.caption("Contratos en los que hemos encontrado alguna señal. " + textos.NOTA_SENAL)

buscar, senal, anio = st.columns([3, 2, 1])
texto = buscar.text_input(
    "Buscar", placeholder="Palabra del título u organismo (vacuna, Metro, hospital…)"
).strip()
conteo = datos.conteo_senales(con)
elegida = senal.selectbox(
    "Señal",
    [None, *textos.SENAL_CORTA],
    format_func=lambda i: (
        "Todas"
        if i is None
        else f"{textos.SENAL_CORTA[i]} ({textos.numero(conteo[i]['encontrados'])})"
        if i in conteo
        else textos.SENAL_CORTA[i]
    ),
)
anio_elegido = anio.selectbox(
    "Año", [None, 2026, 2025, 2024, 2023], format_func=lambda a: "Todos" if a is None else str(a)
)
menores = st.toggle(
    "Incluir contratos menores",
    help="Los contratos menores son los de menos de 15.000 € (40.000 € en obras), sin IVA. "
    "Son muchos y en ellos solo se pueden comprobar dos señales.",
)
if elegida:
    st.caption(f"**{textos.SENAL_CORTA[elegida]}:** {textos.SENAL_FRASE[elegida]}")

# Sin menores, solo contratos en los que se han podido comprobar al menos 3 señales.
filas = datos.alertas(con, 1 if menores else 3, elegida, LIMITE, texto or None, anio_elegido)

if not filas:
    st.info("No hay contratos con estos filtros.")
    st.stop()

st.caption(f"{len(filas)} contratos, de más a menos señales. Pulsa uno para ver por qué.")

for fila in filas:
    titulo = fila["titulo"] or fila["contrato_id"]
    if len(titulo) > 110:
        titulo = titulo[:107].rstrip() + "…"
    encontradas = [i for i in (fila["indicadores_activados"] or "").split(", ") if i]
    nombres = " · ".join(textos.SENAL_CORTA[i] for i in encontradas)
    iva = textos.iva_fuente(fila["fuente"])
    desplegable = st.expander(
        f"**{titulo}**  \n:gray[{fila['organo']}]  ·  :blue[{nombres}]",
        key=f"contrato-{fila['contrato_id']}",
        on_change="rerun",
    )
    with desplegable:
        comprobadas = fila["n_aplicables"]
        st.caption(
            f"{fila['anio'] or 'Sin fecha'} · {textos.euros(fila['importe'], iva)} · "
            f"{len(encontradas)} de {comprobadas} "
            f"{'señal comprobada' if comprobadas == 1 else 'señales comprobadas'}"
        )
        if desplegable.open:
            columnas = st.columns(2) if len(encontradas) > 1 else [st.container()]
            for n, indicador in enumerate(encontradas):
                with columnas[n % len(columnas)]:
                    senales.mostrar(con, indicador, fila["contrato_id"])
            anomalia = datos.anomalia_contrato(con, fila["contrato_id"])
            if anomalia:
                st.markdown(
                    f"**Contrato atípico** respecto a {textos.numero(anomalia['n_grupo'])} "
                    "contratos similares (señal experimental, no suma a las demás; atípico no "
                    f"significa irregular): {anomalia['motivo']}"
                )
            if fila["url_origen"]:
                st.link_button(
                    "Ver el expediente oficial", fila["url_origen"], icon=":material/open_in_new:"
                )
