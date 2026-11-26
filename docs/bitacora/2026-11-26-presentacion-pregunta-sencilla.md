# 2026-11-26 · Presentación: pregunta sencilla en el asistente y guion de Isma

## Qué se ha hecho

- **Diapositiva 7, tercera pregunta.** La pregunta sobre los recursos ante el Tribunal (tarta) se cambia por una
  pregunta de alguien que no sabe nada del tema: «Oye, ¿es verdad que la Comunidad de Madrid tiene helicópteros?».
  La idea es enseñar que no hace falta saber de contratación para preguntar.
- **Corrección a petición de Isma:** la pregunta que se quita es la de los organismos con más importe en 2025 (barras),
  no la del Tribunal. Orden final: 1) licitador único por año (barras), 2) recursos ante el Tribunal por acto
  recurrido (tarta), 3) helicópteros. La tarta compara tipos de acto recurrido, no organismos.
- **Cifras de la respuesta**, sacadas con la búsqueda por palabras en los títulos (`asistente/texto.py`,
  consulta «helicoptero», base del 16-nov):
  - 12 contratos: 4 licitaciones de la Plataforma de Contratación, con 52,8 M€ sin IVA, y 8 contratos del portal
    regional, con 2,6 M€ con IVA. Las dos cifras no se suman.
  - Son servicios de helicóptero de rescate, extinción de incendios y asistencia sanitaria del SUMMA 112, y
    lo que necesitan (por ejemplo, el prefabricado de la base de Las Rozas).
- **Diapositiva 4, el flujo del dinero** (a petición de Isma):
  - arriba, los tres capítulos de ingresos de 2025 que más aportan, con «de cada 100 €» como en la web
    (`app/de_donde_viene.py`): impuestos directos 49 (18.714 M€), indirectos 39 (15.063 M€) y préstamos 9
    (3.445 M€). Ingresos consolidados liquidados del catálogo de datos abiertos, descargados el 23-nov;
  - los enlaces van de los ingresos a la Comunidad y, en un paso nuevo, de la Comunidad a las consejerías: el
    pulso de luz del enlace va de `de` a `a`, así que el dinero baja;
  - de siete consejerías se pasa a las cuatro mayores (Sanidad, Educación, Vivienda y Transportes, Deuda pública)
    para que se lea mejor. Sanidad y sus contratos bajan a la parte de abajo; los pasos de Sanidad, sus contratos y la
    vacuna se retrasan uno;
  - el Estado no sale como fuente propia: en el consolidado, las transferencias corrientes de 2025 son un saldo
    negativo (−6.118 M€), porque se restan las aportaciones al sistema de financiación (D-054). El IRPF y el IVA
    son tributos cedidos por el Estado dentro de ese sistema.
- **Diapositiva 4, sin la vacuna del papiloma** (a petición de Isma): se quita el paso que entraba en ese contrato y
  su ficha. Alrededor de Sanidad quedan seis ejemplos sueltos con nombre corto, que se explican de palabra:
  - licitaciones de la Plataforma: protonterapia (13,7 M€), obras del Clínico (17,1 M€), vacuna de la gripe
    (17,2 M€) y terapias respiratorias (107,4 M€), sin IVA;
  - un contrato menor: café del Hospital Universitario La Paz, 2.860 € con IVA (23-ene-2025). Los órganos de
    Sanidad firmaron 330.085 menores en 2025, unos 900 al día, en 39 hospitales (consulta sobre `contrato_unico`);
  - una subvención: AECC, cuidados paliativos 2025, 0,6 M€ (BDNS).
- **Periodo de los datos** para el guion: 1.354.441 contratos (licitaciones de la Plataforma y del portal y menores
  de enero de 2023 a septiembre de 2026) y 872.821 concesiones de subvenciones (de enero de 2023 a noviembre de 2026).
- **Diapositiva 5:** debajo de los 1.354.441 contratos, más pequeña (`tam: 24`), la cifra de 872.821 subvenciones;
  la de contratos sube de `y: 540` a `y: 430`. `DATOS.subvenciones` pasa de 863.510 a 872.821, lo que hay en la base.
- **Diapositiva 7, pregunta 1** (a petición de Isma): la del licitador único por año se cambia por la de los
  organismos con más importe adjudicado en la Plataforma en 2025 (barras). Orden final: 1) organismos, 2) recursos
  ante el Tribunal (tarta), 3) helicópteros.
- **Diapositiva 6, señales y atípicos** (a petición de Isma), en cuatro pasos: 0) solo burbujas, algunas en ámbar,
  sin texto; 1) «6 señales» con las tres cifras de cada 100; 2) el contrato atípico; 3) resumen con «Señales» a un
  lado, «Atípicos» al otro y debajo «No son acusaciones». Fuera el título «Señales, no acusaciones».
- **Diapositiva 6, paso del atípico:** panel solo con dos puntos, «Aprende de las cifras» y «Destaca lo que se sale de
  lo habitual», a la izquierda de la burbuja del atípico. La `x` de un panel es su borde izquierdo: el primer intento
  (x 620, ancho 640) llegaba hasta la burbuja. En `escena3d.js`, una lista de señales con `titulo: ""` ya no pinta la
  cabecera «Señales». Después, a petición de Isma, las dos frases van como texto suelto, sin puntos ni cabecera,
  a 32 en lugar de 26 y con más espacio entre ellas (regla nueva en `estilo.css`, solo para paneles que no son el chat).
- `presentacion/README.md`: actualizadas las filas de las escenas 4, 6 y 7.
- **Guion de Isma (diapositivas 4 a 7)** reescrito en la conversación con la estructura que pidió: de dónde viene y a
  dónde va el dinero, el volumen de los datos, las señales y los atípicos (Isolation Forest), el asistente
  («no hace falta saber para preguntar») y la vuelta a la alegoría del mar. No se guarda en el repositorio.
- Se aclaró con Isma que los indicadores son reglas fijas en SQL, con umbrales de la LCSP (R-02, R-03 y R-05) o de la
  literatura (R-01, R-04 y R-06), y que no se validaron con casos reales: el guion no debe decir que detectan
  «casos que ya resultaron fraudulentos».

## Pendiente

- Probar las diapositivas 4 y 7 en el ordenador de la demo (no se ha podido ver en un navegador desde esta sesión).
- El QR de la escena 8 sigue sin dirección (`DATOS.urlApp`).

## Siguiente paso

Fusionar la rama `feat/presentacion-pregunta-sencilla` en `main` antes de presentar.
