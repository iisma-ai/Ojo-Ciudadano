# 14 · RAG: datos nuevos, catálogo de la Comunidad y documentos (investigación del 23-nov)

> **Estado (23-nov, noche):** el **bloque A (RAG de catálogo) está implementado** en la rama `feat/rag-catalogo` y pasó el control: 4 de 4 preguntas de catálogo bien con `gpt-6.1-terra`. Ver «Bloque A: implementado» al final. El bloque B (pliegos) sigue como propuesta.

El asistente de texto a SQL ya está conectado (D-010, rama `feat/asistente-openrouter`). Este documento recoge la investigación del 23-nov para decidir qué recupera la segunda parte del asistente, el **RAG**, y cómo. Es el recorte n.º 2 del plan. Decisión propuesta: [D-030](decisions.md).

**Resumen:**
- El núcleo del proyecto, el **catálogo de datos abiertos** de la Comunidad, son **tablas**: 2.231 de sus 2.276 conjuntos son CSV o JSON, y solo 12 tienen algún PDF. El RAG que más aporta no busca en documentos, sino **en el catálogo**:
  1. encuentra el conjunto que responde a la pregunta;
  2. baja su CSV;
  3. el modelo lo consulta con SQL de solo lectura, como ya hace con nuestra base.
  - Está probado de punta a punta con datos reales.
- La parte de **documentos** queda para los **pliegos** de PLACSP, que explican las señales, y después para las **resoluciones del TACPCM** (D-029).

## 1. Qué datos nuevos hay

Los datos nunca se suben a GitHub (`data/` está en `.gitignore`). Lo que hay en GitHub es el código para bajarlos y su documentación:

| Datos | Dónde | Tipo | Qué hacer con ellos en el asistente |
| --- | --- | --- | --- |
| **D-024 · Contexto de la Comunidad:** `serie_cm` (79.226 filas, 25 series), `presupuesto_organo` (2.539), `convenio` (4.914), `entidad_registro` (6.625), `plantilla_organismo` (26) | `main`. Cargado y comprobado el 23-nov («Coincide con la referencia del equipo») | Tablas del catálogo y del Portal de Transparencia | Ya son consultables por SQL: están en `TABLAS_PERMITIDAS`. No necesitan RAG. El texto de `convenio.titulo` se beneficia de la búsqueda textual (sección 4) |
| **D-027 · Fondos europeos** (`contrato_financiacion`: 991 expedientes, 548 del PRTR) | `fix/relleno-y-referencia-r01`, sin fusionar | Tabla de PLACSP | SQL; ya está en la lista permitida de esa rama |
| **D-028 · Encargos a medios propios** (`encargo`: 2.405 encargos, 740,2 M€ con IVA) | Misma rama | Tabla, CSV exportado a mano | SQL, diciendo que no son contratos |
| **D-029 · Recursos ante el TACPCM** (`recurso_especial`: 1.097 resoluciones, con enlace a la ficha y al PDF) | Misma rama | Tabla, más **un PDF por resolución** | Los **PDF** sí son candidatos a RAG documental (sección 3): explican por qué se estimó o desestimó cada recurso |
| X-04 · Referencias de la UE y España (Single Market Scoreboard, Tribunal de Cuentas Europeo) | `docs/13-fuentes-externas.md`, misma rama | Cifras en la ayuda de R-01 | Ninguno: son texto fijo de la interfaz |
| **Catálogo de datos abiertos completo** (2.276 conjuntos, metadatos y CSV) | No incorporado: solo las 25 series y 5 conjuntos de D-024 | Metadatos y tablas | **RAG de catálogo** (sección 2): el núcleo |
| Pliegos de PLACSP (PCAP y PPT) | No incorporado: el Atom los enlaza y la ingesta no los guarda | PDF | **RAG documental** (sección 3) |

D-024 descartó expresamente la agenda de Gobierno, las cuentas anuales y los informes de fiscalización en PDF, por no tener «estructura útil antes de la demo». En el catálogo solo hay 12 conjuntos con PDF, y ninguno trata de gasto o control salvo el de solicitudes de transparencia, que tiene personas físicas.

## 2. RAG de catálogo: el núcleo

### Qué se ha comprobado con la API real (23-nov)

1. **Metadatos ricos.** De los 2.276 conjuntos:
   - 2.097 son del Instituto de Estadística y 179 de la Comunidad;
   - 2.268 tienen etiquetas, con una mediana de 14;
   - las descripciones tienen una mediana de 20 palabras;
   - traen extras útiles: consejería, unidad, fecha de actualización y frecuencia;
   - el 97 % se modificó en 2026.
2. **El buscador del catálogo no sirve para el asistente.** Para «contratos menores sanidad» devuelve el registro de carnicerías, abortos voluntarios y ayudas al alquiler.
3. **Un índice BM25 propio** (DuckDB `fts`, raíces en español, sin dependencias nuevas) sobre título, descripción, etiquetas, temas y extras acierta el conjunto en **6 de 8 preguntas**:

   | Pregunta | Primer resultado |
   | --- | --- |
   | gasto sanitario por habitante | Indicadores de gasto, y Gasto sanitario público en 3.º |
   | presupuesto de educación por consejería | Presupuestos Generales Iniciales por clasificación orgánica |
   | ayudas de la Unión Europea recibidas | Ayudas procedentes del Presupuesto General de la UE |
   | personal de la administración autonómica | Personal de la Administración Autonómica por sexo y tipo |
   | listas de espera quirúrgica hospitales | Lista de espera quirúrgica por hospitales |
   | contratos administrativos por procedimiento | Contratos administrativos de la Comunidad por procedimientos de adjudicación |
   | contratos menores sanidad | *(no existe ese conjunto: correcto decirlo)* |
   | deuda pública de la Comunidad | *(no está en el catálogo; D-024 lo dejó fuera)* |

4. **La consulta remota del catálogo** (`datastore_search_sql`, SQL de solo lectura sobre 2.361 recursos) **falla con columnas con tilde** («Año», «Código territorio»), tanto por GET como por POST. Sin tildes funciona. Por eso no se usa la consulta remota.
5. **Descargar el CSV bajo demanda es barato:** de 2.338 CSV, la mediana ocupa 42 KB y el 90 % baja de 1,2 MB. Solo un caso extremo llega a 88,7 MB. El total, 1,9 GB, no se baja entero.
6. **Prueba de punta a punta.** Pregunta: «¿Qué hospitales tienen más pacientes en lista de espera quirúrgica en el último año disponible?»
   1. BM25 encuentra «Lista de espera quirúrgica por hospitales».
   2. Se baja el CSV: 638 filas.
   3. `gpt-6.1-terra` escribe el SQL de DuckDB y responde: «En 2025: Hospital Universitario 12 de Octubre, 8.556; Ramón y Cajal, 8.256; La Paz, 8.197…», con la fuente y la fecha.
   4. Coste: **0,0028 USD**.

### Cómo funcionaría

**Dos herramientas nuevas del agente:**
- `buscar_conjunto(consulta)`:
  - BM25 sobre la tabla local `catalogo_conjunto`, una fila por conjunto con su título, descripción, etiquetas, temas, consejería, URL, recurso CSV y fecha de actualización;
  - devuelve los 5 mejores con sus columnas;
  - la tabla se rehace con 3 peticiones a `package_search`, de 1.000 conjuntos cada una.
- `consultar_conjunto(nombre, sql)`:
  - baja el CSV del conjunto si no está en caché (`data/raw/catalogo/`), con límite de tamaño de unos 20 MB y solo del dominio `datos.comunidad.madrid`;
  - lo carga en una tabla temporal `conjunto` de una conexión en memoria;
  - ejecuta el SQL del modelo con el validador de `sql_seguro` (una sola `SELECT`, solo la tabla `conjunto`, sin funciones de fichero);
  - devuelve como mucho 50 filas, marcadas como datos.

**Reglas nuevas:**
- **Cita:** cada respuesta del catálogo cita el conjunto, con su enlace y la fecha de actualización del catálogo.
- **Sin mezclas:**
  - no se mezcla con nuestras tablas de contratos en una misma cifra;
  - no se presenta como causa: «el hospital con más lista de espera es el que más contrata» no se puede decir.
- **Fuera de alcance:** los datos municipales (D-001), que en el catálogo son muchos.
- **Datos provisionales:** se avisa cuando la columna «Estado dato» lo indica.

**Precarga para la demo:** los CSV de las preguntas de demo van en caché, para que la demo no dependa de la red.

### Qué aporta

- **Uso de los datos abiertos de la Comunidad, que es el criterio del jurado.** Hoy usamos 25 series y 5 conjuntos; con esto, el asistente puede responder con cualquiera de los 2.276.
- **Preguntas nuevas:**
  - «¿cuánto gasta la Comunidad en sanidad por habitante?»;
  - «¿cuántos contratos administrativos declara la Comunidad por procedimiento?», que además **valida nuestros totales** contra la estadística oficial;
  - «¿cuánto personal tiene la administración autonómica?»;
  - «¿cómo ha evolucionado la ayuda de la UE?».
- Sin dependencias nuevas: BM25 de DuckDB, `httpx` y nuestro validador.

## 3. RAG documental: pliegos y resoluciones

### Pliegos de PLACSP (comprobado el 23-nov)

- **Enlazados:** en el Atom de PLACSP de enero de 2025, 2.283 de las 2.357 entradas de la Comunidad (97 %) traen el pliego administrativo (PCAP), y 2.215 (94 %) el técnico (PPT). Son PDF en `contratos-publicos.comunidad.madrid` y se bajan sin captcha.
- **Legibles:** tienen texto digital, con 1 página sin texto de 146 en 3 PDF. Son largos: de 15 a 84 páginas, hasta 50.000 tokens. Hay que recuperar páginas; no se pueden pasar enteros al modelo.
- **BM25 por páginas:** en las 5 preguntas, la página buena sale entre las 3 primeras, y en 4 es la primera.
- **Prueba con R-02.** Pregunta: «¿qué supuesto alega el pliego para adjudicar sin publicidad?» Respuesta: «ausencia de competencia por razones técnicas, artículo 168.a.2 de la LCSP (págs. 6 y 12); los fragmentos no explican cuáles son esas razones». Costó 0,0014 USD.
- **Valor:** da la explicación del propio expediente junto a la señal:
  - R-02: el supuesto alegado;
  - R-01: la solvencia y los criterios;
  - R-05: las modificaciones previstas;
  - R-06: el umbral de baja anormal.
- **Límite:**
  - Solo cubre las licitaciones de PLACSP: 3.902 de las 11.250 señales R-02, 4.819 de R-01, 177 de R-05 y 1.065 de R-06.
  - El portal regional no enlaza pliegos de emergencias ni de «otro procedimiento», y los menores no tienen pliego.

### Resoluciones del TACPCM (D-029)

- Son 1.097 resoluciones de 2023 a 2026, cada una con su PDF, y algunas enlazadas con un contrato concreto.
- **Valor:** son la explicación jurídica oficial de por qué un pliego o una adjudicación no se ajustaban a derecho. El 30 % de los recursos contra pliegos se estimaron total o parcialmente. Ninguna otra fuente nos da esto.
- **Cautela:** D-029 decidió **no guardar el resumen** porque nombra empresas y puede nombrar personas (D-007). Indexar los PDF necesita antes revisión de `revisor-legal` y filtros: retención de DNI y NIE, y no dar nombres de personas. Además, la rama de D-029 no está en `main`.

### Lo que no se recomienda

- **Informes de la Cámara de Cuentas:** no hay ninguno de contratación de 2023 a 2026.
- **Embeddings:** OpenRouter no tiene modelos de embeddings. Uno local obliga a instalar torch, y BM25 basta con el vocabulario de los catálogos y de los pliegos.

## 4. Búsqueda textual en nuestras tablas (opcional, pequeño)

Hoy el modelo busca texto con `ILIKE` en `contrato.titulo`, `convenio.titulo` o las convocatorias de la BDNS. Un índice BM25 de DuckDB sobre esos campos daría tres mejoras:
- raíces en español: «ambulancias» encuentra «ambulancia»;
- sin tildes;
- resultados ordenados por relevancia.

Son unas 2 h. Solo merece la pena si sobra tiempo: `ILIKE` ya resuelve los casos de la demo.

## 5. Plan de desarrollo, por prioridad

| Fase | Qué | Horas | Resultado comprobable |
| --- | --- | --- | --- |
| **A1** | Tabla `catalogo_conjunto` desde la API (aditiva, `sql/esquema/00x_catalogo.sql`) e índice BM25 | 1,5 | Las 8 preguntas de la sección 2, con al menos 6 aciertos |
| **A2** | `buscar_conjunto` y `consultar_conjunto` con caché, límites y validador; reglas e instrucciones | 2,5 | La pregunta de las listas de espera respondida en la interfaz |
| **A3** | Batería de 4 preguntas de catálogo (B-21 a B-24), incluida una de validación contra la estadística oficial de contratos; `revisor-legal`; documentación | 2 | Aciertos; revisión sin bloqueos |
| **B1** | Enlaces de los pliegos en la ingesta de PLACSP: tabla `contrato_documento` y cobertura en los 47 meses | 3 | % de licitaciones con PCAP |
| **B2** | `buscar_en_pliego`: descarga con caché, páginas con `pypdf` e índice BM25; pantalla con enlace a la página | 5 | Una pregunta de R-02 respondida con cita y enlace |
| **B3** | 3 preguntas de pliego en la batería y precarga de unos 50 pliegos para la demo | 2 | La demo funciona sin red |
| C | PDF del TACPCM, cuando D-029 esté en `main` y `revisor-legal` lo apruebe | 4 | Después de la entrega |
| D | Búsqueda textual en títulos (sección 4) | 2 | Solo si sobra tiempo |

**Calendario:**
- **Bloque A (catálogo, 6 h):** 23-nov por la tarde y 24-nov por la mañana.
  - **Punto de control el 24-nov a las 12:00:** si la herramienta no está integrada o falla en más de 1 de las 4 preguntas, se desactiva (se quita de la lista de herramientas del agente) y queda como trabajo futuro.
- **Bloque B (pliegos, 10 h):** solo si A está aprobado antes de las 12:00 del 24-nov y alguien puede dedicarle la tarde.
  - **Punto de control el 24-nov a las 20:00.**
  - Hace falta avisar antes a quien lleva la ingesta de PLACSP.
- **El 25 no se añaden funciones** (plan).

**Coste en OpenRouter:**
- unos 0,003 USD por pregunta de catálogo y unos 0,002–0,005 USD por pregunta de pliego;
- la batería nueva cuesta menos de 0,10 USD;
- en lo que va del día se han gastado 0,47 USD, y quedan unos 0,93.

## 6. Cómo se vería en la web

- **Pantalla «Asistente»:** la respuesta, con un desplegable por fuente usada.
  - **De nuestra base:** la tabla y el SQL, como ahora.
  - **Del catálogo:** nombre del conjunto, enlace a `datos.comunidad.madrid`, fecha de actualización, la tabla de filas y el SQL aplicado al CSV.
  - **De un pliego:** documento, página, extracto y enlace al PDF oficial en esa página (`…pdf#page=6`).
- **Ficha de contrato** (cuando haya bloque B): debajo de cada señal R-01, R-02, R-05 o R-06 de una licitación de PLACSP, un botón «¿Qué dice el pliego?». Abre el asistente con la pregunta ya escrita.
- **Preguntas guiadas:** 2 nuevas con el catálogo, entre ellas «¿Coinciden nuestros contratos con la estadística oficial de la Comunidad?».

## 7. Riesgos y medidas

| Riesgo | Medida |
| --- | --- |
| Instrucciones escondidas en un CSV o en un PDF (K-13) | El texto se marca como datos; las herramientas solo leen; los filtros de salida no cambian |
| Personas físicas (D-007): firmas en los pliegos, nombres en las resoluciones, conjuntos con datos personales | Retención si hay DNI o NIE en los datos o en los fragmentos; regla de no dar nombres; los PDF del portal vienen anonimizados; se excluyen los conjuntos que D-024 descartó por personas físicas |
| Conjuntos municipales (fuera de alcance, D-001) | Se marcan en `catalogo_conjunto` por su ámbito (extra «Ámbito»), y la regla obliga a avisar de que son de municipios |
| Cifras que se mezclan entre fuentes o se leen como causa | Regla: no sumar con contratos ni deducir causas; aviso como `textos.AVISO_CONTEXTO` |
| Red caída en la demo | Precarga en caché de los CSV y pliegos de la demo |
| Cargar los portales | Una descarga cada vez, con pausa, solo lo que se pregunta; caché local |
| Muestras pequeñas (8 preguntas de catálogo, 3 PDF) | Se confirman en A1, A3 y B1 antes de seguir |

## Recomendación

1. **Hacer el bloque A (RAG de catálogo).** Es el más alineado con el núcleo del proyecto y con el criterio del jurado: uso de los datos públicos de la Comunidad. Está probado de punta a punta, no añade dependencias y son 6 horas.
2. **El bloque B (pliegos) solo si A pasa el control del 24-nov a las 12:00.** Aporta lo que más necesitan las señales, la explicación del expediente, pero son 10 horas más el mismo día de la prueba A-11.
3. **El bloque C (TACPCM), después de la entrega,** con revisión legal.

## Bloque A: implementado (23-nov)

**Diferencias con lo previsto:**
- **Sin tabla `catalogo_conjunto` ni cambio de esquema.**
  - Los metadatos se guardan en `data/raw/catalogo/paquetes.json` (`uv run python -m ojo_ciudadano.asistente.catalogo`, 3 peticiones).
  - El índice BM25 se crea en memoria al usarlo por primera vez: 2.228 conjuntos con CSV en 2,2 s.
  - Si la extensión `fts` no se puede cargar, se buscan palabras en común.
- **Conjuntos excluidos:** los que D-024 descartó por tener personas concretas (altos cargos, personal eventual, solicitudes de transparencia, asociaciones).
- **Límite de llamadas del agente:** 8 por pregunta. Buscar, ver las columnas, consultar y corregir agotaban las 6.

**Piezas:**
- `asistente/catalogo.py`:
  - `buscar` y `para_modelo`;
  - `consultar`: CSV en caché, solo del dominio del catálogo y de 25 MB como máximo, cargado en memoria;
  - después, `SET enable_external_access = false` y el validador de `sql_seguro` con la tabla `conjunto` como única permitida.
- `sql_seguro.validar` y `sql_seguro.ejecutar` admiten una lista de tablas propia.
- **Agente:**
  - herramientas `buscar_conjunto` y `consultar_conjunto`;
  - formato neutro de la llamada con `herramienta` y `argumentos`;
  - reglas del catálogo (cita, sin mezclar con contratos ni deducir causas, aviso de datos municipales y provisionales);
  - la regla de cifras admite las dos herramientas.
- `openrouter.py` ofrece las tres herramientas y traduce sus llamadas.
- **Pantalla «Asistente»:** cada consulta al catálogo muestra el conjunto con su enlace, la fecha de actualización, el aviso municipal si toca, los datos y el SQL.
- **Batería:** B-21 a B-24. Aciertan si consultan el conjunto esperado o uno equivalente.

**Resultados con `gpt-6.1-terra`:**

| Pregunta | Resultado |
| --- | --- |
| B-21 · lista de espera por hospital | Bien: 2025, 12 de Octubre 8.556, Ramón y Cajal 8.256… con la fuente |
| B-22 · personal de la Administración autonómica | Bien: 203.723 personas a 1-1-2026, con otro conjunto oficial equivalente |
| B-23 · contratos por procedimiento (estadística oficial) | Bien |
| B-24 · ayudas del presupuesto de la UE | Bien |
| B-05 y B-17 (comprobación de que no usa el catálogo donde no toca) | Bien |

- La primera pasada tenía un fallo: B-21 tenía las cifras y no las daba, porque la regla antigua solo admitía las de `consultar_sql`. Está corregido.
- **Coste:** de 0,007 a 0,012 USD por pregunta de catálogo (de 4 a 6 llamadas). Las dos pasadas costaron 0,077 USD.
- **Tests:** 11 en `tests/asistente/test_catalogo.py`, sin red: búsqueda, consulta, tablas no permitidas, ficheros bloqueados, dominio ajeno, agente de punta a punta y adaptador.
