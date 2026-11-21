"""Contratos a revisar: los que tienen alguna señal, con un gráfico por señal (D-023, A-03)."""

import streamlit as st

from ojo_ciudadano.app import datos, senales, textos
from ojo_ciudadano.app.conexion import conexion

LIMITE = 30

con = conexion()
st.header("Contratos a revisar")
st.caption("Contratos en los que hemos encontrado alguna señal. " + textos.NOTA_SENAL)

conteo = datos.conteo_senales(con)
elegida = st.pills(
    "Qué señal buscar",
    list(textos.SENAL_CORTA),
    format_func=lambda i: (
        f"{textos.SENAL_CORTA[i]} ({textos.numero(conteo[i]['encontrados'])})"
        if i in conteo
        else textos.SENAL_CORTA[i]
    ),
    selection_mode="single",
)
if elegida:
    st.caption(textos.SENAL_FRASE[elegida])

menores = st.toggle(
    "Incluir contratos menores",
    help="Los contratos menores son los de menos de 15.000 € (40.000 € en obras), sin IVA. "
    "Son muchos y en ellos solo se pueden comprobar dos señales.",
)
# Sin menores, solo contratos en los que se han podido comprobar al menos 3 señales.
filas = datos.alertas(con, 1 if menores else 3, elegida, LIMITE)

if not filas:
    st.info("No hay contratos con esta señal.")
    st.stop()

st.caption(f"Los {len(filas)} contratos con más señales, de más a menos.")

for fila in filas:
    titulo = fila["titulo"] or fila["contrato_id"]
    if len(titulo) > 160:
        titulo = titulo[:157].rstrip() + "…"
    encontradas = (fila["indicadores_activados"] or "").split(", ")
    iva = textos.iva_fuente(fila["fuente"])
    with st.container(border=True):
        izquierda, derecha = st.columns([5, 1], vertical_alignment="center")
        with izquierda:
            st.markdown(f"**{titulo}**")
            st.caption(
                f"{fila['organo']} · {fila['anio'] or 'sin fecha'} · "
                f"{textos.euros(fila['importe'], iva)}"
            )
            insignias = " ".join(
                f":orange-badge[{textos.SENAL_CORTA[i]}]" for i in encontradas if i
            )
            comprobadas = fila["n_aplicables"]
            st.markdown(
                f"{insignias} &nbsp; :gray[de {comprobadas} "
                f"{'señal comprobada' if comprobadas == 1 else 'señales comprobadas'}]"
            )
        with derecha:
            ver = st.toggle("Ver gráficos", key=f"ver-{fila['contrato_id']}")
        if ver:
            columnas = st.columns(2) if len(encontradas) > 1 else [st.container()]
            for n, indicador in enumerate(i for i in encontradas if i):
                with columnas[n % len(columnas)]:
                    senales.mostrar(con, indicador, fila["contrato_id"])
            anomalia = datos.anomalia_contrato(con, fila["contrato_id"])
            if anomalia:
                st.markdown(
                    f"**Contrato atípico** respecto a {textos.numero(anomalia['n_grupo'])} "
                    "contratos similares (señal experimental, no suma a las demás; atípico no "
                    f"significa irregular): {anomalia['motivo']}"
                )
            if fila["url_origen"]:
                st.link_button(
                    "Ver el expediente oficial", fila["url_origen"], icon=":material/open_in_new:"
                )
