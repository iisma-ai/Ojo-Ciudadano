# 2026-11-20 · Asistente: SQL seguro y preguntas de demo (sin LLM)

- **Autor:** Claude (agente), a petición de Ignacio
- **Fase del plan:** 2 · Construcción en paralelo (entregable de la persona 4, asistente)

## Qué se hizo
- Rama `feat/asistente-sql` desde `origin/main`. Nadie había empezado el asistente. D-010 solo bloquea las dependencias del LLM, así que se ha hecho todo lo que no depende de él. No se añade ninguna dependencia.
- `asistente/sql_seguro.py`:
  - `validar` admite una sola sentencia `SELECT` (`extract_statements`) y recorre el árbol de `json_serialize_sql`. Lista blanca de tablas (`TABLAS_PERMITIDAS`; `contrato_unico`, no `contrato`) y de tipos de referencia (tabla, join, subconsulta, `VALUES`). Rechaza funciones de tabla, `SHOW`/`DESCRIBE`/`SUMMARIZE`, otros esquemas y funciones como `getenv` o `current_setting`.
  - `conexion_lectura` abre la base en solo lectura y con `enable_external_access = false`, que DuckDB no deja reactivar mientras la base está abierta.
  - `ejecutar` limita a 200 filas y 20 s (`con.interrupt`), sustituye los `PF-…` y devuelve siempre el SQL usado.
- `asistente/consultas_demo.py`: consultas verificadas para las 4 preguntas de demo, con una nota de alcance cada una. Tardan menos de 1 s sobre la base real.
- Pantalla **«Preguntas guiadas»** (`app/paginas/preguntas.py`): tabla, nota, consulta SQL y enlace al portal oficial. Es también la respuesta de respaldo para la demo.
- `app/conexion.py` usa ahora `conexion_lectura` para toda la interfaz. Las otras cuatro pantallas siguen funcionando.
- Revisión con `revisor-legal`, aplicada:
  - personas físicas y NIF no verificables (`otro`) agregados en la pregunta 1 y excluidos en la 4;
  - alias `*_alerta_r02` en lugar de «sin publicidad»;
  - la pregunta 3 ya no dice «sobrecoste» y lleva una columna `importe_a_comprobar`;
  - fuente con su nombre y `fecha_descarga` en todas;
  - enlace «Ver en el portal oficial».
- 125 tests y `ruff` en verde. Los tests cubren 6 consultas permitidas, 19 rechazadas, la conexión sin ficheros, el límite y los seudónimos, y las 4 consultas de demo con datos sintéticos.

## Decisiones tomadas
- Ninguna nueva. La arquitectura es la de `docs/05-asistente.md`; D-010 sigue abierta.

## Desviaciones del plan
- Ninguna. La pantalla «Preguntas guiadas» es el plan de contingencia de la demo («respuestas cacheadas») del doc 05.

## Problemas y hallazgos
- En R-05, el contrato con más peso de las modificaciones da un 576.190 % (5.761 veces el adjudicado). Casi seguro es un error del importe publicado. La pregunta 3 deja al final los casos de más del 1.000 % y los marca.
- La pregunta 2 da proporciones muy altas en algunos órganos (90 % del importe de la Consejería de Economía, Hacienda y Empleo en el portal). Conviene revisarlas antes de la demo.
- Al tratar como persona el tipo `otro` (NIF extranjero o mal escrito), las empresas extranjeras quedan agregadas en la pregunta 1 y no se encuentran en la 4. Prima D-007.

## Siguiente paso
- **Cerrar D-010 con el equipo** (proveedor y modelo). Después: prompt con el esquema y estas 4 consultas como ejemplos, bucle de reintento con el mensaje de `SQLNoPermitido` y el campo de pregunta libre en la pantalla.
- Batería de 20 preguntas con respuesta esperada.
- Integrar esta rama y `fix/pendientes-revision-legal` en `main` (son independientes).
