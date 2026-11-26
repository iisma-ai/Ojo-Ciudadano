"""Mapa del dinero: mapa general de la Comunidad de Madrid (D-026, D-033, D-038).

Pensado para un ciudadano cualquiera:
- una tarjeta con el dinero del año, lo gastado y lo que tocaría a cada habitante al año y al
  mes, con la mascota (el ojo del logo con manos);
- el mapa de burbujas (D-033, D-047, D-049): tamaño y color = dinero y cada burbuja se llena
  hasta lo gastado; por defecto con dos niveles, las consejerías y sus contratos más grandes,
  y, si se quiere, los contratos menores y las subvenciones agrupados (los frascos de D-038
  se quitaron, D-049). Las opciones del mapa van junto al mapa;
- el porcentaje gastado por cada consejería, de mayor a menor.
Las fuentes y lo que no tenemos van en un botón de información para no llenar la pantalla.
Presupuesto y contratos son fuentes distintas: se comparan por consejería y año, no partida a
partida. Sin personas físicas (D-007).
"""

import html
import math

import streamlit as st

from ojo_ciudadano.app import (
    billetes,
    datos,
    datos_contexto,
    datos_mapa,
    de_donde_viene,
    graficos_contexto,
    red,
    senales,
    textos,
)
from ojo_ciudadano.app import burbujas as mapa_burbujas
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
# las dos caras del dinero (D-054): por defecto, a dónde va
MODOS = {
    "va": ":material/payments: ¿A dónde va el dinero?",
    "viene": ":material/savings: ¿De dónde viene el dinero?",
}
CENTRO = "centro"
RADIO_ENTIDADES = {1: 300, 2: 230}  # distancia de las consejerías al centro, según los niveles
RADIO_CONTRATOS = 125  # distancia de los contratos a su consejería (se añade al radio anterior)
ALTO_MAPA = {1: 920, 2: 960}
ESTIRAR_Y = {1: 1.22, 2: 1.0}  # el mapa es más alto que ancho

# el ancho de la página lo fija estilo.css (D-045)


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


# ------------------------------------------------------------------------------ cuentas
def nombre_corto(nombre: str) -> str:
    """«Consejería de Familia, Juventud y Asuntos Sociales» → «Familia, Juventud y Asuntos
    Sociales»."""
    return nombre.replace("Consejería de ", "").replace("Consejería ", "")


def etiqueta_contrato(contrato: dict, ancho: int = 14) -> str:
    """Quién recibe el contrato (el importe va en otra línea; el título completo,
    al pasar el ratón y al pulsar)."""
    nombres = (contrato["adjudicatarios"] or "Sin adjudicataria").split(" ; ")
    quien = nombres[0][:24] + (f" (+{len(nombres) - 1})" if len(nombres) > 1 else "")
    return red.envolver(quien, ancho)


def importe_vista(entidad: dict, vista: str) -> float:
    if vista == "presupuesto":
        return entidad["credito"] or 0.0
    return entidad.get(CAMPO_VISTA[vista]) or 0.0


def llenado_vista(entidad: dict, vista: str) -> float | None:
    """Burbujas. Presupuesto: lo gastado. Contratos y subvenciones: qué parte del gasto de la
    consejería representan (orden de magnitud: son fuentes distintas)."""
    if vista == "presupuesto":
        return entidad["llenado"]
    if not entidad["gastado"]:
        return None
    return min(importe_vista(entidad, vista) / entidad["gastado"], 1.0)


def etiqueta_burbuja(nombre: str, importe: float, ancho: int = 20) -> str:
    """Nombre y cifra debajo de cada burbuja, para leerla sin pasar el ratón."""
    return red.envolver(nombre, ancho) + chr(10) + textos.millones(importe)


def total_fuente(entidad: dict, fuente: str) -> float:
    """Lo que la consejería adjudicó en el año en la misma fuente que el contrato (Plataforma
    sin IVA o portal con IVA): los billetes de un contrato son de cada 100 € de ese total."""
    campo = "contratos_plataforma" if fuente == "placsp" else "contratos_portal"
    return entidad.get(campo) or 0.0


# ------------------------------------------------------------------------------ mapa
def leyenda_burbujas(vista: str, liquidado: bool, niveles: int) -> str:
    if vista == "presupuesto":
        texto = "Cada burbuja es una consejería u órgano: cuanto **más grande y más clara**, más "
        texto += (
            "dinero tiene. Se **llena hasta lo gastado**; lo gris es lo que queda sin gastar. "
            if liquidado
            else "dinero tiene. Este año todavía no hay gasto publicado. "
        )
    else:
        texto = (
            "Cada burbuja es una consejería: el **tamaño y el color** son lo contratado (o "
            "subvencionado) en el año y se **llena** hasta la parte de su gasto que representa "
            "(orden de magnitud: son fuentes distintas). "
        )
    if niveles == 2:
        texto += (
            "Las pequeñas son sus contratos más grandes del año (en el móvil, se ven al "
            "pulsar la consejería). "
        )
    return texto + (
        "Pasa el ratón por una burbuja para ver sus cifras. Pulsa una consejería para ponerla "
        "en el centro con todos sus contratos, y un contrato para ver su ficha."
    )


def _hijos_agrupados(indice: int, entidad: dict, agregados: dict, destinos: dict) -> list:
    """Burbujas de los contratos menores y las subvenciones de una consejería, agrupados."""
    extra = agregados.get(entidad["organo_id"] or "", {})
    hijos = []
    if extra.get("menores"):
        destinos[f"men:{indice}"] = ("men", entidad["entidad"])
        hijos.append(
            red.NodoRed(
                id=f"men:{indice}",
                etiqueta=f"Menores\n({textos.numero(extra['menores']['n'])})",
                importe=extra["menores"]["importe"] or 0,
                detalle="Contratos menores, portal, con IVA",
                color="#C98500",
                grupo="agr",
            )
        )
    if extra.get("subvenciones"):
        destinos[f"sub:{indice}"] = ("sub", entidad["entidad"])
        hijos.append(
            red.NodoRed(
                id=f"sub:{indice}",
                etiqueta=f"Subvenciones\n({textos.numero(extra['subvenciones']['n'])})",
                importe=extra["subvenciones"]["importe"] or 0,
                detalle="Base de Datos Nacional de Subvenciones",
                color="#199E70",
                grupo="agr",
            )
        )
    return hijos


def grafo_general(entidades, vista, datos_anio, niveles, principales, agregados):
    """Nodos y enlaces del mapa, con el diseño radial calculado (la Comunidad en el centro, las
    consejerías en círculo y sus contratos en un anillo exterior)."""
    liquidado = datos_anio["liquidado"] and vista == "presupuesto"
    total = sum(importe_vista(e, vista) for e in entidades)
    nodos = [
        red.NodoRed(
            id=CENTRO,
            etiqueta="Comunidad\nde Madrid",
            importe=total,
            centro=True,
            detalle="Total de la Comunidad",
            llenado=datos_anio["gastado"] / datos_anio["credito"] if liquidado else None,
            x=0,
            y=0,
        )
    ]
    enlaces: list[tuple] = []
    destinos: dict[str, tuple] = {}
    radio = RADIO_ENTIDADES[niveles]
    con_importe = [(i, e) for i, e in enumerate(entidades) if importe_vista(e, vista) > 0]
    orden = red.alternar_tamanos(con_importe)
    for (indice, e), (x, y) in zip(orden, red.posiciones_radiales(len(orden), radio), strict=True):
        y *= ESTIRAR_Y[niveles]  # elipse algo más alta que ancha: las etiquetas no se pisan
        id_ent = f"ent:{indice}"
        destinos[id_ent] = ("ent", e["entidad"])
        nodos.append(
            red.NodoRed(
                id=id_ent,
                etiqueta=etiqueta_burbuja(nombre_corto(e["entidad"]), importe_vista(e, vista)),
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
        enlaces.append((CENTRO, id_ent, math.hypot(x, y)))
        if niveles != 2 or not e["organo_id"]:
            continue
        hijos = principales.get(e["organo_id"], [])
        angulo = math.atan2(y, x)
        agrupados = _hijos_agrupados(indice, e, agregados, destinos)
        total_hijos = len(hijos) + len(agrupados)
        for j, nodo_agr in enumerate(agrupados, start=len(hijos)):
            desvio = (j - (total_hijos - 1) / 2) * 0.17
            distancia = radio + RADIO_CONTRATOS + (46 if j % 2 else 0)
            nodo_agr.x = distancia * math.cos(angulo + desvio)
            nodo_agr.y = distancia * math.sin(angulo + desvio)
            nodos.append(nodo_agr)
            enlaces.append((id_ent, nodo_agr.id, math.hypot(nodo_agr.x - x, nodo_agr.y - y)))
        for j, c in enumerate(hijos):
            id_con = f"con:{c['contrato_id']}"
            destinos[id_con] = ("con", c["contrato_id"])
            # Anillo exterior en zigzag (dos radios) para que los de consejerías vecinas no se
            # pisen.
            desvio = (j - (total_hijos - 1) / 2) * 0.17
            distancia = radio + RADIO_CONTRATOS + (46 if j % 2 else 0)
            hx = distancia * math.cos(angulo + desvio)
            hy = distancia * math.sin(angulo + desvio)
            nodos.append(
                red.NodoRed(
                    id=id_con,
                    etiqueta=etiqueta_burbuja(etiqueta_contrato(c), c["importe"], 14),
                    importe=c["importe"],
                    titulo=c["adjudicatarios"] or "Sin adjudicataria",
                    detalle=f"{c['organo']} · {textos.iva_fuente(c['fuente'])}",
                    grupo="con",
                    x=hx,
                    y=hy,
                )
            )
            enlaces.append((id_ent, id_con, math.hypot(hx - x, hy - y)))
    return nodos, enlaces, destinos


def grafo_ampliado(entidad: dict, cuerpo: dict):
    """Una consejería en el centro y sus contratos más grandes, menores y subvenciones."""
    nodos = [
        red.NodoRed(
            id=CENTRO,
            etiqueta=etiqueta_burbuja(nombre_corto(entidad["entidad"]), entidad["credito"], 18),
            importe=entidad["credito"],
            llenado=entidad["llenado"],
            centro=True,
            detalle="Consejería",
            x=0,
            y=0,
        )
    ]
    destinos: dict[str, tuple] = {CENTRO: ("ent", entidad["entidad"])}
    hijos: list[red.NodoRed] = []
    for c in cuerpo["contratos"]:
        id_con = f"con:{c['contrato_id']}"
        destinos[id_con] = ("con", c["contrato_id"])
        hijos.append(
            red.NodoRed(
                id=id_con,
                etiqueta=etiqueta_burbuja(etiqueta_contrato(c, 18), c["importe"], 18),
                importe=c["importe"],
                titulo=c["adjudicatarios"] or "Sin adjudicataria",
                detalle=f"{c['organo']} · {textos.iva_fuente(c['fuente'])}",
                grupo="con",
            )
        )
    agregados = {entidad["organo_id"] or "": {}}
    if cuerpo["menores"]:
        agregados[entidad["organo_id"] or ""]["menores"] = cuerpo["menores"]
    if cuerpo["subvenciones"]:
        agregados[entidad["organo_id"] or ""]["subvenciones"] = cuerpo["subvenciones"]
    hijos += _hijos_agrupados(0, entidad, agregados, destinos)
    enlaces = []
    for hijo, (x, y) in zip(hijos, red.posiciones_radiales(len(hijos), 260), strict=True):
        hijo.x, hijo.y = x, y
        nodos.append(hijo)
        enlaces.append((CENTRO, hijo.id, 260))
    return nodos, enlaces, destinos


# ------------------------------------------------------------------------------ fichas
def ficha_entidad(entidad: dict, datos_anio: dict, anio: int, ampliada: bool) -> None:
    """Ficha de la consejería: sus cifras y sus contratos más grandes."""
    st.subheader(entidad["entidad"])
    k = st.columns(2)
    k[0].metric("Disponible", textos.millones(entidad["credito"]))
    if datos_anio["liquidado"]:
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
    if not entidad["organo_id"]:
        st.info(
            "De este órgano no tenemos contratos ni subvenciones en nuestras fuentes.",
            icon=":material/info:",
        )
        return
    if not ampliada:
        st.button(
            "Ver sus contratos más grandes",
            icon=":material/zoom_out_map:",
            on_click=lambda: st.session_state.update(mg_ampliada=entidad["entidad"], mg_sel=None),
        )
    cuerpo = _de_la_consejeria(entidad["organo_id"], anio)
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


def ficha_agrupado(tipo: str, entidad: dict, anio: int) -> None:
    """Ficha de la burbuja de contratos menores o de subvenciones de una consejería."""
    extra = _agregados(anio).get(entidad["organo_id"] or "", {})
    st.subheader("Contratos menores" if tipo == "men" else "Subvenciones")
    st.caption(entidad["entidad"])
    dato = extra.get("menores" if tipo == "men" else "subvenciones")
    if not dato:
        st.info("No hay datos de este año.")
    elif tipo == "men":
        st.markdown(
            f"{textos.numero(dato['n'])} contratos menores en {anio} por "
            f"{textos.euros(dato['importe'], 'con IVA')}. Son tantos que no se pintan uno a uno: "
            "míralos en **Contratos a revisar** o en la **Ficha de órgano**."
        )
    else:
        st.markdown(
            f"{textos.numero(dato['n'])} concesiones en {anio} por "
            f"{textos.euros(dato['importe'])}. El detalle por convocatoria está en la **Ficha de "
            "órgano**."
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
        f"- **Cómo se contrató:** {detalle['procedimiento'] or 'sin dato'}",
        f"- **Estado:** {detalle['estado'] or 'sin dato'}",
    ]
    if entidad:
        n = billetes.billetes_de_cada_100(importe or 0, total_fuente(entidad, detalle["fuente"]))
        lineas.append(
            f"- **De lo que adjudicó la consejería en el año:** {billetes.texto_de_cada_100(n)}"
        )
    st.markdown("\n".join(lineas))
    for fila in datos.motivos(con, detalle["contrato_id"]):
        senales.mostrar(con, fila["indicador"], detalle["contrato_id"])
    anomalia = datos.anomalia_contrato(con, detalle["contrato_id"])
    if anomalia:
        st.markdown(
            ":orange[**Contrato atípico**] respecto a "
            f"{textos.numero(anomalia['n_grupo'])} contratos "
            f"similares (señal experimental; atípico no significa irregular): {anomalia['motivo']}"
        )
    if detalle["url_origen"]:
        st.link_button(
            "Ver el expediente oficial", detalle["url_origen"], icon=":material/open_in_new:"
        )


def _ficha(con, marcado: tuple, entidades, datos_anio, ampliada: bool) -> None:
    tipo, referencia = marcado
    if tipo == "con":
        ficha_contrato(con, referencia, entidades)
        return
    entidad = next((e for e in entidades if e["entidad"] == referencia), None)
    if entidad is None:
        st.info("Esa consejería no está en este periodo.")
    elif tipo in ("men", "sub"):
        ficha_agrupado(tipo, entidad, datos_anio["anio"])
    else:
        ficha_entidad(entidad, datos_anio, datos_anio["anio"], ampliada)


# ------------------------------------------------------------------------------ presupuesto
def barra_presupuesto(datos_anio: dict, anio: int) -> str:
    """El presupuesto del año en una sola barra (D-052): llena hasta lo gastado, con lo gastado,
    lo que quedó sin gastar y el total debajo. Sin frases: las cifras hablan."""
    credito, liquidado = datos_anio["credito"], datos_anio["liquidado"]
    gastado = (datos_anio["gastado"] or 0) if liquidado else 0
    parte = min(gastado / credito, 1) if credito and liquidado else 0
    if liquidado:
        pie = (
            f'<div class="ocp-pie"><span><i class="g"></i>Gastado <b>{textos.millones(gastado)}'
            f"</b> · {textos.porcentaje(parte)}</span><span><i></i>Sin gastar "
            f"<b>{textos.millones(max(credito - gastado, 0))}</b></span></div>"
        )
    else:
        pie = (
            '<div class="ocp-pie"><span>Presupuesto inicial: el gasto se publica al cerrar '
            "el año.</span></div>"
        )
    marca = (
        f'<div class="marca" style="left:calc({100 * parte:.2f}% - 1px)"></div>'
        if liquidado
        else ""
    )
    return f"""
<style>
.ocp {{ font-family:Outfit, sans-serif; color:#E7ECF3; margin: 6px 0 4px; }}
.ocp-cab {{ display:flex; justify-content:space-between; align-items:baseline; gap:12px;
  margin-bottom:10px; }}
.ocp-cab h3 {{ margin:0; padding:0; font-size:1.35rem; font-weight:700; color:#E7ECF3; }}
.ocp-cab .total {{ font-size:1.9rem; font-weight:750; letter-spacing:-.02em;
  background:linear-gradient(180deg,#fff,#9FCBFF); -webkit-background-clip:text;
  background-clip:text; color:transparent; }}
.ocp-cab .total small {{ font-size:.85rem; font-weight:500; color:#9FB6CC;
  -webkit-text-fill-color:#9FB6CC; margin-left:6px; }}
.ocp-barra {{ position:relative; height:30px; border-radius:16px; overflow:hidden;
  background:linear-gradient(180deg, rgba(200,235,255,.14), rgba(170,225,255,.06));
  border:1px solid rgba(170,225,255,.3);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.16), 0 8px 24px rgba(0,8,22,.35); }}
.ocp-barra .lleno {{ height:100%; border-radius:15px 0 0 15px;
  background:linear-gradient(90deg,#2f7cf0,#38bdf8);
  box-shadow:0 0 22px rgba(56,189,248,.5), inset 0 1px 0 rgba(255,255,255,.35);
  transform-origin:left center; animation: ocp-crece 1.2s cubic-bezier(.25,.8,.25,1) both; }}
.ocp-barra .marca {{ position:absolute; top:-2px; bottom:-2px; width:2px; background:#fff;
  opacity:.85; box-shadow:0 0 8px #fff; }}
@keyframes ocp-crece {{ from {{ transform:scaleX(0); }} to {{ transform:none; }} }}
.ocp-pie {{ display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px 20px;
  margin-top:10px; font-size:.95rem; color:#9FB6CC; }}
.ocp-pie b {{ color:#E7ECF3; }}
.ocp-pie i {{ display:inline-block; width:12px; height:12px; border-radius:4px; margin-right:7px;
  vertical-align:-1px; background:rgba(170,225,255,.2); border:1px solid rgba(170,225,255,.4); }}
.ocp-pie i.g {{ background:linear-gradient(90deg,#2f7cf0,#38bdf8); border:none; }}
@media (prefers-reduced-motion: reduce) {{ .ocp-barra .lleno {{ animation:none; }} }}
</style>
<div class="ocp">
  <div class="ocp-cab"><h3>Presupuesto {anio}</h3>
    <span class="total">{textos.millones(credito)}<small>en total</small></span></div>
  <div class="ocp-barra" role="img" aria-label="Gastado {textos.porcentaje(parte)} de
    {textos.millones(credito)}"><div class="lleno" style="width:{100 * parte:.2f}%"></div>
    {marca}
  </div>
  {pie}
</div>"""


# ------------------------------------------------------------------------------ tarjeta del año
def _redondeo(valor: float, a: int = 10) -> str:
    return f"{round(valor / a) * a:,.0f}".replace(",", ".")


def tarjeta_ciudadano(datos_anio: dict, anio: int, poblacion: dict | None) -> None:
    """La frase principal del año y la mascota con lo que tocaría a cada habitante."""
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
        por_persona = (
            f'<p class="oc-persona-txt">Si el dinero de todo el año se repartiera entre sus '
            f"<b>{textos.numero(n_hab)} de habitantes</b>, a cada uno le tocarían unos</p>"
            f'<p class="oc-persona-cifra">{_redondeo(credito / n_hab)} € '
            f'<span class="oc-periodo">al año</span></p>'
            f'<p class="oc-persona-mes">unos <b>{_redondeo(credito / n_hab / 12)} € al mes</b></p>'
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
  font-family:Outfit, sans-serif; color:#E7ECF3; }}
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
  line-height:1.15; color:#fff; }}
.oc-periodo {{ font-size:1.1rem; font-weight:500; color:#7DB3FF; letter-spacing:0; }}
.oc-persona-mes {{ margin:0 0 8px; color:#B9C6D8; font-size:1rem; }}
.oc-persona-mes b {{ color:#E7ECF3; }}
.oc-habitantes {{ display:flex; gap:12px; align-items:center; flex-wrap:wrap;
  color:#93A1B8; font-size:.82rem; margin-top:6px; }}
{billetes.CSS_OJO}
@media (max-width: 640px) {{ .oc-frase {{ font-size:1.15rem; }}
  .oc-persona-cifra {{ font-size:2.3rem; }} .oc-tarjeta {{ padding:16px; }} }}
</style>
<div class="oc-tarjeta">
  {billetes.svg_ojo()}
  <div class="texto">
    <p class="oc-frase">{frase}</p>
    {barra}
    {por_persona}
    {habitantes}
  </div>
</div>"""
    billetes.pintar(contenido, clave=f"mg_tarjeta_{anio}")


def gasto_por_consejeria(entidades: list[dict]) -> str:
    """Una línea por consejería: su barra de lo gastado y el porcentaje, de mayor a menor."""
    filas = []
    con_gasto = [e for e in entidades if e["gastado"] is not None and e["credito"]]
    for e in sorted(con_gasto, key=lambda e: -(e["llenado"] or 0)):
        llenado = e["llenado"] or 0
        filas.append(
            f'<div class="oc-fila"><div class="oc-nombre">'
            f"{html.escape(nombre_corto(e['entidad']))}</div>"
            f'<div class="oc-mini" role="img" aria-label="Gastado {textos.porcentaje(llenado)}">'
            f'<div style="width:{100 * llenado:.1f}%"></div></div>'
            f'<div class="oc-dato">{textos.porcentaje(llenado)}</div></div>'
        )
    return (
        "<style>"
        ".oc-fila{display:grid;grid-template-columns:minmax(150px,1.2fr) 3fr 56px;"
        "gap:14px;align-items:center;padding:7px 0;border-bottom:1px solid rgba(170,225,255,.08);"
        "font-family:Outfit,sans-serif;color:#E7ECF3;font-size:.92rem}"
        ".oc-nombre{line-height:1.25}"
        ".oc-mini{height:12px;border-radius:7px;background:#33415C;overflow:hidden}"
        ".oc-mini div{height:100%;border-radius:7px;"
        "background:linear-gradient(90deg,#1E9E74,#3CC495)}"
        ".oc-dato{font-weight:600;text-align:right}"
        "@media (max-width:640px){.oc-fila{grid-template-columns:1fr 56px}"
        ".oc-mini{grid-column:1 / -1;grid-row:2}}"
        "</style>" + "".join(filas)
    )


def barras_dinero(entidades: list[dict]) -> str:
    """Una barra por consejería (D-047): su largo es todo el dinero disponible y, dentro, la
    parte gastada en azul intenso; lo que queda sin gastar, en cristal claro. A la derecha, el
    porcentaje gastado y lo que quedó sin gastar. De más a menos dinero. HTML y CSS, sin Plotly."""
    con_gasto = [e for e in entidades if e["gastado"] is not None and e["credito"]]
    if not con_gasto:
        return ""
    maximo = max(e["credito"] for e in con_gasto)
    filas = []
    for j, e in enumerate(sorted(con_gasto, key=lambda e: -e["credito"])):
        largo = 100 * e["credito"] / maximo
        gastado = min(max(e["llenado"] or 0, 0), 1)
        filas.append(
            f'<div class="ocb-fila" style="--j:{j}">'
            f'<div class="ocb-nombre"><b>{html.escape(nombre_corto(e["entidad"]))}</b>'
            f"<span>{textos.millones(e['credito'])} disponibles</span></div>"
            f'<div class="ocb-pista"><div class="ocb-total" style="width:max({largo:.2f}%, 6px)"'
            f' role="img" aria-label="Gastado {textos.porcentaje(gastado)} de '
            f'{textos.millones(e["credito"])}">'
            f'<div class="ocb-gastado" style="width:{100 * gastado:.2f}%"></div></div></div>'
            f'<div class="ocb-dato"><b>{textos.porcentaje(gastado)}</b>'
            f"<span>{textos.millones(e['sin_gastar'] or 0)} sin gastar</span></div></div>"
        )
    leyenda = (
        '<div class="ocb-leyenda"><span><i class="ocb-i-gastado"></i>Gastado</span>'
        '<span><i class="ocb-i-resto"></i>Sin gastar</span>'
        "<span>El largo de cada barra es todo su dinero del año.</span></div>"
    )
    return (
        """<style>
.ocb { font-family: Outfit, sans-serif; color: #E7ECF3; }
.ocb-leyenda { display:flex; gap:22px; flex-wrap:wrap; font-size:.85rem; color:#9FB6CC;
  margin: 0 0 14px; }
.ocb-leyenda span { display:flex; align-items:center; gap:8px; }
.ocb-leyenda i { width:22px; height:10px; border-radius:6px; display:inline-block; }
.ocb-i-gastado { background: linear-gradient(90deg, #2f7cf0, #38bdf8);
  box-shadow: 0 0 10px rgba(56,189,248,.45); }
.ocb-i-resto { background: rgba(170,225,255,.16); border: 1px solid rgba(170,225,255,.35); }
.ocb-fila { display:grid; grid-template-columns: minmax(170px, 1.1fr) 4fr minmax(110px, .7fr);
  gap: 18px; align-items:center; padding: 9px 0;
  border-bottom: 1px solid rgba(170,225,255,.07); }
.ocb-nombre { display:flex; flex-direction:column; line-height:1.25; min-width:0; }
.ocb-nombre b { font-weight:600; font-size:.95rem; }
.ocb-nombre span, .ocb-dato span { font-size:.78rem; color:#8FA7BF; }
.ocb-pista { height: 22px; display:flex; align-items:center; }
.ocb-total { height: 100%; border-radius: 12px; position: relative; overflow: hidden;
  background: linear-gradient(180deg, rgba(200,235,255,.16), rgba(170,225,255,.07));
  border: 1px solid rgba(170,225,255,.28);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.18), 0 6px 18px rgba(0,8,22,.35);
  transform-origin: left center;
  animation: ocb-crece 1s cubic-bezier(.25,.8,.25,1) both;
  animation-delay: calc(var(--j) * 45ms); }
.ocb-gastado { height: 100%; border-radius: 11px 0 0 11px;
  background: linear-gradient(90deg, #2f7cf0, #38bdf8);
  box-shadow: 0 0 16px rgba(56,189,248,.45), inset 0 1px 0 rgba(255,255,255,.35); }
.ocb-gastado[style*="width:100.00%"] { border-radius: 11px; }
.ocb-dato { display:flex; flex-direction:column; align-items:flex-end; line-height:1.2; }
.ocb-dato b { font-size: 1.15rem; font-weight: 650; }
@keyframes ocb-crece { from { transform: scaleX(0); opacity: 0; }
  to { transform: none; opacity: 1; } }
@media (prefers-reduced-motion: reduce) { .ocb-total { animation: none; } }
@media (max-width: 640px) {
  .ocb-fila { grid-template-columns: 1fr auto; }
  .ocb-pista { grid-column: 1 / -1; grid-row: 2; }
}
</style><div class="ocb">"""
        + leyenda
        + "".join(filas)
        + "</div>"
    )


def fuentes(datos_anio: dict, anio: int, poblacion: dict | None) -> None:
    """Todo lo que es fuente, matiz o límite de los datos, en el desplegable del final."""
    lineas = [
        f"- **Presupuesto y gasto:** [datos abiertos de la Comunidad de Madrid]"
        f"({datos_anio['url_origen']}), descargado el {datos_anio['fecha_descarga']}. "
        "«Gastado» son las obligaciones reconocidas.",
    ]
    referencia = ine.del_anio(poblacion, anio) if poblacion else None
    if referencia:
        lineas.append(
            f"- **Habitantes:** [Estadística Continua de Población del INE]"
            f"({poblacion['url_origen']}), a 1 de enero de {referencia[0]}, descargado el "
            f"{poblacion['fecha_descarga']}. El reparto por habitante es una forma de dar "
            "escala, no un pago."
        )
    lineas.append(
        "- **Contratos:** Plataforma de Contratación del Sector Público (sin IVA) y Portal de "
        "la Contratación Pública de la Comunidad (con IVA); no se suman entre sí. Solo los "
        f"contratos con fecha de {anio} (del contrato o de la formalización)."
    )
    st.markdown("**Fuentes**\n\n" + "\n".join(lineas))
    st.markdown(textos.AVISO_CONTEXTO)
    st.markdown(
        "**Qué datos no tenemos**\n\n"
        "- **Gasto del año en curso:** la Comunidad publica el presupuesto liquidado al cerrar "
        "el año; de 2026 solo hay presupuesto inicial.\n"
        "- **Gasto que no es contratación:** personal, transferencias, deuda y otras partidas no "
        "pasan por contratos. No sabemos qué partida financió cada contrato.\n"
        "- **Contratos sin fecha:** no se pueden asignar a un año y no salen en el mapa.\n"
        "- **Criterios de adjudicación:** los datos abiertos no dicen por qué se eligió a cada "
        "empresa; solo el procedimiento y el número de ofertas.\n"
        "- **Órganos fuera de las consejerías** (Asamblea, Cámara de Cuentas, deuda pública, "
        "fondo de contingencia): tienen presupuesto pero no contratos en nuestras fuentes.\n"
        "- **Contratos menores recientes:** los últimos meses de 2026 están incompletos en "
        "origen. " + textos.AVISO_MENORES_RECIENTES
    )


# ------------------------------------------------------------------------------ pantalla
con = conexion()
st.header("Mapa del dinero")

periodos = datos_mapa.periodos(con)
if not periodos:
    st.warning(
        "El presupuesto de la Comunidad no está disponible todavía en esta versión de la web.",
        icon=":material/database:",
    )
    st.stop()

# el selector grande de las dos caras del dinero (D-054; su aspecto, en estilo.css)
modo = (
    st.segmented_control(
        "Qué quieres ver",
        list(MODOS),
        default="va",
        format_func=MODOS.get,
        key="mg_modo",
        label_visibility="collapsed",
        width="stretch",
    )
    or "va"
)

anios = [p["anio"] for p in periodos]
por_defecto = next((p["anio"] for p in periodos if p["liquidado"]), anios[0])
liquidados = {p["anio"] for p in periodos if p["liquidado"]}
anio = (
    st.segmented_control(
        "Año",
        anios,
        default=por_defecto,
        format_func=lambda a: str(a) if a in liquidados else f"{a} (previsto)",
        key="mg_anio",
    )
    or por_defecto
)
if modo == "viene":
    de_donde_viene.pintar(con, anio, _poblacion())
    st.stop()

datos_anio = {**_reparto(anio), "anio": anio}
entidades = datos_anio["entidades"]
if not entidades:
    st.info("No hay datos de este periodo.")
    st.stop()
liquidado = datos_anio["liquidado"]
poblacion = _poblacion()

# lo primero, el presupuesto del año en una barra (D-052); lo de cada habitante, abajo
billetes.pintar(barra_presupuesto(datos_anio, anio), clave=f"mg_presupuesto_{anio}")

# --- Mapa de burbujas, con sus opciones al lado del título ---
nombres = [e["entidad"] for e in entidades]
ampliada = st.session_state.get("mg_ampliada")
if ampliada not in nombres:
    ampliada = None
    st.session_state["mg_ampliada"] = None

titulo, opciones = st.columns([6, 1], vertical_alignment="bottom")
titulo.subheader("Cuánto tiene y cuánto ha gastado cada consejería")
vista, niveles, por_consejeria, con_agrupados = "presupuesto", 2, 2, False
if ampliada is None:
    with opciones.popover("Opciones", icon=":material/tune:", width="stretch"):
        vista = (
            st.radio("Qué dinero ver", list(VISTAS), format_func=VISTAS.get, key="mg_vista")
            or "presupuesto"
        )
        # por defecto, dos niveles: las consejerías y sus contratos más grandes (D-049)
        niveles = (
            st.segmented_control(
                "Qué mostrar", list(NIVELES), default=2, format_func=NIVELES.get, key="mg_niveles"
            )
            or 2
        )
        por_consejeria = st.slider(
            "Contratos por consejería",
            1,
            5,
            2,
            disabled=niveles == 1,
            key="mg_contratos",
            help="Cuántos de los contratos más grandes del año se dibujan junto a cada consejería.",
        )
        con_agrupados = st.toggle(
            "Añadir menores y subvenciones",
            disabled=niveles == 1,
            key="mg_agrupados",
            help="Una burbuja por consejería con sus contratos menores y otra con sus "
            "subvenciones.",
        )

izquierda, derecha = st.columns([5, 2])
with izquierda:
    if ampliada is None:
        principales = _principales(anio, por_consejeria) if niveles == 2 else {}
        agregados = _agregados(anio) if (niveles == 2 and con_agrupados) else {}
        nodos, enlaces, destinos = grafo_general(
            entidades, vista, datos_anio, niveles, principales, agregados
        )
        st.markdown(leyenda_burbujas(vista, liquidado, niveles))
        alto = ALTO_MAPA[niveles]
    else:
        st.button(
            "Volver a todas las consejerías",
            icon=":material/arrow_back:",
            type="tertiary",
            on_click=lambda: st.session_state.update(mg_ampliada=None, mg_sel=None),
        )
        entidad_amp = next(e for e in entidades if e["entidad"] == ampliada)
        cuerpo = _de_la_consejeria(entidad_amp["organo_id"] or "", anio)
        nodos, enlaces, destinos = grafo_ampliado(entidad_amp, cuerpo)
        st.markdown(
            f"Los **{len(cuerpo['contratos'])} contratos más grandes** de {anio} de {ampliada}, "
            "más los menores y las subvenciones agrupados. **Tamaño y color = importe.**"
        )
        alto = 760
    # burbujas con la estética de la presentación (D-047), dibujadas en un lienzo propio
    marcada = st.session_state.get("mg_sel")
    sel_id = next((k for k, v in destinos.items() if v == marcada), None)
    seleccion = mapa_burbujas.mapa(
        nodos, enlaces, alto, clave=f"mg_burbujas_{ampliada or 'todas'}", seleccionado=sel_id
    )
    if seleccion and seleccion in destinos:
        tipo_sel, referencia = destinos[seleccion]
        entidad_sel = next((e for e in entidades if e["entidad"] == referencia), None)
        if ampliada is None and tipo_sel == "ent" and entidad_sel and entidad_sel["organo_id"]:
            # pulsar una consejería la pone en el centro con todo lo que conecta (D-050)
            st.session_state.update(mg_ampliada=referencia, mg_sel=("ent", referencia))
            st.rerun()
        st.session_state["mg_sel"] = destinos[seleccion]

with derecha:
    st.html('<span class="oc-ficha-mapa"></span>')  # marca la columna de la ficha (CSS)
    marcado = st.session_state.get("mg_sel")
    if not marcado and ampliada is not None:
        marcado = ("ent", ampliada)
    if not marcado:
        st.info(
            "Pulsa una burbuja del mapa y aquí verás su ficha: cuánto dinero tiene, cuánto ha "
            "gastado y, si es un contrato, cómo se contrató y cuántas ofertas hubo.",
            icon=":material/touch_app:",
        )
    else:
        _ficha(con, marcado, entidades, datos_anio, ampliada is not None)

if liquidado:
    st.subheader("Dinero de cada consejería y cuánto ha gastado")
    st.html(barras_dinero(entidades))
    with st.expander("Gráficas por separado: porcentaje gastado y dinero sin gastar"):
        st.markdown("**Porcentaje gastado**")
        st.html(gasto_por_consejeria(entidades))
        sin_gastar = [e for e in entidades if e["sin_gastar"]]
        st.markdown("**Dinero sin gastar**")
        st.plotly_chart(
            graficos_contexto.barras_horizontales(
                [e["entidad"] for e in sin_gastar], [e["sin_gastar"] for e in sin_gastar]
            ),
            config=graficos_contexto.GRAFICO_CONFIG,
        )
# la tabla de todas las consejerías, en las dos formas del mapa
with st.expander("Todas las consejerías, en una tabla", icon=":material/table:"):
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

with st.expander("Si se repartiera entre todos los habitantes", icon=":material/groups:"):
    tarjeta_ciudadano(datos_anio, anio, poblacion)

# Fuentes, matices y datos que no tenemos, abajo del todo (D-043).
with st.expander("Fuentes y qué datos no tenemos", icon=":material/info:"):
    fuentes(datos_anio, anio, poblacion)
