# 2026-11-21 · Contratos atípicos visuales (D-023, A-04)

- **Autor:** Claude (agente)
- **Fase del plan:** 2. Tarea A-04 de `docs/11-accesibilidad.md` (estudio E-07).
- **Rama:** `feat/accesibilidad-atipicos`

## Qué se hizo
- `anomalias.deteccion.calcular` guarda también la tabla derivada `anomalia_variables`. La base local está regenerada.
- `datos.pares_anomalia`: este contrato y una muestra fija de 1.500 contratos de su grupo. Al principio salían muy pocos puntos porque `USING SAMPLE` se aplica antes del `WHERE`; se ha corregido con una subconsulta.
- `graficos.atipico`:
  - nube de puntos (dos variables) o histograma (una);
  - ejes en lenguaje llano;
  - escala logarítmica cuando hace falta;
  - porcentajes recortados a los percentiles 1-99, sin dejar fuera nunca a este contrato.
- `paginas/atipicos.py`: desplegables con el motivo; al abrirlos, el gráfico y la posición relativa.
- Tests.

## Decisiones tomadas
- Ninguna nueva.

## Siguiente paso
- A-08 (preguntas guiadas y asistente con gráfico), A-09 (glosario), A-10 (revisión de accesibilidad) y A-11 (prueba con personas no expertas).
