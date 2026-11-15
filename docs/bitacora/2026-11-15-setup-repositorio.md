# 2026-11-15 · Puesta en marcha del repositorio

- **Autor:** Claude (agente), a petición de El Harrak
- **Fase del plan:** 1 · Datos y alcance (preparación previa)

## Qué se hizo
- Entorno Python con **uv** (`pyproject.toml`, `uv.lock`, `.python-version` = 3.12) y dependencias base: duckdb, polars, pyarrow, lxml, httpx, streamlit; dev: pytest, ruff. Paquete vacío `src/ojo_ciudadano/` y un test de humo.
- `.gitignore` con datos, secretos, ajustes locales de Claude y el documento de propuesta original.
- `CLAUDE.md` con las reglas para agentes.
- `.claude/`: ajustes compartidos, skills (`/estado`, `/cerrar-sesion`, `/decision`, `/nueva-fuente`, `/nuevo-indicador`) y subagentes (`revisor-legal`, `explorador-datos`, `guardian-plan`).
- `docs/`: toda la propuesta trasladada a documentos temáticos, plan inicial, registro de decisiones (D-001 a D-011), preguntas abiertas y glosario.
- `README.md` público de presentación.

## Decisiones tomadas
- D-001 a D-007: trasladadas de la propuesta original.
- D-008 (uv, Python 3.12) y D-009 (documentación primero) aceptadas.
- D-010 (proveedor de LLM) y D-011 (convenciones) quedan como **Propuesta**.

## Desviaciones del plan
- Ninguna. No se ha empezado el desarrollo.

## Problemas y hallazgos
- El diagrama de arquitectura y el del plan de trabajo de la propuesta original no se exportaron (aparecen como «embedded content»). La arquitectura se ha redibujado en texto y las fases del plan se han reconstruido a partir de las fechas del documento (ver nota en `08-plan.md`).
- El enlace a Fazekas et al. de la propuesta apuntaba a un proxy universitario; se ha sustituido por el DOI 10.1017/S0007123417000461.

## Siguiente paso
- Tareas del día 1 de `08-plan.md`: resolver P-01 (catálogo), P-02 (nº de licitadores en el CSV), P-03 (licencias) y D-010 (LLM); asignar personas a los roles.
