# 2026-11-19 · Primera interfaz: panel de alertas y ficha de empresa

- **Autor:** Claude (agente), a petición de Ignacio
- **Fase del plan:** 2 · Construcción en paralelo (módulos de interfaz)

## Qué se hizo
- Rama `feat/app-empresa-alertas`, creada sobre `feat/indicadores-r04-r06` porque usa las tablas `puntuacion_*`.
- `src/ojo_ciudadano/app/`: `main.py` (navegación, cabecera con fecha de datos y aviso), `datos.py` (consultas), `textos.py`, `conexion.py` y `paginas/alertas.py`, `paginas/empresa.py`.
- Panel de alertas: contratos por puntuación, filtro por indicador y por mínimo de indicadores aplicables (por defecto 3, para que no dominen los menores), motivo y valor de cada indicador, y enlace a la ficha oficial.
- Ficha de empresa: búsqueda por nombre o NIF (mínimo 3 caracteres), contratos, puntuación y tendencia anual. Los importes con y sin IVA se muestran por separado y no se suman. Las personas físicas no tienen ficha ni aparecen en la búsqueda (D-007).
- 7 tests de `datos.py` con base sintética. El `conftest.py` pasa de `tests/indicadores/` a `tests/` para compartirlo. 84 tests y `ruff` en verde.
- Comprobado con Streamlit `AppTest` sobre la base real: las dos pantallas cargan sin errores.

## Decisiones tomadas
- Ninguna nueva (Streamlit ya es D-005).

## Desviaciones del plan
- Ninguna.

## Problemas y hallazgos
- No se ha pasado el agente `revisor-legal` sobre los textos: pendiente antes de la demo.
- Falta el aviso de proyecto independiente con la redacción final y la comprobación visual en el navegador (solo se probó con `AppTest`).

## Siguiente paso
- Revisar los textos con `revisor-legal`.
- Ficha de órgano y mapa del dinero; PR a `main` de esta rama y de la de indicadores.
