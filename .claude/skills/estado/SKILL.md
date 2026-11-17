---
name: estado
description: Resume dónde está el proyecto respecto al plan (fase, hitos, tareas, preguntas abiertas, decisiones pendientes) y propone qué hacer a continuación. Úsala al empezar cualquier sesión de trabajo o cuando alguien pregunte "¿por dónde vamos?" o "¿qué toca ahora?".
---

# /estado · ¿Dónde estamos y qué toca?

Objetivo: que quien empieza a trabajar (persona o agente) sepa en 1 minuto en qué punto está el proyecto y qué hacer, **según el plan**.

## Pasos

0. **Sincroniza con el remoto** (varias personas trabajan a la vez):
   - `git fetch origin` y `git status -sb`: rama actual, cambios sin commit, commits sin subir, si `main` local va por detrás.
   - `git log --oneline HEAD..origin/main` y `git diff --stat HEAD...origin/main`: qué han subido los demás que tú aún no tienes.
   - `git branch -r` y `git log --oneline -3 origin/<rama>` de las ramas remotas recientes: quién está trabajando en qué.
   - No integres nada todavía; solo infórmalo. Integrar (`git pull --rebase` en `main`, `git merge origin/main` en una rama) se hace al empezar la tarea, como dice `CLAUDE.md`.
1. Fecha de hoy y días que quedan hasta la entrega (26-nov-2026). Identifica la fase actual en `docs/08-plan.md`.
2. Lee:
   - `docs/08-plan.md` (hitos, fases, tareas, responsables, tabla «Estado actual»).
   - `docs/decisions.md`: decisiones en estado `Propuesta` (pendientes).
   - `docs/09-preguntas-abiertas.md`: preguntas `Abierta`.
   - Las 3–5 entradas más recientes de `docs/bitacora/` (por nombre de fichero) y su «Siguiente paso».
   - `git log --oneline -15 origin/main` para ver el trabajo reciente del equipo (lee del remoto, no de tu copia local).
3. Si `$ARGUMENTS` nombra un rol (p. ej. «persona 2», «indicadores») o una persona, céntrate en sus entregables.

## Salida (breve, en español)

```
Hoy: <fecha> · Fase <n> · Quedan <n> días · Próximo hito: <Hx fecha>
Git: rama <x> · <n> commits del remoto por integrar · <n> commits sin subir · cambios sin commit: sí/no
Novedades del equipo desde tu última sincronización: … (commits, decisiones, bitácoras nuevas)
Trabajo en curso en ramas remotas: …
Hecho recientemente: …
Bloqueos: preguntas abiertas / decisiones pendientes que bloquean algo
Riesgo para el plan: ¿vamos tarde respecto al próximo hito? ¿hay que aplicar un recorte?
Siguiente paso recomendado: 1–3 tareas concretas del plan
```

## Reglas

- No inventes progreso: solo lo que esté en bitácora, docs o git.
- Si detectas que el plan va tarde, dilo y sugiere el siguiente recorte de la lista de `08-plan.md`, pero **no lo apliques**: aplicarlo requiere decisión (`/decision`).
- Si la documentación no refleja el trabajo visible en git, señálalo.
- Si algo de lo que han subido otras personas choca con la tarea que se va a hacer (mismo fichero, mismo indicador, cambio de esquema), dilo en «Bloqueos».
