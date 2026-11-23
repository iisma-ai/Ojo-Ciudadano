"""Mapa general del dinero de la Comunidad de Madrid (D-026).

De un vistazo: cuánto dinero tiene la Comunidad en un periodo, cómo se reparte entre sus
consejerías y cuánto ha gastado cada una (círculo lleno de color = gastado; gris = sin gastar).
Al elegir una consejería, sus contratos más grandes; al elegir un contrato, lo que se sabe de él.
Presupuesto y contratos son fuentes distintas: se comparan por consejería y año, no partida a
partida. Lo que no tenemos se dice en la propia pantalla. Sin personas físicas (D-007).
"""

import streamlit as st

from ojo_ciudadano.app import datos, datos_mapa, graficos_contexto, red, senales, textos
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
CENTRO = "centro"
URL_PRESUPUESTO = "https://datos.comunidad.madrid/dataset/1902000"


def nombre_corto(nombre: str) -> str:
    """«Consejería de Familia, Juventud y Asuntos Sociales» → «Familia, Juventud y Asuntos
    Sociales», en varias líneas."""
    corto = nombre.replace("Consejería de ", "").replace("Consejería ", "")
    return red.envolver(corto, 18)


def etiqueta_contrato(contrato: dict) -> str:
    """Quién recibe el contrato y cuánto, para que se lea de un vistazo (el título completo
    sale al pasar el ratón y al pulsar)."""
    quien = (contrato["adjudicatarios"] or "Sin adjudicataria").split(" ; ")[0]
    return red.envolver(quien[:30], 18) + chr(10) + textos.millones(contrato["importe"])


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


def leyenda(vista: str, liquidado: bool) -> str:
    if vista == "presupuesto":
        gasto = (
            "La parte **de color** es lo gastado (gasto reconocido) y la **gris**, lo que queda "
            "sin gastar. "
            if liquidado
            else "Este año todavía no hay gasto publicado: todo el círculo es presupuesto. "
        )
        return (
            "Cada círculo es una consejería u órgano: cuanto **más grande y más claro**, más "
            "dinero tiene disponible. " + gasto + "Arrastra los círculos y pulsa uno para ver "
            "sus contratos."
        )
    return (
        "Cada círculo es una consejería: el **tamaño y el color** son lo contratado (o "
        "subvencionado) en el año y la parte **de color** es qué parte de su gasto reconocido "
        "representa (orden de magnitud: son fuentes distintas). Arrastra los círculos y pulsa "
        "uno para ver sus contratos."
    )


def guardar(clave: str, valor) -> None:
    st.session_state[clave] = valor


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
c1, c2 = st.columns([3, 3])
anio = c1.segmented_control("Periodo", anios, default=por_defecto, key="mg_anio") or por_defecto
vista = (
    c2.segmented_control(
        "Qué ver",
        list(VISTAS),
        default="presupuesto",
        format_func=VISTAS.get,
        key="mg_vista",
    )
    or "presupuesto"
)

datos_anio = datos_mapa.reparto(con, anio)
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

# --- Qué entidad está elegida (se conserva entre periodos si existe) ---
nombres = [e["entidad"] for e in entidades]
if st.session_state.get("mg_entidad") not in nombres:
    st.session_state["mg_entidad"] = None
    st.session_state["mg_contrato"] = None
elegida = st.session_state["mg_entidad"]

if elegida is None:
    # ------------------------------------------------ nivel 0: la Comunidad y sus consejerías
    st.markdown(leyenda(vista, liquidado))
    nodos = [
        red.NodoRed(
            id=CENTRO,
            etiqueta="Comunidad\nde Madrid",
            importe=datos_anio["credito"],
            llenado=(datos_anio["gastado"] / datos_anio["credito"]) if liquidado else None,
            centro=True,
            detalle="Total de la Comunidad",
        )
    ]
    for n, e in enumerate(entidades):
        nodos.append(
            red.NodoRed(
                id=f"ent:{n}",
                etiqueta=nombre_corto(e["entidad"]),
                importe=importe_vista(e, vista),
                llenado=llenado_vista(e, vista),
                detalle=(
                    f"Disponible: {textos.euros(e['credito'])}" if vista != "presupuesto" else ""
                ),
            )
        )
    seleccion = red.mapa(nodos, [(CENTRO, n.id) for n in nodos[1:]], alto=700)
    if seleccion and seleccion.startswith("ent:"):
        guardar("mg_entidad", entidades[int(seleccion.split(":")[1])]["entidad"])
        guardar("mg_contrato", None)
        st.rerun()

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
else:
    # ------------------------------------------------ nivel 1: una consejería y sus contratos
    entidad = next(e for e in entidades if e["entidad"] == elegida)
    st.button(
        "Volver a todas las consejerías",
        icon=":material/arrow_back:",
        type="tertiary",
        on_click=guardar,
        args=("mg_entidad", None),
    )
    st.subheader(entidad["entidad"])
    k = st.columns(4)
    k[0].metric("Disponible", textos.millones(entidad["credito"]))
    if liquidado:
        k[1].metric(
            "Gastado",
            textos.millones(entidad["gastado"]),
            delta=textos.porcentaje(entidad["llenado"], 1),
            delta_color="off",
        )
        k[2].metric("Sin gastar", textos.millones(entidad["sin_gastar"]))
    else:
        k[1].metric("Gastado", "Sin publicar")
        k[2].metric("Sin gastar", "Sin publicar")
    peso = datos_anio["credito"]
    k[3].metric(
        "Parte de la Comunidad",
        textos.porcentaje(entidad["credito"] / peso, 1),
        help="Su dinero disponible sobre el total de la Comunidad.",
    )

    organo_id = entidad["organo_id"]
    if not organo_id:
        st.info(
            "De este órgano no tenemos contratos ni subvenciones en nuestros datos (no es una "
            "consejería con órganos de contratación en las fuentes que usamos).",
            icon=":material/info:",
        )
        st.stop()
    cuerpo = datos_mapa.contratos_consejeria(con, organo_id, anio)
    contratos, menores, subv = cuerpo["contratos"], cuerpo["menores"], cuerpo["subvenciones"]
    if not (contratos or menores or subv):
        st.info(
            f"No hay contratos ni subvenciones de {anio} en nuestros datos para esta consejería."
        )
        st.stop()

    st.markdown(
        f"Los **{len(contratos)} contratos más grandes** de {anio} de sus {cuerpo['n_organos']} "
        "órganos (hospitales, agencias, direcciones generales…), más los contratos menores y las "
        "subvenciones agrupados. Cada círculo es un contrato: **tamaño y color = importe**. "
        "Arrastra los círculos y pulsa uno para ver sus datos."
    )
    nodos = [
        red.NodoRed(
            id=CENTRO,
            etiqueta=nombre_corto(entidad["entidad"]),
            importe=entidad["credito"],
            llenado=entidad["llenado"],
            centro=True,
            detalle="Consejería",
        )
    ]
    for c in contratos:
        iva = textos.iva_fuente(c["fuente"])
        nodos.append(
            red.NodoRed(
                id=f"con:{c['contrato_id']}",
                etiqueta=etiqueta_contrato(c),
                importe=c["importe"],
                detalle=f"{(c['titulo'] or '')[:90]} · {c['organo']} · {iva}",
            )
        )
    if menores:
        nodos.append(
            red.NodoRed(
                id="men",
                etiqueta=f"Contratos menores\n({textos.numero(menores['n'])})",
                importe=menores["importe"] or 0,
                detalle="Portal de la Comunidad, con IVA",
                color="#C98500",
            )
        )
    if subv:
        nodos.append(
            red.NodoRed(
                id="sub",
                etiqueta=f"Subvenciones\n({textos.numero(subv['n'])})",
                importe=subv["importe"] or 0,
                detalle="Base de Datos Nacional de Subvenciones",
                color="#199E70",
            )
        )
    seleccion = red.mapa(nodos, [(CENTRO, n.id) for n in nodos[1:]], alto=700)
    if seleccion and seleccion != CENTRO and seleccion != st.session_state.get("mg_contrato"):
        guardar("mg_contrato", seleccion)
        st.rerun()
    st.caption(
        "Contratos con fecha de "
        f"{anio} (por fecha del contrato o de formalización); los que no traen fecha no salen "
        "aquí. Importes de la Plataforma sin IVA y del portal con IVA, sin sumar entre sí."
    )

    # --- Detalle de lo pulsado ---
    marcado = st.session_state.get("mg_contrato")
    if marcado == "men" and menores:
        st.subheader("Contratos menores")
        st.markdown(
            f"{textos.numero(menores['n'])} contratos menores en {anio} por "
            f"{textos.euros(menores['importe'], 'con IVA')}. Son tantos que no se pintan uno a "
            "uno: míralos en **Contratos a revisar** (incluyendo menores) o en la ficha de cada "
            "órgano."
        )
    elif marcado == "sub" and subv:
        st.subheader("Subvenciones")
        st.markdown(
            f"{textos.numero(subv['n'])} concesiones en {anio} por "
            f"{textos.euros(subv['importe'])}. "
            "Detalle por convocatoria en la **Ficha de órgano** y en el **Mapa del dinero**."
        )
    elif marcado and marcado.startswith("con:"):
        detalle = datos_mapa.detalle_contrato(con, marcado[4:])
        if detalle:
            st.subheader((detalle["titulo"] or "Contrato")[:160])
            st.caption(f"{detalle['organo']} · {detalle['tipo_contrato'] or 'tipo sin dato'}")
            iva = textos.iva_fuente(detalle["fuente"])
            importe = detalle["importe_sin_iva"] or detalle["importe_con_iva"]
            presupuesto = detalle["presupuesto_sin_iva"] or detalle["presupuesto_con_iva"]
            m = st.columns(4)
            m[0].metric("Importe adjudicado", textos.euros(importe, iva))
            m[1].metric("Presupuesto de licitación", textos.euros(presupuesto, iva))
            m[2].metric(
                "Ofertas recibidas",
                textos.numero(detalle["n_ofertas"]) if detalle["n_ofertas"] else "Sin dato",
            )
            m[3].metric(
                "Del dinero de la consejería",
                textos.porcentaje((importe or 0) / entidad["credito"], 2),
                help="Importe adjudicado sobre el dinero disponible de la consejería este año.",
            )
            st.markdown(
                f"**Cómo se contrató:** {detalle['procedimiento'] or 'sin dato'}. "
                f"**Estado:** {detalle['estado'] or 'sin dato'}. "
                f"**Adjudicataria:** {detalle['adjudicatarios'] or 'sin dato'}."
            )
            st.caption(
                "Los datos abiertos no publican los criterios de adjudicación ni por qué se "
                "eligió a esta empresa; sí el procedimiento y el número de ofertas."
            )
            for fila in datos.motivos(con, detalle["contrato_id"]):
                senales.mostrar(con, fila["indicador"], detalle["contrato_id"])
            anomalia = datos.anomalia_contrato(con, detalle["contrato_id"])
            if anomalia:
                st.markdown(
                    f"**Contrato atípico** respecto a {textos.numero(anomalia['n_grupo'])} "
                    "contratos similares (señal experimental; atípico no significa "
                    f"irregular): {anomalia['motivo']}"
                )
            if detalle["url_origen"]:
                st.link_button(
                    "Ver el expediente oficial",
                    detalle["url_origen"],
                    icon=":material/open_in_new:",
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
