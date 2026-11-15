---
name: estado
description: Resume dónde está el proyecto respecto al plan (fase, hitos, tareas, preguntas abiertas, decisiones pendientes) y propone qué hacer a continuación. Úsala al empezar cualquier sesión de trabajo o cuando alguien pregunte "¿por dónde vamos?" o "¿qué toca ahora?".
---

# /estado · ¿Dónde estamos y qué toca?

Objetivo: que quien empieza a trabajar (persona o agente) sepa en 1 minuto en qué punto está el proyecto y qué hacer, **según el plan**.

## Pasos

1. Fecha de hoy y días que quedan hasta la entrega (26-nov-2026). Identifica la fase actual en `docs/08-plan.md`.
2. Lee:
   - `docs/08-plan.md` (hitos, fases, tareas, responsables, tabla «Estado actual»).
   - `docs/decisions.md`: decisiones en estado `Propuesta` (pendientes).
   - `docs/09-preguntas-abiertas.md`: preguntas `Abierta`.
   - Las 3–5 entradas más recientes de `docs/bitacora/` (por nombre de fichero) y su «Siguiente paso».
   - `git log --oneline -15` y `git status` para ver trabajo reciente o sin commitear.
3. Si `$ARGUMENTS` nombra un rol (p. ej. «persona 2», «indicadores») o una persona, céntrate en sus entregables.

## Salida (breve, en español)

```
Hoy: <fecha> · Fase <n> · Quedan <n> días · Próximo hito: <Hx fecha>
Hecho recientemente: …
Bloqueos: preguntas abiertas / decisiones pendientes que bloquean algo
Riesgo para el plan: ¿vamos tarde respecto al próximo hito? ¿hay que aplicar un recorte?
Siguiente paso recomendado: 1–3 tareas concretas del plan
```

## Reglas

- No inventes progreso: solo lo que esté en bitácora, docs o git.
- Si detectas que el plan va tarde, dilo y sugiere el siguiente recorte de la lista de `08-plan.md`, pero **no lo apliques**: aplicarlo requiere decisión (`/decision`).
- Si la documentación no refleja el trabajo visible en git, señálalo.
