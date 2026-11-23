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
| X-02 | Resoluciones del Tribunal Administrativo de Contratación Pública de la Comunidad de Madrid | Señal y contexto: contratos recurridos y estimados | En estudio |
| X-03 | Expedientes sancionadores de la CNMC por colusión en licitaciones | Contexto: empresas sancionadas por cárteles en contratación | En estudio |
| X-04 | Indicadores europeos de contratación (Single Market Scoreboard) y OIReScon | Referencia para comparar R-01 y R-02 con España y la UE | En estudio |
| X-05 | DIR3 (directorio común de unidades orgánicas) | Normalizar órganos entre portal y PLACSP | En estudio |
| X-06 | Sistema de exclusión de la UE (EDES) y listas de inhabilitación | Señal: entidad excluida | En estudio |
| X-07 | Fondos europeos (PRTR y FEDER/FSE+ de la Comunidad) | Contexto: contratos y beneficiarios con fondos europeos | En estudio |
| X-08 | Listado de deudores con la Hacienda Pública (AEAT) | Señal posible: limitaciones de uso por estudiar | En estudio |
