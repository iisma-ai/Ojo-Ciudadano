# 2026-11-20 · Pendientes de la revisión legal en la interfaz y DNI con erratas

- **Autor:** Claude (agente), a petición de Ignacio
- **Fase del plan:** 2 · Construcción en paralelo (interfaz; entregable de la persona 3)

## Qué se hizo
- Sincronizado con `origin/main`: la pila de ramas del 18–19 de noviembre ya está integrada, más `9bc56d7` (motivos de R-02, R-03 y R-05) y `657cd3f` (D-021, detección de anomalías). Rama nueva `fix/pendientes-revision-legal` desde `origin/main`.
- **R-04:** el motivo dice «Un adjudicatario concentra…». Estaba sin commit en local aunque la bitácora del 19-nov lo daba por hecho.
- **Personas físicas con DNI o NIE con erratas (D-007):** `normalizacion/nif.py` solo reconocía DNI de 8 cifras. Había 25 adjudicatarios con DNI sin el cero inicial (7 cifras + letra) o NIE con una cifra de más que quedaban como `otro`, con nombre y NIF visibles en la búsqueda, las fichas y el mapa. Ahora esas formas son `fisica` y se seudonimizan. La letra de control no sirve para distinguirlos: falla en 6 de esas personas por erratas de la fuente, y algunos NIF-IVA irlandeses tienen la misma forma. Prima la privacidad: esas pocas empresas extranjeras (p. ej. Google Ireland) quedan ocultas.
- **Interfaz:** `app/datos.py` excluye además cualquier NIF con forma de DNI/NIE (`_sin_personas`), por si la base es anterior a la corrección. Se aplica en la búsqueda, la ficha de empresa, los proveedores del órgano y el mapa del dinero.
- **Fecha de descarga de cada fuente** en la cabecera (`datos.fechas_datos`, `textos.fechas_descarga`) en lugar de la fecha global.
- **Qué mide cada indicador** (`textos.AYUDA_INDICADOR`), en «Metodología y fuentes» y en el panel de alertas al filtrar por un indicador. Incluye la ayuda de R-06 que faltaba. Revisado con `revisor-legal`: se añadieron los umbrales reales de R-03, el mercado mínimo de R-04 y los procedimientos de R-06, y se unificó el nombre del portal.
- Base regenerada (`modelo.carga` + `indicadores.ejecutor`): 5.095 personas físicas (antes 5.070), 0 NIF con forma de DNI/NIE y las mismas cifras de activación en R-01 a R-06. Las cuatro pantallas cargan sin errores con `AppTest`.
- 95 tests y `ruff` en verde.

## Decisiones tomadas
- Ninguna nueva: es una corrección de cómo se aplica D-007. Queda documentada en `docs/06-arquitectura.md`.

## Desviaciones del plan
- Ninguna.

## Problemas y hallazgos
- En el primer intento puse en los tests dos DNI reales copiados de la base. El clasificador de permisos bloqueó el commit y se sustituyeron por valores sintéticos antes de subir nada. **Regla:** en tests y docs, nunca identificadores reales de personas.
- `docs/06-arquitectura.md` documentaba como primera carga del 17-nov 5.070 personas físicas; la cifra nueva está en el mismo apartado.

## Siguiente paso
- **Todo el equipo debe regenerar su base** (`uv run python -m ojo_ciudadano.modelo.carga` y luego `uv run python -m ojo_ciudadano.indicadores.ejecutor`) para que esos NIF desaparezcan también de su copia local.
- Abrir el PR de esta rama a `main`.
- Pendientes: asistente (D-010 sin decidir), subvenciones (BDNS), licencias (P-03) y responsable de la detección de anomalías (D-021, entrega el 23-nov).
