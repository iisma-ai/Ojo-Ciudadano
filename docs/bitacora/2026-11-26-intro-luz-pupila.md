# 2026-11-26 · Entrada de la web: la luz sale de la pupila y la página se aclara desde el centro

## Qué se ha hecho

- **Rayos desde la pupila** (`app/intro3d.py`, a petición de Isma). Antes el cono y los haces estaban detrás del ojo,
  en su centro, y los haces eran anchos desde la raíz: asomaban por el contorno del cristal y parecían salir de los
  bordes. Ahora:
  - cono y haces tienen la raíz en la pupila (punto (0, 0, 0,44) del globo de `presentacion/ojo3d.js`, que no se
    toca) y apuntan hacia donde mira el ojo;
  - los haces son cuñas: casi sin anchura en la raíz (`VS_CUNA`) y abiertos lejos del ojo;
  - se pintan después del ojo, así que se ven nacer en el centro del iris;
  - un brillo pequeño en la pupila; el halo de detrás se queda, así que el ojo entero se sigue viendo luminoso.
- **La página empieza muy oscura y se aclara desde el centro hacia los bordes** (`static/intro.html`). La cortina
  que subía y desvelaba la página de abajo arriba se cambia por un cuadrado oscuro de 160vmax con un claro diminuto
  en el centro, que se agranda (`scale` de 1 a 16) y se desvanece al final. Sigue siendo solo `transform` y
  `opacity`, como exige `tests/app/test_intro.py` (D-043, D-044). El haz de CSS que baja desde arriba queda más
  tenue (opacidad máxima 0,5), para que la luz principal salga del centro.
- Se probó primero animar el radio del degradado con `@property`; se descartó porque repinta en cada cuadro y rompe
  la regla de la intro.

## Pendiente

- Revisarlo a ojo en el navegador (Isma, en local) y en un ordenador sin tarjeta gráfica (ahí sale el ojo plano,
  pero el aclarado desde el centro es el mismo).

## Siguiente paso

Si gusta, fusionar `feat/intro-luz-pupila` en `main`.
