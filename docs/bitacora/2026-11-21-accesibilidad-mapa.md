# 2026-11-21 · Mapa del dinero en burbujas (D-023, A-07)

- **Autor:** Claude (agente)
- **Fase del plan:** 2. Tarea A-07 de `docs/11-accesibilidad.md`.
- **Rama:** `feat/accesibilidad-mapa`

## Qué se hizo
- Estudio A-07 anotado en `docs/11`.
- `paginas/mapa.py` rehecha en dos pasos:
  - Vista general: burbujas de los 15 organismos que más adjudican, con una lista numerada en la que se puede pulsar cada uno.
  - Red de un organismo: sus 10 empresas, con los contratos o convocatorias de la elegida.
  - El diagrama de flujos queda como vista avanzada.
- `datos.totales_organos`, y filtro `organo_id` en `datos.flujos` y `datos.flujos_subvenciones`.
- `graficos.empaquetar`, `burbujas_organismos`, `red_organismo` y `flujos_sankey` (este último sacado de la pantalla).
- Los botones de la lista usan `on_click`: Streamlit no deja cambiar un desplegable ya dibujado en la misma ejecución.
- Tests: no hay solapes al empaquetar y las consultas del mapa funcionan.

## Decisiones tomadas
- Ninguna nueva.

## Siguiente paso
- A-04 (contratos atípicos), A-08 (preguntas guiadas y asistente), A-10 y A-11.
