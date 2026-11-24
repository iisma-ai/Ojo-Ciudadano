"""Mapa general del dinero de la Comunidad de Madrid (D-026, D-033, D-038).

Pensado para un ciudadano cualquiera: una frase con el dinero del año y lo gastado, lo que
tocaría a cada habitante (con su figura) y un treemap de billetes donde cada bloque es una
consejería y cada billete vale lo mismo, así que más dinero = más billetes (los grises, sin
gastar). Al pulsar una consejería se ven sus contratos más grandes, también en billetes, y su
ficha. El mapa de nodos de D-033 se conserva como vista avanzada («Más opciones»).
Presupuesto y contratos son fuentes distintas: se comparan por consejería y año, no partida a
partida. Lo que no tenemos se dice en la propia pantalla. Sin personas físicas (D-007).
"""

import html
import math

import streamlit as st

from ojo_ciudadano.app import (
    billetes,
    datos,
    datos_contexto,
    datos_mapa,
    red,
    senales,
    textos,
)
from ojo_ciudadano.app.conexion import conexion
from ojo_ciudadano.ingesta import ine

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


@st.cache_data(show_spinner=False, ttl=86400)
def _poblacion() -> dict | None:
    return ine.poblacion()


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
    st.subheader(detalle["adjudicatarios"] or "Contrato sin adjudicataria")
    st.caption(
        f"{(detalle['titulo'] or 'Contrato')[:160]} · {detalle['organo']} · "
        f"{detalle['tipo_contrato'] or 'tipo sin dato'}"
    )
    iva = textos.iva_fuente(detalle["fuente"])
    importe = detalle["importe_sin_iva"] or detalle["importe_con_iva"]
    presupuesto = detalle["presupuesto_sin_iva"] or detalle["presupuesto_con_iva"]
    lineas = [
        f"- **Adjudicado:** {textos.euros(importe, iva)}",
        f"- **Precio de salida (licitación):** {textos.euros(presupuesto, iva)}",
        "- **Ofertas recibidas:** "
        + (textos.numero(detalle["n_ofertas"]) if detalle["n_ofertas"] else "sin dato"),
    ]
    if entidad:
        lineas.append(
            f"- **Parte del dinero de la consejería en el año:** "
            f"{textos.porcentaje((importe or 0) / entidad['credito'], 2)}"
        )
    st.markdown("\n".join(lineas))
    st.markdown(
        f"**Cómo se contrató:** {detalle['procedimiento'] or 'sin dato'}. "
        f"**Estado:** {detalle['estado'] or 'sin dato'}."
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


def vista_red(con, entidades, vista, datos_anio, anio, liquidado) -> None:
    """Vista avanzada: el mapa de nodos de D-033, tal cual estaba."""
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
            _ficha(con, marcado, entidades, datos_anio, anio, ampliada is not None)


def _ficha(con, marcado: tuple, entidades, datos_anio, anio, ampliada: bool) -> None:
    tipo, referencia = marcado
    if tipo == "con":
        ficha_contrato(con, referencia, entidades)
        return
    entidad = next((e for e in entidades if e["entidad"] == referencia), None)
    if entidad is None:
        st.info("Esa consejería no está en este periodo.")
    elif tipo == "ent":
        ficha_entidad(con, entidad, datos_anio, anio, ampliada)
    else:
        ficha_agrupado(con, tipo, entidad, anio)


# ------------------------------------------------------------------------------ billetes
def bloques_consejerias(entidades: list[dict], vista: str) -> list[billetes.Bloque]:
    bloques = []
    for indice, e in enumerate(entidades):
        importe = importe_vista(e, vista)
        if not importe or importe <= 0:
            continue
        detalle = ""
        if vista == "presupuesto" and e["gastado"] is not None:
            detalle = f"De media, unos {textos.millones(e['gastado'] / 365)} al día"
        bloques.append(
            billetes.Bloque(
                id=f"ent:{indice}",
                nombre=e["entidad"].replace("Consejería de ", "").replace("Consejería ", ""),
                importe=importe,
                gastado=e["llenado"] if vista == "presupuesto" else None,
                detalle=detalle,
            )
        )
    return bloques


def bloques_contratos(cuerpo: dict) -> tuple[list[billetes.Bloque], dict]:
    """Contratos más grandes de una consejería, uno por bloque. Los menores y las subvenciones
    van aparte, en una línea: juntos pesarían tanto que aplastarían a los contratos."""
    bloques, destinos = [], {}
    for c in cuerpo["contratos"]:
        id_con = f"con:{c['contrato_id']}"
        destinos[id_con] = ("con", c["contrato_id"])
        quien = (c["adjudicatarios"] or "Sin adjudicataria").split(" ; ")
        nombre = quien[0] + (f" y {len(quien) - 1} más" if len(quien) > 1 else "")
        bloques.append(
            billetes.Bloque(
                id=id_con,
                nombre=nombre,
                importe=c["importe"],
                detalle=f"{(c['titulo'] or '')[:120]} ({textos.iva_fuente(c['fuente'])})",
            )
        )
    return bloques, destinos


def tarjeta_ciudadano(datos_anio: dict, anio: int, poblacion: dict | None) -> None:
    """La frase principal del año y la figura con lo que tocaría a cada habitante."""
    credito, liquidado = datos_anio["credito"], datos_anio["liquidado"]
    if liquidado:
        gastado = datos_anio["gastado"] or 0
        de_cada = round(100 * gastado / credito) if credito else 0
        frase = (
            f"En <b>{anio}</b> la Comunidad de Madrid tuvo <b>{textos.millones(credito)}</b> "
            f"(millones de euros) y gastó <b>{de_cada} de cada 100 €</b>."
        )
        barra = (
            f'<div class="oc-barra" role="img" aria-label="Gastado: {de_cada} %">'
            f'<div style="width:{min(de_cada, 100)}%"></div></div>'
            f'<div class="oc-barra-pie"><span>Gastado: {textos.millones(gastado)}</span>'
            f"<span>Sin gastar: {textos.millones(max(credito - gastado, 0))}</span></div>"
        )
    else:
        frase = (
            f"Para <b>{anio}</b> la Comunidad de Madrid aprobó un presupuesto de "
            f"<b>{textos.millones(credito)}</b> (millones de euros). Cuánto se ha gastado se "
            "sabrá cuando cierre el año."
        )
        barra = ""

    por_persona, habitantes = "", ""
    referencia = ine.del_anio(poblacion, anio) if poblacion else None
    if referencia:
        anio_pob, n_hab = referencia
        euros_hab = round(credito / n_hab / 10) * 10
        cifra = f"{euros_hab:,.0f}".replace(",", ".")
        por_persona = (
            f'<p class="oc-persona-txt">Si ese dinero se repartiera entre sus '
            f"<b>{textos.numero(n_hab)} de habitantes</b>, a cada uno le tocarían unos</p>"
            f'<p class="oc-persona-cifra">{cifra} €</p>'
        )
        habitantes = (
            f'<div class="oc-habitantes">{billetes.svg_habitantes(n_hab / 1_000_000)}'
            f"<span>Cada figura, un millón de habitantes (a 1 de enero de {anio_pob})</span></div>"
        )
    contenido = f"""
<style>
.oc-tarjeta {{ display:flex; gap:28px; align-items:center; flex-wrap:wrap;
  padding:22px 26px; border-radius:18px; background:rgba(255,255,255,.045);
  border:1px solid rgba(170,225,255,.16); box-shadow:inset 0 1px 0 rgba(255,255,255,.08);
  font-family:Inter, sans-serif; color:#E7ECF3; }}
.oc-tarjeta .texto {{ flex:1 1 360px; min-width:0; }}
.oc-frase {{ font-size:1.45rem; line-height:1.45; margin:0 0 14px; font-weight:300; }}
.oc-frase b {{ font-weight:650; color:#fff; }}
.oc-barra {{ height:16px; border-radius:9px; background:#33415C; overflow:hidden; }}
.oc-barra div {{ height:100%; border-radius:9px;
  background:linear-gradient(90deg,#1E9E74,#3CC495); }}
.oc-barra-pie {{ display:flex; justify-content:space-between; font-size:.85rem;
  color:#93A1B8; margin-top:6px; }}
.oc-persona-txt {{ margin:18px 0 0; color:#B9C6D8; font-size:1rem; }}
.oc-persona-cifra {{ margin:0; font-size:3rem; font-weight:700; letter-spacing:-.02em;
  background:linear-gradient(180deg,#fff,#7DB3FF); -webkit-background-clip:text;
  background-clip:text; color:transparent; line-height:1.15; }}
.oc-habitantes {{ display:flex; gap:12px; align-items:center; flex-wrap:wrap;
  color:#93A1B8; font-size:.82rem; margin-top:6px; }}
.oc-persona {{ width:210px; max-width:42vw; height:auto; flex:0 0 auto; }}
.oc-salta {{ animation:salta 2.6s ease-in-out infinite; transform-origin:110px 216px; }}
.abanico {{ animation:abanico 2.6s ease-in-out infinite; transform-origin:110px 60px; }}
.cae {{ animation:cae 4.2s linear infinite; opacity:0; }}
@keyframes salta {{ 0%,100% {{ transform:translateY(0) }} 50% {{ transform:translateY(-7px) }} }}
@keyframes abanico {{ 0%,100% {{ transform:rotate(-3deg) }} 50% {{ transform:rotate(3deg) }} }}
@keyframes cae {{ 0% {{ transform:translateY(-10px); opacity:0 }} 15% {{ opacity:.9 }}
  85% {{ opacity:.9 }} 100% {{ transform:translateY(150px); opacity:0 }} }}
@media (prefers-reduced-motion: reduce) {{
  .oc-salta, .abanico {{ animation:none; }} .cae {{ animation:none; opacity:.8; }} }}
@media (max-width: 640px) {{ .oc-frase {{ font-size:1.15rem; }}
  .oc-persona-cifra {{ font-size:2.3rem; }} .oc-tarjeta {{ padding:16px; }} }}
</style>
<div class="oc-tarjeta">
  {billetes.svg_ciudadano()}
  <div class="texto">
    <p class="oc-frase">{frase}</p>
    {barra}
    {por_persona}
    {habitantes}
  </div>
</div>"""
    billetes.pintar(contenido, clave=f"mb_tarjeta_{anio}")
    fuentes = (
        f"Fuente: [presupuesto en datos abiertos de la Comunidad de Madrid]"
        f"({datos_anio['url_origen']}), descargado el {datos_anio['fecha_descarga']}"
    )
    if referencia:
        fuentes += (
            f" · [habitantes: Estadística Continua de Población del INE]"
            f"({poblacion['url_origen']}), descargado el {poblacion['fecha_descarga']}"
        )
    st.caption(fuentes + ". El reparto por habitante es una forma de dar escala, no un pago.")


def gasto_por_consejeria(entidades: list[dict]) -> str:
    """Una línea por consejería: barra de lo gastado, porcentaje, lo que quedó y el gasto medio
    diario. Ordenadas por dinero disponible."""
    filas = []
    for e in sorted(entidades, key=lambda e: -(e["credito"] or 0)):
        if e["gastado"] is None or not e["credito"]:
            continue
        llenado = e["llenado"] or 0
        nombre = html.escape(e["entidad"].replace("Consejería de ", ""))
        filas.append(
            f'<div class="oc-fila"><div class="oc-nombre">{nombre}</div>'
            f'<div class="oc-mini" role="img" aria-label="Gastado {textos.porcentaje(llenado)}">'
            f'<div style="width:{100 * llenado:.1f}%"></div></div>'
            f'<div class="oc-dato"><b>{textos.porcentaje(llenado)}</b> gastado · '
            f"quedan {textos.millones(e['sin_gastar'])} · "
            f"unos {textos.millones(e['gastado'] / 365)} al día</div></div>"
        )
    return (
        "<style>"
        ".oc-fila{display:grid;grid-template-columns:minmax(150px,1.3fr) 2fr minmax(230px,1.5fr);"
        "gap:14px;align-items:center;padding:7px 0;border-bottom:1px solid rgba(170,225,255,.08);"
        "font-family:Inter,sans-serif;color:#E7ECF3;font-size:.92rem}"
        ".oc-nombre{line-height:1.25}"
        ".oc-mini{height:12px;border-radius:7px;background:#33415C;overflow:hidden}"
        ".oc-mini div{height:100%;border-radius:7px;"
        "background:linear-gradient(90deg,#1E9E74,#3CC495)}"
        ".oc-dato{color:#93A1B8;font-size:.85rem}.oc-dato b{color:#E7ECF3}"
        "@media (max-width:760px){.oc-fila{grid-template-columns:1fr;gap:4px}}"
        "</style>" + "".join(filas)
    )


def vista_billetes(con, entidades, vista, datos_anio, anio) -> None:
    """El treemap de billetes: todas las consejerías y, al pulsar una, sus contratos."""
    nombres = [e["entidad"] for e in entidades]
    elegida = st.session_state.get("mb_consejeria")
    if elegida not in nombres:
        elegida = None
        st.session_state["mb_consejeria"] = None

    if elegida is None:
        bloques = bloques_consejerias(entidades, vista)
        if not bloques:
            st.info("No hay importes que mostrar en esta vista y periodo.")
            return
        valor = billetes.valor_billete(sum(b.importe for b in bloques))
        billetes.pintar(
            billetes.leyenda(valor, vista == "presupuesto" and datos_anio["liquidado"]),
            clave="mb_leyenda",
        )
        pulsado = billetes.mostrar(bloques, valor, clave=f"mb_general_{anio}_{vista}", alto=540)
        if pulsado and pulsado.startswith("ent:"):
            st.session_state["mb_consejeria"] = entidades[int(pulsado[4:])]["entidad"]
            st.session_state["mb_sel"] = None
            st.rerun()
        return

    entidad = next(e for e in entidades if e["entidad"] == elegida)
    cuerpo = _de_la_consejeria(entidad["organo_id"] or "", anio)
    bloques, destinos = bloques_contratos(cuerpo)
    izquierda, derecha = st.columns([5, 2])
    with izquierda:
        st.button(
            "Volver a todas las consejerías",
            icon=":material/arrow_back:",
            type="tertiary",
            on_click=lambda: st.session_state.update(mb_consejeria=None, mb_sel=None),
        )
        st.markdown(f"#### {elegida}: sus contratos más grandes de {anio}")
        if not bloques:
            st.info(
                "De este órgano no tenemos contratos ni subvenciones con fecha de este año en "
                "nuestras fuentes.",
                icon=":material/info:",
            )
        else:
            valor = billetes.valor_billete(sum(b.importe for b in bloques), objetivo=160)
            billetes.pintar(billetes.leyenda(valor, False), clave="mb_leyenda_c")
            pulsado = billetes.mostrar(
                bloques,
                valor,
                clave=f"mb_consejeria_{anio}_{elegida}",
                alto=520,
                ancho=720,
                con_cuota=False,
            )
            if pulsado in destinos:
                tipo, ref = destinos[pulsado]
                st.session_state["mb_sel"] = (tipo, ref or elegida)
            st.caption(
                "Cada bloque es un contrato; el nombre es la empresa que lo ganó. Los de la "
                "Plataforma van sin IVA y los del portal, con IVA."
            )
        aparte = []
        if cuerpo["menores"] and cuerpo["menores"]["importe"]:
            m = cuerpo["menores"]
            aparte.append(
                f"**{textos.numero(m['n'])} contratos menores** por "
                f"{textos.euros(m['importe'], 'con IVA')}"
            )
        if cuerpo["subvenciones"] and cuerpo["subvenciones"]["importe"]:
            s = cuerpo["subvenciones"]
            aparte.append(
                f"**{textos.numero(s['n'])} subvenciones** por {textos.euros(s['importe'])}"
            )
        if aparte:
            st.markdown(
                f"Además, en {anio}: " + " y ".join(aparte) + ". Son tantos que no caben uno a "
                "uno: míralos en **Contratos a revisar** o en la **Ficha de órgano**."
            )
    with derecha:
        marcado = st.session_state.get("mb_sel")
        _ficha(con, marcado or ("ent", elegida), entidades, datos_anio, anio, True)


# ------------------------------------------------------------------------------ pantalla
con = conexion()
st.header("A dónde va el dinero")
st.caption("El presupuesto de la Comunidad de Madrid, explicado con billetes.")

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
liquidados = {p["anio"] for p in periodos if p["liquidado"]}
c1, c2 = st.columns([3, 2])
anio = (
    c1.segmented_control(
        "Año",
        anios,
        default=por_defecto,
        format_func=lambda a: str(a) if a in liquidados else f"{a} (previsto)",
        key="mg_anio",
    )
    or por_defecto
)
with c2.expander("Más opciones", icon=":material/tune:"):
    vista = (
        st.radio("Qué dinero ver", list(VISTAS), format_func=VISTAS.get, key="mg_vista")
        or "presupuesto"
    )
    modo = st.radio(
        "Cómo verlo",
        ["billetes", "red"],
        format_func={"billetes": "Billetes", "red": "Red de contratos (avanzada)"}.get,
        key="mg_modo",
    )

datos_anio = _reparto(anio)
entidades = datos_anio["entidades"]
if not entidades:
    st.info("No hay datos de este periodo.")
    st.stop()
liquidado = datos_anio["liquidado"]

tarjeta_ciudadano(datos_anio, anio, _poblacion())

st.subheader("¿A dónde van cada 100 €?" if vista == "presupuesto" else VISTAS[vista])
if modo == "red":
    vista_red(con, entidades, vista, datos_anio, anio, liquidado)
else:
    vista_billetes(con, entidades, vista, datos_anio, anio)

if liquidado:
    st.subheader("¿Cuánto ha gastado cada consejería?")
    st.caption("De más a menos dinero. La barra verde es lo gastado; la gris, lo que quedó.")
    st.html(gasto_por_consejeria(entidades))

with st.expander("Ver los datos en tabla", icon=":material/table:"):
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
    if liquidado:
        st.caption(
            f"Pagado en el año: {textos.euros(datos_anio['pagado'])} (pagos realizados sobre el "
            "gasto reconocido). «Gastado» son las obligaciones reconocidas."
        )

with st.expander("Qué datos no tenemos", icon=":material/help:"):
    st.markdown(
        textos.AVISO_CONTEXTO + "\n\n"
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
