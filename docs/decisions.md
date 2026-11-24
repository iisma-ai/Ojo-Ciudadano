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
- **Consecuencias:** Nuevo [12-datos-cm.md](12-datos-cm.md). Pantalla «Presupuesto y contexto», bloque de presupuesto en la ficha de órgano, registros en la ficha de empresa y tablas nuevas en el asistente. Pie de la interfaz con las dos fuentes nuevas. [02-fuentes-datos.md](02-fuentes-datos.md) y el plan actualizados. **Todo el equipo debe bajar los datos antes de seguir** ([LO-PRIMERO.md](LO-PRIMERO.md)).

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

- **Fecha:** 2026-11-23 · **Estado:** aceptada (prueba de concepto revisada por Lucas)
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

## D-038 · Web fluida y asistente sin SQL a la vista
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
