# 2026-11-21 · Ficha de empresa visual (D-023, A-05)

- **Autor:** Claude (agente)
- **Fase del plan:** 2. Tarea A-05 de `docs/11-accesibilidad.md`.
- **Rama:** `feat/accesibilidad-empresa`

## Qué se hizo
- Estudio A-05 anotado en `docs/11`: alternativas y elección para cada bloque.
- `paginas/empresa.py` rehecha:
  - buscador;
  - cuatro cifras (contratos, con alguna señal, importe adjudicado con su base de IVA, subvenciones);
  - «De qué organismos»: mapa de áreas con un color por organismo y un selector de fuente;
  - contratos por año con y sin señales;
  - qué señales aparecen;
  - sus 30 contratos con más señales como tarjetas desplegables;
  - sus subvenciones con enlace a la convocatoria.
- `datos.reparto_empresa` (por fuente y organismo, sin mezclar bases de IVA) y `datos.senales_empresa`.
- `graficos.reparto_organismos`, `contratos_por_anio`, `senales_de_empresa` y `partir` (nombres largos en varias líneas).
- La tarjeta de contrato pasa a `senales.tarjeta_contrato`, compartida con «Contratos a revisar».
- Textos con «importe adjudicado o concedido», no «dinero recibido»: no sabemos lo pagado (criterio de la revisión legal de D-023).

## Decisiones tomadas
- Ninguna nueva.

## Siguiente paso
- A-06 (ficha de organismo) y A-07 (mapa del dinero).
