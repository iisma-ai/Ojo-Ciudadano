# 2026-11-21 · Agente del asistente independiente del proveedor de LLM

- **Autor:** Claude (agente), a petición de Ignacio
- **Fase del plan:** 2–3. Entregable de la persona 4 (asistente): texto a SQL respondiendo a las preguntas de demo, de cara al H3 (24-nov).
- **Rama:** `feat/asistente-agente`

## Qué se hizo
- Ignacio pidió avanzar sin cerrar D-010. Todo lo del asistente que no depende del proveedor está ahora hecho y probado con modelos de guion, sin red.
- `src/ojo_ciudadano/asistente/agente.py`:
  - **Interfaz neutra del modelo**: `Modelo(instrucciones, mensajes) → LlamadaSQL | TextoFinal`, con la herramienta en JSON Schema (`HERRAMIENTA_SQL`). Conectar un proveedor es escribir un adaptador con esa forma y devolverlo en `modelo_configurado()`, que hoy devuelve `None`.
  - **Instrucciones** (`instrucciones(con)`, ~4.300 tokens). Incluyen las reglas de respuesta (lenguaje, D-007, fuente y fecha, alertas explicadas, atípicos, sin sesgo partidista, resistencia a cambiar de papel), las limitaciones de los datos (IVA por fuente, año, P-12, consejerías, alcance), los indicadores, las reglas de SQL, el esquema y los 4 ejemplos de demo. El esquema se lee de la base, y el significado de cada columna sale de los comentarios del DDL de `sql/esquema/`.
  - **Bucle** `responder`: hasta 5 consultas, y los errores del validador vuelven al modelo. Al modelo le llegan como mucho 50 filas, marcadas como datos y sin seudónimos. Admite historial.
  - **Retención**: no se muestra una respuesta con DNI o NIE (en el texto o en los datos), con términos acusatorios fuera de una negación o con cifras sin consulta. Una pregunta con DNI no se envía al modelo.
  - `pasar_bateria`: pasa las 20 preguntas de `bateria.py` y las evalúa.
- `bateria.py`: más términos vigilados (raíces: «fraud», «amañ», «favorec», «ilegal», «a dedo»…), negaciones que se quitan antes de buscar, y DNI/NIE con puntos o guiones.
- Pantalla **«Asistente»** (`app/paginas/asistente.py`): chat con historial y, por cada consulta, sus datos y su SQL. Avisa de que redacta un modelo de lenguaje y de que no se escriban datos personales. Sin modelo, remite a las preguntas guiadas.
- La tabla de resultados pasa a `app/tablas.py`, compartida con «Preguntas guiadas». Las columnas de enlace se titulan «Enlace oficial» (antes «Expediente oficial», que no valía para la BDNS) y «Bases reguladoras».
- **Revisión de `revisor-legal`**: aplicados todos los bloqueantes (B1–B4), los recomendables M1–M8 y los menores L1–L3 y L5. Comprobado con `AppTest` de Streamlit sobre la base real: sin modelo, con modelo de guion y con una respuesta retenida, sin excepciones.
- Tests: `tests/asistente/test_agente.py` y casos nuevos en `test_bateria.py`. La suite completa queda en verde.

## Decisiones tomadas
- Ninguna. D-010 sigue abierta, pero ahora solo decide el adaptador (unas 30 líneas) y la dependencia del proveedor.

## Desviaciones del plan
- Ninguna. No se añade ninguna dependencia de LLM, como pide CLAUDE.md mientras D-010 siga abierta.

## Problemas y hallazgos
- La retención por lenguaje puede dar falsos positivos con usos neutros («favorecer la competencia»). Se aceptó para la demo, porque es mejor retener de más.
- La base local no tiene `anomalia_resultado` hasta ejecutar `uv run python -m ojo_ciudadano.anomalias.deteccion`. Las instrucciones solo describen las tablas que existen.
- Sin modelo real no se sabe aún cuántas preguntas de la batería acierta.

## Siguiente paso
- Cerrar D-010 con el equipo y conseguir la clave. Después: adaptador en `agente.py`, `uv add` del SDK y `pasar_bateria` para anotar los aciertos en docs/05.
- Preparar las respuestas cacheadas de la demo y el vídeo de respaldo (plan de contingencia de docs/05).
