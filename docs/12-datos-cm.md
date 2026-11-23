# 12 · Contexto de la Comunidad de Madrid: presupuesto, convenios y registros

Añadido el 23-nov-2026 (D-024). Todo viene de **fuentes de la Comunidad de Madrid** (catálogo de datos abiertos y Portal de Transparencia). Da escala y contexto a los contratos y subvenciones; **no son indicadores de riesgo** y no se cruzan partida a partida con los contratos (los datos no lo permiten, ver [02-fuentes-datos.md](02-fuentes-datos.md)).

## Cómo tener estos datos (todo el equipo, igual)

```bash
git pull                # o merge de origin/main en tu rama
uv sync                 # hay una dependencia nueva: fastexcel (lee el Excel de convenios)
# cierra la interfaz (DuckDB no deja escribir con la base abierta)
uv run python -m ojo_ciudadano.modelo.contexto
```

Hace tres cosas: baja a `data/raw/cm_abiertos/` lo que falte (32 ficheros, unos 21 MB, una petición cada vez y con pausa), carga las cinco tablas nuevas en `data/ojo_ciudadano.duckdb` **sin tocar contratos, indicadores ni anomalías** (no hace falta regenerar nada) y compara lo cargado con [`datos-cm-referencia.json`](datos-cm-referencia.json). Debe terminar con `Coincide con la referencia del equipo.`

- Si la fuente se ha actualizado desde el 23-nov (los convenios cambian cada mes), los recuentos o las huellas pueden diferir. **No es un error**: anótalo en tu bitácora y avisa; quien amplíe las fuentes reescribe la referencia con `--escribir-referencia`.
- Opciones: `--forzar` (volver a bajar todo) y `--sin-descarga` (solo cargar lo que ya tienes).
- Una regeneración completa de la base (`uv run python -m ojo_ciudadano.modelo.carga`) también carga este contexto si `data/raw/cm_abiertos/` existe.

## Qué se ha incorporado

| Fuente | Tabla | Filas (23-nov) | Para qué sirve |
| --- | --- | --- | --- |
| Catálogo de datos abiertos: 25 series «Año; Concepto; Valor; Unidad» (presupuestos iniciales y liquidados por capítulo, función, sección y centro; ingresos; ayudas de la UE; personal; gasto sanitario y educativo; recaudación; estadística de contratos) | `serie_cm` | 79.226 | Escala: en qué gasta y cómo se financia la Comunidad |
| Catálogo: presupuestos iniciales por clasificación orgánica y liquidados por órgano y fase | `presupuesto_organo` | 2.539 | Presupuesto, crédito, gasto reconocido y pagos de cada consejería; se enlaza con `organo` cuando el nombre coincide |
| Portal de Transparencia: convenios vigentes (Excel mensual) | `convenio` | 4.914 | Tercer flujo de dinero: consejería y firmantes por nombre |
| Catálogo: registro de transparencia (grupos de interés), fundaciones, cooperativas | `entidad_registro` | 6.625 | Etiqueta de entidad; se cruza con `adjudicatario` por NIF (836 + 151 + 272 empresas con contratos o subvenciones) |
| Catálogo: relación de puestos de trabajo de funcionarios | `plantilla_organismo` | 26 | Puestos por organismo (solo recuentos) |

Esquema en [`sql/esquema/003_contexto_cm.sql`](../sql/esquema/003_contexto_cm.sql) (aditivo: no cambia nada del esquema v1). Cada fila lleva `fuente`, `url_origen` y `fecha_descarga`.

## Dónde se ve en la web

- **Presupuesto y contexto** (pantalla nueva, grupo «Explorar»): gasto por consejería y año con contratos y subvenciones al lado; evolución por capítulo; gastos e ingresos presupuestados; personal; convenios con filtros; registros.
- **Ficha de órgano:** bloque «Presupuesto de la consejería» (crédito y gasto reconocido por año).
- **Ficha de empresa:** «En qué registros de la Comunidad figura» (por NIF).
- **Asistente:** las cinco tablas están en la lista permitida y descritas para el modelo.

## Privacidad y lenguaje (D-007, D-002)

- Los registros solo guardan **NIF de persona jurídica**; un DNI, un NIE o un NIF vacío no entra.
- En los convenios, un firmante solo se guarda si su nombre tiene forma de entidad (empresa, ayuntamiento, fundación…); los demás se cuentan en `n_firmantes` pero no se guardan.
- No se suma el texto de financiación de los convenios: mezcla importes anuales, máximos y de varios años.
- Estar en un registro **no es una señal de riesgo**; la interfaz lo dice (`textos.AVISO_REGISTROS`).
- Las ayudas, los convenios y el presupuesto no se comparan al céntimo con los contratos: `textos.AVISO_CONTEXTO`.

## Condiciones de reutilización

- **Catálogo de datos abiertos:** Creative Commons Attribution (ver [02-fuentes-datos.md](02-fuentes-datos.md)). Se cita en el pie de la interfaz con enlace y fecha.
- **Portal de Transparencia:** aviso legal de comunidad.madrid (citar fuente y fecha, no alterar el sentido, no sugerir patrocinio). El pie lo cumple igual que para el portal de contratación.

## Qué no se ha incorporado y por qué

| Fuente (todas de la Comunidad) | Motivo |
| --- | --- |
| Planes de medios de publicidad institucional (103 Excel de 2025, formato distinto en cada uno) | Mucho parseo para poco; candidato posterior |
| Deuda pública (Excel de operaciones y garantías) | Contexto menor, sin enlace con contratos |
| Registro de solicitudes y reclamaciones de transparencia | Contiene identidad de solicitantes: personas físicas |
| RPT de altos cargos y de personal eventual | Contienen datos de personas concretas (D-007) |
| Registro de asociaciones y de sociedades laborales | No traen NIF: no se pueden cruzar con empresas |
| Centros de atención social, centros sanitarios, residencias | Candidato posterior: titular por nombre, sin NIF |
| Datos municipales (presupuestos de ayuntamientos, IRPF) | Otra administración: fuera de alcance (D-001) |
| Agenda de Gobierno, cuentas anuales y informes de fiscalización (PDF) | Sin estructura útil antes de la demo |

## Para quien amplíe esto

Añadir una serie del catálogo con formato «Año; Concepto; Valor; Unidad» es una línea en `SERIES` de `ingesta/cm_abiertos.py`: entra sola en `serie_cm`. Después, `uv run python -m ojo_ciudadano.modelo.contexto --escribir-referencia` y subir la nueva `datos-cm-referencia.json`.
