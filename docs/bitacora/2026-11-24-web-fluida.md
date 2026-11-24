# 2026-11-24 · Web fluida y asistente sin SQL a la vista (D-040)

**Quién:** El Harrak, con Claude (agente). **Rama:** `feat/web-fluida`.

## Contexto
Petición:
- quitar el SQL de las respuestas del asistente y enseñar solo lo que sacan las consultas;
- que se vea animado cómo se relacionan las tablas y se recuperan los datos;
- que la salida salga en tabla y en gráfico;
- que la web deje de ir a tirones, porque el scroll molestaba a la vista.

## Diagnóstico
- **Fondo:** las burbujas se animaban con `background-position` (repinta la pantalla entera en cada fotograma) y los rayos llevaban `filter: blur`.
- **Cristal:** más de diez tipos de elementos con `backdrop-filter: blur(18–24px)` sobre ese fondo animado; se recalculaban en cada fotograma y al desplazarse.
- **Consultas:** ninguna pantalla tenía caché, así que cada clic repetía todas sus consultas.

## Qué se hizo
- `static/estilo.css`:
  - fondo solo con `transform` (burbujas en una capa alta que sube; alturas de baldosa que dividen 2.400 px, sin salto);
  - sin `background-attachment: fixed`, sin filtro en los rayos y sin `backdrop-filter`;
  - cristal translúcido algo más opaco.
- `app/cache.py`: caché de una hora para `_filas` (`datos`, `datos_contexto` y, a través de ellos, `datos_flujos` y `datos_mapa`). Fuera de Streamlit (tests) consulta directamente.
- **Asistente:**
  - sin SQL;
  - el proceso de la consulta queda en la respuesta, animado una vez y quieto en el historial;
  - texto que se escribe en 40 trozos como mucho;
  - gráfico y tabla a la vista;
  - CSS de las animaciones una vez por página;
  - caché de los resultados de las preguntas preparadas;
  - índice de empresas por base y no por cursor (antes se rehacía en cada pregunta).

## Comprobaciones
- **Tests:** 447, todos bien.
- `ruff` sin avisos.
- **Navegador:**
  - el proceso, el texto, el gráfico y la tabla se ven sin SQL;
  - scroll a 241 fotogramas por segundo, con el más lento de 4 ms;
  - ningún elemento con `backdrop-filter`.
- **Pantallas sin navegador:** todas sin errores, salvo «Inicio», que suelta no tiene el menú para sus enlaces. Al volver a cargar tardan entre 0,01 y 0,3 s; el mapa general, 1,44 s la primera vez y 0,04 s después.

## Siguiente paso
- Fusionar en `main`.
- Si el equipo echa de menos el esmerilado, se puede probar en la barra lateral con el fondo quieto.
