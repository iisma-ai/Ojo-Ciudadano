"""Presupuesto y contexto: cuánto gasta la Comunidad, en qué y qué convenios y registros hay.

D-024.

Datos oficiales de la Comunidad de Madrid (catálogo de datos abiertos y Portal de Transparencia).
Sirven para dar escala a los contratos y subvenciones; no son indicadores de riesgo. Cada cifra
lleva el enlace a su fuente y la fecha de descarga. Sin personas físicas (D-007).
"""

import streamlit as st

from ojo_ciudadano.app import datos_contexto as dc
from ojo_ciudadano.app import datos_flujos as df
from ojo_ciudadano.app import graficos_contexto as gc
from ojo_ciudadano.app import textos
from ojo_ciudadano.app.conexion import conexion

con = conexion()
st.header("Presupuesto y contexto")
st.caption(
    "Cuánto presupuesta y gasta la Comunidad de Madrid, en qué lo gasta y qué convenios y "
    "registros públicos hay. Es el contexto en el que se mueven los contratos y subvenciones."
)

if not dc.hay_contexto(con):
    st.warning(
        "El presupuesto y el contexto de la Comunidad de Madrid no están disponibles "
        "todavía en esta versión de la web.",
        icon=":material/database:",
    )
    st.stop()


def fuente(url: str, fecha, nombre: str = "Datos abiertos de la Comunidad de Madrid") -> None:
    st.caption(f"Fuente: [{nombre}]({url}) · descargado el {fecha}")


pestanas = st.tabs(
    [
        "Gasto por consejería",
        "Evolución del presupuesto",
        "Personal",
        "Convenios",
        "Registros",
        "Recursos ante el Tribunal",
    ]
)

# --- Gasto por consejería ---
with pestanas[0]:
    anios = dc.anios_liquidados(con)
    anio = st.segmented_control("Año", anios, default=anios[0], key="anio_cons") or anios[0]
    filas = dc.ejecucion_consejerias(con, anio)
    st.info(textos.AVISO_CONTEXTO, icon=":material/info:")
    if not filas:
        st.write("No hay datos de ese año.")
    else:
        total = sum(f["obligaciones"] or 0 for f in filas)
        mayor = filas[0]
        st.markdown(
            f"En {anio}, las consejerías reconocieron **{textos.euros(total)}** de gasto; la "
            f"mayor fue {mayor['consejeria']}, con **{textos.euros(mayor['obligaciones'])}**."
        )
        st.caption(
            "Gasto reconocido (obligaciones reconocidas) por consejería, presupuestos liquidados."
        )
        gc.pintar_barras(
            "gasto_consejerias",
            [f["consejeria"] for f in filas],
            [f["obligaciones"] or 0 for f in filas],
        )
        fuente(filas[0]["url_origen"], filas[0]["fecha_descarga"])
        with st.expander("Ver la tabla con contratos y subvenciones de cada consejería"):
            st.dataframe(
                [
                    {
                        "Consejería": f["consejeria"],
                        "Presupuesto inicial": textos.euros(f["inicial"]),
                        "Gasto reconocido": textos.euros(f["obligaciones"]),
                        "Pagado": textos.euros(f["pagos"]),
                        "Contratos, Plataforma (sin IVA)": textos.euros(f["contratos_plataforma"]),
                        "Contratos, portal (con IVA)": textos.euros(f["contratos_portal"]),
                        "Subvenciones concedidas": textos.euros(f["subvenciones"]),
                    }
                    for f in filas
                ],
                hide_index=True,
                width="stretch",
            )
            st.caption(
                "Contratos y subvenciones: los de los órganos de cada consejería con fecha de "
                f"{anio} en nuestra base (Plataforma de Contratación, portal de la Comunidad y "
                "BDNS). La Plataforma y el portal son fuentes distintas y no se suman."
            )

# --- Evolución ---
with pestanas[1]:
    st.info(textos.AVISO_CONTEXTO, icon=":material/info:")
    capitulos = dc.gasto_por_capitulo(con)
    if capitulos:
        st.subheader("En qué se gasta")
        st.caption("Obligaciones reconocidas por capítulo, presupuestos liquidados consolidados.")
        st.plotly_chart(gc.gasto_capitulos(capitulos), config=gc.GRAFICO_CONFIG, width="stretch")
        fuente(capitulos[0]["url_origen"], capitulos[0]["fecha_descarga"])
    gi = dc.gastos_e_ingresos_iniciales(con)
    if gi:
        st.subheader("Gastos e ingresos presupuestados")
        st.plotly_chart(gc.gastos_e_ingresos(gi), config=gc.GRAFICO_CONFIG, width="stretch")
        fuente(gi[0]["url_origen"], capitulos[0]["fecha_descarga"] if capitulos else "")
        ingresos = dc.ingresos_por_capitulo(con, gi[-1]["anio"])
        if ingresos:
            st.subheader(f"De dónde vienen los ingresos presupuestados en {gi[-1]['anio']}")
            gc.pintar_barras(
                "ingresos",
                [i["capitulo"].capitalize() for i in ingresos],
                [i["importe"] for i in ingresos],
            )
            fuente(ingresos[0]["url_origen"], ingresos[0]["fecha_descarga"])

# --- Personal ---
with pestanas[2]:
    personal = dc.personal_por_area(con)
    if personal:
        total = [p for p in personal if p["concepto"].lower().startswith("total")]
        areas = [p for p in personal if not p["concepto"].lower().startswith("total")]
        st.markdown(
            f"En {personal[0]['anio']}, la Comunidad tenía "
            + (
                f"**{textos.numero(total[0]['personas'])} personas** a su servicio."
                if total
                else "personal en estas áreas."
            )
        )
        gc.pintar_barras(
            "personal",
            [a["concepto"].replace("Personal al servicio de ", "") for a in areas],
            [a["personas"] for a in areas],
            formato=lambda v: textos.numero(v),
        )
        fuente(personal[0]["url_origen"], personal[0]["fecha_descarga"])
    plantilla = dc.plantilla(con)
    if plantilla:
        st.subheader("Puestos de la relación de puestos de trabajo (funcionarios)")
        st.caption("Solo recuentos por organismo; no hay datos de personas.")
        gc.pintar_barras(
            "plantilla",
            [p["organismo"].capitalize() for p in plantilla[:15]],
            [p["n_puestos"] for p in plantilla[:15]],
            formato=lambda v: textos.numero(v),
        )
        fuente(plantilla[0]["url_origen"], plantilla[0]["fecha_descarga"])

# --- Convenios ---
with pestanas[3]:
    st.info(textos.AVISO_CONVENIOS, icon=":material/info:")
    por_anio = dc.convenios_por_consejeria(con)
    if por_anio:
        st.plotly_chart(gc.convenios_por_anio(por_anio), config=gc.GRAFICO_CONFIG, width="stretch")
    columnas = st.columns([2, 2, 1])
    consejeria = columnas[0].selectbox(
        "Consejería", [None, *dc.consejerias_con_convenios(con)], format_func=lambda c: c or "Todas"
    )
    texto = columnas[1].text_input("Buscar en el título o en los firmantes")
    con_fin = columnas[2].toggle("Con financiación")
    convenios = dc.lista_convenios(con, consejeria, texto, con_fin)
    st.caption(f"{len(convenios)} convenios (los más recientes primero, hasta 50).")
    for cv in convenios:
        titulo = (cv["titulo"] or cv["referencia"])[:140]
        with st.expander(f"{titulo} · {cv['consejeria'].title()}"):
            vigencia = "indefinida" if cv["indefinido"] else cv["vigencia_hasta"] or "sin dato"
            st.markdown(
                f"**Referencia** {cv['referencia']} · **Firma** {cv['fecha_firma'] or 'sin dato'}"
                f" · **Vigencia** {vigencia}"
            )
            if cv["entidades"]:
                st.markdown(f"**Firmantes que son entidades:** {cv['entidades']}")
            if cv["n_firmantes"]:
                st.caption(f"{cv['n_firmantes']} firmantes además de la Comunidad.")
            if cv["financiacion"]:
                st.markdown(f"**Financiación según la fuente:** {cv['financiacion']}")
            fuente(cv["url_origen"], cv["fecha_descarga"], "Portal de Transparencia")

# --- Registros ---
with pestanas[4]:
    st.info(textos.AVISO_REGISTROS, icon=":material/info:")
    resumen = dc.empresas_en_registros(con)
    cifras = st.columns(max(1, len(resumen)))
    for columna, r in zip(cifras, resumen, strict=False):
        columna.metric(
            dc.NOMBRE_REGISTRO[r["registro"]],
            textos.numero(r["n_entidades"]),
            help=f"{textos.numero(r['n_con_contratos'])} aparecen también como adjudicatarias o "
            "beneficiarias en nuestros datos.",
        )
        columna.caption(f"{textos.numero(r['n_con_contratos'])} con contratos o subvenciones")
    if resumen:
        registro = (
            st.segmented_control(
                "Registro",
                [r["registro"] for r in resumen],
                default=resumen[0]["registro"],
                format_func=dc.NOMBRE_REGISTRO.get,
            )
            or resumen[0]["registro"]
        )
        entidades = dc.entidades_registradas_con_contratos(con, registro)
        st.markdown("**Con más importe adjudicado (Plataforma de Contratación, sin IVA)**")
        st.dataframe(
            [
                {
                    "Entidad": e["nombre"],
                    "NIF": e["nif"],
                    "Detalle": e["detalle"],
                    "Contratos": e["n_contratos"],
                    "Importe adjudicado": textos.euros(e["importe_sin_iva"], "sin IVA"),
                }
                for e in entidades
            ],
            hide_index=True,
            width="stretch",
        )
        actual = next(r for r in resumen if r["registro"] == registro)
        fuente(actual["url_origen"], actual["fecha_descarga"])


# --- Recursos ante el Tribunal (D-029) ---
with pestanas[5]:
    st.info(textos.AVISO_RECURSOS, icon=":material/info:")
    recursos = df.resumen_recursos(con)
    if not recursos:
        st.write(
            "Los recursos ante el Tribunal no están disponibles todavía en esta versión de la web."
        )
    else:
        st.markdown(
            f"Resoluciones del Tribunal entre el {min(r['desde'] for r in recursos)} y el "
            f"{max(r['hasta'] for r in recursos)} sobre consejerías, hospitales, otros "
            "poderes adjudicadores y universidades de la Comunidad, según el acto recurrido."
        )
        st.dataframe(
            [
                {
                    "Acto recurrido": r["acto_recurrido"],
                    "Resoluciones": r["n"],
                    "% estimadas": textos.porcentaje(r["estimadas"] / r["n"]),
                    "Estimadas (total o parcialmente)": r["estimadas"],
                    "Desestimadas": r["desestimadas"],
                    "Inadmitidas": r["inadmitidas"],
                }
                for r in recursos
            ],
            hide_index=True,
            width="stretch",
        )
        st.caption(
            "Algunas resoluciones resuelven a la vez varios actos y no se cuentan aquí. El "
            "buscador del Tribunal no da el organismo de cada resolución, así que solo unas "
            "pocas se pueden enlazar con su contrato (aparecen en la ficha del contrato)."
        )
        fuente(
            "https://www.comunidad.madrid/tacp/busquedaresoluciones",
            recursos[0]["fecha_descarga"],
            "Tribunal Administrativo de Contratación Pública de la Comunidad de Madrid",
        )
