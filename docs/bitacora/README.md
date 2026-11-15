# Bitácora de trabajo

Una entrada por sesión de trabajo (humana o de agente). Es la forma de que la siguiente persona o agente sepa **qué se hizo, qué quedó a medias y qué sigue**.

## Reglas

- Un fichero por sesión: `AAAA-MM-DD-tema-corto.md` (p. ej. `2026-11-16-ingesta-placsp.md`). Ficheros separados para evitar conflictos de merge.
- Se escribe **al terminar** la sesión (skill `/cerrar-sesion`), aunque la sesión haya sido corta o haya fallado algo.
- Se lee **al empezar**: las 3–5 entradas más recientes (skill `/estado`).
- Hechos, no relleno. Si algo falló, se dice con el error.

## Plantilla

```markdown
# AAAA-MM-DD · Tema

- **Autor:** persona / agente (a petición de quién)
- **Fase del plan:** 1 | 2 | 3 | 4 — tarea o entregable del plan al que contribuye

## Qué se hizo
- …

## Decisiones tomadas
- D-xxx (enlace) o «ninguna»

## Desviaciones del plan
- «ninguna» o qué y por qué (con su decisión registrada)

## Problemas y hallazgos
- …

## Siguiente paso
- …
```
