---
name: nueva-fuente
description: Explora e incorpora una fuente de datos (Portal de Contratación CM, PLACSP, BDNS, Catálogo CKAN, Portal de Transparencia...) al pipeline de ingesta - inspecciona campos reales, escribe el módulo de descarga con caché, lo mapea al esquema unificado y lo documenta en docs/02-fuentes-datos.md. Úsala al empezar a trabajar con cualquier fuente.
argument-hint: "<fuente, p. ej. F-02 PLACSP>"
---

# /nueva-fuente · Incorporar una fuente de datos

Antes de empezar, lee `docs/02-fuentes-datos.md`, `docs/06-arquitectura.md` (modelo de datos) y las decisiones D-001, D-003, D-006 y D-007 de `docs/decisions.md`.

## 1. Explorar (sin escribir pipeline todavía)

- Localiza el punto de acceso oficial (CSV, Atom, API, CKAN). Puedes delegar en el agente `explorador-datos`.
- Descarga una **muestra pequeña** a `data/raw/<fuente>/` (nunca al repo).
- Documenta: campos reales y su significado, cobertura temporal, volumen, identificadores (expediente, código de órgano, NIF), si trae **nº de ofertas** (P-02), licencia y condiciones de reutilización (P-03), rarezas.

## 2. Implementar la ingesta

- Módulo en `src/ojo_ciudadano/ingesta/<fuente>.py`:
  - Descarga reproducible con `httpx`, caché en `data/raw/<fuente>/`, troceo por meses si el volumen lo exige, sin peticiones masivas en paralelo.
  - Lectura con polars (lxml para XML/Atom).
  - Añade siempre `fuente`, `url_origen` y `fecha_descarga` a cada fila.
- Mapeo al esquema unificado (`sql/esquema/`). Si el esquema ya está congelado (después del 17-nov, H1) y no encaja, **no lo cambies**: propón decisión con `/decision`.
- Normalización compartida (NIF, UTE, deduplicación) en `src/ojo_ciudadano/normalizacion/`, no dentro del módulo de la fuente.
- Personas físicas: seudonimiza o agrega (D-007).

## 3. Probar

- Test en `tests/` con un **fichero de muestra sintético y pequeño** (no datos reales descargados) que cubra el parseo y el mapeo.
- `uv run pytest` y `uv run ruff check .` en verde.

## 4. Documentar (obligatorio)

- Actualiza la fila de la fuente en `docs/02-fuentes-datos.md` y añade una sección «F-xx · detalle» con campos, cobertura, cómo se descarga y problemas.
- Resuelve en `docs/09-preguntas-abiertas.md` las preguntas que hayas contestado (con fuente y fecha).
- Termina con `/cerrar-sesion`.
