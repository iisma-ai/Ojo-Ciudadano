"""Asistente: una sola pantalla para preguntar en lenguaje natural (D-037, docs/05-asistente.md).

Cada pregunta se intenta primero con las respuestas preparadas (consulta SQL revisada por el
equipo y texto escrito de antemano, sin modelo de lenguaje). Si no hay una que encaje, contesta
el modelo elegido (D-010) con sus herramientas: SQL sobre la base, catálogo de datos abiertos,
pliegos y resoluciones del Tribunal. Mientras se consulta se anima lo que se está haciendo
(las tablas y sus uniones, o los documentos que se leen); el proceso de cada consulta se queda
en la respuesta, seguido del texto, que aparece como si se escribiera, y de lo que sacan las
consultas (gráfico y tabla con el enlace a la fuente). El SQL no se muestra. Si la respuesta no
necesita datos, solo se escribe el texto.
"""

import time

import streamlit as st

from ojo_ciudadano.app import animacion, graficos, limite_modelo, textos
from ojo_ciudadano.app.conexion import conexion
from ojo_ciudadano.app.tablas import mostrar_resultado
from ojo_ciudadano.asistente import agente, bateria, catalogo, plano, respuestas_fijas

# Qué se muestra en lugar de una respuesta retenida (agente.RETENCION_*).
RETENIDAS = {
    agente.RETENCION_DNI: (
        "Esta respuesta no se muestra porque podía contener datos de personas físicas, que la "
        "plataforma no publica (RGPD). Puedes preguntar por datos agregados."
    ),
    agente.RETENCION_LENGUAJE: (
        "Esta respuesta se ha retenido porque usaba expresiones que la plataforma no emplea. "
        "Ojo Ciudadano solo muestra indicadores de riesgo: señalan contratos que merecen "
        "revisión y no prueban ninguna irregularidad. Prueba a reformular la pregunta."
    ),
    agente.RETENCION_CIFRAS: (
        "Esta respuesta se ha retenido porque daba cifras sin haberlas consultado en la base. "
        "Prueba a reformular la pregunta."
    ),
}

SIN_MODELO = (
    "No tengo una respuesta preparada para esta pregunta y el modelo de lenguaje no está "
    "conectado ahora mismo. Prueba con una de las preguntas con respuesta preparada de la lista "
    "de arriba, o reformula la pregunta con otras palabras."
)

MODELO_CAIDO = (
    "No tengo una respuesta preparada para esta pregunta y el modelo de lenguaje no responde "
    "ahora mismo. Vuelve a intentarlo en unos minutos o elige una de las preguntas con "
    "respuesta preparada."
)


def texto_visible(respuesta: agente.Respuesta) -> str:
    """Lo que ve la persona (y lo que vuelve al modelo en el historial)."""
    return RETENIDAS.get(respuesta.retencion, respuesta.texto)


def mostrar_conjunto(consulta: dict) -> None:
    """Una consulta al catálogo de datos abiertos (D-030): el conjunto, su enlace, su fecha y
    los datos que salen."""
    st.markdown(
        f"**[{consulta['titulo_conjunto']}]({consulta['url_origen']})** · "
        f"{catalogo.NOMBRE_FUENTE} (licencia CC BY) · actualizado el "
        f"{consulta['actualizado']} · datos descargados el {consulta['fecha_descarga']}"
    )
    if consulta.get("municipal"):
        st.caption(
            "Son datos de municipios: la plataforma trata la Comunidad de Madrid, no los "
            "ayuntamientos."
        )
    st.dataframe(
        {c: [f[i] for f in consulta["filas"]] for i, c in enumerate(consulta["columnas"])},
        hide_index=True,
    )


def mostrar_busqueda(consulta: dict) -> None:
    """Una búsqueda por palabras en los títulos: el resumen por fuente y los ejemplos."""
    resumen = consulta["resumen"]
    st.markdown(f"**Búsqueda «{consulta['busqueda']}» en los títulos**")
    st.dataframe(
        {c: [f[i] for f in resumen["filas"]] for i, c in enumerate(resumen["columnas"])},
        hide_index=True,
    )
    st.caption(
        "Cuenta los títulos que contienen esas palabras: puede haber otros del mismo tema "
        "con otro título. Debajo, los más parecidos a la búsqueda con su enlace oficial. La "
        "relevancia solo mide el parecido del título con la búsqueda: no es un indicador de "
        "riesgo. Los títulos de contratos o convenios con personas físicas no se muestran."
    )
    mostrar_resultado(consulta)


def mostrar_documento(consulta: dict) -> None:
    """Una búsqueda en pliegos o resoluciones del Tribunal (D-030, bloques B y C): cada página
    encontrada con su extracto y el enlace al PDF oficial en esa página."""
    if consulta["documento"] == "resoluciones":
        titulo = f"Resoluciones del Tribunal · «{consulta['consulta_documento']}»"
    else:
        titulo = f"Documentos de {consulta['documento']} · «{consulta['consulta_documento']}»"
    with st.expander(titulo, expanded=True):
        columnas = consulta["columnas"]
        if not consulta["filas"]:
            st.caption("Ninguna página contiene esas palabras.")
        for fila in consulta["filas"]:
            f = dict(zip(columnas, fila, strict=True))
            if "resolucion" in f:
                cabecera = (
                    f"**Resolución {f['resolucion']}** ({f['fecha']}) · {f['tipo_resolucion']} · "
                    f"acto recurrido: {f['acto_recurrido']} · pág. {f['pagina']} · "
                    f"[ficha de la resolución]({f['url_origen']})"
                )
            else:
                cabecera = f"**{f['documento']}** · pág. {f['pagina']}"
            st.markdown(cabecera)
            st.text(f["extracto"])
            st.link_button(
                "Abrir el PDF oficial en esta página",
                f["enlace_pagina"],
                icon=":material/open_in_new:",
            )
        st.caption(
            f"Fuente: {consulta['fuente']}, documento descargado el "
            f"{consulta.get('fecha_descarga') or 'sin fecha'}. El extracto es texto literal del "
            "documento oficial, con los nombres de personas y los documentos de identidad "
            "tapados (si ves alguno sin tapar, el documento completo está en el enlace oficial y "
            "aquí no debería aparecer). Las expresiones del extracto son del Tribunal o del "
            "órgano de contratación, no de Ojo Ciudadano, y se refieren solo al acto que se "
            "resolvió. Lo que dice un pliego da contexto al expediente; no confirma ni descarta "
            "una señal. Que el Tribunal estime un recurso especial no es una sanción ni implica "
            "una conducta reprochable de la empresa adjudicataria."
        )
        for fallo in consulta.get("fallos") or []:
            st.caption(f"No se ha podido leer: {fallo}")


def es_sql(consulta: dict) -> bool:
    """Una consulta SQL a la base (no catálogo, búsqueda en títulos ni documentos)."""
    return not (consulta.get("conjunto") or consulta.get("busqueda") or consulta.get("documento"))


def plano_de(consulta: dict) -> plano.Plano:
    """El plano de la consulta, calculado una vez y guardado con ella."""
    if "plano" not in consulta:
        consulta["plano"] = plano.plano_consulta(conexion(), consulta["sql"])
    return consulta["plano"]


def aviso_sin_fuente(numero: int, consulta: dict) -> None:
    """Regla 5 de CLAUDE.md: una cifra sin su origen no se puede comprobar desde aquí."""
    columnas = consulta["columnas"]
    sin_fuente = "fuente" not in columnas or "fecha_descarga" not in columnas
    sin_enlace = "contrato_id" in columnas and "url_origen" not in columnas
    if sin_fuente or sin_enlace:
        st.warning(
            f"Las cifras de la consulta {numero} no llevan "
            + ("su fuente y su fecha de descarga" if sin_fuente else "")
            + (" ni " if sin_fuente and sin_enlace else "")
            + ("el enlace oficial de cada contrato" if sin_enlace else "")
            + ", así que no se pueden comprobar desde aquí. Tómalas como orientativas o "
            "repite la pregunta pidiendo la fuente y el enlace oficial.",
            icon=":material/warning:",
        )


def mostrar_salida(respuesta: agente.Respuesta, clave: str) -> None:
    """Lo que sacan las consultas: gráfico y tabla de la primera consulta SQL, y los datos de
    las demás (catálogo, títulos, documentos u otras consultas)."""
    sql = [c for c in respuesta.consultas if es_sql(c)]
    for numero, consulta in enumerate(sql, start=1):
        if not respuesta.preparada:
            aviso_sin_fuente(numero, consulta)
        if numero == 1:
            figura, _ = graficos.automatico(consulta)
            if figura is not None:
                st.plotly_chart(figura, config=graficos.CONFIG, key=f"grafico-{clave}")
            mostrar_resultado(consulta)
        else:
            filas = len(consulta["filas"])
            with st.expander(f"Datos de la consulta {numero} ({filas} filas)"):
                mostrar_resultado(consulta)
    for consulta in respuesta.consultas:
        if consulta.get("conjunto"):
            mostrar_conjunto(consulta)
        elif consulta.get("busqueda"):
            mostrar_busqueda(consulta)
        elif consulta.get("documento"):
            mostrar_documento(consulta)


def mostrar_respuesta(
    pregunta: str, respuesta: agente.Respuesta, clave: str, nueva: bool = False
) -> None:
    """Proceso de la consulta, texto y salida. `nueva`: la respuesta se acaba de calcular, así
    que el texto se escribe y, en una preparada, el proceso se anima (en la del modelo ya se
    vio mientras trabajaba)."""
    if respuesta.retencion:
        st.warning(texto_visible(respuesta))
        return
    sql = [c for c in respuesta.consultas if es_sql(c)]
    animar = nueva and bool(respuesta.preparada)
    for consulta in sql:
        st.html(animacion.consulta(plano_de(consulta), len(consulta["filas"]), animar=animar))
    if animar and sql:
        time.sleep(min(2.4, max(animacion.duracion(plano_de(c)) for c in sql)))
    if nueva:
        st.write_stream(animacion.escribir(textos.sin_codigos(respuesta.texto)))
    else:
        st.markdown(textos.sin_codigos(respuesta.texto))
    mostrar_salida(respuesta, clave)
    if respuesta.preparada:
        interpretado = "; ".join(f"{k}: {v}" for k, v in respuesta.interpretacion.items())
        st.caption(
            "Respuesta preparada"
            + (" con una consulta comprobada de antemano" if respuesta.consultas else "")
            + f", sin modelo de lenguaje, para la pregunta «{respuesta.pregunta_preparada}»"
            + (f" ({interpretado})" if interpretado else "")
            + "."
        )
        if modelo is not None and st.button(
            "No es lo que preguntaba: que responda el modelo",
            key=f"al-modelo-{clave}",
            icon=":material/smart_toy:",
        ):
            st.session_state["pregunta_asistente"] = pregunta
            st.session_state["forzar_modelo"] = True
            st.rerun()
    if respuesta.consultas:
        st.caption(textos.AVISO_CORTO)


@st.cache_data(ttl=3600, max_entries=500, show_spinner=False)
def resultado_preparado(id_: str, parametros: tuple) -> dict | None:
    """El resultado de una consulta preparada (la base no cambia con la web abierta)."""
    fija = next(f for f in respuestas_fijas.FIJAS if f.id == id_)
    coincidencia = respuestas_fijas.Coincidencia(fija, dict(parametros))
    return respuestas_fijas.ejecutar(conexion(), coincidencia)


def preparada(pregunta: str) -> agente.Respuesta | None:
    """La respuesta preparada, o None si no hay ninguna que encaje."""
    coincidencia = respuestas_fijas.reconocer(conexion(), pregunta)
    if coincidencia is None:
        return None
    fija = coincidencia.fija
    resultado = None
    if fija.sql:
        resultado = resultado_preparado(fija.id, tuple(sorted(coincidencia.parametros.items())))
    pregunta_preparada, interpretacion = fija.pregunta, dict(coincidencia.descripcion)
    if fija.anio and str(fija.anio) in fija.pregunta:  # «… en 2025» con el año pedido
        pregunta_preparada = fija.pregunta.replace(str(fija.anio), str(interpretacion.pop("año")))
    return agente.Respuesta(
        texto=respuestas_fijas.redactar(coincidencia, resultado),
        consultas=[resultado] if resultado and resultado["filas"] else [],
        preparada=fija.id,
        pregunta_preparada=pregunta_preparada,
        interpretacion=interpretacion,
    )


def del_modelo(pregunta: str, historial: list[dict]) -> agente.Respuesta:
    """La respuesta del modelo, animando cada herramienta mientras la usa."""
    con = conexion()
    zona = st.empty()
    zona.html(animacion.pensando())

    def al_usar(llamada) -> None:
        zona.html(animacion.de_llamada(con, llamada))

    try:
        respuesta = agente.responder(con, modelo, pregunta, historial, al_usar=al_usar)
    except Exception:  # red, saldo o proveedor caído: no enseñar la traza
        respuesta = agente.Respuesta(MODELO_CAIDO)
    zona.empty()
    return respuesta


def contestar(pregunta: str, historial: list[dict], forzar_modelo: bool) -> agente.Respuesta:
    if bateria.PATRON_DNI.search(pregunta):  # no se busca ni llega al modelo
        return agente.Respuesta(agente.PREGUNTA_CON_DNI)
    if not forzar_modelo:
        respuesta = preparada(pregunta)
        if respuesta is not None:
            return respuesta
    if modelo is None:
        return agente.Respuesta(SIN_MODELO)
    # Solo cuentan las preguntas que llegan al modelo (D-057): 2 seguidas y 5 minutos de espera.
    espera = limite_modelo.limitador().intentar(limite_modelo.identidad())
    if espera:
        return agente.Respuesta(limite_modelo.mensaje(espera))
    return del_modelo(pregunta, historial)


# --- Pantalla ---

st.html(animacion.CSS)  # una vez por página, para todas las animaciones
st.header("Asistente")
st.caption(
    "Pregunta en tus palabras sobre los contratos y las subvenciones de la Comunidad de Madrid, "
    "sobre los datos de su catálogo de datos abiertos (sanidad, educación, presupuestos…), sobre "
    "lo que dicen los pliegos de una licitación o sobre las resoluciones del Tribunal "
    "Administrativo de Contratación Pública. Las preguntas frecuentes tienen una respuesta "
    "preparada con una consulta comprobada de antemano; las demás las redacta un modelo de "
    "lenguaje, que "
    "puede equivocarse: comprueba siempre los datos y el enlace oficial que se "
    "muestran con cada respuesta. No escribas datos personales en tus preguntas."
)

modelo = agente.modelo_configurado()
if modelo is None:
    st.info(
        "El modelo de lenguaje no está conectado: ahora solo se contestan las preguntas con "
        "respuesta preparada.",
        icon=":material/info:",
    )

turnos = st.session_state.setdefault("turnos_asistente", [])
elegida = None

with st.expander("Preguntas con respuesta preparada", icon=":material/quiz:"):
    grupos: dict[str, list] = {}
    for fija in respuestas_fijas.FIJAS:
        grupos.setdefault(fija.grupo, []).append(fija)
    for grupo in (
        "Datos",
        "Empresas",
        "Señales",
        "Subvenciones",
        "Tribunal",
        "Conceptos",
        "Límites",
    ):
        if grupo not in grupos:
            continue
        st.markdown(f"**{grupo}**")
        for fija in grupos[grupo]:
            if "empresa" in fija.parametros:
                continue  # necesita el nombre de una empresa: va como pista, abajo
            if st.button(fija.pregunta, key=f"fija-{fija.id}", type="tertiary"):
                elegida = fija.pregunta
    st.caption(
        "Para una empresa o entidad, escribe «¿Qué ha recibido …?» con su nombre o su NIF. "
        "Se pueden preguntar con otras palabras, y con otro año, consejería o empresa. Las "
        "demás preguntas (por ejemplo, sobre un pliego concreto o el catálogo de datos "
        "abiertos) las contesta el modelo."
    )

if not turnos:
    st.markdown("**Prueba con una de estas preguntas**")
    columnas = st.columns(3)
    for n, fija in enumerate(respuestas_fijas.sugerencias()):
        if columnas[n % 3].button(fija.pregunta, key=f"sugerencia-{fija.id}", width="stretch"):
            elegida = fija.pregunta

for n, (anterior, respuesta) in enumerate(turnos):
    st.chat_message("user").write(anterior)
    with st.chat_message("assistant"):
        mostrar_respuesta(anterior, respuesta, clave=str(n))  # quieta: sin animar ni escribir

# Una pregunta que llega escrita desde otra pantalla («¿Qué dice el pliego?») o desde el botón
# «que responda el modelo».
pendiente = st.session_state.pop("pregunta_asistente", None)
forzar = st.session_state.pop("forzar_modelo", False)
if pregunta := st.chat_input("Escribe tu pregunta") or elegida or pendiente:
    st.chat_message("user").write(pregunta)
    historial = []
    for anterior, respuesta in turnos:
        historial += [
            {"rol": "usuario", "contenido": anterior},
            {"rol": "modelo", "contenido": texto_visible(respuesta)},
        ]
    with st.chat_message("assistant"):
        respuesta = contestar(pregunta, historial, forzar_modelo=forzar and not elegida)
        mostrar_respuesta(pregunta, respuesta, clave=str(len(turnos)), nueva=True)
    turnos.append((pregunta, respuesta))

# Las fuentes van en el pie de la página (D-043, main.pie).
