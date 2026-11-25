# 2026-11-25 · Luz sutil al pasar el ratón por las tarjetas del Inicio

- **Quién:** El Harrak con Claude (agente)
- **Rama:** `feat/puertas-luz` (sale de `main` en `3127340`)

## Qué se ha hecho

- **Tarjetas de «Qué ofrecemos»** (Mapa del dinero, Contratos a revisar, Asistente de IA): al pasar el ratón ya no sale el recuadro de fondo que Streamlit ponía al título. En su lugar entra una luz sutil, como los rayos de la página:
  - unos haces que bajan desde arriba con un halo y se apagan hacia abajo; se funden con la tarjeta y el texto (`mix-blend-mode: screen`) y se mecen despacio mientras el ratón está encima;
  - un destello que cruza la tarjeta una sola vez;
  - el título se ilumina un poco y la frase se aclara.
- **Coste bajo:** son dos pseudoelementos de la propia tarjeta, solo con opacidad y `transform`. No se anima nada si el ratón no está encima. Sin animación con `prefers-reduced-motion` ni en equipos sin tarjeta gráfica (D-044).
- Solo cambia el CSS de `paginas/inicio.py`. Comprobado en el navegador.

## Siguiente paso

Fusionar en `main`: es un retoque visual, no una función nueva.
