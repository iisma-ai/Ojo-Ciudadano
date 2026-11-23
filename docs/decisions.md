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
