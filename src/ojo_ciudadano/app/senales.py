"""Explicación visual de cada señal de un contrato (D-023, estudios E-01 a E-06).

Cada señal se muestra con su nombre en lenguaje claro, una frase con las cifras del contrato
(que hace de texto alternativo del gráfico) y el gráfico pensado para ella.
"""

import duckdb
import streamlit as st

from ojo_ciudadano.app import datos, graficos, textos


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
