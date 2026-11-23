# 2026-11-23 · Fuentes externas candidatas

- **Autor:** Claude (agente), a petición de una persona del equipo
- **Fase del plan:** 2, un día antes del hito H3 (demo funcional)
- **Rama:** `docs/fuentes-externas` (solo documentación; no toca código, esquema ni datos)

## Qué se hizo

Se pidió buscar las fuentes que más calidad pueden dar al proyecto sin pisar a la otra línea del día (`feat/datos-cm-abiertos`, D-024: catálogo de datos abiertos y Portal de Transparencia de la Comunidad). Por eso aquí se buscaron fuentes **fuera** de esas dos: estatales, europeas y de la Comunidad que no están en el catálogo. Resultado en [`../13-fuentes-externas.md`](../13-fuentes-externas.md), con commits y push a cada paso para que la otra línea viera el avance.

| ID | Fuente | Resultado |
| --- | --- | --- |
| X-01 | Prohibiciones de contratar (ROLECE) | Descartada: no hay listado público |
| X-02 | Tribunal Administrativo de Contratación Pública de la Comunidad (TACPCM) | Viable: 1.109 resoluciones de 2023–2026 de órganos de la Comunidad, con resultado y acto recurrido; el resumen cita el expediente |
| X-03 | CNMC, colusión en licitaciones | Solo manual; ningún caso de órganos de la Comunidad en 2023–2026 en la búsqueda |
| X-04 | Referencias de licitador único | Viable y barata: OIReScon 2025 (45,5 % de los lotes autonómicos), Scoreboard 2024 (España 33 %, UE 28 %), TCE por NUTS2 (ES30: 37,5 % en 2021) |
| X-05 | DIR3 | Viable, valor medio: 499 unidades de la Comunidad con jerarquía y NIF; PLACSP no trae el código de la Comunidad |
| X-06 | EDES (exclusión de la UE) | Descartada: 5 entidades |
| X-07 | Fondos europeos | Ya están en el Atom de PLACSP (`FundingProgramCode`) y no los leemos: 991 expedientes con fondos de la UE, 548 del PRTR |
| X-08 | Deudores de la AEAT | Descartada: la ley obliga a retirarlo a los tres meses e impide su reutilización |

## Hallazgos

- **R-01 no es anómalo en el contexto español:** el 39,4 % de licitador único de la Comunidad queda por debajo de la media del sector autonómico en 2025 (45,5 % de los lotes, OIReScon) y por encima de la media europea en TED (28 %). Conviene decirlo en la ayuda de R-01.
- **Calidad de datos:** en `adjudicatario` hay filas de relleno con el NIF de la propia Comunidad: `S7800001E` «33 EMPRESAS ADJUDICATARIAS» (6 adjudicaciones, 35,2 M€) y `Q7850065I` «VER ORDEN DE ADJUDICACIÓN» (58). Hoy cuentan como empresas en fichas, R-04 y puntuación. Se vio al cruzar con DIR3 sobre la base local del 20-nov.

## Decisiones y desviaciones

- Ninguna. No se ha incorporado nada al pipeline: incorporar cualquiera de estas fuentes amplía D-001 y necesita una decisión registrada. La recomendación priorizada está al final de `13-fuentes-externas.md`.
- Para leer el Excel de DIR3 se usó `fastexcel` solo en un entorno temporal (`uv run --with`), sin añadirlo a `pyproject.toml`. D-024 lo añade al proyecto.

## Siguiente paso

1. Que el equipo decida qué entra antes del H3 (recomendación: X-04 en la ayuda de R-01 y tratar las filas de relleno hoy; X-07 si da tiempo).
2. Avisar a la línea de ingesta de las filas de relleno con el NIF de la Comunidad.
3. Fusionar esta rama en `main` (solo documentación).
