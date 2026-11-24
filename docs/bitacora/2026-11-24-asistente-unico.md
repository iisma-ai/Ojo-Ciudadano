# 2026-11-24 · Un solo asistente: respuestas preparadas, modelo de respaldo y animaciones (D-037)

**Quién:** El Harrak, con Claude (agente). **Rama:** `feat/asistente-unico`, que sale de `feat/datos-nuevos-modelos`.

## Contexto
El Harrak pidió juntar en una sola pantalla las preguntas guiadas (SQL verificado) y el asistente con modelo (SQL y RAG):
- que lo preguntable con los datos que hay esté resuelto de antemano;
- que el modelo elegido conteste el resto;
- que se vea una animación de la consulta mientras se ejecuta y la respuesta escribiéndose;
- que, si no hacen falta datos, solo se escriba el texto.

## Qué se hizo
- `asistente/respuestas_fijas.py`: 43 respuestas preparadas.
  - **26 de datos:** las preguntas de datos de la batería y de las antiguas preguntas guiadas, más 5 nuevas.
  - **17 de texto:** conceptos y límites.
  - Se reconocen por palabras clave, con exclusiones, y leen de la pregunta el año, la consejería o la empresa.
  - Lo que no reconocen pasa al modelo.
- `asistente/plano.py`: tablas, uniones con su clave y pasos de un SQL, sacados del árbol de DuckDB.
- `app/animacion.py`: animación de la consulta, de los documentos, del modelo pensando y de la escritura. Solo CSS.
- `agente.responder(..., al_usar=...)`: avisa de cada herramienta antes de usarla, y un fallo de la animación no rompe la respuesta.
- `app/paginas/asistente.py`:
  - orden de respuesta: DNI, luego respuesta preparada, luego modelo;
  - lista de preguntas preparadas por grupos, sugerencias al empezar, nota de qué pregunta se reconoció y botón «que responda el modelo».
- Se quita «Preguntas guiadas» (`app/paginas/preguntas.py`) del menú y del código.
- **Al probar el reconocimiento se corrigieron:**
  - el presupuesto de la UE, que se tomaba por la empresa «UNION 50 S.L.»;
  - los contratos de ambulancias, que se tomaban por el recuento por fuente;
  - textos que el filtro de lenguaje marcaba («tamaño» contiene «amañ»; «irregular» lejos de la negación).

## Comprobaciones
- **Tests:** 444, todos bien (366 al empezar). Hay nuevos de reconocimiento, SQL, textos, plano, animaciones y el aviso del agente.
- `ruff` sin avisos.
- **Pantalla sin navegador (AppTest) con la base real:** respuesta preparada con su nota, concepto sin consulta y pregunta de pliego contestada por el modelo (unos céntimos).
- **En el navegador:** se ve la animación de la consulta (tablas, uniones y pasos) y la respuesta escribiéndose.
- Revisión de `revisor-legal` de los textos nuevos.

## Siguiente paso
- **Orden de fusión:** `feat/cpv-invente`, `feat/datos-nuevos-modelos` y `feat/asistente-unico`.
- Si en la demo aparece una forma de preguntar que no se reconoce, añadir sus palabras clave con un test.
