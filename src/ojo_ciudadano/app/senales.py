"""Explicación visual de cada señal de un contrato (D-023, estudios E-01 a E-06).

Cada señal se muestra con su nombre en lenguaje claro, una frase con las cifras del contrato
(que hace de texto alternativo del gráfico) y el gráfico pensado para ella.
"""

import hashlib

import duckdb
import streamlit as st

from ojo_ciudadano.app import datos, datos_flujos, graficos, textos


def _porcentaje(parte: float, total: float) -> str:
    return textos.porcentaje(parte / total) if total else "—"


def frase_y_grafico(con: duckdb.DuckDBPyConnection, indicador: str, contrato_id: str):
    """(frase, figura) de una señal, o (None, None) si no hay datos para dibujarla."""
    if indicador == "R-01":
        d = datos.detalle_r01(con, contrato_id)
        if not d:
            return None, None
        n = d["ofertas"]
        total = sum(c for _, c in d["distribucion"])
        varias = sum(c for o, c in d["distribucion"] if o >= 2)
        frase = (
            f"Este contrato recibió **{n} {'oferta' if n == 1 else 'ofertas'}**. De "
            f"{textos.numero(total)} contratos parecidos ({d['tipo'] or 'del mismo tipo'}), "
            f"**el {_porcentaje(varias, total)} recibió dos o más**."
        )
        return frase, graficos.ofertas(d)
    if indicador == "R-02":
        d = datos.detalle_r02(con, contrato_id)
        if not d:
            return None, None
        total = d["sin_anuncio"] + d["con_anuncio"]
        frase = (
            f"{d['organo']} adjudicó sin anuncio público, o por «otro procedimiento», el "
            f"**{_porcentaje(d['sin_anuncio'], total)} del importe** de sus contratos de este "
            f"tipo ({d['n_sin_anuncio']} de {d['n_contratos']} contratos)."
        )
        return frase, graficos.sin_anuncio(d)
    if indicador == "R-03":
        d = datos.detalle_r03(con, contrato_id)
        if not d:
            return None, None
        maximo = max(graficos.suma_doce_meses(d["contratos"]))
        quien = d["empresa"] or "la misma adjudicataria"
        frase = (
            f"{len(d['contratos'])} contratos menores de {quien} con este organismo, del mismo "
            f"tipo y de más de {textos.euros(d['umbral'] / 3)} cada uno (en el año antes y el "
            f"año después de este). En algún periodo de 12 meses suman "
            f"**{textos.euros(maximo)}**, más que el máximo de un contrato menor "
            f"({textos.euros(d['umbral'])}, con IVA). Pueden ser compras distintas: el "
            "expediente lo aclara."
        )
        return frase, graficos.menores(d, contrato_id)
    if indicador == "R-04":
        d = datos.detalle_r04(con, contrato_id)
        if not d or d["cuota"] is None:
            return None, None
        quien = d["partes"][0]["nombre"]
        cuota = textos.porcentaje(d["cuota"])
        mercado = f"contratos de {d['tipo']}"
        if d.get("division"):
            nombre = f" ({d['nombre_division'].lower()})" if d.get("nombre_division") else ""
            mercado += f" de la división CPV {d['division']}{nombre}"
        frase = (
            f"{quien} recibe el **{cuota}** del importe que {d['organo']} ha adjudicado "
            f"en {mercado} ({d['n_empresas']} adjudicatarios en total)."
        )
        return frase, graficos.reparto(d)
    if indicador in ("R-05", "R-06"):
        d = datos.detalle_importes(con, contrato_id)
        if not d or not d["adjudicado"]:
            return None, None
        iva = textos.iva_fuente(d["fuente"])
        if indicador == "R-05":
            mod = d["modificaciones"] or 0
            frase = (
                f"Se adjudicó por {textos.euros(d['adjudicado'], iva)} y después se añadieron "
                f"**{textos.euros(mod, iva)} ({_porcentaje(mod, d['adjudicado'])})** en "
                "modificaciones."
            )
            return frase, graficos.subida(d)
        if not d["presupuesto"]:
            return None, None
        baja = 1 - d["adjudicado"] / d["presupuesto"]
        if baja < 0:
            detalle = (
                f"se adjudicó **un {textos.porcentaje(-baja)} por encima** del precio de salida"
            )
        else:
            detalle = f"la rebaja fue del **{textos.porcentaje(baja, 1)}**"
        frase = (
            f"Precio de salida: {textos.euros(d['presupuesto'], iva)}; adjudicado por "
            f"{textos.euros(d['adjudicado'], iva)}: {detalle}."
        )
        return frase, graficos.rebaja(d)
    return None, None


def _clave_caja(prefijo: str, fila: dict, indicador: str) -> str:
    """Clave de la subcaja de una señal; el CSS (`estilo.css`) la reconoce por «cajasenal_»."""
    contrato = hashlib.md5(fila["contrato_id"].encode()).hexdigest()[:12]
    return f"cajasenal_{prefijo}_{contrato}_{indicador}"


def mostrar(
    con: duckdb.DuckDBPyConnection, indicador: str, contrato_id: str, en_caja: bool = False
) -> None:
    """Bloque de una señal: su nombre con icono, la frase con las cifras de este contrato y su
    gráfico. La explicación general va en «¿Qué significa?» (D-042). `en_caja`: dentro de la
    subcaja de la tarjeta, con el nombre en ámbar y la etiqueta «En este contrato»."""
    nombre = f"{textos.ICONO_SENAL[indicador]} **{textos.SENAL_CORTA[indicador]}**"
    st.markdown(f":orange[{nombre}]" if en_caja else nombre)
    frase, figura = frase_y_grafico(con, indicador, contrato_id)
    if frase:
        if en_caja:
            st.caption("En este contrato")
        st.markdown(frase)
    if figura is not None:
        st.plotly_chart(figura, config=graficos.CONFIG, key=f"{indicador}-{contrato_id}")
    with st.popover("¿Qué significa?", icon=":material/help:"):
        st.markdown(textos.SENAL_FRASE[indicador])
        if indicador in textos.CONTEXTO_SENAL:
            st.caption(textos.CONTEXTO_SENAL[indicador])


def etiquetas_senales(indicadores: list[str]) -> str:
    """Señales como etiquetas ámbar con su icono (Markdown de Streamlit)."""
    return " ".join(
        f":orange-badge[{textos.ICONO_SENAL[i]} {textos.SENAL_CORTA[i]}]" for i in indicadores
    )


def cabecera_contrato(fila: dict) -> str:
    """Cabecera de la tarjeta: título limpio; cuánto, a quién, quién lo adjudica y cuándo; y
    las señales. `adjudicatarios` es opcional (en la ficha de empresa ya se sabe quién es)."""
    titulo = textos.titulo_limpio(fila["titulo"] or fila["contrato_id"])
    if len(titulo) > 120:
        titulo = titulo[:117].rstrip() + "…"
    datos_fila = [f"**{textos.millones(fila['importe'])}**"] if fila.get("importe") else []
    quien = (fila.get("adjudicatarios") or "").split(" ; ")
    if quien[0]:
        datos_fila.append(quien[0] + (f" y {len(quien) - 1} más" if len(quien) > 1 else ""))
    datos_fila.append(fila["organo"])
    if fila.get("anio"):
        datos_fila.append(str(fila["anio"]))
    encontradas = [i for i in (fila["indicadores_activados"] or "").split(", ") if i]
    cabecera = f"**{titulo}**  \n" + " · ".join(datos_fila)
    if encontradas:
        cabecera += "  \n" + etiquetas_senales(encontradas)
    return cabecera


def tarjeta_contrato(con: duckdb.DuckDBPyConnection, fila: dict, prefijo: str) -> None:
    """Contrato como desplegable (D-042). En la cabecera, el título limpio, cuánto, a quién,
    quién lo adjudica y las señales en etiquetas ámbar. Al pulsar en cualquier parte se abre con
    el enlace al expediente arriba, un gráfico por señal (que solo se calcula entonces) y el
    aviso de contrato atípico. `fila` lleva los campos de `datos.alertas` o
    `datos.contratos_empresa`."""
    encontradas = [i for i in (fila["indicadores_activados"] or "").split(", ") if i]
    desplegable = st.expander(
        cabecera_contrato(fila), key=f"{prefijo}-{fila['contrato_id']}", on_change="rerun"
    )
    with desplegable:
        if not desplegable.open:
            return
        comprobadas = fila["n_aplicables"] or 0
        arriba = st.columns([3, 2], vertical_alignment="center")
        arriba[0].caption(
            f"{textos.euros(fila['importe'], textos.iva_fuente(fila['fuente']))} · "
            f"{len(encontradas)} de {comprobadas} "
            f"{'señal comprobada' if comprobadas == 1 else 'señales comprobadas'}"
        )
        if fila.get("url_origen"):
            arriba[1].link_button(
                "Ver el expediente oficial",
                fila["url_origen"],
                icon=":material/open_in_new:",
                width="stretch",
            )
        objeto = datos_flujos.cpv_contrato(con, fila["contrato_id"])
        if objeto:
            st.caption(
                f"Objeto (CPV {objeto['codigo']}): {objeto['nombre']} · sector: "
                f"{objeto['nombre_division']}. Clasificación oficial de la Plataforma de "
                "Contratación del Sector Público."
            )
        if encontradas:
            # Cada señal en su propia subcaja, de dos en dos y de la misma altura (D-042).
            for inicio in range(0, len(encontradas), 2):
                columnas = st.columns(2)
                pareja = encontradas[inicio : inicio + 2]
                for columna, indicador in zip(columnas, pareja, strict=False):
                    clave = _clave_caja(prefijo, fila, indicador)
                    with columna.container(border=True, key=clave):
                        mostrar(con, indicador, fila["contrato_id"], en_caja=True)
        else:
            st.markdown("En este contrato no hemos encontrado ninguna señal.")
        anomalia = datos.anomalia_contrato(con, fila["contrato_id"])
        if anomalia:
            st.markdown(
                f":material/scatter_plot: **Contrato atípico:** sus cifras se salen de lo "
                f"habitual en {textos.numero(anomalia['n_grupo'])} contratos parecidos. Es una "
                "señal experimental: atípico no significa irregular."
            )
            with st.popover("Ver el detalle", icon=":material/info:"):
                st.markdown(anomalia["motivo"])
        fondos = datos_flujos.financiacion_contrato(con, fila["contrato_id"])
        if fondos and fondos["financiado_ue"]:
            programas = ", ".join(
                datos_flujos.NOMBRE_PROGRAMA_UE.get(p, p)
                for p in (fondos["programas_ue"] or "").split(",")
                if p
            )
            st.markdown(
                "**Financiado con fondos de la Unión Europea**"
                + (f" ({programas})" if programas else "")
                + ", según la Plataforma de Contratación. Es un dato, no una señal."
            )
        for r in datos_flujos.recursos_contrato(con, fila["contrato_id"]):
            if r["expediente_citado"]:
                cabecera = (
                    "Resolución del Tribunal de Contratación de la Comunidad sobre este contrato"
                )
                metodo = "Enlazada por el expediente que cita la resolución."
            else:  # enlace por el título citado en el PDF (D-030, bloque C)
                cabecera = "Resolución del Tribunal que cita un contrato con el mismo título"
                metodo = (
                    "Enlazada por el título que cita la resolución, no por el expediente: "
                    "comprueba en la resolución que se refiere a este contrato."
                )
            st.markdown(
                f"**{cabecera}:** "
                f"[resolución {r['numero']}]({r['url_origen']}) del {r['fecha']}, "
                f"{r['tipo_resolucion'].lower()} (acto recurrido: {r['acto_recurrido'].lower()}). "
                f"{metodo} Fuente: Tribunal Administrativo de Contratación Pública de la "
                f"Comunidad de Madrid, datos descargados el {r['fecha_descarga']}."
            )
            st.caption(textos.AVISO_RECURSOS)
        pliegos = datos_flujos.pliegos_contrato(con, fila["contrato_id"])
        if pliegos:
            enlaces = " · ".join(
                f"[{textos.NOMBRE_PLIEGO[p['tipo']]}]({p['url_documento']})" for p in pliegos
            )
            st.markdown(
                f"**Pliegos:** {enlaces} · Fuente: Plataforma de Contratación del Sector "
                f"Público, enlaces descargados el {pliegos[0]['fecha_descarga']}."
            )
            if st.button(
                "¿Qué dice el pliego?",
                key=f"{prefijo}-pliego-{fila['contrato_id']}",
                icon=":material/description:",
                help="Abre el asistente con la pregunta escrita: busca en el pliego los "
                "apartados relacionados con las señales de este contrato; no confirma ni "
                "descarta ninguna.",
            ):
                st.session_state["pregunta_asistente"] = textos.pregunta_pliego(
                    pliegos[0]["contrato_id"], encontradas
                )
                st.switch_page("paginas/asistente.py")
        if not fila["url_origen"]:
            st.caption("Sin enlace oficial disponible para este contrato.")
