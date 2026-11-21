# 11 · Accesibilidad y visualización

> Objetivo (D-023): que **cualquier ciudadano** entienda en pocos segundos qué es Ojo Ciudadano y qué está viendo, **con gráficos y esquemas antes que con texto**. Sin tratar a nadie de tonto y sin saturar la pantalla.

## Principios

1. **Primero se ve, luego se lee.** Cada pantalla empieza con una imagen que responde a su pregunta: una cifra grande, un gráfico o un esquema. El texto acompaña, no explica lo que el gráfico ya cuenta.
2. **Lenguaje claro.**
   - Frases cortas y palabras de uso común: «una sola empresa se presentó», no «licitador único en procedimiento con concurrencia».
   - El término técnico va entre paréntesis o en la ayuda, nunca como título.
   - Nada de cifras sin contexto: «2 de 3 señales» no dice nada; hay que decir **qué señales**.
3. **Una idea por bloque y nada repetido.** Si algo ya está en la barra lateral o en la ayuda, no se vuelve a poner en la pantalla.
4. **Cada indicador tiene su propia visualización**, pensada para lo que mide (ver «Estudios de visualización»). Ningún gráfico genérico «porque sí».
5. **El tamaño representa dinero** cuando se muestran relaciones entre órganos y empresas (burbujas, flujos), para que se vea de un vistazo quién recibe más.
6. **Se mantiene lo legal.** Lenguaje no acusatorio (D-002), sin personas físicas (D-007) y cada cifra con su enlace (regla 5 de `CLAUDE.md`). Cambia cómo se cuenta, no lo que se cuenta.
7. **Accesible de verdad:**
   - contraste AA;
   - el color nunca es la única pista (también forma o texto);
   - texto alternativo en los gráficos;
   - legible en el móvil;
   - sin emojis (D-022).

## Tareas

Cada tarea de pantalla empieza con un **estudio**: qué pregunta responde, qué datos hay, dos o tres formas de visualizarlo y por qué se elige una. El estudio se anota en este documento antes de programar. Orden por prioridad: lo que entra en la demo del 24-nov va primero.

| ID | Pantalla | Qué hay que conseguir | Prioridad | Estado |
| --- | --- | --- | --- | --- |
| A-01 | **Portada** (nueva) | Que en 10 segundos se entienda qué es Ojo Ciudadano: una frase, tres cifras grandes (dinero seguido, contratos, señales) y tres puertas de entrada («Ver contratos a revisar», «Buscar una empresa», «Ver a quién paga cada organismo») | Alta (demo) | Pendiente |
| A-02 | **Qué mide cada señal** | Una tarjeta por indicador con nombre en lenguaje llano, la pregunta que responde, un esquema mínimo y cuántos contratos la tienen. Se puede abrir desde cualquier señal | Alta (demo) | Pendiente |
| A-03 | **Panel de alertas** | Lista con **el nombre de cada señal** en vez de «2 de 3». Sin el control de «mínimo de indicadores aplicables». Al abrir un contrato, **un gráfico por cada señal** (ver estudios E-01 a E-06) | Alta (demo) | Pendiente |
| A-04 | **Contratos atípicos** | Ver dónde cae el contrato frente a sus contratos similares: nube de puntos o distribución con el contrato resaltado (estudio E-07) | Media | Pendiente |
| A-05 | **Ficha de empresa** | Resumen visual: de qué organismos recibe dinero (burbujas, el tamaño es el importe), evolución por año y señales con nombre | Alta (no recortable) | Pendiente |
| A-06 | **Ficha de organismo** | A qué empresas paga (burbujas o mapa de áreas por importe), lo concentrado que está su gasto y cómo contrata (barra de procedimientos) | Media | Pendiente |
| A-07 | **Mapa del dinero** | Rehacerlo para que se entienda: empezar por pocos organismos, red de burbujas (organismo → empresa, tamaño = dinero) en vez de un diagrama de flujos denso, y elegir un organismo para ver su red | Media | Pendiente |
| A-08 | **Preguntas guiadas y asistente** | Cada respuesta con una frase resumen y un gráfico automático según el tipo de resultado (ranking → barras, evolución → línea) | Media | Pendiente |
| A-09 | **Glosario en contexto** | Definición al pasar el ratón por los términos inevitables (organismo, adjudicataria, contrato menor, licitación) | Baja | Pendiente |
| A-10 | **Revisión de accesibilidad** | Pasada final por todas las pantallas: contraste, color, textos alternativos, móvil, longitud de los textos | Alta (antes del 25) | Pendiente |
| A-11 | **Prueba con personas no expertas** | Enseñar la web a 2 o 3 personas ajenas al proyecto: ¿entienden qué es en 30 s y qué significa una alerta? Anotar lo que no entienden | Alta (antes del 25) | Pendiente |

## Estudios de visualización por indicador

Primera propuesta; cada estudio se completa al hacer A-03 (datos usados, alternativas y elección).

| Estudio | Señal | Qué hay que ver | Propuesta |
| --- | --- | --- | --- |
| E-01 | R-01 · Una sola empresa se presentó | Que este contrato tuvo 1 oferta cuando lo normal en contratos parecidos son varias | Puntos o barras: ofertas de este contrato frente a la mediana de su tipo |
| E-02 | R-02 · Adjudicado sin anuncio público | Qué parte de lo que gasta el organismo va por esta vía | Barra apilada del organismo: con anuncio / sin anuncio, con este contrato marcado |
| E-03 | R-03 · Muchos contratos pequeños a la misma empresa | Que la suma de contratos menores en 12 meses supera el límite legal | Línea temporal de los menores (puntos por fecha e importe) con la suma acumulada y la línea del límite |
| E-04 | R-04 · Una empresa se lleva casi todo | Qué parte del gasto del organismo en ese tipo de contrato se lleva la empresa | Anillo o mapa de áreas con la cuota de la empresa frente al resto |
| E-05 | R-05 · Subió mucho de precio después | Cuánto se añadió en modificaciones respecto a lo adjudicado | Barra de lo adjudicado más lo añadido, con la línea del 20 % |
| E-06 | R-06 · Rebaja de precio anormal o nula | Diferencia entre el precio de salida y el adjudicado | Dos barras (precio de salida y adjudicado) con la zona «normal» sombreada |
| E-07 | Contrato atípico | En qué se aleja de sus pares | Distribución de los contratos similares en las dos variables del motivo, con este contrato resaltado |

## Guía rápida de redacción

| En vez de | Escribir |
| --- | --- |
| Indicadores de riesgo aplicables / activados | Señales que se pudieron comprobar / señales encontradas |
| 2 de 3 señales | «Una sola oferta» y «Sin anuncio público» (de 3 comprobadas) |
| Órgano de contratación | Organismo (y «órgano de contratación» en la ayuda) |
| Adjudicatario | Empresa que lo ganó |
| Puntuación ponderada | Proporción de señales, teniendo en cuenta el dinero |
| Procedimiento negociado sin publicidad | Adjudicado sin anuncio público |
