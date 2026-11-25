# 2026-11-24 · Presentación: tono oscuro, ojo de cristal y escenas con datos reales

## Qué se hizo
- Agua en azul marino desde la superficie, que se oscurece al bajar sin llegar a negro; superficie, rayos y reflejos más apagados (`agua.js`).
- El ojo pasa a ser de cristal (`ojo3d.js`): esfera de vidrio con borde luminoso, iris de luz en anillos y fibras que giran y pupila de cristal oscuro. Un ojo realista daba grima según el feedback.
- Motor (`escena3d.js`): la cámara puede acercarse a una burbuja (`foco`); el ojo va pegado a la cámara; paneles de cristal fijos en pantalla con bloques que se dibujan solos (cifras, barras, medidor, de cada 100, señales, filas, fuentes); chat del asistente que escribe la pregunta, piensa y contesta. `hasta` hace que un panel o un foco se releven.
- Escenas nuevas con datos reales de la base (2025): Sanidad (40 de cada 100 € gastados por la Comunidad; empresas; procedimientos), el contrato de la vacuna VPH (negociado sin publicidad, una oferta, señal R-02 con su explicación), señales de cada 100 (R-01 39, R-02 31, R-03 17) y dos respuestas preparadas del asistente (R-01 por año con referencias de OIReScon y la Comisión; organismos con más importe en 2025).

## Ojo de cristal, segunda versión
- El primer ojo de cristal parecía de plástico (capas mates y reflejos con forma de ventana). Ahora es una bola de cristal maciza con un sombreado propio: el rayo entra, cruza la esfera y sale (refracción con un índice por color: dispersión), y lo que se ve a través es el mar alrededor (la superficie luminosa invertida abajo). Brillos nítidos, borde fino de luz y el iris y la pupila pintados dentro.
- Se descartó `transmission` de Three.js: solo refracta objetos opacos y casi todo el mar es transparente, así que se veía lechoso.

## Tercera pregunta del asistente y mirada propia del ojo
- Nueva pregunta preparada de la app en el chat: la proporción de recursos ante el Tribunal que se estiman según el acto recurrido (1.104 resoluciones), con una tarta animada (bloque `tarta`) y el texto legal de la respuesta de la app. «Otros actos» suma Otros, Admisión y Anuncio (54 resoluciones, 8 estimadas).
- La pregunta de tipos de objeto (CPV) necesitaba la tabla `cpv` (D-035), pero el portal rechazó la descarga automática («Request Rejected»); no se forzó y se borró de la caché la respuesta vacía.
- El ojo ya no sigue el ratón (en la presentación nadie lo mueve): mira al centro y echa vistazos a los lados cada pocos segundos.

## Adaptada al guion
- Orden nuevo (ver `presentacion/README.md`): fuera del agua sin ojo (atardecer, mar visto desde arriba, rocas; cámara libre con `vista` para asomarse), bajada a la oscuridad, aparición del ojo, mapa (Sanidad y contrato, con su peso en el gasto de la consejería), millón de contratos, señales y atípico, asistente, QR (`qr`, librería qrcode-generator 1.4.4), tecnologías y cierre. Se quitan la escena de capturas vacías y la del total adjudicado.
- Arreglo: la niebla de Three.js guarda una copia del color; ahora se actualiza cada fotograma (las rocas salían blancas).
- El guion cita tecnologías que no usamos (Node, Vercel, PostgreSQL) y datos «desde 2016»; la escena de tecnologías usa las reales (Python, DuckDB, Polars, Streamlit, Plotly, scikit-learn, OpenRouter).

## Logos
- Las tecnologías llevan su logo real dentro de la burbuja (`logo` y `color` en una burbuja): Devicon a color (Python, Streamlit, Plotly, scikit-learn, Three.js) y Simple Icons teñidos con su color (DuckDB, Polars, OpenAI, Anthropic), servidos por jsDelivr en versiones fijas. OpenRouter no tiene logo en esas colecciones: la IA se muestra con los dos modelos que usamos (GPT y Claude) y «OpenRouter» en la etiqueta.
- Logo de Ojo Ciudadano (`app/static/logo-horizontal.svg`) en el panel del QR y en el cierre (tipo `imagen`).

## Pendiente
- Guion definitivo (lo da Ismael) para ordenar las escenas.
- Capturas o vídeos de la web en la escena 9.
- Revisión de textos con `revisor-legal`.

## Salto desde las rocas

- La bajada de la escena 1 a la 2 atravesaba la roca desde la que se salta (la cámara iba en línea recta hacia abajo). Ahora es un salto: impulso hacia arriba y adelante, pasa por delante de la roca, cae al agua y baja hasta la escena 2 (`zambullida` en `escena3d.js`, curva Catmull-Rom de 2,8 s). Al volver atrás hace el mismo camino al revés.
- Las dos rocas de debajo del salto se han apartado a los lados para dejar libre la caída. Comprobado en Chrome muestreando la cámara en cada fotograma: ningún punto del camino entra en una roca, ni a la ida ni a la vuelta.
