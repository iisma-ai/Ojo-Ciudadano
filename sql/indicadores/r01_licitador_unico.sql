-- R-01 · Licitador único
--
-- Definición (docs/04-indicadores-riesgo.md): procedimiento abierto o restringido en el que
-- se recibió una sola oferta.
--
-- Cálculo por contrato:
--   * Aplicable: procedimiento abierto, abierto simplificado o restringido, con al menos un
--     lote o adjudicatario resuelto (adjudicado o formalizado) del que se publica el número
--     de ofertas. Los lotes desiertos o sin ofertas publicadas no cuentan.
--   * Activado: algún lote resuelto recibió exactamente una oferta.
--   * Valor: número de lotes resueltos con una sola oferta.
--
-- Datos: contrato.procedimiento y adjudicacion.n_ofertas. En PLACSP el número de ofertas viene
-- en el 100 % de los resultados; en el portal regional, en la columna «Nº de ofertas».
-- Se usa la vista contrato_unico para no contar dos veces las licitaciones que están en las
-- dos fuentes (cuenta la fila de PLACSP).
--
-- Limitaciones: no distingue causas legales de oferta única (exclusividad técnica); en un
-- procedimiento abierto esas causas no deberían darse, pero el dato no lo dice. En PLACSP,
-- 0 ofertas en un lote formalizado es un error de la fuente: ese lote no es aplicable.
--
-- Decisiones: D-002, D-004, D-012.

WITH lotes AS (
    SELECT
        c.contrato_id,
        c.procedimiento,
        c.url_origen,
        a.n_ofertas
    FROM contrato_unico AS c
    JOIN adjudicacion AS a USING (contrato_id)
    WHERE c.procedimiento IN ('Abierto', 'Abierto simplificado', 'Restringido')
      AND a.n_ofertas > 0
      -- PLACSP publica el resultado de cada lote; el portal no tiene resultado por lote.
      AND (a.resultado IS NULL OR a.resultado IN ('Adjudicado', 'Formalizado'))
),

por_contrato AS (
    SELECT
        contrato_id,
        any_value(procedimiento) AS procedimiento,
        any_value(url_origen) AS url_origen,
        count(*) AS n_lotes,
        count_if(n_ofertas = 1) AS lotes_una_oferta
    FROM lotes
    GROUP BY contrato_id
)

SELECT
    contrato_id,
    'R-01' AS indicador,
    TRUE AS aplicable,
    lotes_una_oferta > 0 AS activado,
    CAST(lotes_una_oferta AS DOUBLE) AS valor,
    CASE
        WHEN lotes_una_oferta = 0 THEN NULL
        WHEN n_lotes = 1 THEN 'Se recibió una sola oferta en un procedimiento '
            || lower(procedimiento)
        ELSE 'Se recibió una sola oferta en ' || lotes_una_oferta || ' de ' || n_lotes
            || ' lotes de un procedimiento ' || lower(procedimiento)
    END AS motivo,
    url_origen
FROM por_contrato
