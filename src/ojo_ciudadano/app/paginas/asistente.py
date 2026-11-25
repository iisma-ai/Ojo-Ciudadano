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

import random
import time
from pathlib import Path

import streamlit as st

from ojo_ciudadano.app import animacion, billetes, graficos, limite_modelo, ojo_cristal, textos
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
        st.caption("Respuesta preparada, con una consulta comprobada de antemano.")
        if modelo is not None and st.button(
            "No es lo que preguntaba: que responda el modelo",
            key=f"al-modelo-{clave}",
            icon=":material/smart_toy:",
        ):
            st.session_state["pregunta_asistente"] = pregunta
            st.session_state["forzar_modelo"] = True
            st.rerun()


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
    # Solo para las preguntas que llegan al modelo (D-057): desde España, y 5 seguidas con 5
    # minutos de espera. Lo de fuera de España no cuenta como consulta.
    if not limite_modelo.desde_pais_permitido():
        return agente.Respuesta(limite_modelo.FUERA_DE_ESPANA)
    espera = limite_modelo.limitador().intentar(limite_modelo.identidad())
    if espera:
        return agente.Respuesta(limite_modelo.mensaje(espera))
    return del_modelo(pregunta, historial)


# --- Pantalla (D-059) ---
# Solo el chat, en un panel de cristal: el ojo y un saludo al empezar, la conversación, tres
# preguntas sugeridas que se pueden cambiar y la caja para escribir. Nada más: el aviso legal,
# cómo responde el asistente y la lista de preguntas preparadas están en «Aviso legal y fuentes».

LOGO = str(Path(__file__).parents[1] / "static" / "logo.svg")
OJO = ojo_cristal.imagenes()
N_SUGERIDAS = 3

# silueta de persona, clara y sin fondo, para tus mensajes (D-061)
ICONO_PERSONA = (
    "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' "
    "fill='none' stroke='%23E8F2FF' stroke-width='1.8' stroke-linecap='round'%3E"
    "%3Ccircle cx='12' cy='8' r='4'/%3E%3Cpath d='M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6'/%3E"
    '%3C/svg%3E")'
)

ESTILO = """
<style>
/* El panel del chat: cristal azul vivo como el de la presentación (D-060): teñido de azul,
   con luces azules difuminadas detrás, borde claro y desenfoque de lo que hay detrás. */
.st-key-chat { position: relative; isolation: isolate; overflow: hidden;
  padding: 1.2rem 1.4rem 1rem !important; border-radius: 30px !important;
  background: linear-gradient(150deg, rgba(120, 175, 255, 0.24), rgba(61, 139, 253, 0.10) 45%,
    rgba(30, 90, 210, 0.18)) !important;
  border: 1px solid rgba(160, 205, 255, 0.34) !important;
  box-shadow: 0 30px 80px rgba(0, 6, 20, 0.55), 0 0 60px rgba(61, 139, 253, 0.18),
    inset 0 1px 0 rgba(255, 255, 255, 0.28) !important;
  -webkit-backdrop-filter: blur(22px) saturate(160%); backdrop-filter: blur(22px) saturate(160%); }
.st-key-chat::before { content: ""; position: absolute; inset: 0; z-index: -1;
  pointer-events: none;
  background:
    radial-gradient(42% 38% at 12% 8%, rgba(110, 170, 255, 0.38), transparent 70%),
    radial-gradient(38% 34% at 92% 30%, rgba(56, 189, 248, 0.22), transparent 70%),
    radial-gradient(50% 40% at 70% 105%, rgba(61, 110, 253, 0.32), transparent 70%); }
.st-key-chat_mensajes { border: none !important; background: none !important;
  box-shadow: none !important; }
.st-key-chat [data-testid="stChatMessage"] { background: transparent; padding: .4rem 0; }
/* los mensajes de la persona, en burbuja azul a la derecha */
.st-key-chat [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
  flex-direction: row-reverse; text-align: right; }
.st-key-chat [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
  [data-testid="stMarkdownContainer"] { width: fit-content; max-width: 85%; margin-left: auto;
  text-align: left; padding: .65rem 1rem;
  border-radius: 18px 18px 4px 18px; color: #fff;
  /* cristal claro translúcido, a juego con el panel (D-061) */
  background: linear-gradient(135deg, rgba(255,255,255,.16), rgba(160,205,255,.08));
  border: 1px solid rgba(190, 220, 255, 0.32);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.18); }
/* el icono de la persona: solo la silueta, casi blanca, sin el cuadrado de color */
.st-key-chat [data-testid="stChatMessageAvatarUser"] { background: transparent !important;
  color: rgba(232, 242, 255, 0.85) !important; border: 1.5px solid rgba(232, 242, 255, 0.5);
  border-radius: 50% !important; }
.st-key-chat [data-testid="stChatMessageAvatarUser"] > span { display: none; }
.st-key-chat [data-testid="stChatMessageAvatarUser"] { background-repeat: no-repeat !important;
  background-position: center !important; background-size: 62% !important;
  background-image: ICONO_PERSONA  !important; }

/* sugerencias: cápsulas de cristal pequeñas */
.st-key-sugerencias { gap: .5rem !important; flex-wrap: wrap; justify-content: center; }
.st-key-sugerencias button p { font-size: .9rem !important; }
.st-key-sugerencias button { background: rgba(255, 255, 255, 0.10) !important;
  border: 1px solid rgba(180, 215, 255, 0.34) !important; }
.st-key-sugerencias button:hover { background: rgba(255, 255, 255, 0.18) !important; }
.st-key-chat [data-testid="stChatInput"] > div { background: rgba(8, 36, 84, 0.45) !important;
  border: 1px solid rgba(170, 210, 255, 0.34) !important; }
.st-key-chat [data-testid="stChatInput"] { border-radius: 999px !important; }
</style>
"""

BIENVENIDA = """
<style>
.oc-saludo { display:flex; flex-direction:column; align-items:center; gap:12px;
  padding: 150px 0 8px; font-family: Outfit, sans-serif; text-align:center; }
.oc-saludo h2 { margin:0; padding:0; font-size:clamp(1.6rem, 2.6vw, 2.2rem); font-weight:700;
  letter-spacing:-.02em; color:#fff; }
.oc-saludo p { margin:0; color:#C4D8F2; font-size:1.05rem; }
</style>
<div class="oc-saludo">
  <h2>¿Qué quieres saber del gasto público?</h2>
  <p>Pregunta como hablas. Te respondo con los datos oficiales y su fuente.</p>
</div>"""

# El ojo, fuera del panel y a su lado, como un personaje que acompaña: flota despacio, el iris
# gira y de vez en cuando mira a un lado y a otro.
PERSONAJE = f"""
<style>
.oc-personaje {{ position:relative; width:min(100%, 190px); aspect-ratio:1; margin: 0 auto;
  animation: oc-flota 6s ease-in-out infinite; }}
.oc-personaje::before {{ content:""; position:absolute; inset:-22%; border-radius:50%;
  background:radial-gradient(circle, rgba(56,189,248,.32), transparent 62%); }}
/* el iris se mueve dentro del cristal (el cristal queda quieto): mira a un lado y a otro con
   saltos rápidos y pausas, como una mirada de verdad, mientras gira */
.oc-personaje .globo {{ position:absolute; inset:0; border-radius:50%; overflow:hidden; }}
.oc-personaje .mira {{ position:absolute; inset:0;
  animation: oc-mira 12s cubic-bezier(.6,0,.2,1) infinite; }}
.oc-personaje img {{ position:absolute; inset:0; width:100%; height:100%; }}
.oc-personaje .iris {{ animation: oc-gira 24s linear infinite; }}
@keyframes oc-flota {{ 0%,100% {{ transform: translateY(0); }}
  50% {{ transform: translateY(-12px); }} }}
@keyframes oc-gira {{ to {{ transform: rotate(360deg); }} }}
@keyframes oc-mira {{
  0%,18% {{ transform: translate(0, 0); }}
  21%,34% {{ transform: translate(-13%, -2%); }}
  37%,46% {{ transform: translate(0, 0); }}
  49%,60% {{ transform: translate(13%, 3%); }}
  63%,70% {{ transform: translate(7%, -9%); }}
  73%,100% {{ transform: translate(0, 0); }} }}
@media (prefers-reduced-motion: reduce) {{ .oc-personaje, .oc-personaje * {{ animation:none; }} }}
html.oc-sin-gpu .oc-personaje, html.oc-sin-gpu .oc-personaje * {{ animation:none; }}
</style>
<div class="oc-personaje" role="img" aria-label="El ojo de Ojo Ciudadano">
  <div class="globo"><div class="mira"><img class="iris" src="{OJO["{iris}"]}" alt=""></div></div>
  <img src="{OJO["{cristal}"]}" alt="">
</div>"""


def preguntas_sugeribles() -> list:
    """Las preguntas preparadas que se pueden ofrecer tal cual (sin pedir una empresa)."""
    return [f for f in respuestas_fijas.FIJAS if "empresa" not in f.parametros]


def sugeridas() -> list:
    """Las tres sugerencias de ahora; al principio, las de `respuestas_fijas.sugerencias`."""
    todas = {f.id: f for f in preguntas_sugeribles()}
    ids = st.session_state.get("sugeridas_asistente")
    if not ids:
        ids = [f.id for f in respuestas_fijas.sugerencias() if f.id in todas][:N_SUGERIDAS]
        st.session_state["sugeridas_asistente"] = ids
    return [todas[i] for i in ids if i in todas]


def otras_sugerencias() -> None:
    """Tres preguntas distintas de las que se ven."""
    vistas = set(st.session_state.get("sugeridas_asistente") or [])
    candidatas = [f.id for f in preguntas_sugeribles() if f.id not in vistas]
    st.session_state["sugeridas_asistente"] = random.sample(
        candidatas, min(N_SUGERIDAS, len(candidatas))
    )


st.html(animacion.CSS)  # una vez por página, para todas las animaciones
st.html(ESTILO.replace("ICONO_PERSONA", ICONO_PERSONA))

modelo = agente.modelo_configurado()
turnos = st.session_state.setdefault("turnos_asistente", [])
elegida = None

lado, centro, _ = st.columns([1.3, 6, 1], vertical_alignment="center")
with lado:
    billetes.pintar(PERSONAJE, clave="asistente_personaje")
with centro, st.container(key="chat", border=True):
    mensajes = st.container(key="chat_mensajes", height=560, border=False)
    with st.container(key="sugerencias", horizontal=True, vertical_alignment="center"):
        for fija in sugeridas():
            if st.button(fija.pregunta, key=f"sugerencia-{fija.id}"):
                elegida = fija.pregunta
        st.button(
            "",
            icon=":material/refresh:",
            key="otras_sugerencias",
            help="Otras preguntas",
            type="tertiary",
            on_click=otras_sugerencias,
        )
    escrita = st.chat_input("Escribe tu pregunta")

# Una pregunta que llega escrita desde otra pantalla («¿Qué dice el pliego?») o desde el botón
# «que responda el modelo».
pendiente = st.session_state.pop("pregunta_asistente", None)
forzar = st.session_state.pop("forzar_modelo", False)
pregunta = escrita or elegida or pendiente

with mensajes:
    if not turnos and not pregunta:
        billetes.pintar(BIENVENIDA, clave="asistente_saludo")
    for n, (anterior, respuesta) in enumerate(turnos):
        st.chat_message("user").write(anterior)
        with st.chat_message("assistant", avatar=LOGO):
            mostrar_respuesta(anterior, respuesta, clave=str(n))  # quieta: sin animar
    if pregunta:
        st.chat_message("user").write(pregunta)
        historial = []
        for anterior, respuesta in turnos:
            historial += [
                {"rol": "usuario", "contenido": anterior},
                {"rol": "modelo", "contenido": texto_visible(respuesta)},
            ]
        with st.chat_message("assistant", avatar=LOGO):
            respuesta = contestar(pregunta, historial, forzar_modelo=forzar and not elegida)
            mostrar_respuesta(pregunta, respuesta, clave=str(len(turnos)), nueva=True)
        turnos.append((pregunta, respuesta))
