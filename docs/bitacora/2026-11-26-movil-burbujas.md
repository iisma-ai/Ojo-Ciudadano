# 26-nov-2026 · Las burbujas y las barras se leen en el móvil

**Rama:** `fix/movil-burbujas`

## Contexto

El día de la entrega la mayoría de visitantes entra con el móvil (código QR). En una pantalla de
390 px el mapa de burbujas de «¿A dónde va el dinero?» encogía unas 60 burbujas en un cuadro
diminuto, con las etiquetas pisadas e ilegibles y mucho hueco vacío debajo.

## Qué se ha hecho

- **Mapa de burbujas en el móvil** (`burbujas.py`, solo JavaScript; por debajo de 640 px de
  ancho):
  - se ven el centro y sus burbujas directas, de 6 en 6, en un óvalo; la burbuja «Ver N más»
    pasa a las siguientes (sin recargar) y al final vuelve a las primeras;
  - las de un nivel más (los contratos de cada consejería) no se dibujan: se ven al pulsar la
    consejería, que ya la pone en el centro con todos sus contratos;
  - tamaños y letra legibles, nombres partidos en líneas cortas, etiquetas que no se salen por
    los lados, zona de pulsación más grande y un aviso arriba («Vista 1 de 3 · pulsa "Ver más"
    para el resto»);
  - el alto del mapa sale del ancho, así que no queda hueco vacío.
  - En pantallas grandes no cambia nada.
  - Vale para todos los mapas de burbujas: portada, mapa del dinero, la consejería ampliada,
    «¿De dónde viene el dinero?» y la red del dinero.
- **Leyenda del mapa:** dice que en el móvil los contratos se ven al pulsar la consejería.
- **Barras horizontales** (`graficos_contexto.barras_horizontales`): los nombres largos se
  cortaban por la izquierda y las cifras por la derecha en el móvil. Ahora los nombres van en
  líneas más cortas, el margen se ajusta solo y hay más sitio para la cifra.

## Cómo se ha comprobado

Capturas con Chrome sin ventana a 390 px de ancho (emulación de móvil y pantalla táctil) de
todas las pantallas: inicio, mapa del dinero (las dos caras), contratos a revisar, atípicos, red
del dinero, presupuesto y contexto, fichas, asistente y aviso legal. Ninguna se sale por los
lados. Se han pulsado «Ver más» y una consejería en el mapa. A 1400 px el mapa sale igual que
antes. 496 tests en verde y `ruff` limpio.

## Siguiente paso

Probarlo en un móvil real con datos, después de fusionar en `main`.

## Después: la marca del último toque en el iPhone (rama `fix/movil-toque`)

En el iPhone, al tocar una burbuja quedaba un aro alrededor (y a veces la burbuja agrandada con
su cuadro de cifras), como si siguiera señalada. Causa: el aro es el de «burbuja seleccionada»
del ordenador, y el móvil, al tocar, simula un ratón encima del punto tocado, así que la burbuja
se quedaba como «con el ratón encima» porque nunca llega el «ratón se va».

- Con el dedo ya no hay «pasar por encima» (solo con un ratón de verdad, por `pointerType`).
- En pantallas táctiles no se dibuja el aro de la burbuja tocada. Se mira la pantalla
  (`hover: none` o `pointer: coarse`) y el último toque, para que valga también en el mapa nuevo
  de la consejería abierta.
- Sin el resaltado gris de iOS al tocar el lienzo.
- En el ordenador, igual que antes (aro, cuadro y agrandar al pasar el ratón).

Comprobado con un toque táctil de verdad (emulado por DevTools) a 390 px, comparado con la
versión anterior, que sí dejaba el aro, y a 1400 px.
