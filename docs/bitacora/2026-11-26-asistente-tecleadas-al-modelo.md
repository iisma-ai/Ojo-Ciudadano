# 2026-11-26 · Asistente: las preguntas tecleadas van al modelo (D-065)

## Qué se ha hecho

- **Problema** (lo vio Isma): una pregunta escrita a mano, que no estaba entre las preparadas, recibió una
  respuesta preparada, porque las preparadas se reconocen por palabras clave y se probaban siempre primero (D-037).
- **Cambio** en `app/paginas/asistente.py` (`contestar`, nuevo parámetro `preferir_modelo`):
  - lo que llega por la caja del chat (`st.chat_input`) va al modelo aunque encaje con una preparada;
  - las sugeridas (botones) y las que llegan desde otras pantallas siguen con la preparada;
  - si el modelo no puede responder (sin conectar, fuera de España, límite de D-057 o `MODELO_CAIDO`), se usa la
    preparada si encaja, en lugar del mensaje de error;
  - el filtro de DNI/NIE no cambia.
- Decisión D-065 en `docs/decisions.md`; orden de respuesta actualizado en `docs/05-asistente.md`; fila en el plan.
- Directo en `main`, a petición de Isma. Tests y ruff en verde. No se ha probado contra el modelo real (gasta saldo).

## Pendiente

- Vigilar el saldo de OpenRouter: ahora llegan más preguntas al modelo.
