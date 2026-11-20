-- Ampliación aditiva del esquema v1 (D-017): concesiones de subvenciones de la BDNS (F-03).
-- No cambia ninguna tabla existente. Los beneficiarios se guardan en `adjudicatario` con la
-- misma identidad que en los contratos (NIF normalizado), para poder sumar por empresa lo
-- recibido en contratos y en subvenciones sin mezclar las dos tablas.
-- Personas físicas: seudónimo «PF-…» del idPersona de la BDNS, sin NIF ni nombre (D-007).

CREATE TABLE concesion (
    concesion_id         VARCHAR PRIMARY KEY,   -- «bdns:<codConcesion>»
    fuente               VARCHAR NOT NULL,      -- bdns
    organo_id            VARCHAR NOT NULL REFERENCES organo (organo_id),
    beneficiario_id      VARCHAR REFERENCES adjudicatario (adjudicatario_id),
    id_convocatoria      BIGINT,
    numero_convocatoria  VARCHAR,               -- código BDNS de la convocatoria
    convocatoria         VARCHAR,               -- título de la convocatoria
    instrumento          VARCHAR,               -- subvención, préstamo, garantía…
    fecha_concesion      DATE,
    importe              DOUBLE,                -- importe concedido (sin distinción de IVA)
    ayuda_equivalente    DOUBLE,                -- equivalente de subvención (préstamos, avales)
    url_bases            VARCHAR,               -- bases reguladoras publicadas por el órgano
    url_origen           VARCHAR NOT NULL,      -- ficha de la convocatoria en la BDNS
    fecha_descarga       DATE NOT NULL
);
