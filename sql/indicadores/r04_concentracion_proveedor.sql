-- R-04 · Concentración de proveedor
--
-- Definición (docs/04-indicadores-riesgo.md, D-018): una empresa se queda con más de la mitad
-- del importe adjudicado por un órgano en un mismo tipo de contrato.
--
-- Mercado = fuente + órgano + tipo de contrato, sobre todo el periodo cargado (2023–2026).
-- Se separa por fuente porque PLACSP da importes sin IVA y el portal regional con IVA, y no se
-- suman importes de bases distintas.
--
-- Cálculo por contrato:
--   * Aplicable: el contrato tiene adjudicatario, tipo de contrato e importe positivo, y su
--     mercado tiene al menos 10 contratos y 3 empresas distintas. Con menos, una cuota alta es
--     normal y no dice nada.
--   * Activado: algún adjudicatario del contrato tiene más del 50 % del importe del mercado.
--   * Valor: la mayor cuota (0–1) entre los adjudicatarios del contrato.
--   * El motivo incluye también el índice HHI del mercado (suma de cuotas al cuadrado, 0–1).
--
-- Limitaciones: no distingue mercados pequeños por naturaleza dentro de un tipo de contrato
-- (sin CPV, D-013); un órgano con un único proveedor posible (exclusividad) queda señalado;
-- incluye menores y mayores del portal. Las alertas de personas físicas seudonimizadas solo se
-- muestran agregadas (D-007). Una cuota alta es una señal de dependencia, no una irregularidad.
--
-- Decisiones: D-004, D-007, D-018.

WITH adjudicaciones AS (
    SELECT
        c.contrato_id,
        c.fuente,
        c.organo_id,
        c.tipo_contrato,
        c.url_origen,
        a.adjudicatario_id,
        coalesce(a.importe_sin_iva, a.importe_con_iva) AS importe
    FROM contrato_unico AS c
    JOIN adjudicacion AS a USING (contrato_id)
    WHERE a.adjudicatario_id IS NOT NULL
      AND c.tipo_contrato IS NOT NULL
      AND coalesce(a.importe_sin_iva, a.importe_con_iva) > 0
      AND (a.resultado IS NULL OR a.resultado IN ('Adjudicado', 'Formalizado'))
),

por_empresa AS (
    SELECT fuente, organo_id, tipo_contrato, adjudicatario_id, sum(importe) AS importe
    FROM adjudicaciones
    GROUP BY ALL
),

mercado AS (
    SELECT
        e.fuente,
        e.organo_id,
        e.tipo_contrato,
        count(*) AS n_empresas,
        sum(e.importe) AS total,
        sum(power(e.importe / t.total, 2)) AS hhi
    FROM por_empresa AS e
    JOIN (
        SELECT fuente, organo_id, tipo_contrato, sum(importe) AS total
        FROM por_empresa GROUP BY ALL
    ) AS t USING (fuente, organo_id, tipo_contrato)
    GROUP BY e.fuente, e.organo_id, e.tipo_contrato
),

contratos_mercado AS (
    SELECT fuente, organo_id, tipo_contrato, count(DISTINCT contrato_id) AS n_contratos
    FROM adjudicaciones
    GROUP BY ALL
),

por_contrato AS (
    SELECT
        a.contrato_id,
        any_value(a.url_origen) AS url_origen,
        any_value(a.tipo_contrato) AS tipo_contrato,
        max(e.importe / m.total) AS cuota,
        any_value(m.hhi) AS hhi,
        any_value(m.n_empresas) AS n_empresas,
        any_value(cm.n_contratos) AS n_contratos
    FROM adjudicaciones AS a
    JOIN por_empresa AS e USING (fuente, organo_id, tipo_contrato, adjudicatario_id)
    JOIN mercado AS m USING (fuente, organo_id, tipo_contrato)
    JOIN contratos_mercado AS cm USING (fuente, organo_id, tipo_contrato)
    WHERE cm.n_contratos >= 10 AND m.n_empresas >= 3
    GROUP BY a.contrato_id
)

SELECT
    contrato_id,
    'R-04' AS indicador,
    TRUE AS aplicable,
    cuota > 0.5 AS activado,
    cuota AS valor,
    CASE
        WHEN cuota > 0.5 THEN 'Un adjudicatario concentra el '
            || replace(CAST(round(100 * cuota, 1) AS VARCHAR), '.', ',')
            || ' % del importe adjudicado por este órgano en contratos de '
            || lower(tipo_contrato) || ' (' || n_contratos || ' contratos, ' || n_empresas
            || ' empresas, HHI ' || replace(CAST(round(hhi, 2) AS VARCHAR), '.', ',') || ')'
    END AS motivo,
    url_origen
FROM por_contrato
