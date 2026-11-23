-- Ampliación aditiva del esquema v1 (D-017, D-025): financiación con fondos europeos de cada
-- licitación, tal como la publica PLACSP en `cac:TenderingTerms/cbc:FundingProgramCode`
-- (lista FundingProgramCode-2.08). No cambia ninguna tabla existente.
-- Es contexto, no una señal de riesgo. Solo hay fila si la entrada trae el campo.

CREATE TABLE contrato_financiacion (
    contrato_id     VARCHAR PRIMARY KEY REFERENCES contrato (contrato_id),
    financiado_ue   BOOLEAN NOT NULL,       -- código «EU» (true) o «NO-EU» (false)
    programas_ue    VARCHAR,                -- PRTR, FEDER, FSE+, FEADER u OFE, separados por comas
    fuente          VARCHAR NOT NULL,       -- placsp
    url_origen      VARCHAR NOT NULL,
    fecha_descarga  DATE NOT NULL
);
