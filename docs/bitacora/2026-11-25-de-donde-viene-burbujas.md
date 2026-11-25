# 2026-11-25 · «¿De dónde viene el dinero?» solo con las burbujas

- **Quién:** Ignacio con Claude (agente)
- **Rama:** `feat/de-donde-viene-burbujas` (sale de `main` en `08407ab`)

## Qué se ha hecho

- **«¿De dónde viene el dinero?» (D-064):**
  - fuera la barra apilada «de cada 100 € que entran» y la caja de tres cifras de arriba;
  - la vista empieza con el título del año y el mapa de burbujas, con la fuente debajo;
  - el sistema de financiación autonómica deja de ocupar la página: ahora es una caja de información en la columna de la ficha, con el saldo y lo que queda, y un botón «Cómo funciona el sistema» con la explicación de siempre, los fondos y su fuente.
- **Nombre del compañero:** se corrige a «Ismael» en todo el repositorio (decisiones y bitácoras), donde figuraba otro nombre por error. Las tareas y decisiones siguen asignadas igual, con el nombre correcto.

## Comprobaciones

- Tests y `ruff` en verde. El test de la barra se sustituye por uno de la caja del saldo.
- No se ha mirado todavía en el navegador.

## Siguiente paso

- Revisarlo en pantalla y, si gusta, integrar en `main`.
