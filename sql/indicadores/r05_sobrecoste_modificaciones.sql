-- R-05 · Sobrecoste por modificaciones
--
-- Definición (D-016): el importe de las modificaciones supera el 20 % del importe adjudicado.
-- El 20 % es el límite de la LCSP para las modificaciones previstas en el pliego (art. 204).
--
-- Cálculo por contrato:
--   * Aplicable: licitación (no menor) del portal regional con importe adjudicado mayor que
--     cero y con el dato de modificaciones publicado (aunque sea 0).
--   * Valor: modificaciones / importe adjudicado, sumando todos los adjudicatarios o lotes.
--   * Activado: las modificaciones superan el 20 % del adjudicado en más de 1 €. El margen
--     evita que el redondeo de céntimos active contratos que están justo en el 20 %, que
--     son muchos (es el máximo legal de las modificaciones previstas).
--   * Las prórrogas NO cuentan: suelen ser anualidades previstas en el pliego (mediana del
--     100 % del importe adjudicado). Se mencionan en el motivo como contexto.
--
-- Datos: adjudicacion.importe_con_iva e importe_modificaciones_con_iva del CSV del portal
-- regional (ambos con IVA). PLACSP no publica modificaciones.
-- Si la licitación también está en PLACSP, el resultado se asigna al contrato de PLACSP
-- (duplicado_de) para que la puntuación no la cuente dos veces; el enlace sigue siendo la
-- ficha del portal, que es donde están las modificaciones.
--
-- Limitaciones: el portal da el importe acumulado de las modificaciones, sin fecha ni motivo;
-- una modificación puede estar justificada (art. 205 LCSP). No mide sobrecostes que no se
-- tramitan como modificación (liquidación, revisiones de precios).
--
-- Decisiones: D-002, D-004, D-012, D-016.

WITH portal AS (
    SELECT
        coalesce(c.duplicado_de, c.contrato_id) AS contrato_id,
        c.url_origen,
        sum(a.importe_con_iva) AS adjudicado,
        sum(a.importe_modificaciones_con_iva) AS modificaciones,
        sum(coalesce(a.importe_prorrogas_con_iva, 0)) AS prorrogas
    FROM contrato AS c
    JOIN adjudicacion AS a USING (contrato_id)
    WHERE c.fuente = 'portal_cm'
      AND NOT c.es_menor
      AND a.importe_con_iva > 0
      AND a.importe_modificaciones_con_iva IS NOT NULL
    GROUP BY ALL
),

-- Por si dos fichas del portal apuntan al mismo contrato de PLACSP.
por_contrato AS (
    SELECT
        contrato_id,
        min(url_origen) AS url_origen,
        sum(adjudicado) AS adjudicado,
        sum(modificaciones) AS modificaciones,
        sum(prorrogas) AS prorrogas
    FROM portal
    GROUP BY contrato_id
)

SELECT
    contrato_id,
    'R-05' AS indicador,
    TRUE AS aplicable,
    modificaciones > 0.20 * adjudicado + 1 AS activado,
    modificaciones / adjudicado AS valor,
    CASE WHEN modificaciones > 0.20 * adjudicado + 1 THEN
        'Las modificaciones (' || euros(modificaciones) || ' € con IVA) suponen el '
        || replace(CAST(round(100 * modificaciones / adjudicado, 1) AS VARCHAR), '.', ',')
        || ' % del importe adjudicado (' || euros(adjudicado) || ' € con IVA); referencia: '
        || '20 %, límite de las modificaciones previstas en la LCSP'
        || CASE WHEN prorrogas > 0
            THEN '. Prórrogas, no incluidas en el cálculo: ' || euros(prorrogas) || ' €'
            ELSE ''
        END
    END AS motivo,
    url_origen
FROM por_contrato
