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
- `presentacion/README.md`: actualizadas las filas de las escenas 4 y 7.
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
