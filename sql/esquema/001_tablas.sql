-- Esquema de la base analítica de Ojo Ciudadano (DuckDB).
-- PROPUESTA para congelar en el hito H1 (17-nov-2026). Después de congelarlo, cualquier
-- cambio requiere una decisión registrada en docs/decisions.md.
--
-- Reglas:
--   * Toda tabla de hechos lleva fuente, url_origen y fecha_descarga.
--   * No hay personas físicas identificables: su adjudicatario_id es un seudónimo «PF-…»
--     y no se guarda ni su NIF ni su nombre (D-007).
--   * Los importes de PLACSP van SIN IVA y los del portal regional CON IVA. Cada columna
--     dice cuál es; nunca se suman columnas de bases distintas.

CREATE TABLE organo (
    organo_id        VARCHAR PRIMARY KEY,  -- nombre del órgano normalizado (mayúsculas, sin tildes)
    nombre           VARCHAR NOT NULL,
    consejeria       VARCHAR,              -- primer nivel de la jerarquía, si la fuente lo da
    jerarquia        VARCHAR,              -- niveles de arriba abajo separados por «··>»
    codigo_placsp    VARCHAR               -- identificador del órgano en PLACSP (ID_OC_PLAT)
);

CREATE TABLE adjudicatario (
    adjudicatario_id VARCHAR PRIMARY KEY,  -- NIF normalizado, «PF-…» (persona física) o «UTE:…»
    nif              VARCHAR,              -- vacío en personas físicas y UTE
    nombre           VARCHAR,              -- vacío en personas físicas
    tipo_persona     VARCHAR NOT NULL      -- juridica | fisica | ute | otro
);

CREATE TABLE contrato (
    contrato_id          VARCHAR PRIMARY KEY,   -- «placsp:<n>» o «portal_cm:<referencia>»
    fuente               VARCHAR NOT NULL,      -- placsp | portal_cm
    expediente           VARCHAR,
    referencia_portal    VARCHAR,               -- referencia de la ficha en el portal regional
    organo_id            VARCHAR NOT NULL REFERENCES organo (organo_id),
    titulo               VARCHAR,
    tipo_publicacion     VARCHAR,               -- solo portal: menores, licitación, sin publicidad…
    tipo_contrato        VARCHAR,               -- suministros | servicios | obras | …
    procedimiento        VARCHAR,
    es_menor             BOOLEAN NOT NULL,
    estado               VARCHAR,
    cpv                  VARCHAR,               -- solo PLACSP
    presupuesto_sin_iva  DOUBLE,                -- solo PLACSP
    presupuesto_con_iva  DOUBLE,                -- solo portal
    valor_estimado       DOUBLE,                -- solo PLACSP
    fecha_contrato       DATE,                  -- solo portal
    fecha_fin_plazo      DATE,                  -- solo PLACSP: fin del plazo de presentación
    -- Una licitación puede estar en las dos fuentes. La fila del portal apunta aquí a la de
    -- PLACSP para no contarla dos veces (ver la vista contrato_unico).
    duplicado_de         VARCHAR,
    url_origen           VARCHAR NOT NULL,
    fecha_descarga       DATE NOT NULL
);

CREATE TABLE adjudicacion (
    contrato_id                     VARCHAR NOT NULL REFERENCES contrato (contrato_id),
    orden                           INTEGER NOT NULL,  -- posición del adjudicatario en el contrato
    lote                            VARCHAR,           -- solo PLACSP
    adjudicatario_id                VARCHAR REFERENCES adjudicatario (adjudicatario_id),
    n_ofertas                       BIGINT,            -- ofertas recibidas
    resultado                       VARCHAR,           -- solo PLACSP: Formalizado, Desierto…
    importe_sin_iva                 DOUBLE,            -- solo PLACSP
    importe_con_iva                 DOUBLE,            -- solo portal
    importe_modificaciones_con_iva  DOUBLE,            -- solo portal
    importe_prorrogas_con_iva       DOUBLE,            -- solo portal
    importe_liquidacion_con_iva     DOUBLE,            -- solo portal
    fecha_formalizacion             DATE,              -- solo PLACSP
    fuente                          VARCHAR NOT NULL,
    url_origen                      VARCHAR NOT NULL,
    fecha_descarga                  DATE NOT NULL,
    PRIMARY KEY (contrato_id, orden)
);

-- Contratos sin repetir los que están en las dos fuentes.
CREATE VIEW contrato_unico AS
SELECT * FROM contrato WHERE duplicado_de IS NULL;
