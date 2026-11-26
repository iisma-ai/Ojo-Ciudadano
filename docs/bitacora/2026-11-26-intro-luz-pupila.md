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
- **Halo más difuso** (a petición de Isma, tras verlo): el halo de detrás del cristal se veía como un aro de luz
  alrededor del ojo. Pasa a ser más grande (escala 7 en lugar de 4,2), más tenue (0,11 en lugar de 0,24) y con una
  caída más lenta, para que se funda con el fondo. El halo de CSS del centro (`.oc-intro-luz`) también se suaviza
  y se extiende más.
- **Haces que no se distinguen** (a petición de Isma): los haces se veían como rectángulos claros. Ahora son 18 en
  lugar de 11, más anchos y más tenues (intensidad 0,12 en lugar de 0,26), con un perfil de campana a los lados
  (sin borde) y una variación suave a lo largo, de modo que se solapan y se leen como una sola luz. El cono sube de
  0,5 a 0,62 para que la página siga igual de iluminada.
- **El ojo sube más y se desvanece más poco a poco** (a petición de Isma): tras subir (1,4-2,4 s) sigue subiendo
  despacio hasta casi el borde de arriba (2-3 s). El desvanecimiento va de 1,9 a 3 s con una curva cuadrática, que
  empieza muy suave: casi todo llega cuando el ojo ya está más arriba. La entrada sigue durando 3 s.
- Se probó primero animar el radio del degradado con `@property`; se descartó porque repinta en cada cuadro y rompe
  la regla de la intro.

## Pendiente

- Revisarlo a ojo en el navegador (Isma, en local) y en un ordenador sin tarjeta gráfica (ahí sale el ojo plano,
  pero el aclarado desde el centro es el mismo).

## Siguiente paso

Si gusta, fusionar `feat/intro-luz-pupila` en `main`.
