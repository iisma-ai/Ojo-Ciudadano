# 2026-11-23 · RAG de catálogo (D-030, bloque A)

- **Autor:** Claude (agente), a petición de El Harrak («empieza el bloque A del catálogo»)
- **Fase del plan:** 2, víspera del H3 (24-nov)

## Qué se hizo
- **`asistente/catalogo.py`:**
  - descarga de los metadatos del catálogo (3 peticiones a `package_search`, caché en `data/raw/catalogo/paquetes.json`);
  - índice BM25 en memoria (2.228 conjuntos con CSV, 2,2 s), con búsqueda de palabras en común como respaldo;
  - consulta del CSV de un conjunto en una base en memoria que se cierra a ficheros antes de ejecutar el SQL del modelo.
- **`sql_seguro`:** lista de tablas permitidas configurable.
- **Agente:**
  - herramientas `buscar_conjunto` y `consultar_conjunto`;
  - formato neutro de la llamada con `herramienta` y `argumentos`, compatible con el anterior;
  - reglas del catálogo;
  - la regla de cifras admite las dos herramientas;
  - 8 llamadas como máximo.
- **`openrouter.py`:** las tres herramientas y su traducción.
- **Pantalla «Asistente»:** bloque de cada consulta al catálogo con el conjunto, su enlace, la fecha, el aviso municipal, los datos y el SQL.
- **Batería:** de 20 a 24 preguntas (B-21 a B-24, de catálogo), evaluadas por conjunto usado (`bateria.evaluar_respuesta`).
- **Tests:** de 265 a 277, más los del catálogo. Ruff limpio.
- **Validación con `gpt-6.1-terra`:** 4 de 4 preguntas de catálogo bien tras un arreglo, y B-05 y B-17 sin cambios. Coste: 0,077 USD.

## Decisiones tomadas
- **D-030:** el bloque A, aceptado e implementado. El bloque B sigue en Propuesta.

## Desviaciones del plan
- **Sin tabla `catalogo_conjunto`:** el índice va en memoria y los metadatos en caché JSON. Así no hay cambio de esquema ni se toca `modelo/carga.py`. Registrado en D-030.

## Problemas y hallazgos
- **B-21 tenía las cifras y no las daba:** la regla de respuesta solo admitía cifras de `consultar_sql`. Está corregido.
- **B-22 usó otro conjunto oficial equivalente** (personal por área de actividad): se admite como válido.
- **B-01**, pregunta de demo sin relación con el catálogo, ha fallado en esta pasada. Es variación del modelo en la ventana de fechas; hay que vigilarla en el ensayo.
- **La extensión `fts` de DuckDB** se descarga la primera vez que se usa. Sin red, la búsqueda pasa al respaldo.
- **Gasto total de la clave:** 0,551 USD; quedan unos 0,85 de saldo.

## Siguiente paso
- **Fusionar en `main`,** en este orden: `feat/asistente-openrouter` y después `feat/rag-catalogo`, que va encima.
- **En cada instalación,** bajar el catálogo con `uv run python -m ojo_ciudadano.asistente.catalogo`.
- **Decidir el bloque B** (pliegos).
- **Ensayar las preguntas de catálogo en la demo** y precargar sus CSV, que quedan en caché al hacer la pregunta una vez.
