# 2026-11-21 · El asistente puede consultar los contratos atípicos

- **Autor:** Claude (agente)
- **Fase del plan:** 2
- **Rama:** `feat/asistente-anomalias`

## Qué se hizo
- Respuesta a lo que quedó abierto en `2026-11-21-bateria-preguntas.md`: `anomalia_resultado` (D-021) entra en `TABLAS_PERMITIDAS` de `sql_seguro.py`. Es una tabla derivada sin datos personales: lleva `contrato_id`, grupo, percentil, motivo y enlace.
- Nueva regla de respuesta en `docs/05`: si el asistente usa esta tabla, presenta los contratos como «atípicos respecto a contratos similares», como señal experimental que no suma a la puntuación y aclarando que atípico no significa irregular. Hay que incluirla en las instrucciones del modelo al cerrar D-010.
- Test de que la consulta pasa el validador.

## Decisiones tomadas
- Ninguna nueva (aplicación de D-021).

## Siguiente paso
- Incluir la regla en el prompt del modelo cuando se conecte (D-010).
