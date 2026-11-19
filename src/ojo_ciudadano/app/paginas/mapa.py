"""Mapa del dinero: flujos de los órganos a las empresas adjudicatarias."""

import plotly.graph_objects as go
import streamlit as st

from ojo_ciudadano.app import datos
from ojo_ciudadano.app.conexion import conexion

FUENTES = {
    "Plataforma de Contratación del Sector Público (importes sin IVA)": "placsp",
    "Portal de la Contratación de la Comunidad de Madrid (importes con IVA)": "portal_cm",
}

st.header("Mapa del dinero")
st.write(
    "A qué empresas adjudica cada órgano. Se muestran los mayores flujos según los filtros. "
    "Esto es el nivel de **contratos**; no hay enlace entre una partida del presupuesto y un "
    "contrato, así que no se puede seguir el dinero desde el presupuesto."
)

c1, c2, c3, c4 = st.columns(4)
fuente = FUENTES[c1.selectbox("Fuente", list(FUENTES))]
anio = c2.selectbox(
    "Año", [None, 2023, 2024, 2025, 2026], format_func=lambda a: "Todos" if a is None else str(a)
)
tipo = c3.selectbox("Tipo de contrato", [None, *datos.tipos_contrato(conexion())])
menores = c4.checkbox("Incluir contratos menores", value=False)
limite = st.slider("Flujos a mostrar", 5, 40, 20)

filas = datos.flujos(conexion(), fuente, menores, anio, tipo, limite)
if not filas:
    st.info("No hay flujos con estos filtros.")
    st.stop()

organos = list(dict.fromkeys(f["organo"] for f in filas))
empresas = list(dict.fromkeys(f["empresa"] for f in filas))
etiquetas = organos + empresas
figura = go.Figure(
    go.Sankey(
        node={"label": etiquetas, "pad": 12},
        link={
            "source": [organos.index(f["organo"]) for f in filas],
            "target": [len(organos) + empresas.index(f["empresa"]) for f in filas],
            "value": [f["importe"] for f in filas],
        },
    )
)
figura.update_layout(height=600, margin={"l": 0, "r": 0, "t": 10, "b": 10})
st.plotly_chart(figura, width="stretch")

st.subheader("Detalle de los flujos")
st.caption("Elige un flujo para ver sus contratos, cada uno con el enlace a su ficha oficial.")
flujo = st.selectbox(
    "Flujo",
    filas,
    format_func=lambda f: (
        f"{f['organo']} → {f['empresa']}: {f['importe']:,.0f} € ({f['n_contratos']} contratos)"
    ),
)
for c in datos.contratos_flujo(
    conexion(), flujo["organo_id"], flujo["adjudicatario_id"], fuente, menores, anio, tipo
):
    titulo = (c["titulo"] or c["contrato_id"])[:100]
    st.markdown(
        f"- [{titulo}]({c['url_origen']}) · {c['anio'] or 'sin fecha'} · {c['importe']:,.0f} €"
    )
