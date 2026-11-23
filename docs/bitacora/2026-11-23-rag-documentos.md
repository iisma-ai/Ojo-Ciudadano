# 2026-11-23 · RAG documental: pliegos y resoluciones del Tribunal (D-030, bloques B y C)

**Quién:** El Harrak, con Claude (agente). **Rama:** `feat/rag-documentos`.

## Qué se pidió
«Realiza los bloques B y C en su integridad. Y asegúrate de que no rompas nada y que todos esos tests con datos anteriores sigan funcionando igual de bien.»

## Qué se hizo
- **Bloque B, pliegos de PLACSP:**
  - `ingesta/placsp.py` lee de cada licitación los enlaces al PCAP y al PPT y los guarda en `contrato_documento`. Es esquema aditivo (`007_documentos.sql`) y la tabla `contrato` no cambia.
  - `ingesta/documentos.py` baja los PDF con caché y saca el texto por páginas.
  - Herramienta `buscar_en_documento`.
  - Botón «¿Qué dice el pliego?» en las fichas de contrato.
- **Bloque C, resoluciones del TACPCM:**
  - `tacp --pdf` baja los 1.092 PDF.
  - Con el encabezamiento de cada PDF, las resoluciones enlazadas con su contrato pasan de 6 a 396.
  - El texto queda en la tabla derivada `resolucion_pagina`, con BM25.
  - Herramienta `buscar_resoluciones`.
- **Protección de datos (D-032, propuesta):**
  - se tapan DNI, NIE, nombres con tratamiento, también «don» y «doña» en minúscula, y firmas;
  - las páginas «en nombre propio» no se muestran;
  - se rechazan las búsquedas por persona;
  - las cifras se comprueban contra los extractos.
- **Batería:** B-31 a B-34. Se actualizaron los tests que cuentan preguntas (30 → 34) y herramientas (4 → 6).
- **Dependencia nueva:** `pypdf` (`uv add pypdf`), para extraer el texto de los PDF. Es ligera y sin dependencias nativas; la investigación del bloque B ya la había elegido.

## Comprobaciones
- **Tests:** 343, todos bien; había 316 al empezar. Los 316 anteriores siguen pasando y solo cambian las dos cuentas de arriba. `ruff` sin avisos.
- **Base regenerada** con carga, ejecutor, anomalías, texto y documentos. Los indicadores salen con los mismos recuentos que antes: R-01 8.144, R-02 11.250, R-05 573 y R-06 2.226.
- **Batería completa con `gpt-6.1-terra`** (34 preguntas, 0,297 USD):
  - B-31 a B-34 bien;
  - B-01 a B-30 responden como en la pasada de las 14:11 (revisadas a mano B-07, B-11 y B-30, con el desglose distinto);
  - 0 retenidas y 0 errores de API.
- **Web** (AppTest con la base real): alertas, atípicos y empresa sin excepciones. Una ficha abierta muestra los pliegos y el botón.
- **Revisión a mano** de 20 resoluciones enlazadas por título: las 20 cuadran.

## Revisión legal
`revisor-legal` encontró 2 puntos altos (nombres en los extractos y enlace por título), 3 medios y 5 bajos. Todos están aplicados; el detalle está en [14](../14-rag-documental.md).

## Gasto de la clave
0,297 USD en esta sesión. En total, unos 0,97 de los 1,4 previstos.

## Siguiente paso
- Validar D-032 en equipo.
- Fusionar `feat/rag-documentos`.
- Avisar a quien lleva la ingesta de PLACSP de que `leer_zips` devuelve también `documentos`.
- En cada instalación: `uv run python -m ojo_ciudadano.ingesta.tacp --pdf`, regenerar la base y `uv run python -m ojo_ciudadano.asistente.documentos --precargar`.
