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
│   ├── asistente/            # Agente, herramientas texto a SQL y RAG
│   └── app/                  # Streamlit
├── sql/
│   ├── esquema/              # DDL del modelo unificado (congelado el 17-nov)
│   └── indicadores/          # r01_licitador_unico.sql, r02_..., uno por indicador
├── tests/                    # pytest, con datos sintéticos pequeños
└── data/                     # (ignorado por git) raw/, interim/, ojo_ciudadano.duckdb
```

## Modelo de datos (borrador, se congela el 17 de noviembre)

Entidades mínimas: **órgano** (código de órgano), **empresa/beneficiario** (NIF normalizado; personas físicas seudonimizadas), **contrato** (expediente + órgano, procedimiento, CPV, importes base/adjudicado/final, fechas, nº ofertas si existe, URL de origen), **modificación/prórroga**, **concesión de subvención**, **UTE ↔ miembros**, **documento** (para el corpus).

Toda tabla de hechos lleva `fuente`, `url_origen` y `fecha_descarga`.

El esquema definitivo se documentará aquí y en `sql/esquema/` cuando se congele (hito H1). A partir de ahí, cambiarlo requiere decisión registrada, porque bloquea al resto del equipo.
