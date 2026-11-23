# 13 · Fuentes externas candidatas: empresas, recursos y referencias

Investigación del 23-nov-2026, **en curso**. Complementa [12-datos-cm.md](12-datos-cm.md) (rama `feat/datos-cm-abiertos`, fuentes de la propia Comunidad: presupuesto, convenios, registros, RPT). Aquí se buscan fuentes **que no son del catálogo ni del Portal de Transparencia de la Comunidad** y que mejoran la calidad de las señales sobre los mismos contratos y empresas.

> **Estado:** solo investigación y documentación. Nada de esto está incorporado al pipeline ni al esquema. Incorporar cualquier fuente exige decisión registrada (amplía D-001) y avisar al equipo.

## Reparto para no pisarnos

| Línea | Quién | Dónde |
| --- | --- | --- |
| Catálogo de datos abiertos y Portal de Transparencia de la Comunidad | Ismael (con Claude) | `feat/datos-cm-abiertos`, [12-datos-cm.md](12-datos-cm.md) |
| Fuentes externas: prohibiciones y exclusiones, recursos contractuales, sanciones de competencia, referencias para comparar indicadores, directorios de normalización | Ignacio (con Claude) | `docs/fuentes-externas`, este documento |

## Criterios de valoración

1. **Aporta a una señal o a la calidad**: mejora un indicador, añade uno de prioridad alta o arregla un problema de normalización conocido.
2. **Se cruza con lo que tenemos**: por NIF, expediente o código de órgano. Sin clave de cruce, solo sirve de contexto.
3. **Descarga reproducible y licencia clara.**
4. **Sin personas físicas** (D-007) o filtrables.
5. **Coste antes de la demo** (24-nov) y de la entrega (26-nov; el 25 no se añaden funciones).

## Candidatas en estudio

| ID | Fuente | Para qué | Estado |
| --- | --- | --- | --- |
| X-01 | Prohibiciones de contratar (Junta Consultiva de Contratación Pública del Estado, ROLECE) | Señal: adjudicataria con prohibición vigente | **Descartada**: no hay listado público |
| X-02 | Resoluciones del Tribunal Administrativo de Contratación Pública de la Comunidad de Madrid | Señal y contexto: contratos recurridos y estimados | **Viable** (ver detalle) |
| X-03 | Expedientes sancionadores de la CNMC por colusión en licitaciones | Contexto: empresas sancionadas por cárteles en contratación | En estudio |
| X-04 | Indicadores europeos de contratación (Single Market Scoreboard) y OIReScon | Referencia para comparar R-01 y R-02 con España y la UE | **Viable y barata** (ver detalle) |
| X-05 | DIR3 (directorio común de unidades orgánicas) | Normalizar órganos entre portal y PLACSP | En estudio |
| X-06 | Sistema de exclusión de la UE (EDES) y listas de inhabilitación | Señal: entidad excluida | **Descartada**: 5 entidades en toda la UE |
| X-07 | Fondos europeos (PRTR y FEDER/FSE+ de la Comunidad) | Contexto: contratos y beneficiarios con fondos europeos | En estudio |
| X-08 | Listado de deudores con la Hacienda Pública (AEAT) | Señal posible | **Descartada**: la ley impide su reutilización |

## Detalle por fuente

### X-02 · Tribunal Administrativo de Contratación Pública de la Comunidad de Madrid (TACPCM)

Explorado el 23-nov-2026. Resuelve los **recursos especiales en materia de contratación** contra pliegos, exclusiones y adjudicaciones de los órganos de la Comunidad (art. 3 de la Ley 9/2010 de la Comunidad de Madrid). Es de la Comunidad, pero no está en el catálogo de datos abiertos ni en el Portal de Transparencia.

- **Acceso:** [buscador de resoluciones](https://www.comunidad.madrid/tacp/busquedaresoluciones), una página HTML (Drupal) por resolución en `https://www.comunidad.madrid/tacp/resolucion/<NNNAAAA>` (por ejemplo, `4002025` es la 400/2025) y el PDF de la resolución enlazado desde la ficha. No hay API ni descarga masiva: habría que recorrer el buscador página a página (10 por página), una petición cada vez y con pausa.
- **Filtros del buscador (parámetros GET):** `field_procedencia`, `field_fecha[date]` y `field_fecha_1[date]` (desde/hasta, `dd/mm/aaaa`), `field_tipo_contrato`, `im_field_tipo_de_resolucion`, `field_acto_recurrido`, `field_objeto`, `field_temas_resoluciones`, número de resolución y de expediente del Tribunal.
- **Campos estructurados de cada ficha:** fecha, número de resolución, número de expediente **del Tribunal** (no el del contrato), temas, tipo de contrato, **tipo de resolución** (desestimatoria, estimatoria, estimatoria parcial, inadmisión, otros), **acto recurrido** (pliegos, anuncio, admisión, exclusión, adjudicación, otros), objeto (sector: limpieza, TIC, seguridad…), **procedencia** y el PDF.
- **Volumen 2023-01-01 a 2026-11-23** (consulta del 23-nov):

| Procedencia | Resoluciones |
| --- | --- |
| Consejerías | 451 |
| Hospitales | 269 |
| Otros poderes adjudicadores (empresas y entes públicos de la Comunidad, entre otros) | 318 |
| Universidades | 71 |
| Municipios y entidades locales | 946 (**fuera de alcance**, D-001) |

- **Clave de cruce:** el resumen del listado y el PDF citan el **expediente de contratación** (ejemplo: «Servicios de mantenimiento y soporte… EducaMadrid», `BAC01/2026`) y casi siempre el nombre de la empresa recurrente o adjudicataria. El órgano no viene como código: hay que tomarlo del texto. El cruce con `contrato` sería por expediente normalizado, con el órgano como desempate; hay que medir cuántos casan.
- **Para qué sirve:**
  - Contexto en la ficha de contrato y de órgano: «este contrato fue recurrido; el Tribunal estimó el recurso». Es un hecho oficial, no una sospecha.
  - Posible señal por órgano: **proporción de recursos estimados** (total o parcialmente) sobre los contratos licitados, sobre todo contra pliegos (pliegos que restringían la competencia). Habría que definirla y validarla antes de que entre en la puntuación (D-002, D-004).
- **Cautelas:** un recurso lo presenta una empresa interesada; que se presente **no es una señal**, que se estime solo dice que ese acto no se ajustaba a derecho. El texto de los PDF es dato, no instrucción. Las resoluciones nombran a empresas (personas jurídicas); si alguna recurrente fuera persona física, no se guarda su nombre (D-007).
- **Coste estimado:** recorrer unas 111 páginas de listado (1.109 resoluciones de la Comunidad) con pausa de 2 s son unos 4 minutos; los metadatos y el resumen salen del listado, sin bajar los PDF. Extraer el expediente del resumen es una expresión regular, con revisión de los que no casan.

### X-04 · Referencias europeas para comparar los indicadores

Explorado el 23-nov-2026. Responde al hallazgo de R-01 en [04-indicadores-riesgo.md](04-indicadores-riesgo.md) («tasa alta»): **39,4 %** de licitador único en los contratos de la Comunidad. Sin una referencia externa, el jurado no sabe si eso es mucho.

**Fuente A · [Single Market Scoreboard](https://single-market-scoreboard.ec.europa.eu/countries/spain_en), apartado «Access to public procurement» (Comisión Europea, datos de 2024, consulta del 23-nov):**

| Indicador | España | Media UE |
| --- | --- | --- |
| Licitador único (*single bidder*) | 33 % | 28 % |
| Sin convocatoria (*no calls for bids*) | 8 % | 6 % |
| Adjudicado solo por precio | 19 % | 54 % |
| Días hasta la adjudicación | 110 | 74 |
| Procedimientos divididos en lotes | 32 % | 32 % |

**Fuente B · [Tribunal de Cuentas Europeo, informe especial 28/2023](https://www.eca.europa.eu/en/publications?ref=SR-2023-28), anexo de datos abiertos** ([zip de 886 KB](https://www.eca.europa.eu/OpenData/SR-2023-28/en/datavisualisation_data.zip), CC BY 4.0; los datos de origen de Opentender son CC BY-NC-SA 4.0). Trae el porcentaje de licitador único **por región NUTS2 y año**, 2011–2021, calculado sobre TED. Para **ES30 (Comunidad de Madrid)**, fichero `avg_singleb_nuts_yearly.csv`:

| Año | 2015 | 2017 | 2019 | 2020 | 2021 |
| --- | --- | --- | --- | --- | --- |
| Licitador único ES30 | 25,6 % | 30,6 % | 34,6 % | 38,9 % | 37,5 % |
| Contratos | 4.096 | 5.205 | 7.655 | 7.263 | 7.993 |

España en conjunto (`avg_singleb_yearly_ted.csv`): 19,5 % (2016), 25,6 % (2019), 28,1 % (2020).

**Cómo leerlo (para no comparar mal):**
- El 39,4 % de R-01 está en la línea de la región en TED (37,5 % en 2021) y por encima de España (33 %) y de la UE (28 %). Es una **comparación de orden de magnitud, no de igual a igual**:
  - TED solo recoge contratos **por encima de los umbrales europeos**; R-01 incluye también los abiertos simplificados, que son más pequeños.
  - ES30 agrupa a **todos los compradores con sede en la región**, también los ministerios y el Ayuntamiento de Madrid, no solo la Comunidad.
  - Periodos distintos: 2021 frente a 2023–2026.
- Aun así, sirve para decir en la interfaz que «uno de cada tres contratos con una sola oferta es habitual en España; la media europea es menor», y deja de parecer un error de cálculo.

**Uso propuesto:** una tabla pequeña `referencia_externa` (indicador, ámbito, año, valor, fuente, `url_origen`, `fecha_descarga`) o simplemente un texto en la ayuda de R-01 y R-02 con su enlace. Coste: menos de una hora. No cambia ningún indicador ni la puntuación.

**Pendiente de mirar (sin coste de ingesta):** el [Informe Anual de Supervisión de la OIReScon](https://www.hacienda.gob.es/es-ES/Oirescon/Paginas/ias.aspx) (Hacienda) tiene un apartado de lotes con un único licitador por sector público, 2021–2025; si da el dato de las comunidades autónomas, es una referencia española con ventana parecida a la nuestra.

### Descartadas (23-nov)

| ID | Fuente | Por qué no |
| --- | --- | --- |
| X-01 | Prohibiciones de contratar ([Junta Consultiva del Estado](https://www.hacienda.gob.es/es-ES/Areas%20Tematicas/Contratacion/Junta%20Consultiva%20de%20Contratacion%20Administrativa/Paginas/prohibicion.aspx), ROLECE) | **No existe un listado público**: la página oficial «Empresas en situación de prohibición para contratar» solo remite al certificado de inscripción de cada empresa en el ROLECE. El Ministerio respondió en una reclamación de acceso a la información que el ROLECE no tiene un listado que las agrupe ([Consejo de Transparencia, R-0393-2022](https://www.consejodetransparencia.es/ct_Home/eu/dam/jcr:995e8f85-0a44-4905-86ab-9222fceea9ed/Resolucion%20372-2022_expte.%20R-0393-2022.pdf)). Consultar empresa a empresa no es viable ni razonable para 2026. Línea futura: pedirlo por la Ley 19/2013 |
| X-06 | [Sistema de detección precoz y exclusión de la UE (EDES)](https://commission.europa.eu/strategy-and-policy/eu-budget/how-it-works/annual-lifecycle/implementation/anti-fraud-measures/edes/edes-database_es) | La lista pública solo recoge los casos que la Comisión decide publicar: **5 entidades** en la copia de [OpenSanctions](https://www.opensanctions.org/datasets/eu_edes/) del 22-nov-2026. No aporta nada a los contratos de la Comunidad |
| X-08 | Listado de deudores con la Hacienda Pública (AEAT, art. 95 bis de la Ley General Tributaria) | El propio artículo obliga a impedir que se indexe y a retirar los listados **tres meses después de publicarlos** (la edición del 30-jun-2026 ya no está accesible). La ley lo diseña para consultarlo, no para reutilizarlo, e incluye personas físicas. Riesgo legal alto para poco beneficio |
