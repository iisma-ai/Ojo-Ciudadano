# Presentación de Ojo Ciudadano

Presentación animada en HTML: un viaje bajo el mar con el ojo como guía. Sin instalar nada.

## Cómo verla

Abre `index.html` en Chrome (doble clic). Si el navegador bloquea algo al abrirlo como fichero, sirve la carpeta
raíz del repositorio con `python -m http.server 8600` y abre `http://127.0.0.1:8600/presentacion/index.html`.

- Flechas, espacio o clic: siguiente paso. Flecha izquierda o clic en el borde izquierdo: atrás.
- `F`: pantalla completa. `#3` al final de la dirección abre directamente la diapositiva 3.
- Cada diapositiva tiene varios pasos (una pulsación cada uno), así que el ritmo lo marcas tú.

## Cómo cambiarla

Todo el contenido está en `diapositivas.js`, con los tipos de elemento explicados al principio:
textos, cifras, burbujas (con su nivel de llenado), enlaces y capturas. Las cifras reales están en el
objeto `DATOS`. El resto de ficheros es el motor y no hace falta tocarlo:

| Fichero | Qué hace |
| --- | --- |
| `fondo.js` | Agua, rayos de luz, partículas y burbujas que suben; se oscurece al bajar |
| `ojo.js` | El ojo: mira, parpadea y sigue el ratón |
| `escena.js` | Construye las diapositivas y la navegación |
| `estilo.css` | Aspecto: cristal, agua, sombras, textos |

## Capturas y vídeos de la aplicación

Las burbujas de tipo `captura` están vacías. Guarda las imágenes o vídeos (`.png`, `.jpg`, `.mp4`, `.webm`) en
`presentacion/media/` y pon la ruta en `src`, por ejemplo `src: "media/mapa.mp4"`. Los vídeos se reproducen
solos, en bucle y sin sonido, dentro de la burbuja.
