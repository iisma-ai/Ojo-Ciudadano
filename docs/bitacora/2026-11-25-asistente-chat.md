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
