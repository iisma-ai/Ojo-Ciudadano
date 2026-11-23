"""Explicación visual de cada señal de un contrato (D-023, estudios E-01 a E-06).

Cada señal se muestra con su nombre en lenguaje claro, una frase con las cifras del contrato
(que hace de texto alternativo del gráfico) y el gráfico pensado para ella.
"""

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
        frase = (
            f"{quien} recibe el **{cuota}** del importe que {d['organo']} ha adjudicado "
            f"en contratos de {d['tipo']} ({d['n_empresas']} empresas en total)."
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


def mostrar(con: duckdb.DuckDBPyConnection, indicador: str, contrato_id: str) -> None:
    """Bloque de una señal: título, frase y gráfico."""
    st.markdown(f"**{textos.SENAL_CORTA[indicador]}**")
    st.caption(textos.SENAL_FRASE[indicador])
    frase, figura = frase_y_grafico(con, indicador, contrato_id)
    if frase:
        st.markdown(frase)
    if figura is not None:
        st.plotly_chart(figura, config=graficos.CONFIG, key=f"{indicador}-{contrato_id}")


def tarjeta_contrato(con: duckdb.DuckDBPyConnection, fila: dict, prefijo: str) -> None:
    """Contrato como desplegable: título, organismo y señales en la cabecera; al pulsar en
    cualquier parte se abre con un gráfico por señal (que solo se calcula entonces), el aviso
    de contrato atípico y el enlace al expediente. `fila` lleva los campos de
    `datos.alertas` o `datos.contratos_empresa`."""
    titulo = fila["titulo"] or fila["contrato_id"]
    if len(titulo) > 110:
        titulo = titulo[:107].rstrip() + "…"
    encontradas = [i for i in (fila["indicadores_activados"] or "").split(", ") if i]
    nombres = " · ".join(textos.SENAL_CORTA[i] for i in encontradas)
    cabecera = f"**{titulo}**  \n:gray[{fila['organo']}]"
    if nombres:
        cabecera += f"  ·  :blue[{nombres}]"
    desplegable = st.expander(cabecera, key=f"{prefijo}-{fila['contrato_id']}", on_change="rerun")
    with desplegable:
        comprobadas = fila["n_aplicables"] or 0
        st.caption(
            f"{fila['anio'] or 'Sin fecha'} · "
            f"{textos.euros(fila['importe'], textos.iva_fuente(fila['fuente']))} · "
            f"{len(encontradas)} de {comprobadas} "
            f"{'señal comprobada' if comprobadas == 1 else 'señales comprobadas'}"
        )
        if not desplegable.open:
            return
        objeto = datos_flujos.cpv_contrato(con, fila["contrato_id"])
        if objeto:
            st.caption(
                f"Objeto (CPV {objeto['codigo']}): {objeto['nombre']} · sector: "
                f"{objeto['nombre_division']}. Clasificación oficial de la Plataforma de "
                "Contratación del Sector Público."
            )
        if encontradas:
            columnas = st.columns(2) if len(encontradas) > 1 else [st.container()]
            for n, indicador in enumerate(encontradas):
                with columnas[n % len(columnas)]:
                    mostrar(con, indicador, fila["contrato_id"])
        else:
            st.markdown("En este contrato no hemos encontrado ninguna señal.")
        anomalia = datos.anomalia_contrato(con, fila["contrato_id"])
        if anomalia:
            st.markdown(
                f"**Contrato atípico** respecto a {textos.numero(anomalia['n_grupo'])} "
                "contratos similares (señal experimental, no suma a las demás; atípico no "
                f"significa irregular): {anomalia['motivo']}"
            )
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
        if fila["url_origen"]:
            st.link_button(
                "Ver el expediente oficial", fila["url_origen"], icon=":material/open_in_new:"
            )
        else:
            st.caption("Sin enlace oficial disponible para este contrato.")
