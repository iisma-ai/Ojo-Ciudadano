"""Contratos a revisar: los que tienen alguna señal (D-023, A-03; D-042).

Pensada para un ciudadano cualquiera:
- un buscador y las seis señales como botones, con el resto de filtros en «Más filtros»;
- cada contrato es una tarjeta con su título limpio, cuánto, a quién, quién lo adjudica y sus
  señales en etiquetas ámbar. Al pulsarla se abre con un gráfico por señal (que solo se calcula
  entonces) y el enlace al expediente arriba;
- primero los contratos con más señales, y «Ver más contratos» al final.
"""

import streamlit as st

from ojo_ciudadano.app import buscador, datos, senales, textos
from ojo_ciudadano.app.conexion import conexion

TANDA = 30  # contratos que se añaden con «Ver más contratos»
SOLO_MENORES = {"R-03"}  # señales que solo se comprueban en contratos menores
MAXIMO = 300


@st.cache_data(show_spinner=False, ttl=3600)
def _conteo() -> dict:
    return datos.conteo_senales(conexion())


con = conexion()
st.header("Contratos a revisar", help=textos.NOTA_SENAL, anchor=False)
st.caption("Contratos en los que hemos visto alguna señal. Pulsa uno para ver por qué.")
# el aviso y las fuentes, aquí y no en la portada (D-051)
st.caption(
    "Una señal no prueba nada irregular: indica dónde merece la pena mirar con más detalle. "
    "Cada contrato, con su explicación y su enlace al expediente oficial. Fuentes: "
    "[Plataforma de Contratación del Sector Público](https://contrataciondelestado.es) "
    "(sin IVA) y [Portal de la Contratación Pública de la Comunidad de Madrid]"
    "(https://contratos-publicos.comunidad.madrid/contratos) (con IVA)."
)

conteo = _conteo()
busqueda, mas = st.columns([5, 1], vertical_alignment="bottom")
texto = busqueda.text_input(
    "Buscar",
    placeholder="Palabra del título u organismo (vacuna, Metro, hospital…)",
    label_visibility="collapsed",
).strip()
elegidas = (
    st.pills(
        "Qué señal",
        list(textos.SENAL_CORTA),
        selection_mode="multi",
        format_func=lambda i: (
            f"{textos.ICONO_SENAL[i]} {textos.SENAL_CORTA[i]}"
            + (f" ({textos.numero(conteo[i]['encontrados'])})" if i in conteo else "")
        ),
        help="Pulsa una o varias para ver solo los contratos con esas señales. "
        + textos.GLOSARIO["senal"],
    )
    or []
)

with mas.popover("Más filtros", icon=":material/tune:", width="stretch"):
    todas = False
    if len(elegidas) > 1:
        todas = (
            st.segmented_control(
                "Con las señales elegidas",
                ["cualquiera", "todas"],
                default="cualquiera",
                format_func=lambda m: (
                    "Cualquiera de ellas" if m == "cualquiera" else "Todas a la vez"
                ),
            )
            == "todas"
        )
    orden = st.selectbox(
        "Ordenar por", list(textos.ORDEN_ALERTAS), format_func=textos.ORDEN_ALERTAS.get
    )
    anio_elegido = st.selectbox(
        "Año",
        [None, 2026, 2025, 2024, 2023],
        format_func=lambda a: "Todos" if a is None else str(a),
    )
    tipo = st.selectbox(
        "Tipo de contrato",
        [None, "servicios", "suministros", "obras"],
        format_func=lambda x: "Todos" if x is None else x.capitalize(),
    )
    min_senales = st.selectbox(
        "Con al menos",
        [1, 2, 3, 4],
        format_func=lambda n: "1 señal" if n == 1 else f"{n} señales",
    )
    menores = st.toggle(
        "Incluir contratos menores",
        help="Los contratos menores son los de menos de 15.000 € (40.000 € en obras), sin IVA. "
        "Son muchos y en ellos solo se pueden comprobar dos señales.",
    )
    organo_elegido = buscador.organo("revisar_organo", "Organismo concreto")
    empresa_elegida = buscador.empresa("revisar_empresa", "Empresa concreta")

activos = [
    etiqueta
    for etiqueta, activo in (
        ("año", anio_elegido is not None),
        ("tipo de contrato", tipo is not None),
        ("orden", orden != "senales"),
        ("mínimo de señales", min_senales > 1),
        ("contratos menores", menores),
        ("organismo", organo_elegido is not None),
        ("empresa", empresa_elegida is not None),
        ("todas las señales a la vez", todas),
    )
    if activo
]
if activos:
    st.caption("Filtros activos: " + ", ".join(activos) + ".")

# Una señal que solo se comprueba en contratos menores no tendría resultados sin ellos: al
# elegirla, se incluyen solos.
con_menores = menores or bool(SOLO_MENORES & set(elegidas))
if con_menores and not menores:
    st.caption(
        "Se incluyen los contratos menores, porque «"
        + ", ".join(textos.SENAL_CORTA[i] for i in sorted(SOLO_MENORES & set(elegidas)))
        + "» solo se comprueba en ellos."
    )

# Al cambiar de filtros se vuelve a la primera tanda.
filtros = (
    texto,
    tuple(elegidas),
    todas,
    orden,
    anio_elegido,
    tipo,
    min_senales,
    menores,
    organo_elegido,
    empresa_elegida,
)
if st.session_state.get("revisar_filtros") != filtros:
    st.session_state["revisar_filtros"] = filtros
    st.session_state["revisar_cuantos"] = TANDA
cuantos = st.session_state.get("revisar_cuantos", TANDA)

# Sin menores, solo contratos en los que se han podido comprobar al menos 3 señales.
filas = datos.alertas(
    con,
    1 if con_menores else 3,
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

for fila in filas:
    senales.tarjeta_contrato(con, fila, "revisar")

if len(filas) == cuantos and cuantos < MAXIMO:
    st.button(
        "Ver más contratos",
        icon=":material/expand_more:",
        on_click=lambda: st.session_state.update(revisar_cuantos=cuantos + TANDA),
    )
