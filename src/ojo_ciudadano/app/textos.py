"""Textos fijos de la interfaz. Lenguaje no acusatorio (docs/07-riesgos.md)."""

AVISO_CORTO = (
    "Las alertas son **indicadores de riesgo** calculados con reglas públicas: señalan "
    "contratos que merecen revisión y **no prueban ninguna irregularidad**."
)

AVISO = (
    "**Qué significa una alerta.** Es un *indicador de riesgo*: una señal calculada con una "
    "regla pública sobre datos oficiales que indica que un contrato merece revisión. "
    "**No prueba ninguna irregularidad** y puede tener explicaciones legítimas (por ejemplo, "
    "exclusividad técnica o mercados pequeños). Los indicadores y la puntuación son cálculo "
    "propio de esta plataforma, no datos de la Administración y pueden contener errores. "
    "Un contrato sin alertas tampoco queda avalado. Cada alerta indica qué regla y qué valor "
    "la activó y enlaza al expediente oficial. Con pocos indicadores aplicables la puntuación "
    "es menos fiable y menos comparable. Reglas completas en `docs/04-indicadores-riesgo.md`."
)

FUENTES = (
    "Fuentes: [Portal de la Contratación Pública de la Comunidad de Madrid]"
    "(https://contratos-publicos.comunidad.madrid/contratos), "
    "[Plataforma de Contratación del Sector Público](https://contrataciondelestado.es) y "
    "[Base de Datos Nacional de Subvenciones]"
    "(https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones) "
    "(origen de los datos de subvenciones: Intervención General de la Administración del "
    "Estado). Recursos especiales: [Tribunal Administrativo de Contratación Pública de la "
    "Comunidad de Madrid](https://www.comunidad.madrid/tacp/busquedaresoluciones). Entes del "
    "sector público: [Inventario de Entes del Sector Público (INVENTE)]"
    "(https://www.pap.hacienda.gob.es/invente2/pagMenuPrincipalV2.aspx), Intervención General "
    "de la Administración del Estado. Contexto presupuestario y organizativo: "
    "[Catálogo de Datos Abiertos]"
    "(https://datos.comunidad.madrid) y [Portal de Transparencia]"
    "(https://www.comunidad.madrid/transparencia) de la Comunidad de Madrid. "
    "Indicadores y puntuaciones: cálculo propio de Ojo Ciudadano."
)

PIE = (
    "Proyecto independiente, sin vinculación con la Comunidad de Madrid, la Plataforma de "
    "Contratación del Sector Público ni la Intervención General de la Administración del "
    "Estado, y no patrocinado ni apoyado por ellas. Los datos oficiales se reutilizan citando "
    "su fuente y fecha de descarga y sin alterar su sentido. Ojo Ciudadano seudonimiza los "
    "datos de personas físicas: no guarda su nombre ni su NIF, los sustituye por un código "
    "interno y solo los muestra agregados. " + FUENTES
)

# Umbral de cada indicador, para que el valor se pueda interpretar.
UMBRALES = {
    "R-04": "umbral: cuota superior al 50 %",
    "R-05": "referencia de la regla: 20 % del importe adjudicado",
    "R-06": "se activa con baja ≤ 0,5 % o ≥ 50 %",
}


def formatear_valor(indicador: str, valor: float | None) -> str:
    """Valor del indicador con unidad y, si existe, su umbral."""
    if valor is None:
        return "—"
    if indicador in ("R-04", "R-05", "R-06"):
        texto = f"{valor:.1%}".replace(".", ",")
        return f"{texto}; {UMBRALES[indicador]}"
    return format(valor, ".3g").replace(".", ",")


def encabezado_contrato(titulo: str, n_activados: int, n_aplicables: int, organo: str) -> str:
    """Encabezado sin porcentaje suelto, que se leería como probabilidad de irregularidad."""
    return f"{n_activados} de {n_aplicables} señales · {titulo[:90]} · {organo}"


NOMBRES_INDICADOR = {
    "R-01": "Licitador único",
    "R-02": "Procedimiento sin publicidad",
    "R-03": "Posible fraccionamiento",
    "R-04": "Concentración de proveedor",
    "R-05": "Modificaciones sobre el importe adjudicado",
    "R-06": "Baja nula o muy alta (umbrales en el detalle)",
}

# Qué mide cada indicador, en una frase, y por qué puede tener explicación legítima.
AYUDA_INDICADOR = {
    "R-01": "Licitación abierta o restringida que recibió una sola oferta. Puede deberse a "
    "un mercado con pocas empresas o a requisitos técnicos muy específicos.",
    "R-02": "Adjudicado sin publicidad (negociado sin publicidad u «otro procedimiento» del "
    "portal regional). La ley lo permite en supuestos concretos, como las emergencias.",
    "R-03": "Dos o más contratos menores al mismo adjudicatario, órgano y tipo de contrato "
    "que en 12 meses suman, con IVA, más de 18.150 € (servicios y suministros) o 48.400 € "
    "(obras). Solo cuentan los menores de al menos 6.050 € / 16.133,33 €. Pueden ser "
    "necesidades distintas.",
    "R-04": "Un adjudicatario recibe más del 50 % del importe que un órgano adjudica en un tipo "
    "de contrato y, en la Plataforma de Contratación, en la misma división CPV (si ese mercado "
    "tiene al menos 10 contratos y 3 adjudicatarios). Los entes del sector público no la "
    "activan. Puede deberse a exclusividad técnica o a un mercado pequeño.",
    "R-05": "Las modificaciones suman más del 20 % del importe adjudicado. La ley admite otras "
    "modificaciones justificadas; las prórrogas no se cuentan.",
    "R-06": "La baja es cuánto rebaja la oferta ganadora el presupuesto de licitación "
    "(1 − adjudicado / presupuesto). Se activa si es nula o casi nula (≤ 0,5 %), lo que puede "
    "indicar poca competencia, o si es muy alta (≥ 50 %), lo que puede comprometer la "
    "ejecución. Solo en procedimientos abiertos, abiertos simplificados y restringidos con "
    "al menos dos ofertas. Incluye las adjudicaciones por encima del presupuesto.",
}

# Referencias externas para leer una señal frecuente sin tomarla por anómala
# (docs/13-fuentes-externas.md, X-04). Se miden de forma algo distinta que aquí.
CONTEXTO_SENAL = {
    "R-01": "Como referencia: en 2025, el 45,5 % de los lotes que adjudicaron las comunidades "
    "autónomas recibió una sola oferta ([OIReScon, Informe Anual de Supervisión 2026]"
    "(https://www.hacienda.gob.es/rsc/oirescon/informe-anual-supervision-2026/"
    "ias2026-modulo1.pdf), tabla 77), y en la Unión Europea la media fue del 28 % en 2024 "
    "([Comisión Europea, Single Market Scoreboard]"
    "(https://single-market-scoreboard.ec.europa.eu/countries/spain_en)). Esas cifras se "
    "cuentan de otra manera (por lotes, o solo contratos grandes) y aquí se cuentan contratos "
    "de la Comunidad de Madrid, así que sirven como orden de magnitud, no para comparar al "
    "decimal ni para concluir que un contrato con una sola oferta sea anómalo (fuentes "
    "consultadas el 23-nov-2026).",
}

NOMBRES_FUENTE = {
    "placsp": "Plataforma de Contratación del Sector Público",
    "portal_cm": "Portal de la Contratación Pública de la Comunidad de Madrid",
    "bdns": "Base de Datos Nacional de Subvenciones",
    "ckan_cm": "Catálogo de Datos Abiertos de la Comunidad de Madrid",
    "transparencia_cm": "Portal de Transparencia de la Comunidad de Madrid",
}


def lista_indicadores() -> str:
    """Explicación de cada indicador en Markdown, para el apartado de metodología."""
    return "\n".join(
        f"- **{i} · {NOMBRES_INDICADOR[i]}**: "
        + " ".join(filter(None, [AYUDA_INDICADOR[i], CONTEXTO_SENAL.get(i)]))
        for i in NOMBRES_INDICADOR
    )


def fechas_descarga(fechas: list[dict]) -> str:
    """«Datos descargados: <fuente> el <fecha>; …», una fecha por fuente."""
    if not fechas:
        return ""
    partes = [f"{NOMBRES_FUENTE.get(f['fuente'], f['fuente'])} el {f['fecha']}" for f in fechas]
    return "Datos descargados: " + "; ".join(partes) + "."


AVISO_ATIPICOS = (
    "**Qué es un contrato atípico.** Un modelo de aprendizaje automático no supervisado "
    "(Isolation Forest) compara cada contrato con otros similares (misma fuente, tipo de "
    "contrato y si es menor o licitación) y marca el 1 % que más se aleja de ellos en importe, "
    "número de ofertas, baja, modificaciones, cuota del adjudicatario en el órgano o número de "
    "contratos menores. **Atípico no significa irregular**: un contrato puede ser poco habitual "
    "por razones legítimas (tamaño, urgencia, un único proveedor posible). Es una señal "
    "experimental, aparte de los indicadores de riesgo, que **no suma a la puntuación** y "
    "puede contener errores. Que un contrato no aparezca aquí no lo avala: los grupos con "
    "menos de 50 contratos no se analizan. Método completo en "
    "`docs/04-indicadores-riesgo.md` (D-021)."
)


def nombre_grupo(grupo: str) -> str:
    """«placsp · menor · obras» → «Plataforma de Contratación del Sector Público · contrato
    menor · obras»; «… · CPV 33» → «… · división CPV 33» (D-036)."""
    fuente, _, resto = grupo.partition(" · ")
    resto = resto.replace("menor", "contrato menor", 1).replace("· CPV ", "· división CPV ")
    return f"{NOMBRES_FUENTE.get(fuente, fuente)} · {resto}"


AVISO_MENORES_RECIENTES = (
    "Los contratos menores se publican con retraso: la ley pide publicarlos al menos cada "
    "trimestre (art. 63.4 de la Ley 9/2017 de Contratos del Sector Público). Los meses más "
    "recientes de 2026 están incompletos, así que una caída en 2026 no indica que se "
    "contrate menos."
)


# --- Lenguaje claro (D-023, docs/11-accesibilidad.md) ---

PRESENTACION = (
    "Consulta en qué gasta la Comunidad de Madrid en contratos y subvenciones, y qué contratos "
    "conviene revisar."
)

NOTA_SENAL = (
    "Una señal no demuestra nada irregular: indica dónde merece la pena mirar con más detalle "
    "y puede tener una explicación legítima. Es un cálculo nuestro, puede tener errores, y un "
    "contrato sin señales tampoco queda avalado."
)

# Nombre corto de cada señal, para etiquetas y filtros.
SENAL_CORTA = {
    "R-01": "Una sola oferta",
    "R-02": "Sin anuncio público",
    "R-03": "Muchos contratos menores",
    "R-04": "Una empresa concentra el gasto",
    "R-05": "Modificaciones de más del 20 %",
    "R-06": "Rebaja nula o muy alta",
}

# Qué se comprueba, en una frase que se entienda sin saber de contratación.
SENAL_FRASE = {
    "R-01": "Al concurso (o a alguno de sus lotes) solo se presentó una empresa, así que no "
    "hubo ofertas con las que comparar. Puede pasar en mercados con pocas empresas.",
    "R-02": "El contrato se adjudicó sin anuncio público previo, o con un procedimiento que el "
    "portal no detalla. La ley lo permite en casos concretos, como las emergencias.",
    "R-03": "El mismo organismo dio a la misma empresa varios contratos menores del mismo tipo "
    "que, sumados en 12 meses, pasan del importe máximo de un contrato menor. Puede ser normal "
    "si son compras distintas.",
    "R-04": "Una sola empresa recibe más de la mitad del importe que el organismo adjudica en "
    "este tipo de contrato (en la Plataforma de Contratación, para el mismo tipo de objeto). "
    "Puede deberse a un proveedor único o a un mercado pequeño.",
    "R-05": "Después de adjudicarlo, se añadieron modificaciones por más del 20 % del importe "
    "(sin contar prórrogas). La ley permite modificaciones justificadas.",
    "R-06": "La empresa ganó rebajando casi nada el precio de salida (0,5 % o menos, o incluso "
    "por encima), o rebajándolo a la mitad o más. Las dos cosas son poco habituales con varias "
    "ofertas.",
}

# Qué tienen los contratos de la cifra «X de cada 100 contratos …» de la portada (D-039). El
# «de cada 100» se cuenta sobre los contratos en los que se pudo comprobar la señal.
SENAL_DE_100 = {
    "R-01": "tienen una sola oferta",
    "R-02": "se adjudicaron sin anuncio público",
    "R-03": "son menores a la misma empresa que, juntos, pasan del máximo de un contrato menor",
    "R-04": "son de una empresa que concentra el gasto del organismo",
    "R-05": "tienen modificaciones de más del 20 %",
    "R-06": "tienen una rebaja nula o muy alta",
}

ICONO_SENAL = {
    "R-01": ":material/person:",
    "R-02": ":material/visibility_off:",
    "R-03": ":material/stacks:",
    "R-04": ":material/donut_large:",
    "R-05": ":material/trending_up:",
    "R-06": ":material/percent:",
}


def euros(valor: float | None, iva: str = "") -> str:
    """Importe legible: «1,2 millones €», «45.300 €». `iva`: «con IVA» o «sin IVA»."""
    if valor is None:
        return "sin dato"
    if abs(valor) >= 1_000_000_000:
        texto = f"{valor / 1_000_000_000:.1f} mil millones €".replace(".", ",")
    elif abs(valor) >= 1_000_000:
        texto = f"{valor / 1_000_000:.1f} millones €".replace(".", ",")
    else:
        texto = f"{valor:,.0f} €".replace(",", ".")
    return f"{texto} {iva}".strip()


def numero(valor: int | float) -> str:
    """Número con separador de miles español; millones abreviados."""
    if valor >= 1_000_000:
        cifra = f"{valor / 1_000_000:.2f}".replace(".", ",").rstrip("0").rstrip(",")
        return cifra + (" millón" if cifra == "1" else " millones")
    return f"{valor:,.0f}".replace(",", ".")


def iva_fuente(fuente: str) -> str:
    return "sin IVA" if fuente == "placsp" else "con IVA"


def porcentaje(valor: float, decimales: int = 0) -> str:
    """Proporción como porcentaje en español: 0,394 → «39 %» o «39,4 %»."""
    return f"{100 * valor:.{decimales}f} %".replace(".", ",")


# Nombre llano de cada procedimiento de adjudicación (ficha de organismo).
PROCEDIMIENTO_LLANO = {
    "Contrato menor": "Contrato menor (importe pequeño, sin concurso)",
    "Contratos Menores": "Contrato menor (importe pequeño, sin concurso)",
    "Abierto": "Concurso abierto",
    "Abierto simplificado": "Concurso abierto simplificado",
    "Negociado sin publicidad": "Negociado sin anuncio público",
    "Negociado con publicidad": "Negociado con anuncio público",
    "Otro procedimiento": "Otra vía (sin detallar en el portal)",
    "Restringido": "Concurso restringido (por invitación)",
    "Derivado de acuerdo marco": "Dentro de un acuerdo marco",
    "Basado en un sistema dinámico de adquisición": "Sistema dinámico de compra",
    "Licitación con negociación": "Concurso con negociación",
    "No indicado": "Sin indicar",
    "Otros": "Otras vías",
    "Normas internas": "Normas internas de la entidad",
}


# Definiciones cortas de los términos que no se pueden evitar (A-09). Se muestran en la ayuda
# («?») junto al término.
GLOSARIO = {
    "organismo": "Consejería, hospital, empresa pública u otra entidad de la Comunidad de "
    "Madrid que firma contratos (en la ley, «órgano de contratación»).",
    "adjudicataria": "Empresa o entidad que gana un contrato.",
    "contrato_menor": "Contrato de menos de 15.000 € (40.000 € en obras), sin IVA, que se puede "
    "dar directamente a una empresa sin concurso.",
    "licitacion": "Concurso público en el que varias empresas pueden presentar ofertas.",
    "fuentes": "Los contratos vienen de dos fuentes oficiales: la Plataforma de Contratación "
    "del Sector Público da los importes sin IVA y el portal de la Comunidad de Madrid, con IVA. "
    "Por eso no se suman. Las subvenciones vienen de la Base de Datos Nacional de Subvenciones.",
    "tipo_contrato": "Qué se contrata: obras, servicios o suministros (compra de productos), "
    "entre otros.",
    "senal": "Indicador calculado con una regla pública que señala un contrato que merece "
    "revisión. No demuestra nada irregular.",
}


# Contexto presupuestario y organizativo (D-024).
AVISO_CONTEXTO = (
    "Estas cifras vienen de fuentes distintas de las de los contratos y **no se pueden restar "
    "ni cruzar partida a partida**: los datos oficiales no dicen qué parte del presupuesto "
    "de una consejería acabó en cada contrato (docs/02-fuentes-datos.md). Sirven para dar "
    "escala. No son indicadores de riesgo."
)
AVISO_REGISTROS = (
    "Que una empresa figure en uno de estos registros **no es una señal de riesgo ni dice "
    "nada sobre cómo contrata**: solo informa de en qué listados oficiales de la Comunidad "
    "aparece su NIF."
)
AVISO_CONVENIOS = (
    "Listado oficial de convenios vigentes. Los firmantes vienen por nombre, sin NIF, y solo "
    "se muestran los que son entidades. El texto de financiación es el de la fuente: no se "
    "suma porque mezcla importes anuales, máximos y de varios años."
)

# Filtros de contratos atípicos y de contratos a revisar.
ORDEN_ATIPICOS = {
    "mas_atipico": "Más alejados de sus pares primero",
    "menos_atipico": "Menos alejados primero",
    "importe_desc": "Mayor importe primero",
    "importe_asc": "Menor importe primero",
}
ORDEN_ALERTAS = {
    "senales": "Más señales primero",
    "puntuacion": "Mayor puntuación primero",
    "importe_desc": "Mayor importe primero",
    "importe_asc": "Menor importe primero",
    "reciente": "Más recientes primero",
}
AYUDA_POSIBLES_ERRORES = (
    "Son contratos atípicos cuyos valores no tienen sentido, por ejemplo adjudicados por más "
    "del doble del presupuesto, con modificaciones de más de cinco veces el importe o con un "
    "importe de menos de 1 €. Lo más probable es que haya un error al introducir los datos en "
    "la fuente, no un contrato realmente atípico. No se puede asegurar sin ver el expediente."
)


def aviso_errores_ocultos(n: int) -> str:
    return (
        f"Se ocultan {numero(n)} contratos cuyos valores parecen un error al introducir los "
        "datos en la fuente (por ejemplo, adjudicados por más del doble del presupuesto). "
        "Activa «Mostrar posibles errores de datos» para verlos."
    )


def millones(valor: float | None) -> str:
    """Importe corto para cifras grandes: «33.286 M€» (millones de euros); menos de un millón,
    en euros."""
    if valor is None:
        return "sin dato"
    if abs(valor) >= 1_000_000:
        return f"{valor / 1_000_000:,.0f} M€".replace(",", ".")
    return f"{valor:,.0f} €".replace(",", ".")


# --- Encargos, fondos europeos y recursos (D-027 a D-029) ---

AVISO_ENCARGOS = (
    "Un **encargo a medio propio** es un trabajo que un organismo asigna a una entidad pública "
    "que actúa como su medio propio (como Tragsa o Canal de Isabel II). La ley lo permite sin "
    "licitación cuando se cumplen los requisitos del art. 32 de la Ley 9/2017 de Contratos del "
    "Sector Público; no comprobamos esos requisitos. No es un contrato "
    "y no se le aplican las señales. Importes con IVA; el año es el de publicación en el portal."
)

NOMBRE_PLIEGO = {
    "pcap": "Pliego de cláusulas administrativas",
    "ppt": "Pliego de prescripciones técnicas",
}
# Qué buscar en el pliego para explicar cada señal (D-030, bloque B).
BUSCAR_EN_PLIEGO = {
    "R-01": "qué solvencia y qué criterios de adjudicación pide",
    "R-02": "qué supuesto alega para adjudicarlo sin publicidad",
    "R-05": "qué modificaciones prevé",
    "R-06": "cómo define las ofertas anormalmente bajas",
}


def pregunta_pliego(contrato_id: str, indicadores: list[str]) -> str:
    """Pregunta para el asistente sobre el pliego de un contrato, según sus señales."""
    temas = [BUSCAR_EN_PLIEGO[i] for i in indicadores if i in BUSCAR_EN_PLIEGO]
    if not temas:
        temas = ["cuál es su objeto y qué criterios de adjudicación fija"]
    return (
        f"Según su pliego, en el contrato {contrato_id}: {'; '.join(temas)}. "
        "Cita la página del pliego."
    )


AVISO_RECURSOS = (
    "Cualquier empresa interesada puede recurrir los pliegos, su exclusión o la adjudicación de "
    "un contrato ante el Tribunal Administrativo de Contratación Pública de la Comunidad de "
    "Madrid. **Presentar un recurso no es una señal.** Que el Tribunal lo estime solo dice que "
    "dio la razón al recurrente sobre ese acto; no es una señal sobre la empresa adjudicataria "
    "ni sobre el organismo."
)


# --- Títulos de contrato legibles (D-042) ---

# Fórmulas administrativas con las que empiezan muchos títulos y que no dicen nada del objeto.
_ENTRADAS_TITULO = (
    "el presente contrato tiene por objeto",
    "el presente contrato tiene por finalidad",
    "este contrato tiene por objeto",
    "el contrato tiene por objeto",
    "el objeto del contrato es",
    "procedimiento de adjudicación de",
    "procedimiento para la adjudicación de",
)


def titulo_limpio(titulo: str | None) -> str:
    """Título sin las fórmulas administrativas del principio ni comillas sueltas: «Este contrato
    tiene por objeto “La adquisición de vacunas…”» → «La adquisición de vacunas…». Si viene
    todo en mayúsculas, se pasa a frase normal."""
    texto = " ".join((titulo or "").split())
    cambiado = True
    while cambiado:
        cambiado = False
        texto = texto.strip(" :.,-\"'“”«»")
        for entrada in _ENTRADAS_TITULO:
            if texto.lower().startswith(entrada):
                texto = texto[len(entrada) :]
                cambiado = True
    if not texto:
        return (titulo or "").strip() or "Contrato sin título"
    if texto.isupper():  # todo en mayúsculas: a frase normal, que se lee mejor
        texto = texto.lower()
    return texto[0].upper() + texto[1:]
