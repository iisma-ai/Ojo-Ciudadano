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
| X-01 | Prohibiciones de contratar (Junta Consultiva de Contratación Pública del Estado, ROLECE) | Señal: adjudicataria con prohibición vigente | En estudio |
| X-02 | Resoluciones del Tribunal Administrativo de Contratación Pública de la Comunidad de Madrid | Señal y contexto: contratos recurridos y estimados | **Viable** (ver detalle) |
| X-03 | Expedientes sancionadores de la CNMC por colusión en licitaciones | Contexto: empresas sancionadas por cárteles en contratación | En estudio |
| X-04 | Indicadores europeos de contratación (Single Market Scoreboard) y OIReScon | Referencia para comparar R-01 y R-02 con España y la UE | En estudio |
| X-05 | DIR3 (directorio común de unidades orgánicas) | Normalizar órganos entre portal y PLACSP | En estudio |
| X-06 | Sistema de exclusión de la UE (EDES) y listas de inhabilitación | Señal: entidad excluida | En estudio |
| X-07 | Fondos europeos (PRTR y FEDER/FSE+ de la Comunidad) | Contexto: contratos y beneficiarios con fondos europeos | En estudio |
| X-08 | Listado de deudores con la Hacienda Pública (AEAT) | Señal posible: limitaciones de uso por estudiar | En estudio |

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
