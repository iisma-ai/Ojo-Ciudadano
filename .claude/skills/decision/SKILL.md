---
name: decision
description: Registra una decisión del proyecto en docs/decisions.md con el formato del equipo (contexto, decisión, alternativas, consecuencias) y propaga sus efectos al plan y demás docs. Úsala cuando se elija una tecnología, se cambie un umbral o definición de indicador, se aplique un recorte, se cambie el esquema o haya cualquier desviación del plan.
argument-hint: "<resumen de la decisión>"
---

# /decision · Registrar una decisión

## Pasos

1. Lee `docs/decisions.md` entero. Comprueba si ya existe una decisión sobre el tema:
   - Si existe y la nueva la contradice, la nueva **sustituye** a la antigua: marca la antigua como `Sustituida por D-xxx` (solo cambia su línea de estado; no reescribas su contenido).
   - Si es la misma decisión, no dupliques: actualiza la existente solo si estaba en `Propuesta`.
2. Asigna el siguiente número libre (`D-012`, `D-013`…) y añade la entrada **al final** con la plantilla del fichero:
   Fecha · Estado · Autor · Contexto · Decisión · Alternativas consideradas · Consecuencias.
3. Estado:
   - `Aceptada` solo si la persona del equipo lo ha decidido explícitamente en la conversación.
   - En otro caso, `Propuesta`, y avisa a la persona de que debe validarla.
4. **Propaga** las consecuencias: actualiza `docs/08-plan.md` (alcance, recortes, fechas, responsables), y los documentos temáticos afectados (`02`–`07`). Si resuelve una pregunta de `docs/09-preguntas-abiertas.md`, márcala como resuelta.
5. Si la decisión cambia algo de `CLAUDE.md` (stack, comandos, reglas, alcance), actualízalo también.
6. Resume a la persona: número de decisión, estado y documentos tocados.

## Reglas

- Una decisión = una entrada. Breve y concreta.
- Nunca borres decisiones antiguas.
- `$ARGUMENTS` es el resumen de la decisión; si falta contexto o alternativas, pregunta lo imprescindible.
