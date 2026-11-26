# Presentación de Ojo Ciudadano

Presentación de la demo y la entrega de DataMad 2026 (H3, 24-nov; H4, 26-nov). Es una página HTML en 3D en
tiempo real (WebGL con Three.js), sin vídeo: cada diapositiva se pasa con las flechas, así que el ritmo lo marca
quien presenta.

## La idea

Un viaje bajo el mar, en azul marino que se oscurece al bajar. El gasto público es público, pero está escondido en el fondo: datos dispersos,
formatos técnicos, APIs. El ojo de cristal (Ojo Ciudadano) acompaña todo el recorrido y es el que ilumina lo que está
oculto. Las burbujas son el dinero: cada contrato es una burbuja de cristal llena de líquido hasta lo que
se ha gastado, y se unen en consejerías y en la Comunidad de Madrid. Poco texto: se enseña, no se lee.

| # | Escena | Guion |
| --- | --- | --- |
| 1 | Fuera del agua, sin ojo: atardecer, mar y las rocas desde las que se salta; al pulsar, nos asomamos al borde y no se ve lo que hay debajo | Ignacio: Málaga, las rocas, saltar |
| 2 | Bajo el agua, oscuro: las rocas están pero no se ven | Datos «transparentes» que no se pueden ver |
| 3 | Aparece el ojo de cristal, «Ojo Ciudadano», y su luz ilumina | La plataforma accesible |
| 4 | De dónde viene y a dónde va el dinero de 2025: arriba los tres ingresos que más aportan (impuestos directos, indirectos y préstamos), el dinero baja a la Comunidad de Madrid y, al pulsar, sale hacia las cuatro mayores consejerías; después la cámara entra en Sanidad y salen ejemplos sueltos de en qué gasta: licitaciones, un contrato menor (café) y una subvención (cuidados paliativos), con nombre corto | Isma: el mapa interactivo |
| 5 | Enjambre de burbujas, 1.354.441 contratos y, debajo, 872.821 subvenciones | Más de un millón de contratos abruma |
| 6 | Solo burbujas; «6 señales» con tres ejemplos en grande, sin cifras; un contrato atípico; y el resumen: señales a un lado, atípicos al otro, «No son acusaciones» | Los 6 indicadores, los atípicos y que no son acusaciones |
| 7 | El asistente: tres preguntas reales (organismos con más importe en 2025, tarta de los recursos ante el Tribunal y una pregunta sencilla: «¿la Comunidad tiene helicópteros?») | La IA busca, compara, relaciona y visualiza |
| 8 | El ojo y un QR de cristal | Ignacio: ya está en marcha, pruébalo |
| 9 | Burbujas con las tecnologías | El stack |
| 10 | Cierre | Democratizar los datos. Gracias |

Estado: adaptada al guion del 24-nov. El QR de la escena 8 apunta a `https://ojo-ciudadano.iismael.workers.dev/` (`DATOS.urlApp` en `diapositivas.js`). Faltan las capturas o vídeos de la aplicación (burbujas de las
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
- El ojo no sigue el ratón: mira al centro y de vez en cuando echa un vistazo a los lados.

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

## Versión para el jurado (`jurado.html`)

Tres diapositivas, como piden las bases de DataMad 2026, con más texto: el jurado la lee sola, sin
quien presente. Mismo motor (`escena3d.js`) y mismos tipos de elemento; el contenido está en
`diapositivas-jurado.js` y sus estilos en `jurado.css`.

| # | Escena | Qué cuenta |
| --- | --- | --- |
| 1 | En la roca, sobre el mar, con el ojo | Nombre del proyecto, integrantes y la propuesta: que cualquier ciudadano vea a dónde va su dinero |
| 2 | Salto al agua; el mar turbio se aclara con la luz del ojo | El problema y los datos: primero los conjuntos del Catálogo de Datos Abiertos de la Comunidad, con enlace, y después las fuentes de contratos y subvenciones |
| 3 | Más abajo, entre muchas burbujas | Qué hacemos con los datos (unión, seis indicadores, aprendizaje automático), el agente de Ojo Ciudadano, utilidad, impacto y viabilidad, y el QR y los enlaces a la web y al código |

Se abre igual que la otra, servida desde la raíz del repositorio:
`http://127.0.0.1:8600/presentacion/jurado.html`. Los enlaces se pueden pulsar (se abren en otra
pestaña); un clic en cualquier otro sitio pasa de paso.

