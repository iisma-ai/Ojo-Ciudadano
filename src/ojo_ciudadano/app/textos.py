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
    "Estado). Contexto presupuestario y organizativo: [Catálogo de Datos Abiertos]"
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
    "de contrato (si ese mercado tiene al menos 10 contratos y 3 empresas). Puede deberse a "
    "exclusividad técnica o a un mercado pequeño.",
    "R-05": "Las modificaciones suman más del 20 % del importe adjudicado. La ley admite otras "
    "modificaciones justificadas; las prórrogas no se cuentan.",
    "R-06": "La baja es cuánto rebaja la oferta ganadora el presupuesto de licitación "
    "(1 − adjudicado / presupuesto). Se activa si es nula o casi nula (≤ 0,5 %), lo que puede "
    "indicar poca competencia, o si es muy alta (≥ 50 %), lo que puede comprometer la "
    "ejecución. Solo en procedimientos abiertos, abiertos simplificados y restringidos con "
    "al menos dos ofertas. Incluye las adjudicaciones por encima del presupuesto.",
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
        f"- **{i} · {NOMBRES_INDICADOR[i]}**: {AYUDA_INDICADOR[i]}" for i in NOMBRES_INDICADOR
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
    menor · obras»."""
    fuente, _, resto = grupo.partition(" · ")
    resto = resto.replace("menor", "contrato menor", 1)
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
    "este tipo de contrato. Puede deberse a un proveedor único o a un mercado pequeño.",
    "R-05": "Después de adjudicarlo, se añadieron modificaciones por más del 20 % del importe "
    "(sin contar prórrogas). La ley permite modificaciones justificadas.",
    "R-06": "La empresa ganó rebajando casi nada el precio de salida (0,5 % o menos, o incluso "
    "por encima), o rebajándolo a la mitad o más. Las dos cosas son poco habituales con varias "
    "ofertas.",
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
    "puntuacion": "Mayor puntuación primero",
    "senales": "Más señales primero",
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
