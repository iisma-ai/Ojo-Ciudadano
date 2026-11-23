-- Ampliación aditiva del esquema v1 (D-017, D-024): contexto presupuestario y organizativo de la
-- Comunidad de Madrid (catálogo de datos abiertos y Portal de Transparencia).
-- No cambia ninguna tabla existente. Todas las filas llevan fuente, url_origen y fecha_descarga.
-- Personas físicas: no entra ninguna (D-007). Los registros de entidades solo guardan NIF de
-- persona jurídica y los convenios solo guardan firmantes con forma de entidad.

-- Series del catálogo de datos abiertos con el formato «Año; Concepto; Valor; Unidad» (presupuestos
-- iniciales y liquidados, ayudas de la UE, personal, gasto sanitario y educativo, recaudación).
CREATE TABLE serie_cm (
    serie_id        VARCHAR NOT NULL,   -- nombre del conjunto de datos en el catálogo
    serie           VARCHAR NOT NULL,   -- título del conjunto de datos
    anio            INTEGER NOT NULL,
    concepto        VARCHAR NOT NULL,
    dimension       VARCHAR,            -- fase de ejecución, capítulo o tipo de recaudación
    valor           DOUBLE,             -- en la unidad de la fuente
    unidad          VARCHAR,
    valor_eur       DOUBLE,             -- el valor en euros cuando la unidad es de dinero
    estado_dato     VARCHAR,
    fuente          VARCHAR NOT NULL,   -- ckan_cm
    url_origen      VARCHAR NOT NULL,
    fecha_descarga  DATE NOT NULL
);

-- Presupuesto por órgano (consejería, organismo) de las dos series que lo desglosan: iniciales por
-- clasificación orgánica y liquidados por órgano y fase de ejecución.
CREATE TABLE presupuesto_organo (
    anio            INTEGER NOT NULL,
    tipo            VARCHAR NOT NULL,   -- inicial | liquidado
    fase            VARCHAR,            -- crédito actual, obligaciones reconocidas, pagos…
    entidad         VARCHAR NOT NULL,   -- nombre del órgano tal como lo escribe la fuente
    organo_id       VARCHAR REFERENCES organo (organo_id),  -- nulo si no se reconoce el nombre
    importe_eur     DOUBLE NOT NULL,
    fuente          VARCHAR NOT NULL,
    url_origen      VARCHAR NOT NULL,
    fecha_descarga  DATE NOT NULL
);

-- Convenios vigentes firmados por la Comunidad (Portal de Transparencia). Los firmantes vienen
-- por nombre, sin NIF.
CREATE TABLE convenio (
    convenio_id     VARCHAR PRIMARY KEY,   -- «convenio:<referencia>»
    consejeria      VARCHAR NOT NULL,
    organo_id       VARCHAR REFERENCES organo (organo_id),
    referencia      VARCHAR NOT NULL,
    titulo          VARCHAR,
    fecha_firma     DATE,
    vigencia_desde  DATE,
    vigencia_hasta  DATE,
    indefinido      BOOLEAN,
    prorroga        VARCHAR,
    entidad_cm      VARCHAR,               -- entidad de la Comunidad que firma
    entidades       VARCHAR,               -- firmantes con forma de entidad, separados por « ; »
    n_firmantes     INTEGER,               -- todos los firmantes (también los que no se muestran)
    financiacion    VARCHAR,               -- texto de la fuente; no se suma
    con_financiacion BOOLEAN,
    fuente          VARCHAR NOT NULL,      -- transparencia_cm
    url_origen      VARCHAR NOT NULL,
    fecha_descarga  DATE NOT NULL
);

-- Entidades de los registros de la Comunidad que traen NIF: grupos de interés inscritos en el
-- registro de transparencia, fundaciones y cooperativas. Se cruzan con `adjudicatario` por NIF.
CREATE TABLE entidad_registro (
    nif             VARCHAR NOT NULL,
    registro        VARCHAR NOT NULL,      -- transparencia | fundaciones | cooperativas
    nombre          VARCHAR,
    detalle         VARCHAR,               -- categoría, clase o protectorado
    estado          VARCHAR,
    fuente          VARCHAR NOT NULL,
    url_origen      VARCHAR NOT NULL,
    fecha_descarga  DATE NOT NULL,
    PRIMARY KEY (nif, registro)
);

-- Puestos de la relación de puestos de trabajo (funcionarios) por organismo. Solo recuentos.
CREATE TABLE plantilla_organismo (
    organismo       VARCHAR NOT NULL,      -- tal como lo escribe la fuente
    organo_id       VARCHAR REFERENCES organo (organo_id),
    n_puestos       INTEGER NOT NULL,
    fuente          VARCHAR NOT NULL,
    url_origen      VARCHAR NOT NULL,
    fecha_descarga  DATE NOT NULL
);
