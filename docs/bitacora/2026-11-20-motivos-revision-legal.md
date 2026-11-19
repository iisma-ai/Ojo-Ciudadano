# 2026-11-20 · Motivos de R-02, R-03 y R-05 tras la revisión legal

- **Autor:** Claude (agente), a petición de El Harrak
- **Fase del plan:** 2 — indicadores de riesgo (textos que ve el usuario)

## Qué se hizo
- Al hacer `git pull` aparecieron las ramas de Ignacio Vallejo. Las tres de la interfaz y `feat/indicadores-r04-r06` se apilan sobre `feat/indicadores-r01-r03-r05`, y `docs/cierre-h1` parte de `main`. Traen D-017 a D-020: esquema congelado, R-04, R-06, puntuación e interfaz. Comprobado que no tocan los SQL de R-01, R-02, R-03 y R-05 y que renumeraron sus decisiones para no chocar con D-015 y D-016.
- La revisión legal (bitácora `2026-11-19-mapa-dinero-y-revision-legal.md`) dejó pendiente matizar tres motivos. Aplicado en los SQL y en sus tests:
  - **R-02:** la ley permite el negociado sin publicidad en supuestos concretos y los datos no dicen cuál se alegó. En «otro procedimiento», las emergencias aparecen entre otras tramitaciones y los datos no dicen si el contrato lo es.
  - **R-03:** el motivo empieza por «Posible fraccionamiento» y añade «Es una señal para revisar, no una prueba: pueden ser necesidades distintas».
  - **R-05:** superar el 20 % no implica por sí solo un incumplimiento, porque la ley admite otras modificaciones justificadas.
- La rama `fix/motivos-revision-legal` parte de `feat/app-mapa-dinero`, la última de la pila, para no crear conflictos.
- Pasan 91 tests y `ruff` no da avisos. Regenerados indicadores y puntuación sobre la base real; las cifras no cambian (solo cambia el texto).

## Decisiones tomadas
- Ninguna: solo cambia la redacción, no la definición.

## Desviaciones del plan
- Ninguna.

## Problemas y hallazgos
- `main` sigue en `d6b7a42`: todo el trabajo del 18 y 19 de noviembre está en ramas apiladas sin integrar. Cuanto más tarde se integre, más difícil será.

## Siguiente paso
- Integrar la pila en `main`. Integrando esta rama entran todas las de debajo.
- El resto de pendientes de la revisión legal no son de indicadores: excluir NIF con formato DNI/NIE en búsquedas y listados, fecha de descarga por fuente y licencias (P-03).
