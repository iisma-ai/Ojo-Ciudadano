-- Ampliación aditiva del esquema v1 (D-017, D-035): nombres oficiales de los códigos CPV
-- (Reglamento (CE) 213/2008), de la lista CODICE de la Plataforma de Contratación. Es un
-- diccionario para leer `contrato.cpv`: no cambia ninguna tabla ni ningún indicador.

CREATE TABLE cpv (
    codigo           VARCHAR PRIMARY KEY,  -- 8 cifras, como contrato.cpv
    nombre           VARCHAR,              -- nombre oficial en español
    division         VARCHAR NOT NULL,     -- 2 primeras cifras (p. ej. 33, equipamiento médico)
    nombre_division  VARCHAR,              -- nombre de la división
    fuente           VARCHAR NOT NULL,     -- placsp
    url_origen       VARCHAR NOT NULL,     -- lista de códigos oficial
    fecha_descarga   DATE NOT NULL
);
