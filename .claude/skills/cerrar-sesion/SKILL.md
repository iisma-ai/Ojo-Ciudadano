---
name: cerrar-sesion
description: Cierra una sesión de trabajo documentándolo todo - escribe la entrada de bitácora en docs/bitacora/, actualiza los documentos de docs/ afectados (plan, indicadores, fuentes, preguntas abiertas) y comprueba que nada queda sin registrar. Úsala SIEMPRE al terminar una tarea o sesión, antes de hacer commit.
---

# /cerrar-sesion · Documentar lo hecho

En este proyecto **se documenta todo lo que se hace**. Esta skill garantiza que la siguiente persona o agente pueda continuar sin preguntar.

## Pasos

1. Reconstruye qué se ha hecho en la sesión: conversación, `git status`, `git diff --stat` y commits de hoy.
2. **Bitácora.** Crea `docs/bitacora/AAAA-MM-DD-tema-corto.md` con la plantilla de `docs/bitacora/README.md`:
   - Autor (persona o agente, y a petición de quién) y fase/entregable del plan.
   - Qué se hizo · Decisiones tomadas · Desviaciones del plan · Problemas y hallazgos (con errores reales) · Siguiente paso.
   - Si ya existe una entrada de hoy sobre el mismo tema, amplíala en vez de crear otra.
3. **Documentos afectados.** Actualiza los que correspondan:
   | Si la sesión… | Actualiza |
   | --- | --- |
   | Exploró o incorporó una fuente | `docs/02-fuentes-datos.md` |
   | Implementó/cambió un indicador | Tabla «Estado de implementación» de `docs/04-indicadores-riesgo.md` |
   | Tocó el asistente | `docs/05-asistente.md` |
   | Creó carpetas, módulos o cambió el esquema | `docs/06-arquitectura.md` |
   | Resolvió una pregunta | `docs/09-preguntas-abiertas.md` (respuesta + fuente + fecha) |
   | Avanzó un hito o tarea | Checklist y tabla «Estado actual» de `docs/08-plan.md` |
   | Tomó una decisión o se desvió del plan | `docs/decisions.md` (usa `/decision`) |
   | Descubrió un riesgo nuevo | `docs/07-riesgos.md` |
4. **Comprobación final.** Lista a la persona: ficheros de docs tocados, decisiones nuevas, preguntas que siguen abiertas. Si hubo una desviación del plan sin decisión registrada, **regístrala antes de terminar**.
5. Sugiere un mensaje de commit en español (sin co-autor de Claude). No hagas commit ni push salvo que te lo pidan.

## Reglas

- Hechos, no relleno. Si algo falló o quedó a medias, se dice.
- No borres entradas antiguas de la bitácora ni decisiones.
