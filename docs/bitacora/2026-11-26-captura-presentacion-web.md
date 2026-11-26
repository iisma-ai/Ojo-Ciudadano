# 2026-11-26 · La captura de la presentación del jurado, publicada desde portada/

## Qué se ha hecho

- La diapositiva 4 de `presentacion/jurado.html` salía sin la captura de la web: el comando de build de Cloudflare
  solo copia los `.html`, `.js` y `.css` de `presentacion/`, y añadir la copia de `capturas/` en el panel no
  funcionó (lo probó Isma).
- Se copia la imagen a `portada/presentacion/capturas/web-inicio.jpg`. Cloudflare publica `portada/` tal cual, así
  que la imagen queda en `/presentacion/capturas/web-inicio.jpg`, la ruta que usa la diapositiva.

## Pendiente

- La captura queda duplicada (`presentacion/capturas/` y `portada/presentacion/capturas/`). Si se cambia, hay que
  cambiar las dos, o arreglar el comando de build y borrar la de `portada/`.
