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

- `src/ojo_ciudadano/asistente/agente.py` (21-nov): **agente independiente del proveedor**. El modelo es cualquier función `Modelo(instrucciones, mensajes) → LlamadaSQL | TextoFinal`, con la conversación en un formato neutro (`usuario`, `llamada`, `resultado`, `modelo`) y la herramienta descrita en JSON Schema (`HERRAMIENTA_SQL`).
  - `instrucciones(con)` arma el prompt de sistema (~4.300 tokens con la base real). Incluye las reglas de respuesta (también la de `anomalia_resultado`), las limitaciones de los datos (IVA por fuente, año, P-12, consejerías, personas físicas), los indicadores (de `app/textos.py`), las reglas de SQL, el esquema y los 4 ejemplos de demo. El esquema se lee de la base, con los comentarios de columna del DDL.
  - `responder` hace el bucle: hasta 5 consultas, y los errores del validador vuelven al modelo para que corrija. Al modelo le llegan como mucho 50 filas, en JSON y marcadas como datos, con los seudónimos ya ocultos. Admite historial para preguntas de seguimiento. Una pregunta con DNI o NIE no llega al modelo, porque el proveedor es externo.
  - **Retención** (`Respuesta.retencion`, revisión de `revisor-legal` del 21-nov): la interfaz no muestra la respuesta, y explica por qué, en tres casos. Si hay un DNI o NIE en el texto o en los datos de alguna consulta. Si hay un término acusatorio de la tabla de docs/07 fuera de una negación («atípico no significa irregular» sí se puede decir). Si da cifras sin ninguna consulta detrás.
  - `pasar_bateria` pasa las 20 preguntas y las evalúa con `bateria.evaluar`.
  - `modelo_configurado()` devuelve el adaptador de OpenRouter si hay clave, o `None` si no la hay (ver «Modelo conectado»).
- Pantalla **«Asistente»** (`app/paginas/asistente.py`): chat con historial y, por cada consulta, sus datos (tabla compartida con preguntas guiadas en `app/tablas.py`, con enlace oficial) y su SQL. Avisa de que las respuestas las redacta un modelo de lenguaje y pueden contener errores, y pide no escribir datos personales. Avisa también si una consulta no trae `fuente` o el enlace de cada contrato. Sin modelo, lo dice y remite a las preguntas guiadas.

## Modelo conectado (23-nov, D-010)

- **Proveedor y modelos:**
  - OpenRouter, con `openai/gpt-6.1-terra` de principal y `anthropic/claude-haiku-5.5` de respaldo;
  - elección y resultados de la batería en [D-010](decisions.md);
  - se cambia con `LLM_MODEL` en `.env`.
- **`asistente/openrouter.py`:**
  - lee `OPENROUTER_API_KEY` del entorno o de `.env` y nunca la imprime;
  - traduce la conversación neutra al formato de OpenAI, enlazando cada `llamada` con su `resultado`;
  - interpreta la llamada a `consultar_sql`; si los argumentos llegan rotos, el SQL vacío vuelve al validador;
  - temperatura 0, una consulta por vuelta y caché de las instrucciones;
  - acumula el coste (`Gasto`).
  - Comprobación de la clave y del saldo: `uv run python -m ojo_ciudadano.asistente.openrouter`.
- **`asistente/comparar_modelos.py`:**
  - pasa la batería, o parte de ella, a varios modelos, con tope de gasto por modelo y en total;
  - guarda cada respuesta en `data/evaluaciones/`, que no se sube.
- **Cambios en el agente:**
  - **Reescritura:** si el texto tiene términos que el filtro retendría (casi siempre en negaciones largas: «no puedo decir si una empresa es corrupta»), se pide al modelo una sola reescritura. El filtro no cambia: si insiste, se retiene igual.
  - **Cifras sin consulta:** se admiten solo los umbrales de las definiciones de los indicadores («más del 50 %» de R-04) y solo si la respuesta nombra el indicador (R-0x). Aun así queda un aviso. Una cifra atribuida a una empresa o un órgano sin consulta se sigue reteniendo (revisión de `revisor-legal` del 23-nov, con test).
  - **Si falla la reescritura,** queda el texto original y el filtro lo retiene.
  - **Instrucciones nuevas:**
    - no escribir los términos de la tabla de lenguaje, ni siquiera negados;
    - en los rankings por puntuación, solo órganos o empresas con al menos 100 contratos;
    - al agrupar por año, filtrar de 2023 a 2026, porque hay unos 4.000 contratos con años anteriores o mal escritos en origen, como «23» o «206».
- **Evaluación (`bateria.coincide` y `bateria.evaluar`):**
  - vale cualquiera de las consultas del modelo, no solo la última;
  - se admiten hasta 5 filas de más y rankings más cortos de al menos 3 filas que coincidan con el principio de la referencia;
  - el código de la fuente equivale a su nombre, y el año como texto equivale al año como número.
  - Aun así, conviene leer las respuestas: un dato correcto puede presentarse de otra forma (el mes como fecha, nombres en vez de NIF).
- **Pantalla:** si el proveedor falla (red, saldo), se avisa y se remite a las preguntas guiadas, sin mostrar el error técnico.

## Pendiente

- **RAG documental:** propuesta de no hacerlo y aplicar el recorte 2 del plan. Queda por confirmar con el equipo.
- **Validar más:** repetir la batería si cambian las tablas o las instrucciones (por ejemplo, `contrato_financiacion` de D-026). Una pasada con terra cuesta unos 0,15 USD.

## Gráfico en las respuestas (D-023, A-08)

Desde el 21-nov, cada respuesta del asistente muestra, debajo del texto, el gráfico de la primera consulta que se pueda dibujar (`graficos.automatico`: barras por año o ranking). Los datos y el SQL siguen en los desplegables de cada consulta.
