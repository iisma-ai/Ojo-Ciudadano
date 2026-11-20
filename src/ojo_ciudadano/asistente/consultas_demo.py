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
    CASE WHEN d.tipo_persona IN ('juridica', 'ute') THEN coalesce(d.nombre, d.adjudicatario_id)
         ELSE 'Personas físicas o sin identificar (agregadas)' END AS adjudicatario,
    CASE WHEN d.tipo_persona IN ('juridica', 'ute') THEN d.nif END AS nif,
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
        "tienen consejería en la fuente. Las personas físicas y los adjudicatarios cuyo NIF "
        "no se reconoce como de empresa española se muestran agregados."
    ),
)

SIN_PUBLICIDAD_POR_ORGANO = ConsultaDemo(
    pregunta=(
        "¿Qué órganos adjudican más por negociado sin publicidad u otros procedimientos "
        "(R-02), en proporción a su gasto?"
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
    CASE c.fuente WHEN 'placsp' THEN 'Plataforma de Contratación del Sector Público'
         ELSE 'Portal de la Contratación Pública de la Comunidad de Madrid' END AS fuente,
    CASE c.fuente WHEN 'placsp' THEN 'sin IVA' ELSE 'con IVA' END AS base_importe,
    count(*) AS n_contratos,
    count_if(r.activado) AS n_alerta_r02,
    sum(i.importe) AS importe_total,
    coalesce(sum(i.importe) FILTER (WHERE r.activado), 0) AS importe_alerta_r02,
    coalesce(sum(i.importe) FILTER (WHERE r.activado), 0) / sum(i.importe)
        AS proporcion_importe_alerta_r02,
    max(c.fecha_descarga) AS fecha_descarga
FROM indicador_resultado AS r
JOIN contrato_unico AS c USING (contrato_id)
JOIN organo AS o USING (organo_id)
JOIN importe AS i USING (contrato_id)
WHERE r.indicador = 'R-02' AND i.importe > 0
GROUP BY ALL
HAVING count(*) >= 20
ORDER BY proporcion_importe_alerta_r02 DESC
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
    pregunta=(
        "Enséñame los contratos en los que las modificaciones pesan más sobre el importe "
        "adjudicado."
    ),
    parametros=(),
    sql="""
SELECT
    c.titulo,
    o.nombre AS organo,
    r.valor AS modificaciones_sobre_adjudicado,
    r.activado AS supera_referencia_20,
    r.valor > 10 AS importe_a_comprobar,
    r.motivo,
    'Portal de la Contratación Pública de la Comunidad de Madrid' AS fuente,
    c.fecha_descarga,
    r.url_origen
FROM indicador_resultado AS r
JOIN contrato_unico AS c USING (contrato_id)
JOIN organo AS o USING (organo_id)
WHERE r.indicador = 'R-05' AND r.valor > 0
ORDER BY r.valor > 10, r.valor DESC
LIMIT 20
""",
    nota=(
        "Contratos del portal regional ordenados por el peso de sus modificaciones sobre el "
        "importe adjudicado (indicador R-05). Las prórrogas aparecen en el motivo pero no "
        "cuentan: suelen ser anualidades previstas en el pliego (D-016). Superar el 20 % no "
        "implica por sí solo un incumplimiento. PLACSP no publica modificaciones. Los porcentajes "
        "de más del 1.000 % aparecen al final, marcados en «importe_a_comprobar»: "
        "probablemente son un error del importe publicado, no un aumento real."
    ),
)

RECIBIDO_POR_EMPRESA = ConsultaDemo(
    pregunta="¿Qué ha recibido esta empresa de la Comunidad entre contratos y subvenciones?",
    parametros=("empresa",),
    sql="""
WITH empresas AS (
    SELECT adjudicatario_id, nombre, nif
    FROM adjudicatario
    WHERE tipo_persona IN ('juridica', 'ute')
      AND (nif = upper($empresa) OR nombre ILIKE '%' || $empresa || '%')
),
contratos AS (
    SELECT
        e.nombre AS entidad,
        e.nif,
        CASE c.fuente WHEN 'placsp' THEN 'Plataforma de Contratación del Sector Público'
             ELSE 'Portal de la Contratación Pública de la Comunidad de Madrid' END AS fuente,
        'contratos' AS tipo,
        year(coalesce(c.fecha_contrato, a.fecha_formalizacion, c.fecha_fin_plazo)) AS anio,
        count(DISTINCT c.contrato_id) AS n_contratos_o_concesiones,
        count(DISTINCT c.contrato_id) FILTER (WHERE p.n_activados > 0)
            AS n_con_indicadores_activados,
        sum(a.importe_sin_iva) AS importe_sin_iva,
        sum(a.importe_con_iva) AS importe_con_iva,
        max(c.fecha_descarga) AS fecha_descarga,
        CASE c.fuente WHEN 'placsp' THEN 'https://contrataciondelestado.es'
             ELSE 'https://contratos-publicos.comunidad.madrid/contratos' END AS url_origen
    FROM empresas AS e
    JOIN adjudicacion AS a USING (adjudicatario_id)
    JOIN contrato_unico AS c USING (contrato_id)
    LEFT JOIN puntuacion_contrato AS p USING (contrato_id)
    GROUP BY ALL
),
subvenciones AS (
    SELECT
        e.nombre AS entidad,
        e.nif,
        'Base de Datos Nacional de Subvenciones' AS fuente,
        'subvenciones' AS tipo,
        year(s.fecha_concesion) AS anio,
        count(*) AS n_contratos_o_concesiones,
        sum(s.importe) AS importe_concedido,
        max(s.fecha_descarga) AS fecha_descarga,
        'https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones' AS url_origen
    FROM empresas AS e
    JOIN concesion AS s ON s.beneficiario_id = e.adjudicatario_id
    GROUP BY ALL
)
SELECT * FROM (
    SELECT * FROM contratos
    UNION ALL BY NAME
    SELECT * FROM subvenciones
)
WHERE anio IS NULL OR anio BETWEEN 2023 AND 2026
ORDER BY entidad, tipo, fuente, anio
LIMIT 100
""",
    nota=(
        "Importes adjudicados (contratos) y concedidos (subvenciones) a la entidad, por fuente "
        "y año, de 2023 a 2026 (más los contratos sin "
        "fecha en la fuente). Contratos adjudicados: sin IVA en la "
        "Plataforma de Contratación y con IVA en el portal regional. Subvenciones: importe "
        "concedido según la Base de Datos Nacional de Subvenciones. Son bases distintas y no "
        "se suman entre sí. El detalle de cada contrato está en la ficha de la entidad y en el "
        "portal de origen; el de cada concesión, en la ficha de su convocatoria en la BDNS. Solo "
        "se buscan personas jurídicas españolas (empresas, entidades públicas y asociaciones) y "
        "UTE: no hay fichas de personas físicas ni de adjudicatarios cuyo NIF no se puede "
        "verificar."
    ),
)

CONSULTAS_DEMO = [
    MENORES_POR_CONSEJERIA,
    SIN_PUBLICIDAD_POR_ORGANO,
    SOBRECOSTE_MODIFICACIONES,
    RECIBIDO_POR_EMPRESA,
]
