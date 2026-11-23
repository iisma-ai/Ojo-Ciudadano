"""Asistente: preguntas en lenguaje natural respondidas con SQL validado (docs/05-asistente.md).

Cada respuesta enseña las consultas usadas y sus resultados con enlace a la fuente. Mientras no
haya modelo de lenguaje conectado (D-010), la pantalla lo dice y remite a las preguntas guiadas.
"""

import streamlit as st

from ojo_ciudadano.app import graficos, textos
from ojo_ciudadano.app.conexion import conexion
from ojo_ciudadano.app.tablas import mostrar_resultado
from ojo_ciudadano.asistente import agente, bateria, catalogo

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


def texto_visible(respuesta: agente.Respuesta) -> str:
    """Lo que ve la persona (y lo que vuelve al modelo en el historial)."""
    return RETENIDAS.get(respuesta.retencion, respuesta.texto)


st.header("Asistente")
st.caption(
    "Pregunta en tus palabras sobre los contratos y las subvenciones de la Comunidad de Madrid, "
    "sobre los datos de su catálogo de datos abiertos (sanidad, educación, presupuestos…), sobre "
    "lo que dicen los pliegos de una licitación o sobre las resoluciones del Tribunal "
    "Administrativo de Contratación Pública. "
    "Las respuestas las redacta un modelo de lenguaje y pueden contener errores: comprueba "
    "siempre la consulta, los datos y el enlace oficial que se muestran con cada una. No "
    "escribas datos personales en tus preguntas."
)

modelo = agente.modelo_configurado()
if modelo is None:
    st.info(
        "El asistente todavía no está conectado a un modelo de lenguaje. Mientras tanto, las "
        "preguntas guiadas responden a las preguntas más frecuentes con consultas verificadas."
    )
    st.page_link(
        "paginas/preguntas.py", label="Ir a las preguntas guiadas", icon=":material/arrow_forward:"
    )
    with st.expander("Ejemplos de preguntas que podrá responder"):
        st.markdown("\n".join(f"- {p.pregunta}" for p in bateria.BATERIA if p.sql))
    st.stop()


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


def mostrar_respuesta(respuesta: agente.Respuesta) -> None:
    if respuesta.retencion:
        st.warning(texto_visible(respuesta))
        return
    st.markdown(respuesta.texto)
    # Primero se ve (D-023, A-08): el gráfico de la primera consulta que se pueda dibujar.
    for numero, consulta in enumerate(respuesta.consultas, start=1):
        if consulta.get("documento"):
            continue  # extractos de texto: nada que dibujar
        figura, _ = graficos.automatico(consulta)
        if figura is not None:
            st.plotly_chart(
                figura, config=graficos.CONFIG, key=f"asistente-{id(respuesta)}-{numero}"
            )
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
        with st.expander(f"Datos de la consulta {numero}"):
            mostrar_resultado(consulta)
            if "fuente" not in consulta["columnas"]:
                st.caption(
                    "Esta consulta no incluye la columna de fuente: consulta las fuentes al pie "
                    "de la página."
                )
            if "contrato_id" in consulta["columnas"] and "url_origen" not in consulta["columnas"]:
                st.caption("Esta consulta no incluye el enlace oficial de cada contrato.")
            st.code(consulta["sql"].strip(), language="sql")
    st.caption(textos.AVISO_CORTO)


turnos = st.session_state.setdefault("turnos_asistente", [])
for pregunta, respuesta in turnos:
    st.chat_message("user").write(pregunta)
    with st.chat_message("assistant"):
        mostrar_respuesta(respuesta)

# Una pregunta que llega escrita desde otra pantalla («¿Qué dice el pliego?»).
pendiente = st.session_state.pop("pregunta_asistente", None)
if pregunta := st.chat_input("Escribe tu pregunta") or pendiente:
    st.chat_message("user").write(pregunta)
    historial = []
    for anterior, respuesta in turnos:
        historial += [
            {"rol": "usuario", "contenido": anterior},
            {"rol": "modelo", "contenido": texto_visible(respuesta)},
        ]
    with st.chat_message("assistant"):
        try:
            with st.spinner("Consultando los datos…"):
                respuesta = agente.responder(conexion(), modelo, pregunta, historial)
        except Exception:  # red, saldo o proveedor caído: no enseñar la traza
            st.warning(
                "El modelo de lenguaje no está disponible ahora mismo. Vuelve a intentarlo en "
                "unos minutos o usa las preguntas guiadas.",
                icon=":material/cloud_off:",
            )
            st.page_link(
                "paginas/preguntas.py",
                label="Ir a las preguntas guiadas",
                icon=":material/arrow_forward:",
            )
            st.stop()
        mostrar_respuesta(respuesta)
    turnos.append((pregunta, respuesta))

st.caption(textos.FUENTES)
