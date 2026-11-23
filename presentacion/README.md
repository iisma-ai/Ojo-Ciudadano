# Presentación de Ojo Ciudadano

Presentación de la demo y la entrega de DataMad 2026 (H3, 24-nov; H4, 26-nov). Es una página HTML en 3D en
tiempo real (WebGL con Three.js), sin vídeo: cada diapositiva se pasa con las flechas, así que el ritmo lo marca
quien presenta.

## La idea

Un viaje bajo el mar. El gasto público es público, pero está escondido en el fondo: datos dispersos,
formatos técnicos, APIs. El ojo (Ojo Ciudadano) acompaña todo el recorrido y es el que ilumina lo que está
oculto. Las burbujas son el dinero: cada contrato es una burbuja de cristal llena de líquido hasta lo que
se ha gastado, y se unen en consejerías y en la Comunidad de Madrid. Poco texto: se enseña, no se lee.

| # | Escena | Qué se cuenta |
| --- | --- | --- |
| 1 | Portada bajo la superficie, el ojo grande | Ojo Ciudadano |
| 2 | Bajamos; el ojo va a la esquina y aparecen burbujas | Cada burbuja es un contrato; cuanto más llena, más gastado |
| 3 | Las burbujas se unen a consejerías y a la Comunidad | 22.857 M€ adjudicados (Plataforma de Contratación, sin IVA, 2023-2026) |
| 4 | Una cifra enorme y la niebla lo tapa todo | 1,35 millones de contratos públicos, pero no accesibles |
| 5 | El ojo enciende un haz de luz | Ojo Ciudadano lo hace transparente |
| 6 | Burbujas con la aplicación dentro | Mapa del dinero, ficha de empresa, ficha de organismo |
| 7 | Más burbujas | Señales, no acusaciones; asistente con citas |
| 8 | Cierre, el ojo de nuevo grande | Lo público, a la vista de todos |

Estado: prueba de concepto completa. Faltan las capturas o vídeos de la aplicación (burbujas de las
escenas 6 y 7), revisar los textos con `revisor-legal` y probarla en el ordenador y el proyector de la demo.

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
