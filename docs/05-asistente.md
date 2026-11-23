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

## Catálogo de datos abiertos (23-nov, D-030, bloque A)

El asistente responde también con cualquiera de los 2.276 conjuntos del catálogo de datos abiertos de la Comunidad, no solo con nuestra base. Dos herramientas nuevas:

1. `buscar_conjunto(consulta)`: BM25 sobre los metadatos del catálogo (`catalogo.py`). Devuelve los 5 conjuntos más relevantes con su nombre, título, ámbito y fecha de actualización.
2. `consultar_conjunto(conjunto, sql)`: baja el CSV, que se guarda en caché, y ejecuta una `SELECT` sobre la tabla `conjunto` en una base en memoria sin acceso a ficheros, con el mismo validador.

**Reglas (`REGLAS_CATALOGO`):**
- usar el catálogo solo para lo que no está en la base, y decir cuándo ningún conjunto encaja;
- citar el conjunto con su fecha de actualización;
- no sumar ni comparar al céntimo con contratos o subvenciones, ni deducir causas;
- avisar cuando los datos son municipales o provisionales.

**Preparación:** cada instalación baja el catálogo una vez con `uv run python -m ojo_ciudadano.asistente.catalogo`. Sin ese paso, las herramientas responden al modelo que el catálogo no está descargado.

Detalle, pruebas y resultados en [14-rag-documental.md](14-rag-documental.md).

## Búsqueda por palabras en títulos (23-nov, D-030, bloque A)

Herramienta `buscar_texto(consulta, en)` (`texto.py`), con `en` = `contrato`, `convenio` o `convocatoria`:
- BM25 de DuckDB, con raíces en español y sin tildes, sobre la tabla derivada `busqueda_texto`: 1.361.618 títulos con su índice guardado en la base.
- **Exige todas las palabras.** Sin esa condición, «ambulancias transporte sanitario» contaba cualquier título con «transporte».
- **Mejora a ILIKE:** «ambulancias» encuentra 120 contratos frente a 73.

**Qué devuelve:**
- un resumen por fuente: número de títulos y, en contratos, el importe sin IVA de PLACSP y el importe con IVA del portal, por separado;
- en convocatorias, las concesiones y el importe;
- los 20 títulos más relevantes con su enlace oficial.

**Conexión:** la de solo lectura carga `fts` antes de cerrar el acceso a ficheros (`sql_seguro.conexion_lectura`).

**Construir** con la interfaz cerrada, tras regenerar la base: `uv run python -m ojo_ciudadano.asistente.texto`. Sin la tabla, la herramienta le dice al modelo que use `consultar_sql` con ILIKE.

**Reglas:**
- una búsqueda por alternativa, sin sumar coincidencias repetidas;
- decir que cuenta títulos que mencionan las palabras;
- no sumar importes con y sin IVA.

**Revisión de `revisor-legal` de la búsqueda por palabras (23-nov), aplicada:**
- **Títulos con personas:**
  - los títulos de contratos con un adjudicatario persona física (28.258) se muestran como «Con una persona física: título no mostrado»;
  - lo mismo con los convenios con firmantes no guardados por no ser entidades (353);
  - esas filas siguen contando en el resumen.
- **Búsquedas de personas:** la herramienta no se usa con nombres de personas. B-27 lo comprueba: el modelo se niega y ofrece el dato agregado.
- **Presentación:**
  - `relevancia_busqueda`, con la aclaración de que no es un indicador de riesgo;
  - fuentes con su nombre oficial;
  - criterio de B-26 con búsquedas separadas, sin sumarlas, y con la cita.

## Datos de D-027 a D-029 en el asistente (23-nov, D-031)

- `contrato_financiacion`, `encargo` y `recurso_especial` ya estaban en la lista permitida. Ahora se añaden `anomalia_encargo` (encargos atípicos) y `anomalia_validacion` (comprobación con los recursos y los fondos UE), con sus reglas de lenguaje.
- `buscar_texto` admite `en = "encargo"`: busca en los títulos de los encargos y resume su número y su importe con IVA.
- **Batería:** de 27 a 30 preguntas.
  - B-28: órganos con más contratos con fondos europeos.
  - B-29: medios propios con más importe encargado.
  - B-30: proporción de recursos estimados por acto recurrido.

## Pliegos y resoluciones del Tribunal (23-nov, D-030 bloques B y C, D-032)

Dos herramientas nuevas (`asistente/documentos.py`):

1. `buscar_en_documento(identificador, consulta, tipo)`:
   - busca en los pliegos de una licitación de PLACSP (`contrato_documento`: `pcap` y `ppt`) o en el PDF de una resolución del Tribunal (`tacpcm:<n>/<año>`);
   - el PDF se baja la primera vez a `data/raw/documentos/`, se parte en páginas y se buscan las 4 más parecidas con BM25;
   - devuelve, por página, el extracto (1.500 caracteres como mucho) y el enlace al PDF en esa página (`…#page=N`);
   - una licitación del portal regional que duplica una de PLACSP usa los pliegos de esa.
2. `buscar_resoluciones(consulta, tipo_resolucion)`:
   - busca en el texto de todas las resoluciones (tabla derivada `resolucion_pagina`, no consultable por SQL);
   - devuelve las 6 más parecidas con su mejor página, su tipo, el acto recurrido y el contrato enlazado;
   - «Estimatoria» incluye las parciales y no trae las desestimatorias.

**Reglas** (`REGLAS_DOCUMENTOS`):
- responde solo con lo que dicen los extractos, cita el documento y la página;
- un pliego da contexto, no confirma ni descarta una señal, y no se valora si lo alegado es suficiente;
- una estimatoria no es una sanción, y una desestimatoria no significa que el contrato «esté bien»;
- sin nombres de personas, y las herramientas son para temas, no para personas.

**Protección de datos (D-032):**
- al extraer el texto se tapan DNI, NIE, nombres con tratamiento y firmas;
- las páginas «en nombre propio» no se muestran;
- las búsquedas con un nombre con tratamiento o un DNI se rechazan;
- si la respuesta solo usa documentos, cada cifra tiene que estar en un extracto.

**Web:**
- **Pantalla «Asistente»:** cada búsqueda en documentos muestra la página, el extracto, el botón «Abrir el PDF oficial en esta página», la fuente y la fecha.
- **Ficha de contrato** (alertas, empresa, órgano):
  - enlaces a los pliegos con su fuente y fecha;
  - botón «¿Qué dice el pliego?», que abre el asistente con la pregunta escrita según las señales del contrato (R-01 solvencia y criterios, R-02 supuesto alegado, R-05 modificaciones, R-06 ofertas anormalmente bajas).

**Batería:**
- B-31 (supuesto de un negociado sin publicidad, buscando antes el contrato);
- B-32 (la pregunta del botón);
- B-33 (resoluciones estimatorias sobre criterios de juicio de valor);
- B-34 (límites: nombres de personas en una resolución).
- Las de documentos aciertan si se lee el documento esperado, y hay aviso si no se cita la página.
