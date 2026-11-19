-- R-06 · Baja anormal o nula
--
-- Definición (docs/04-indicadores-riesgo.md, D-019): diferencia entre el presupuesto base y el
-- importe adjudicado. Baja = 1 - adjudicado / presupuesto.
--   * Baja nula: baja <= 0,5 % (incluye adjudicar por encima del presupuesto). Con varias
--     ofertas, que nadie rebaje el precio sugiere poca competencia real.
--   * Baja extrema: baja >= 50 %. Riesgo de ejecución o de oferta no sostenible.
--
-- Cálculo por contrato:
--   * Aplicable: procedimiento abierto, abierto simplificado o restringido, con al menos dos
--     ofertas en todos sus adjudicatarios, todos los lotes resueltos (adjudicado o formalizado),
--     y presupuesto e importe adjudicado positivos de la misma base (sin IVA en PLACSP, con IVA
--     en el portal; nunca se comparan columnas de bases distintas).
--   * Activado: baja nula o baja extrema.
--   * Valor: la baja (0–1; negativa si se adjudica por encima del presupuesto).
--
-- Limitaciones: el presupuesto base y el importe adjudicado pueden no ser comparables si hay
-- lotes parciales, mejoras o revisiones de precio; las bajas extremas no siempre son anormales
-- (art. 149 LCSP las mide frente a las demás ofertas, que no tenemos). Si el contrato tiene
-- solo una oferta, el caso lo recoge R-01.
--
-- Decisiones: D-004, D-019.

WITH contratos AS (
    SELECT
        c.contrato_id,
        c.url_origen,
        any_value(CASE WHEN c.fuente = 'placsp' THEN c.presupuesto_sin_iva
                       ELSE c.presupuesto_con_iva END) AS presupuesto,
        sum(CASE WHEN c.fuente = 'placsp' THEN a.importe_sin_iva
                 ELSE a.importe_con_iva END) AS adjudicado,
        min(a.n_ofertas) AS min_ofertas,
        bool_and(a.resultado IS NULL OR a.resultado IN ('Adjudicado', 'Formalizado')) AS resuelto
    FROM contrato_unico AS c
    JOIN adjudicacion AS a USING (contrato_id)
    WHERE c.procedimiento IN ('Abierto', 'Abierto simplificado', 'Restringido')
      AND NOT c.es_menor
    GROUP BY c.contrato_id, c.url_origen
),

con_baja AS (
    SELECT *, round(1 - adjudicado / presupuesto, 6) AS baja  -- redondeo: que no decida el coma flotante
    FROM contratos
    WHERE resuelto AND min_ofertas >= 2 AND presupuesto > 0 AND adjudicado > 0
)

SELECT
    contrato_id,
    'R-06' AS indicador,
    TRUE AS aplicable,
    baja <= 0.005 OR baja >= 0.5 AS activado,
    baja AS valor,
    CASE
        WHEN baja <= 0.005 THEN 'Adjudicado sin baja sobre el presupuesto base ('
            || replace(CAST(round(100 * baja, 1) AS VARCHAR), '.', ',') || ' %) con '
            || min_ofertas || ' o más ofertas'
        WHEN baja >= 0.5 THEN 'Baja del ' || replace(CAST(round(100 * baja, 1) AS VARCHAR), '.', ',')
            || ' % sobre el presupuesto base'
    END AS motivo,
    url_origen
FROM con_baja
