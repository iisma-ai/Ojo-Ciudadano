# 2026-11-23 · Estética «océano» y cristal en la web (D-034)

- **Fase del plan:** 2, víspera del H3. Solo estilo; no cambia datos ni lógica.

## Qué se hizo
- `static/estilo.css`: fondo de mar (degradado, rayos de luz y burbujas en CSS, sin animación con `prefers-reduced-motion`); cristal esmerilado en métricas, tarjetas de `st.container(border=True)`, desplegables, avisos, barra lateral, botones, controles segmentados, campos y menús; títulos con degradado.
- `red.svg_nodo`: burbujas de cristal sobrias (líquido hasta lo gastado, borde más claro, velo de luz arriba, sin manchas de brillo). Los mapas de nodos ya no tienen recuadro: el fondo del componente se funde con `mix-blend-mode: lighten` y bordes difuminados con `mask-image`.
- `graficos.py`: las separaciones de tartas, rectángulos y puntos pasan de negro (`#0B1120`) a líneas claras casi transparentes (`SEPARADOR`, `BRILLO`).
- `.streamlit/config.toml` y `docs/marca.md`: paleta azul océano.
- Renumerada la decisión del mapa de un vistazo a **D-033** (D-032 ya la usaba el RAG documental en `main`).

## Comprobado
- En Chrome: mapa general, mapa del dinero (vista general y red de un organismo), inicio, contratos a revisar y presupuesto y contexto. Tests y `ruff` en verde.

## Siguiente paso
- Revisar en el proyector de la demo que el contraste del cristal se ve bien.
- Si una versión nueva de Streamlit cambia los `data-testid`, revisar `estilo.css`.
