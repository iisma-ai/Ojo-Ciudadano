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
| A-04 | **Contratos atípicos** | Ver dónde cae el contrato frente a sus contratos similares: nube de puntos o distribución con el contrato resaltado (estudio E-07) | Media | Hecho (21-nov): ver «Estudio A-04 / E-07» |
| A-05 | **Ficha de empresa** | Resumen visual: de qué organismos recibe dinero (burbujas, el tamaño es el importe), evolución por año y señales con nombre | Alta (no recortable) | Hecho (21-nov): ver «Estudio A-05» |
| A-06 | **Ficha de organismo** | A qué empresas paga (burbujas o mapa de áreas por importe), lo concentrado que está su gasto y cómo contrata (barra de procedimientos) | Media | Hecho (21-nov): ver «Estudio A-06» |
| A-07 | **Mapa del dinero** | Rehacerlo para que se entienda: empezar por pocos organismos, red de burbujas (organismo → empresa, tamaño = dinero) en vez de un diagrama de flujos denso, y elegir un organismo para ver su red | Media | Hecho (21-nov): ver «Estudio A-07» |
| A-08 | **Preguntas guiadas y asistente** | Cada respuesta con una frase resumen y un gráfico automático según el tipo de resultado (ranking → barras, evolución → línea) | Media | Hecho en «Preguntas guiadas» (21-nov): `graficos.automatico`. Falta conectarlo en la pantalla del asistente (la lleva Ignacio) |
| A-09 | **Glosario en contexto** | Definición al pasar el ratón por los términos inevitables (organismo, adjudicataria, contrato menor, licitación) | Baja | Hecho (21-nov): `textos.GLOSARIO` en la ayuda («?») de organismo, señal, fuentes, tipo de contrato y contrato menor |
| A-10 | **Revisión de accesibilidad** | Pasada final por todas las pantallas: contraste, color, textos alternativos, móvil, longitud de los textos | Alta (antes del 25) | Primera pasada (21-nov): ver «Revisión A-10». Repetir el 24-25 con la versión final |
| A-11 | **Prueba con personas no expertas** | Enseñar la web a 2 o 3 personas ajenas al proyecto: ¿entienden qué es en 30 s y qué significa una alerta? Anotar lo que no entienden | Alta (antes del 25) | Guion preparado (ver «Guion de la prueba A-11»); falta hacerla con 2 o 3 personas |

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

## Estudio A-07 · Mapa del dinero (21-nov)

- **Problema:** el diagrama de flujos (Sankey) con 20 flujos de muchos organismos a la vez no se entendía. Había demasiadas líneas cruzadas y demasiados nombres.
- **Alternativas valoradas:**
  - mantener el Sankey con menos flujos: sigue cruzándose;
  - red de fuerzas con todos los organismos y empresas: ilegible con más de 30 nodos y necesita otra dependencia;
  - **elegido, en dos pasos:**
    1. **Vista general:** burbujas empaquetadas de los 15 organismos que más adjudican (área = importe, un color por organismo, el nombre dentro de las grandes y un número en las pequeñas). Al lado, una lista numerada en la que cada organismo se puede pulsar.
    2. **Red de un organismo:** el organismo en el centro y sus 10 empresas alrededor. El área de cada burbuja y el grosor de cada línea son el importe, con un color por empresa y la etiqueta hacia fuera. Debajo, los contratos o convocatorias de la empresa elegida, con su enlace.
- El Sankey se conserva como «Vista avanzada» en un desplegable.
- Filtros: fuente (una cada vez, sin mezclar IVA), año, tipo y menores. El organismo también se elige en un desplegable, para quien no use el ratón.
- Sin dependencias nuevas: el empaquetado de burbujas está en `graficos.empaquetar` (búsqueda en espiral), con test de que no hay solapes.

## Estudio A-04 / E-07 · Contratos atípicos (21-nov)

- **Pregunta:** en qué se aleja este contrato de los parecidos.
- **Datos:** la detección (D-021) guarda ahora también `anomalia_variables`, con los valores de cada contrato. La interfaz toma una muestra fija (semilla 42) de 1.500 contratos del mismo grupo.
  - Ojo: en DuckDB, `USING SAMPLE` se aplica antes del `WHERE`. Hay que filtrar primero en una subconsulta.
- **Elegido:**
  - Con dos variables en el motivo: **nube de puntos** de los contratos similares en gris y este contrato en azul, con ejes en lenguaje llano.
  - Con una variable: **histograma** con una línea azul en la posición del contrato.
  - Importes y recuentos con mucha dispersión, en escala logarítmica.
  - Los porcentajes se recortan a los percentiles 1-99, porque hay rebajas erróneas de miles por cien en la fuente, pero este contrato nunca queda fuera.
- **Pantalla:** cada contrato atípico es un desplegable con el motivo; al abrirlo se calculan el gráfico y una frase con su posición relativa.

## Estudio A-08 · Respuestas con gráfico (21-nov)

- `graficos.automatico(resultado)` recibe el resultado de cualquier consulta de `sql_seguro` y elige el gráfico:
  - **Con columna `anio`:** barras agrupadas por año, una serie por fuente y tipo, con **recuentos** de contratos o concesiones. Los importes de cada fuente tienen distinta base y no saldrían todas.
  - **Sin `anio`:** ranking en barras horizontales, de las 12 primeras filas. Se usa la primera columna de texto que sirva de etiqueta y la primera columna numérica relevante (proporción, modificaciones, importe o recuento). La primera barra va en azul. Si un nombre sale una vez por fuente, se añade la fuente.
- Devuelve además una frase resumen («En primer lugar: X, con Y»).
- «Preguntas guiadas»: frase y gráfico arriba; la tabla con los enlaces debajo, siempre visible; la nota de qué cubre la respuesta, en pequeño.
- Pensado para reutilizarlo en el asistente cuando responda con una consulta libre.

## Revisión A-10 (21-nov)

- **Contraste (WCAG 2.1) sobre el fondo `#0B1120`, la tarjeta `#131C2E` y la barra lateral `#0E1626`:**

  | Color | Fondo | Tarjeta | Barra lateral | Resultado |
  | --- | --- | --- | --- | --- |
  | Texto `#E7ECF3` | 15,9:1 | 14,3:1 | 15,2:1 | AA |
  | Secundario `#93A1B8` | 7,2:1 | 6,5:1 | 6,9:1 | AA |
  | Azul `#3D8BFD` | 5,7:1 | 5,1:1 | 5,4:1 | AA |
  | Enlaces `#7DB3FF` | 8,8:1 | 7,9:1 | 8,4:1 | AA |
  | Ámbar `#F2B544` | 10,3:1 | 9,3:1 | 9,9:1 | AA |
  | Gris de las barras de contexto | 2,7:1 | — | — | **Fallaba** el 3:1 para gráficos (1.4.11) |

  El gris de las barras se ha cambiado a `#5B6B86`, que da 3,5:1 sobre el fondo y 3,2:1 sobre la tarjeta.
- **El color no es la única pista:**
  - en E-01, «Este contrato» lleva además una etiqueta;
  - en E-03 y E-07, este contrato se distingue por color y tamaño;
  - las señales aparecen siempre con su nombre;
  - las leyendas tienen texto.
- **Texto alternativo:** cada gráfico de señal va con una frase con las mismas cifras. Los de las fichas llevan un texto que explica cómo leerlos.
- **Teclado:** el organismo del mapa también se elige con un desplegable, no solo con la lista o el ratón.
- **Pendiente para la pasada final:**
  - probar en el móvil (las columnas de Streamlit se apilan);
  - revisar la longitud de los textos de las fichas;
  - comprobar el contraste del gris de `:gray[…]` en la versión desplegada.

## Guion de la prueba A-11

Con 2 o 3 personas que no conozcan el proyecto, sin explicarles nada antes. Unos 10 minutos con cada una. Anotar lo que dicen, no lo que pensamos que quieren decir.

1. Abrir la portada: «¿Qué crees que es esta web y para qué sirve?» (debería entenderse en 30 s).
2. «¿Qué crees que significa que un contrato tenga una señal?» Comprobar que no lo entienden como «es corrupto».
3. «Busca qué contratos tiene la empresa X» (por ejemplo, una que conozcan). ¿Llegan solos a la ficha de empresa?
4. En «Contratos a revisar», abrir un contrato: «¿Por qué crees que aparece aquí?» ¿Entienden el gráfico de cada señal?
5. En el mapa del dinero: «¿A qué empresa adjudica más dinero el Metro de Madrid?»
6. «¿Qué palabra o parte no has entendido?»

Resultado: una entrada de bitácora con lo que no se entendió y los cambios que se hacen por ello.

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
