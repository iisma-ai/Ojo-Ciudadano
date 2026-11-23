-- Ampliación aditiva del esquema v1 (D-017, D-029): resoluciones del Tribunal Administrativo
-- de Contratación Pública de la Comunidad de Madrid sobre recursos especiales. Es contexto
-- oficial del contrato, no un indicador de riesgo: no entra en la puntuación. Presentar un
-- recurso no es una señal; que se estime solo dice que ese acto no se ajustaba a derecho.
-- No se guarda el resumen de la resolución: nombra a las empresas y puede nombrar a personas.

CREATE TABLE recurso_especial (
    resolucion_id      VARCHAR PRIMARY KEY,  -- «tacpcm:<número>/<año>»
    numero             VARCHAR NOT NULL,     -- número de resolución del Tribunal
    fecha              DATE,
    procedencia        VARCHAR NOT NULL,     -- Consejerías | Hospitales | Otros poderes adjudicadores | Universidades
    tipo_resolucion    VARCHAR NOT NULL,     -- Desestimatoria | Estimatoria | Estimatoria parcial | Inadmisión | Otros (varios: «; »)
    acto_recurrido     VARCHAR NOT NULL,     -- Pliegos | Anuncio | Admisión | Exclusión | Adjudicación | Otros (varios: «; »)
    expediente_citado  VARCHAR,              -- expediente de contratación citado en el resumen que casa con un contrato
    contrato_id        VARCHAR REFERENCES contrato (contrato_id),  -- solo si casa con un único contrato
    fuente             VARCHAR NOT NULL,     -- tacpcm
    url_origen         VARCHAR NOT NULL,     -- ficha de la resolución
    url_documento      VARCHAR,              -- PDF de la resolución
    fecha_descarga     DATE NOT NULL
);
