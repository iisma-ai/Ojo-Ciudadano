-- Puntuación de riesgo por contrato, órgano y empresa (docs/04-indicadores-riesgo.md, D-020).
-- Parte de indicador_resultado; el ejecutor lo lanza después de calcular los indicadores.
--
-- Contrato: puntuación = indicadores activados / indicadores aplicables (0–1). Los no
-- aplicables no cuentan ni a favor ni en contra. n_aplicables permite a la interfaz no
-- fiarse de una puntuación calculada con un solo indicador.
-- Órgano y empresa: media de la puntuación de sus contratos ponderada por importe, total y
-- por año. El importe se usa solo como peso: no se presentan sumas que mezclen bases con y
-- sin IVA (P-10).
-- Personas físicas (PF-…): no tienen puntuación propia (D-007); sus contratos sí cuentan en
-- el órgano.
-- Entes del sector público (INVENTE, D-036): conservan su ficha y sus contratos, pero su
-- puntuación de empresa queda vacía (NULL) y `sector_publico` lo marca, porque no son empresas
-- privadas (una universidad, un hospital o una empresa pública) y no se comparan con ellas.
-- Sus contratos sí cuentan en el órgano que adjudica.

CREATE OR REPLACE TABLE puntuacion_contrato AS
WITH agregado AS (
    SELECT
        contrato_id,
        count(*) AS n_aplicables,
        count_if(activado) AS n_activados,
        string_agg(indicador, ', ' ORDER BY indicador) FILTER (WHERE activado) AS indicadores
    FROM indicador_resultado
    WHERE aplicable
    GROUP BY contrato_id
),
importes AS (
    SELECT
        contrato_id,
        sum(coalesce(importe_sin_iva, importe_con_iva)) AS importe,
        min(fecha_formalizacion) AS fecha_formalizacion
    FROM adjudicacion
    GROUP BY contrato_id
)
SELECT
    c.contrato_id,
    c.organo_id,
    year(coalesce(c.fecha_contrato, i.fecha_formalizacion, c.fecha_fin_plazo)) AS anio,
    coalesce(i.importe, 0) AS importe,
    g.n_aplicables,
    g.n_activados,
    g.n_activados / g.n_aplicables AS puntuacion,
    g.indicadores AS indicadores_activados,
    c.url_origen
FROM agregado AS g
JOIN contrato_unico AS c USING (contrato_id)
LEFT JOIN importes AS i USING (contrato_id);

-- Un contrato por empresa: reparte el importe de cada adjudicación a su adjudicatario.
CREATE OR REPLACE TABLE puntuacion_empresa_contrato AS
SELECT
    a.adjudicatario_id,
    p.contrato_id,
    p.anio,
    p.puntuacion,
    p.n_activados,
    d.adjudicatario_id IN (SELECT adjudicatario_id FROM adjudicatario_ente_publico)
        AS sector_publico,
    sum(coalesce(a.importe_sin_iva, a.importe_con_iva, 0)) AS importe
FROM adjudicacion AS a
JOIN puntuacion_contrato AS p USING (contrato_id)
JOIN adjudicatario AS d USING (adjudicatario_id)
WHERE d.tipo_persona <> 'fisica'
GROUP BY ALL;

CREATE OR REPLACE TABLE puntuacion_organo AS
SELECT
    organo_id,
    count(*) AS n_contratos,
    count_if(n_activados > 0) AS n_con_alertas,
    sum(puntuacion * importe) / nullif(sum(importe), 0) AS puntuacion_ponderada,
    avg(puntuacion) AS puntuacion_media
FROM puntuacion_contrato
GROUP BY organo_id;

CREATE OR REPLACE TABLE puntuacion_organo_anio AS
SELECT
    organo_id,
    anio,
    count(*) AS n_contratos,
    count_if(n_activados > 0) AS n_con_alertas,
    sum(puntuacion * importe) / nullif(sum(importe), 0) AS puntuacion_ponderada,
    avg(puntuacion) AS puntuacion_media
FROM puntuacion_contrato
WHERE anio BETWEEN 2023 AND 2026  -- fuera de ese rango son fechas erróneas de la fuente
GROUP BY organo_id, anio;

CREATE OR REPLACE TABLE puntuacion_empresa AS
SELECT
    adjudicatario_id,
    count(*) AS n_contratos,
    count_if(n_activados > 0) AS n_con_alertas,
    bool_or(sector_publico) AS sector_publico,
    CASE WHEN NOT bool_or(sector_publico)
         THEN sum(puntuacion * importe) / nullif(sum(importe), 0) END AS puntuacion_ponderada,
    CASE WHEN NOT bool_or(sector_publico) THEN avg(puntuacion) END AS puntuacion_media
FROM puntuacion_empresa_contrato
GROUP BY adjudicatario_id;

CREATE OR REPLACE TABLE puntuacion_empresa_anio AS
SELECT
    adjudicatario_id,
    anio,
    count(*) AS n_contratos,
    count_if(n_activados > 0) AS n_con_alertas,
    bool_or(sector_publico) AS sector_publico,
    CASE WHEN NOT bool_or(sector_publico)
         THEN sum(puntuacion * importe) / nullif(sum(importe), 0) END AS puntuacion_ponderada,
    CASE WHEN NOT bool_or(sector_publico) THEN avg(puntuacion) END AS puntuacion_media
FROM puntuacion_empresa_contrato
WHERE anio BETWEEN 2023 AND 2026
GROUP BY adjudicatario_id, anio;
