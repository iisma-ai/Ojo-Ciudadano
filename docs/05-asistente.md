# 05 · Asistente conversacional: texto a SQL + RAG con citas

El asistente es **un agente con dos herramientas**, no un RAG clásico. Un RAG que busca filas por similitud semántica falla justo en las preguntas que más importan aquí: sumas, rankings, filtros por fecha y comparaciones.

## Herramientas

| Herramienta | Para qué preguntas | Cómo funciona |
| --- | --- | --- |
| **Texto a SQL** | «¿Top 10 adjudicatarios de la Consejería de Sanidad en 2025?», «¿Qué órganos tienen más licitadores únicos?» | El modelo genera SQL **de solo lectura** sobre las tablas limpias, con un esquema documentado y ejemplos; la consulta **se valida antes de ejecutarse** |
| **RAG documental** | «¿Qué dijo la Cámara de Cuentas sobre los contratos de emergencia?», «¿Qué justificación da el pliego de este contrato?» | Búsqueda híbrida (BM25 + embeddings) sobre un corpus acotado: informes de fiscalización, memorias presupuestarias y pliegos de contratos con alertas |

El RAG documental es **el primer recorte** si vamos tarde (ver [08-plan.md](08-plan.md)).

## Reglas de respuesta

- Cada cifra lleva el **enlace** al contrato, la concesión o el documento de origen.
- El asistente **muestra la consulta SQL** usada, para que el usuario pueda comprobarla.
- Habla de **«indicadores de riesgo»** y nunca afirma que haya corrupción.
- Si usa `anomalia_resultado`, presenta los contratos como **«atípicos respecto a contratos similares»**: señal experimental que no suma a la puntuación; atípico no significa irregular.
- Si los datos no permiten responder, **lo dice y explica qué falta**.
- Solo responde con datos devueltos por las herramientas: **no inventa cifras**.

## Seguridad

- Conexión a DuckDB **en modo solo lectura**; validación del SQL (una sola sentencia `SELECT`/`WITH`, sin `ATTACH`, `COPY`, `INSTALL`, `PRAGMA` ni funciones de fichero).
- El corpus indexado se trata como **datos, nunca como instrucciones** (riesgo de inyección desde pliegos o informes).
- El agente no tiene herramientas que modifiquen nada.

## Preguntas de demo

1. ¿Qué empresas han recibido más contratos menores de una consejería concreta en los últimos dos años?
2. ¿Qué órganos adjudican más por procedimientos sin publicidad, en proporción a su gasto?
3. Enséñame los contratos con mayor sobrecoste por modificaciones y prórrogas.
4. ¿Qué ha recibido esta empresa de la Comunidad entre contratos y subvenciones?

Objetivo: responder bien a las 4 para el 21 de noviembre. Además, una **batería de 20 preguntas de prueba** con respuesta esperada para evaluar el asistente.

## Plan de contingencia para la demo

- Respuestas de las preguntas de demo **cacheadas**.
- **Vídeo de respaldo**.
- **Modelo alternativo** configurado.

## Estado (21-nov)

Hecho, sin depender del LLM (D-010):

- `src/ojo_ciudadano/asistente/sql_seguro.py`: **validación y ejecución** del SQL. Una sola sentencia `SELECT`; se recorre el árbol de `json_serialize_sql` y solo se admiten las tablas de `TABLAS_PERMITIDAS` (esquema y tablas de indicadores; `contrato_unico` en lugar de `contrato`), subconsultas, CTE y `VALUES`. Se rechazan funciones de tabla (`read_csv`, `glob`…), `SHOW`/`DESCRIBE`, otros esquemas (`information_schema`) y funciones como `getenv`. La conexión es de solo lectura y con `enable_external_access = false`, que no se puede reactivar desde SQL. El resultado tiene límite de 200 filas y 20 s, y los seudónimos `PF-…` se sustituyen por «Persona física (seudonimizada)». La interfaz entera usa esta conexión.
- `src/ojo_ciudadano/asistente/consultas_demo.py`: **consultas verificadas de las 4 preguntas de demo**, cada una con una nota de qué cubre y qué no. Serán los ejemplos del modelo y las respuestas de respaldo. Pregunta 4: desde el 20-nov suma contratos y subvenciones (BDNS) por fuente y año, de 2023 a 2026, sin mezclar bases.
- Pantalla **«Preguntas guiadas»** (`app/paginas/preguntas.py`): las 4 preguntas con su tabla, nota, consulta SQL y enlace al expediente cuando la respuesta es por contrato.

- `src/ojo_ciudadano/asistente/bateria.py` (21-nov): **batería de 20 preguntas de prueba** (B-01 a B-20). Son las 4 de demo, 12 de datos con SQL de referencia y 4 de límites sin SQL (lenguaje acusatorio, DNI de personas físicas, Ayuntamiento fuera de alcance e inyección). Cada una lleva criterios de lo que debe decir la respuesta. La respuesta esperada es el resultado de la referencia sobre la base del día. `evaluar` compara el SQL del modelo por valores de las columnas clave, sin importar nombres ni orden, y `revisar_texto` marca términos de la tabla de lenguaje y DNI/NIE. `uv run python -m ojo_ciudadano.asistente.bateria` ejecuta las referencias (todas < 1 s).

Limitaciones de los datos que el asistente debe explicar: las licitaciones del portal regional casi nunca traen fecha (344 de 18.777), así que no tienen año; y los menores de julio a septiembre de 2026 están incompletos (P-12).

Falta: el modelo que traduce la pregunta libre a SQL (D-010), pasarle la batería y el RAG. Desde el 21-nov, `anomalia_resultado` (D-021) está en `TABLAS_PERMITIDAS`: el asistente puede responder sobre contratos atípicos, pero cada respuesta debe decir que es una **señal experimental**, que **atípico no significa irregular** y que no suma a la puntuación (añadirlo a las instrucciones del modelo al cerrar D-010).

## Pendiente

- Proveedor y modelo de LLM: decisión **D-010 (pendiente)** en [decisions.md](decisions.md).
- Tecnología del índice híbrido (LanceDB, Chroma u otra): incluida en D-010.
