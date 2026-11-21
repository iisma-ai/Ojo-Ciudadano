# 2026-11-21 · Ficha de organismo visual (D-023, A-06)

- **Autor:** Claude (agente)
- **Fase del plan:** 2. Tarea A-06 de `docs/11-accesibilidad.md`.
- **Rama:** `feat/accesibilidad-organo`

## Qué se hizo
- Estudio A-06 anotado en `docs/11`.
- `paginas/organo.py` rehecha:
  - cifras;
  - «A quién adjudica»: mapa de áreas de las 20 empresas con más importe por fuente, con las personas físicas agregadas en gris;
  - «Comparado con los demás»: un punto por señal;
  - «Cómo contrata»: vías de adjudicación con nombres llanos;
  - contratos por año;
  - sus 20 contratos con más señales en tarjetas desplegables;
  - subvenciones en un desplegable.
- Nuevo: `datos.reparto_organo` (por fuente, sin mezclar IVA, con personas agregadas) y el filtro `organo_id` en `datos.alertas`.
- Nuevo: `graficos.comparacion_senales` y `graficos.procedimientos`. `reparto_organismos` sirve ahora para organismos y para empresas.
- Nuevo: `textos.PROCEDIMIENTO_LLANO`, y `textos.euros` escribe «mil millones».
- Tests en `tests/app/test_visual.py`.

## Decisiones tomadas
- Ninguna nueva.

## Siguiente paso
- A-07 (mapa del dinero como red de burbujas) y A-04 (contratos atípicos).
