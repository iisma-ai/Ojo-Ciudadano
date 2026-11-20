"""Consultas verificadas para las 4 preguntas de demo (docs/05-asistente.md).

Sirven para tres cosas: ejemplos para el modelo cuando se conecte (D-010), respuestas
cacheadas si el modelo falla en la demo (plan de contingencia) y casos de prueba. Todas pasan
por el mismo validador que el SQL que escriba el modelo.

Reglas comunes: no se suman importes con y sin IVA (P-10), las personas físicas solo
aparecen agregadas (D-007) y cada fila lleva la fuente o el enlace al expediente.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ConsultaDemo:
    pregunta: str
    sql: str
    parametros: tuple[str, ...]  # nombres de los $parámetros que necesita
    nota: str  # qué responde exactamente y qué no, para mostrarlo con la respuesta


MENORES_POR_CONSEJERIA = ConsultaDemo(
    pregunta=(
        "¿Qué empresas han recibido más contratos menores de una consejería concreta en los "
        "últimos dos años?"
    ),
    parametros=("consejeria",),
    sql="""
WITH ultima AS (
    SELECT max(fecha_contrato) AS fecha FROM contrato_unico WHERE es_menor
)
SELECT
    CASE WHEN d.tipo_persona = 'fisica' THEN 'Personas físicas (agregadas)'
         ELSE coalesce(d.nombre, d.adjudicatario_id) END AS adjudicatario,
    CASE WHEN d.tipo_persona = 'fisica' THEN NULL ELSE d.nif END AS nif,
    count(DISTINCT c.contrato_id) AS n_contratos,
    sum(a.importe_con_iva) AS importe_con_iva,
    min(c.fecha_contrato) AS desde,
    max(c.fecha_contrato) AS hasta,
    'Portal de la Contratación Pública de la Comunidad de Madrid' AS fuente,
    max(c.fecha_descarga) AS fecha_descarga
FROM contrato_unico AS c
JOIN organo AS o USING (organo_id)
JOIN adjudicacion AS a USING (contrato_id)
JOIN adjudicatario AS d USING (adjudicatario_id)
CROSS JOIN ultima
WHERE c.es_menor
  AND o.consejeria ILIKE '%' || $consejeria || '%'
  AND c.fecha_contrato > ultima.fecha - INTERVAL 2 YEAR
GROUP BY 1, 2
ORDER BY n_contratos DESC, importe_con_iva DESC
LIMIT 20
""",
    nota=(
        "Contratos menores del portal regional (importes con IVA) de los órganos cuya "
        "consejería contiene el texto indicado, en los dos años anteriores al último contrato "
        "publicado. Las consejerías cambian de nombre entre legislaturas y 21 órganos no "
        "tienen consejería en la fuente. Las personas físicas se muestran agregadas."
    ),
)

SIN_PUBLICIDAD_POR_ORGANO = ConsultaDemo(
    pregunta=(
        "¿Qué órganos adjudican más por procedimientos sin publicidad, en proporción a su gasto?"
    ),
    parametros=(),
    sql="""
WITH importe AS (
    SELECT contrato_id,
           sum(coalesce(importe_sin_iva, importe_con_iva)) AS importe
    FROM adjudicacion
    GROUP BY contrato_id
)
SELECT
    o.nombre AS organo,
    c.fuente,
    CASE c.fuente WHEN 'placsp' THEN 'sin IVA' ELSE 'con IVA' END AS base_importe,
    count(*) AS n_contratos,
    count_if(r.activado) AS n_sin_publicidad,
    sum(i.importe) AS importe_total,
    coalesce(sum(i.importe) FILTER (WHERE r.activado), 0) AS importe_sin_publicidad,
    coalesce(sum(i.importe) FILTER (WHERE r.activado), 0) / sum(i.importe)
        AS proporcion_importe_sin_publicidad
FROM indicador_resultado AS r
JOIN contrato_unico AS c USING (contrato_id)
JOIN organo AS o USING (organo_id)
JOIN importe AS i USING (contrato_id)
WHERE r.indicador = 'R-02' AND i.importe > 0
GROUP BY ALL
HAVING count(*) >= 20
ORDER BY proporcion_importe_sin_publicidad DESC
LIMIT 20
""",
    nota=(
        "Proporción del importe adjudicado por negociado sin publicidad u «otro procedimiento» "
        "(indicador R-02) sobre el importe de los contratos no menores del órgano, por fuente "
        "para no mezclar importes con y sin IVA. Solo órganos con al menos 20 contratos. "
        "Estos procedimientos son legales en supuestos concretos (exclusividad, emergencia); "
        "los datos no dicen cuál se alegó."
    ),
)

SOBRECOSTE_MODIFICACIONES = ConsultaDemo(
    pregunta="Enséñame los contratos con mayor sobrecoste por modificaciones y prórrogas.",
    parametros=(),
    sql="""
SELECT
    c.titulo,
    o.nombre AS organo,
    r.valor AS modificaciones_sobre_adjudicado,
    r.activado AS supera_referencia_20,
    r.motivo,
    r.url_origen
FROM indicador_resultado AS r
JOIN contrato_unico AS c USING (contrato_id)
JOIN organo AS o USING (organo_id)
WHERE r.indicador = 'R-05' AND r.valor > 0
ORDER BY r.valor DESC
LIMIT 20
""",
    nota=(
        "Contratos del portal regional ordenados por el peso de sus modificaciones sobre el "
        "importe adjudicado (indicador R-05). Las prórrogas aparecen en el motivo pero no "
        "cuentan: suelen ser anualidades previstas en el pliego (D-016). Superar el 20 % no "
        "implica por sí solo un incumplimiento. PLACSP no publica modificaciones. Un porcentaje "
        "desmesurado (más del 1.000 %) suele deberse a un error en el importe publicado: "
        "compruébalo en la ficha oficial."
    ),
)

RECIBIDO_POR_EMPRESA = ConsultaDemo(
    pregunta="¿Qué ha recibido esta empresa de la Comunidad entre contratos y subvenciones?",
    parametros=("empresa",),
    sql="""
SELECT
    d.nombre AS empresa,
    d.nif,
    c.fuente,
    year(coalesce(c.fecha_contrato, a.fecha_formalizacion, c.fecha_fin_plazo)) AS anio,
    count(DISTINCT c.contrato_id) AS n_contratos,
    count(DISTINCT c.contrato_id) FILTER (WHERE p.n_activados > 0) AS n_con_alertas,
    sum(a.importe_sin_iva) AS importe_sin_iva,
    sum(a.importe_con_iva) AS importe_con_iva,
    max(c.fecha_descarga) AS fecha_descarga
FROM adjudicatario AS d
JOIN adjudicacion AS a USING (adjudicatario_id)
JOIN contrato_unico AS c USING (contrato_id)
LEFT JOIN puntuacion_contrato AS p USING (contrato_id)
WHERE d.tipo_persona <> 'fisica'
  AND (d.nif = upper($empresa) OR d.nombre ILIKE '%' || $empresa || '%')
GROUP BY ALL
ORDER BY empresa, fuente, anio
LIMIT 100
""",
    nota=(
        "Contratos adjudicados a la empresa por fuente y año: sin IVA en la Plataforma de "
        "Contratación y con IVA en el portal regional (no se suman). **Las subvenciones aún "
        "no están cargadas**, así que esta respuesta solo cubre contratos. No hay fichas de "
        "personas físicas."
    ),
)

CONSULTAS_DEMO = [
    MENORES_POR_CONSEJERIA,
    SIN_PUBLICIDAD_POR_ORGANO,
    SOBRECOSTE_MODIFICACIONES,
    RECIBIDO_POR_EMPRESA,
]
