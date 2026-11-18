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
- **Estado:** Propuesta (aplazada: El Harrak indicó el 2026-11-16 que el LLM se decide más adelante; no bloquea ingesta, esquema ni indicadores)
- **Autor:** Claude (agente)
- **Contexto:** La propuesta dice «LLM por API con llamada a herramientas» y «LanceDB o Chroma», sin concretar.
- **Decisión:** _Por decidir el día 1._ Criterios: soporte sólido de *tool calling*, calidad en texto a SQL en español, coste para la demo, disponibilidad de un modelo alternativo como respaldo (K-14).
- **Alternativas consideradas:** —
- **Consecuencias:** Bloquea las dependencias del asistente y el trabajo de la persona 4 (P-04).

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
