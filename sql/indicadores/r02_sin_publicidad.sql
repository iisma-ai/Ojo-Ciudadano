-- R-02 · Procedimiento sin publicidad
--
-- Definición (docs/04-indicadores-riesgo.md): peso de los negociados sin publicidad y de las
-- emergencias en el gasto de cada órgano. Este fichero da la señal por contrato; el peso por
-- órgano se calcula al agregar la puntuación.
--
-- Cálculo por contrato (contrato_unico, sin menores):
--   * Aplicable: contrato con procedimiento conocido. No aplica a los contratos derivados de
--     un acuerdo marco o de un sistema dinámico de adquisición: la concurrencia se dio al
--     licitar el acuerdo, no en el contrato derivado.
--   * Activado si:
--       - el procedimiento es «Negociado sin publicidad» en PLACSP o en el portal, o
--       - el portal regional lo publica en su lista «Contratos adjudicados por procedimientos
--         sin publicidad» con procedimiento «Otro procedimiento», que es donde aparecen las
--         tramitaciones de emergencia.
--     Si la licitación está en las dos fuentes se mira también la ficha del portal (duplicado_de).
--   * Valor: NULL. La señal es sí o no; el importe se pondera al agregar por órgano.
--
-- Limitaciones: el negociado sin publicidad y la emergencia son legales cuando se dan sus
-- causas (exclusividad, urgencia imprevisible…); los datos no dicen cuál se alegó. «Otro
-- procedimiento» también incluye casos que no son emergencias. Las emergencias de PLACSP que
-- no estén en el portal no se detectan.
--
-- Decisiones: D-002, D-004, D-012.

WITH ficha_portal AS (
    -- Ficha del portal de cada contrato único: la suya o la que apunta a él.
    SELECT coalesce(duplicado_de, contrato_id) AS contrato_id,
           any_value(procedimiento) AS procedimiento,
           any_value(tipo_publicacion) AS tipo_publicacion
    FROM contrato
    WHERE fuente = 'portal_cm' AND NOT es_menor
    GROUP BY 1
),

contratos AS (
    SELECT
        c.contrato_id,
        c.url_origen,
        c.procedimiento,
        p.procedimiento AS procedimiento_portal,
        p.tipo_publicacion = 'Contratos adjudicados por procedimientos sin publicidad'
            AS en_lista_sin_publicidad
    FROM contrato_unico AS c
    LEFT JOIN ficha_portal AS p USING (contrato_id)
    WHERE NOT c.es_menor
      AND c.procedimiento IS NOT NULL
      AND c.procedimiento NOT IN (
          'Derivado de acuerdo marco', 'Basado en un sistema dinámico de adquisición'
      )
),

senales AS (
    SELECT
        *,
        'Negociado sin publicidad' IN (procedimiento, coalesce(procedimiento_portal, ''))
            AS negociado,
        coalesce(en_lista_sin_publicidad AND procedimiento_portal = 'Otro procedimiento', FALSE)
            AS otro_sin_publicidad
    FROM contratos
)

SELECT
    contrato_id,
    'R-02' AS indicador,
    TRUE AS aplicable,
    negociado OR otro_sin_publicidad AS activado,
    CAST(NULL AS DOUBLE) AS valor,
    CASE
        WHEN negociado THEN 'Adjudicado por procedimiento negociado sin publicidad'
        WHEN otro_sin_publicidad THEN 'Adjudicado sin publicidad: el portal regional lo '
            || 'clasifica como «otro procedimiento» (incluye las tramitaciones de emergencia)'
    END AS motivo,
    url_origen
FROM senales
