"""Asistente: una sola pantalla para preguntar en lenguaje natural (D-037, docs/05-asistente.md).

Cada pregunta se intenta primero con las respuestas preparadas (consulta SQL revisada por el
equipo y texto escrito de antemano, sin modelo de lenguaje). Si no hay una que encaje, contesta
el modelo elegido (D-010) con sus herramientas: SQL sobre la base, catálogo de datos abiertos,
pliegos y resoluciones del Tribunal. Mientras se consulta se anima lo que se está haciendo
(las tablas y sus uniones, o los documentos que se leen) y la respuesta aparece como si se
escribiera. Si la respuesta no necesita datos, solo se escribe el texto. Cada respuesta con
datos enseña la consulta, los resultados y el enlace a la fuente.
"""

import time

import streamlit as st

from ojo_ciudadano.app import animacion, graficos, textos
from ojo_ciudadano.app.conexion import conexion
from ojo_ciudadano.app.tablas import mostrar_resultado
from ojo_ciudadano.asistente import agente, bateria, catalogo, plano, respuestas_fijas

SEGUNDOS_ANIMACION = 1.8  # lo mínimo que se ve la animación de una consulta preparada

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


def mostrar_conjunto(numero: int, consulta: dict) -> None:
    """Una consulta al catálogo de datos abiertos (D-030): el conjunto, su enlace y su fecha."""
    with st.expander(f"Datos de la consulta {numero} · catálogo de datos abiertos"):
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
        st.code(consulta["sql"].strip(), language="sql")


def mostrar_busqueda(numero: int, consulta: dict) -> None:
    """Una búsqueda por palabras en los títulos: el resumen por fuente y los ejemplos."""
    with st.expander(f"Datos de la consulta {numero} · búsqueda «{consulta['busqueda']}»"):
        resumen = consulta["resumen"]
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
        st.code(consulta["sql"].strip(), language="sql")


def mostrar_documento(numero: int, consulta: dict) -> None:
    """Una búsqueda en pliegos o resoluciones del Tribunal (D-030, bloques B y C): cada página
    encontrada con su extracto y el enlace al PDF oficial en esa página."""
    if consulta["documento"] == "resoluciones":
        titulo = f"resoluciones del Tribunal · «{consulta['consulta_documento']}»"
    else:
        titulo = f"documentos de {consulta['documento']} · «{consulta['consulta_documento']}»"
    with st.expander(f"Datos de la consulta {numero} · {titulo}"):
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
            "una señal. Que el Tribunal estime un recurso no es una sanción ni dice nada de la "
            "empresa adjudicataria."
        )
        for fallo in consulta.get("fallos") or []:
            st.caption(f"No se ha podido leer: {fallo}")


def mostrar_datos(respuesta: agente.Respuesta, clave: str) -> None:  # noqa: C901
    """Gráfico de la primera consulta que se pueda dibujar y los datos de cada consulta."""
    for numero, consulta in enumerate(respuesta.consultas, start=1):
        if consulta.get("documento"):
            continue  # extractos de texto: nada que dibujar
        figura, _ = graficos.automatico(consulta)
        if figura is not None:
            st.plotly_chart(figura, config=graficos.CONFIG, key=f"grafico-{clave}-{numero}")
            break
    for numero, consulta in enumerate(respuesta.consultas, start=1):
        if consulta.get("conjunto"):
            mostrar_conjunto(numero, consulta)
            continue
        if consulta.get("busqueda"):
            mostrar_busqueda(numero, consulta)
            continue
        if consulta.get("documento"):
            mostrar_documento(numero, consulta)
            continue
        columnas = consulta["columnas"]
        sin_fuente = "fuente" not in columnas or "fecha_descarga" not in columnas
        sin_enlace = "contrato_id" in columnas and "url_origen" not in columnas
        if (sin_fuente or sin_enlace) and not respuesta.preparada:  # las preparadas la citan
            # Regla 5 de CLAUDE.md: una cifra sin su origen no se puede comprobar desde aquí.
            st.warning(
                f"Las cifras de la consulta {numero} no llevan "
                + ("su fuente y su fecha de descarga" if sin_fuente else "")
                + (" ni " if sin_fuente and sin_enlace else "")
                + ("el enlace oficial de cada contrato" if sin_enlace else "")
                + ", así que no se pueden comprobar desde aquí. Tómalas como orientativas o "
                "repite la pregunta pidiendo la fuente y el enlace oficial.",
                icon=":material/warning:",
            )
        with st.expander(f"Datos de la consulta {numero}"):
            mostrar_resultado(consulta)
            st.code(consulta["sql"].strip(), language="sql")


def mostrar_respuesta(
    pregunta: str, respuesta: agente.Respuesta, clave: str, animar: bool = False
) -> None:
    if respuesta.retencion:
        st.warning(texto_visible(respuesta))
        return
    if animar:
        st.write_stream(animacion.escribir(respuesta.texto))
    else:
        st.markdown(respuesta.texto)
    mostrar_datos(respuesta, clave)
    if respuesta.preparada:
        interpretado = "; ".join(f"{k}: {v}" for k, v in respuesta.interpretacion.items())
        st.caption(
            "Respuesta preparada"
            + (" con una consulta revisada por el equipo" if respuesta.consultas else "")
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


def preparada(pregunta: str, zona) -> agente.Respuesta | None:
    """La respuesta preparada, con la animación de su consulta, o None si no hay ninguna."""
    con = conexion()
    coincidencia = respuestas_fijas.reconocer(con, pregunta)
    if coincidencia is None:
        return None
    resultado = None
    if coincidencia.fija.sql:
        inicio = time.perf_counter()
        zona.html(animacion.consulta(plano.plano_consulta(con, coincidencia.fija.sql)))
        resultado = respuestas_fijas.ejecutar(con, coincidencia)
        time.sleep(max(0.0, SEGUNDOS_ANIMACION - (time.perf_counter() - inicio)))
        zona.empty()
    fija = coincidencia.fija
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


def del_modelo(pregunta: str, historial: list[dict], zona) -> agente.Respuesta:
    """La respuesta del modelo, animando cada herramienta que usa."""
    con = conexion()
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
    zona = st.empty()
    if bateria.PATRON_DNI.search(pregunta):  # no se busca ni llega al modelo
        return agente.Respuesta(agente.PREGUNTA_CON_DNI)
    if not forzar_modelo:
        respuesta = preparada(pregunta, zona)
        if respuesta is not None:
            return respuesta
    if modelo is None:
        return agente.Respuesta(SIN_MODELO)
    return del_modelo(pregunta, historial, zona)


# --- Pantalla ---

st.header("Asistente")
st.caption(
    "Pregunta en tus palabras sobre los contratos y las subvenciones de la Comunidad de Madrid, "
    "sobre los datos de su catálogo de datos abiertos (sanidad, educación, presupuestos…), sobre "
    "lo que dicen los pliegos de una licitación o sobre las resoluciones del Tribunal "
    "Administrativo de Contratación Pública. Las preguntas frecuentes tienen una respuesta "
    "preparada con una consulta revisada por el equipo; las demás las redacta un modelo de "
    "lenguaje, que "
    "puede equivocarse: comprueba siempre la consulta, los datos y el enlace oficial que se "
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
        mostrar_respuesta(anterior, respuesta, clave=str(n))

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
        mostrar_respuesta(pregunta, respuesta, clave=str(len(turnos)), animar=True)
    turnos.append((pregunta, respuesta))

st.caption(textos.FUENTES)
