# 2026-11-21 · Batería de 20 preguntas del asistente

- **Autor:** Claude (agente), a petición de Lucas
- **Fase del plan:** 2. Entregable de la persona 4 (asistente), parte sin LLM.
- **Rama:** `feat/bateria-asistente`

## Qué se hizo
- `src/ojo_ciudadano/asistente/bateria.py` con las 20 preguntas de prueba que pedía `docs/05` (B01–B20):
  - recuentos por fuente y año;
  - rankings de órganos, empresas y convocatorias;
  - indicadores R-01, R-05 y R-06;
  - puntuaciones de riesgo;
  - subvenciones, con la parte que va a personas físicas solo agregada;
  - empresas con contratos y subvenciones;
  - un órgano concreto con parámetro;
  - dos preguntas sin respuesta posible.
- Cada pregunta lleva su consulta de referencia, las columnas clave que deciden si una respuesta es correcta y una nota de lo que la respuesta debe matizar (IVA, P-12, D-007, «no es una irregularidad»).
- `evaluar()` compara el SQL que genere el modelo con la referencia:
  - pasan los dos por `sql_seguro`;
  - se comparan por columnas clave, con tolerancia numérica;
  - se acepta una proporción o un porcentaje;
  - en los rankings basta con el 80 % de las filas.
- Tests en `tests/asistente/test_bateria.py`: todas las referencias pasan el validador y se evalúan como correctas; además, casos de SQL equivalente, SQL erróneo, SQL prohibido y preguntas sin respuesta.

## Decisiones tomadas
- Ninguna. No añade dependencias ni elige proveedor de LLM (D-010 sigue abierta).

## Desviaciones del plan
- Ninguna.

## Problemas y hallazgos
- Las personas físicas se filtran en las referencias con `tipo_persona` y, además, con `NOT contains(adjudicatario_id, 'PF-')`, por las UTE con personas físicas de bases antiguas (ver `2026-11-21-ute-personas-fisicas.md`).

## Siguiente paso
- Cuando se cierre D-010, pasar la batería al modelo y anotar el porcentaje de aciertos en `docs/05`.
