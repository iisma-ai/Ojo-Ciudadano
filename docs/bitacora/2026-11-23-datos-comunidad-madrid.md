# 2026-11-23 · Contexto de la Comunidad de Madrid: presupuesto, convenios y registros

- **Autor:** Claude (agente), a petición de la persona que coordina
- **Fase del plan:** 2, un día antes del hito H3 (demo funcional). Amplía D-001 con D-024.

## Qué se hizo

La web tenía poca información: solo contratos y subvenciones, sin contexto. Se pidió buscar en las fuentes de la **Comunidad de Madrid** (y solo en ellas) lo que pudiera servir, cargarlo y mostrarlo.

1. **Barrido de fuentes.** Catálogo de datos abiertos completo (2.276 conjuntos, 111 de Hacienda y Sector público) y secciones del Portal de Transparencia. Se descartaron TED y otras fuentes que no son de la Comunidad.
2. **Descarga reproducible** (`ingesta/cm_abiertos.py`): 32 ficheros, unos 21 MB, una petición cada vez con pausa, en `data/raw/cm_abiertos/` con manifiesto (URL, fecha, tamaño y huella).
3. **Lectura y carga** (`ingesta/cm_contexto.py`, `modelo/contexto.py`): cinco tablas nuevas en `sql/esquema/003_contexto_cm.sql` (`serie_cm`, `presupuesto_organo`, `convenio`, `entidad_registro`, `plantilla_organismo`). La carga **no toca** contratos, indicadores ni anomalías.
4. **Interfaz:** pantalla «Presupuesto y contexto» (cinco pestañas), bloque de presupuesto en la ficha de órgano, registros en la ficha de empresa, pie con las dos fuentes nuevas.
5. **Asistente:** las tablas nuevas están en la lista permitida y descritas.
6. **Comprobación entre equipos:** `docs/datos-cm-referencia.json` (filas por tabla y huella de cada fichero). El comando termina diciendo si coincide.

## Resultados

| Tabla | Filas |
| --- | --- |
| `serie_cm` | 79.226 |
| `presupuesto_organo` | 2.539 (65 filas de consejerías con `organo_id`) |
| `convenio` | 4.914 (4.572 con algún firmante que es entidad; 1.724 con financiación) |
| `entidad_registro` | 6.625 (4.237 cooperativas, 1.799 registro de transparencia, 589 fundaciones) |
| `plantilla_organismo` | 26 |

- Cruce por NIF con nuestras empresas: 836 adjudicatarias o beneficiarias figuran en el registro de transparencia, 151 son fundaciones y 272 cooperativas.
- Gasto reconocido por las consejerías en 2024 y 2025 en el orden esperado (Sanidad 12,8 mil millones en 2025).

## Decisiones y desviaciones

- **D-024** (ver `decisions.md`): ampliación aditiva del esquema, nueva dependencia `fastexcel`, contexto sin entrar en la puntuación.
- El esquema v1 sigue congelado; `003` solo añade tablas.
- Dependencia nueva: `fastexcel` (lector de Excel de polars) para el listado de convenios, que el portal publica en `.xlsx`. Quien actualice debe hacer `uv sync`.

## Privacidad y lenguaje (D-007, D-002)

- Registros: solo NIF de persona jurídica (el DNI, el NIE y el vacío no entran).
- Convenios: solo se guardan los firmantes con forma de entidad; el resto se cuenta pero no se guarda. El texto de financiación no se suma.
- Registros de solicitudes de transparencia, RPT de altos cargos y de personal eventual: **no** se han incorporado (identidad de personas).
- La interfaz avisa de que estar en un registro no es una señal de riesgo y de que presupuesto y contratos no se cruzan partida a partida.

## Qué falta

1. **Todo el equipo debe bajar los datos antes de seguir:** [`../LO-PRIMERO.md`](../LO-PRIMERO.md) tiene los pasos y un contador de confirmaciones (se borra al llegar a 2).
2. Revisión legal de los textos nuevos con `revisor-legal` (`AVISO_CONTEXTO`, `AVISO_REGISTROS`, `AVISO_CONVENIOS` y la pantalla nueva).
3. P-13: cruzar convenios con empresas por nombre (hoy no se hace).
4. Candidatos posteriores: planes de medios de publicidad, deuda pública, centros de atención social.

## Siguiente paso

Fusionar la rama `feat/datos-cm-abiertos` en `main` (PR) para que el resto del equipo reciba el código, la guía y `LO-PRIMERO.md`, y que cada persona ejecute `uv run python -m ojo_ciudadano.modelo.contexto`.
