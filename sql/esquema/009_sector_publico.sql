-- Ampliación aditiva del esquema v1 (D-017, D-033): entes del sector público institucional
-- (INVENTE, IGAE) con su NIF, para reconocer los adjudicatarios que son entes públicos y no
-- empresas privadas. Es contexto: no cambia ninguna tabla ni ningún indicador. Se cruza con
-- adjudicatario.nif; un NIF que casa con un nombre muy distinto suele ser un error de la fuente.

CREATE TABLE entidad_sector_publico (
    nif              VARCHAR PRIMARY KEY,  -- NIF del ente, mayúsculas sin separadores
    codigo_invente   VARCHAR NOT NULL,     -- código en el inventario (INV…)
    nombre           VARCHAR,              -- denominación oficial
    forma_juridica   VARCHAR,              -- Fundación | Universidad pública | Sociedad mercantil | Organismo autónomo…
    administracion   VARCHAR,              -- Comunidad de Madrid | Entidad local de Madrid | Otra comunidad autónoma | Entidad local de otra comunidad | Estado
    codigo_dir3      VARCHAR,              -- código DIR3 si lo tiene
    codigo_origen    VARCHAR,              -- código del inventario de origen
    fuente           VARCHAR NOT NULL,     -- invente
    url_origen       VARCHAR NOT NULL,     -- aplicación de consulta de INVENTE
    fecha_descarga   DATE NOT NULL
);
