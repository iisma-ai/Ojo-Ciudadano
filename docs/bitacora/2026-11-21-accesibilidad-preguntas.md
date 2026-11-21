# 2026-11-21 · Respuestas con gráfico (D-023, A-08)

- **Autor:** Claude (agente)
- **Fase del plan:** 2. Tarea A-08 de `docs/11-accesibilidad.md`.
- **Rama:** `feat/accesibilidad-preguntas`

## Qué se hizo
- `graficos.automatico`: elige un gráfico para el resultado de cualquier consulta (por año o ranking) y genera una frase resumen. Criterios en `docs/11`.
- `paginas/preguntas.py`: frase y gráfico encima de la tabla; la tabla, con sus enlaces, sigue siempre visible.
- Probado con las 4 preguntas de demo y con tests sintéticos (nombres repetidos por fuente, recuentos por año, resultado vacío).

## Decisiones tomadas
- Ninguna nueva.

## Siguiente paso
- Conectar `graficos.automatico` en la pantalla del asistente. Hay que coordinarlo con su responsable para no pisar su trabajo.
