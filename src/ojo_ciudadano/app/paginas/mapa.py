"""Mapa del dinero: flujos de los órganos a las empresas adjudicatarias y a los beneficiarios
de subvenciones."""

import plotly.graph_objects as go
import streamlit as st

from ojo_ciudadano.app import datos, graficos, textos
from ojo_ciudadano.app.conexion import conexion

FUENTES = {
    "Plataforma de Contratación del Sector Público (importes sin IVA)": "placsp",
    "Portal de la Contratación de la Comunidad de Madrid (importes con IVA)": "portal_cm",
    "Base de Datos Nacional de Subvenciones (importes concedidos)": "bdns",
}

st.header("Mapa del dinero")
st.caption("A qué empresas adjudica contratos cada órgano y a qué entidades concede subvenciones.")
with st.expander("Cómo leer el mapa", icon=":material/info:"):
    st.markdown(
        "Se muestran los mayores flujos según los filtros, una fuente cada vez: sus importes "
        "no son comparables entre sí. No hay enlace entre una partida del presupuesto y un "
        "contrato o una subvención, así que no se puede seguir el dinero desde el presupuesto."
    )

c1, c2, c3, c4 = st.columns(4)
fuente = FUENTES[c1.selectbox("Fuente", list(FUENTES))]
anio = c2.selectbox(
    "Año", [None, 2023, 2024, 2025, 2026], format_func=lambda a: "Todos" if a is None else str(a)
)
es_subvencion = fuente == "bdns"
tipo = c3.selectbox(
    "Tipo de contrato",
    [None, *datos.tipos_contrato(conexion())],
    format_func=lambda t: "Todos" if t is None else t,
    disabled=es_subvencion,
)
menores = c4.checkbox("Incluir contratos menores", value=False, disabled=es_subvencion)
limite = st.slider("Flujos a mostrar", 5, 40, 20)
if menores and not es_subvencion and anio in (None, 2026):
    st.caption(textos.AVISO_MENORES_RECIENTES)

if es_subvencion:
    filas = datos.flujos_subvenciones(conexion(), anio, limite)
    st.caption(
        "Fuente: [Base de Datos Nacional de Subvenciones]"
        "(https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones), datos descargados el "
        f"{datos.fecha_subvenciones(conexion())}. Importes concedidos. Las personas físicas y "
        "los beneficiarios cuyo NIF no se puede verificar aparecen en un único flujo agregado "
        "por órgano (RGPD). Un beneficiario puede ser una empresa, una entidad pública o una "
        "entidad sin ánimo de lucro. El tamaño de un flujo refleja sobre todo el tipo de "
        "convocatoria: algunas entidades gestionan programas enteros (p. ej. la asistencia "
        "jurídica gratuita) y las becas se reparten entre muchas personas. Un flujo grande no es "
        "una señal de riesgo por sí mismo."
    )
else:
    filas = datos.flujos(conexion(), fuente, menores, anio, tipo, limite)
    fecha = next(
        (f["fecha"] for f in datos.fechas_datos(conexion()) if f["fuente"] == fuente), None
    )
    st.caption(
        f"Datos descargados el {fecha}. Un flujo grande refleja el volumen de compras del órgano "
        "y no es una señal de riesgo por sí mismo."
    )
if not filas:
    st.info("No hay flujos con estos filtros.")
    st.stop()

organos = list(dict.fromkeys(f["organo"] for f in filas))
empresas = list(dict.fromkeys(f["empresa"] for f in filas))
etiquetas = organos + empresas
figura = go.Figure(
    go.Sankey(
        node={
            "label": etiquetas,
            "pad": 14,
            "thickness": 14,
            "line": {"width": 0},
            # Cada organismo con su color (paleta validada, graficos.CATEGORICOS) y sus
            # flujos del mismo color; las empresas en gris claro.
            "color": [graficos.color_categorico(i) for i in range(len(organos))]
            + ["#93A1B8"] * len(empresas),
        },
        link={
            "source": [organos.index(f["organo"]) for f in filas],
            "target": [len(organos) + empresas.index(f["empresa"]) for f in filas],
            "value": [f["importe"] for f in filas],
            "color": [
                graficos.transparente(graficos.color_categorico(organos.index(f["organo"])), 0.35)
                for f in filas
            ],
        },
        textfont={"color": "#E7ECF3", "size": 12, "shadow": "none"},
    )
)
figura.update_layout(
    height=600,
    margin={"l": 0, "r": 0, "t": 10, "b": 10},
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font={"family": "Inter, sans-serif"},
)
st.plotly_chart(figura, width="stretch")

st.subheader("Detalle de los flujos")
unidad = "concesiones" if es_subvencion else "contratos"
st.caption(
    "Elige un flujo para ver sus convocatorias. Cada enlace lleva a la ficha de la convocatoria "
    "en la BDNS (las concesiones no tienen página propia)."
    if es_subvencion
    else "Elige un flujo para ver sus contratos, cada uno con el enlace a su ficha oficial."
)
flujo = st.selectbox(
    "Flujo",
    filas,
    format_func=lambda f: (
        f"{f['organo']} → {f['empresa']}: {f['importe']:,.0f} € ({f['n_contratos']} {unidad})"
    ),
)
if es_subvencion:
    for c in datos.concesiones_flujo(
        conexion(), flujo["organo_id"], flujo["adjudicatario_id"], anio
    ):
        titulo = (c["titulo"] or "Convocatoria sin título")[:100]
        enlace = f"[{titulo}]({c['url_origen']})" if c["url_origen"] else titulo
        st.markdown(f"- {enlace} · {c['n_concesiones']:,} concesiones · {c['importe']:,.0f} €")
else:
    for c in datos.contratos_flujo(
        conexion(), flujo["organo_id"], flujo["adjudicatario_id"], fuente, menores, anio, tipo
    ):
        titulo = (c["titulo"] or c["contrato_id"])[:100]
        st.markdown(
            f"- [{titulo}]({c['url_origen']}) · {c['anio'] or 'sin fecha'} · {c['importe']:,.0f} €"
        )
