---
name: nuevo-indicador
description: Implementa un indicador de riesgo de contratación (R-01 licitador único, R-02 sin publicidad, R-03 fraccionamiento, R-04 concentración/HHI, R-05 sobrecoste, R-06 baja anormal, R-07 plazo corto, R-08 opacidad) como SQL versionado con test y documentación. Úsala al crear o modificar cualquier indicador o la puntuación de riesgo.
argument-hint: "<R-xx>"
---

# /nuevo-indicador · Implementar un indicador de riesgo

Antes de empezar, lee `docs/04-indicadores-riesgo.md` entero y las decisiones D-002 y D-004.

## Reglas de metodología (no negociables sin decisión)

- La definición operativa es la de `docs/04-indicadores-riesgo.md`. Si necesitas cambiar umbral o definición → `/decision` primero.
- **Comparación entre pares**: contra contratos del mismo tipo y CPV, no contra el total.
- **Aplicabilidad**: si faltan datos o el indicador no aplica al procedimiento, el resultado es `NULL` (no aplicable), **nunca** `false`. La puntuación es la proporción de indicadores *aplicables* activados (0–1).
- **Explicabilidad**: el resultado incluye el valor que disparó la alerta y el motivo en texto, en lenguaje no acusatorio («licitador único en procedimiento abierto», no «adjudicación sospechosa»).
- Excluye causas legales conocidas (exclusividad técnica, emergencias justificadas) cuando los datos lo permitan.

## Pasos

1. Fichero `sql/indicadores/rXX_nombre_corto.sql`, con cabecera de comentario: ID, nombre, definición, datos necesarios, limitaciones, decisión que lo respalda.
   - Salida mínima por contrato: `contrato_id`, `indicador` ('R-xx'), `aplicable` (bool), `activado` (bool o NULL), `valor`, `motivo`, `url_origen`.
2. Test en `tests/indicadores/test_rXX.py` con una base DuckDB **en memoria** y filas sintéticas que cubran: caso que activa, caso que no activa, caso no aplicable, caso límite del umbral.
3. Si hace falta, registra el indicador en el ejecutor de `src/ojo_ciudadano/indicadores/`.
4. `uv run pytest` y `uv run ruff check .` en verde.
5. **Documenta**: tabla «Estado de implementación» de `docs/04-indicadores-riesgo.md` (estado, fichero, notas y cifras reales si ya se ha ejecutado: nº de contratos aplicables y activados). Si los resultados son sorprendentes (p. ej. 90 % activados), anótalo como hallazgo y revisa falsos positivos (K-11).
6. Opcional: pasa el texto de `motivo` por el agente `revisor-legal`.
7. Termina con `/cerrar-sesion`.
