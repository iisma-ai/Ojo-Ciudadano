# 2026-11-23 · Investigación del RAG documental

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

## Decisiones tomadas
- **D-030, Propuesta:** RAG acotado a los pliegos de PLACSP bajo demanda, con BM25 y sin embeddings. Falta la decisión del equipo.

## Desviaciones del plan
- Ninguna todavía. Si se acepta D-030, el RAG se queda sin embeddings y sin informes de la Cámara de Cuentas, a diferencia de lo previsto en `docs/05`.

## Problemas y hallazgos
- El RAG cubre las licitaciones de PLACSP, no los contratos solo del portal ni los menores. Por ejemplo, en R-02 cubre 3.902 de 11.250 señales.
- La muestra es pequeña (3 PDF): la cobertura y el acierto se confirman en la fase 1 del plan.
- Gasto en OpenRouter: 0,0014 USD.

## Siguiente paso
- **Decisión sobre D-030.** Si es sí:
  - fase 1, enlaces en la ingesta de PLACSP; avisar antes a quien la lleva;
  - fases 2 y 3 el 24-nov por la mañana;
  - punto de control a las 14:00.
