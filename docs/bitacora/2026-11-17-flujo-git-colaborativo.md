# 2026-11-17 · Flujo de git para trabajo en paralelo

- **Autor:** Claude (agente), a petición de El Harrak
- **Fase del plan:** 1 — organización del equipo (transversal)

## Qué se hizo
- `CLAUDE.md`: nueva regla 0 («Sincroniza antes de nada») y nueva sección «Trabajo en equipo con git». Explica qué hacer al empezar, durante el trabajo y al terminar, qué ficheros suelen chocar y cómo evitarlo, y qué operaciones están prohibidas. La regla 3 incluye ahora subir el trabajo, y se añade una convención de mensajes de commit.
- `/estado`: empieza con `git fetch` y explica qué han subido los demás y quién trabaja en qué rama.
- `/cerrar-sesion`: antes, la skill no hacía commit ni push; ahora hace commit y push de la rama de la tarea (nunca de `main`) y da el enlace del PR.
- `guardian-plan`: comprueba también si la rama está al día con `origin/main`, si hay commits sin subir y si se repiten números D-xxx o P-xx.
- D-011 ampliada con el flujo de git.

## Decisiones tomadas
- Ampliación de [D-011](../decisions.md#d-011--convenciones-de-código-y-colaboración).

## Desviaciones del plan
- Ninguna.

## Problemas y hallazgos
- Si una rama se crea con `git switch -c <rama> origin/main`, por defecto sigue a `origin/main`, y un `git push` a secas subiría a `main`. Por eso las instrucciones usan `--no-track` y nombran siempre la rama en el push.
- No está instalado `gh`: los PR se abren con el enlace `compare` de GitHub.
- Intenté añadir a `.claude/settings.json` permisos sin pregunta para `git fetch`, `git commit` y `git push` a ramas de tarea, y prohibir `git reset --hard` y `git clean`. El clasificador de permisos de Claude Code lo denegó y no está hecho. Si el equipo lo quiere, tiene que hacerlo una persona.

## Siguiente paso
- Que el resto del equipo haga pull de `main` cuando se integre el PR, para que sus agentes usen las nuevas instrucciones.
