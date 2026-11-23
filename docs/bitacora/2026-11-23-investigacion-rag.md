# 2026-11-23 · Investigación del RAG: datos nuevos, catálogo y pliegos

- **Autor:** Claude (agente), a petición de El Harrak
- **Fase del plan:** 2. El Harrak pidió no aplicar el recorte 2 sin comprobar antes si el RAG funcionaría y qué aportaría.

## Qué se hizo
- **Enlaces a documentos en el Atom de PLACSP** (enero de 2025): 2.283 de las 2.357 entradas de la Comunidad traen el PCAP y 2.215 el PPT. Todos apuntan a `contratos-publicos.comunidad.madrid`.
- **Prueba de descarga:** 3 pliegos de muestra, sin captcha, de 0,9 a 2,9 MB. Se guardaron en el scratchpad de la sesión, no en el repositorio.
- **Extracción con `pypdf`**, instalado solo para la prueba con `uv run --with`, sin añadirlo al proyecto: 146 páginas y solo 1 sin texto. Los PDF tienen de 15 a 84 páginas, entre 7.600 y 50.000 tokens.
- **Índice BM25 con la extensión `fts` de DuckDB**, con raíces en español: en las 5 preguntas la página buena sale entre las 3 primeras, y en 4 es la primera.
- **Una respuesta de prueba de `gpt-6.1-terra`** con las páginas recuperadas: supuesto del art. 168.a.2 citado con la página. Costó 0,0014 USD.
- **Comprobado además:**
  - las fichas del portal de contratos sin publicidad no enlazan pliegos;
  - OpenRouter no tiene modelos de embeddings;
  - no hay informes de contratación de la Cámara de Cuentas de 2023 a 2026;
  - D-029 (TACPCM), en la rama de otra persona, enlaza resoluciones con contratos.
- Escrito el plan en `docs/14-rag-documental.md`.

## Segunda parte: datos nuevos y catálogo de datos abiertos
El Harrak pidió revisar los datos nuevos de las ramas y centrar el RAG en el catálogo de datos abiertos de la Comunidad.
- **Datos de D-024 cargados en local** con `modelo.contexto`. Coinciden con la referencia del equipo. No he hecho la confirmación de `LO-PRIMERO.md`: queda pendiente de que la pida la persona.
- **Inventario:** D-024 está en `main`; D-027, D-028 y D-029, en `fix/relleno-y-referencia-r01`. Ninguno sube datos a GitHub; se bajan con código.
- **Catálogo CKAN completo** (3 peticiones a `package_search`):
  - 2.276 conjuntos, 2.231 con CSV o JSON y solo 12 con PDF;
  - 2.097 son del Instituto de Estadística;
  - 2.361 recursos tienen `datastore_active`.
- **Su buscador falla** («contratos menores sanidad» devuelve carnicerías). Un BM25 propio sobre los metadatos acierta 6 de 8 preguntas.
- **`datastore_search_sql`** responde, pero da error interno con columnas con tilde.
- **CSV:** mediana de 42 KB y p90 de 1,2 MB.
- **Prueba de punta a punta** con CSV bajo demanda y DuckDB local: listas de espera por hospital en 2025, bien respondida, por 0,0028 USD.
- **Gasto de la investigación** en OpenRouter: unos 0,009 USD, incluido un intento fallido por agotar `max_tokens`. terra razona antes de contestar: no hay que bajar `max_tokens` de unos 2.000.

## Decisiones tomadas
- **D-030, Propuesta, reescrita:** bloque A, el RAG de catálogo, primero; bloque B, los pliegos, solo si A pasa el control del 24-nov a las 12:00. Falta la decisión del equipo.

## Desviaciones del plan
- Ninguna todavía. Si se acepta D-030, el RAG se queda sin embeddings y sin informes de la Cámara de Cuentas, a diferencia de lo previsto en `docs/05`.

## Problemas y hallazgos
- El RAG cubre las licitaciones de PLACSP, no los contratos solo del portal ni los menores. Por ejemplo, en R-02 cubre 3.902 de 11.250 señales.
- La muestra es pequeña (3 PDF): la cobertura y el acierto se confirman en la fase 1 del plan.
- Gasto en OpenRouter: 0,0014 USD.

## Siguiente paso
- **Decisión sobre D-030.** Si es sí:
  - A1–A3 (catálogo) hoy por la tarde y el 24-nov por la mañana;
  - control a las 12:00;
  - B (pliegos) por la tarde, avisando antes a quien lleva la ingesta de PLACSP.
