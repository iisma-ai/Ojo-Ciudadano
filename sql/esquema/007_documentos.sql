-- Ampliación aditiva del esquema v1 (D-017, D-030 bloque B): pliegos de cada licitación de
-- PLACSP, tal como los enlaza el Atom (`cac:LegalDocumentReference` y
-- `cac:TechnicalDocumentReference`). No cambia ninguna tabla existente. Solo guarda el enlace:
-- el texto del pliego se lee bajo demanda en el asistente (`asistente/documentos.py`) y no
-- entra en la base. Tener o no pliego no es una señal de riesgo.

CREATE TABLE contrato_documento (
    contrato_id     VARCHAR NOT NULL REFERENCES contrato (contrato_id),
    orden           INTEGER NOT NULL,     -- 1, 2… en el orden de la entrada
    tipo            VARCHAR NOT NULL,     -- pcap (cláusulas administrativas) | ppt (prescripciones técnicas)
    nombre          VARCHAR,              -- nombre del fichero que publica la Plataforma
    url_documento   VARCHAR NOT NULL,     -- PDF del pliego en el portal de la Comunidad
    fuente          VARCHAR NOT NULL,     -- placsp
    url_origen      VARCHAR NOT NULL,     -- ficha de la licitación
    fecha_descarga  DATE NOT NULL,
    PRIMARY KEY (contrato_id, orden)
);
