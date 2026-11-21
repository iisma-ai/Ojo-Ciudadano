"""Tabla de resultados de una consulta del asistente, compartida por «Preguntas guiadas» y
«Asistente»: proporciones en porcentaje, importes con separador de miles y enlaces clicables."""

import streamlit as st

from ojo_ciudadano.asistente import sql_seguro


def mostrar_resultado(resultado: dict) -> None:
    columnas_pct = [
        c for c in resultado["columnas"] if c.startswith(("proporcion", "modificaciones_"))
    ]
    filas = []
    for fila in resultado["filas"]:
        registro = dict(zip(resultado["columnas"], fila, strict=True))
        for c in columnas_pct:
            if registro[c] is not None:
                registro[c] = 100 * registro[c]
        filas.append(registro)

    if not filas:
        st.write("Sin resultados para esta consulta.")
        return
    configuracion = {c: st.column_config.NumberColumn(format="%.1f %%") for c in columnas_pct}
    for c in resultado["columnas"]:
        if c.startswith("importe"):
            configuracion[c] = st.column_config.NumberColumn(format="localized")
        if c.startswith("url"):
            etiqueta = {"url_origen": "Enlace oficial", "url_bases": "Bases reguladoras"}.get(c, c)
            configuracion[c] = st.column_config.LinkColumn(
                etiqueta, display_text="Ver en la fuente oficial"
            )
    st.dataframe(filas, column_config=configuracion, hide_index=True)
    if resultado["recortado"]:
        st.caption(f"Se muestran las primeras {sql_seguro.LIMITE_FILAS} filas.")
