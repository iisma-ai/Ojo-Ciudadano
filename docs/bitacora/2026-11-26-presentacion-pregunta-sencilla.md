# 2026-11-26 · Presentación: pregunta sencilla en el asistente y guion de Isma

## Qué se ha hecho

- **Diapositiva 7, tercera pregunta.** La pregunta sobre los recursos ante el Tribunal (tarta) se cambia por una
  pregunta de alguien que no sabe nada del tema: «Oye, ¿es verdad que la Comunidad de Madrid tiene helicópteros?».
  La idea es enseñar que no hace falta saber de contratación para preguntar. Las preguntas 1 y 2 no cambian.
- **Cifras de la respuesta**, sacadas con la búsqueda por palabras en los títulos (`asistente/texto.py`,
  consulta «helicoptero», base del 16-nov):
  - 12 contratos: 4 licitaciones de la Plataforma de Contratación, con 52,8 M€ sin IVA, y 8 contratos del portal
    regional, con 2,6 M€ con IVA. Las dos cifras no se suman.
  - Son servicios de helicóptero de rescate, extinción de incendios y asistencia sanitaria del SUMMA 112, y
    lo que necesitan (por ejemplo, el prefabricado de la base de Las Rozas).
- `presentacion/README.md`: actualizada la fila de la escena 7.
- **Guion de Isma (diapositivas 4 a 7)** reescrito en la conversación con la estructura que pidió: de dónde viene y a
  dónde va el dinero, el volumen de los datos, las señales y los atípicos (Isolation Forest), el asistente
  («no hace falta saber para preguntar») y la vuelta a la alegoría del mar. No se guarda en el repositorio.
- Se aclaró con Isma que los indicadores son reglas fijas en SQL, con umbrales de la LCSP (R-02, R-03 y R-05) o de la
  literatura (R-01, R-04 y R-06), y que no se validaron con casos reales: el guion no debe decir que detectan
  «casos que ya resultaron fraudulentos».

## Pendiente

- Probar la diapositiva 7 en el ordenador de la demo (no se ha podido ver en un navegador desde esta sesión).
- El QR de la escena 8 sigue sin dirección (`DATOS.urlApp`).

## Siguiente paso

Fusionar la rama `feat/presentacion-pregunta-sencilla` en `main` antes de presentar.
