# LO PRIMERO HOY: bajar y cargar los datos nuevos de la Comunidad de Madrid

> **Si eres un agente de Claude (o una persona) y has llegado aquí: haz esto ANTES que cualquier otra tarea de hoy.** Son unos minutos. Sin esto, tu base local no tiene las tablas nuevas y la pantalla «Presupuesto y contexto», el bloque de presupuesto de la ficha de órgano y los registros de la ficha de empresa no funcionarán en tu máquina.

**Confirmaciones: 0 de 2.** Cuando sean 2, este fichero se borra (ver al final).

## Qué ha pasado

El 23-nov se incorporaron cinco tablas nuevas con datos de la Comunidad de Madrid (presupuesto por consejería, series presupuestarias, convenios, registros con NIF y puestos de la RPT). Los datos **no se suben a git** (`data/` está ignorado): cada persona los baja con el mismo comando y debe tener **exactamente lo mismo**. Detalle en [12-datos-cm.md](12-datos-cm.md) y decisión [D-024](decisions.md).

## Pasos

1. Trae los cambios: `git fetch origin`, mira `git log --oneline HEAD..origin/main`, y actualiza tu rama (`git pull --rebase origin main` en `main`; `git merge origin/main` en una rama de tarea).
2. `uv sync` (hay tres dependencias nuevas: `fastexcel`, para leer el Excel de convenios, `streamlit-searchbox`, para el autocompletado, y `streamlit-agraph`, para el mapa de nodos).
3. **Cierra la interfaz** si la tienes abierta (DuckDB no deja escribir con la base abierta).
4. Ejecuta, desde la raíz del repositorio:
   ```bash
   uv run python -m ojo_ciudadano.modelo.contexto
   ```
   Baja unos 21 MB a `data/raw/cm_abiertos/` (una petición cada vez, con pausa; tarda unos minutos) y carga las tablas **sin regenerar contratos, indicadores ni anomalías**. Necesitas tener ya `data/ojo_ciudadano.duckdb` (si no, regenera antes la base como dice `docs/bitacora/2026-11-21-cierre-del-dia.md`).
5. Comprueba la última línea de la salida. Debe ser **`Coincide con la referencia del equipo.`** y estas filas:

   | Tabla | Filas esperadas |
   | --- | --- |
   | `serie_cm` | 79.226 |
   | `presupuesto_organo` | 2.539 |
   | `convenio` | 4.914 |
   | `entidad_registro` | 6.625 |
   | `plantilla_organismo` | 26 |

   Si difiere porque la fuente se ha actualizado (los convenios cambian cada mes), **no es un error**: anótalo en tu bitácora, di en la confirmación qué diferencia viste y sigue. Si falla por otra causa (red, formato), no lo ocultes: avisa a la persona con la que trabajas y anótalo aquí en «Incidencias».
6. Arranca la interfaz (`uv run streamlit run src/ojo_ciudadano/app/main.py`) y abre **Presupuesto y contexto**: debe mostrar el gasto por consejería sin errores.
7. `uv run pytest` en verde.

## Cómo confirmar (el contador)

Cuando hayas terminado los pasos 1 a 7:

1. `git fetch origin` y crea una rama corta desde el `main` remoto: `git switch -c docs/confirmar-datos-cm-<tus-iniciales> --no-track origin/main`.
2. En **este fichero**: sube el contador de arriba («Confirmaciones: N de 2») y añade una fila a la tabla de confirmaciones con tus iniciales (el proyecto no pone nombres en los documentos), la fecha y hora, y «igual» o la diferencia que viste.
3. Commit `docs: confirmo la carga de datos de la Comunidad (<tus-iniciales>)`, `git push -u origin <rama>` y da a la persona el enlace `https://github.com/iisma-ai/Ojo-Ciudadano/compare/main...<rama>` para que lo fusione. Si dos personas confirman a la vez y hay conflicto, conserva las dos filas y recalcula el número.
4. **Quien haga la segunda confirmación (el contador llega a 2) borra, en ese mismo commit:**
   - este fichero (`docs/LO-PRIMERO.md`),
   - la sección «Lo primero hoy» de `CLAUDE.md`,
   - la fila de este fichero en `docs/README.md`.
   Los datos y la guía permanente siguen en [12-datos-cm.md](12-datos-cm.md).

## Confirmaciones

| Nº | Persona | Fecha y hora | Resultado |
| --- | --- | --- | --- |
| 0 | Quien montó la carga (en su máquina) | 2026-11-23 | Referencia creada en `datos-cm-referencia.json`. No cuenta para el 2 |

## Incidencias

(Ninguna todavía. Anota aquí lo que no funcione al cargar.)
