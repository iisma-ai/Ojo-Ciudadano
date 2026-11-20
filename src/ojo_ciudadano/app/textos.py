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
    "(https://contratos-publicos.comunidad.madrid/contratos) y "
    "[Plataforma de Contratación del Sector Público](https://contrataciondelestado.es). "
    "Indicadores y puntuaciones: cálculo propio de Ojo Ciudadano."
)

PIE = (
    "Proyecto independiente, sin vinculación con la Comunidad de Madrid ni con la Plataforma "
    "de Contratación del Sector Público, y no patrocinado por ellas. Los datos oficiales se "
    "reutilizan citando su fuente y sin alterar su sentido. " + FUENTES
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
