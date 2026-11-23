# 2026-11-23 · Filas de relleno, fondos europeos y referencia de R-01

- **Autor:** Claude (agente), a petición de una persona del equipo
- **Fase del plan:** 2, un día antes del hito H3. Prioridad del día: **la mejor calidad de datos posible**.
- **Rama:** `fix/relleno-y-referencia-r01` (sale de `docs/fuentes-externas`, así que incluye la investigación de [`../13-fuentes-externas.md`](../13-fuentes-externas.md))

## Qué se hizo

1. **Filas de relleno fuera de los adjudicatarios (D-027).** `normalizacion.nif.es_relleno` reconoce el NIF o el nombre de las líneas que resumen a varios adjudicatarios («Varios adjudicatarios», «33 EMPRESAS ADJUDICATARIAS» con el NIF de la Comunidad, «Ver resolución de adjudicación», NIF de ceros). Se guardan como adjudicatario desconocido, **sin nombre** (entre los NIF de ceros hay alguna persona, D-007). La adjudicación y su importe se conservan. Medido sobre la base del 20-nov: **15 identificadores, 165 adjudicaciones, 156,6 M€ con IVA** que contaban como empresas en fichas, R-04 y puntuación de empresa. Tests con los casos reales y con una empresa que lleva «Varios» en el nombre.
2. **Referencia de licitador único en la ayuda de R-01 (X-04).** `textos.CONTEXTO_SENAL`: en 2025, el 45,5 % de los lotes autonómicos tuvo una sola oferta (OIReScon) y la media de la UE fue del 28 % en 2024 (Single Market Scoreboard), con enlace a cada fuente y la advertencia de que se miden de otra forma. Se muestra en «Contratos a revisar» al elegir la señal y en la metodología.
3. **Fondos europeos (D-027, X-07).** `ingesta/placsp.py` lee `cbc:FundingProgramCode` (`financiado_ue`, `programas_ue`); `modelo/carga.py` los carga en la tabla aditiva `contrato_financiacion` (`sql/esquema/004_financiacion_ue.sql`); el asistente puede consultarla. Contexto, no señal: no entra en la puntuación.

## Decisiones y desviaciones

- **D-027** (nueva): tabla `contrato_financiacion` y tratamiento de las filas de relleno. D-025 y D-026 ya estaban usadas en `feat/datos-cm-abiertos`.
- El esquema v1 no cambia: `004` solo añade una tabla. `003` es de D-024 (otra rama); los números no chocan.

## Comprobaciones

- `uv run pytest`: todo en verde. `ruff check` y `ruff format`: limpios.
- Regeneración local completa (carga, indicadores y anomalías: 8 min 53 s), con los CSV del portal del 16-nov, los zip de PLACSP y la BDNS:
  - **Filas de relleno:** ya no aparecen. `S7800001E` y `Q7850065I` siguen solo en adjudicaciones legítimas: `Q7850065I` es el NIF del Organismo Autónomo Boletín Oficial de la Comunidad (56 adjudicaciones, 0,26 M€), y `S7800001E` el de la propia Comunidad (4 adjudicaciones, 3.235 €).
  - **`contrato_financiacion`:** 14.772 licitaciones con el dato; **965 con fondos de la UE** (PRTR 540, FEDER 200, otros fondos europeos 153, FSE+ 52, FEADER 20) y 13.807 sin ellos.
  - **Indicadores:** R-01 sin cambios (8.144 de 20.693); R-04 pasa de 84 a **83** activados; anomalías: 13.498 atípicos de 1.349.510.

## Contratos menores de julio a septiembre de 2026 (P-12)

- Con el navegador integrado se comprobó en el buscador del portal que jul–sep de 2026 tenían ya 10.993, 6.574 y 7.357 menores, frente a 3.565, 2.312 y 3.218 en la exportación del 16-nov. Abril, mayo y junio coinciden exactamente con la base, así que la medida es fiable. Octubre y noviembre siguen sin menores publicados.
- Una persona del equipo exportó jul–sep (captcha) el 23-nov: `data/raw/portal_cm/menores_2026-07-01_2026-09-30.csv`, 24.924 filas. Los ficheros de agosto y septiembre del 16-nov están en `data/raw/portal_cm_respaldo_2026-11-16/` (no se leen).
- Tras regenerar (9 min 17 s): **152.702 menores en 2026** (antes 136.873, +15.829); `contrato` 1.387.522 filas. R-03 pasa a 1.332.957 aplicables y **228.122 activados** (17,1 %; antes 1.317.145 y 222.122). Anomalías: 13.657 atípicos de 1.365.339. R-01, R-02, R-05 y R-06 no cambian (los menores no les aplican).
- **Para el resto del equipo:** este CSV no se puede bajar por código. O se repite la exportación (contratos menores, «Fecha del contrato o encargo» del 01-07-2026 al 30-09-2026) o se pasa el fichero por un canal privado; `data/` no se sube a git.

## Qué falta

1. **Regenerar la base** en cada máquina: `uv run python -m ojo_ciudadano.modelo.carga`, luego `indicadores.ejecutor` y `anomalias.deteccion`.
2. Mostrar los fondos europeos en la interfaz (etiqueta en la ficha de contrato o filtro). No se ha hecho: la interfaz la está cambiando la otra línea (D-025) y chocaría.
3. **Contratos menores recientes (P-12):** volver a exportar julio a noviembre de 2026 del portal. La exportación tiene captcha y el buscador tiene protección antibot, así que lo tiene que hacer una persona en el navegador.
4. Revisión legal de `CONTEXTO_SENAL` hecha con `revisor-legal`: aplicados sus dos cambios (no invitar a comparar al decimal ni a ver anómalo un contrato con una oferta; fecha de consulta).

## Siguiente paso

Fusionar `docs/fuentes-externas` y `fix/relleno-y-referencia-r01` (la segunda contiene la primera) y regenerar la base.
