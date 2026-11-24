"""Red del dinero: a quién adjudica cada organismo (D-023, A-07).

1. Burbujas de los organismos que más adjudican (tamaño y color = importe), con la misma
   estética que el Mapa del dinero (lienzo de `app/burbujas.py`, D-050). Al pulsar uno, su red.
2. Su red: el organismo en el centro y sus empresas alrededor, con las motas de luz que van del
   organismo a cada empresa. Al pulsar una empresa, sus contratos o convocatorias debajo.
3. El diagrama de flujos queda como vista avanzada.
Una fuente cada vez: sus importes no se suman (P-10). Sin personas físicas con nombre (D-007).
"""

import streamlit as st

from ojo_ciudadano.app import burbujas, datos, graficos, red, textos
from ojo_ciudadano.app.conexion import conexion

FUENTES = {
    "placsp": "Contratos (Plataforma de Contratación, sin IVA)",
    "portal_cm": "Contratos (portal de la Comunidad, con IVA)",
    "bdns": "Subvenciones",
}
TODOS = "__todos__"


def elegir(organo_id: str) -> None:
    """Se ejecuta antes de redibujar, así puede cambiar el desplegable de organismo."""
    st.session_state["mapa_organo"] = organo_id


con = conexion()
st.header("Red del dinero")
st.caption(
    "A quién adjudica contratos o concede subvenciones cada organismo. El tamaño de cada "
    "burbuja es el dinero."
)

c1, c2, c3, c4 = st.columns([3, 1, 2, 2])
fuente = c1.selectbox(
    "Fuente", list(FUENTES), format_func=FUENTES.get, help=textos.GLOSARIO["fuentes"]
)
anio = c2.selectbox(
    "Año", [None, 2026, 2025, 2024, 2023], format_func=lambda a: "Todos" if a is None else str(a)
)
es_subvencion = fuente == "bdns"
tipo = c3.selectbox(
    "Tipo de contrato",
    [None, *datos.tipos_contrato(con)],
    help=textos.GLOSARIO["tipo_contrato"],
    format_func=lambda t: "Todos" if t is None else t,
    disabled=es_subvencion,
)
menores = c4.toggle(
    "Incluir contratos menores", disabled=es_subvencion, help=textos.GLOSARIO["contrato_menor"]
)
if menores and not es_subvencion and anio in (None, 2026):
    st.caption(textos.AVISO_MENORES_RECIENTES)

organismos = datos.totales_organos(con, fuente, menores, anio, tipo, limite=30)
if not organismos:
    st.info("No hay datos con estos filtros.")
    st.stop()

# El organismo elegido se guarda para que la lista de la vista general pueda elegirlo.
opciones = [TODOS, *(o["organo_id"] for o in organismos)]
if st.session_state.get("mapa_organo_pulsado") in opciones:
    st.session_state["mapa_organo"] = st.session_state.pop("mapa_organo_pulsado")
if st.session_state.get("mapa_organo") not in opciones:
    st.session_state["mapa_organo"] = TODOS
nombres = {o["organo_id"]: o["organo"] for o in organismos}
elegido = st.selectbox(
    "Organismo",
    opciones,
    help=textos.GLOSARIO["organismo"],
    format_func=lambda o: "Todos: los que más adjudican" if o == TODOS else nombres[o],
    key="mapa_organo",
)

if elegido == TODOS:
    principales = organismos[:12]
    grafico, lista = st.columns([3, 2])
    with grafico:
        # los organismos alrededor de un centro con el total, como el Mapa del dinero
        total = sum(o["importe"] for o in principales)
        nodos = [
            red.NodoRed(
                id="centro",
                etiqueta="Los que más\nadjudican",
                importe=total,
                centro=True,
                detalle=f"{len(principales)} organismos",
                x=0,
                y=0,
            )
        ]
        orden = red.alternar_tamanos(list(enumerate(principales)))
        for (_, o), (x, y) in zip(orden, red.posiciones_radiales(len(orden), 260), strict=True):
            nodos.append(
                red.NodoRed(
                    id=o["organo_id"],
                    etiqueta=red.envolver(o["organo"].replace("Consejería de ", "")[:34], 15)
                    + chr(10)
                    + textos.millones(o["importe"]),
                    importe=o["importe"],
                    titulo=o["organo"],
                    x=x,
                    y=y,
                )
            )
        pulsado = burbujas.mapa(
            nodos, [("centro", n.id) for n in nodos[1:]], alto=720, clave="red_organismos"
        )
        if pulsado and pulsado != "centro":
            # el desplegable ya está dibujado: se elige en la siguiente ejecución, antes de él
            st.session_state["mapa_organo_pulsado"] = pulsado
            st.rerun()
    with lista:
        st.caption("Pulsa un organismo en el mapa o en la lista para ver a quién adjudica.")
        for n, o in enumerate(principales, start=1):
            st.button(
                f"{n}. {o['organo']} · {textos.euros(o['importe'])}",
                key=f"mapa-{o['organo_id']}",
                type="tertiary",
                on_click=elegir,
                args=(o["organo_id"],),
            )
    st.stop()

# --- Red de un organismo ---
organismo = next(o for o in organismos if o["organo_id"] == elegido)
if es_subvencion:
    filas = datos.flujos_subvenciones(con, anio, 10, organo_id=elegido)
else:
    filas = datos.flujos(con, fuente, menores, anio, tipo, 10, organo_id=elegido)
if not filas:
    st.info("No hay empresas con estos filtros.")
    st.stop()

st.button(
    "Volver a todos los organismos",
    icon=":material/arrow_back:",
    type="tertiary",
    on_click=elegir,
    args=(TODOS,),
)
nodos_red = [
    red.NodoRed(
        id="centro",
        etiqueta=red.envolver(organismo["organo"], 18),
        importe=organismo["importe"],
        centro=True,
        titulo=organismo["organo"],
        x=0,
        y=0,
    )
]
radio = 230
orden = red.alternar_tamanos(list(enumerate(filas)))
for (n, f), (x, y) in zip(orden, red.posiciones_radiales(len(orden), radio), strict=True):
    nodos_red.append(
        red.NodoRed(
            id=f"emp:{n}",
            etiqueta=red.envolver(f["empresa"][:30], 18) + chr(10) + textos.millones(f["importe"]),
            importe=f["importe"],
            titulo=f["empresa"],
            detalle=f"{textos.numero(f['n_contratos'])} "
            + ("concesiones" if es_subvencion else "contratos"),
            x=x,
            y=y,
        )
    )
pulsada = burbujas.mapa(
    nodos_red, [("centro", n.id) for n in nodos_red[1:]], alto=700, clave=f"red_{elegido}"
)
if pulsada and pulsada.startswith("emp:"):
    # al pulsar una empresa, sus contratos salen en el desplegable de debajo
    st.session_state["mapa_flujo"] = filas[int(pulsada.split(":")[1])]
quien = "entidades" if es_subvencion else "empresas"
st.caption(
    f"Las 10 {quien} con más importe de {organismo['organo']}. El tamaño y el color de cada "
    "burbuja son el dinero; pulsa una para ver sus contratos debajo. "
    "Un flujo grande refleja el volumen de compras o ayudas del organismo y no es una señal de "
    "riesgo por sí mismo."
    + (
        " Las personas físicas aparecen juntas y sin nombre."
        if es_subvencion
        else " Las personas físicas no aparecen."
    )
)

# --- Detalle ---
unidad = "concesiones" if es_subvencion else "contratos"
if st.session_state.get("mapa_flujo") not in filas:  # de otro organismo o con otros filtros
    st.session_state.pop("mapa_flujo", None)
flujo = st.selectbox(
    "Ver los contratos de" if not es_subvencion else "Ver las convocatorias de",
    filas,
    key="mapa_flujo",
    format_func=lambda f: (
        f"{f['empresa']} · {textos.euros(f['importe'])} "
        f"({textos.numero(f['n_contratos'])} {unidad})"
    ),
)
if es_subvencion:
    st.caption(
        "Fuente: [Base de Datos Nacional de Subvenciones]"
        "(https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones), datos descargados el "
        f"{datos.fecha_subvenciones(con)}. Cada enlace lleva a la convocatoria."
    )
    for c in datos.concesiones_flujo(con, flujo["organo_id"], flujo["adjudicatario_id"], anio):
        titulo = (c["titulo"] or "Convocatoria sin título")[:100]
        enlace = f"[{titulo}]({c['url_origen']})" if c["url_origen"] else titulo
        st.markdown(
            f"- {enlace} · {textos.numero(c['n_concesiones'])} concesiones · "
            f"{textos.euros(c['importe'])}"
        )
else:
    iva = textos.iva_fuente(fuente)
    for c in datos.contratos_flujo(
        con, flujo["organo_id"], flujo["adjudicatario_id"], fuente, menores, anio, tipo
    ):
        titulo = (c["titulo"] or c["contrato_id"])[:100]
        st.markdown(
            f"- [{titulo}]({c['url_origen']}) · {c['anio'] or 'sin fecha'} · "
            f"{textos.euros(c['importe'], iva)}"
        )

with st.expander("Vista avanzada: diagrama de flujos", icon=":material/account_tree:"):
    if es_subvencion:
        todos = datos.flujos_subvenciones(con, anio, 20)
    else:
        todos = datos.flujos(con, fuente, menores, anio, tipo, 20)
    st.caption("Los 20 mayores flujos de todos los organismos con estos filtros.")
    st.plotly_chart(graficos.flujos_sankey(todos), config=graficos.CONFIG)
