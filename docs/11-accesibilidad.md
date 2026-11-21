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
| A-01 | **Portada** (nueva) | Que en 10 segundos se entienda qué es Ojo Ciudadano: una frase, tres cifras grandes (dinero seguido, contratos, señales) y tres puertas de entrada («Ver contratos a revisar», «Buscar una empresa», «Ver a quién paga cada organismo») | Alta (demo) | Hecho (21-nov): `paginas/inicio.py`, página por defecto |
| A-02 | **Qué mide cada señal** | Una tarjeta por indicador con nombre en lenguaje llano, la pregunta que responde, un esquema mínimo y cuántos contratos la tienen. Se puede abrir desde cualquier señal | Alta (demo) | Hecho (21-nov), primera versión: tarjetas en la portada con barra de proporción; filtro por señal con su frase en «Contratos a revisar» |
| A-03 | **Panel de alertas** | Lista con **el nombre de cada señal** en vez de «2 de 3». Sin el control de «mínimo de indicadores aplicables». Al abrir un contrato, **un gráfico por cada señal** (ver estudios E-01 a E-06) | Alta (demo) | Hecho (21-nov): «Contratos a revisar», insignias con el nombre de cada señal y «de N señales comprobadas», interruptor de menores en vez del control de mínimo, un gráfico por señal al pulsar «Ver gráficos» |
| A-04 | **Contratos atípicos** | Ver dónde cae el contrato frente a sus contratos similares: nube de puntos o distribución con el contrato resaltado (estudio E-07) | Media | Pendiente |
| A-05 | **Ficha de empresa** | Resumen visual: de qué organismos recibe dinero (burbujas, el tamaño es el importe), evolución por año y señales con nombre | Alta (no recortable) | Hecho (21-nov): ver «Estudio A-05» |
| A-06 | **Ficha de organismo** | A qué empresas paga (burbujas o mapa de áreas por importe), lo concentrado que está su gasto y cómo contrata (barra de procedimientos) | Media | Hecho (21-nov): ver «Estudio A-06» |
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
| E-04 | R-04 · Una empresa concentra el gasto | Qué parte del importe que adjudica el organismo en ese tipo de contrato recibe la empresa | Anillo o mapa de áreas con la cuota de la empresa frente al resto |
| E-05 | R-05 · Modificaciones de más del 20 % | Cuánto se añadió en modificaciones respecto a lo adjudicado | Barra de lo adjudicado más lo añadido, con la línea del 20 % |
| E-06 | R-06 · Rebaja nula o muy alta | Diferencia entre el precio de salida y el adjudicado | Dos barras (precio de salida y adjudicado) con la zona «normal» sombreada |
| E-07 | Contrato atípico | En qué se aleja de sus pares | Distribución de los contratos similares en las dos variables del motivo, con este contrato resaltado |

## Resultado de los estudios E-01 a E-06 (21-nov)

Implementados en `app/graficos.py` (gráficos), `app/senales.py` (frase con cifras y gráfico de cada señal) y `app/datos.py` (`detalle_r01`… `detalle_importes`). Probados con contratos reales de cada señal.

| Estudio | Alternativas valoradas | Elegido y por qué |
| --- | --- | --- |
| E-01 | Cifra sola («1 oferta»); comparación con la mediana; distribución | **Distribución de ofertas** de los contratos del mismo tipo con la barra de este contrato en azul, y la frase «de N contratos parecidos, el X % recibió dos o más». La mediana sola engaña: en suministros también es 1 |
| E-02 | Anillo; barra apilada | **Barra apilada** del organismo (con / sin anuncio), con el porcentaje en la leyenda. Una barra se lee mejor que un anillo para dos partes |
| E-03 | Puntos por contrato; suma acumulada desde el inicio; suma móvil de 12 meses | **Suma de los 12 meses anteriores** en escalera, con un punto por contrato (este, más grande y en azul) y la línea del límite en ámbar. Es la misma ventana que usa R-03; los puntos sueltos quedaban aplastados contra el eje |
| E-04 | Mapa de áreas; anillo; barras | **Anillo** con la empresa en azul, las 4 siguientes y «Otras N empresas» en gris, y la cuota en el centro. Los porcentajes van en la leyenda: dentro del anillo eran ilegibles en los trozos pequeños |
| E-05 | Dos barras; barra apilada | **Barra apilada**: precio adjudicado (gris) + lo añadido después (azul), con la marca del +20 % |
| E-06 | Barras con zona sombreada; dos barras | **Dos barras** (precio de salida y adjudicado) con la cifra dentro, y la rebaja en la frase. La zona sombreada añadía ruido |

Formato común: números y fechas en español (`1.234`, `05/2025`), fondo transparente, sin barra de herramientas y una frase con las mismas cifras encima de cada gráfico (texto alternativo).

## Estudio A-05 · Ficha de empresa (21-nov)

- **Pregunta:** qué contratos y subvenciones tiene una empresa, de qué organismos y con qué señales.
- **Problema de los datos:** PLACSP da importes sin IVA, el portal con IVA y la BDNS importes concedidos. No se pueden sumar (P-10).
- **Alternativas para «de qué organismos»:**
  - burbujas: no hay disposición nativa y las áreas se comparan mal;
  - barras horizontales: precisas, pero planas;
  - **mapa de áreas (elegido):** el tamaño es el importe, hay un color por organismo (paleta categórica) y los que pasan del 12.º se agrupan en «Otros N organismos». Un selector de fuente evita mezclar bases de IVA; por defecto se muestra la fuente con más importe.
- **Evolución:** barras apiladas del **número** de contratos por año (sin señales en gris, con alguna señal en ámbar). Se usan recuentos, no importes, para no mezclar bases.
- **Señales:** barras horizontales en ámbar con el número de contratos con cada señal.
- **Contratos:** la misma tarjeta desplegable que «Contratos a revisar» (`senales.tarjeta_contrato`), los 30 con más señales e importe.
- **Cifras:** contratos, contratos con alguna señal, importe adjudicado (con su base de IVA en la etiqueta y las dos fuentes en la ayuda) y subvenciones.

## Estudio A-06 · Ficha de organismo (21-nov)

- **Pregunta:** a quién adjudica, cómo contrata y cómo se compara con los demás organismos.
- **A quién adjudica:** mapa de áreas como en A-05, con selector de fuente.
  - Con cientos de proveedores, la caja «Otros» ocupaba casi todo. Por eso se muestran las 20 empresas con más importe y el texto dice qué parte del total suman.
  - Las personas físicas van juntas en una caja gris sin nombre (D-007).
- **Comparado con los demás:**
  - Alternativas: tabla de porcentajes (era lo que había) o barras agrupadas.
  - **Elegido:** un punto por señal, el del organismo en azul frente a la marca de todos los organismos en gris, unidos por una línea. Se ve a la vez la diferencia y su sentido.
- **Cómo contrata:** barras horizontales por vía de adjudicación con nombres llanos (`textos.PROCEDIMIENTO_LLANO`). Se suman las vías con el mismo nombre y el resto va a «Otras vías».
- **Por año:** el mismo gráfico de contratos con y sin señales que en A-05.
- **Contratos:** los 20 del organismo con más señales, como tarjetas desplegables.
- **Subvenciones:** un desplegable con las convocatorias.
- **Cifras:** importes legibles («3,9 mil millones €»).

## Guía rápida de redacción

| En vez de | Escribir |
| --- | --- |
| Indicadores de riesgo aplicables / activados | Señales que se pudieron comprobar / señales encontradas |
| 2 de 3 señales | «Una sola oferta» y «Sin anuncio público» (de 3 comprobadas) |
| Órgano de contratación | Organismo (y «órgano de contratación» en la ayuda) |
| Adjudicatario | Empresa que lo ganó |
| Puntuación ponderada | Proporción de señales, teniendo en cuenta el dinero |
| Procedimiento negociado sin publicidad | Adjudicado sin anuncio público |
| Se lleva, domina, gasta | Recibe, concentra, adjudica (revisión legal del 21-nov: medimos importe adjudicado, no pagado) |
| Habría que hacer un concurso | Pasa del importe máximo de un contrato menor; puede ser normal si son compras distintas |
