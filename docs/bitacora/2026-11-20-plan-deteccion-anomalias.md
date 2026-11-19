# 2026-11-20 · Detección de anomalías añadida al plan

- **Autor:** Claude (agente), a petición de El Harrak
- **Fase del plan:** 2 — cambio de alcance

## Qué se hizo
- Registrada [D-021](../decisions.md): detección de anomalías con aprendizaje automático, no supervisada por defecto (clustering o Isolation Forest). Supervisada solo si hay etiquetas legítimas, nunca de «corrupción» (D-002). Se muestra como señal complementaria, fuera de la puntuación hasta validarla.
- Propagada a:
  - `docs/08-plan.md`: nueva fila de responsable, entregable para el 23-nov y primer puesto en la lista de recortes.
  - `docs/04-indicadores-riesgo.md`: nueva sección.
  - `docs/06-arquitectura.md`: carpeta `anomalias/`.
  - `CLAUDE.md`: alcance y orden de recortes.
- Origen: la respuesta para el formulario de DataMad menciona «modelos de aprendizaje automático que detectan anomalías», y El Harrak pidió incluirlo en el plan.

## Decisiones tomadas
- D-021.

## Desviaciones del plan
- Amplía el alcance; registrado en D-021. Es el primer recorte si vamos tarde.

## Problemas y hallazgos
- El aprendizaje supervisado choca con D-002: no hay etiquetas fiables. Por eso el método por defecto es no supervisado.

## Siguiente paso
- Asignar responsable.
- Implementarlo entre el 21 y el 23 de noviembre: `uv add scikit-learn`, `src/ojo_ciudadano/anomalias/`, tabla `anomalia_resultado` y test con datos sintéticos.
- Pasar los textos por `revisor-legal`.
