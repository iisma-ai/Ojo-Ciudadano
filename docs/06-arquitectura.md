# 06 · Arquitectura técnica

Cuatro fuentes oficiales alimentan una **base analítica** y un **corpus documental**. Sobre ellos trabajan el **motor de indicadores** y el **asistente**, y la **interfaz** lo muestra todo con enlace al origen.

## Capas del MVP

```
 ┌──────────────────────────────────────────────────────────────────────┐
 │ 5. Interfaz (Streamlit): mapa del dinero · fichas · alertas · chat   │
 └───────────────▲───────────────────────────────▲──────────────────────┘
                 │                               │
 ┌───────────────┴──────────────┐  ┌─────────────┴────────────────────┐
 │ 3. Motor de indicadores      │  │ 4. Asistente                     │
 │    SQL versionado → scores   │  │    texto a SQL + RAG con citas   │
 └───────────────▲──────────────┘  └─────▲───────────────────▲────────┘
                 │                       │                   │
 ┌───────────────┴───────────────────────┴──────┐  ┌─────────┴────────┐
 │ 2a. Base analítica (DuckDB, un fichero)      │  │ 2b. Corpus       │
 │     contratos · subvenciones · órganos · NIF │  │  (BM25+embedd.)  │
 └───────────────▲──────────────────────────────┘  └─────────▲────────┘
                 │                                           │
 ┌───────────────┴───────────────────────────────────────────┴────────┐
 │ 1. Ingesta y normalización (Python + polars, lxml para Atom)       │
 │    Portal Contratación CM · PLACSP · BDNS · Transparencia/Presup.  │
 └────────────────────────────────────────────────────────────────────┘
```

El **motor de indicadores** es la pieza que no existe en los portales actuales: es nuestro valor diferencial.

## Tecnologías

| Pieza | Tecnología | Motivo | Decisión |
| --- | --- | --- | --- |
| Entorno y dependencias | **uv** | Reproducible, rápido, un solo comando para todo el equipo | D-008 |
| Ingesta | Python con **polars** (pandas si hace falta); **lxml** para el Atom de PLACSP; **httpx** para descargas | El equipo ya lo domina; rápido de iterar | D-003 |
| Base analítica | **DuckDB** en un único fichero | SQL analítico sin servidor; fácil de compartir entre los 4 | D-003 |
| Indicadores | **Consultas SQL versionadas** en el repositorio | Transparentes y reproducibles por el jurado | D-004 |
| Corpus y búsqueda | Índice híbrido BM25 + embeddings (p. ej. LanceDB o Chroma) | Corpus pequeño; sin infraestructura | D-010 (pendiente) |
| Asistente | LLM por API con llamada a herramientas | Texto a SQL y RAG como dos herramientas del mismo agente | D-010 (pendiente) |
| Interfaz | **Streamlit** | Paneles y chat en pocos días; migrable después | D-005 |

## Estructura del repositorio (prevista)

Se crea a medida que haga falta; no crear carpetas vacías por adelantado. Si se cambia esta estructura, se registra en [decisions.md](decisions.md).

```
Ojo-Ciudadano/
├── CLAUDE.md                 # Reglas para agentes (leer siempre)
├── README.md                 # Presentación pública del proyecto
├── pyproject.toml / uv.lock  # Dependencias (uv)
├── docs/                     # Memoria del proyecto: plan, decisiones, bitácora
├── src/ojo_ciudadano/
│   ├── ingesta/              # Un módulo por fuente (portal_cm, placsp, bdns, ...)
│   ├── normalizacion/        # NIF, alias, UTE, deduplicación
│   ├── modelo/               # Esquema DuckDB y carga
│   ├── indicadores/          # Ejecutor de los SQL de indicadores y puntuación
│   ├── anomalias/            # Detección de anomalías con aprendizaje automático (D-021)
│   ├── asistente/            # Agente, herramientas texto a SQL y RAG
│   └── app/                  # Streamlit
├── sql/
│   ├── esquema/              # DDL del modelo unificado (congelado el 17-nov)
│   └── indicadores/          # r01_licitador_unico.sql, r02_..., uno por indicador
├── tests/                    # pytest, con datos sintéticos pequeños
└── data/                     # (ignorado por git) raw/, interim/, ojo_ciudadano.duckdb
```

## Modelo de datos (propuesta para congelar en H1, 17 de noviembre)

El DDL está en [`sql/esquema/001_tablas.sql`](../sql/esquema/001_tablas.sql) y la base se regenera con:

```bash
uv run python -m ojo_ciudadano.modelo.carga
```

| Tabla | Una fila por | Clave | Notas |
| --- | --- | --- | --- |
| `organo` | Órgano de contratación | `organo_id` = nombre normalizado (mayúsculas, sin tildes) | Lleva consejería, jerarquía y, si existe, el código de PLACSP |
| `adjudicatario` | Empresa, UTE o persona física seudonimizada | `adjudicatario_id` = NIF, `UTE:…` o `PF-…` | Las personas físicas no llevan NIF ni nombre (D-007) |
| `contrato` | Contrato o licitación de una fuente | `contrato_id` = `placsp:<n>` o `portal_cm:<referencia>` | `duplicado_de` enlaza la fila del portal con la de PLACSP cuando es la misma licitación |
| `adjudicacion` | Adjudicatario de un contrato (uno por lote) | `contrato_id` + `orden` | Nº de ofertas, importes, modificaciones y prórrogas |
| `contrato_unico` (vista) | Contrato sin repetir entre fuentes | — | `contrato` donde `duplicado_de` está vacío |

Reglas del modelo:

- Toda tabla de hechos lleva `fuente`, `url_origen` y `fecha_descarga`.
- **Los importes no se mezclan**: PLACSP los da sin IVA (`…_sin_iva`) y el portal regional con IVA (`…_con_iva`). Cada columna dice su base (P-10).
- Dos filas son el mismo contrato si coinciden **expediente y órgano**. De PLACSP se conserva la última versión de cada expediente y órgano. Los menores solo existen en el portal.
- El órgano se identifica por su nombre normalizado porque el CSV del portal no trae código. Si un órgano cambia de nombre aparecerá como dos órganos (limitación conocida).

Primera carga con datos reales (2026-11-17): 131 órganos, 28.045 adjudicatarios (5.070 personas físicas seudonimizadas), 1.371.693 contratos (17.589 de PLACSP, 36.029 licitaciones y adjudicaciones sin publicidad del portal —17.252 marcadas como duplicadas de PLACSP— y 1.318.075 menores) y 1.404.789 adjudicaciones. Tarda unos 3 minutos; el fichero ocupa unos 350 MB.

Personas físicas: además de los DNI y NIE válidos, se tratan como físicas las formas con errata habituales en las fuentes (DNI sin el cero inicial, `1234567L`; NIE con una cifra de más). Algunos NIF-IVA extranjeros con la misma forma (p. ej. irlandeses) quedan también ocultos: prima la privacidad (D-007). Con esta regla, la carga del 20-nov tiene 5.095 personas físicas seudonimizadas (25 más que el 17-nov). La interfaz vuelve a filtrar por la forma del NIF por si la base es anterior.

Seudónimos: se calculan con una sal secreta (`SEUDONIMO_SAL` en `.env`, o `data/.sal_seudonimos` si no está definida). **Todo el equipo debe usar la misma sal** para que los identificadores `PF-…` coincidan entre máquinas; nunca se sube al repositorio.

### Resultados de los indicadores

Tabla derivada `indicador_resultado`, que se regenera entera (unos 10 segundos) con:

```bash
uv run python -m ojo_ciudadano.indicadores.ejecutor
```

El ejecutor (`src/ojo_ciudadano/indicadores/ejecutor.py`) crea las funciones de `sql/indicadores/000_funciones.sql` y une el resultado de cada `sql/indicadores/rXX_*.sql`. Cada indicador devuelve una fila por contrato **aplicable** con `contrato_id`, `indicador`, `aplicable`, `activado`, `valor`, `motivo` y `url_origen`. Si un contrato no aparece para un indicador, ese indicador **no le es aplicable** y no cuenta en la puntuación. `contrato_id` siempre es el de `contrato_unico`: si la licitación está en las dos fuentes, se usa el de PLACSP. Para la interfaz, a las personas físicas (`PF-…`) que aparecen en alertas de R-03 se les aplica D-007: se muestran agregadas, nunca con ficha.

Pendiente de añadir antes o después de congelar (requiere acuerdo del equipo): concesiones de subvenciones (BDNS), miembros de UTE como tabla propia, documentos para el corpus.

Cuando el equipo lo congele, cambiarlo requiere decisión registrada, porque bloquea al resto.

## Interfaz (Streamlit)

`uv run streamlit run src/ojo_ciudadano/app/main.py`. `app/main.py` define la navegación y la cabecera (fecha de descarga de cada fuente, aviso de metodología y qué mide cada indicador); `app/paginas/` tiene una pantalla por fichero (`alertas.py`, `empresa.py`, `organo.py`, `mapa.py`, `preguntas.py`); `app/datos.py` reúne todas las consultas (solo lectura, con tests en `tests/app/`); `app/textos.py` guarda los textos fijos revisados para el lenguaje no acusatorio. Las pantallas leen `puntuacion_*` e `indicador_resultado` de `data/ojo_ciudadano.duckdb`, que hay que regenerar con el ejecutor de indicadores.

## Asistente

`src/ojo_ciudadano/asistente/`: `sql_seguro.py` valida y ejecuta el SQL de solo lectura (conexión sin acceso a ficheros) y `consultas_demo.py` guarda las consultas verificadas de las preguntas de demo. Detalle y reglas en [05-asistente.md](05-asistente.md).
