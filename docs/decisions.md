# Registro de decisiones

Aquí se apunta **toda decisión que afecte al alcance, la metodología, los datos, la arquitectura, las herramientas o el plan**. Es lo que impide que el proyecto cambie de rumbo en silencio.

## Cómo usar este fichero

- **Antes de proponer un cambio de enfoque**, comprueba si ya hay una decisión al respecto. Si la hay, respétala o propón sustituirla con una nueva entrada.
- **Nunca se borra ni se reescribe una decisión.** Si cambia, se añade una nueva que la **sustituye** y se marca la antigua como `Sustituida por D-xxx`.
- Las decisiones nuevas van **al final**, con el siguiente número libre.
- Estados: `Propuesta` (pendiente de validar por el equipo) · `Aceptada` · `Sustituida por D-xxx` · `Descartada`.
- Un agente puede registrar decisiones como `Propuesta`; las pasa a `Aceptada` una persona del equipo (o el agente, si la persona lo ha pedido explícitamente).
- Puedes usar la skill `/decision` para registrar una.

Plantilla:

```markdown
## D-xxx · Título corto
- **Fecha:** AAAA-MM-DD
- **Estado:** Propuesta | Aceptada | Sustituida por D-xxx | Descartada
- **Autor:** quién (persona o agente, y a petición de quién)
- **Contexto:** qué problema o pregunta la motiva
- **Decisión:** qué se decide, en una o dos frases
- **Alternativas consideradas:** y por qué se descartan
- **Consecuencias:** qué cambia, qué documentos se actualizan, qué se recorta
```

---

## D-001 · Alcance del MVP: contratos y subvenciones de la Comunidad de Madrid
- **Fecha:** 2026-11-15
- **Estado:** Aceptada
- **Autor:** Propuesta inicial (El Harrak)
- **Contexto:** 11 días y 4 personas para DataMad 2026. Seguir «cada euro» desde el presupuesto no es posible con los datos disponibles.
- **Decisión:** El MVP cubre **contratos** (núcleo) y **subvenciones** de los órganos de la Comunidad de Madrid. Presupuesto y altos cargos son contexto, mostrados por separado.
- **Alternativas consideradas:** Incluir trazabilidad partida → contrato (los datos no lo permiten); incluir ayuntamientos y otras administraciones (alcance excesivo, queda tras el datatón).
- **Consecuencias:** Ver [02-fuentes-datos.md](02-fuentes-datos.md) y [08-plan.md](08-plan.md). Las subvenciones son el 4.º recorte de la lista.

## D-002 · Indicadores de riesgo, no detección de corrupción
- **Fecha:** 2026-11-15
- **Estado:** Aceptada
- **Autor:** Propuesta inicial
- **Contexto:** El mayor riesgo del proyecto es acusar en falso (derecho al honor, difamación) y la percepción partidista.
- **Decisión:** La plataforma calcula y comunica **indicadores de riesgo** con metodología pública; nunca afirma que haya corrupción. Cada alerta explica qué la disparó y enlaza al expediente.
- **Alternativas consideradas:** Clasificador de «contratos corruptos» (sin etiquetas fiables, riesgo legal alto).
- **Consecuencias:** Regla de lenguaje obligatoria en interfaz, asistente, README y presentación ([07-riesgos.md](07-riesgos.md)).

## D-003 · Python + polars para ingesta, DuckDB como base analítica
- **Fecha:** 2026-11-15
- **Estado:** Aceptada
- **Autor:** Propuesta inicial
- **Contexto:** El equipo domina Python; necesitamos SQL analítico sin montar servidores y fácil de compartir.
- **Decisión:** Ingesta en Python con polars (pandas si una librería lo exige) y lxml para el Atom de PLACSP. Base analítica en **un único fichero DuckDB**.
- **Alternativas consideradas:** PostgreSQL (requiere servidor), solo ficheros Parquet sin motor SQL (peor para texto a SQL).
- **Consecuencias:** El fichero `.duckdb` no se sube al repo; se regenera con el pipeline.

## D-004 · Indicadores como SQL versionado en el repositorio
- **Fecha:** 2026-11-15
- **Estado:** Aceptada
- **Autor:** Propuesta inicial
- **Contexto:** El jurado y los usuarios deben poder auditar cómo se calcula cada señal.
- **Decisión:** Cada indicador es un fichero SQL en `sql/indicadores/`, con ID `R-xx`, definición en [04-indicadores-riesgo.md](04-indicadores-riesgo.md) y test con datos sintéticos.
- **Alternativas consideradas:** Lógica en Python/pandas (menos legible para no programadores), librería Cardinal de OCP (requiere datos en OCDS; queda como línea futura).
- **Consecuencias:** Cambiar un umbral o definición requiere una nueva decisión.

## D-005 · Streamlit para la interfaz del MVP
- **Fecha:** 2026-11-15
- **Estado:** Aceptada
- **Autor:** Propuesta inicial
- **Contexto:** Paneles y chat en pocos días.
- **Decisión:** Interfaz en **Streamlit**. Migrable después del datatón.
- **Alternativas consideradas:** React + API (más tiempo), Dash (menos soporte de chat).
- **Consecuencias:** Toda la app en Python; un solo entorno uv.

## D-006 · Ventana temporal 2023–2026
- **Fecha:** 2026-11-15
- **Estado:** Aceptada
- **Autor:** Propuesta inicial
- **Contexto:** Cambios de estructura de ficheros entre años y cobertura desigual.
- **Decisión:** El MVP trabaja con datos de **2023 a 2026**. Los huecos se documentan en la propia plataforma.
- **Alternativas consideradas:** Desde 2012 (PLACSP lo permite, pero multiplica el trabajo de normalización).
- **Consecuencias:** Ampliar la ventana es una línea futura.

## D-007 · Sin fichas de personas físicas
- **Fecha:** 2026-11-15
- **Estado:** Aceptada
- **Autor:** Propuesta inicial
- **Contexto:** RGPD: autónomos adjudicatarios y beneficiarios personas físicas.
- **Decisión:** No se crean fichas de personas físicas; sus NIF se agregan o seudonimizan. Altos cargos solo con lo que la ley obliga a publicar. No se analizan retribuciones individuales de funcionarios.
- **Alternativas consideradas:** Mostrar todo lo publicado (legal en origen, pero la agregación crea un riesgo nuevo).
- **Consecuencias:** La normalización debe distinguir personas físicas y jurídicas por NIF (P-07).

## D-008 · uv para entorno y dependencias; Python 3.12
- **Fecha:** 2026-11-15
- **Estado:** Aceptada
- **Autor:** Claude (agente), a petición de El Harrak
- **Contexto:** 4 personas deben tener el mismo entorno desde el primer día.
- **Decisión:** **uv** gestiona Python (3.12, fijado en `.python-version`), dependencias (`pyproject.toml` + `uv.lock`, ambos versionados) y ejecución (`uv run`). No se usa `pip install` directamente. Calidad: `ruff` (lint/formato) y `pytest`.
- **Alternativas consideradas:** pip + requirements.txt, Poetry, conda.
- **Consecuencias:** Instalar = `uv sync`. Añadir dependencia = `uv add <paquete>` (o `uv add --dev`). Las dependencias del asistente se añaden al cerrar D-010.

## D-009 · Documentación primero y estructura para agentes
- **Fecha:** 2026-11-15
- **Estado:** Aceptada
- **Autor:** Claude (agente), a petición de El Harrak
- **Contexto:** Colaboran 4 personas y varios agentes de IA en sesiones cortas. Sin memoria escrita, se repite trabajo y el plan se diluye.
- **Decisión:** `docs/` es la memoria del proyecto: plan ([08-plan.md](08-plan.md)), decisiones (este fichero), preguntas abiertas y bitácora por sesión (`docs/bitacora/`). `CLAUDE.md` obliga a los agentes a leerla, respetar el plan y documentar todo lo que hacen. Se añaden skills, comandos y subagentes en `.claude/`. El documento de propuesta original queda fuera del repo (en `.gitignore`); su contenido está en `docs/`.
- **Alternativas consideradas:** Wiki de GitHub (fuera del flujo de los agentes), un único documento largo (conflictos de merge).
- **Consecuencias:** Cada sesión termina con entrada en la bitácora (`/cerrar-sesion`).

## D-010 · Proveedor de LLM e índice híbrido del asistente
- **Fecha:** 2026-11-15
- **Estado:** Aceptada el 2026-11-23 para el proveedor y los modelos (El Harrak eligió OpenRouter y pidió elegir los modelos con la batería). El índice híbrido del RAG queda **Propuesta**: no hacerlo, aplicando el recorte 2.
- **Autor:** Claude (agente), a petición de El Harrak
- **Contexto:** La propuesta dice «LLM por API con llamada a herramientas» y «LanceDB o Chroma», sin concretar. Criterios del 15-nov: buena llamada a herramientas, texto a SQL en español, coste de la demo y un modelo de respaldo (K-14). El 23-nov el equipo tiene una clave de OpenRouter con un límite de 6 USD. El presupuesto para probar es de 1,40 USD.
- **Decisión:**
  - **Proveedor:** OpenRouter, por API compatible con OpenAI. El adaptador es `asistente/openrouter.py`, sobre `httpx`; no se añaden dependencias.
  - **Modelo principal:** `openai/gpt-6.1-terra`.
  - **Respaldo:** `anthropic/claude-haiku-5.5`, de otro proveedor. OpenRouter cambia al respaldo solo si el principal falla.
  - **Cómo cambiarlo:** con `LLM_MODEL` en `.env`, sin tocar el código.
- **Resultados de la batería de 20 preguntas (23-nov):**

  | Modelo | Datos, evaluación automática | Datos, revisión a mano | Retenidas por lenguaje | Coste de las 20 | Mediana de palabras |
  | --- | --- | --- | --- | --- | --- |
  | `openai/gpt-6.1-terra` | 12/16 | 16/16 (los 4 restantes cambian la forma, no el dato) | 0 | 0,153 USD | 206 |
  | `anthropic/claude-haiku-5.5` | 13/16 | — | 4 (0 con la reescritura) | 0,037 USD | 278 |
  | `deepseek/deepseek-v4.1-flash` | 11/16 | — | 2 | 0,064 USD | 342 |

  En la primera ronda, de 6 preguntas, se descartaron `mistralai/mistral-large-4-0` (lento y con errores de SQL) y `google/gemini-3.8-flash` (el triple de caro sin mejores datos).
- **Por qué terra:** es el que mejor se entiende. Da respuestas más cortas, en lenguaje llano y con los nombres de las convocatorias traducidos, y no tuvo ninguna respuesta retenida. Cuesta unos 0,008 USD por pregunta, así que 1 USD da para unas 130 preguntas.
- **Alternativas consideradas:**
  - Haiku como principal: más barato y con la mejor nota automática, pero escribe respuestas más largas y repite las palabras de la pregunta.
  - Modelos más caros (`claude-sonnet-5.5`, `gpt-6.2-sol`, 2 USD por millón de tokens de entrada): no se probaron, por presupuesto.
- **Consecuencias:**
  - El asistente responde preguntas libres si hay `OPENROUTER_API_KEY` en `.env`; sin clave, la pantalla remite a las preguntas guiadas.
  - Para que pruebe todo el equipo, cada persona necesita la clave en su `.env`. Nunca se sube al repositorio.
  - Las pruebas y la demo gastan del saldo compartido: los resultados se guardan en `data/evaluaciones/` para no repetir llamadas.

## D-011 · Convenciones de código y colaboración
- **Fecha:** 2026-11-15
- **Estado:** Propuesta
- **Autor:** Claude (agente)
- **Contexto:** Evitar discusiones de estilo con 4 personas trabajando en paralelo.
- **Decisión:** Documentación, interfaz, mensajes de commit y comentarios en **español**. Identificadores de código en inglés salvo términos del dominio sin traducción clara (`organo`, `adjudicatario`, `cpv`, `expediente`), que se documentan en el glosario. Nombres de tablas y columnas de DuckDB en español y `snake_case`. Una rama por tarea (`feat/…`, `fix/…`, `docs/…`) y PR a `main`. Los commits no incluyen a Claude como co-autor.
  - **Ampliación (2026-11-17, a petición de El Harrak):** como trabajan varias personas a la vez, se sincroniza, se hace commit y se sube a menudo. Al empezar y antes de cada tarea: `git fetch`, revisar qué han subido los demás e integrarlo. Durante el trabajo: commits pequeños, push de la rama tras cada commit y `git merge origin/main` antes de subir (merge y no rebase en ramas ya subidas, porque nunca se fuerza el push). Ramas de menos de un día. Al cerrar, nada se queda solo en local (commit `wip:` si está a medias). Push a `main` solo si la persona lo pide. Mensajes de commit con prefijo (`feat:`, `fix:`, `docs:`, `wip:`…).
- **Alternativas consideradas:** Todo en inglés (alejaría el código del dominio y del jurado). Para git: rebase sobre `main` (historial más limpio, pero obliga a forzar el push en ramas ya subidas); commit solo al final de la sesión (más conflictos y trabajo invisible para el resto).
- **Consecuencias:** Recogido en `CLAUDE.md` (sección «Trabajo en equipo con git»), en las skills `/estado` y `/cerrar-sesion` y en el agente `guardian-plan`.

## D-012 · PLACSP como fuente principal de licitaciones; portal regional como complemento con exportación manual
- **Fecha:** 2026-11-16
- **Estado:** Aceptada (El Harrak, 2026-11-16)
- **Autor:** Claude (agente), trabajando con El Harrak
- **Contexto:** El plan daba al portal regional (F-01) el papel de fuente principal. Su exportación a CSV está protegida por captcha y limitada a 50.000 filas, así que no es reproducible por código. PLACSP (F-02) se descarga libremente y trae nº de ofertas, NIF, CPV, lotes y código de órgano, pero no contratos menores ni modificaciones o prórrogas. El catálogo CKAN (F-06) no tiene contratos a nivel de registro.
- **Decisión:** Las licitaciones se ingieren desde **PLACSP**. Del **portal regional** se toman los **contratos menores** y los **importes de modificaciones, prórrogas y liquidación**, a partir de CSV exportados a mano (una persona resuelve el captcha) y guardados en `data/raw/portal_cm/`. El captcha no se automatiza. El catálogo CKAN se usa como contexto y validación.
- **Alternativas consideradas:** Mantener el portal como fuente principal (depende entera de trabajo manual y pierde CPV, lotes y fechas); prescindir de menores y modificaciones (caerían R-03, R-05 y las preguntas de demo 1 y 3).
- **Consecuencias:** La parte del portal no se regenera solo con el pipeline: hay que documentar el procedimiento de exportación y la fecha de cada fichero. Los menores cubren 2023-01-01 a 2026-09-30 (descargados el 2026-11-16). Hay que cruzar las dos fuentes por expediente y órgano (P-06, P-11) y resolver la mezcla de importes con y sin IVA (P-10). Actualizados 02 y 09.

## D-013 · R-03 (posible fraccionamiento) sin CPV
- **Fecha:** 2026-11-16
- **Estado:** Sustituida por D-014
- **Autor:** Claude (agente), trabajando con El Harrak
- **Contexto:** La definición de R-03 agrupa menores por NIF, CPV y órgano. Los contratos menores del portal no traen CPV, y sus importes van con IVA mientras que los umbrales legales (15.000 € y 40.000 €) son sin IVA.
- **Decisión:** _Por decidir._ Propuesta: agrupar por NIF + órgano + **tipo de contrato** en 12 meses y resolver el tratamiento del IVA en P-10 antes de fijar el umbral.
- **Alternativas consideradas:** Inferir el CPV del título con IA (segundo recorte del plan, poco fiable); recortar R-03.
- **Consecuencias:** Agrupar por tipo de contrato es más grueso que por CPV y dará más señales; hay que decirlo en la nota de limitaciones del indicador. Cambia 04 cuando se acepte.

## D-014 · Definición de R-03 (posible fraccionamiento) con los datos disponibles
- **Fecha:** 2026-11-16
- **Estado:** Aceptada (El Harrak pidió «calcularla de la manera más fiable» y delegó la definición; 2026-11-16)
- **Autor:** Claude (agente), a petición de El Harrak
- **Contexto:** Concreta D-013. Comprobado en tres fichas oficiales el 2026-11-16: la columna «Importe de adjudicación» del CSV de menores es el importe **con IVA**; el tipo de IVA varía de un contrato a otro (0 % en dos de las tres fichas, 21 % en la otra); la ficha tampoco publica CPV. No hay forma de recuperar el importe sin IVA ni el CPV sin abrir 1,3 millones de fichas.
- **Decisión:** R-03 se activa cuando la **suma de los contratos menores de un mismo adjudicatario, mismo órgano y mismo tipo de contrato en una ventana móvil de 12 meses** supera el umbral legal **multiplicado por 1,21**: **18.150 €** en servicios y suministros (15.000 € × 1,21) y **48.400 €** en obras (40.000 € × 1,21), con al menos dos contratos en la ventana. Como el IVA nunca supera el 21 %, una suma con IVA por encima de ese valor implica una suma sin IVA por encima del umbral legal, sea cual sea el tipo aplicado.
- **Alternativas consideradas:** Comparar el importe con IVA directamente con 15.000 € / 40.000 € (daría señales falsas en todos los contratos entre el umbral y el umbral más IVA); dividir todo entre 1,21 (infravalora los contratos exentos o con tipo reducido y también falla); inferir el CPV del título con IA (poco fiable y segundo recorte del plan).
- **Consecuencias:** El criterio es conservador: no señala los casos cuya suma sin IVA supera el umbral pero con IVA queda por debajo de 18.150 € / 48.400 €. Agrupar por tipo de contrato en lugar de CPV es más grueso y puede juntar prestaciones distintas; ambas limitaciones se explican en la nota del indicador y en la interfaz. Los contratos de tipo «Otros» o sin tipo quedan fuera (no aplicable). Actualizado 04; P-10 queda resuelta para R-03 y abierta para las sumas que mezclen fuentes.

## D-015 · R-03 solo suma contratos menores de al menos un tercio del umbral
- **Fecha:** 2026-11-19
- **Estado:** Aceptada (El Harrak, 2026-11-19)
- **Autor:** Claude (agente), trabajando con El Harrak
- **Contexto:** Con la definición de D-014, R-03 se activaba en el **84,8 %** de los 1.317.145 menores aplicables (88 % en suministros). Casi todo eran pedidos de hospitales a su proveedor habitual: cientos de compras de medicamentos de 16 €, 260 €… que juntas superan 18.150 € en un año. Una señal que se activa en casi todos los contratos no distingue nada.
- **Decisión:** Se mantiene D-014 (mismo adjudicatario, órgano y tipo de contrato; ventana móvil de 12 meses; al menos dos contratos; suma con IVA por encima de 18.150 € o 48.400 €), pero en la suma **solo cuentan los menores de al menos un tercio del umbral**: 6.050 € con IVA en servicios y suministros y 16.133,33 € en obras. Es el patrón de dividir un contrato grande en unos pocos trozos. Los menores más pequeños siguen siendo aplicables, pero no activan la señal. Resultado con los datos del 16-nov: 16,9 % de los menores activados, que suman 3.094 M€.
- **Alternativas consideradas:** Exigir también el mismo título (12,5 %, pero lo evita cualquier cambio de redacción y los títulos del portal son muy irregulares); ventana de 3 meses (68,6 %); mantener D-014 y ordenar por cuánto se supera el umbral (el 85 % seguiría activado).
- **Consecuencias:** No señala el fraccionamiento en muchos trozos pequeños (p. ej. diez contratos de 2.000 €); se dice en la nota de limitaciones. Las compras recurrentes de pequeño importe de los hospitales son un patrón distinto que R-03 no mide. Actualizado 04 y `sql/indicadores/r03_posible_fraccionamiento.sql`.

## D-016 · R-05 mide las modificaciones, no las prórrogas, con umbral del 20 %
- **Fecha:** 2026-11-19
- **Estado:** Aceptada (El Harrak, 2026-11-19)
- **Autor:** Claude (agente), trabajando con El Harrak
- **Contexto:** La definición de R-05 en 04 suma modificaciones y prórrogas y no fija umbral. En el CSV del portal (31.411 licitaciones con importe y datos de modificación), las prórrogas valen una mediana del **100 %** del importe adjudicado: son anualidades previstas en el pliego, no sobrecostes. Sumarlas activaría el 25,7 % de los contratos.
- **Decisión:** R-05 se activa cuando el **importe de las modificaciones supera el 20 % del importe adjudicado** (con IVA, ambos del portal regional). El 20 % es el límite de la LCSP para las modificaciones previstas en el pliego (art. 204). Valor = modificaciones / adjudicado. Las prórrogas se muestran en el motivo, pero no cuentan. Para evitar que el redondeo de céntimos decida, se exige superar el 20 % en más de 1 €: 362 contratos tienen las modificaciones justo en el 20 %, el máximo legal. Resultado con los datos del 16-nov: 573 contratos (1,8 %).
- **Alternativas consideradas:** Umbral del 10 % (1.531 contratos, 4,9 %, sin referencia legal); modificaciones + prórrogas > 20 % (8.072 contratos, mayoría de prórrogas previstas).
- **Consecuencias:** Solo aplica a contratos del portal regional (PLACSP no publica modificaciones). Si la licitación también está en PLACSP, el resultado se asigna al contrato de PLACSP para que la puntuación no la cuente dos veces. Actualizado 04.

## D-017 · Congelar el esquema v1 (`sql/esquema/001_tablas.sql`) con ampliaciones aditivas
- **Fecha:** 2026-11-19
- **Estado:** Aceptada (El Harrak, 2026-11-19)
- **Autor:** Claude (agente), trabajando con El Harrak
- **Contexto:** El plan fijaba el congelado del esquema para H1 (17-nov). Existe una propuesta (`sql/esquema/001_tablas.sql`) con la que ya se cargaron 1,37 M de contratos y sobre la que se construyen los indicadores. Sin congelarlo, las cuatro personas trabajan sobre una base que puede cambiar. (Citada antes como D-015 en la bitácora del 17-nov; renumerada porque D-015 y D-016 se usaron en la rama de indicadores.)
- **Decisión:** Se congela la versión 1 del esquema tal como está en `001_tablas.sql`. Se permiten **ampliaciones aditivas** (tablas o columnas nuevas, p. ej. subvenciones) en ficheros nuevos `002_…sql`, avisando al equipo. Cambiar o borrar columnas existentes requiere una decisión nueva.
- **Alternativas consideradas:** Seguir sin congelar (bloquea el trabajo en paralelo); congelar sin permitir ampliaciones (obligaría a una decisión para incorporar la BDNS).
- **Consecuencias:** Al aceptarla, H1 pasa a cumplido en 08. Falta la parte de subvenciones, que irá en una ampliación aditiva.

## D-018 · R-04 señala cuota superior al 50 % por órgano y tipo de contrato
- **Fecha:** 2026-11-19
- **Estado:** Aceptada (El Harrak pidió seguir con los indicadores del plan; umbral revisable, 2026-11-19)
- **Autor:** Claude (agente), trabajando con El Harrak
- **Contexto:** 04 define R-04 como «cuota de una empresa en el gasto de un órgano o CPV; índice HHI por mercado», sin umbral. No tenemos CPV en el portal regional (D-013) y los importes de las dos fuentes no se pueden sumar (con y sin IVA).
- **Decisión:** Mercado = fuente + órgano + tipo de contrato, sobre todo el periodo. Un contrato activa R-04 si algún adjudicatario suyo concentra **más del 50 %** del importe del mercado. Solo es aplicable si el mercado tiene al menos **10 contratos y 3 empresas**. El HHI del mercado se muestra en el motivo. Resultado con los datos del 16-nov: 1.348.715 aplicables, 84 activados (0,006 %).
- **Alternativas consideradas:** Umbral del 30 % (cientos de contratos más, sin referencia clara); HHI > 0,25 del mercado (marcaría a todas las empresas del mercado, no a la dominante); mercado por CPV (no disponible).
- **Consecuencias:** Es un indicador muy selectivo: casi no moverá la puntuación por contrato, pero sí sirve en la ficha de órgano y de empresa (cuota y HHI). No distingue exclusividades legítimas ni mercados pequeños por naturaleza. Actualizado 04.

## D-019 · R-06 señala baja nula (≤ 0,5 %) o extrema (≥ 50 %) en procedimientos con concurrencia
- **Fecha:** 2026-11-19
- **Estado:** Aceptada (El Harrak pidió seguir con los indicadores del plan; umbrales revisables, 2026-11-19)
- **Autor:** Claude (agente), trabajando con El Harrak
- **Contexto:** 04 define R-06 como diferencia entre presupuesto base y adjudicación «cercana a cero, o extrema», sin cifras. En los datos del 16-nov, la baja es cero en el 78 % de los negociados sin publicidad (donde es esperable, no hay competencia) y en el 13 % de los abiertos. El 4 % de los contratos con concurrencia tienen una baja del 50 % o más.
- **Decisión:** Baja = 1 − adjudicado / presupuesto base, con la misma base en ambos (sin IVA en PLACSP, con IVA en el portal). Solo aplica a procedimientos abierto, abierto simplificado y restringido, con al menos dos ofertas, todos los lotes resueltos y presupuesto e importe positivos. Se activa con baja **≤ 0,5 %** (incluye adjudicar por encima del presupuesto) o **≥ 50 %**. Resultado con los datos del 16-nov: 11.909 aplicables, 2.226 activados (18,7 %).
- **Alternativas consideradas:** Incluir negociados (activaría casi todos sin aportar nada); baja exacta cero (el redondeo y pequeñas diferencias lo esquivarían); umbral extremo del 30 % (mucho más amplio); comparar con la media de las ofertas como pide el art. 149 LCSP (no tenemos las ofertas).
- **Consecuencias:** La tasa es alta y mezcla dos señales distintas; la interfaz debe mostrar cuál se dio (el motivo lo dice). Un solo licitador queda fuera (lo cubre R-01). Actualizado 04.

## D-020 · Puntuación de riesgo por contrato, órgano y empresa
- **Fecha:** 2026-11-19
- **Estado:** Aceptada (El Harrak pidió seguir con el plan; 2026-11-19)
- **Autor:** Claude (agente), trabajando con El Harrak
- **Contexto:** 04 fija la puntuación por contrato (proporción de indicadores aplicables activados) y «media ponderada por importe y tendencia anual» para órgano y empresa, sin más detalle.
- **Decisión:** `sql/indicadores/900_puntuacion.sql` crea `puntuacion_contrato`, `puntuacion_organo`, `puntuacion_organo_anio`, `puntuacion_empresa` y `puntuacion_empresa_anio`. Contrato = activados / aplicables, guardando `n_aplicables` para que la interfaz sepa cuánto se fía. Órgano y empresa: media ponderada por importe (se da también la media simple y el nº de contratos con alertas). El importe es solo un peso: no se suman importes con y sin IVA (P-10). Las tablas por año solo incluyen 2023–2026 (hay fechas erróneas en la fuente). Las personas físicas no tienen puntuación propia (D-007).
- **Alternativas consideradas:** Exigir un mínimo de indicadores aplicables para puntuar (esconde el 99 % de los contratos, casi todo menores con solo R-03 y R-04); ponderar los indicadores por prioridad (no hay base para los pesos).
- **Consecuencias:** El 99 % de los contratos tiene solo 1–2 indicadores aplicables (menores: R-03 y R-04), así que su puntuación es poco comparable con la de una licitación con 5. La interfaz debe mostrar `n_aplicables` y comparar entre pares. Los hospitales encabezan la puntuación de órgano por R-03 (compras recurrentes de pequeño importe): hay que leerlo con cuidado (K-11). 19.174 contratos no tienen fecha y no entran en las tablas anuales.

## D-021 · Detección de anomalías con aprendizaje automático como señal complementaria
- **Fecha:** 2026-11-20
- **Estado:** Aceptada (El Harrak, 2026-11-20: «incluye en el plan la detección de anomalías, que sea por clustering no supervisado o supervisado»). El método concreto se elige al medirlo con datos (ver Decisión).
- **Autor:** Claude (agente), a petición de El Harrak
- **Contexto:** La propuesta para DataMad quiere mencionar modelos de aprendizaje automático, además de los indicadores en SQL (D-004). Los indicadores solo ven los patrones que alguien ha definido antes. Un modelo puede encontrar contratos raros respecto a sus pares que ninguna regla captura. D-002 descartó un clasificador de «contratos corruptos» porque no hay etiquetas fiables y el riesgo legal es alto.
- **Decisión:** Se añade un módulo de **detección de anomalías** sobre las licitaciones y los menores ya cargados. Se usan variables que ya están en la base: importe, nº de ofertas, baja, modificaciones, procedimiento, tipo, órgano, cuota del adjudicatario y nº de menores en 12 meses.
  - **Método por defecto, no supervisado:** agrupar contratos parecidos (clustering, p. ej. k-means o HDBSCAN por tipo de contrato) y medir lo lejos que está cada uno de su grupo, o un Isolation Forest. No necesita etiquetas.
  - **Supervisado, solo si hay etiquetas legítimas:** p. ej. contratos citados en informes de la Cámara de Cuentas. Nunca se entrena con etiquetas de «corrupción» (D-002). Entrenar para imitar nuestros propios indicadores no aporta nada nuevo (sería circular).
  - **Cómo se muestra:** como «contrato atípico respecto a contratos similares», con las variables que más lo alejan y el enlace al expediente. Es una señal aparte y **no entra en la puntuación de D-020** hasta validarla.
  - **Reproducible:** semilla fija, el código y los parámetros en el repositorio, y el resultado en una tabla derivada.
  - **Calendario:** del 21 al 23 de noviembre, antes de la demo (H3).
  - **Recortes:** pasa a ser el **primer recorte** de la lista, porque es alcance nuevo.
  - **Método elegido (21-nov, al implementarlo):** Isolation Forest por grupo de pares (fuente · licitación o menor · tipo de contrato, grupos de 50 o más), 200 árboles, semilla 42, el 1 % más alejado de cada grupo como atípico; explicación por desviación robusta frente a la mediana del grupo. Detalle y resultados en `docs/04-indicadores-riesgo.md`.
- **Alternativas consideradas:** No incluirlo (la propuesta no podría mencionar aprendizaje automático); solo supervisado (no hay etiquetas fiables, D-002); meter la anomalía en la puntuación (mezcla una señal sin validar con indicadores auditables).
- **Consecuencias:** Nueva dependencia (scikit-learn, con `uv add` cuando se implemente, registrada en la bitácora). Nueva carpeta `src/ojo_ciudadano/anomalias/` y tabla derivada `anomalia_resultado`; no toca el esquema congelado (D-017). Hay que asignar responsable. Los textos deben pasar por `revisor-legal`, porque «atípico» no puede leerse como «irregular». Actualizados 08, 04, 06 y `CLAUDE.md`.

## D-022 · Identidad visual: logo, paleta oscura con azul y sin emojis
- **Fecha:** 2026-11-21
- **Estado:** Aceptada
- **Autor:** Claude (agente)
- **Contexto:** La interfaz usaba el tema por defecto de Streamlit, con mucho texto en pantalla y algún emoji. El README y varios documentos también tenían emojis. Para un jurado, el proyecto necesita un aspecto serio y reconocible.
- **Decisión:**
  - **Logo vectorial:** un ojo abierto de trazo uniforme con la pupila azul, en tres variantes (`src/ojo_ciudadano/app/static/`).
  - **Tema oscuro:** fondo `#0B1120`, acento azul `#3D8BFD` y ámbar `#F2B544` solo para contraste. Tipografía Inter. Se configura en `.streamlit/config.toml`.
  - **Navegación:** agrupada en «Señales», «Explorar» y «Preguntar», con iconos Material.
  - **Menos texto:** una línea bajo cada título y las explicaciones en desplegables. Metodología, fuentes y aviso legal van a la barra lateral.
  - **Prohibidos los emojis y emoticonos** en todo el repositorio y la presentación. Los iconos son Material Symbols o SVG propios. Lo comprueba `tests/test_sin_emojis.py`.
- **Alternativas consideradas:** Mantener el tema de serie (aspecto genérico). Usar una librería de componentes externa (más dependencias y riesgo a cuatro días de la demo).
- **Consecuencias:** Nuevo `docs/marca.md` con logo, paleta y reglas. Regla 7 en `CLAUDE.md`. Las pantallas nuevas deben seguir estas reglas.

## D-023 · Accesibilidad y visualización como prioridad de la interfaz
- **Fecha:** 2026-11-21
- **Estado:** Aceptada
- **Autor:** Claude (agente)
- **Contexto:** Al revisar la web, quien no conoce el proyecto no entiende de primeras qué es Ojo Ciudadano ni qué significa una alerta. Hay demasiado texto y términos técnicos («indicadores aplicables», «2 de 3 señales»), y el mapa del dinero es difícil de leer. El público principal es la ciudadanía (`01-vision.md`).
- **Decisión:**
  - La interfaz se rediseña con el criterio «primero se ve, luego se lee».
  - Hay una portada que explica qué es Ojo Ciudadano.
  - Cada indicador tiene su propia visualización.
  - Se usa lenguaje claro y no se repite texto.
  - El trabajo se organiza en las tareas A-01 a A-11 de [11-accesibilidad.md](11-accesibilidad.md). Cada pantalla empieza con un estudio de visualización.
  - Lo legal no cambia: D-002, D-007 y el enlace al origen en cada cifra.
- **Alternativas consideradas:** Dejar la interfaz como está y explicar más en la metodología (más texto, el problema de fondo). Rehacerla con otra tecnología (no da tiempo, D-005).
- **Consecuencias:**
  - Portada nueva y cambios en todas las pantallas, coordinados con el responsable de la interfaz.
  - Para la demo, las tareas de prioridad alta. El resto entra en la lista de recortes, detrás de la detección de anomalías.
  - Se actualizan 03 (reglas de interfaz), 08 (plan) y 11.

## D-024 · Contexto de la Comunidad de Madrid: presupuesto, convenios y registros
- **Fecha:** 2026-11-23
- **Estado:** Aceptada
- **Autor:** Claude (agente), a petición de la persona que coordina; amplía D-001
- **Contexto:** La web tenía poca información y las fuentes cargadas (contratos y subvenciones) no tenían contexto: nada de presupuesto, convenios ni registros de entidades. D-001 ya preveía presupuesto y altos cargos «como contexto, mostrados por separado». Se pidió usar solo fuentes de la Comunidad de Madrid.
- **Decisión:**
  - Se incorporan datos de la **Comunidad de Madrid** (catálogo de datos abiertos y Portal de Transparencia): 25 series presupuestarias y de personal, presupuesto por órgano y fase, convenios vigentes, registros con NIF (transparencia, fundaciones, cooperativas) y puestos de la RPT.
  - Esquema: ampliación **aditiva** `sql/esquema/003_contexto_cm.sql` (cinco tablas; no cambia el esquema v1 congelado, igual que 002 en D-017).
  - Un comando para todo el equipo (`uv run python -m ojo_ciudadano.modelo.contexto`), con referencia en `docs/datos-cm-referencia.json` para comprobar que todos tienen lo mismo.
  - Nueva dependencia `fastexcel` (lector de Excel para polars): el Portal de Transparencia publica los convenios en `.xlsx`.
  - Es **contexto**, no indicador de riesgo: no entra en la puntuación y no se cruza partida a partida con los contratos.
  - Privacidad: solo NIF de persona jurídica en los registros; en convenios, solo firmantes con forma de entidad (D-007).
  - Fuera de la ampliación (decisión explícita): datos de otras administraciones (ayuntamientos), cualquier dato con identidad de personas y lo listado en [12-datos-cm.md](12-datos-cm.md).
- **Alternativas consideradas:** Más fuentes estatales o europeas (TED repite PLACSP y no son de la Comunidad). Parsear los 103 Excel de planes de medios (mucho esfuerzo, poco valor). Guardar las series en una tabla por conjunto de datos (más tablas que mantener; la tabla larga `serie_cm` basta).
- **Consecuencias:** Nuevo [12-datos-cm.md](12-datos-cm.md). Pantalla «Presupuesto y contexto», bloque de presupuesto en la ficha de órgano, registros en la ficha de empresa y tablas nuevas en el asistente. Pie de la interfaz con las dos fuentes nuevas. [02-fuentes-datos.md](02-fuentes-datos.md) y el plan actualizados. **Todo el equipo debe bajar los datos antes de seguir** ([12-datos-cm.md](12-datos-cm.md)).

## D-025 · Buscadores con autocompletado y más filtros en las pantallas de señales
- **Fecha:** 2026-11-23
- **Estado:** Aceptada
- **Autor:** Claude (agente), a petición de la persona que coordina
- **Contexto:** Quien no conoce los nombres de las empresas no podía buscarlas: la búsqueda pedía tres letras y no sugería nada. En «Contratos atípicos» había contratos con valores sin sentido (por ejemplo, una baja de -300.000 %) que se confundían con atípicos reales, y las dos pantallas de señales casi no tenían filtros ni formas de ordenar (D-023: «primero se ve, luego se lee»).
- **Decisión:**
  - Los buscadores de empresa y de organismo sugieren mientras se escribe, primero lo que **empieza** por lo escrito y luego lo que lo contiene (`app/buscador.py`, consultas `datos.sugerir_empresas` y `datos.sugerir_organos`). Se usan en la ficha de empresa, la de organismo, las preguntas guiadas y los filtros de «Contratos a revisar». Solo salen empresas y entidades con contratos o subvenciones, sin personas físicas (D-007).
  - Nueva dependencia de interfaz **`streamlit-searchbox`** (componente de Streamlit, sin llamadas externas): Streamlit no trae autocompletado que consulte la base mientras se escribe.
  - «Contratos atípicos»: orden (más o menos alejado, mayor o menor importe), nivel mínimo de lejanía, variable en la que se aleja, búsqueda y un interruptor **«Mostrar posibles errores de datos»** (apagado por defecto). Es un posible error cuando la baja es inferior a -100 % (adjudicado por más del doble del presupuesto, criterio que ya usaba la detección), las modificaciones superan cinco veces el importe adjudicado o el importe es inferior a 1 euro. No es una afirmación: se llama «posible error al introducir los datos en la fuente».
  - «Contratos a revisar»: varias señales a la vez (cualquiera o todas), año, tipo de contrato, orden, mínimo de señales, cuántos mostrar y organismo o empresa concretos.
- **Alternativas consideradas:** `st.selectbox` con todas las empresas (decenas de miles de opciones enviadas al navegador). Un cuadro de texto con botón de buscar (no sugiere mientras se escribe). Quitar los posibles errores del cálculo del modelo (cambiaría D-021; aquí solo se ocultan en la pantalla).
- **Consecuencias:** `uv sync` para instalar la dependencia. Los umbrales de «posible error» están en `app/datos.py` (`_POSIBLE_ERROR`). Se actualiza [03-modulos.md](03-modulos.md).

## D-026 · Mapa general del dinero y mapa de nodos arrastrable
- **Fecha:** 2026-11-23
- **Estado:** Aceptada
- **Autor:** Claude (agente), a petición de la persona que coordina
- **Contexto:** El «Mapa del dinero» dibujaba la red como un gráfico más (burbujas y líneas de grosor variable) y no daba la visión de conjunto: cuánto dinero tiene la Comunidad, cómo se reparte entre consejerías y cuánto han gastado. Se pidió un mapa principal, visual, con nodos que se mueven al estilo de Neo4j.
- **Decisión:**
  - Nuevo componente `app/red.py`: mapa de nodos arrastrable (los conectados se mueven al tirar de uno, sin zoom). El **tamaño y el color** de cada círculo son el dinero (más grande y más claro, más dinero) y el **relleno** muestra qué parte se ha gastado (el resto, en gris). Todas las líneas son iguales. Usa la nueva dependencia **`streamlit-agraph`** (vis-network), que devuelve el nodo pulsado.
  - Nueva pantalla **«Mapa general»**, la primera de la navegación y la que se abre por defecto: la Comunidad en el centro y sus consejerías y órganos alrededor, con selector de periodo (2015 a 2026) y de qué ver (presupuesto y gasto; contratos de la Plataforma; contratos del portal; subvenciones). Arriba, dinero disponible, gastado, sin gastar y pagado. Al pulsar una consejería, sus 15 contratos más grandes del año más los menores y las subvenciones agrupados; al pulsar un contrato, su ficha (importe, presupuesto de licitación, ofertas, cómo se contrató, adjudicataria, señales y enlace) y qué parte del dinero de la consejería es.
  - El «Mapa del dinero» (organismo y sus empresas) usa el mismo componente.
  - Lo que no hay se dice en la pantalla («Qué datos no tenemos»): gasto del año en curso, gasto que no es contratación, contratos sin fecha, criterios de adjudicación y órganos sin contratos en nuestras fuentes.
- **Alternativas consideradas:** Componente propio con D3 (más trabajo y sin devolver el clic a Streamlit). Mantener Plotly (no se puede arrastrar un nodo y que tiren los demás). Cruzar partida a partida presupuesto y contratos (los datos no lo permiten, ver 02).
- **Consecuencias:** `uv sync` para instalar `streamlit-agraph`. Presupuesto y contratos son fuentes distintas y se comparan por consejería y año, no partida a partida (`textos.AVISO_CONTEXTO`). Los nodos deben ser deterministas entre ejecuciones (si cambia el orden de un nombre, Streamlit ve un componente nuevo y pierde el clic): las consultas ordenan las adjudicatarias. Se actualizan [03-modulos.md](03-modulos.md) y el plan.

## D-027 · Financiación con fondos europeos desde PLACSP y filas de relleno fuera de los adjudicatarios
- **Fecha:** 2026-11-23
- **Estado:** Aceptada
- **Autor:** Claude (agente), a petición de una persona del equipo
- **Contexto:** La investigación de fuentes externas ([13-fuentes-externas.md](13-fuentes-externas.md)) mostró dos cosas sobre datos que ya tenemos. 1) El Atom de PLACSP dice en cada licitación si se financia con fondos de la UE y con qué programa (`FundingProgramCode`: PRTR, FEDER, FSE+, FEADER, OFE), y la ingesta no lo leía: 991 expedientes de la Comunidad con fondos europeos, 548 del PRTR. 2) En `adjudicatario` había filas de relleno de las fuentes («Varios adjudicatarios», «33 EMPRESAS ADJUDICATARIAS» con el NIF de la Comunidad, «Ver resolución de adjudicación», NIF de ceros): 15 «adjudicatarios», 165 adjudicaciones y 156,6 M€ con IVA atribuidos a empresas que no existen.
- **Decisión:**
  - Tabla nueva `contrato_financiacion` en `sql/esquema/004_financiacion_ue.sql` (ampliación **aditiva**, D-017; no cambia `contrato`). Una fila por contrato de PLACSP que trae el campo. Es **contexto**, no señal de riesgo: no entra en la puntuación.
  - `normalizacion.nif.es_relleno`: esas filas se guardan como adjudicatario desconocido (sin identificador ni nombre), igual que una adjudicación sin NIF. La adjudicación y su importe se conservan.
- **Alternativas consideradas:** Columna nueva en `contrato` (cambia el esquema congelado). Bajar los listados de perceptores del PRTR (repiten lo que ya dice el contrato). Para el relleno, borrarlo a mano en la interfaz (no arregla indicadores ni puntuación).
- **Consecuencias:** Hay que regenerar la base (`modelo.carga`, `indicadores.ejecutor`, `anomalias.deteccion`). R-04 y la puntuación de empresa dejan de contar esas filas como empresa. Se actualizan 02, 06 y 13.

## D-028 · Encargos a medios propios en una tabla aparte, fuera de los indicadores
- **Fecha:** 2026-11-23
- **Estado:** Aceptada
- **Autor:** Claude (agente), a petición de una persona del equipo
- **Contexto:** El portal de contratación publica los **encargos a medios propios** (art. 32 de la Ley 9/2017): trabajos que un órgano asigna sin licitación a una entidad pública que actúa como su medio propio. Nunca se habían exportado. La exportación del 23-nov tiene 2.405 encargos, 740,2 M€ con IVA, sobre todo a Tragsa (513 M€) y Tragsatec (117 M€). El CSV no trae ninguna fecha; la referencia del portal (`C<número>`) crece con la fecha de publicación, y los tramos por año coinciden exactamente con el buscador (236, 226, 260 y 222 encargos de 2023 a 2026).
- **Decisión:**
  - Tabla aditiva `encargo` (`sql/esquema/005_encargos.sql`, D-017) con el órgano, el medio propio (en `adjudicatario`, con la misma identidad que en los contratos), el importe y el **año de publicación** deducido de la referencia (`ingesta/encargos.py`, `LIMITES_REFERENCIA`). Solo 2023–2026 (D-006).
  - **No entran en `contrato` ni en los indicadores ni en la puntuación**: no son contratos licitados, y meterlos cambiaría R-02 (aplicables) y R-04 (cuotas de los medios propios). Son un tercer flujo de dinero, igual que las subvenciones.
  - El asistente puede consultarlos, diciendo que no son contratos.
- **Alternativas consideradas:** Cargarlos en `contrato` con `tipo_publicacion = 'Encargos a medios propios'` y excluirlos en cada indicador (toca los seis SQL a un día del H3). Tomar la fecha de cada ficha (2.405 peticiones; la referencia da lo mismo con un recorrido de 95 páginas).
- **Consecuencias:** Hay que regenerar la base. El CSV se exporta a mano (captcha): está en `data/raw/encargos/`, fuera de git. Si se exporta de nuevo en 2027, hay que añadir el tramo de referencias de ese año. Pendiente: mostrarlos en la ficha de órgano y en el mapa del dinero (lo coordina quien lleva la interfaz). Se actualizan 02, 06 y 13.

## D-029 · Recursos especiales ante el TACPCM como contexto del contrato
- **Fecha:** 2026-11-23
- **Estado:** Aceptada
- **Autor:** Claude (agente), a petición de una persona del equipo
- **Contexto:** El Tribunal Administrativo de Contratación Pública de la Comunidad de Madrid publica sus resoluciones sobre recursos especiales (pliegos, exclusiones, adjudicaciones) en un buscador HTML. Es un hecho oficial sobre contratos concretos que no teníamos. De 2023 a 2026 hay unas 1.100 resoluciones de consejerías, hospitales, otros poderes adjudicadores y universidades ([13-fuentes-externas.md](13-fuentes-externas.md), X-02).
- **Decisión:**
  - Descarga reproducible del listado (`ingesta/tacp.py`), una petición cada vez con 2 s de pausa y caché en `data/raw/tacp/`. Se recorre por procedencia × tipo de resolución × acto recurrido: los filtros reparten las resoluciones sin huecos (comprobado con las 451 de consejerías), así que cada una sale una vez y ya etiquetada.
  - Tabla aditiva `recurso_especial` (`sql/esquema/006_recursos_tacp.sql`). Se enlaza con `contrato` cuando el resumen cita un expediente que corresponde a **un único** contrato no menor y no duplicado; si no casa o es ambiguo, queda sin enlazar.
  - **No se guarda el resumen** (nombra a empresas y puede nombrar a personas, D-007): solo los campos estructurados y los enlaces a la ficha y al PDF.
  - Es **contexto, no señal**: no entra en la puntuación. Presentar un recurso no indica nada; una estimación solo dice que ese acto no se ajustaba a derecho según el Tribunal.
- **Alternativas consideradas:** Abrir la ficha de cada resolución (1.100 peticiones frente a unas 340). Leer los PDF con IA para sacar el expediente (recorte n.º 3 del plan). Una señal «recursos estimados por órgano» (necesita definición y validación; queda como línea futura).
- **Consecuencias:** Hay que bajar el listado (`uv run python -m ojo_ciudadano.ingesta.tacp`; el 23-nov fueron 377 páginas y unos 50 minutos, el servidor es lento) y regenerar la base. **Resultado y límites (23-nov):** 1.097 resoluciones de 1.109 (la paginación del buscador repite o salta filas cuando hay fechas empatadas). Solo **6 se enlazan con un contrato**: la mayoría de los resúmenes no citan el expediente, y el listado no da el órgano, solo la procedencia (consejerías, hospitales…). Por eso sirve sobre todo como **contexto agregado** (por ejemplo, el Tribunal estimó total o parcialmente el 30 % de los recursos contra pliegos, el 25 % contra adjudicaciones y el 18 % contra exclusiones). Enlazar más exigiría leer los PDF (recorte n.º 3), que queda como línea futura. Pendiente: mostrarlo en la ficha de contrato y de órgano. Se actualizan 02, 06 y 13.

## D-030 · RAG centrado en el catálogo de datos abiertos y, después, en los pliegos
- **Fecha:** 2026-11-23
- **Estado:** **Bloque A aceptado** el 2026-11-23 (El Harrak: «empieza el bloque A del catálogo») e implementado ese día; pasó el control (4 de 4 preguntas de catálogo). **Bloques B y C aceptados** el 2026-11-23 (El Harrak: «realiza los bloques B y C en su integridad») e implementados ese día en la rama `feat/rag-documentos`. El bloque C, que esta decisión dejaba fuera de la entrega, se adelanta con las medidas de [D-032](#d-032--texto-de-los-pdf-del-tacpcm-y-de-los-pliegos-en-el-asistente).
- **Autor:** Claude (agente), a petición de El Harrak
- **Contexto:** El plan preveía un RAG con BM25 y embeddings sobre informes, memorias y pliegos (D-010, [05](05-asistente.md)), y es el recorte 2. La investigación del 23-nov está en [14-rag-documental.md](14-rag-documental.md).
  - **El catálogo son tablas:** 2.231 de 2.276 conjuntos en CSV o JSON, y solo 12 con PDF.
  - **Su buscador no encuentra lo que se pregunta.** Un índice BM25 propio acierta 6 de 8 preguntas, y las otras 2 piden datos que no existen.
  - **La consulta remota** (`datastore_search_sql`) falla con columnas con tilde.
  - **El CSV bajo demanda es pequeño:** 42 KB de mediana. La prueba de punta a punta (listas de espera por hospital) respondió bien por 0,0028 USD.
  - **Los pliegos de PLACSP** están enlazados en el 97 % de las licitaciones de la muestra, y la prueba con R-02 citó el art. 168.a.2 con su página.
- **Decisión propuesta:**
  - **Bloque A, RAG de catálogo (6 h):**
    - tabla aditiva `catalogo_conjunto` con índice BM25 de DuckDB;
    - herramientas `buscar_conjunto` y `consultar_conjunto`: CSV bajo demanda con caché, consultado en local con el validador de `sql_seguro`;
    - control el 24-nov a las 12:00.
  - **Bloque B, pliegos de PLACSP bajo demanda (10 h):**
    - tabla aditiva `contrato_documento`, herramienta `buscar_en_pliego` y dependencia `pypdf`;
    - solo si A pasa el control; control el 24-nov a las 20:00.
  - **Fuera de esta entrega:**
    - PDF del TACPCM (D-029): necesitan revisión legal y la fusión de su rama;
    - embeddings;
    - informes de la Cámara de Cuentas.
- **Alternativas consideradas:**
  - Aplicar el recorte 2.
  - Solo pliegos, que era la primera versión de esta propuesta: menos alineado con el núcleo.
  - Consulta remota con `datastore_search_sql`: falla con las tildes.
  - RAG completo con embeddings: torch y varios días.
- **Implementación del bloque A (23-nov):** sin cambio de esquema. Los metadatos del catálogo se guardan como caché JSON en `data/raw/catalogo/`, que no se sube, y el índice BM25 se crea en memoria la primera vez que se usa: 2.228 conjuntos con CSV en 2,2 s. Así no se toca `modelo/carga.py`, que otras ramas están cambiando.
- **Consecuencias:**
  - Sin cambio de esquema en A. Con B, esquema aditivo (D-017) y cambio en `ingesta/placsp.py`: hay que avisar a quien lleva la ingesta.
  - Cada instalación baja el catálogo con `uv run python -m ojo_ciudadano.asistente.catalogo` (3 peticiones).
  - **RGPD (revisión legal del 23-nov):** no se ofrecen al asistente 57 conjuntos con listados que pueden nombrar a personas: registros, agenda de Gobierno, listas de interinos, ayudas con beneficiarios… Detalle en [14](14-rag-documental.md).
  - De 4 a 7 preguntas nuevas en la batería.
  - Si se acepta, se actualizan 05, 06 y 08.

## D-031 · Datos de D-027 a D-029 en la detección de anomalías, el asistente y la búsqueda
- **Fecha:** 2026-11-23
- **Estado:** Propuesta. El Harrak pidió integrar los datos nuevos en la detección de anomalías, el RAG y las consultas en lenguaje natural; la forma de hacerlo la propone el agente y falta validarla.
- **Autor:** Claude (agente), a petición de El Harrak
- **Contexto:** D-027 (fondos europeos), D-028 (encargos a medios propios) y D-029 (recursos ante el TACPCM) ya estaban en la web y en la lista de tablas del asistente, pero no en la detección de anomalías (D-021) ni en la búsqueda por palabras (D-030). D-021 pedía validar los atípicos con etiquetas legítimas antes de pensar en usarlos para más cosas.
- **Decisión propuesta:**
  - **Recursos del TACPCM: para validar, no como variable.**
    - Nueva tabla `anomalia_validacion`: proporción de atípicos y puntuación de riesgo media en todos los contratos, en los que tienen algún recurso estimado y en los que solo tienen recursos desestimados o inadmitidos.
    - Usarlos como variable haría que el modelo solo aprendiera a marcar los contratos recurridos.
  - **Fondos europeos: descriptivo, no como variable.** La misma tabla compara las licitaciones de PLACSP con y sin fondos UE. Tener fondos europeos no indica nada sobre el riesgo.
  - **Encargos: grupo de pares propio** («portal_cm · encargo»), con importe, modificaciones y cuota del medio propio en lo que encarga el órgano.
    - Resultado en `anomalia_encargo`, aparte de `anomalia_resultado`.
    - No entran en indicadores ni en puntuación (D-028), y el motivo habla de «encargos similares».
  - **Asistente:**
    - `anomalia_encargo` y `anomalia_validacion` en la lista permitida, con sus reglas de lenguaje;
    - `buscar_texto` busca también en los títulos de los encargos;
    - preguntas B-28 a B-30 en la batería.
  - **Web:** dos desplegables en «Contratos atípicos»: los encargos atípicos y la comprobación.
- **Alternativas consideradas:**
  - Recursos estimados como etiqueta de un modelo supervisado: hay muy pocos enlazados a un contrato.
  - Fondos UE como variable.
  - Encargos dentro de `anomalia_resultado`: mezclaría encargos y contratos, en contra de D-028.
- **Consecuencias:**
  - Hay que regenerar la detección de anomalías tras cargar los datos nuevos, con `anomalias.deteccion`.
  - Sin el CSV de encargos, que se exporta a mano por el captcha, `anomalia_encargo` queda vacía.
  - Se actualizan 04, 05, 06 y 08.

## D-032 · Texto de los PDF del TACPCM y de los pliegos en el asistente
- **Fecha:** 2026-11-23
- **Estado:** Propuesta. El Harrak pidió hacer los bloques B y C de D-030 «en su integridad»; las medidas de protección de datos las propone el agente, tras la revisión de `revisor-legal`, y falta que el equipo las valide.
- **Autor:** Claude (agente), a petición de El Harrak
- **Contexto:** D-029 no guardaba el resumen de las resoluciones porque nombra a empresas y puede nombrar a personas. El bloque C indexa el texto completo de sus PDF, que es más que el resumen. La revisión legal del 23-nov encontró que la regla al modelo no basta: el extracto literal se ve en la web, se envía al proveedor del modelo y el índice permitía buscar por apellidos.
- **Decisión propuesta:**
  - **Texto solo en tablas que no se consultan por SQL.** El texto de las resoluciones va a la tabla derivada `resolucion_pagina`, con índice BM25, que solo usa la herramienta `buscar_resoluciones`. El de los pliegos no entra en la base: se lee bajo demanda desde la caché local. En el esquema solo se añade `contrato_documento`, con los enlaces (`007_documentos.sql`).
  - **Tapado al extraer el texto** (`ingesta/documentos.py`), también al leer la caché: DNI y NIE, nombres con tratamiento («D.», «Dña.», «Sr.»…) y líneas de firma.
  - **Si una página dice «en nombre propio» o «persona física»**, ni la web ni el modelo reciben su extracto: solo el enlace al PDF oficial.
  - **Las búsquedas son por temas.** Se rechazan las que llevan un DNI, un NIE o un nombre con tratamiento, y una regla del modelo prohíbe buscar o escribir nombres de personas.
  - **Cifras:** si la respuesta solo se apoya en documentos, cada cifra tiene que estar en algún extracto. Si no, se retiene.
  - **Enlace de resoluciones por título:** solo con el título exacto (25 caracteres o más) de un único contrato que sea anterior a la resolución y de no más de 24 meses antes. La ficha del contrato y el asistente dicen «cita un contrato con el mismo título» y piden comprobarlo en la resolución.
- **Alternativas consideradas:**
  - No mostrar nunca el extracto, solo el enlace: protege más, pero el asistente no podría citar lo que dice el documento.
  - Reconocimiento de entidades con un modelo: nueva dependencia pesada y sin tiempo para validarlo.
  - Dejar el bloque C para después de la entrega, como decía D-030.
- **Consecuencias:**
  - **Riesgo residual:** un nombre de persona sin tratamiento ni marca de «nombre propio» puede verse en un extracto. Está en el K-02 de [07](07-riesgos.md).
  - Antes de la demo, hay que comprobar a mano unas 20 resoluciones enlazadas por título. Si falla más de 1 de cada 10, se desactiva ese enlace.
  - El comentario de `expediente_citado` en `006_recursos_tacp.sql` («citado en el resumen») ahora incluye el expediente que sale del PDF. No se cambia porque el esquema está congelado: se avisa al equipo.
  - Cada instalación ejecuta `ingesta.tacp --pdf` (unos 25 minutos la primera vez) y, tras regenerar la base, `asistente.documentos`.

## D-033 · Mapa general de un vistazo: diseño radial, niveles y ficha lateral
- **Fecha:** 2026-11-23
- **Estado:** Aceptada
- **Autor:** Claude (agente), a petición de la persona que coordina; ajusta D-026
- **Contexto:** Al probar el mapa general de D-026 se vieron dos fallos: algunos círculos se cortaban por abajo (la física los repartía fuera del lienzo) y había que pulsar una consejería para ver sus contratos, cuando lo que se quería era ver todo a la vez.
- **Decisión:**
  - **Diseño radial calculado** en vez de la distribución al azar de la física: la Comunidad en el centro, las consejerías en una circunferencia (los grandes intercalados con los pequeños) y los contratos en un anillo exterior. Los nodos parten de esas posiciones y la física solo da el efecto elástico al arrastrar; el lienzo se dimensiona para el diseño (700 px con un nivel, 900 con dos). Es el mismo dibujo en cada carga.
  - **Niveles elegibles:** «Solo consejerías» o «Consejerías y sus contratos» (por defecto), con 1 a 5 contratos por consejería y la opción de añadir un círculo de contratos menores y otro de subvenciones por consejería. Todo se ve de una vez, sin pulsar.
  - **Ficha lateral:** al pulsar un círculo, su ficha aparece a la derecha (consejería: cuánto tiene, cuánto ha gastado, sin gastar y parte de la Comunidad; contrato: importe, ofertas, cómo se contrató, adjudicataria, señales). Un botón amplía una consejería a sus 15 contratos más grandes.
  - Cada grupo de nodos (consejerías, contratos, agrupados) tiene su propia escala de tamaño y color: un contrato no se compara con el dinero de una consejería.
  - El «Mapa del dinero» (organismo y sus empresas) usa el mismo diseño.
- **Alternativas consideradas:** Dejar solo la física (círculos fuera del lienzo). Pedir zoom (se quiso sin zoom). Ventana emergente para la ficha (se cierra al interactuar y el componente no repite un clic sobre el mismo círculo).
- **Consecuencias:** Más consultas al abrir el mapa (los contratos principales de todas las consejerías en una sola consulta, con caché de una hora). Se actualizan 03-modulos y el plan.

## D-034 · Estética «océano» y cristal en la web

- **Fecha:** 2026-11-23 · **Estado:** aceptada (prueba de concepto revisada por Ismael)
- **Contexto:** la presentación (carpeta `presentacion/`) usa una estética submarina con burbujas de cristal; la web debía verse coherente con ella y más moderna.
- **Decisión:** solo estilo, sin tocar datos ni lógica. Fondo de mar profundo con luz y burbujas que suben (CSS); métricas, tarjetas, desplegables, avisos, barra lateral, botones y campos de cristal esmerilado; títulos finos con degradado; burbujas de cristal sobrias en los mapas de nodos (sin manchas de brillo); los mapas de nodos sin recuadro (el fondo del componente se funde con `mix-blend-mode: lighten` y bordes difuminados); separaciones de gráficos claras y casi transparentes, nunca negras. Paleta del tema ajustada a azul océano (`docs/marca.md`).
- **Alternativas:** mantener el tema plano anterior; tema claro.
- **Consecuencias:** `static/estilo.css`, `.streamlit/config.toml`, `red.svg_nodo` y los bordes de `graficos.py`. Los selectores de Streamlit pueden cambiar con la versión: si algo deja de verse de cristal, revisar `estilo.css`. Sin animación con `prefers-reduced-motion`.

## D-035 · Nombres de los CPV y entes del sector público (INVENTE) como contexto
- **Fecha:** 2026-11-23
- **Estado:** Aceptada (El Harrak: «empieza por los CPV y mira INVENTE», tras el análisis de datos libres del 23-nov). Numerada D-033 en su rama; pasó a D-035 al fusionar `main`, donde D-033 y D-034 ya eran del mapa de un vistazo y de la estética.
- **Autor:** Claude (agente), a petición de El Harrak
- **Contexto:** Las 17.589 licitaciones de PLACSP traen su código CPV, pero la web y el asistente solo enseñaban el número. Además, entre los adjudicatarios hay entes públicos (universidades, fundaciones del sector público, sociedades mercantiles públicas) que aparecen como «empresas» en las fichas. DIR3 ([13](13-fuentes-externas.md), X-05) ya se había estudiado, pero cubre sobre todo unidades de las administraciones y el cruce era por nombre.
- **Decisión:**
  - **CPV:**
    - tabla aditiva `cpv` (`sql/esquema/008_cpv.sql`) con los 9.454 códigos y su nombre oficial en español;
    - viene de la lista CODICE de la Plataforma de Contratación (`CPV2008-2.04.gc`), que es la misma con la que PLACSP clasifica: casan los 1.963 códigos distintos de la base;
    - la de TED pide pasar una comprobación de robots, y no se fuerza.
  - **INVENTE:**
    - tabla aditiva `entidad_sector_publico` (`009_sector_publico.sql`) con los 4.602 entes con NIF del inventario de la IGAE;
    - se baja con una sola petición a su API pública, documentada en el YAML de la aplicación;
    - se cruza con `adjudicatario.nif`.
  - **Uso:**
    - **ficha de contrato:** el objeto CPV con su sector;
    - **ficha de empresa:** si el NIF es de un ente público, aviso «Ente del sector público, no una empresa privada», con su forma jurídica y la administración de la que depende. Si el nombre del adjudicatario no se parece al del inventario, solo una nota: puede ser un nombre abreviado o un error de NIF en la fuente;
    - **asistente:** las dos tablas, en la lista permitida y con sus reglas.
  - **No cambia ningún indicador** (lo hace después D-036). Excluir los entes públicos de R-04 (concentración) o de la puntuación de empresa sería un cambio de metodología: queda para decidirlo en equipo.
- **Alternativas consideradas:**
  - DIR3, cuyo cruce era por nombre y no trae fundaciones ni sociedades.
  - Consultar INVENTE NIF a NIF: unas 2.000 peticiones, frente a una.
  - Los nombres del CPV desde TED: protegidos por la comprobación de robots.
- **Consecuencias:**
  - **Datos:** `uv run python -m ojo_ciudadano.ingesta.cpv` y `uv run python -m ojo_ciudadano.ingesta.invente` bajan y cargan cada tabla en la base ya construida. `modelo.carga` las incluye si están en `data/raw/`.
  - **Resultado del cruce (23-nov):** 261 adjudicatarios con NIF de un ente público, con unas 4.200 adjudicaciones y unos 121 M€ con IVA y 40 M€ sin IVA. De ellos, 235 tienen el nombre compatible y 26 no: siglas, nombres abreviados o errores de NIF de la fuente, como «PIXELWARE, S.A.» con el NIF de Planifica Madrid.

## D-036 · CPV y entes del sector público en R-04, en la puntuación de empresa y en los atípicos
- **Fecha:** 2026-11-24
- **Estado:** Aceptada (El Harrak: «haz la 1, la 2 y la 3. Además de llevar todo a las anomalías y a los indicadores»). Es un cambio de metodología el día de la demo H3: el equipo debe conocerlo antes de fusionarlo, y se puede deshacer revirtiendo la rama `feat/datos-nuevos-modelos`.
- **Autor:** Claude (agente), a petición de El Harrak
- **Contexto:** D-035 trajo los nombres de los CPV y el inventario INVENTE solo como contexto. R-04 decía en sus limitaciones que no distinguía mercados por CPV (D-013), y unos 200 entes públicos (universidades, fundaciones, sociedades públicas) tenían puntuación de empresa como si fueran empresas privadas.
- **Decisión:**
  - **R-04:**
    - en PLACSP, el mercado es fuente + órgano + tipo + **división CPV** (dos primeras cifras); el portal regional no publica CPV y sigue con órgano + tipo;
    - los entes del sector público **cuentan en el mercado** (se llevan parte del importe) pero **no activan** la señal: un contrato cuyos adjudicatarios son todos entes públicos no es aplicable;
    - la ficha (E-04) dibuja el mismo mercado y nombra la división.
  - **Qué es un ente público aquí:** un adjudicatario cuyo NIF está en INVENTE **y cuyo nombre se parece** al del inventario. El ejecutor de indicadores lo guarda en la tabla derivada `adjudicatario_ente_publico` (235 adjudicatarios). Si el nombre no cuadra, suele ser un NIF de otra entidad puesto por error en la fuente (D-035, como PIXELWARE con el NIF de Planifica Madrid), y se sigue tratando como empresa privada: un error de la fuente no debe apagar sus señales.
  - **Puntuación de empresa:** los entes públicos conservan su ficha y sus contratos, pero `puntuacion_empresa[_anio]` les deja la puntuación vacía y los marca con `sector_publico`. Sus contratos siguen contando en el órgano.
  - **Atípicos (D-021):**
    - en las licitaciones de PLACSP, el grupo de pares se divide por división CPV;
    - una división con menos de 50 contratos va a «otras divisiones CPV»; si ese resto no llega a 50, o ninguna división llega, el tipo no se divide.
  - **Validación de atípicos:** grupo nuevo «Adjudicados a entes del sector público (INVENTE)» en `anomalia_validacion`. No es variable del modelo.
  - **No se llevan al modelo ni a los indicadores:**
    - las resoluciones del Tribunal, que son la única referencia externa para validar los atípicos (D-031);
    - los pliegos, porque tener o no PDF depende de cómo publica cada portal y no del contrato.
  - **Asistente:** preguntas B-35 a B-37 en la batería, y reglas sobre el CPV y los entes públicos.
- **Alternativas consideradas:**
  - Sacar los entes públicos del mercado de R-04. Inflaría la cuota de las demás empresas.
  - Quitarles la ficha de empresa. Se perdía el aviso de D-035 y la lista de sus contratos.
  - Dividir por CPV todos los grupos. El portal regional no lo trae, y las divisiones pequeñas se quedaban sin pares.
  - Grupo CPV de 3 o 4 cifras. Haría mercados aún más pequeños.
- **Consecuencias (recalculado el 24-nov con la base del 16-nov):**
  - **R-04 en PLACSP:**
    - de 14.537 a 11.686 contratos aplicables, porque más mercados quedan por debajo de 10 contratos o 3 adjudicatarios;
    - de 29 a 92 activados, con 22 en común;
    - en el portal regional, 54 antes y 54 después, todos los mismos;
    - los entes públicos no activaban R-04 ni antes.
  - **Puntuación de órgano:** cambia en 83 de 131 órganos, con 0,10 de diferencia máxima, porque cambia R-04.
  - **Puntuación de empresa:** 209 entes públicos con contratos puntuados pasan a no tener puntuación. Antes algunos estaban arriba, como la Fábrica Nacional de Moneda y Timbre (0,42) o Renfe Viajeros (0,42).
  - **Atípicos de PLACSP:**
    - de 151 a 165, con 97 en común;
    - 48 grupos en vez de 14;
    - el total sigue en el 1 %.
  - **Validación:**
    - recursos estimados: 0 de 55 atípicos (igual que antes);
    - solo desestimados o inadmitidos: 10 de 174 (5,7 %, antes 4,6 %);
    - entes públicos: 5 de 3.961 (0,13 %).
    - El CPV no hace que los atípicos se acerquen más a los recursos estimados.
  - **Batería:** B-35 a B-37 con `openai/gpt-6.1-terra` (0,028 USD). Las tres bien, B-35 tras corregir su referencia para que use la misma definición de año que B-06.
  - **Riesgo:** la comparación de nombres puede fallar en los dos sentidos. Por un lado, una sigla puede no cuadrar con el nombre completo: un ente público, como ASERPINTO o CEDEX, se tratará como empresa. Por otro, una empresa con una palabra en común con el ente se tratará como ente. El primer error es el más prudente, porque conserva las señales.
  - **Instalaciones:** `ingesta.cpv` e `ingesta.invente` antes de `indicadores.ejecutor` y `anomalias.deteccion`. Sin esas tablas, el ejecutor las crea vacías y todo funciona como antes de D-036.

## D-037 · Un solo asistente: respuestas preparadas primero y el modelo como respaldo
- **Fecha:** 2026-11-24
- **Estado:** Aceptada (El Harrak: «que el asistente RAG y SQL sean el mismo […] es mejor si es hardcodeado […] y si no, deberíamos dejarlo al modelo que hemos elegido»).
- **Autor:** Claude (agente), a petición de El Harrak
- **Contexto:** Había dos pantallas para preguntar. «Preguntas guiadas» tenía 4 consultas verificadas en un desplegable. «Asistente» era el modelo de lenguaje con SQL, catálogo, pliegos y resoluciones. Para la demo se quería una sola pantalla, que respondiera sin modelo todo lo que la base permite responder de antemano y que enseñara qué hace mientras consulta.
- **Decisión:**
  - **Una sola pantalla, «Asistente».** «Preguntas guiadas» desaparece del menú y su contenido pasa a la lista «Preguntas con respuesta preparada».
  - **Primero, las respuestas preparadas** (`asistente/respuestas_fijas.py`), con 43 preguntas:
    - 26 de datos. Usan el SQL verificado de la batería y de las antiguas preguntas guiadas, más 5 consultas nuevas: importe por fuente y año, empresas con más importe, señales por indicador, atípicos por grupo y organismos con más menores. El texto está escrito de antemano y se rellena con las cifras del resultado y la cita de su fuente.
    - 17 sin consulta: conceptos (contrato menor, señal, puntuación, atípico, fuentes, IVA y cada indicador) y límites (calificar de irregular, personas físicas, otras administraciones, instrucciones al asistente).
  - **Cómo se reconocen:** palabras clave, sin modelo. Hacen falta todas las de la pregunta y ninguna de sus exclusiones.
    - El año, la consejería o la empresa (por NIF o por el principio de su nombre) se leen de la pregunta.
    - Un año fuera de 2023–2026, o una consejería o empresa que no está en la base, pasan al modelo.
    - Ante la duda, contesta el modelo. La pantalla dice qué pregunta preparada se reconoció y ofrece «que responda el modelo».
  - **Después, el modelo** (D-010), con las mismas herramientas y filtros de retención.
  - **Animaciones** (`app/animacion.py`, `asistente/plano.py`), solo con CSS y quietas con «reducir movimiento»:
    - mientras corre una consulta, las tablas que lee, sus uniones con la clave y los pasos (filtrar, agrupar, ordenar), sacados del árbol del SQL;
    - mientras se buscan documentos, páginas que se recorren;
    - la respuesta aparece palabra a palabra, también cuando no hay consulta.
  - El agente avisa a la interfaz antes de usar cada herramienta (`al_usar`) para cambiar la animación.
- **Alternativas consideradas:**
  - Clasificar la pregunta con el modelo antes de decidir. Cuesta una llamada por pregunta y depende de la red.
  - Parecido por vectores con las preguntas preparadas. Sin vectores en el proyecto, y menos explicable.
  - Dejar dos pantallas.
- **Consecuencias:**
  - **Coste:** las preguntas frecuentes no gastan saldo, responden en unos 2 segundos y funcionan sin clave del modelo.
  - **Mantenimiento:** una pregunta preparada nueva necesita su SQL, su texto y sus palabras clave, con test.
  - **Riesgo:** reconocer mal una pregunta da una respuesta correcta a otra pregunta. Por eso se enseña siempre la pregunta reconocida y se puede pedir el modelo.
  - Los textos preparados pasan los mismos filtros de lenguaje que los del modelo (tests).

## D-038 · Mapa general para el ciudadano: frascos de 100 billetes, presupuesto por habitante y entrada por el Inicio
- **Fecha:** 2026-11-24
- **Estado:** Aceptada por Ignacio en dos rondas. Primero eligió un treemap de billetes y una figura; después lo cambió: «Vuelve al grafo pero cada nodo debe ser un frasco de dinero, cada frasco debe tener un número de billetes proporcional a 100 con lo que recibe»; «Cambia el muñeco por un ojo con manos, replicando nuestra identidad de marca». Está en la rama propia `feat/mapa-billetes` para poder deshacerlo sin tocar el trabajo de nadie; falta que el equipo lo vea antes de fusionarlo.
- **Autor:** Claude (agente), a petición de Ignacio, dentro del repaso «dashboard a dashboard» pensando en un ciudadano medio
- **Contexto:** La web se abría con el mapa de nodos de D-033: seis controles, palabras como «crédito» o «gasto reconocido», cifras como «33.296 M€» sin referencia y etiquetas que se pisaban. Era la pantalla más difícil y la primera que se veía.
- **Decisión:**
  - **Se entra por el Inicio.** El mapa pasa a llamarse «A dónde va el dinero» y es la segunda página (su dirección sigue siendo `/mapa_general`).
  - **Tarjeta del año:**
    - la frase «En 2025 la Comunidad de Madrid tuvo 33.296 M€ y gastó 95 de cada 100 €», con una barra de lo gastado;
    - lo que tocaría a cada habitante si se repartiera el dinero de todo el año, **al año y al mes** (unos 4.680 € al año y 390 € al mes en 2025), con una figurita por cada millón de habitantes;
    - la mascota: **el ojo del logo, con su mismo trazo y su pupila azul, con dos manos**. Una levanta un abanico de billetes y la otra saluda; la pupila mira a los lados, y todo se queda quieto con «reducir movimiento».
  - **Habitantes del INE**, Estadística Continua de Población (serie ECP115490), a 1 de enero: es la fuente F-12, en `ingesta/ine.py`, con caché en `data/raw/ine/`. No entra en la base ni en ningún indicador.
  - **El mapa de nodos de D-033 se queda, con frascos** (`app/billetes.py`, campos `imagen` y `tamano` opcionales en `red.NodoRed`):
    - cada nodo es un frasco de cristal en el que **caben 100 billetes**;
    - el frasco de la Comunidad está lleno, y el de cada consejería lleva **un billete por cada euro que recibe de cada 100**; cada frasco lleva una etiqueta de papel con esos euros («39 €»; «<1 €» si no llega a uno) y debajo solo el nombre;
    - lo que no llega a un billete es un trozo de billete y **los billetes grises son lo que quedó sin gastar**;
    - todos los frascos de consejería tienen el mismo tamaño, para que se compare lo llenos que están;
    - en el nivel con contratos, el frasco de un contrato lleva los euros que recibió de cada 100 que su consejería adjudicó en la misma fuente (Plataforma sin IVA o portal con IVA, sin mezclarlas);
    - por defecto se ven solo las consejerías.
  - **Opciones junto al mapa** (botón «Opciones»): qué dinero ver, si se muestran los contratos y cuántos por consejería. Se quitan los menores y las subvenciones como nodos; al abrir una consejería se resumen en una línea.
  - **Fuentes en un botón de información** («Fuentes», arriba a la derecha): presupuesto, habitantes, contratos, el aviso de que no se cruzan partida a partida y «Qué datos no tenemos». Desaparecen esas notas de la pantalla y de las fichas.
  - **«¿Cuánto ha gastado cada consejería?»:** barra y porcentaje, de mayor a menor porcentaje, sin más texto.
  - **Sin la tabla de datos:** repetía lo que ya está en la pantalla.
  - Las fichas de consejería y de contrato pasan sus cifras a líneas de texto, porque en la columna estrecha se cortaban.
- **Alternativas:**
  - treemap de billetes: se probó y se descartó porque no era lo bastante explicativo;
  - waffle de 100 cuadraditos: no permite entrar en cada consejería;
  - frascos de tamaño proporcional al dinero: doble codificación, y los frascos pequeños no dejaban ver los billetes.
- **Consecuencias:**
  - nueva fuente F-12 (INE): cada instalación la baja sola la primera vez que se abre el mapa, o con `uv run python -m ojo_ciudadano.ingesta.ine`; si no hay red ni caché, la cifra por habitante no se muestra y el resto funciona;
  - el «Mapa del dinero» no cambia;
  - docs: 02, 03 y 08.

## D-039 · Inicio para el ciudadano: buscador único, cuatro puertas y señales «de cada 100»
- **Fecha:** 2026-11-24
- **Estado:** Aceptada por Ignacio («si» a quitar la cifra de contratos con señal, a la cuadrícula de 100, al buscador y a las cuatro puertas). Está en la rama `feat/mapa-billetes`, junto con D-038, para poder deshacer el rediseño de una vez; falta que el equipo lo vea antes de fusionarlo.
- **Autor:** Claude (agente), a petición de Ignacio, en el repaso «dashboard a dashboard»
- **Contexto:** La portada abría con cuatro cifras sin referencia, entre ellas «249.999 contratos con alguna señal». Esa cifra se lee como «uno de cada cinco contratos tiene un problema», cuando 228.000 de ellos son la señal más débil (muchos contratos menores). Además, las puertas eran pequeñas, faltaban el mapa nuevo y el asistente, no había buscador y la sección de señales eran seis párrafos.
- **Decisión:**
  - **Bienvenida:** la mascota de D-038 y la frase «Mira en qué se gasta tu dinero la Comunidad de Madrid».
  - **Buscador único:** empresas y organismos a la vez; al elegir, abre su ficha. Las fichas leen `?empresa=` y `?organo=` de la dirección, un cambio pequeño en `empresa.py` y `organo.py`.
  - **Cuatro puertas grandes, pulsables enteras:** dinero, contratos a revisar, buscar empresa u organismo, y asistente. Cada una con su icono SVG propio en `billetes.ICONOS_PUERTA`.
  - **Cifras en una línea discreta.** Se quita «contratos con alguna señal» de la portada.
  - **Señales «X de cada 100 contratos …»:** cuadrícula de 100 con los que tienen la señal en ámbar, el color de las señales (nunca rojo). Si hay alguno pero no llega a 1 de cada 100, se pinta medio cuadrado y se dice «menos de 1». La explicación va en «¿Qué significa?», con los recuentos exactos.
  - **Aviso legal:** «Una señal no prueba nada irregular» en el icono de información junto al título «Qué señales buscamos», a petición de Ignacio. El aviso corto de la barra lateral sigue siempre visible y el texto completo está en «Fuentes».
  - **Todas las tarjetas del mismo tamaño:** las puertas rellenan la altura de su fila, y las seis señales van en una sola rejilla CSS con filas iguales (3, 2 o 1 columnas según el ancho), con el botón abajo.
- **Alternativas:** frascos también para las señales (descartado: los frascos significan euros y aquí se cuentan contratos); mantener las cifras grandes.
- **Consecuencias:** cambia la portada; las fichas de empresa y de órgano aceptan el elegido por la dirección; sin dependencias nuevas. Docs: 03 y 08.
## D-040 · Web fluida y asistente sin SQL a la vista
- **Fecha:** 2026-11-24
- **Estado:** Aceptada (El Harrak: «Quita la consulta SQL de la respuesta. Solo queremos lo que saca la consulta […] optimiza todo para que vaya mejor y que la página web sea fluida»). Ajusta D-034 (estética) y D-037 (asistente).
- **Autor:** Claude (agente), a petición de El Harrak
- **Contexto:** La web iba a tirones y el scroll molestaba a la vista. Había tres causas:
  - **Burbujas del fondo:** se animaban moviendo la posición de la imagen de fondo, lo que repinta la pantalla entera en cada fotograma.
  - **Paneles de cristal:** botones, métricas, desplegables, campos, avisos y barra lateral usaban `backdrop-filter`, que desenfoca lo que hay detrás en cada fotograma y al desplazarse.
  - **Consultas:** las pantallas no tenían caché, así que cada clic repetía todas sus consultas a la base.

  Además, el asistente enseñaba el SQL de cada consulta, y se quería ver el proceso y el resultado, no el código.
- **Decisión:**
  - **Fondo:** rayos y burbujas se mueven solo con `transform`, sin filtro de desenfoque ni `background-attachment: fixed`.
  - **Cristal:** sin `backdrop-filter`. Es un fondo translúcido algo más opaco, con el mismo borde, reflejo y sombra.
  - **Caché de consultas** (`app/cache.py`): todas las consultas de `datos._filas` y `datos_contexto._filas` (también las de `datos_flujos` y `datos_mapa`) y las de las respuestas preparadas se guardan una hora. La base no cambia con la web abierta: para regenerarla hay que pararla.
  - **Asistente:**
    - se quita el SQL de las respuestas;
    - cada respuesta enseña, en este orden, el proceso de la consulta (tablas, uniones con su clave, pasos y la tarjeta del resultado con sus filas), el texto que se escribe y la salida (gráfico y tabla a la vista);
    - el proceso se anima una sola vez y en el historial se dibuja quieto; el CSS de las animaciones se carga una vez por página;
    - el texto se escribe en 40 trozos como mucho, en 1,5 s.
- **Alternativas consideradas:**
  - Mantener el desenfoque solo en la barra lateral. Seguía recalculándose sobre el fondo animado.
  - Quitar el fondo animado.
  - Dejar el SQL en un desplegable cerrado. Se pidió quitarlo.
- **Consecuencias:**
  - **Scroll medido en el navegador:** 241 fotogramas por segundo, con el más lento de 4 ms; no queda ningún `backdrop-filter`.
  - **Pantallas al volver a cargarlas:** entre 0,01 y 0,3 s (el mapa general, de 1,4 s a 0,04 s).
  - El cristal se ve algo menos esmerilado.
  - Quien quiera comprobar una consulta ya no ve el SQL; ve las tablas, las uniones y los pasos, los datos y el enlace oficial de cada fila.

## D-041 · Web fluida con el Inicio y el mapa de billetes
- **Fecha:** 2026-11-24
- **Estado:** Aceptada (El Harrak: «En una nueva rama, coge lo que ha hecho Ignacio e intenta fluidificarlo más, como hicimos antes»). Ajusta D-038 y D-039 (mascota) y se suma a D-040.
- **Autor:** Claude (agente), a petición de El Harrak
- **Contexto:** La rama `feat/billetes-fluido` junta `feat/mapa-billetes` (D-038 y D-039, de Ignacio) con `feat/web-fluida` (D-040). Medido en el navegador y en el servidor:
  - **Servidor:** las consultas nuevas ya tenían caché. Volver a cargar el Inicio tarda 0,03 s y el mapa, 0,07 s. Un año que no se había visto tarda unos 0,3 s más.
  - **Scroll:** 240 fotogramas por segundo en las dos pantallas, sin tareas largas. El grafo de frascos se queda quieto unos 0,3 s después de cambiar de año.
  - **Mascota:** el ojo con manos tenía 7 animaciones infinitas dentro del SVG. Las animaciones dentro de un SVG no pasan a la tarjeta gráfica, así que el navegador repintaba el dibujo en cada fotograma, sin parar, en el Inicio y en el mapa. En un portátil modesto es el único gasto continuo que quedaba aparte del fondo.
- **Decisión:**
  - La mascota se mueve unas vueltas al llegar (unos 10 a 25 s) y se queda quieta. Al pasar el ratón por encima vuelve a moverse.
  - `contain: layout paint` limita el repintado a su recuadro.
  - Con «reducir movimiento» sigue quieta.
- **Alternativas consideradas:**
  - Dejarla en bucle. Repinta siempre.
  - Pasar el salto al SVG entero para que lo mueva la tarjeta gráfica. La sombra y los billetes que caen saltarían con ella.
  - Quitar las animaciones.
- **Consecuencias:**
  - Ni el Inicio ni el mapa tienen animaciones que se repitan sin fin, salvo el fondo, que va por la tarjeta gráfica.
  - Test en `tests/app/test_billetes.py`.
  - Las demás pantallas de Ignacio no cambian.

## D-042 · «Contratos a revisar» para el ciudadano: filtros sencillos, tarjeta clara y más señales primero
- **Fecha:** 2026-11-24
- **Estado:** Aceptada por Ignacio («1 sí, 2 sí, 3 sí, 4 más señales primero»). Rama `feat/mapa-billetes`, que ya incluye `feat/billetes-fluido` de Ismael (D-040 y D-041). Falta que el equipo lo vea antes de fusionarlo.
- **Autor:** Claude (agente), a petición de Ignacio, en el repaso «dashboard a dashboard»
- **Contexto:** La lista tenía estos problemas:
  - 30 desplegables casi iguales, con títulos administrativos cortados («Este contrato tiene por objeto…», «Procedimiento de adjudicación de…»);
  - sin importe ni adjudicataria en la fila;
  - las señales en texto azul, como si fueran enlaces;
  - siete filtros técnicos («Mínimo de señales», «Cuántos mostrar», «Mayor puntuación»);
  - dentro, una explicación general repetida en cada señal y un párrafo técnico de atípico.
- **Decisión:**
  - **Filtros:** buscador y las seis señales como botones (`st.pills`, con icono y recuento). El resto va en «Más filtros», y «Cuántos mostrar» se sustituye por «Ver más contratos» (de 30 en 30, hasta 300; al cambiar los filtros se vuelve a 30).
  - **Orden por defecto: «Más señales primero».** La puntuación sigue como opción.
  - **Tarjeta:**
    - título limpio (`textos.titulo_limpio`);
    - importe en grande y adjudicataria (`datos.alertas` la trae, con las personas físicas agregadas como en D-007), organismo y año;
    - señales en etiquetas ámbar con icono (`:orange-badge[]`).
  - **Interior:**
    - el expediente oficial arriba;
    - **cada señal en su propia subcaja** (a petición de Ignacio, para distinguir mejor las explicaciones): de dos en dos, con la misma altura y un borde ámbar a la izquierda. Dentro, el nombre en ámbar con su icono, «En este contrato», la frase con cifras, el gráfico y, abajo, «¿Qué significa?» con la explicación general y el contexto;
    - el atípico en una frase llana («sus cifras se salen de lo habitual en N contratos parecidos; atípico no significa irregular») y el motivo técnico en «Ver el detalle».
  - **Aviso legal:** en el icono de información del título, como en el Inicio (D-039). El aviso corto de la barra lateral sigue visible.
- **Alternativas:** dejar «Mayor puntuación» con otro nombre; agrupar los contratos de un mismo acuerdo marco (descartado: son registros distintos en origen).
- **Consecuencias:** la tarjeta cambia también en las fichas de empresa y de organismo (comprobado sin errores). Ningún indicador ni cifra cambia. Docs: 03 y 08.
- **Ajustes del mismo día (Ignacio):**
  - **Color de las señales: azul de cristal** (#7DB3FF) en vez del naranja (`:orange-badge`), que no encajaba con la estética océano. Afecta a:
    - las etiquetas (`:blue-badge`, con estilo de cristal en `estilo.css`, `.stMarkdownBadge`);
    - el nombre y el borde de cada subcaja;
    - la cuadrícula del Inicio (`billetes.COLOR_SENAL`).
    El ámbar queda solo para las líneas de referencia de los gráficos. Cambia la regla de `docs/marca.md`.
  - **«Sin anuncio público»:** la frase se parte en «En este contrato: se adjudicó sin anuncio público (vía: …)» y «Para comparar: de cada 100 € que el organismo adjudicó en la misma fuente, X € fueron sin anuncio». Se corrige un error: antes decía «de sus contratos de este tipo», pero la cifra cuenta todos los contratos del organismo en esa fuente, de cualquier tipo. `datos.detalle_r02` devuelve además el procedimiento del contrato.
  - **«Una empresa concentra el gasto»:**
    - el donut pasa a un ranking de barras de «de cada 100 €» por empresa, con la de este contrato en azul y una línea de puntos en «la mitad», que es donde salta la señal (`graficos.reparto`);
    - la frase dice «De cada 100 € que X adjudicó en contratos de suministros de [sector], 52 € fueron a Y (entre N empresas). La señal salta cuando una sola empresa se lleva más de la mitad»;
    - el sector sale del nombre de la división CPV, o «de este sector» si falta la lista de CPV.
  - **«Muchos contratos menores»:** al elegir una señal que solo se comprueba en contratos menores (R-03), la lista los incluye sola y lo dice; antes salía vacía. Los títulos escritos todo en mayúsculas se pasan a frase normal.
  - **Gráficos y frases de R-03, R-05 y R-06** (Ignacio: «poco intuitiva», «muy fea», «muy sosa» y «¿de qué forma sabemos que gana?»):
    - **R-03:**
      - los contratos menores de los 12 meses en que más suman, como bloques en una barra (este en azul, con «este»), frente a la línea del máximo de un contrato menor, con la suma al final (`graficos.ventana_doce_meses`, `graficos.menores`);
      - frase: «es uno de los N contratos menores… Juntos suman X, más que el máximo de un contrato menor».
    - **R-05:**
      - «antes y después»: el precio adjudicado frente al precio con modificaciones, que crece en dos tramos (hasta el 20 % y por encima), con la línea del +20 % y la subida en grande;
      - frase con «En este contrato» y «Para comparar» (el 20 % es el máximo de las modificaciones previstas en el pliego; otras pueden estar justificadas).
    - **R-06:**
      - una regla de la rebaja con las dos zonas donde salta la señal sombreadas, el marcador de este contrato y el de la rebaja habitual;
      - la rebaja habitual es la mediana de los contratos de la misma fuente y tipo en los que se comprueba R-06 (`datos.baja_habitual`; p. ej., 17 % en 3.112 servicios de la Plataforma);
      - la frase explica el precio de salida, cuántas ofertas hubo y por cuánto se adjudicó.
    - **Textos de «¿Qué significa?»:**
      - el de R-06 explica cómo funciona un concurso (precio de salida, ofertas, a quién se adjudica) en lugar de «la empresa ganó rebajando…»;
      - el de R-05 explica qué es una modificación.
    - Las líneas de referencia de estos gráficos pasan del ámbar a un gris claro de puntos.
  - **R-03, segunda versión (Ignacio):**
    - en lugar del gráfico de bloques, un contrato grande con «Suma de los contratos menores: X», «Máximo de un contrato menor: Y» y cuántas veces el máximo;
    - debajo, un icono de contrato por cada contrato menor de la ventana de 12 meses, el de este en azul con «este». Al pasar el ratón (o con el teclado) se ve su precio, su fecha y su título;
    - HTML propio (`billetes.html_menores`, con el componente de `billetes.pintar`); se quita `graficos.menores`;
    - la frase ya no repite la suma.

## D-043 · Web ligera: sin barra lateral, barra de arriba con menú, avisos en el pie y entrada animada
- **Fecha:** 2026-11-24
- **Estado:** Aceptada por El Harrak como **versión alternativa** en la rama `feat/web-ligera`, que sale de `feat/mapa-billetes` (D-038 a D-042). Si el equipo la prefiere, sustituye a la navegación con barra lateral de D-023.
- **Autor:** Claude (agente), a petición de El Harrak («simplificar el HTML aligerando un poco a la vista»)
- **Contexto:** La web era pesada a la vista. Tenía cuatro problemas:
  - **Barra lateral** con diez entradas, el aviso, las fechas y la metodología.
  - **Avisos y fuentes** también arriba de algunas pantallas.
  - **Dos mascotas:** el ojo con billetes salía en el Inicio y en el mapa.
  - **Desplegables translúcidos:** su fondo se mezclaba con el mar y costaba leerlos.
- **Decisión:**
  - **Sin barra lateral.** Arriba hay una barra fija con el logo, cuatro botones (Inicio, A dónde va el dinero, Contratos a revisar y Asistente) y «Explorar», que abre el resto de pantallas (`st.navigation(position="hidden")` y `st.page_link`).
    - «Explorar» lleva Mapa del dinero, Presupuesto y contexto, Ficha de empresa y Ficha de órgano.
    - También lleva Contratos atípicos, que no tiene botón arriba y si no quedaría sin enlace.
    - Primero se llamaba «Menú» y repetía todas las pantallas.
  - **Pie en todas las pantallas**, abajo del todo:
    - el aviso corto;
    - el desplegable «Aviso legal, metodología y fuentes», con el aviso, la nota de las señales, qué mide cada indicador, las fuentes y el pie legal;
    - las fechas de descarga.
    - El pie se dibuja antes que la pantalla y el CSS lo coloca al final, así que sale aunque la pantalla se pare esperando una elección.
  - **Notas de una pantalla, al final de esa pantalla:**
    - «Cómo se calculan los contratos atípicos» pasa al pie de Atípicos;
    - las fuentes del mapa del dinero pasan al desplegable final «Fuentes y qué datos no tenemos»;
    - se quita el botón «Fuentes» de arriba del Inicio y del mapa, y las fuentes repetidas al final del Asistente.
    - Siguen donde estaban los iconos de ayuda («una señal no prueba nada») de los títulos y los avisos ligados a una cifra concreta.
  - **Inicio con solo el logo.** La mascota con billetes queda en «A dónde va el dinero».
  - **Desplegables opacos.** Desplegables, ventanas emergentes, listas de opciones y ayudas tienen fondo azul marino opaco.
  - **Entrada animada de 3 s**, la primera vez que se abre la web en la sesión (`static/intro.html` y `app/intro3d.py`):
    - mar muy oscuro con nieve marina;
    - aparece el **ojo 3D de la presentación**, con el mismo código (`presentacion/ojo3d.js`) y Three.js 0.169.0 de jsDelivr;
    - se ilumina como en la presentación: entorno de reflejos y color del agua de `presentacion/agua.js`, el mismo tono de imagen (`NeutralToneMapping`), cielo y sol, y el **mismo posproceso** (brillo `UnrealBloomPass` 0,55 / 0,7 / 0,82 y `OutputPass`). Al brillo se le corrige la opacidad para que no tape la página;
    - **el ojo es la fuente de luz**, pero por dentro se ve como en la presentación: el iris, la pupila y el cristal, sin núcleo ni destello pintados encima. La luz sale hacia fuera y queda un halo suave por detrás del cristal, que crece poco a poco al ritmo con que se aclara la página, sin encenderse de golpe;
    - se acerca un poco y **sube alejándose hasta cerca del borde de arriba**, sobre el título (así también se ve en el móvil), mirando hacia la página. Allí **se desvanece poco a poco** con su luz, de 1,95 a 3 s; la opacidad la lleva el mismo bucle que el movimiento, para que vayan a la par;
    - al apartarse, su núcleo se enciende y **despliega la luz de la presentación**: el cono de luz del ojo (`crearLuz`) y los haces de los rayos de sol (`crearRayos`), con la raíz en el ojo. Empiezan rectos hacia abajo y se abren poco a poco a los lados, como mucho a 66° de la vertical, sin apuntar nunca hacia arriba; aclaran la página mientras el ojo sube. La luz es suave (cono 0,5, haces 0,26, brillo 0,35) para que se funda con la página en vez de taparla. Toda se calcula en sombreadores, sin texturas, así que no se pixela, y se apaga antes de terminar;
    - **el ojo, ligero y nítido**: se dibuja al doble de resolución y con suavizado de bordes también en el posproceso. Es algo más pequeño (0,47), más claro (agua de superficie ×1,35 y exposición 1,3) y con un halo discreto;
    - **el mar de la presentación, de principio a fin**: rayos de sol muy tenues y burbujas plateadas que suben (`crearRayos` y `crearBurbujitas` de `agua.js`), sin la superficie, porque estamos en el fondo y todo es oscuro, más claros a medida que se aclara la página y fundidos al final con el fondo de la web. La nieve marina es la capa CSS: la de la presentación usa puntos de WebGL, que aquí salían como cuadrados;
    - **la página se desvela de abajo arriba**: el mar oscuro es una cortina con el borde difuminado que sube desde 1,26 s (solo `transform`).
    - Al terminar se libera WebGL y se quita el lienzo.
    - **Reserva:** si Three.js no carga en 1,2 s (sin red o sin WebGL), sale el ojo plano de `app/ojo_cristal.py`, que también sube. Si nada arranca, la capa se quita sola a los 2,5 s.
    - Las capas CSS solo animan opacidad y transformaciones, no bloquean los clics y no salen con «reducir movimiento».
    - **Versiones anteriores** (a petición de El Harrak):
      - 1,5 s con el logo;
      - 3 s con el ojo de la presentación en plano;
      - el ojo 3D yéndose a la izquierda, más oscuro y con la luz hacia la derecha;
      - el ojo subiendo solo hasta arriba de la pantalla, sin rayos;
      - rayos en todas direcciones con una textura que se pixelaba.
- **Alternativas consideradas:**
  - Barra lateral plegada por defecto: seguía ahí y el aviso no se veía.
  - Navegación nativa arriba (`position="top"`): con diez entradas se desborda.
  - Entrada en cada cambio de pantalla: cansa.
- **Consecuencias:**
  - El aviso legal deja de estar siempre a la vista en la barra lateral: queda abajo, más los iconos de ayuda de los títulos. Conviene que `revisor-legal` lo valide antes de la entrega.
  - Medido: scroll a 240 fotogramas por segundo, sin tareas largas; las nueve pantallas cargan sin errores y todas tienen pie.
  - Tests en `tests/app/test_intro.py`.

## D-044 · Sin tarjeta gráfica, entrada con el ojo plano y fondo quieto
- **Fecha:** 2026-11-24
- **Estado:** Aceptada (El Harrak: «Vale, pues haz eso», sobre detectar el dibujo sin tarjeta gráfica). En la rama `feat/web-ligera`, junto a D-043.
- **Autor:** Claude (agente), a petición de El Harrak
- **Contexto:** En Microsoft Edge la web iba lenta. Casi todos los equipos tienen tarjeta gráfica, aunque sea la integrada, pero hay navegadores que no pueden usarla y lo dibujan todo con el procesador:
  - aceleración por hardware desactivada;
  - controlador antiguo y bloqueado;
  - escritorio remoto o máquina virtual;
  - equipos con restricciones.

  En esos casos, la entrada 3D de D-043 (doble resolución y brillo) y el fondo animado iban a tirones. La reserva de la entrada solo saltaba si el 3D no cargaba, no si cargaba pero se dibujaba por software.
- **Decisión:** `app/rendimiento.py` comprueba al abrir la página si el navegador dibuja con tarjeta gráfica:
  - pide a WebGL un contexto con `failIfMajorPerformanceCaveat` y mira el nombre del dibujador (SwiftShader, llvmpipe, Microsoft Basic Render…);
  - guarda el resultado para la pestaña (`sessionStorage`, `oc-gpu`).
  - Sin tarjeta gráfica:
    - la página lleva la clase `oc-sin-gpu`;
    - la entrada usa el ojo plano (CSS) en vez del 3D, sin descargar Three.js;
    - los rayos y las burbujas del fondo se quedan quietos.
  - Con tarjeta gráfica no cambia nada.
- **Alternativas consideradas:**
  - Medir los primeros fotogramas y bajar la calidad sobre la marcha: es más complejo y la entrada ya habría empezado a tirones.
  - Quitar la entrada 3D para todos.
  - Avisar al usuario de que active la aceleración.
- **Consecuencias:**
  - Comprobado en el navegador en los dos casos: con tarjeta gráfica, entrada 3D y fondo en movimiento; simulando que no la hay (`oc-gpu` = `no`), ojo plano, sin Three.js y el fondo quieto.
  - Si Edge u otro navegador va lento por desactivar el optimizador de JavaScript («Mejorar la seguridad en la web»), esto no lo arregla: hay que añadir una excepción para el sitio.
  - Tests en `tests/app/test_rendimiento.py`.

## D-045 · Diseño expandido y cabecera moderna
- **Fecha:** 2026-11-24
- **Estado:** Aceptada (El Harrak: «rediseñes la página web expandiendo todo… el logo simplemente arriba a la izquierda y los botones arriba a la derecha, como lo hacen muchas páginas modernas actuales»). En la rama `feat/web-ligera`, sobre D-043.
- **Autor:** Claude (agente), a petición de El Harrak
- **Contexto:** La página usaba 1.200 px de ancho en el centro: en una pantalla de 1.920 px quedaba más de un tercio vacío. La barra de D-043 era una cápsula con todo junto en el centro. Referencias consultadas:
  - logo arriba a la izquierda y navegación en una línea a la derecha, el patrón más común; el logo a la izquierda se recuerda mejor;
  - ancho máximo de contenido de 1.280 a 1.440 px con márgenes laterales que crecen con la pantalla;
  - espaciado en múltiplos de 8 px.
- **Decisión (`static/estilo.css`):**
  - **Ancho:** contenido de hasta 1.680 px, casi toda la pantalla grande, con márgenes laterales de 20 a 64 px (`clamp(1.25rem, 4vw, 4rem)`).
  - **Espaciado:** variables de 8 px (`--oc-e1` … `--oc-e8`); 24 px entre bloques. Texto base de 16,5 px con interlineado 1,6.
  - **Cabecera sin banda:** el mismo fondo que el resto de la página.
    - El logo (36 px) y el nombre, a la izquierda.
    - A la derecha, los botones juntos en una cápsula de cristal sutil, con la sección abierta rellena de azul. Si la pantalla es una de «Explorar», se resalta «Explorar».
    - La marca `main.marcar_seccion`, porque Streamlit no marca el enlace activo con un atributo estable.
    - Por debajo de 1.080 px, solo iconos; en móvil, también sin el nombre, y «Explorar» como icono.
    - Se desplaza con la página: sin fondo propio, fija se pondría encima del contenido.
    - Primero fue una banda fija y opaca de borde a borde; a El Harrak no le gustó una franja más oscura.
  - **Inicio:** el título y el logo crecen con la pantalla (`clamp`), con más separación entre las tarjetas y más relleno dentro.
  - El mapa general deja su ancho propio de 1.500 px y usa el común.
- **Alternativas consideradas:**
  - 1.440 px, como recomiendan varias guías: en una pantalla de 1.920 px seguía dejando un 25 % vacío, y se pidió usar toda la pantalla.
  - Menú hamburguesa en móvil: con cuatro iconos y «Explorar» cabe en una línea.
- **Consecuencias:**
  - Comprobado en el navegador a 1.920, 1.280, 1.000 y 390 px de ancho.
  - El estilo de la cabecera usa clases y estructura de Streamlit 1.67 (`stLayoutWrapper`, `stPageLink`, `stPopover`). Si se actualiza Streamlit, hay que revisarlo.

## D-046 · Mapa del dinero con burbujas o frascos, cabecera solo con el nombre e Inicio con menos texto

- **Fecha:** 2026-11-24
- **Estado:** Aceptada (Ismael: «que esté su opción, pero que haya un switch… lo mío tenía muchísima más información»). En la rama `feat/web-retoques`, sobre `feat/web-ligera` (D-043 a D-045).
- **Autor:** Claude (agente), a petición de Ismael
- **Contexto:** D-038 cambió las burbujas del mapa general (D-033) por frascos de 100 billetes. Los frascos se entienden mejor de un vistazo, pero perdían información:
  - el llenado según lo gastado;
  - el tamaño según el dinero;
  - los contratos menores y las subvenciones agrupados;
  - la tabla de cada consejería.

  Además:
  - el logo salía dos veces en el Inicio;
  - el buscador parecía un desplegable;
  - las burbujas del fondo parecían pintadas con rotulador;
  - el doble clic en un nodo del mapa abría una pestaña rota.
- **Decisión:**
  - **Mapa del dinero** (`paginas/mapa_general.py`):
    - **Interruptor:** «Burbujas» (por defecto) / «Frascos de 100 €».
    - **Burbujas (D-033):** tamaño y color = dinero; cada burbuja se llena hasta lo gastado, con la superficie ondulada como en la presentación (`red.svg_nodo`). Vuelven:
      - los menores y las subvenciones agrupados, como opción;
      - las cifras de la ficha;
      - la tabla de contratos de cada consejería;
      - el gráfico de dinero sin gastar;
      - la tabla de todas las consejerías.
    - **Frascos (D-038):** se mantienen, con un dibujo nuevo (`billetes.svg_frasco`): cristal con hombros redondeados, tapa azul de la marca y billetes con brillo.
  - **Nombres de las pantallas:**
    - La pestaña «A dónde va el dinero» pasa a llamarse **«Mapa del dinero»**.
    - La red de adjudicaciones (antes «Mapa del dinero») pasa a **«Red del dinero»**.
    - La puerta del Inicio sigue diciendo «¿A dónde va el dinero?».
  - **Cabecera:** solo «Ojo Ciudadano», sin el icono. El logo con el nombre va en el pie, y el logo grande queda en el Inicio.
  - **Inicio:**
    - Sin el subtítulo ni la línea de cifras: esas cifras van en las pantallas de análisis.
    - Buscador como barra de búsqueda: cápsula de cristal con lupa y sin flecha. El fondo del iframe se vuelve transparente con un componente que corre en la página.
  - **Fondo:** burbujas sin trazo, con el borde que se aclara poco a poco y un reflejo difuso (SVG generados).
  - **Doble clic en el mapa:** `streamlit-agraph` hace `window.open(título del nodo)`. Un componente anula `window.open` dentro de sus iframes, que son del mismo origen.
- **Alternativas consideradas:**
  - Volver solo a las burbujas: se pierde el «de cada 100 €», que Ignacio quería para el ciudadano.
  - Parchear el paquete `streamlit-agraph`: se perdería al reinstalar.
- **Consecuencias:**
  - Los dos parches de iframes (buscador y mapa) dependen de que los componentes sigan siendo del mismo origen.
  - Una base generada antes de D-036 no tiene `adjudicatario_ente_publico` y «Contratos a revisar» falla. Se arregla con `uv run python -m ojo_ciudadano.ingesta.invente` y `uv run python -m ojo_ciudadano.indicadores.ejecutor`.

## D-047 · Mapa de burbujas dibujado como en la presentación, barra de dinero sin Plotly y pie sencillo

- **Fecha:** 2026-11-24
- **Estado:** Aceptada (Ismael: «mira la diferencia entre el gráfico de las burbujas que has dibujado en la presentación y el que hay luego realmente en la página web… no tienes por qué usar Plotly»). En la rama `feat/web-retoques`, sobre D-046.
- **Autor:** Claude (agente), a petición de Ismael
- **Contexto:** En el Mapa del dinero, las burbujas eran imágenes SVG dentro de `streamlit-agraph` (vis-network): planas y muy lejos de las de la presentación. Debajo había dos gráficas, una en HTML y otra en Plotly, que repetían información. El pie tenía demasiadas cosas sueltas.
- **Decisión:**
  - **Burbujas en un lienzo propio** (`app/burbujas.py`, un componente `components.v2` que corre en la página):
    - **Cristal:** borde que se aclara (Fresnel) y un arco de reflejo suave, sin manchas de dibujo animado.
    - **Líquido:** sube hasta lo gastado, con la superficie en perspectiva y ondulada.
    - **Entrada:** al abrir el mapa, el líquido sube y las burbujas crecen.
    - **Movimiento:** las burbujas flotan y unas motas de luz recorren las líneas.
    - **Interacción:** cuadro al pasar el ratón y clic que abre la ficha.
    - **Sin tarjeta gráfica (D-044) o con «reducir movimiento»:** se dibuja quieto.
    - Mismas escalas de tamaño y color que `red.mapa`. Los frascos siguen en `streamlit-agraph`.
  - **Una sola barra por consejería** (`barras_dinero`, HTML y CSS):
    - el largo es todo su dinero del año;
    - dentro, lo gastado en azul intenso, y lo que queda sin gastar en cristal claro;
    - a la derecha, el porcentaje y lo que queda sin gastar.

    Las dos gráficas anteriores quedan en un desplegable «Gráficas por separado».
  - **Plotly** se queda para las gráficas del asistente y las secundarias. Las importantes se hacen a mano.
  - **Pie:** el desplegable «Aviso legal, metodología y fuentes» lleva dentro el aviso corto, las notas de la pantalla y las fechas de descarga. Debajo, lo último y centrado, el logo con el nombre. En el Inicio, solo el logo.
  - **Cabecera:** en el Inicio, solo el nombre (el logo grande está debajo); en las demás pantallas, el logo y el nombre.
  - **Buscadores:** los de las fichas también como barra de búsqueda. Al ir a una ficha desde el Inicio se olvida la búsqueda: antes, volver al Inicio llevaba otra vez a la ficha.
- **Alternativas consideradas:**
  - Three.js, como en la presentación: más peso y dependencia de un CDN en la web. El lienzo 2D consigue el mismo lenguaje (cristal, líquido, luz) sin dependencias y sin tarjeta gráfica.
  - Arrastrar las burbujas: se pierde. El diseño radial ya no se pisa y el clic es lo que importa.
- **Consecuencias:**
  - El mapa de burbujas ya no depende de `streamlit-agraph`.
  - Las etiquetas se dibujan en el lienzo. Lo accesible sigue estando en la tabla de todas las consejerías.

## D-048 · Portada como página de bienvenida, no como panel

- **Fecha:** 2026-11-25
- **Estado:** Aceptada (Ismael: «parece demasiado como un panel informativo en vez de una web accesible y amable»). En la rama `feat/web-retoques`. Es el 25-nov, día sin funciones nuevas según el plan: es un rediseño de la portada pedido expresamente y no añade cálculos nuevos, solo dos consultas de lectura sobre los indicadores existentes.
- **Autor:** Claude (agente), a petición de Ismael
- **Contexto:** Lo que había en el Inicio:
  - el título alineado a la izquierda y un buscador de borde a borde;
  - cuatro puertas;
  - seis cuadrículas iguales de «de cada 100 contratos», que no transmitían el peso de cada señal.
- **Decisión** (`paginas/inicio.py`), de arriba abajo:
  1. **Cabecera:** el logo y la frase, centrados, y el buscador más estrecho (760 px como máximo).
  2. **Qué hace Ojo Ciudadano:**
     - a la izquierda, «Siempre fueron públicos. Ahora, por fin, accesibles.» y tres frases cortas;
     - a la derecha, un mapa de burbujas vivo (`burbujas.vista_previa`, el lienzo de D-047) con la Comunidad, sus 8 consejerías con más dinero y los dos contratos más grandes de las tres primeras;
     - cada burbuja lleva a su ficha en el Mapa del dinero.
  3. **«Qué ofrecemos»:** tres puertas, Mapa del dinero, Contratos a revisar y Asistente de IA. Desaparece «Busca una empresa», porque ya está el buscador.
  4. **Asistente de IA:** el ojo de cristal de la presentación, con el iris girando, y un ejemplo de pregunta y respuesta con su fuente.
  5. **«Contratos que destacan»:** tres señales contadas en dinero, cada una con su propio dibujo (`datos.destacados_portada`):
     - **una sola oferta:** dinero adjudicado así, con una barra sobre el total comprobado;
     - **modificaciones de más del 20 %:** cuánto subieron, comparado con la consejería de presupuesto más parecido, en dos burbujas;
     - **concentración:** el caso con más dinero, en un anillo. Solo se nombra el organismo, no la empresa.

     El aviso de que una señal no prueba nada y los enlaces a las fuentes van debajo.
- **Alternativas consideradas:**
  - Mantener las seis señales: demasiado para una portada; siguen explicadas en «Contratos a revisar».
  - El ojo en 3D: el de la entrada ya usa WebGL; aquí basta el SVG del ojo de cristal.
- **Consecuencias:** las cifras de la portada salen de la base en cada carga (en caché una hora), con sus fuentes enlazadas.

## D-049 · Fuera los frascos: el Mapa del dinero solo con burbujas y en dos niveles

- **Fecha:** 2026-11-25
- **Estado:** Aceptada (Ismael: «hemos quedado en que vamos a quitar los frascos con mis compañeros… vamos con las burbujas a tope»). Sustituye a la parte de mapa de D-038 y al interruptor de D-046.
- **Autor:** Claude (agente), a petición de Ismael
- **Decisión:**
  - El Mapa del dinero solo tiene burbujas (D-047): se quita el interruptor y el código de los frascos de la pantalla.
  - Por defecto se ven dos niveles: las consejerías y sus dos contratos más grandes.
  - La tarjeta del año con la mascota sigue igual.
- **Consecuencias:**
  - `billetes.svg_frasco` queda solo para su test y para el icono antiguo de la puerta, que ya no se usa en el Inicio. Se puede borrar más adelante.
  - Las cifras de la ficha lateral se achican para que no se corten.

## D-050 · Logo arriba también en el Inicio, consejería al centro al pulsarla y Red del dinero con las burbujas del lienzo

- **Fecha:** 2026-11-25
- **Estado:** Aceptada (Ismael). En la rama `feat/web-retoques`, sobre D-047 a D-049.
- **Autor:** Claude (agente), a petición de Ismael
- **Decisión:**
  - **Logo:** sale arriba con el nombre en todas las pantallas, también en el Inicio. Se quita el logo grande de encima del título del Inicio.
  - **Inicio:**
    - el mapa de burbujas a la izquierda y el texto a la derecha, más juntos, sin el texto de debajo del mapa;
    - la lista del buscador sale por encima de la página (`style_absolute`), sin empujar lo de debajo;
    - las modificaciones, en dos barras con la misma escala en lugar de dos burbujas;
    - el anillo de la concentración, en dos partes con extremos rectos y un hueco (lo de una empresa en azul y el resto en ámbar), con su leyenda.
  - **Mapa del dinero:**
    - pulsar una consejería la pone en el centro con todo lo que conecta: sus 15 contratos más grandes, los menores y las subvenciones;
    - pulsar el centro abre su ficha;
    - por defecto, dos contratos por consejería, ajustable hasta cinco.
  - **Red del dinero** (Explorar): no es lo mismo que el Mapa del dinero, porque va por organismo de contratación y empresa, con filtros de fuente, año, tipo y menores. Se mantiene con las burbujas del lienzo (`app/burbujas.py`) en lugar de Plotly y `streamlit-agraph`:
    - los 12 organismos que más adjudican, alrededor de un centro;
    - al pulsar uno, su red con sus empresas;
    - al pulsar una empresa, sus contratos debajo.

    El diagrama de flujos sigue en la vista avanzada.
- **Consecuencias:** `streamlit-agraph` ya no se usa en ninguna pantalla. `graficos.burbujas_organismos` y `red.mapa` quedan solo para sus tests; se pueden borrar más adelante.

## D-051 · Logo junto al título del Inicio y buscador debajo del mapa

- **Fecha:** 2026-11-25
- **Estado:** En prueba (Ismael: «a ver cómo queda»). En la rama `feat/web-retoques`, sobre D-050.
- **Autor:** Claude (agente), a petición de Ismael
- **Decisión:**
  - **Logo:** en el Inicio va a la izquierda del título, de tamaño medio; arriba solo el nombre. En las demás pantallas, el logo arriba con el nombre.
  - **Orden del Inicio:**
    1. el título;
    2. el mapa de burbujas con el texto;
    3. el buscador;
    4. «Qué ofrecemos»;
    5. el asistente;
    6. los contratos que destacan.
  - **Aviso y fuentes:** el aviso de que una señal no prueba nada y las fuentes de los contratos salen de la portada y pasan a la cabecera de «Contratos a revisar».
- **Consecuencias:** las cifras de los destacados de la portada ya no llevan su enlace a la fuente en la misma pantalla; lo llevan «Contratos a revisar» y el pie de las demás pantallas. Hay que revisarlo con el equipo frente a la regla de «cada cifra enlaza a su fuente».

## D-052 · Mapa del dinero: el presupuesto en una barra, lo primero

- **Fecha:** 2026-11-25
- **Estado:** Aceptada (Ismael: «lo primero tendría que salir el selector de año y luego ya el presupuesto general y el mapa»).
- **Autor:** Claude (agente), a petición de Ismael
- **Decisión:**
  - Debajo del selector de año, «Presupuesto 2025» con el total y una sola barra llena hasta lo gastado, con una marca donde acaba. Debajo, lo gastado (y su %) y lo que quedó sin gastar. Sin frases.
  - La tarjeta de la mascota con lo que tocaría a cada habitante pasa a un desplegable al final, «Si se repartiera entre todos los habitantes».
  - En el Inicio, las tres tarjetas de «Qué ofrecemos» se pueden pulsar enteras: lo de dentro de la tarjeta deja de tener posición propia, para que el enlace se estire sobre toda ella.

## D-053 · Portada: el mapa de burbujas con la animación de la presentación

- **Fecha:** 2026-11-25
- **Estado:** Retirada el mismo día (Ismael: «no me terminó de convencer… vamos a volver a lo de antes»). Se vuelve al estilo del lienzo de D-047 con el líquido algo más azulado (mezclado con el azul de la marca), y se borra el código del estilo «presentacion». Se deja aquí como registro.
- **Autor:** Claude (agente), a petición de Ismael
- **Decisión:** el lienzo de `app/burbujas.py` tiene un segundo estilo, `estilo="presentacion"`, que solo usa la portada:
  - burbujas de azul intenso con ondas de luz (cáusticas) que se mueven dentro, reflejos arriba y halo;
  - líneas como collares de perlas de luz que avanzan de la burbuja grande a la pequeña;
  - nombres en mayúsculas y espaciados, sin cifras debajo;
  - la cifra total y «Comunidad de Madrid · año» dentro de la burbuja central;
  - la burbuja central y las consejerías, algo más grandes.

  El Mapa del dinero sigue con el estilo `mapa`, más sobrio y con cifras, porque ahí se lee y se compara.
- **Consecuencias:** las cifras de cada consejería en la portada salen al pasar el ratón.

## D-054 · Mapa del dinero: «¿De dónde viene el dinero?» al lado de «¿A dónde va?»

- **Fecha:** 2026-11-25
- **Estado:** Aceptada (El Harrak: «haz merge de todo el trabajo… directamente en main», 25-nov). Se hizo en una rama aparte (`feat/de-donde-viene`); entra en `main` el 25 aunque el plan dice que ese día no se añaden funciones, por decisión expresa de El Harrak.
- **Autor:** Claude (agente), a petición de El Harrak
- **Contexto:** el mapa del dinero solo contaba en qué se gasta. La base ya tiene, del catálogo de datos abiertos de la Comunidad (`serie_cm`, D-024), los ingresos por capítulo (iniciales hasta 2026 y liquidados hasta 2025), el sistema de financiación autonómica y las ayudas de la UE (hasta 2023). No hace falta bajar nada nuevo.
- **Decisión:**
  - Arriba del Mapa del dinero, un selector grande a lo ancho con dos tarjetas: «¿A dónde va el dinero?» (por defecto, la vista de siempre) y «¿De dónde viene el dinero?». La tarjeta sin elegir late cuatro veces y se para (sin animación sin fin, D-041). El año es el mismo para las dos.
  - «¿De dónde viene?» (`app/de_donde_viene.py`):
    - una barra con «de cada 100 € que entran»: impuestos directos, indirectos, préstamos y el resto;
    - tres cifras: lo que entra, el saldo neto de transferencias corrientes y los ingresos netos;
    - el mapa de burbujas con la misma estética que el de gastos, con una ficha por tipo de ingreso; con el año cerrado, cada burbuja se llena hasta lo que entró frente a lo previsto;
    - una explicación neutra del sistema de financiación autonómica, con sus cifras;
    - los impuestos divididos entre habitantes, las ayudas de la UE y las fuentes.
  - Con el año cerrado, «entró» son los **derechos reconocidos**, como «gastado» son las obligaciones reconocidas. Si no, el presupuesto inicial.
  - Los textos los revisó `revisor-legal`: la explicación del sistema de financiación es técnica y neutra (Ley 22/2009, población ajustada, signo de cada fondo), sin «Madrid paga por otros»; se avisa cuando se mezclan años; cada bloque de cifras lleva su fuente con enlace y fecha.
- **Alternativas consideradas:** una pantalla nueva en «Explorar» (se ve menos; el usuario quería que estuviera al lado de «a dónde va»); un diagrama de flujo de ingresos a gastos (no se puede seguir un euro de un impuesto a un contrato: el dinero entra en una caja común).
- **Consecuencias:**
  - Ninguna tabla nueva; solo consultas en `app/datos_contexto.py` (`ingresos_del_anio`, `sistema_financiacion`, `ayudas_ue`).
  - El cuadro al pasar el ratón por una burbuja acepta otra lectura del llenado (`extra["linea_llenado"]` en `red.py`).
  - El estilo del selector depende de cómo pinta Streamlit 1.67 el `segmented_control` (`role="radio"`, `aria-checked`).
## D-055 · Gráficos de Plotly con estilo acuático (opción A: solo el tema)

- **Fecha:** 2026-11-25
- **Estado:** Aceptada (El Harrak: «haz merge de todo el trabajo… directamente en main», 25-nov). Se hizo en una rama aparte (`feat/graficos-acuaticos`) para no arriesgar la entrega.
- **Autor:** Claude (agente), a petición de El Harrak
- **Contexto:** los unos 20 gráficos de Plotly (fichas, señales, atípicos, contexto, asistente) no seguían el estilo acuático de la web. Se valoraron tres caminos:
  - **A:** cambiar el tema de Plotly, 4–8 h;
  - **B:** rehacerlos todos con dibujo propio, 6–10 días;
  - **C:** mixto.
  Se eligió A por el riesgo, a un día de la entrega.
- **Decisión:**
  - Todo en el tema común `_tema` de `app/graficos.py`, que usan todos los gráficos:
    - rejilla casi invisible;
    - barras de cristal: translúcidas, con borde claro y esquinas redondeadas;
    - puntos como burbujas: degradado radial con el borde más claro;
    - cuadro al pasar el ratón con nuestra letra (Inter, 14 px), sin cortar nombres.
  - En `estilo.css`:
    - el cuadro al pasar el ratón como una burbuja: más margen con un trazo grueso del color del fondo, esquinas redondeadas, borde de luz y sombra;
    - un halo azul suave en el grupo de barras (un solo filtro, sin él en equipos sin tarjeta gráfica, D-044);
    - entrada suave de cada gráfico (opacidad y `transform`).
  - Los colores, la forma de cada gráfico y sus frases no cambian.
- **Alternativas consideradas:** B y C (ver contexto), para después de la entrega si se quiere ir más lejos.
- **Consecuencias:**
  - El cuadro al pasar el ratón depende de cómo dibuja Plotly su etiqueta (`.hoverlayer .hovertext path`).
  - Las barras más translúcidas tienen algo menos de contraste. El borde claro las separa del fondo, pero conviene revisarlas en la pantalla de la demo.
- **Ajuste del mismo día (lo atípico en ámbar y menos tirones):**
  - **Ámbar:** lo atípico pasa al ámbar de la presentación (`#E0A032` y `#FFD27A`, tono «ambar» de `presentacion/escena3d.js`):
    - en el gráfico E-07, el contrato es una burbuja ámbar de cristal con un halo que se apaga hacia fuera (dos puntos, sin 3D);
    - en el histograma, la línea y su etiqueta van en ámbar;
    - en la ficha de contrato del Mapa del dinero, «Contrato atípico» sale en naranja.
  - **Menos tirones:**
    - los puntos con degradado solo se usan en trazas de hasta 50 puntos (la nube de atípicos tiene 1.500 y cada degradado es un elemento SVG propio);
    - se quitan el halo de las barras y la sombra grande del cuadro al pasar el ratón, que se recalculaban en cada redibujado;
    - la entrada de los gráficos es solo de opacidad.
- **Ajuste del mismo día (abrir un contrato atípico sin esperas):**
  - Cada contrato de la pantalla de atípicos va en su propio fragmento (`st.fragment`): al abrirlo solo se vuelve a ejecutar ese contrato, no toda la pantalla con sus filtros y su lista.
  - La frase «Por qué se aleja» sale al momento. Mientras se prepara el gráfico, en su sitio está nuestro ojo con el iris girando y «Preparando el gráfico…» (`app/cargando.py`, reutilizable).
  - La nube de comparación se dibuja con WebGL (`Scattergl`).
  - Al abrir, el contenido entra con una transición corta; el gráfico aparece con opacidad y `transform`, una sola vez.
- **Ajuste del mismo día (fichas de empresa y de organismo):**
  - El mapa de rectángulos «De qué organismos» / «A qué empresas» pasa a cristal en el tema común: colores translúcidos, borde claro, esquinas redondeadas y aire entre rectángulos.
  - Las tarjetas de contrato (`senales.tarjeta_contrato`, en las dos fichas y en «Contratos a revisar») van en su propio fragmento, con el ojo girando mientras se calculan sus señales.
  - «Contrato atípico» dentro de la tarjeta, en ámbar.
  - Todos los desplegables se abren con la misma transición corta, y sus gráficos entran animados.
- **Ajuste del mismo día (solo azules y grises; el ámbar, solo para lo atípico):**
  - La paleta categórica pasa a azules y grises azulados, alternando claros y oscuros: `#3D8BFD`, `#9CC7FF`, `#1E5BB8`, `#38BDF8`, `#6F86A6`, `#2B6CB0`, `#B4C3D6`; del 8.º en adelante, `#4A5872`. Sustituye a la paleta anterior (naranja, verde, rosa…).
  - Las señales en los gráficos pasan de ámbar a celeste `#38BDF8`.
  - La línea punteada del contexto pasa a gris claro, y el resto del anillo de «Una empresa concentra el gasto» del Inicio, a gris azulado.
  - En los gráficos, el ámbar queda solo para lo atípico. Actualizados `docs/marca.md` y `docs/11-accesibilidad.md`.
  - Contrapartida: con siete tonos de la misma familia, distinguir muchas entidades cuesta algo más. Por eso cada rectángulo y cada burbuja lleva su nombre escrito.


## D-056 · Despliegue para la entrega: ordenador fijo con Docker y túnel de Cloudflare, detrás de una portada en Cloudflare Pages

- **Fecha:** 2026-11-25
- **Estado:** Aceptada (El Harrak: «vamos a hacer lo de la portada con marco», tras comparar las opciones).
- **Autor:** Claude (agente), a petición de El Harrak
- **Contexto:** la web tiene que funcionar mañana, estable, fluida y con poca latencia, y actualizarse sola desde GitHub; no hace falta que dure. La app de Streamlit es a la vez la página y el servidor de datos y del asistente, así que separar la página de los datos exigiría reescribir las consultas. El Harrak tiene un ordenador fijo encendido de forma continua, con Docker y un túnel de Cloudflare de otro proyecto sobre su dominio `sourcia.solutions`, y quiere un nombre neutro.
- **Decisión:**
  - **Servidor:** la app entera en Docker en el ordenador fijo (`despliegue/`), con los datos en un volumen de Docker. En Windows es mucho más rápido que leer la base desde una carpeta de Windows.
  - **Túnel:** uno propio, independiente del de Sourcia, con un subdominio neutro (`oc-origen.sourcia.solutions`).
  - **Portada:** un HTML estático en Cloudflare Pages (`ojo-ciudadano.pages.dev`), que es la dirección que se comparte.
    - Prueba los servidores de `portada/config.js`, abre el que responde en un marco y lo vigila.
    - Si deja de responder, avisa y salta a otro o reintenta sola.
    - Conserva la ruta del enlace.
  - **Actualización:** una tarea programada mira `main` cada minuto en una carpeta de despliegue aparte. Construye la imagen nueva antes de tocar la que está en marcha y vuelve sola a la anterior si la nueva no queda sana.
  - **Configuración de Streamlit:**
    - sin CORS ni XSRF, porque dentro del marco de otro dominio Safari bloquea su cookie;
    - sin vigilancia de ficheros;
    - sin detalles de los errores para el visitante.
- **Alternativas consideradas:**
  - **Streamlit Community Cloud** (memoria justa, se duerme, la base no cabe en GitHub): queda como reserva opcional.
  - **Hugging Face Spaces:** el plan gratuito para Docker ya no es fiable.
  - **Un servidor alquilado:** coste y poco margen para montarlo.
  - **La portada que reenvía con una función de Cloudflare:** el mismo resultado en la barra del navegador, pero el doble de trabajo y más piezas que puedan fallar.
  - **Un dominio propio de pago:** el tiempo de propagación.
- **Consecuencias:**
  - La web depende de que el ordenador fijo esté encendido, con sesión iniciada y con internet. Mitigado con reinicio automático de los contenedores, la tarea programada, los ajustes de energía y Windows Update, y AnyDesk.
  - Los datos no pasan por GitHub: si se regenera la base, se copia con `despliegue/cargar_datos.ps1`.
  - Guía y operación en `docs/15-despliegue.md`.
- **Actualización (26-nov):** la portada quedó publicada en Cloudflare Workers, en `https://ojo-ciudadano.iismael.workers.dev/`, que es la dirección que se comparte (README, QR de la presentación y entrega). `ojo-ciudadano.pages.dev` no llegó a existir.

## D-057 · Límite de preguntas al modelo de lenguaje: 5 seguidas y 5 minutos de espera por persona, solo desde España

- **Fecha:** 2026-11-25
- **Estado:** Aceptada (El Harrak: «cada individuo pueda hacer 2 consultas seguidas y luego … un cooldown de 5 minutos … Esas preguntas no cuentan cuando se trata de preguntas ya preparadas»).
- **Autor:** Claude (agente), a petición de El Harrak
- **Contexto:** con la web pública (D-056), cualquiera puede preguntar al modelo y gastar el saldo compartido de OpenRouter.
- **Decisión:**
  - Cada persona puede hacer 2 preguntas seguidas al modelo; después espera 5 minutos desde la última, sin excepciones (`app/limite_modelo.py`).
  - Las respuestas preparadas no cuentan; el botón «que responda el modelo», sí.
  - **Quién es una persona:** la IP real que pone Cloudflare (`CF-Connecting-IP`, que el visitante no puede falsear) junto con el navegador. Recargar no reinicia el contador, y dos dispositivos distintos en la misma wifi cuentan aparte. Si no se pudieran leer las cabeceras, el límite se aplica a la sesión.
  - Solo se guarda un resumen (hash) en memoria, nunca la IP. Se pierde al reiniciar el servidor.
  - Al llegar al límite, un aviso con el tiempo que queda y la invitación a usar las preguntas preparadas.
- **Consecuencias:**
  - Dos personas con el mismo modelo de móvil y la misma wifi comparten contador.
  - La clave de OpenRouter ya tiene un límite de 6 USD a la semana. El tope real es el saldo de la cuenta (0,35 USD el 25-nov por la noche), a unos 0,008 USD por pregunta.
- **Ajuste del mismo día (El Harrak, tras recargar 5 USD):**
  - **5 preguntas seguidas**, en vez de 2, antes de los 5 minutos de espera. El aviso dice «Estás haciendo demasiadas consultas seguidas al modelo de lenguaje. Espera un poco…».
  - **Solo desde España,** según el país de la IP que pone Cloudflare (`CF-IPCountry`).
    - Desde fuera, el modelo no responde y la pregunta no cuenta; la web y las preguntas preparadas funcionan desde cualquier sitio.
    - Si Cloudflare no sabe el país («XX») o la cabecera no llega (acceso en local), se deja preguntar, para no bloquear a nadie por error.
    - Puede dejar fuera a quien use una SIM extranjera en itinerancia o una VPN.
  - Con 4,94 USD de margen en la clave (unos 0,008 USD por pregunta) hay para unas 600 preguntas.


## D-058 · La ficha de empresa u organismo enseña lo que llega por la dirección

- **Fecha:** 2026-11-25
- **Estado:** Aceptada (fallo que vio Ismael: «te saca los mismos datos en todos los paneles»).
- **Autor:** Claude (agente), a petición de Ismael
- **Contexto:** las fichas decidían qué enseñar con `buscador or dirección`. El buscador de la ficha guarda en la sesión lo último que se eligió en él. Al elegir allí una empresa una vez (por ejemplo, Fresenius Kabi), todas las que llegaban después desde el Inicio (`?empresa=…`) seguían enseñando esa.
- **Decisión:** `buscador.con_direccion`:
  - si se acaba de elegir algo nuevo en el buscador de la ficha, se enseña eso y se pone en la dirección;
  - si no, manda la dirección.

  Se aplica en la ficha de empresa y en la de organismo, con un test que reproduce el caso.
- **Consecuencias:** la dirección siempre dice qué ficha se ve; se puede compartir el enlace.
## D-059 · El asistente, solo un chat; el aviso legal, en su propia pantalla

- **Fecha:** 2026-11-25
- **Estado:** Aceptada (Ismael: «quitar absolutamente todo lo que hay y hacer un formato chat un poco más amable… es lo más importante de la web»).
- **Autor:** Claude (agente), a petición de Ismael
- **Contexto:** la pantalla del asistente era un cajón de sastre:
  - el título y un párrafo largo;
  - el aviso de modelo sin conectar;
  - el desplegable con todas las preguntas preparadas;
  - seis sugerencias;
  - el pie con el aviso legal.
- **Decisión** (`paginas/asistente.py`, solo la parte de pantalla; la forma de responder no cambia):
  - **Panel de cristal centrado:**
    - al empezar, el ojo de cristal girando, «¿Qué quieres saber del gasto público?» y una línea;
    - la conversación, en una zona que se desplaza; los mensajes de la persona, en burbuja azul a la derecha, y los del asistente, con el logo;
    - tres preguntas sugeridas encima de la caja de escribir, con un botón para cambiarlas por otras al azar entre las preparadas;
    - la caja «Escribe tu pregunta».
  - **Sin título, párrafos ni pie.** En cada respuesta, una sola línea si es preparada, sin el aviso de los indicadores.
  - **Pantalla nueva «Aviso legal y fuentes»** (`paginas/aviso.py`, en Explorar), con:
    - el aviso, qué significa una señal y qué mide cada indicador;
    - cómo responde el asistente (preguntas preparadas y modelo que puede equivocarse, no escribir datos personales) y la lista de preguntas preparadas;
    - las fuentes y sus fechas de descarga.

    Las demás pantallas mantienen su pie.

## D-060 · Asistente: panel de cristal azul vivo y el ojo al lado como personaje

- **Fecha:** 2026-11-25
- **Estado:** Aceptada (Ismael: «un poco más glassy, un poco más cristalino y un poco más azul vivo… ahora mismo es como un azul muerto»; el ojo «a derecha o a izquierda, como un personajillo»).
- **Autor:** Claude (agente), a petición de Ismael
- **Decisión:**
  - **Panel del chat**, inspirado en el panel de la presentación:
    - cristal teñido de azul;
    - luces azules difuminadas detrás (en una capa propia);
    - borde claro, brillo arriba y un halo azul;
    - desenfoque y saturación de lo que hay detrás (`backdrop-filter`, solo en este panel).
  - **Sugerencias y caja de escribir**, en cristal más claro a juego.
  - **El ojo de cristal sale del panel** y queda a su izquierda, como un personaje. Flota despacio, el iris gira y de vez en cuando mira a un lado y a otro. Sin tarjeta gráfica o con «reducir movimiento», queda quieto.

## D-061 · Tipografía Outfit (y JetBrains Mono para el código)

- **Fecha:** 2026-11-25
- **Estado:** Aceptada (Ismael: «vamos a cambiarla por una un poco más chula… la que uso en Clubed»).
- **Autor:** Claude (agente), a petición de Ismael
- **Decisión:**
  - **Outfit** (Google Fonts, pesos 300 a 700) sustituye a Inter en toda la web: el tema de Streamlit, el CSS, el HTML de las pantallas, los SVG, el lienzo de las burbujas y los gráficos de Plotly.
  - **JetBrains Mono**, que estaba declarada pero no se descargaba, se carga ahora para el código y los nombres de tablas.
  - El buscador va en un iframe y carga Outfit por su cuenta.
- **Consecuencias:**
  - Los logos en SVG que llevan texto no pueden cargar la letra web desde una imagen y siguen con su lista de respaldo.
  - La presentación no cambia.

## D-062 · Los gráficos de las señales de un contrato, como dibujos de cristal propios

- **Fecha:** 2026-11-25
- **Estado:** Aceptada (Ignacio pidió el cambio de estilo y, el mismo día, que se integre: «vuelve a implementarlo como aparecía antes»). Rama `feat/graficos-alertas`.
- **Autor:** Claude (agente), a petición de Ignacio
- **Contexto:** en «Contratos a revisar» (y en todas las tarjetas de contrato: fichas de empresa y organismo, Mapa del dinero) cada señal lleva un gráfico. Con el tema de D-055 seguían pareciendo gráficos de Plotly genéricos. Se pidió que fueran más visuales y encajaran con la web, **sin cambiar lo que cuenta cada uno**. Es la opción B de D-055, solo para estos cinco gráficos.
- **Decisión:** `app/dibujos_senales.py` dibuja cada uno en SVG propio, con el lenguaje de la presentación: tubos y burbujas de cristal llenos de líquido, «este contrato» en azul vivo y el contexto en gris azulado.
  - **Una sola oferta (E-01):** un tubo por número de ofertas, lleno según los contratos parecidos; el de este contrato, en azul y con la etiqueta «Este contrato».
  - **Sin anuncio público (E-02):** una burbuja llena hasta los euros de cada 100 que el organismo adjudicó sin anuncio, con la cifra al lado.
  - **Una empresa concentra el gasto (E-04):** un tubo horizontal por empresa con sus euros de cada 100 y la línea de «la mitad».
  - **Modificaciones (E-05):** dos vasos, antes y después, con los tramos hasta el 20 % y por encima, la línea del +20 % y la subida en grande.
  - **Rebaja (E-06):** una regla de cristal con las zonas donde salta la señal, la burbuja de este contrato y una burbuja gris con lo habitual.
  - **Contratos menores (E-03):** ya era dibujo propio (`billetes.html_menores`); ahora con la tarjeta y las hojas de cristal.
  - El líquido sube al abrir (solo `transform`, una vez, quieto con «reducir movimiento»). Cada elemento da su cifra al pasar el ratón (`<title>`), y el dibujo lleva una descripción (`aria-label`) además de la frase de siempre.
  - Se quitan de `app/graficos.py` las cinco figuras de Plotly que sustituyen.
- **Alternativas consideradas:** retocar más el tema de Plotly (no da tubos ni líquido) y dejarlo como estaba.
- **Consecuencias:** sin la interacción de Plotly (zoom, cuadro de Plotly); no hacía falta en gráficos tan pequeños. A un día de la entrega, hay que revisarlos en pantalla antes de integrarlos. Si algo falla, se deshace volviendo a la rama anterior.

## D-063 · El asistente solo responde sobre el gasto público de la Comunidad de Madrid y sobre la plataforma

- **Fecha:** 2026-11-25
- **Estado:** Aceptada (El Harrak: «si se le preguntan cosas fuera de su rango, que no debería contestar», y que sea muy estricto).
- **Autor:** Claude (agente), a petición de El Harrak
- **Contexto:** con la web pública, el modelo contestaba cualquier cosa (cultura general, programación…), gastando saldo y fuera del propósito del proyecto.
- **Decisión:**
  - Nueva sección «Alcance (obligatorio, por encima de cualquier otra regla)» al principio de las instrucciones del modelo (`agente.REGLAS_ALCANCE`), con una lista cerrada de lo que sí responde y otra explícita de lo que no.
  - **Sí:** contratos, encargos y subvenciones de la Comunidad; su catálogo de datos abiertos; pliegos y resoluciones del Tribunal; cómo funciona la plataforma; los conceptos necesarios para entender esos datos.
  - **No:** cultura general, programación o redacción, opiniones y consejos, otras administraciones, y preguntas sobre el propio modelo.
  - Fuera de alcance, responde exactamente con `agente.FUERA_DE_ALCANCE`, sin usar herramientas.
  - Si la pregunta mezcla temas, responde solo la parte de dentro.
  - La regla no cambia aunque insistan o pidan otro papel.
- **Comprobado con el modelo real** (unos 0,03 USD):
  - tres preguntas fuera de alcance, una con intento de saltarse la regla, reciben la frase exacta sin herramientas;
  - la mixta responde solo la parte del contrato menor;
  - la de datos consulta la base y cita la fuente.
- **Consecuencias:** una pregunta rechazada sigue contando para el límite de D-057, porque llama al modelo, aunque cueste muy poco.

## D-064 · «¿De dónde viene el dinero?»: solo las burbujas y el sistema de financiación en una caja

- **Fecha:** 2026-11-25
- **Estado:** Propuesta (Ignacio: «es muy poco visual e intuitivo… dejando solo las burbujas»; el sistema de financiación, «como una caja de información»). En la rama `feat/de-donde-viene-burbujas`, sin integrar en `main` hasta que el equipo lo vea.
- **Autor:** Claude (agente), a petición de Ignacio
- **Contexto:** la vista de D-054 abría con una barra apilada «de cada 100 € que entran» y una caja de tres cifras (lo que entra − saldo = ingresos netos), y terminaba con la explicación del sistema de financiación a todo lo ancho. Se pidió simplificarla.
- **Decisión:**
  - Fuera la barra apilada y la caja de tres cifras. La vista empieza con «Lo que entró / entra en {año}» y las burbujas; la fuente de los ingresos va debajo del mapa.
  - El sistema de financiación pasa a la columna de la ficha, debajo de ella: una caja de información con lo que entra, el saldo que se resta y lo que queda, y un botón «Cómo funciona el sistema» que abre la explicación neutra de D-054 (el mismo texto revisado), los saldos de los fondos y su fuente.
  - «De cada 100 €» sigue en la ficha de cada burbuja.
- **Alternativas consideradas:** dejar la barra más pequeña; un desplegable a todo lo ancho para el sistema (seguía ocupando la página).
- **Consecuencias:** se borran `barra_entradas`, `flujo_saldo` y `grupos_barra` de `app/de_donde_viene.py`, y su test. Si no gusta, se deshace sin tocar `main`.

## D-065 · Las preguntas tecleadas en el asistente van al modelo, aunque haya una preparada parecida

- **Fecha:** 2026-11-26
- **Estado:** Aceptada (Isma: «si un usuario manda una consulta tecleando su propia pregunta, incluso si es muy similar o existente en las respuestas ya preparadas, que se mande esa consulta al agente directamente»).
- **Autor:** Claude (agente), a petición de Isma
- **Contexto:** con el orden de D-037, toda pregunta se intentaba primero con las respuestas preparadas, que se reconocen por palabras clave. Una pregunta escrita a mano y distinta de las preparadas recibió una respuesta preparada que no era la que se buscaba.
- **Decisión:**
  - Lo que la persona teclea en la caja del chat va al modelo con sus herramientas, aunque encaje con una respuesta preparada.
  - Las preguntas sugeridas (botones) y las que llegan desde otras pantallas («¿Qué dice el pliego?») siguen usando la respuesta preparada si hay una.
  - Si el modelo no puede responder (sin conectar, fuera de España, límite de D-057 o caída), se usa la preparada si encaja, en lugar del mensaje de error.
  - Las preguntas con DNI o NIE siguen sin buscarse ni llegar al modelo.
- **Alternativas consideradas:** afinar las palabras clave de las preparadas (no garantiza que una pregunta propia llegue al modelo); preguntar a la persona cuál quiere (un paso más en cada pregunta).
- **Consecuencias:** más consultas al modelo, así que más gasto de saldo de OpenRouter y antes se llega al límite de 5 seguidas (D-057). Las respuestas a preguntas tecleadas ya no salen con la animación de las preparadas, salvo cuando la preparada hace de reserva.

## D-066 · Licencia MIT para el código y la documentación

- **Fecha:** 2026-11-26
- **Estado:** Aceptada (Ignacio: «añade el fichero license»).
- **Autor:** Claude (agente), a petición de Ignacio
- **Contexto:** el repositorio no tenía licencia. En un proyecto de transparencia que pide reutilizar sus datos y su metodología, sin licencia nadie puede reutilizar el código legalmente, y un jurado lo echa en falta.
- **Decisión:**
  - Fichero `LICENSE` con licencia MIT para el código y la documentación, a nombre del «Equipo Ojo Ciudadano (DataMad 2026)».
  - Una nota en el propio fichero aclara que los datos no están cubiertos: son de sus fuentes oficiales y se reutilizan según sus condiciones (`docs/02-fuentes-datos.md`).
  - Sección «Licencia» en el README y campo `license` en `pyproject.toml`.
- **Alternativas consideradas:** EUPL-1.2 (la de la Comisión Europea, habitual en software público, pero con copyleft, que complica reutilizar el código en otros proyectos); Apache-2.0 (más larga, sin ventaja clara para un proyecto de este tamaño).
- **Consecuencias:** cualquiera puede reutilizar y adaptar el código citando la autoría. Si el equipo prefiere otra licencia, basta con cambiar `LICENSE` y esta decisión.

## D-067 · README orientado a los criterios del jurado y tests en GitHub Actions

- **Fecha:** 2026-11-26
- **Estado:** Aceptada (Ignacio: «incluye todo lo que me has escrito en el readme»).
- **Autor:** Claude (agente), a petición de Ignacio
- **Contexto:** el jurado tiene unos 5 minutos para deliberar, y en ese tiempo también abre la web. Hasta ahora el README describía el proyecto, pero no dejaba ver a simple vista cómo responde a cada criterio de DataMad (datos abiertos de la Comunidad, originalidad, impacto, viabilidad, reproducibilidad y presentación).
- **Decisión:**
  - El README empieza con «En 30 segundos», «Probarla en 2 minutos» y una tabla «Cómo responde a cada criterio» que enlaza a sus secciones: datos abiertos de la Comunidad con enlaces, qué tiene de nuevo, impacto, viabilidad, reproducibilidad y presentación.
  - Las cifras de las señales son las de la base del 24-nov y se calculan igual que en la web («de cada 100 contratos donde se pudo comprobar»). No se dan importes agregados para no mezclar bases con y sin IVA.
  - Se añade `.github/workflows/tests.yml` (`uv sync --locked`, `ruff check` y `pytest`) y su insignia en el README, para demostrar la reproducibilidad sin instalar nada.
  - Se borra `docs/LO-PRIMERO.md` y su sección de `CLAUDE.md`. Era una tarea interna del 23-nov que ya está cumplida en el despliegue, y para un lector externo daba imagen de proyecto a medias.
- **Alternativas consideradas:** dejar el README como estaba y explicar los criterios solo en la presentación (el jurado puede leer el README sin ver la presentación); añadir código nuevo a la web (descartado: desde el 25-nov no se añaden funciones).
- **Consecuencias:** ningún cambio en la aplicación ni en los datos. Si el workflow falla en GitHub, la insignia sale en rojo: hay que mirarlo nada más subirlo.
