"""Mapa del dinero: mapa general de la Comunidad de Madrid (D-026, D-033, D-038).

Pensado para un ciudadano cualquiera:
- una tarjeta con el dinero del año, lo gastado y lo que tocaría a cada habitante al año y al
  mes, con la mascota (el ojo del logo con manos);
- el mapa de nodos de D-033, donde cada nodo es un **frasco de 100 billetes**: el de la
  Comunidad está lleno y el de cada consejería lleva tantos billetes como euros recibe de cada
  100 (los grises, sin gastar). Las opciones del mapa van junto al mapa;
- el porcentaje gastado por cada consejería, de mayor a menor.
Las fuentes y lo que no tenemos van en un botón de información para no llenar la pantalla.
Presupuesto y contratos son fuentes distintas: se comparan por consejería y año, no partida a
partida. Sin personas físicas (D-007).
"""

import html
import math

import streamlit as st

from ojo_ciudadano.app import billetes, datos, datos_contexto, datos_mapa, red, senales, textos
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
RADIO_ENTIDADES = {1: 300, 2: 230}  # distancia de las consejerías al centro, según los niveles
RADIO_CONTRATOS = 125  # distancia de los contratos a su consejería (se añade al radio anterior)
ALTO_MAPA = {1: 920, 2: 960}
ESTIRAR_Y = {1: 1.22, 2: 1.0}  # el mapa es más alto que ancho
FRASCO = {"centro": 78, "ent": 50, "con": 28}  # radio de cada frasco en el mapa

# el ancho de la página lo fija estilo.css (D-045)


@st.cache_data(show_spinner=False, ttl=3600)
def _reparto(anio: int) -> dict:
    return datos_mapa.reparto(conexion(), anio)


@st.cache_data(show_spinner=False, ttl=3600)
def _principales(anio: int, n: int) -> dict:
    return datos_mapa.contratos_principales(conexion(), anio, n)


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
    """Quién recibe el contrato (los euros van en la etiqueta del frasco; el importe y el título,
    al pasar el ratón y al pulsar)."""
    nombres = (contrato["adjudicatarios"] or "Sin adjudicataria").split(" ; ")
    quien = nombres[0][:24] + (f" (+{len(nombres) - 1})" if len(nombres) > 1 else "")
    return red.envolver(quien, ancho)


def importe_vista(entidad: dict, vista: str) -> float:
    if vista == "presupuesto":
        return entidad["credito"] or 0.0
    return entidad.get(CAMPO_VISTA[vista]) or 0.0


def total_fuente(entidad: dict, fuente: str) -> float:
    """Lo que la consejería adjudicó en el año en la misma fuente que el contrato (Plataforma
    sin IVA o portal con IVA): los billetes de un contrato son de cada 100 € de ese total."""
    campo = "contratos_plataforma" if fuente == "placsp" else "contratos_portal"
    return entidad.get(campo) or 0.0


# ------------------------------------------------------------------------------ mapa de frascos
def leyenda_mapa(vista: str, liquidado: bool, niveles: int) -> str:
    if vista == "presupuesto":
        texto = (
            "El frasco del centro es todo el dinero de la Comunidad: **100 billetes**. Cada "
            "consejería se lleva **los billetes que recibe de cada 100 €**, y su etiqueta dice "
            "cuántos euros son. "
        )
        if not liquidado:
            texto += "Este año todavía no hay gasto publicado. "
    else:
        texto = (
            f"Frascos de **{VISTAS[vista].lower()}**: cada consejería lleva los billetes que le "
            "tocan de cada 100 € del total. "
        )
    if niveles == 2:
        texto += (
            "Los frascos pequeños son sus contratos más grandes: de cada 100 € que esa "
            "consejería adjudicó en contratos, cuántos fueron a ese contrato. "
        )
    return texto + "Pulsa un frasco para ver su ficha."


def grafo_general(entidades, vista, datos_anio, niveles, principales):
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
            detalle="Todo el dinero: 100 de cada 100 €",
            imagen=billetes.imagen_frasco(
                100, datos_anio["gastado"] / datos_anio["credito"] if liquidado else None, True
            ),
            tamano=FRASCO["centro"],
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
        n = billetes.billetes_de_cada_100(importe_vista(e, vista), total)
        nodos.append(
            red.NodoRed(
                id=id_ent,
                etiqueta=red.envolver(nombre_corto(e["entidad"]), 24),
                importe=importe_vista(e, vista),
                titulo=e["entidad"],
                detalle=f"Recibe {billetes.texto_de_cada_100(n)} de la Comunidad",
                imagen=billetes.imagen_frasco(n, e["llenado"] if liquidado else None),
                tamano=FRASCO["ent"] if niveles == 1 else 38,
                x=x,
                y=y,
            )
        )
        enlaces.append((CENTRO, id_ent, math.hypot(x, y)))
        if niveles != 2 or not e["organo_id"]:
            continue
        hijos = principales.get(e["organo_id"], [])
        angulo = math.atan2(y, x)
        for j, c in enumerate(hijos):
            id_con = f"con:{c['contrato_id']}"
            destinos[id_con] = ("con", c["contrato_id"])
            n_c = billetes.billetes_de_cada_100(c["importe"], total_fuente(e, c["fuente"]))
            # Anillo exterior en zigzag (dos radios) para que los de consejerías vecinas no se
            # pisen.
            desvio = (j - (len(hijos) - 1) / 2) * 0.17
            distancia = radio + RADIO_CONTRATOS + (46 if j % 2 else 0)
            hx = distancia * math.cos(angulo + desvio)
            hy = distancia * math.sin(angulo + desvio)
            nodos.append(
                red.NodoRed(
                    id=id_con,
                    etiqueta=etiqueta_contrato(c),
                    importe=c["importe"],
                    titulo=c["adjudicatarios"] or "Sin adjudicataria",
                    detalle=(
                        f"{billetes.texto_de_cada_100(n_c)} de lo que adjudicó la consejería "
                        f"({textos.iva_fuente(c['fuente'])})"
                    ),
                    grupo="con",
                    imagen=billetes.imagen_frasco(n_c),
                    tamano=FRASCO["con"],
                    x=hx,
                    y=hy,
                )
            )
            enlaces.append((id_ent, id_con, math.hypot(hx - x, hy - y)))
    return nodos, enlaces, destinos


def grafo_ampliado(entidad: dict, cuerpo: dict, datos_anio: dict):
    """Una consejería en el centro (su frasco lleno) y sus contratos más grandes alrededor."""
    liquidado = datos_anio["liquidado"]
    nodos = [
        red.NodoRed(
            id=CENTRO,
            etiqueta=red.envolver(nombre_corto(entidad["entidad"]), 18),
            importe=entidad["credito"],
            centro=True,
            detalle="Consejería",
            imagen=billetes.imagen_frasco(100, entidad["llenado"] if liquidado else None, True),
            tamano=FRASCO["centro"],
            x=0,
            y=0,
        )
    ]
    destinos: dict[str, tuple] = {}
    enlaces = []
    contratos = cuerpo["contratos"]
    for c, (x, y) in zip(contratos, red.posiciones_radiales(len(contratos), 270), strict=True):
        id_con = f"con:{c['contrato_id']}"
        destinos[id_con] = ("con", c["contrato_id"])
        n_c = billetes.billetes_de_cada_100(c["importe"], total_fuente(entidad, c["fuente"]))
        nodos.append(
            red.NodoRed(
                id=id_con,
                etiqueta=etiqueta_contrato(c, 16),
                importe=c["importe"],
                titulo=c["adjudicatarios"] or "Sin adjudicataria",
                detalle=f"{(c['titulo'] or '')[:120]} ({textos.iva_fuente(c['fuente'])})",
                grupo="con",
                imagen=billetes.imagen_frasco(n_c),
                tamano=30,
                x=x,
                y=y,
            )
        )
        enlaces.append((CENTRO, id_con, 270))
    return nodos, enlaces, destinos


# ------------------------------------------------------------------------------ fichas
def ficha_entidad(entidad: dict, datos_anio: dict, ampliada: bool) -> None:
    st.subheader(entidad["entidad"])
    n = billetes.billetes_de_cada_100(entidad["credito"], datos_anio["credito"])
    lineas = [
        f"- **Dinero del año:** {textos.millones(entidad['credito'])}",
        f"- **Recibe:** {billetes.texto_de_cada_100(n)} de la Comunidad",
    ]
    if datos_anio["liquidado"]:
        lineas += [
            f"- **Gastado:** {textos.millones(entidad['gastado'])} "
            f"({textos.porcentaje(entidad['llenado'])})",
            f"- **Sin gastar:** {textos.millones(entidad['sin_gastar'])}",
        ]
    else:
        lineas.append("- **Gastado:** se publica al cerrar el año")
    st.markdown("\n".join(lineas))
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
            f"**Contrato atípico** respecto a {textos.numero(anomalia['n_grupo'])} contratos "
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
    else:
        ficha_entidad(entidad, datos_anio, ampliada)


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
        "font-family:Inter,sans-serif;color:#E7ECF3;font-size:.92rem}"
        ".oc-nombre{line-height:1.25}"
        ".oc-mini{height:12px;border-radius:7px;background:#33415C;overflow:hidden}"
        ".oc-mini div{height:100%;border-radius:7px;"
        "background:linear-gradient(90deg,#1E9E74,#3CC495)}"
        ".oc-dato{font-weight:600;text-align:right}"
        "@media (max-width:640px){.oc-fila{grid-template-columns:1fr 56px}"
        ".oc-mini{grid-column:1 / -1;grid-row:2}}"
        "</style>" + "".join(filas)
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
        "Esta base no tiene todavía el presupuesto de la Comunidad. Ejecuta "
        "`uv run python -m ojo_ciudadano.modelo.contexto` (docs/12-datos-cm.md).",
        icon=":material/database:",
    )
    st.stop()

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
datos_anio = _reparto(anio)
entidades = datos_anio["entidades"]
if not entidades:
    st.info("No hay datos de este periodo.")
    st.stop()
liquidado = datos_anio["liquidado"]
poblacion = _poblacion()

tarjeta_ciudadano(datos_anio, anio, poblacion)

# --- Mapa de frascos, con sus opciones al lado del título ---
nombres = [e["entidad"] for e in entidades]
ampliada = st.session_state.get("mg_ampliada")
if ampliada not in nombres:
    ampliada = None
    st.session_state["mg_ampliada"] = None

titulo, opciones = st.columns([6, 1], vertical_alignment="bottom")
titulo.subheader("¿A dónde van cada 100 €?")
vista, niveles, por_consejeria = "presupuesto", 1, 3
if ampliada is None:
    with opciones.popover("Opciones", icon=":material/tune:", width="stretch"):
        vista = (
            st.radio("Qué dinero ver", list(VISTAS), format_func=VISTAS.get, key="mg_vista")
            or "presupuesto"
        )
        niveles = (
            st.segmented_control(
                "Qué mostrar", list(NIVELES), default=1, format_func=NIVELES.get, key="mg_niveles"
            )
            or 1
        )
        por_consejeria = st.slider(
            "Contratos por consejería",
            1,
            5,
            3,
            disabled=niveles == 1,
            key="mg_contratos",
            help="Cuántos de los contratos más grandes del año se dibujan junto a cada consejería.",
        )

billetes.pintar(billetes.leyenda_frascos(vista == "presupuesto" and liquidado), clave="mg_leyenda")
izquierda, derecha = st.columns([5, 2])
with izquierda:
    if ampliada is None:
        principales = _principales(anio, por_consejeria) if niveles == 2 else {}
        nodos, enlaces, destinos = grafo_general(entidades, vista, datos_anio, niveles, principales)
        st.markdown(leyenda_mapa(vista, liquidado, niveles))
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
        nodos, enlaces, destinos = grafo_ampliado(entidad_amp, cuerpo, datos_anio)
        st.markdown(
            f"Los **{len(cuerpo['contratos'])} contratos más grandes** de {anio} de {ampliada}. "
            "Cada frasco lleva los billetes que recibió de cada 100 € que adjudicó la consejería."
        )
        alto = 760
    seleccion = red.mapa(nodos, enlaces, alto=alto)
    if seleccion and seleccion in destinos:
        st.session_state["mg_sel"] = destinos[seleccion]
    if ampliada is not None:
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
    marcado = st.session_state.get("mg_sel")
    if not marcado and ampliada is not None:
        marcado = ("ent", ampliada)
    if not marcado:
        st.info(
            "Pulsa un frasco del mapa y aquí verás su ficha: cuánto dinero tiene, cuánto ha "
            "gastado y, si es un contrato, cómo se contrató y cuántas ofertas hubo.",
            icon=":material/touch_app:",
        )
    else:
        _ficha(con, marcado, entidades, datos_anio, ampliada is not None)

if liquidado:
    st.subheader("¿Cuánto ha gastado cada consejería?")
    st.html(gasto_por_consejeria(entidades))

# Fuentes, matices y datos que no tenemos, abajo del todo (D-043).
with st.expander("Fuentes y qué datos no tenemos", icon=":material/info:"):
    fuentes(datos_anio, anio, poblacion)
