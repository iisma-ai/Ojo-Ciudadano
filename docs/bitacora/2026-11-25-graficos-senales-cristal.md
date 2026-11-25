# 2026-11-25 · Gráficos de las señales como dibujos de cristal

## Qué se ha hecho

- Los cinco gráficos de Plotly de las señales de un contrato (una sola oferta, sin anuncio, una empresa
  concentra el gasto, modificaciones y rebaja) pasan a dibujos propios en SVG, con el mismo concepto y el estilo
  de la web: tubos y burbujas de cristal llenos de líquido (D-062, `app/dibujos_senales.py`).
- Los contratos menores (E-03) mantienen su dibujo, con la tarjeta y las hojas en cristal (`billetes.py`).
- Se quitan las figuras de Plotly sustituidas de `app/graficos.py`; tests nuevos en `tests/app/test_visual.py`.
- Afecta a todas las tarjetas de contrato: «Contratos a revisar», fichas de empresa y organismo, y Mapa del dinero.

## Decisiones

- D-062 (propuesta).

## Pendiente

- **No subido** (a petición de Ignacio): commit solo en local, rama `feat/graficos-alertas`.
- Revisarlo en pantalla: no se pudo ver desde el agente (sin navegador ni conversor de SVG).
