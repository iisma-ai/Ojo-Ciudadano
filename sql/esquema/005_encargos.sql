-- Ampliación aditiva del esquema v1 (D-017, D-028): encargos a medios propios del Portal de la
-- Contratación Pública de la Comunidad de Madrid (art. 32 de la Ley 9/2017). Un encargo no
-- es un contrato licitado: va aparte y no entra en los indicadores de riesgo ni en la
-- puntuación. El medio propio se guarda en `adjudicatario` con la misma identidad que en los
-- contratos (NIF normalizado; persona física sin NIF ni nombre, D-007).

CREATE TABLE encargo (
    encargo_id                      VARCHAR NOT NULL,  -- «portal_cm:<referencia>»
    orden                           INTEGER NOT NULL,  -- posición del medio propio en el encargo
    fuente                          VARCHAR NOT NULL,  -- portal_cm
    expediente                      VARCHAR,
    referencia_portal               VARCHAR,
    organo_id                       VARCHAR NOT NULL REFERENCES organo (organo_id),
    titulo                          VARCHAR,
    tipo_contrato                   VARCHAR,
    anio_publicacion                INTEGER NOT NULL,  -- año de publicación en el portal (el CSV no trae fechas)
    medio_propio_id                 VARCHAR REFERENCES adjudicatario (adjudicatario_id),
    importe_con_iva                 DOUBLE,            -- importe del encargo, con impuestos
    importe_modificaciones_con_iva  DOUBLE,
    url_origen                      VARCHAR NOT NULL,  -- ficha del encargo en el portal
    fecha_descarga                  DATE NOT NULL,
    PRIMARY KEY (encargo_id, orden)
);
