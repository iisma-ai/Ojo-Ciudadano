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

## Después: el ordenador, como antes; el móvil, todas las consejerías (rama `fix/movil-todas-las-consejerias`)

Lo que vio el usuario:
- en su portátil el mapa salía en la forma del móvil (6 burbujas y «Ver más");
- en el móvil caben todas las consejerías y no hacen falta las páginas.

Causa de lo del portátil: la forma del móvil se elegía por el ancho del hueco del mapa (la
columna izquierda), que en un portátil puede bajar de 640 px.

Qué cambia:
- **Ordenador: exactamente lo de antes.** `burbujas.py` vuelve a la versión anterior a hoy y
  solo se le añade una rama aparte para el móvil.
  - La leyenda del mapa vuelve al texto de antes.
  - Las barras horizontales del ordenador vuelven a ser las de antes.
- **Qué cuenta como móvil:** el ancho de la pantalla (`window.innerWidth` < 640 px), no el del
  hueco del mapa.
- **Mapa en el móvil:**
  - se ven el centro y **todas** sus burbujas directas (las consejerías, o los contratos de la
    consejería abierta);
  - van en un óvalo alto que crece con el número de burbujas, repartidas a la misma distancia;
  - no hay páginas ni «Ver más»;
  - los contratos se ven al pulsar la consejería;
  - el aviso de arriba pasa a ser «Pulsa una burbuja para ver más».
- **Toques:** se mantiene lo del iPhone. En pantallas táctiles no se dibuja el aro de la tocada,
  no hay «pasar por encima» y no sale el resaltado gris.
- **Barras en el móvil:** `graficos_contexto.pintar_barras` dibuja dos versiones (la de siempre
  y otra con nombres más cortos) y `estilo.css` enseña solo la que toca según el ancho.

**Fallo de CSS encontrado al probar:**
- En `estilo.css`, el `@media (max-width: 640px)` del selector «A dónde va / De dónde viene» no
  estaba cerrado (pasó al fusionar el 25-nov).
- Por eso todo lo que va detrás solo se aplica en el móvil: la burbuja del cuadro al pasar el
  ratón en Plotly y las entradas animadas de gráficos y desplegables.
- Para no cambiar el ordenador hoy, se cierra al final del fichero, antes de las reglas nuevas.
- Pendiente de decidir: cerrarlo donde toca, lo que activaría esos estilos también en el
  ordenador.

Comprobado con capturas a 390 px (mapa, consejería abierta con un toque táctil, portada,
presupuesto y contexto) y a 1000 y 1400 px (como antes). 496 tests en verde.
