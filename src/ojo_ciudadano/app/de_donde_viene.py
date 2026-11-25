"""«¿De dónde viene el dinero?» (D-054): los ingresos de la Comunidad de Madrid, al lado del mapa
de a dónde va.

Para un ciudadano cualquiera:
- una barra con «de cada 100 € que entran» (impuestos directos, indirectos, préstamos y el
  resto);
- el saldo con el sistema común de financiación, que en el presupuesto consolidado sale como
  transferencias corrientes en negativo;
- el mapa de burbujas con la misma estética que el de gastos: una burbuja por tipo de ingreso
  que, con el año cerrado, se llena hasta lo que entró respecto a lo previsto;
- lo que supone por habitante, las ayudas de la UE y las fuentes al final.

Todas las cifras salen de las series del catálogo de datos abiertos de la Comunidad
(`serie_cm`), con su enlace. No hay personas físicas (D-007).
"""

import html

import streamlit as st

from ojo_ciudadano.app import billetes, datos_contexto, red, textos
from ojo_ciudadano.app import burbujas as mapa_burbujas
from ojo_ciudadano.ingesta import ine

CENTRO = "centro"
# capítulo → (nombre corto, qué es, color en la barra)
CAPITULOS = {
    "directos": (
        "Impuestos directos",
        "Sobre todo la parte autonómica del IRPF; también los impuestos de Patrimonio y de "
        "Sucesiones y Donaciones.",
        "#3D8BFD",
    ),
    "indirectos": (
        "Impuestos indirectos",
        "La parte del IVA y de los impuestos especiales (alcohol, tabaco, hidrocarburos, "
        "electricidad) que corresponde a la Comunidad, y el impuesto de Transmisiones "
        "Patrimoniales y Actos Jurídicos Documentados.",
        "#22B5D8",
    ),
    "pasivos": (
        "Préstamos y deuda nueva",
        "Dinero que la Comunidad pide prestado en el año (emisiones de deuda y préstamos). Es "
        "una cifra bruta: la mayor parte suele servir para devolver deuda que vence ese año, así "
        "que no equivale a lo que crece la deuda.",
        "#C98500",
    ),
    "tasas": (
        "Tasas y otros ingresos",
        "Tasas, precios públicos, multas, reintegros y otros ingresos.",
        "#7E8FA8",
    ),
    "transferencias_capital": (
        "Transferencias para inversiones",
        "Dinero del Estado, de la Unión Europea y de otras administraciones destinado a "
        "inversiones.",
        "#7E8FA8",
    ),
    "transferencias_corrientes": (
        "Transferencias corrientes",
        "Dinero que la Comunidad recibe de otras administraciones para el gasto corriente, una "
        "vez restadas sus aportaciones al sistema de financiación autonómica.",
        "#7E8FA8",
    ),
    "patrimoniales": (
        "Rentas de su patrimonio",
        "Intereses, alquileres y concesiones de bienes de la Comunidad.",
        "#7E8FA8",
    ),
    "activos": (
        "Activos financieros",
        "Devolución de préstamos y anticipos que dio la Comunidad y venta de acciones.",
        "#7E8FA8",
    ),
    "enajenacion": (
        "Venta de bienes",
        "Venta de terrenos, edificios y otras inversiones.",
        "#7E8FA8",
    ),
}
# en la barra, los tres grandes por separado y el resto juntos
EN_LA_BARRA = ("directos", "indirectos", "pasivos")
COLOR_RESTO = "#7E8FA8"
COLOR_APORTA = "#B57BFF"


# ------------------------------------------------------------------------------ cuentas
def de_cada_100(valores: dict[str, float]) -> dict[str, int]:
    """Reparte 100 entre las claves según su peso, redondeando de forma que sumen 100 (el resto
    se da a las que más decimales perdieron)."""
    total = sum(v for v in valores.values() if v > 0)
    if total <= 0:
        return {k: 0 for k in valores}
    exactos = {k: 100 * max(v, 0) / total for k, v in valores.items()}
    enteros = {k: int(v) for k, v in exactos.items()}
    falta = 100 - sum(enteros.values())
    for k in sorted(exactos, key=lambda k: -(exactos[k] - enteros[k]))[:falta]:
        enteros[k] += 1
    return enteros


def entradas_y_saldo(ingresos: dict) -> tuple[dict[str, float], float]:
    """Lo que entra (capítulos en positivo) y el saldo negativo de las transferencias corrientes
    (0 si ese año es positivo: entonces cuenta como una entrada más)."""
    entradas, saldo = {}, 0.0
    for c in ingresos["capitulos"]:
        importe = c["importe"] or 0
        if importe < 0 and c["capitulo"] == "transferencias_corrientes":
            saldo += importe
        elif importe > 0:
            entradas[c["capitulo"]] = importe
    return entradas, saldo


def grupos_barra(entradas: dict[str, float]) -> dict[str, float]:
    """Los tres grandes y el resto sumado."""
    grupos = {k: entradas.get(k, 0.0) for k in EN_LA_BARRA}
    grupos["resto"] = sum(v for k, v in entradas.items() if k not in EN_LA_BARRA)
    return grupos


def nombre(clave: str) -> str:
    return "El resto" if clave == "resto" else CAPITULOS.get(clave, (clave,))[0]


def color(clave: str) -> str:
    return COLOR_RESTO if clave == "resto" else CAPITULOS.get(clave, ("", "", COLOR_RESTO))[2]


# ------------------------------------------------------------------------------ piezas
def barra_entradas(ingresos: dict, entradas: dict[str, float]) -> str:
    """La cabecera: cuánto entra, «de cada 100 €» en una frase y una barra por tramos."""
    anio, liquidado = ingresos["anio"], ingresos["liquidado"]
    grupos = grupos_barra(entradas)
    partes = de_cada_100(grupos)
    total = sum(entradas.values())
    verbo = "entraron" if liquidado else "está previsto que entren"
    trozos = [f"<b>{partes[k]}</b> {nombre(k).lower()}" for k in EN_LA_BARRA if partes[k]]
    frase = (
        f"De cada 100 € que {'entraron' if liquidado else 'entran'}: "
        + ", ".join(trozos)
        + (f" y <b>{partes['resto']}</b> de todo lo demás" if partes["resto"] else "")
        + "."
    )
    tramos = "".join(
        f'<div class="dvb-tramo" style="width:{100 * v / total:.2f}%;background:{color(k)};'
        f'--j:{j}" title="{html.escape(nombre(k))}: {textos.millones(v)}"></div>'
        for j, (k, v) in enumerate(grupos.items())
        if v > 0
    )
    leyenda = "".join(
        f'<span><i style="background:{color(k)}"></i>{html.escape(nombre(k))} '
        f"<b>{textos.millones(v)}</b></span>"
        for k, v in grupos.items()
        if v > 0
    )
    etiqueta = html.escape(frase.replace("<b>", "").replace("</b>", ""))
    return f"""
<style>
.dvb {{ font-family:Outfit, sans-serif; color:#E7ECF3; margin:6px 0 4px; }}
.dvb-cab {{ display:flex; justify-content:space-between; align-items:baseline; gap:12px;
  flex-wrap:wrap; margin-bottom:6px; }}
.dvb-cab h3 {{ margin:0; padding:0; font-size:1.35rem; font-weight:700; color:#E7ECF3; }}
.dvb-cab .total {{ font-size:1.9rem; font-weight:750; letter-spacing:-.02em;
  background:linear-gradient(180deg,#fff,#9FCBFF); -webkit-background-clip:text;
  background-clip:text; color:transparent; }}
.dvb-cab .total small {{ font-size:.85rem; font-weight:500; color:#9FB6CC;
  -webkit-text-fill-color:#9FB6CC; margin-left:6px; }}
.dvb-frase {{ font-size:1.2rem; line-height:1.5; margin:0 0 12px; color:#B9C6D8;
  font-weight:300; }}
.dvb-frase b {{ color:#fff; font-weight:650; font-size:1.35rem; }}
.dvb-barra {{ display:flex; gap:3px; height:30px; border-radius:16px; overflow:hidden;
  border:1px solid rgba(170,225,255,.3);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.16), 0 8px 24px rgba(0,8,22,.35); }}
.dvb-tramo {{ height:100%; box-shadow: inset 0 1px 0 rgba(255,255,255,.35);
  transform-origin:left center; animation: dvb-crece .9s cubic-bezier(.25,.8,.25,1) both;
  animation-delay: calc(var(--j) * 90ms); }}
@keyframes dvb-crece {{ from {{ transform:scaleX(0); opacity:0; }}
  to {{ transform:none; opacity:1; }} }}
.dvb-leyenda {{ display:flex; flex-wrap:wrap; gap:8px 22px; margin-top:10px; font-size:.95rem;
  color:#9FB6CC; }}
.dvb-leyenda b {{ color:#E7ECF3; }}
.dvb-leyenda i {{ display:inline-block; width:12px; height:12px; border-radius:4px;
  margin-right:7px; vertical-align:-1px; }}
@media (prefers-reduced-motion: reduce) {{ .dvb-tramo {{ animation:none; }} }}
</style>
<div class="dvb">
  <div class="dvb-cab"><h3>Lo que {verbo} en {anio}</h3>
    <span class="total">{textos.millones(total)}<small>en total</small></span></div>
  <p class="dvb-frase">{frase}</p>
  <div class="dvb-barra" role="img" aria-label="{etiqueta}">{tramos}</div>
  <div class="dvb-leyenda">{leyenda}</div>
</div>"""


def flujo_saldo(entradas: dict[str, float], saldo: float, liquidado: bool) -> str:
    """Entra, sale hacia el sistema común y queda para la Comunidad, en tres cifras."""
    total = sum(entradas.values())
    pasado = "entró" if liquidado else "entra"
    return f"""
<style>
.dvf {{ display:grid; grid-template-columns: 1fr auto 1fr auto 1fr; gap:14px; align-items:center;
  font-family:Outfit, sans-serif; color:#E7ECF3; padding:18px 22px; border-radius:18px;
  background:rgba(255,255,255,.045); border:1px solid rgba(170,225,255,.16);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.08); }}
.dvf div {{ display:flex; flex-direction:column; gap:4px; }}
.dvf span {{ font-size:.9rem; color:#9FB6CC; line-height:1.35; }}
.dvf b {{ font-size:1.6rem; font-weight:700; letter-spacing:-.01em; }}
.dvf .menos b {{ color:{COLOR_APORTA}; }}
.dvf .flecha {{ font-size:1.6rem; color:#7DB3FF; }}
@media (max-width: 760px) {{ .dvf {{ grid-template-columns: 1fr; }}
  .dvf .flecha {{ display:none; }} }}
</style>
<div class="dvf">
  <div><span>Lo que {pasado}</span><b>{textos.millones(total)}</b></div>
  <p class="flecha">&minus;</p>
  <div class="menos"><span>Saldo neto de transferencias corrientes (sistema de financiación y
    otras administraciones)</span><b>{textos.millones(-saldo)}</b></div>
  <p class="flecha">=</p>
  <div><span>Ingresos netos de la Comunidad</span><b>{textos.millones(total + saldo)}</b></div>
</div>"""


def grafo(ingresos: dict, entradas: dict[str, float]):
    """Nodos y enlaces: la Comunidad en el centro y una burbuja por tipo de ingreso."""
    total = sum(entradas.values())
    previstos = {c["capitulo"]: c["previsto"] for c in ingresos["capitulos"]}
    nodos = [
        red.NodoRed(
            id=CENTRO,
            etiqueta="Entra en la\nComunidad",
            importe=total,
            centro=True,
            detalle="Todo lo que entra",
            x=0,
            y=0,
        )
    ]
    enlaces = []
    orden = red.alternar_tamanos(sorted(entradas.items(), key=lambda kv: -kv[1]))
    for (clave, importe), (x, y) in zip(
        orden, red.posiciones_radiales(len(orden), 280), strict=True
    ):
        previsto = previstos.get(clave)
        llenado = min(importe / previsto, 1.0) if ingresos["liquidado"] and previsto else None
        nodos.append(
            red.NodoRed(
                id=clave,
                etiqueta=red.envolver(nombre(clave), 16) + "\n" + textos.millones(importe),
                importe=importe,
                llenado=llenado,
                titulo=nombre(clave),
                x=x,
                y=y * 1.1,
                extra=(
                    {
                        "linea_llenado": "Entró el "
                        + textos.porcentaje(importe / previsto)
                        + " de lo previsto"
                    }
                    if llenado is not None
                    else {}
                ),
            )
        )
        enlaces.append((CENTRO, clave, 280))
    return nodos, enlaces


def ficha(clave: str, ingresos: dict, entradas: dict[str, float], habitantes: int | None) -> None:
    """Ficha de la burbuja pulsada: qué es, cuánto y, con el año cerrado, frente a lo previsto."""
    if clave == CENTRO:
        st.subheader("Todo lo que entra")
        st.markdown(
            "La suma de todos los ingresos del año antes de restar el saldo neto de "
            "transferencias corrientes. Pulsa una burbuja para ver cada tipo de ingreso."
        )
        return
    nombre_c, que_es, _ = CAPITULOS[clave]
    importe = entradas[clave]
    st.subheader(nombre_c)
    st.markdown(que_es)
    partes = de_cada_100(entradas)
    k = st.columns(2)
    k[0].metric("Entró" if ingresos["liquidado"] else "Previsto", textos.millones(importe))
    k[1].metric("De cada 100 € que entran", f"{partes[clave]} €")
    fila = next((c for c in ingresos["capitulos"] if c["capitulo"] == clave), None)
    if ingresos["liquidado"] and fila and fila["previsto"]:
        k = st.columns(2)
        k[0].metric("Se preveía", textos.millones(fila["previsto"]))
        k[1].metric(
            "Frente a lo previsto",
            textos.porcentaje(importe / fila["previsto"]),
            help="Derechos reconocidos (lo que la Comunidad tiene derecho a cobrar, aunque parte "
            "no se haya cobrado aún) sobre la previsión actual. Más del 100 % es que se reconoció "
            "más de lo previsto.",
        )
    if habitantes:
        st.caption(
            f"Unos {textos.numero(round(importe / habitantes))} € por habitante en el año "
            "(una forma de dar escala, no lo que paga cada persona)."
        )


def sistema_comun(sistema: dict | None, anio: int) -> None:
    """El sistema de financiación autonómica, en una explicación neutra con sus cifras (revisada
    por `revisor-legal`)."""
    st.markdown(
        "Por ley (Ley 22/2009), el Estado cede a las comunidades de régimen común el 50 % del "
        "IRPF y del IVA, el 58 % de los impuestos especiales sobre alcohol, tabaco e "
        "hidrocarburos y el 100 % del de electricidad, además de tributos como Patrimonio, "
        "Sucesiones y Donaciones o Transmisiones Patrimoniales. El IVA y los impuestos "
        "especiales se asignan según el consumo estimado en cada comunidad.\n\n"
        "Cada comunidad aporta el 75 % de su capacidad tributaria al **Fondo de Garantía de "
        "Servicios Públicos Fundamentales**, al que el Estado añade su parte, y el fondo se "
        "reparte según la población ajustada de cada comunidad (corregida por edad, superficie, "
        "dispersión e insularidad) para sanidad, educación y servicios sociales. Si una "
        "comunidad aporta más de lo que recibe, su saldo es negativo. El **Fondo de Suficiencia "
        "Global** ajusta cada año los recursos de cada comunidad con sus competencias y puede "
        "ser positivo (lo paga el Estado) o negativo (lo paga la comunidad al Estado).\n\n"
        "En el presupuesto consolidado estos saldos se restan dentro de las transferencias "
        "corrientes; por eso ese capítulo sale en negativo. País Vasco y Navarra tienen un "
        "sistema propio (concierto y convenio)."
    )
    if not sistema:
        return
    lineas = [
        f"- **Fondo de Garantía de Servicios Públicos Fundamentales:** saldo de "
        f"{textos.millones(sistema['garantia'])}"
        + (
            " (negativo: la Comunidad aporta al fondo más de lo que recibe de él)."
            if sistema["garantia"] < 0
            else "."
        ),
    ]
    if sistema["suficiencia"] is not None:
        lineas.append(
            f"- **Fondo de Suficiencia Global:** saldo de "
            f"{textos.millones(sistema['suficiencia'])}"
            + (
                " (negativo: la Comunidad lo abona al Estado)."
                if sistema["suficiencia"] < 0
                else "."
            )
        )
    if sistema["irpf"] and sistema["iva"]:
        lineas.append(
            f"- **Lo que la Comunidad recibe del IRPF y del IVA** por el sistema: "
            f"{textos.millones(sistema['irpf'])} y {textos.millones(sistema['iva'])}."
        )
    aviso = (
        f"; el saldo de arriba es de {anio} y no es directamente comparable, porque las "
        "transferencias corrientes incluyen también otras transferencias del Estado y de la "
        "Unión Europea"
        if sistema["anio"] != anio
        else ""
    )
    st.markdown(
        f"Según la serie del sistema de financiación ({sistema['anio']}, el último año "
        f"publicado{aviso}):\n\n" + "\n".join(lineas)
    )
    st.caption(
        f"Fuente: [sistema de financiación, datos abiertos de la Comunidad de Madrid]"
        f"({sistema['url_origen']}), descargado el {sistema['fecha_descarga']}."
    )


def fuentes(ingresos: dict, sistema, ue, poblacion, anio: int) -> None:
    lineas = [
        f"- **Ingresos por capítulo:** [datos abiertos de la Comunidad de Madrid]"
        f"({ingresos['url_origen']}), descargado el {ingresos['fecha_descarga']}. "
        + (
            "Con el año cerrado, «entró» son los **derechos reconocidos** (como «gastado» son "
            "las obligaciones reconocidas) y «se preveía» es la previsión actual."
            if ingresos["liquidado"]
            else "Son los **presupuestos iniciales**: lo que se prevé ingresar, no lo cobrado."
        )
        + " Cifras consolidadas: sin contar el dinero que se pasan entre sí los organismos de "
        "la Comunidad.",
    ]
    if sistema:
        lineas.append(
            f"- **Sistema de financiación autonómica:** [datos abiertos de la Comunidad]"
            f"({sistema['url_origen']}), año {sistema['anio']}, descargado el "
            f"{sistema['fecha_descarga']}."
        )
    if ue:
        lineas.append(
            f"- **Ayudas de la Unión Europea:** [datos abiertos de la Comunidad]"
            f"({ue['url_origen']}), año {ue['anio']}, descargado el {ue['fecha_descarga']}."
        )
    referencia = ine.del_anio(poblacion, anio) if poblacion else None
    if referencia:
        lineas.append(
            f"- **Habitantes:** [Estadística Continua de Población del INE]"
            f"({poblacion['url_origen']}), a 1 de enero de {referencia[0]}, descargado el "
            f"{poblacion['fecha_descarga']}. El reparto por "
            "habitante es una forma de dar escala, no lo que paga cada persona."
        )
    st.markdown("**Fuentes**\n\n" + "\n".join(lineas))
    st.markdown(
        "**Qué datos no tenemos**\n\n"
        "- **Qué ingreso paga cada gasto:** el dinero entra en una caja común; no se puede "
        "seguir un euro de un impuesto a un contrato.\n"
        "- **El detalle de cada impuesto del año en curso:** la serie del sistema de "
        "financiación se publica con unos años de retraso.\n"
        "- **Ingresos y gastos:** en el presupuesto inicial cuadran porque los préstamos ya "
        "cuentan como ingreso. Con el año cerrado, la diferencia entre derechos y obligaciones "
        "reconocidos es el resultado presupuestario, que no mostramos aquí."
    )


# ------------------------------------------------------------------------------ pantalla
def pintar(con, anio: int, poblacion: dict | None) -> None:
    ingresos = datos_contexto.ingresos_del_anio(con, anio)
    if not ingresos["capitulos"]:
        st.info(f"No tenemos los ingresos de {anio}. Prueba con otro año.", icon=":material/info:")
        return
    entradas, saldo = entradas_y_saldo(ingresos)
    referencia = ine.del_anio(poblacion, anio) if poblacion else None
    habitantes = referencia[1] if referencia else None

    billetes.pintar(barra_entradas(ingresos, entradas), clave=f"dv_barra_{anio}")
    if saldo < 0:
        st.html(flujo_saldo(entradas, saldo, ingresos["liquidado"]))
    st.caption(
        "Fuente: [ingresos consolidados por capítulo, datos abiertos de la Comunidad de Madrid]"
        f"({ingresos['url_origen']}), "
        + ("derechos reconocidos" if ingresos["liquidado"] else "presupuesto inicial")
        + f" de {anio}, descargado el {ingresos['fecha_descarga']}."
    )

    st.subheader("Cada tipo de ingreso, en una burbuja")
    izquierda, derecha = st.columns([5, 2])
    with izquierda:
        st.markdown(
            "Cuanto **más grande y más clara**, más dinero. "
            + (
                "Cada burbuja **se llena hasta lo que entró** frente a lo que se preveía. "
                if ingresos["liquidado"]
                else "Este año es presupuesto inicial: aún no se sabe lo que entrará. "
            )
            + "Pulsa una para ver qué es."
        )
        nodos, enlaces = grafo(ingresos, entradas)
        pulsada = mapa_burbujas.mapa(
            nodos,
            enlaces,
            720,
            clave=f"dv_burbujas_{anio}",
            seleccionado=st.session_state.get("dv_sel"),
        )
        if pulsada:
            st.session_state["dv_sel"] = pulsada
    with derecha:
        st.html('<span class="oc-ficha-mapa"></span>')  # misma columna de ficha que el mapa
        elegida = st.session_state.get("dv_sel")
        if elegida in entradas or elegida == CENTRO:
            ficha(elegida, ingresos, entradas, habitantes)
        else:
            st.info(
                "Pulsa una burbuja del mapa y aquí verás qué es ese ingreso, cuánto entró y "
                "cuánto supone de cada 100 €.",
                icon=":material/touch_app:",
            )

    if saldo < 0:
        st.subheader("El saldo de la Comunidad con el sistema de financiación autonómica")
        sistema_comun(datos_contexto.sistema_financiacion(con, anio), anio)

    impuestos = entradas.get("directos", 0) + entradas.get("indirectos", 0)
    ue = datos_contexto.ayudas_ue(con, anio)
    datos_extra = []
    if habitantes and impuestos:
        datos_extra.append(
            "**Impuestos divididos entre habitantes:** unos "
            f"{textos.numero(round(impuestos / habitantes))} € en {anio} (directos e indirectos) "
            f"si se repartieran entre los {textos.numero(habitantes)} de habitantes. Sirve para "
            "dar escala: no es lo que paga cada persona, porque también pagan empresas y "
            "personas no residentes."
        )
    if ue:
        datos_extra.append(
            f"**Ayudas de la Unión Europea:** {textos.millones(ue['total'])} en {ue['anio']}"
            + (
                f", la mayor parte del Fondo Social Europeo ({textos.millones(ue['fse'])})"
                if ue["fse"] and ue["fse"] > ue["total"] / 2
                else ""
            )
            + (
                f": menos de 1 € de cada 100 que entraron en {anio}."
                if ue["anio"] == anio and ue["total"] < sum(entradas.values()) / 100
                else "."
            )
        )
    if datos_extra:
        st.subheader("Para hacerse una idea")
        st.markdown("\n\n".join(datos_extra))

    with st.expander("Fuentes y qué datos no tenemos", icon=":material/info:"):
        fuentes(ingresos, datos_contexto.sistema_financiacion(con, anio), ue, poblacion, anio)
