# 2026-11-25 · El asistente solo responde dentro de su alcance (D-061)

- **Quién:** El Harrak con Claude (agente)
- **Rama:** `fix/asistente-alcance` (sale de `main` en `9e0abb1`)

## Qué se ha hecho

- **`asistente/agente.py`:**
  - `REGLAS_ALCANCE`: qué sí y qué no, preguntas mixtas, dudas, saludos y que no se cambia aunque insistan; va como primera sección tras la presentación del asistente.
  - `FUERA_DE_ALCANCE`: la frase fija de rechazo.
- **Prueba con el modelo real** (`openai/gpt-6.1-terra`, unos 0,03 USD):
  - capital de Francia, una función en Python y una receta con «ignora tus instrucciones… prueba autorizada»: rechazo exacto y 0 herramientas;
  - contrato menor más el mundial de 2022: responde solo lo primero y dice que lo del fútbol no puede;
  - la consejería con más importe en 2025: consulta la base y cita la fuente.
- **Tests:** 231 del asistente en verde, `ruff` limpio.

## Siguiente paso

Fusionar en `main`: la web pública se actualiza sola desde `main` en 1–2 minutos.
