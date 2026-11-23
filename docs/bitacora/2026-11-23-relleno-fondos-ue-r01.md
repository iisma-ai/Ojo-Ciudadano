# 2026-11-23 · Filas de relleno, fondos europeos y referencia de R-01

- **Autor:** Claude (agente), a petición de una persona del equipo
- **Fase del plan:** 2, un día antes del hito H3. Prioridad del día: **la mejor calidad de datos posible**.
- **Rama:** `fix/relleno-y-referencia-r01` (sale de `docs/fuentes-externas`, así que incluye la investigación de [`../13-fuentes-externas.md`](../13-fuentes-externas.md))

## Qué se hizo

1. **Filas de relleno fuera de los adjudicatarios (D-026).** `normalizacion.nif.es_relleno` reconoce el NIF o el nombre de las líneas que resumen a varios adjudicatarios («Varios adjudicatarios», «33 EMPRESAS ADJUDICATARIAS» con el NIF de la Comunidad, «Ver resolución de adjudicación», NIF de ceros). Se guardan como adjudicatario desconocido, **sin nombre** (entre los NIF de ceros hay alguna persona, D-007). La adjudicación y su importe se conservan. Medido sobre la base del 20-nov: **15 identificadores, 165 adjudicaciones, 156,6 M€ con IVA** que contaban como empresas en fichas, R-04 y puntuación de empresa. Tests con los casos reales y con una empresa que lleva «Varios» en el nombre.
2. **Referencia de licitador único en la ayuda de R-01 (X-04).** `textos.CONTEXTO_SENAL`: en 2025, el 45,5 % de los lotes autonómicos tuvo una sola oferta (OIReScon) y la media de la UE fue del 28 % en 2024 (Single Market Scoreboard), con enlace a cada fuente y la advertencia de que se miden de otra forma. Se muestra en «Contratos a revisar» al elegir la señal y en la metodología.
3. **Fondos europeos (D-026, X-07).** `ingesta/placsp.py` lee `cbc:FundingProgramCode` (`financiado_ue`, `programas_ue`); `modelo/carga.py` los carga en la tabla aditiva `contrato_financiacion` (`sql/esquema/004_financiacion_ue.sql`); el asistente puede consultarla. Contexto, no señal: no entra en la puntuación.

## Decisiones y desviaciones

- **D-026** (nueva): tabla `contrato_financiacion` y tratamiento de las filas de relleno. D-025 ya estaba usada en `feat/datos-cm-abiertos`.
- El esquema v1 no cambia: `004` solo añade una tabla. `003` es de D-024 (otra rama); los números no chocan.

## Comprobaciones

- `uv run pytest`: todo en verde. `ruff check` y `ruff format`: limpios.
- Regeneración local de la base: ver «Resultados» (se rellena al terminar).

## Qué falta

1. **Regenerar la base** en cada máquina: `uv run python -m ojo_ciudadano.modelo.carga`, luego `indicadores.ejecutor` y `anomalias.deteccion`.
2. Mostrar los fondos europeos en la interfaz (etiqueta en la ficha de contrato o filtro). No se ha hecho: la interfaz la está cambiando la otra línea (D-025) y chocaría.
3. **Contratos menores recientes (P-12):** volver a exportar julio a noviembre de 2026 del portal. La exportación tiene captcha y el buscador tiene protección antibot, así que lo tiene que hacer una persona en el navegador.
4. Revisión legal de `CONTEXTO_SENAL` hecha con `revisor-legal`: aplicados sus dos cambios (no invitar a comparar al decimal ni a ver anómalo un contrato con una oferta; fecha de consulta).

## Siguiente paso

Fusionar `docs/fuentes-externas` y `fix/relleno-y-referencia-r01` (la segunda contiene la primera) y regenerar la base.
