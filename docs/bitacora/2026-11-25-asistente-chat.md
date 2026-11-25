# 2026-11-25 · El asistente como un chat

**Quién:** Lucas con Claude (agente). Rama `feat/asistente-chat`, integrada en `main` junto con `fix/ficha-buscador` (D-058).

## Qué se ha hecho (D-059)

- **Asistente:** solo un panel de chat de cristal. Lleva el ojo y un saludo al empezar, la conversación en una zona que se desplaza, tres sugerencias que se pueden cambiar y la caja de escribir. Sin título, párrafos ni pie.
- **Pantalla nueva «Aviso legal y fuentes»** en Explorar. Recoge lo que salía en el pie y en la cabecera del asistente, y la lista de preguntas preparadas.
- **Comprobado en Chrome:**
  - la pantalla vacía;
  - una sugerencia con su respuesta (gráfico y tabla dentro del panel);
  - el cambio de sugerencias;
  - la pantalla del aviso.

  `pytest` en verde.

## A partir de ahora

Lucas pide que todo se fusione y se suba a `main` al momento, porque `main` se publica solo en la web (D-056).

## Segunda vuelta (D-060)

- Panel del chat en cristal azul vivo, como el de la presentación, con las sugerencias y la caja de escribir a juego.
- El ojo, fuera del panel y a su izquierda: flota, gira y mira a los lados.

## Tercera vuelta

- **Icono de la persona:** una silueta clara dentro de un círculo fino, en lugar del cuadrado rojo con la carita de Streamlit. Se oculta el icono por defecto y se pinta la silueta con CSS, así se mantiene el avatar de usuario que alinea los mensajes.
- **Tu pregunta:** una burbuja de cristal claro translúcido, a la medida del texto y a la derecha, en lugar del degradado azul y cian.
