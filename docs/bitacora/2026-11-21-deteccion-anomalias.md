# 2026-11-21 · Detección de contratos atípicos (D-021)

- **Autor:** Claude (agente), a petición de Lucas
- **Fase del plan:** 2. Entregable de D-021, previsto para el 23-nov y adelantado.
- **Rama:** `feat/anomalias`

## Qué se hizo
- Nueva dependencia: `uv add scikit-learn` (1.9.1). Es para el Isolation Forest y ya estaba prevista en D-021.
- `src/ojo_ciudadano/anomalias/deteccion.py` detecta contratos atípicos así:
  - Los compara con contratos similares: misma fuente, misma modalidad (licitación o menor) y mismo tipo de contrato.
  - Usa variables que ya estaban en la base:
    - importe;
    - número de ofertas;
    - baja;
    - modificaciones;
    - cuota del adjudicatario en el órgano;
    - número de menores en 12 meses.
  - Aplica un Isolation Forest por grupo (semilla fija) y marca como atípico el 1 % de cada grupo.
  - Explica cada caso con las variables que más lo alejan de la mediana de su grupo.
  - Guarda el resultado en la tabla derivada `anomalia_resultado`. No se toca el esquema congelado ni la puntuación.
  - Se ejecuta con `uv run python -m ojo_ciudadano.anomalias.deteccion`, unos 45 s después del ejecutor de indicadores.
- Interfaz:
  - Pantalla nueva «Contratos atípicos», con filtro por grupo, aviso de método y enlace al expediente.
  - Los contratos de personas físicas solo se cuentan.
  - En el panel de alertas, una línea en los contratos que además son atípicos.
- Tests: `tests/anomalias/test_deteccion.py` (8) y 2 nuevos en `tests/app/test_datos.py`. Todos con datos sintéticos.
- Revisado con `revisor-legal`; todas las propuestas aplicadas:
  - importes con «sin IVA» o «con IVA»;
  - un motivo con cifras también cuando ninguna variable es extrema;
  - la aclaración de que atípico no es irregular, también en el panel de alertas;
  - nombres legibles de los grupos;
  - aviso de que un contrato no listado no queda avalado;
  - aviso del corte a 100.
- La base local se ha regenerado con BDNS: 863.510 concesiones, 1.371.693 contratos. Las cifras de los indicadores no cambian.

## Resultados (base del 21-nov)
- 1.349.510 contratos puntuados en 14 grupos; **13.496 atípicos (1,0 %)**.
- El 76 % de los atípicos no tiene ningún indicador de riesgo activado: la señal añade casos que las reglas no ven.
- 27 contratos atípicos son de personas físicas (D-007). Además, la interfaz agrupa 42 por NIF con forma de DNI o NIE.
- Hay 23 contratos adjudicados por más del doble de su presupuesto. El motivo los marca como «posible error en los datos de la fuente».

## Decisiones tomadas
- Ninguna nueva: es la implementación de D-021, con sus parámetros en el código y en `docs/04`.

## Desviaciones del plan
- Ninguna. Se adelanta el entregable del 23-nov y se asigna como responsable a Lucas, con Claude.

## Problemas y hallazgos
- En los menores domina el número de pedidos del mismo proveedor al mismo hospital, con miles al año. Es el patrón que ya llevó a D-015 en R-03 y suele tener explicación legítima.
- Hay licitaciones de obras con modificaciones del 100 % del importe o con presupuestos 100 veces menores que el importe. Es probable que sean errores de la fuente.
- La revisión legal señaló un riesgo que ya existía y que afecta a toda la interfaz: una UTE con un autónomo como miembro podría mostrar su nombre en el de la UTE. No se ha cambiado aquí. Hay que revisarlo en la normalización (miembros de UTE).

## Siguiente paso
- Validar los atípicos con casos de la Cámara de Cuentas antes de pensar en meterlos en la puntuación.
- Revisar los nombres de UTE con personas físicas.
- PR a `main`.
