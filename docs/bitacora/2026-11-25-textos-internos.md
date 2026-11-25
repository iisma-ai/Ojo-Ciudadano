# 2026-11-25 · La web sin referencias al desarrollo del proyecto

- **Quién:** El Harrak con Claude (agente)
- **Rama:** `fix/textos-internos` (sale de `main` en `3127340`)

## Qué se ha hecho

Revisión de todo el texto que ve el usuario. Se busca en el código y luego en el navegador, pantalla por pantalla, con los desplegables cerrados incluidos. Se quitan los códigos internos (R-0x, D-0xx, P-xx), las rutas de `docs/`, los comandos `uv run`, las menciones al equipo y la palabra «base» con sentido técnico.

- **Textos fijos** (`app/textos.py`):
  - el aviso legal ya no remite a `docs/04-indicadores-riesgo.md`;
  - el de atípicos, sin `docs/` ni D-021;
  - el de contexto, sin `docs/02-fuentes-datos.md`;
  - la lista de metodología del pie nombra cada señal sin «R-01 ·».
- **Mensajes de datos que faltan** (atípicos, contexto, encargos, recursos, mapa del dinero, catálogo, pliegos, resoluciones y búsqueda por palabras): decían qué comando ejecutar. Ahora dicen que esos datos «no están disponibles todavía en esta versión de la web».
- **Asistente:**
  - las preguntas de ejemplo ya no dicen «¿Qué mide el indicador R-01 (…)?», sino «¿Qué mide la señal «Una sola oferta»?»;
  - las preguntas de demostración y sus explicaciones, sin «(R-02)» ni «(indicador R-05)»;
  - «revisada por el equipo» pasa a «comprobada de antemano»;
  - las fuentes de algunas respuestas, sin «R-01 a R-06» ni «D-021»;
  - las descripciones de tablas que lee el modelo, sin códigos de decisión.
- **Lo que escribe el modelo:** las instrucciones le piden nombrar cada indicador con código y nombre, y la comprobación de cifras usa ese código. Para no tocar esa seguridad, se limpia justo antes de enseñarlo con `textos.sin_codigos`:
  - «R-02 (Procedimiento sin publicidad)» pasa al nombre;
  - «(señal R-01)» desaparece;
  - un código suelto pasa a «la señal «…»»;
  - se quitan D-0xx, P-xx y las rutas `docs/`.
  No toca códigos parecidos que son datos reales (la autovía A-42, un lote B-12). En las tablas del asistente, la columna `indicador` se enseña por el nombre de la señal.
- **Se deja:** «Isolation Forest» en la explicación de los atípicos, porque es el nombre del método de cálculo, no algo del desarrollo.
- **Tests:**
  - `sin_codigos`, incluidos los datos reales que no se tocan;
  - los avisos fijos, sin códigos;
  - la lista de metodología, sin códigos;
  - los mensajes de error del asistente.
  Total: 478 en verde, `ruff` limpio.
- **Comprobado:**
  - las nueve pantallas recorridas en el navegador sin ninguna referencia interna;
  - todas las respuestas preparadas del asistente generadas con la base real: las 7 que llevaban códigos quedan limpias tras la limpieza.

## Siguiente paso

Fusionar en `main`: es una corrección de textos, no una función nueva. Puede chocar en `paginas/atipicos.py` y `paginas/mapa_general.py` con `feat/graficos-acuaticos`; al fusionar hay que quedarse con los dos cambios.
