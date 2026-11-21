# 2026-11-21 · Batería de 20 preguntas de prueba del asistente

- **Autor:** Claude (agente), a petición de Ignacio
- **Fase del plan:** 2. Entregable de la persona 4 (asistente): «batería de 20 preguntas de prueba con respuesta esperada» (docs/05-asistente.md).
- **Rama:** `feat/bateria-preguntas`

## Qué se hizo
- Nuevo `src/ojo_ciudadano/asistente/bateria.py` con 20 preguntas (`BATERIA`):
  - **B-01 a B-04**: las 4 de demo, reutilizando `consultas_demo.py` con parámetros fijos (consejería «Sanidad»; empresa A80364243, CLECE S.A., que tiene contratos y subvenciones).
  - **B-05 a B-16**: preguntas de datos nuevas con SQL de referencia. Cubren recuentos por fuente y año, ranking de órganos en PLACSP, R-01 por año, empresas y órganos con más alertas, R-03 por consejería, mayores obras, convocatorias de la BDNS, entidades con contratos y subvenciones, R-06 por órgano, R-04 y menores por mes en 2026.
  - **B-17 a B-20**: preguntas sobre los límites, sin SQL. Son lenguaje acusatorio («¿qué empresas son corruptas?»), DNI de autónomos (D-007), Ayuntamiento de Madrid (fuera de alcance) e inyección («borra la tabla»).
- Cada pregunta lleva **criterios** de lo que debe decir una buena respuesta (avisos de IVA, P-12, legalidad de los procedimientos…).
- La respuesta esperada **es el resultado de la referencia sobre la base del día**. No se fijan cifras porque cambian al regenerar la base.
- `evaluar(con, pregunta, sql_modelo, texto)` compara el resultado del SQL del modelo con el de la referencia. Para cada columna clave, alguna columna del modelo debe tener los mismos valores en las primeras filas, sin importar el nombre ni el orden de las columnas.
- `revisar_texto` marca para revisión manual los términos de la tabla de lenguaje de docs/07 y cualquier DNI o NIE que aparezca.
- `uv run python -m ojo_ciudadano.asistente.bateria` ejecuta las 16 referencias sobre la base real: todas por debajo de 1 s y dentro del límite de 20 s del validador.
- Tests en `tests/asistente/test_bateria.py`, con datos sintéticos. Comprueban que las referencias pasan el validador y llevan `fuente`, la lógica de `coincide`, `revisar_texto` y `evaluar`. La suite completa queda en 193 tests en verde.

## Decisiones tomadas
- Ninguna. D-010 (proveedor de LLM) sigue abierta: Ignacio prefirió avanzar primero con la batería.

## Desviaciones del plan
- Ninguna.

## Problemas y hallazgos
- **Las licitaciones del portal regional casi nunca traen fecha**: solo 344 de 18.777 contratos no menores tienen `fecha_contrato`. Por eso B-11 (mayores obras de 2024) se hizo sobre PLACSP, con su fecha de formalización. Cualquier pregunta por año sobre licitaciones del portal se queda corta, y el asistente debe decirlo (está en los criterios de B-05 y B-11).
- R-06 tiene bajas de casi el 100 % y bajas negativas de miles por cien, que son probables errores del importe publicado. Por eso B-14 agrega por órgano en vez de listar contratos.
- La primera versión de B-05 combinaba `GROUP BY ALL` con `HAVING` sobre un alias y devolvía filas duplicadas (200 en vez de 8). Se corrigió con una CTE y `GROUP BY 1, 2`. Conviene evitar ese patrón en los ejemplos que se den al modelo.
- `anomalia_resultado` (D-021) no está en `TABLAS_PERMITIDAS` de `sql_seguro.py`, así que el asistente no puede consultar los contratos atípicos. No se ha tocado porque es la línea de Ismael y hay que decidir si se quiere exponer.

## Siguiente paso
- Cerrar D-010 (proveedor y modelo) y conectar el modelo. Después, pasar la batería con `evaluar` y anotar los aciertos en docs/05.
- Decidir con Ismael si `anomalia_resultado` entra en `TABLAS_PERMITIDAS`.
- PR a `main`.
