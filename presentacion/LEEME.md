# Presentación de Ojo Ciudadano

Presentación animada en HTML: un viaje bajo el mar con el ojo como guía. Sin instalar nada.

## Cómo verla

Es 3D en tiempo real (WebGL con Three.js), así que hay que servirla, no abrirla con doble clic. Desde la
raíz del repositorio:

```bash
uv run python -m http.server 8600
```

y abre `http://127.0.0.1:8600/presentacion/index.html` en Chrome. Necesita internet la primera vez
(Three.js y la tipografía vienen de CDN); si el sitio de la demo no tiene conexión, hay que copiar esos
ficheros a la carpeta antes.

- Flechas, espacio o clic: siguiente paso. Flecha izquierda o clic en el borde izquierdo: atrás.
- `F`: pantalla completa. `#3` al final de la dirección abre directamente la diapositiva 3.
- Cada diapositiva tiene varios pasos (una pulsación cada uno), así que el ritmo lo marcas tú.
- El ojo mira al cursor si lo mueves; a los tres segundos vuelve a mirar donde toca.

## Cómo cambiarla

Todo el contenido está en `diapositivas.js`, con los tipos de elemento explicados al principio:
textos, cifras, burbujas (con su nivel de llenado), enlaces y capturas. Las cifras reales están en el
objeto `DATOS`. El resto de ficheros es el motor y no hace falta tocarlo:

| Fichero | Qué hace |
| --- | --- |
| `escena3d.js` | Monta cada diapositiva a una profundidad del mar, la cámara baja entre ellas; burbujas de cristal con líquido, enlaces, luz y navegación |
| `agua.js` | Color del agua, superficie vista desde abajo, rayos de sol, partículas, burbujas que suben y acabado de cámara |
| `ojo3d.js` | El globo ocular: esclera, iris, pupila que se dilata y córnea |
| `estilo.css` | Tipografía de los textos que van encima del 3D |

## Capturas y vídeos de la aplicación

Las burbujas de tipo `captura` están vacías. Guarda las imágenes o vídeos (`.png`, `.jpg`, `.mp4`, `.webm`) en
`presentacion/media/` y pon la ruta en `src`, por ejemplo `src: "media/mapa.mp4"`. Los vídeos se reproducen
solos, en bucle y sin sonido, dentro de la burbuja.
