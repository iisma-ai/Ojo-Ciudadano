"""«¿De dónde viene el dinero?» (D-054): los ingresos de la Comunidad de Madrid, al lado del mapa
de a dónde va.

Para un ciudadano cualquiera:
- el mapa de burbujas con la misma estética que el de gastos: una burbuja por tipo de ingreso
  que, con el año cerrado, se llena hasta lo que entró respecto a lo previsto;
- al lado, una caja de información con el saldo con el sistema común de financiación, que en
  el presupuesto consolidado sale como transferencias corrientes en negativo (D-064);
- lo que supone por habitante, las ayudas de la UE y las fuentes al final.

Todas las cifras salen de las series del catálogo de datos abiertos de la Comunidad
(`serie_cm`), con su enlace. No hay personas físicas (D-007).
"""

import streamlit as st

from ojo_ciudadano.app import burbujas as mapa_burbujas
from ojo_ciudadano.app import datos_contexto, red, textos
from ojo_ciudadano.ingesta import ine

CENTRO = "centro"
# capítulo → (nombre corto, qué es, color)
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


def nombre(clave: str) -> str:
    return CAPITULOS.get(clave, (clave,))[0]


# ------------------------------------------------------------------------------ piezas
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


EXPLICACION_SISTEMA = (
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


def resumen_saldo(entradas: dict[str, float], saldo: float, liquidado: bool) -> str:
    """La caja de información en tres líneas: lo que entra, el saldo que se resta y lo que queda."""
    total = sum(entradas.values())
    return (
        "**El saldo con el sistema de financiación autonómica**\n\n"
        f"De los {textos.millones(total)} que {'entraron' if liquidado else 'entran'}, se restan "
        f"**{textos.millones(-saldo)}** de saldo neto de transferencias corrientes (sistema de "
        "financiación y otras administraciones). A la Comunidad le quedan "
        f"**{textos.millones(total + saldo)}**."
    )


def lineas_sistema(sistema: dict) -> list[str]:
    """Los saldos de los dos fondos y lo recibido del IRPF y del IVA, del último año publicado."""
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
    return lineas


def caja_sistema(
    entradas: dict[str, float], saldo: float, ingresos: dict, sistema: dict | None
) -> None:
    """Caja de información junto a las burbujas; la explicación completa, en un desplegable
    (texto revisado por `revisor-legal`)."""
    anio = ingresos["anio"]
    st.info(resumen_saldo(entradas, saldo, ingresos["liquidado"]), icon=":material/info:")
    with st.popover("Cómo funciona el sistema", icon=":material/account_balance:"):
        st.markdown(EXPLICACION_SISTEMA)
        if sistema:
            aviso = (
                f"; el saldo de la caja es de {anio} y no es directamente comparable, porque "
                "las transferencias corrientes incluyen también otras transferencias del Estado "
                "y de la Unión Europea"
                if sistema["anio"] != anio
                else ""
            )
            st.markdown(
                f"Según la serie del sistema de financiación ({sistema['anio']}, el último año "
                f"publicado{aviso}):\n\n" + "\n".join(lineas_sistema(sistema))
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

    st.subheader(f"Lo que {'entró' if ingresos['liquidado'] else 'entra'} en {anio}")
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
        st.caption(
            "Fuente: [ingresos consolidados por capítulo, datos abiertos de la Comunidad de "
            f"Madrid]({ingresos['url_origen']}), "
            + ("derechos reconocidos" if ingresos["liquidado"] else "presupuesto inicial")
            + f" de {anio}, descargado el {ingresos['fecha_descarga']}."
        )
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
            caja_sistema(entradas, saldo, ingresos, datos_contexto.sistema_financiacion(con, anio))

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
