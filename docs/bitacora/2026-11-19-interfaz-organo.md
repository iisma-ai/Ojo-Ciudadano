# 2026-11-19 · Ficha de órgano

- **Autor:** Claude (agente), a petición de Ignacio
- **Fase del plan:** 2 · Construcción en paralelo (módulos de interfaz)

## Qué se hizo
- Rama `feat/app-organo`, sobre `feat/app-empresa-alertas`.
- `paginas/organo.py` y consultas nuevas en `app/datos.py`: búsqueda de órganos, ficha, indicadores del órgano frente al total, evolución anual, procedimientos y principales empresas.
- La posición frente a los demás es un percentil entre los órganos con al menos 100 contratos puntuados, con la advertencia de que no valora la gestión.
- Importes con y sin IVA por separado; sin personas físicas en los listados (D-007).
- 4 tests nuevos (88 en total) y `ruff` en verde. Comprobado con `AppTest` sobre la base real (2 s, sin errores).

## Decisiones tomadas
- Ninguna. Umbral de 100 contratos para el percentil: criterio de presentación, sin efecto sobre los indicadores.

## Desviaciones del plan
- Ninguna.

## Problemas y hallazgos
- Los proveedores se ordenan por número de contratos, no por importe, para no mezclar importes con y sin IVA (P-10).
- Falta el pase de `revisor-legal` sobre los textos de las tres pantallas.

## Siguiente paso
- Mapa del dinero (órgano → empresa).
- `revisor-legal` sobre la interfaz.
- PR a `main` de la cadena de ramas.
