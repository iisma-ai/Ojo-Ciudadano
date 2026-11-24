# 2026-11-24 · Presentación: tono oscuro, ojo de cristal y escenas con datos reales

## Qué se hizo
- Agua en azul marino desde la superficie, que se oscurece al bajar sin llegar a negro; superficie, rayos y reflejos más apagados (`agua.js`).
- El ojo pasa a ser de cristal (`ojo3d.js`): esfera de vidrio con borde luminoso, iris de luz en anillos y fibras que giran y pupila de cristal oscuro. Un ojo realista daba grima según el feedback.
- Motor (`escena3d.js`): la cámara puede acercarse a una burbuja (`foco`); el ojo va pegado a la cámara; paneles de cristal fijos en pantalla con bloques que se dibujan solos (cifras, barras, medidor, de cada 100, señales, filas, fuentes); chat del asistente que escribe la pregunta, piensa y contesta. `hasta` hace que un panel o un foco se releven.
- Escenas nuevas con datos reales de la base (2025): Sanidad (40 de cada 100 € gastados por la Comunidad; empresas; procedimientos), el contrato de la vacuna VPH (negociado sin publicidad, una oferta, señal R-02 con su explicación), señales de cada 100 (R-01 39, R-02 31, R-03 17) y dos respuestas preparadas del asistente (R-01 por año con referencias de OIReScon y la Comisión; organismos con más importe en 2025).

## Ojo de cristal, segunda versión
- El primer ojo de cristal parecía de plástico (capas mates y reflejos con forma de ventana). Ahora es una bola de cristal maciza con un sombreado propio: el rayo entra, cruza la esfera y sale (refracción con un índice por color: dispersión), y lo que se ve a través es el mar alrededor (la superficie luminosa invertida abajo). Brillos nítidos, borde fino de luz y el iris y la pupila pintados dentro.
- Se descartó `transmission` de Three.js: solo refracta objetos opacos y casi todo el mar es transparente, así que se veía lechoso.

## Pendiente
- Guion definitivo (lo da Lucas) para ordenar las escenas.
- Capturas o vídeos de la web en la escena 9.
- Revisión de textos con `revisor-legal`.
