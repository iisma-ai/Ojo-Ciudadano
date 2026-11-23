# 2026-11-23 · Datos de D-027 a D-029 en anomalías, asistente y búsqueda (D-031)

- **Autor:** Claude (agente), a petición de El Harrak («integra los datos nuevos… si ya está hecho no lo hagas»)
- **Fase del plan:** 2, víspera del H3

## Qué estaba hecho y qué no
| Parte | Fondos UE (D-027), encargos (D-028) y recursos TACPCM (D-029) |
| --- | --- |
| Web (fichas, «Presupuesto y contexto») | Ya estaba (PR #9): no se ha tocado |
| SQL del asistente (lista permitida y descripciones) | Ya estaba: no se ha tocado |
| Detección de anomalías | Faltaba: hecho |
| Búsqueda por palabras | Faltaban los encargos: hecho |
| Batería del asistente | Faltaban preguntas: B-28 a B-30 |

## Qué se hizo
- **Datos:**
  - Descargado el listado del TACPCM (`ingesta.tacp`).
  - Regenerada la base: carga, indicadores, anomalías y `asistente.texto`. Cargadas 1.097 resoluciones (6 enlazadas a un contrato) y los fondos europeos de PLACSP.
  - **Encargos: no cargados.** El CSV se exporta a mano por el captcha y no estaba en esta máquina.
- **Anomalías (D-031, Propuesta):**
  - encargos como grupo de pares propio (`anomalia_encargo`);
  - recursos y fondos UE solo para validar o describir (`anomalia_validacion`), nunca como variables.
- **Asistente:**
  - las dos tablas nuevas en la lista permitida, con sus reglas;
  - `buscar_texto` con `en = "encargo"`;
  - B-28 a B-30, con el modelo real: B-28 y B-30 bien; B-29 no se pudo probar sin encargos.
- **Web:** dos desplegables nuevos en «Contratos atípicos», probados con `streamlit.testing` sobre la base real, sin errores.
- **Tests:** de 305 a 315.

## Resultados
- **Validación con recursos: sin casos útiles.** Solo 6 de 1.097 resoluciones casan con un contrato (limitación conocida de D-029), y solo 1 con un contrato puntuado.
- **Fondos europeos:**
  - con fondos UE, 1,19 % de atípicos (10 de 843) y puntuación media 0,166;
  - sin fondos UE, 0,94 % (111 de 11.782) y 0,182.
  - No hay diferencia apreciable.
- **B-30:** el modelo separó bien las 7 resoluciones con dos actos o dos resultados unidos. La referencia se ha corregido para hacer lo mismo, y había además un fallo mío: `ILIKE '%Estimatoria%'` también contaba «Desestimatoria».
- **Gasto de la clave:** unos 0,67 USD.

## Revisión de `revisor-legal`, aplicada
- **Tabla de validación:**
  - cita las fuentes con su fecha (TACPCM y PLACSP);
  - el aviso dice cuántos contratos con recurso estimado hay enlazados, y que un recurso estimado no dice nada de la empresa;
  - los grupos con menos de 30 contratos muestran «— (muy pocos casos)»;
  - la columna pasa a llamarse «Puntuación de riesgo media (indicadores)».
- **Motivo de los encargos:** ya no puede empezar por «Cuota del adjudicatario…» cuando la cuota es la primera variable. Lleva test.
- **Asistente:** la regla de `anomalia_validacion` aclara qué es un recurso estimado (no es una sanción) y pide las fuentes con su fecha; el criterio de B-30 dice lo mismo.

## Decisiones tomadas
- D-031, en Propuesta.

## Siguiente paso
- **Exportar a mano el CSV de encargos** a `data/raw/encargos/`, regenerar la base y pasar B-29.
- **Para que la validación con recursos sirva,** enlazar más resoluciones con su contrato leyendo los PDF del TACPCM. Es el bloque C del RAG y la línea futura de D-029, y necesita revisión legal.
- **Fusionar en `main`** cuando el equipo lo apruebe.
