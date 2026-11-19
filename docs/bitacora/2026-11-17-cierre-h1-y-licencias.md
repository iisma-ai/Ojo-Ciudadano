# 2026-11-17 · Preparación del cierre de H1 y revisión de licencias

- **Autor:** Claude (agente), a petición de Ignacio
- **Fase del plan:** 1 · Datos y alcance (hito H1)

## Qué se hizo
- Estado del proyecto con `/estado` y revisión del esquema propuesto (`sql/esquema/001_tablas.sql`) frente a la decisión de congelarlo.
- **P-03 resuelta en parte.** Leídos los avisos legales de la Comunidad de Madrid y del Ministerio de Hacienda (PLACSP). Condiciones, enlaces y cómo las aplicamos, en 02 («Licencias y condiciones de reutilización»). La BDNS no se pudo leer (página dinámica): queda pendiente de lectura manual.
- **D-017 registrada como Propuesta:** congelar el esquema v1, con ampliaciones aditivas permitidas.
- Actualizados 08 (tarea de licencias), 09 (P-03) y 02.
- Nota: esta sesión no cubre la sesión de código de la madrugada del 17-nov (ingesta, esquema, primera carga): la recoge la sección «Segunda parte» de `2026-11-16-exploracion-fuentes.md`.

## Decisiones tomadas
- Ninguna aceptada. D-017 queda como propuesta para el equipo.

## Desviaciones del plan
- Ninguna.

## Problemas y hallazgos
- `uv run pytest` no se pudo ejecutar: `uv` agotó el tiempo al sincronizar el entorno (fallo de red). Los 27 tests se dieron por verdes en la sesión anterior; hay que volver a pasarlos.
- Condición a tener en cuenta en la interfaz: la Comunidad exige indicar la fecha de extracción y no sugerir patrocinio. Hace falta un aviso visible de proyecto independiente.
- El texto del aviso de Madrid prohíbe «alterar el contenido»: los datos originales se muestran tal cual y los indicadores se etiquetan como cálculo propio.

## Siguiente paso
- El equipo revisa el esquema y acepta D-017 (entonces H1 pasa a cumplido en 08).
- Asignar nombres a las personas 1–4 en 08.
- Compartir la muestra limpia y la sal de seudónimos por un canal privado.
- Leer el aviso de la BDNS a mano y encontrar el filtro de la Comunidad de Madrid.
- Empezar R-01, R-03 y R-05 con `/nuevo-indicador`.

## Nota del 19-nov (renumeración)
- La decisión de congelar el esquema se había citado como D-015, pero nunca llegó a escribirse en `docs/decisions.md`, y la rama `feat/indicadores-r01-r03-r05` ya usa D-015 y D-016 para R-03 y R-05 (aceptadas). Se registra ahora como **D-017** (Propuesta) y se corrigen las referencias de esta bitácora.
