"""Mapa general del dinero de la Comunidad de Madrid (D-026, D-033).

De un vistazo: la Comunidad en el centro, sus consejerías alrededor y, si se quiere, los
contratos más grandes de cada una. Tamaño y color = dinero; relleno = parte gastada (el resto,
en gris). No hace falta entrar en ninguna consejería: se ve todo a la vez y, al pulsar un
círculo, su ficha aparece a la derecha. Niveles elegibles: solo consejerías, o consejerías y sus
contratos principales.
Presupuesto y contratos son fuentes distintas: se comparan por consejería y año, no partida a
partida. Lo que no tenemos se dice en la propia pantalla. Sin personas físicas (D-007).
"""

import math

import streamlit as st

from ojo_ciudadano.app import (
    datos,
    datos_contexto,
    datos_mapa,
    graficos_contexto,
    red,
    senales,
    textos,
)
from ojo_ciudadano.app.conexion import conexion

VISTAS = {
    "presupuesto": "Presupuesto y gasto",
    "plataforma": "Contratos (Plataforma, sin IVA)",
    "portal": "Contratos (portal, con IVA)",
    "subvenciones": "Subvenciones",
}
CAMPO_VISTA = {
    "plataforma": "contratos_plataforma",
    "portal": "contratos_portal",
    "subvenciones": "subvenciones",
}
NIVELES = {1: "Solo consejerías", 2: "Consejerías y sus contratos"}
CENTRO = "centro"
RADIO_ENTIDADES = {1: 250, 2: 205}  # distancia de las consejerías al centro, según los niveles
RADIO_CONTRATOS = 108  # distancia de los contratos a su consejería (se añade al radio anterior)
ALTO_MAPA = {1: 740, 2: 880}

st.html("<style>.block-container { max-width: 1500px; }</style>")


@st.cache_data(show_spinner=False, ttl=3600)
def _reparto(anio: int) -> dict:
    return datos_mapa.reparto(conexion(), anio)


@st.cache_data(show_spinner=False, ttl=3600)
def _principales(anio: int, n: int) -> dict:
    return datos_mapa.contratos_principales(conexion(), anio, n)


@st.cache_data(show_spinner=False, ttl=3600)
def _agregados(anio: int) -> dict:
    return datos_mapa.menores_y_subvenciones(conexion(), anio)


@st.cache_data(show_spinner=False, ttl=3600)
def _de_la_consejeria(organo_id: str, anio: int) -> dict:
    return datos_mapa.contratos_consejeria(conexion(), organo_id, anio)


def nombre_corto(nombre: str) -> str:
    """«Consejería de Familia, Juventud y Asuntos Sociales» → «Familia, Juventud y Asuntos
    Sociales», en varias líneas."""
    corto = nombre.replace("Consejería de ", "").replace("Consejería ", "")
    return red.envolver(corto, 18)


def etiqueta_contrato(contrato: dict, ancho: int = 16) -> str:
    """Quién recibe el contrato y cuánto, para que se lea de un vistazo (el título completo
    sale al pasar el ratón y al pulsar)."""
    nombres = (contrato["adjudicatarios"] or "Sin adjudicataria").split(" ; ")
    quien = nombres[0][:20] + (f" (+{len(nombres) - 1})" if len(nombres) > 1 else "")
    return red.envolver(quien, ancho) + chr(10) + textos.millones(contrato["importe"])


def importe_vista(entidad: dict, vista: str) -> float:
    if vista == "presupuesto":
        return entidad["credito"]
    return entidad.get(CAMPO_VISTA[vista]) or 0.0


def llenado_vista(entidad: dict, vista: str) -> float | None:
    """Presupuesto: lo gastado. Contratos y subvenciones: qué parte del gasto de la consejería
    representan (orden de magnitud: son fuentes distintas)."""
    if vista == "presupuesto":
        return entidad["llenado"]
    if not entidad["gastado"]:
        return None
    return min(importe_vista(entidad, vista) / entidad["gastado"], 1.0)


def leyenda(vista: str, liquidado: bool, niveles: int) -> str:
    if vista == "presupuesto":
        gasto = (
            "La parte **de color** es lo gastado (gasto reconocido) y la **gris**, lo que queda "
            "sin gastar. "
            if liquidado
            else "Este año todavía no hay gasto publicado: todo el círculo es presupuesto. "
        )
        texto = (
            "Cada círculo grande es una consejería u órgano: cuanto **más grande y más claro**, "
            "más dinero tiene disponible. " + gasto
        )
    else:
        texto = (
            "Cada círculo grande es una consejería: el **tamaño y el color** son lo contratado "
            "(o subvencionado) en el año y la parte **de color** es qué parte de su gasto "
            "reconocido representa (orden de magnitud: son fuentes distintas). "
        )
    if niveles == 2:
        texto += "Los círculos pequeños son sus contratos más grandes del año. "
    return texto + "Arrastra los círculos y pulsa uno para ver su ficha."


def grafo_general(entidades, vista, datos_anio, niveles, principales, agregados, con_agrupados):
    """Nodos y enlaces del mapa de un vistazo, con el diseño radial calculado (la Comunidad en el
    centro, las consejerías en círculo y sus contratos en un anillo exterior)."""
    liquidado = datos_anio["liquidado"]
    nodos = [
        red.NodoRed(
            id=CENTRO,
            etiqueta="Comunidad\nde Madrid",
            importe=datos_anio["credito"],
            llenado=(datos_anio["gastado"] / datos_anio["credito"]) if liquidado else None,
            centro=True,
            detalle="Total de la Comunidad",
            x=0,
            y=0,
        )
    ]
    enlaces: list[tuple] = []
    destinos: dict[str, tuple] = {}
    radio = RADIO_ENTIDADES[niveles]
    orden = red.alternar_tamanos(list(enumerate(entidades)))
    for (indice, e), (x, y) in zip(orden, red.posiciones_radiales(len(orden), radio), strict=True):
        id_ent = f"ent:{indice}"
        destinos[id_ent] = ("ent", e["entidad"])
        nodos.append(
            red.NodoRed(
                id=id_ent,
                etiqueta=nombre_corto(e["entidad"]),
                importe=importe_vista(e, vista),
                llenado=llenado_vista(e, vista),
                titulo=e["entidad"],
                detalle=(
                    f"Disponible: {textos.euros(e['credito'])}" if vista != "presupuesto" else ""
                ),
                x=x,
                y=y,
            )
        )
        enlaces.append((CENTRO, id_ent, radio))
        if niveles != 2 or not e["organo_id"]:
            continue
        hijos: list[red.NodoRed] = []
        for c in principales.get(e["organo_id"], []):
            iva = textos.iva_fuente(c["fuente"])
            id_con = f"con:{c['contrato_id']}"
            destinos[id_con] = ("con", c["contrato_id"])
            hijos.append(
                red.NodoRed(
                    id=id_con,
                    etiqueta=etiqueta_contrato(c, 12),
                    importe=c["importe"],
                    titulo=c["adjudicatarios"] or "Sin adjudicataria",
                    detalle=f"{c['organo']} · {iva}",
                    grupo="con",
                )
            )
        if con_agrupados:
            extra = agregados.get(e["organo_id"], {})
            if extra.get("menores"):
                id_men = f"men:{indice}"
                destinos[id_men] = ("men", e["entidad"])
                hijos.append(
                    red.NodoRed(
                        id=id_men,
                        etiqueta=f"Menores\n({textos.numero(extra['menores']['n'])})",
                        importe=extra["menores"]["importe"],
                        detalle="Contratos menores, portal, con IVA",
                        color="#C98500",
                        grupo="agr",
                    )
                )
            if extra.get("subvenciones"):
                id_sub = f"sub:{indice}"
                destinos[id_sub] = ("sub", e["entidad"])
                hijos.append(
                    red.NodoRed(
                        id=id_sub,
                        etiqueta=f"Subvenciones\n({textos.numero(extra['subvenciones']['n'])})",
                        importe=extra["subvenciones"]["importe"],
                        detalle="Base de Datos Nacional de Subvenciones",
                        color="#199E70",
                        grupo="agr",
                    )
                )
        angulo = math.atan2(y, x)
        for j, hijo in enumerate(hijos):
            # Anillo exterior en zigzag (dos radios) para que los hijos de consejerías vecinas no
            # se pisen.
            desvio = (j - (len(hijos) - 1) / 2) * 0.17
            distancia = radio + RADIO_CONTRATOS + (46 if j % 2 else 0)
            hijo.x = distancia * math.cos(angulo + desvio)
            hijo.y = distancia * math.sin(angulo + desvio)
            nodos.append(hijo)
            enlaces.append((id_ent, hijo.id, math.hypot(hijo.x - x, hijo.y - y)))
    return nodos, enlaces, destinos


def grafo_ampliado(entidad, cuerpo, datos_anio):
    """Una consejería en el centro y sus contratos más grandes, menores y subvenciones."""
    contratos, menores, subv = cuerpo["contratos"], cuerpo["menores"], cuerpo["subvenciones"]
    nodos = [
        red.NodoRed(
            id=CENTRO,
            etiqueta=nombre_corto(entidad["entidad"]),
            importe=entidad["credito"],
            llenado=entidad["llenado"],
            centro=True,
            detalle="Consejería",
            x=0,
            y=0,
        )
    ]
    destinos: dict[str, tuple] = {}
    hijos: list[red.NodoRed] = []
    for c in contratos:
        iva = textos.iva_fuente(c["fuente"])
        id_con = f"con:{c['contrato_id']}"
        destinos[id_con] = ("con", c["contrato_id"])
        hijos.append(
            red.NodoRed(
                id=id_con,
                etiqueta=etiqueta_contrato(c, 18),
                importe=c["importe"],
                titulo=c["adjudicatarios"] or "Sin adjudicataria",
                detalle=f"{c['organo']} · {iva}",
                grupo="con",
            )
        )
    if menores:
        destinos["men"] = ("men", entidad["entidad"])
        hijos.append(
            red.NodoRed(
                id="men",
                etiqueta=f"Contratos menores\n({textos.numero(menores['n'])})",
                importe=menores["importe"] or 0,
                detalle="Portal de la Comunidad, con IVA",
                color="#C98500",
                grupo="agr",
            )
        )
    if subv:
        destinos["sub"] = ("sub", entidad["entidad"])
        hijos.append(
            red.NodoRed(
                id="sub",
                etiqueta=f"Subvenciones\n({textos.numero(subv['n'])})",
                importe=subv["importe"] or 0,
                detalle="Base de Datos Nacional de Subvenciones",
                color="#199E70",
                grupo="agr",
            )
        )
    enlaces = []
    for hijo, (x, y) in zip(hijos, red.posiciones_radiales(len(hijos), 260), strict=True):
        hijo.x, hijo.y = x, y
        nodos.append(hijo)
        enlaces.append((CENTRO, hijo.id, 260))
    return nodos, enlaces, destinos


def metricas_entidad(entidad: dict, datos_anio: dict, liquidado: bool) -> None:
    k = st.columns(2)
    k[0].metric("Disponible", textos.millones(entidad["credito"]))
    if liquidado:
        k[1].metric(
            "Gastado",
            textos.millones(entidad["gastado"]),
            delta=textos.porcentaje(entidad["llenado"], 1),
            delta_color="off",
        )
        k = st.columns(2)
        k[0].metric("Sin gastar", textos.millones(entidad["sin_gastar"]))
    else:
        k[1].metric("Gastado", "Sin publicar")
        k = st.columns(2)
        k[0].metric("Sin gastar", "Sin publicar")
    k[1].metric(
        "Parte de la Comunidad",
        textos.porcentaje(entidad["credito"] / datos_anio["credito"], 1),
        help="Su dinero disponible sobre el total de la Comunidad.",
    )


def ficha_entidad(con, entidad: dict, datos_anio: dict, anio: int, ampliada: bool) -> None:
    st.subheader(entidad["entidad"])
    metricas_entidad(entidad, datos_anio, datos_anio["liquidado"])
    organo_id = entidad["organo_id"]
    if not organo_id:
        st.info(
            "De este órgano no tenemos contratos ni subvenciones en nuestros datos (no es una "
            "consejería con órganos de contratación en las fuentes que usamos).",
            icon=":material/info:",
        )
        return
    if not ampliada:
        st.button(
            "Ver todos sus contratos principales en el mapa",
            icon=":material/zoom_out_map:",
            on_click=lambda: st.session_state.update(mg_ampliada=entidad["entidad"], mg_sel=None),
        )
    cuerpo = _de_la_consejeria(organo_id, anio)
    if cuerpo["contratos"]:
        with st.expander("Sus contratos más grandes, en una tabla", icon=":material/table:"):
            st.dataframe(
                [
                    {
                        "Adjudicataria": c["adjudicatarios"] or "Sin dato",
                        "Importe": textos.euros(c["importe"], textos.iva_fuente(c["fuente"])),
                        "Ofertas": c["n_ofertas"],
                        "Cómo se contrató": c["procedimiento"],
                        "Expediente": c["url_origen"],
                    }
                    for c in cuerpo["contratos"]
                ],
                column_config={
                    "Expediente": st.column_config.LinkColumn(
                        "Expediente", display_text="Ver expediente oficial"
                    )
                },
                hide_index=True,
                width="stretch",
            )
    st.caption(
        f"Contratos con fecha de {anio} (por fecha del contrato o de formalización); los que no "
        "traen fecha no salen aquí. Plataforma sin IVA y portal con IVA, sin sumar entre sí."
    )


def ficha_agrupado(con, tipo: str, entidad: dict, anio: int) -> None:
    extra = _agregados(anio).get(entidad["organo_id"] or "", {})
    st.subheader("Contratos menores" if tipo == "men" else "Subvenciones")
    st.caption(entidad["entidad"])
    dato = extra.get("menores" if tipo == "men" else "subvenciones")
    if not dato:
        st.info("No hay datos de este año.")
        return
    if tipo == "men":
        st.markdown(
            f"{textos.numero(dato['n'])} contratos menores en {anio} por "
            f"{textos.euros(dato['importe'], 'con IVA')}. Son tantos que no se pintan uno a uno: "
            "míralos en **Contratos a revisar** (incluyendo menores) o en la ficha de cada órgano."
        )
    else:
        st.markdown(
            f"{textos.numero(dato['n'])} concesiones en {anio} por "
            f"{textos.euros(dato['importe'])}. Detalle por convocatoria en la **Ficha de órgano** "
            "y en el **Mapa del dinero**."
        )


def ficha_contrato(con, contrato_id: str, entidades: list[dict]) -> None:
    detalle = datos_mapa.detalle_contrato(con, contrato_id)
    if not detalle:
        st.info("No se encuentra este contrato.")
        return
    destino = datos_contexto._consejeria_de(con)
    entidad = next(
        (e for e in entidades if e["organo_id"] == destino.get(detalle["organo_id"])), None
    )
    st.subheader((detalle["titulo"] or "Contrato")[:140])
    st.caption(f"{detalle['organo']} · {detalle['tipo_contrato'] or 'tipo sin dato'}")
    iva = textos.iva_fuente(detalle["fuente"])
    importe = detalle["importe_sin_iva"] or detalle["importe_con_iva"]
    presupuesto = detalle["presupuesto_sin_iva"] or detalle["presupuesto_con_iva"]
    m = st.columns(2)
    m[0].metric("Adjudicado", textos.millones(importe), help=f"Importe adjudicado, {iva}.")
    m[1].metric(
        "Licitación", textos.millones(presupuesto), help=f"Presupuesto de licitación, {iva}."
    )
    m = st.columns(2)
    m[0].metric(
        "Ofertas recibidas",
        textos.numero(detalle["n_ofertas"]) if detalle["n_ofertas"] else "Sin dato",
    )
    if entidad:
        m[1].metric(
            "De la consejería",
            textos.porcentaje((importe or 0) / entidad["credito"], 2),
            help="Importe adjudicado sobre el dinero disponible de la consejería este año.",
        )
    st.markdown(
        f"**Cómo se contrató:** {detalle['procedimiento'] or 'sin dato'}. "
        f"**Estado:** {detalle['estado'] or 'sin dato'}. "
        f"**Adjudicataria:** {detalle['adjudicatarios'] or 'sin dato'}."
    )
    st.caption(
        "Los datos abiertos no publican los criterios de adjudicación ni por qué se eligió a "
        "esta empresa; sí el procedimiento y el número de ofertas."
    )
    for fila in datos.motivos(con, detalle["contrato_id"]):
        senales.mostrar(con, fila["indicador"], detalle["contrato_id"])
    anomalia = datos.anomalia_contrato(con, detalle["contrato_id"])
    if anomalia:
        st.markdown(
            f"**Contrato atípico** respecto a {textos.numero(anomalia['n_grupo'])} contratos "
            f"similares (señal experimental; atípico no significa irregular): {anomalia['motivo']}"
        )
    if detalle["url_origen"]:
        st.link_button(
            "Ver el expediente oficial", detalle["url_origen"], icon=":material/open_in_new:"
        )


# ------------------------------------------------------------------------------ pantalla
con = conexion()
st.header("Mapa general del dinero")
st.caption(
    "Cuánto dinero tiene la Comunidad de Madrid, cómo se reparte entre sus consejerías y cuánto "
    "han gastado, de un vistazo."
)

periodos = datos_mapa.periodos(con)
if not periodos:
    st.warning(
        "Esta base no tiene todavía el presupuesto de la Comunidad. Ejecuta "
        "`uv run python -m ojo_ciudadano.modelo.contexto` (docs/12-datos-cm.md).",
        icon=":material/database:",
    )
    st.stop()

anios = [p["anio"] for p in periodos]
por_defecto = next((p["anio"] for p in periodos if p["liquidado"]), anios[0])
c1, c2 = st.columns(2)
anio = c1.segmented_control("Periodo", anios, default=por_defecto, key="mg_anio") or por_defecto
vista = (
    c2.segmented_control(
        "Qué ver", list(VISTAS), default="presupuesto", format_func=VISTAS.get, key="mg_vista"
    )
    or "presupuesto"
)
datos_anio = _reparto(anio)
entidades = datos_anio["entidades"]
if not entidades:
    st.info("No hay datos de este periodo.")
    st.stop()
liquidado = datos_anio["liquidado"]

# --- Cifras de arriba ---
cifras = st.columns(4)
cifras[0].metric(
    "Dinero disponible" if liquidado else "Presupuesto inicial",
    textos.millones(datos_anio["credito"]),
    help="Crédito actual de todas las consejerías y órganos (presupuesto liquidado)."
    if liquidado
    else "Presupuesto inicial aprobado para el año.",
)
if liquidado:
    gastado, credito = datos_anio["gastado"], datos_anio["credito"]
    cifras[1].metric(
        "Gastado",
        textos.millones(gastado),
        delta=f"{textos.porcentaje(gastado / credito, 1)} del disponible",
        delta_color="off",
        help="Obligaciones reconocidas: gasto ya comprometido por la Administración.",
    )
    cifras[2].metric("Sin gastar", textos.millones(max(credito - gastado, 0)))
    cifras[3].metric(
        "Pagado",
        textos.millones(datos_anio["pagado"]),
        help="Pagos realizados sobre las obligaciones reconocidas.",
    )
else:
    cifras[1].metric("Gastado", "Sin publicar")
    cifras[2].metric("Sin gastar", "Sin publicar")
    cifras[3].metric("Pagado", "Sin publicar")
    st.info(
        f"Todavía no hay datos de gasto de {anio}: la Comunidad publica el presupuesto "
        "liquidado cuando cierra el año. Se muestra el presupuesto inicial.",
        icon=":material/info:",
    )
st.caption(
    f"Fuente: [Datos abiertos de la Comunidad de Madrid]({datos_anio['url_origen']}) · "
    f"descargado el {datos_anio['fecha_descarga']}. " + textos.AVISO_CONTEXTO
)

# --- Qué entidad está ampliada (se conserva entre periodos si existe) ---
nombres = [e["entidad"] for e in entidades]
ampliada = st.session_state.get("mg_ampliada")
if ampliada not in nombres:
    ampliada = None
    st.session_state["mg_ampliada"] = None

if ampliada is None:
    o1, o2, o3 = st.columns([3, 3, 3])
    niveles = (
        o1.segmented_control(
            "Niveles", list(NIVELES), default=2, format_func=NIVELES.get, key="mg_niveles"
        )
        or 2
    )
    por_consejeria = o2.slider(
        "Contratos por consejería",
        1,
        5,
        3,
        disabled=niveles == 1,
        key="mg_contratos",
        help="Cuántos de los contratos más grandes del año se dibujan junto a cada consejería.",
    )
    con_agrupados = o3.toggle(
        "Añadir menores y subvenciones",
        disabled=niveles == 1,
        key="mg_agrupados",
        help="Un círculo por consejería con sus contratos menores y otro con sus subvenciones.",
    )
else:
    st.button(
        "Volver a todas las consejerías",
        icon=":material/arrow_back:",
        type="tertiary",
        on_click=lambda: st.session_state.update(mg_ampliada=None, mg_sel=None),
    )

izquierda, derecha = st.columns([5, 2])
with izquierda:
    if ampliada is None:
        principales = _principales(anio, por_consejeria) if niveles == 2 else {}
        agregados = _agregados(anio) if (niveles == 2 and con_agrupados) else {}
        nodos, enlaces, destinos = grafo_general(
            entidades, vista, datos_anio, niveles, principales, agregados, con_agrupados
        )
        alto = ALTO_MAPA[niveles]
        st.markdown(leyenda(vista, liquidado, niveles))
    else:
        entidad_amp = next(e for e in entidades if e["entidad"] == ampliada)
        cuerpo = _de_la_consejeria(entidad_amp["organo_id"] or "", anio)
        nodos, enlaces, destinos = grafo_ampliado(entidad_amp, cuerpo, datos_anio)
        alto = 760
        st.markdown(
            f"Los **{len(cuerpo['contratos'])} contratos más grandes** de {anio} de "
            f"{ampliada}, más los menores y las subvenciones agrupados. **Tamaño y color = "
            "importe.** Arrastra los círculos y pulsa uno para ver su ficha."
        )
    seleccion = red.mapa(nodos, enlaces, alto=alto)
    if seleccion and seleccion in destinos:
        st.session_state["mg_sel"] = destinos[seleccion]

with derecha:
    marcado = st.session_state.get("mg_sel")
    if not marcado:
        st.info(
            "Pulsa un círculo del mapa y aquí verás su ficha: cuánto dinero tiene, cuánto ha "
            "gastado y, si es un contrato, cómo se contrató y cuántas ofertas hubo.",
            icon=":material/touch_app:",
        )
    else:
        tipo, referencia = marcado
        if tipo == "con":
            ficha_contrato(con, referencia, entidades)
        else:
            entidad = next((e for e in entidades if e["entidad"] == referencia), None)
            if entidad is None:
                st.info("Esa consejería no está en este periodo.")
            elif tipo == "ent":
                ficha_entidad(con, entidad, datos_anio, anio, ampliada is not None)
            else:
                ficha_agrupado(con, tipo, entidad, anio)

if ampliada is None:
    st.subheader("Cada consejería, de más a menos dinero")
    if liquidado:
        sin_gastar = [e for e in entidades if e["sin_gastar"]]
        st.markdown("**Dinero sin gastar**")
        st.plotly_chart(
            graficos_contexto.barras_horizontales(
                [e["entidad"] for e in sin_gastar], [e["sin_gastar"] for e in sin_gastar]
            ),
            config=graficos_contexto.GRAFICO_CONFIG,
        )
    st.dataframe(
        [
            {
                "Consejería u órgano": e["entidad"],
                "Disponible": textos.euros(e["credito"]),
                "Gastado": textos.euros(e["gastado"]) if liquidado else "Sin publicar",
                "% gastado": textos.porcentaje(e["llenado"], 1) if liquidado else "",
                "Contratos (Plataforma, sin IVA)": textos.euros(e["contratos_plataforma"]),
                "Contratos (portal, con IVA)": textos.euros(e["contratos_portal"]),
                "Subvenciones": textos.euros(e["subvenciones"]),
            }
            for e in entidades
        ],
        hide_index=True,
        width="stretch",
    )

with st.expander("Qué datos no tenemos", icon=":material/help:"):
    st.markdown(
        "- **Gasto del año en curso:** la Comunidad publica el presupuesto liquidado al cerrar "
        "el año; de 2026 solo hay presupuesto inicial.\n"
        "- **Gasto que no es contratación:** personal, transferencias, deuda y otras partidas no "
        "pasan por contratos, así que los contratos y subvenciones que vemos solo explican una "
        "parte del gasto de cada consejería. No sabemos qué partida financió cada contrato.\n"
        "- **Contratos sin fecha:** los que la fuente no fecha no se pueden asignar a un año y "
        "no salen en el mapa.\n"
        "- **Criterios de adjudicación:** los datos abiertos no dicen por qué se eligió a cada "
        "empresa; solo el procedimiento y el número de ofertas.\n"
        "- **Órganos fuera de las consejerías** (Asamblea, Cámara de Cuentas, deuda pública, "
        "fondo de contingencia): tienen presupuesto pero no contratos en nuestras fuentes.\n"
        "- **Contratos menores recientes:** los últimos meses de 2026 están incompletos en "
        "origen. " + textos.AVISO_MENORES_RECIENTES
    )
