-- R-03 · Posible fraccionamiento de contratos menores
--
-- Definición (D-014 y D-015): dos o más contratos menores al mismo adjudicatario, del mismo órgano y
-- del mismo tipo de contrato, dentro de una ventana móvil de 12 meses, cuya suma CON IVA
-- supera 18.150 € (servicios y suministros) o 48.400 € (obras), es decir, el umbral legal de
-- 15.000 € / 40.000 € multiplicado por 1,21. Como el IVA nunca supera el 21 %, superar esa
-- suma con IVA implica superar el umbral legal sin IVA.
--
-- En la suma solo cuentan los menores de al menos UN TERCIO del umbral (6.050 € / 16.133,33 €
-- con IVA, D-015): el patrón de partir un contrato grande en pocos trozos. Sin ese filtro la
-- señal se activaba en el 85 % de los menores por los pedidos recurrentes de los hospitales.
--
-- Cálculo:
--   1. Para cada pieza (menor ≥ un tercio del umbral) se suma su ventana de los 12 meses
--      anteriores (incluida ella), contando solo piezas.
--   2. Una ventana se activa si tiene al menos 2 contratos y supera el umbral.
--   3. Un contrato se activa si pertenece a alguna ventana activada. Valor = la mayor suma de
--      las ventanas activadas a las que pertenece; el motivo da su número de contratos.
--   * Aplicable: contrato menor de servicios, suministros u obras con adjudicatario, fecha e
--     importe. Los de otros tipos o sin esos datos no son aplicables (NULL). Los menores por
--     debajo de un tercio del umbral son aplicables, pero nunca se activan.
--   * Excluidas: suscripciones a publicaciones y bases de datos (título con «suscripción»),
--     que la ley permite contratar como menores sin ese límite (LCSP, disposición adicional
--     novena).
--
-- Datos: menores del portal regional (es_menor, tipo_contrato, fecha_contrato, organo_id) y
-- adjudicacion.adjudicatario_id e importe_con_iva. Las personas físicas aparecen seudonimizadas.
--
-- Limitaciones: agrupa por tipo de contrato y no por CPV (los menores no publican CPV), así
-- que puede juntar prestaciones distintas; el umbral con IVA es conservador y no señala sumas
-- que superan el umbral sin IVA pero quedan por debajo con IVA; tampoco señala la división en
-- muchos trozos pequeños (D-015). La suma de varios menores no prueba un fraccionamiento:
-- puede haber necesidades distintas e imprevisibles.
--
-- Decisiones: D-002, D-004, D-014, D-015.

WITH menores AS (
    SELECT
        c.contrato_id,
        c.organo_id,
        c.tipo_contrato,
        c.fecha_contrato,
        c.url_origen,
        a.adjudicatario_id,
        a.importe_con_iva,
        CASE WHEN c.tipo_contrato = 'obras' THEN 48400 ELSE 18150 END AS umbral
    FROM contrato_unico AS c
    JOIN adjudicacion AS a USING (contrato_id)
    WHERE c.es_menor
      AND c.tipo_contrato IN ('servicios', 'suministros', 'obras')
      AND c.fecha_contrato IS NOT NULL
      AND a.adjudicatario_id IS NOT NULL
      AND a.importe_con_iva IS NOT NULL
      AND NOT regexp_matches(coalesce(c.titulo, ''), '(?i)su(b)?scrip')
),

piezas AS (
    SELECT * FROM menores WHERE importe_con_iva >= umbral / 3
),

ventanas AS (
    SELECT
        *,
        count(*) OVER w AS n_ventana,
        sum(importe_con_iva) OVER w AS suma_ventana
    FROM piezas
    WINDOW w AS (
        PARTITION BY adjudicatario_id, organo_id, tipo_contrato
        ORDER BY fecha_contrato
        RANGE BETWEEN INTERVAL 364 DAYS PRECEDING AND CURRENT ROW
    )
),

ventanas_activadas AS (
    SELECT adjudicatario_id, organo_id, tipo_contrato, fecha_contrato AS fin,
           n_ventana, suma_ventana
    FROM ventanas
    WHERE n_ventana >= 2 AND suma_ventana > umbral
),

-- Cada pieza contra las ventanas activadas que la contienen: las que acaban entre su fecha y
-- 364 días después.
activados AS (
    SELECT
        m.contrato_id,
        arg_max(v.n_ventana, v.suma_ventana) AS n_ventana,
        max(v.suma_ventana) AS suma_ventana
    FROM piezas AS m
    JOIN ventanas_activadas AS v
      ON v.adjudicatario_id = m.adjudicatario_id
     AND v.organo_id = m.organo_id
     AND v.tipo_contrato = m.tipo_contrato
     AND v.fin >= m.fecha_contrato
     AND v.fin <= m.fecha_contrato + INTERVAL 364 DAYS
    GROUP BY m.contrato_id
),

-- Un menor con varios adjudicatarios (poco frecuente) da una fila por contrato.
por_contrato AS (
    SELECT contrato_id, any_value(url_origen) AS url_origen, any_value(umbral) AS umbral
    FROM menores
    GROUP BY contrato_id
)

SELECT
    p.contrato_id,
    'R-03' AS indicador,
    TRUE AS aplicable,
    a.contrato_id IS NOT NULL AS activado,
    a.suma_ventana AS valor,
    CASE WHEN a.contrato_id IS NOT NULL THEN
        'Posible fraccionamiento: ' || a.n_ventana || ' contratos menores de al menos '
        || euros(p.umbral / 3) || ' € con el mismo adjudicatario, órgano y tipo de contrato '
        || 'suman ' || euros(a.suma_ventana) || ' € con IVA en 12 meses (umbral de referencia: '
        || euros(p.umbral) || ' € con IVA). Es una señal para revisar, no una prueba: '
        || 'pueden ser necesidades distintas'
    END AS motivo,
    p.url_origen
FROM por_contrato AS p
LEFT JOIN activados AS a USING (contrato_id)
