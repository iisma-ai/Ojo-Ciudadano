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

## Ajuste: lo atípico en ámbar y menos tirones

- **Ámbar:** lo atípico, en el ámbar de la presentación.
  - En E-07, burbuja ámbar de cristal con un halo, que no se recorta en el borde del gráfico (`cliponaxis=False`).
  - En el histograma, línea y etiqueta en ámbar, a la izquierda de la línea para que no se corte.
  - «Contrato atípico», en naranja en la ficha del Mapa del dinero.
  - La frase de la pantalla de atípicos dice «el punto amarillo».
- **Tirones:**
  - la nube de 1.500 puntos tenía un degradado SVG por punto: ahora, puntos planos por encima de 50;
  - fuera el halo de las barras y la sombra grande del cuadro al pasar el ratón;
  - entrada solo con opacidad.
- **Comprobado en el navegador:** histograma de un atípico real y nube de puntos de prueba con 1.500 puntos.

## Ajuste: abrir un contrato atípico sin esperas

- **Causa:** el desplegable de cada contrato volvía a ejecutar toda la pantalla (filtros, lista y consultas) antes de abrirse, y la nube de 1.500 puntos se dibujaba en SVG.
- **Arreglo:**
  - cada contrato, en su propio `st.fragment`;
  - la frase al momento y, en el sitio del gráfico, el ojo girando (`app/cargando.py`) hasta que el gráfico está listo;
  - la nube con `Scattergl`;
  - transiciones de apertura y de entrada del gráfico.
- **Comprobado en el navegador:** al pulsar sale la frase con el ojo girando y, en uno o dos segundos, el gráfico entra animado (histograma y nube de puntos).

## Ajuste: fichas de empresa y de organismo

- **Mapa de rectángulos de cristal** (`_treemap_de_cristal` en el tema común): opacidad 0,5, borde claro, esquinas de 8 px y 4 px de separación.
- **Tarjetas de contrato en su propio fragmento:** al abrir una, solo se recalcula esa tarjeta, con el ojo girando mientras se calculan las señales. Sirve para la ficha de empresa, la de organismo y «Contratos a revisar».
- **«Contrato atípico»** en ámbar dentro de la tarjeta.
- **Transición** de apertura en todos los desplegables y entrada animada de sus gráficos.
- **Comprobado en el navegador** con la ficha de B. Braun Medical: mapa de rectángulos, contratos por año, señales y una tarjeta abierta con sus dos gráficos.

## Pendiente

- Mirar en la pantalla de la demo el contraste de las barras translúcidas.
- Los puntos-burbuja solo se han comprobado con test, no a la vista: atípicos y asistente.

## Siguiente paso

Que el equipo lo vea y decida si entra en `main`.
