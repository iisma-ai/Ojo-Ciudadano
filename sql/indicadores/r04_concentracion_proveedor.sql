-- R-04 · Concentración de proveedor
--
-- Definición (docs/04-indicadores-riesgo.md, D-018, D-036): una empresa se queda con más de la
-- mitad del importe adjudicado por un órgano en un mismo mercado.
--
-- Mercado = fuente + órgano + tipo de contrato y, en PLACSP, también la división del CPV (las
-- dos primeras cifras: 33 equipamiento médico, 79 servicios a empresas…), sobre todo el
-- periodo cargado (2023–2026). Así no se mezclan en un mismo mercado, por ejemplo, el material
-- sanitario y el material de oficina. El portal regional no publica CPV: allí el mercado sigue
-- siendo órgano + tipo. Se separa por fuente porque PLACSP da importes sin IVA y el portal
-- regional con IVA, y no se suman importes de bases distintas.
--
-- Cálculo por contrato:
--   * Aplicable: el contrato tiene adjudicatario, tipo de contrato e importe positivo, su
--     mercado tiene al menos 10 contratos y 3 adjudicatarios distintos, y algún adjudicatario
--     del contrato no es un ente del sector público.
--   * Entes del sector público (INVENTE, D-036): cuentan en el mercado, porque se llevan parte
--     del importe, pero no activan la señal. Una universidad o una empresa pública que recibe
--     mucho de su consejería no es una dependencia de un proveedor privado.
--   * Activado: algún adjudicatario privado del contrato tiene más del 50 % del importe del
--     mercado.
--   * Valor: la mayor cuota (0–1) entre los adjudicatarios privados del contrato.
--   * El motivo incluye también el índice HHI del mercado (suma de cuotas al cuadrado, 0–1).
--
-- Limitaciones: en el portal regional no distingue mercados pequeños por naturaleza dentro de
-- un tipo de contrato (sin CPV, D-013); un órgano con un único proveedor posible
-- (exclusividad) queda señalado; incluye menores y mayores del portal. Un NIF de la fuente mal
-- puesto puede hacer pasar por ente público a una empresa (D-035). Las alertas de personas
-- físicas seudonimizadas solo se muestran agregadas (D-007). Una cuota alta es una señal de
-- dependencia, no una irregularidad.
--
-- Decisiones: D-004, D-007, D-018, D-035, D-036.

WITH adjudicaciones AS (
    SELECT
        c.contrato_id,
        c.fuente,
        c.organo_id,
        c.tipo_contrato,
        CASE WHEN c.fuente = 'placsp' THEN coalesce(substr(c.cpv, 1, 2), '') ELSE '' END
            AS division,
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
    SELECT fuente, organo_id, tipo_contrato, division, adjudicatario_id, sum(importe) AS importe
    FROM adjudicaciones
    GROUP BY ALL
),

mercado AS (
    SELECT
        e.fuente,
        e.organo_id,
        e.tipo_contrato,
        e.division,
        count(*) AS n_empresas,
        sum(e.importe) AS total,
        sum(power(e.importe / t.total, 2)) AS hhi
    FROM por_empresa AS e
    JOIN (
        SELECT fuente, organo_id, tipo_contrato, division, sum(importe) AS total
        FROM por_empresa GROUP BY ALL
    ) AS t USING (fuente, organo_id, tipo_contrato, division)
    GROUP BY e.fuente, e.organo_id, e.tipo_contrato, e.division
),

-- Adjudicatarios cuyo NIF está en el inventario de entes del sector público (INVENTE).
entes_publicos AS (
    SELECT d.adjudicatario_id
    FROM adjudicatario AS d
    JOIN entidad_sector_publico AS e ON e.nif = d.nif
),

contratos_mercado AS (
    SELECT fuente, organo_id, tipo_contrato, division, count(DISTINCT contrato_id) AS n_contratos
    FROM adjudicaciones
    GROUP BY ALL
),

por_contrato AS (
    SELECT
        a.contrato_id,
        any_value(a.url_origen) AS url_origen,
        any_value(a.tipo_contrato) AS tipo_contrato,
        any_value(a.division) AS division,
        max(e.importe / m.total) AS cuota,
        any_value(m.hhi) AS hhi,
        any_value(m.n_empresas) AS n_empresas,
        any_value(cm.n_contratos) AS n_contratos
    FROM adjudicaciones AS a
    JOIN por_empresa AS e USING (fuente, organo_id, tipo_contrato, division, adjudicatario_id)
    JOIN mercado AS m USING (fuente, organo_id, tipo_contrato, division)
    JOIN contratos_mercado AS cm USING (fuente, organo_id, tipo_contrato, division)
    WHERE cm.n_contratos >= 10 AND m.n_empresas >= 3
      AND a.adjudicatario_id NOT IN (SELECT adjudicatario_id FROM entes_publicos)
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
            || lower(tipo_contrato)
            || CASE WHEN division <> '' THEN ' de la división CPV ' || division ELSE '' END
            || ' (' || n_contratos || ' contratos, ' || n_empresas
            || ' adjudicatarios, HHI ' || replace(CAST(round(hhi, 2) AS VARCHAR), '.', ',') || ')'
    END AS motivo,
    url_origen
FROM por_contrato
