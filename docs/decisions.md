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
- **Estado:** Propuesta (pendiente de decidir por el equipo)
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
- **Alternativas consideradas:** Todo en inglés (alejaría el código del dominio y del jurado).
- **Consecuencias:** Recogido en `CLAUDE.md`.
