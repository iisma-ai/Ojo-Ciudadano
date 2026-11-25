# 2026-11-25 · Gráficos de Plotly con estilo acuático (D-055)

- **Quién:** El Harrak con Claude (agente)
- **Rama:** `feat/graficos-acuaticos` (sale de `main` en `3127340`)

## Qué se ha hecho

- **Valoración previa:** unos 20 gráficos de Plotly en 8 pantallas, todos con el tema común `_tema`. Se valoraron tres caminos:
  - **A:** cambiar el tema, 4–8 h;
  - **B:** rehacerlos con dibujo propio, 6–10 días;
  - **C:** mixto.
  Se eligió A.
- **`app/graficos.py`:** `_tema` aplica a todos:
  - rejilla casi invisible;
  - barras de cristal (opacidad 0,72, borde claro y esquinas de 6 px);
  - puntos como burbujas (degradado radial);
  - cuadro al pasar el ratón con letra Inter de 14 px, sin cortar nombres y alineado a la izquierda.
- **`estilo.css`:**
  - cuadro al pasar el ratón como una burbuja, con más margen, esquinas redondeadas, borde de luz y sombra;
  - halo suave del grupo de barras (sin él en equipos sin tarjeta gráfica);
  - entrada suave de cada gráfico.
- **Tests:** `tests/app/test_graficos_acuaticos.py` (2). Total: 478 en verde, `ruff` limpio.
- **Comprobado en el navegador** en «Presupuesto y contexto»: barras horizontales, barras apiladas y cuadro al pasar el ratón.

## Pendiente

- Mirar en la pantalla de la demo el contraste de las barras translúcidas.
- Los puntos-burbuja solo se han comprobado con test, no a la vista: atípicos y asistente.

## Siguiente paso

Que el equipo lo vea y decida si entra en `main`.
