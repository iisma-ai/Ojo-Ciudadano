# 2026-11-26 · Dedo discreto en lugar de la caja «Pulsa una burbuja»

## Qué se ha hecho

- En «A dónde va el dinero» (`paginas/mapa_general.py`) y «De dónde viene el dinero»
  (`de_donde_viene.py`) se quita la caja informativa «Pulsa una burbuja del mapa y aquí verás…»
  de la columna de la ficha.
- En su lugar, `burbujas.pista_pulsar()` pinta solo un icono: un dedo (SVG propio basado en
  `touch_app` de Material Symbols, D-022) tenue, que da un toque suave en bucle con una onda
  pequeña. Con «reducir movimiento» queda quieto. Lleva `aria-label` para lectores de pantalla.

## Comprobaciones

- `ruff` y `pytest` en verde (496 tests).
- Sin navegador sin cabeza en esta máquina: falta verlo en pantalla.

## Siguiente paso

- Revisarlo en la web local y, si gusta, integrar el PR a `main`.
