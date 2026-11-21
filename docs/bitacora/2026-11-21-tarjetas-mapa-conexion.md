# 2026-11-21 · Error de conexión, tarjetas desplegables y colores del mapa

- **Autor:** Claude (agente)
- **Fase del plan:** 2. Ajustes de A-03 y A-07 (D-023) tras revisarlos en la web.
- **Rama:** `fix/tarjetas-mapa-conexion`

## Qué se hizo
- **Error «connection is busy»:** todas las sesiones del navegador compartían una sola conexión DuckDB, que no admite llamadas a la vez. `app/conexion.py` da ahora un cursor por sesión sobre la conexión de solo lectura. Se ha comprobado que el cursor sigue sin acceso a ficheros.
- **Contratos a revisar:**
  - Cada contrato es un desplegable. Al pulsar en cualquier parte se abre con sus gráficos, que solo se calculan entonces (`on_change="rerun"` y `.open`). Ya no hay un botón «Ver gráficos» repetido en cada tarjeta.
  - Las señales van en texto normal junto al organismo, en lugar de insignias naranjas.
  - Filtros más libres: buscar por palabra del título u organismo, señal (desplegable) y año, además del interruptor de menores. `datos.alertas` admite `texto` y `anio`.
- **Mapa del dinero:**
  - Cada organismo tiene su color de una paleta categórica de 7 colores, y sus flujos llevan el mismo color, translúcido. Del 8.º organismo en adelante, gris.
  - La paleta (`graficos.CATEGORICOS`) pasa las comprobaciones del validador de la guía de visualización sobre el fondo `#0B1120`: luminosidad, croma, separación para daltonismo y contraste.

## Decisiones tomadas
- Ninguna nueva.

## Siguiente paso
- A-05, A-06 y A-07 completo (red de burbujas), según `docs/11-accesibilidad.md`.
