# 08 · Plan de trabajo hasta el 26 de noviembre de 2026

> **Este es el plan. Se respeta en la medida de lo posible.** Cualquier desviación (alcance, fechas, tecnología, responsables) se registra en [decisions.md](decisions.md) y se refleja aquí. Al empezar cada sesión, compara lo que vas a hacer con este documento; al terminar, actualiza el estado.

Cuatro fases en 11 días, con hitos internos que protegen la entrega: **esquema de datos congelado el 17** y **demo funcional el 24**.

## Hitos

| ID | Fecha | Hito | Criterio de cumplido | Estado |
| --- | --- | --- | --- | --- |
| H1 | 17-nov | Esquema de datos y alcance del MVP **congelados** | DDL en `sql/esquema/` + muestra de datos limpia compartida + preguntas P-01/P-02 resueltas | Cumplido el 19-nov (D-017) |
| H2 | 21-nov | Entregables por persona | Ver tabla de responsables | Pendiente |
| H3 | 24-nov | **Demo funcional** de extremo a extremo | Las 4 preguntas de demo funcionan; las 4 pantallas muestran datos reales | Pendiente |
| H4 | 26-nov | **Entrega** a DataMad 2026 | Proyecto enviado según las bases | Pendiente |

## Fases

> La propuesta original incluía un diagrama del plan (4 fases, 3 hitos) que no se ha conservado. Estas fases se reconstruyen a partir de las fechas y entregables del texto; si el equipo las ajusta, se registra en `decisions.md`.

| Fase | Fechas | Objetivo | Salidas |
| --- | --- | --- | --- |
| 1 · Datos y alcance | 15 – 17 nov | Confirmar catálogo, licencias y campos; descargar muestras; fijar esquema y MVP | Respuestas a P-01..P-05; esquema congelado (H1); muestra limpia para trabajar en paralelo |
| 2 · Construcción en paralelo | 18 – 21 nov | Cada persona construye su pieza sobre el esquema fijado | Entregables de H2 |
| 3 · Integración | 22 – 24 nov | Unir pipeline, indicadores, interfaz y asistente con datos reales | Demo funcional (H3) |
| 4 · Pulido y entrega | 25 – 26 nov | **El 25 no se añaden funciones**: solo correcciones, vídeo de respaldo y presentación | Entrega (H4) |

### Tareas del día 1 (Fase 1)

- [x] Revisar el Catálogo de Datos Abiertos (CKAN): qué datasets de contratos y presupuesto hay (P-01). Sin contratos a nivel de registro.
- [x] Exportar un CSV del Portal de la Contratación Pública y comprobar si trae el número de licitadores (P-02). Sí lo trae; exportados licitaciones, sin publicidad y menores 2023–2026.
- [ ] Revisar licencias y avisos legales de reutilización (P-03).
- [x] Descargar una muestra del Atom de PLACSP filtrada a órganos de la Comunidad de Madrid (octubre de 2026).
- [ ] Probar la API de la BDNS con concesiones de la Comunidad. La API responde; falta el filtro de la Comunidad de Madrid.
- [ ] Decidir proveedor de LLM (D-010). Aplazado el 16-nov: no bloquea datos ni indicadores.
- [ ] Asignar nombres a las personas 1–4 de la tabla de responsables.

## Responsables

| Persona | Nombre | Responsabilidad | Entregable para el 21 de noviembre |
| --- | --- | --- | --- |
| 1 | _por asignar_ | Ingesta y normalización | Contratos 2023–2026 y subvenciones de la Comunidad en DuckDB, deduplicados y con NIF normalizado |
| 2 | _por asignar_ | Indicadores de riesgo | Cinco indicadores de prioridad alta y media en SQL, con puntuación por contrato, órgano y empresa |
| 3 | _por asignar_ | Interfaz | Mapa del dinero, ficha de empresa, ficha de órgano y panel de alertas en Streamlit |
| 4 | _por asignar_ | Asistente | Agente con texto a SQL y RAG sobre un corpus pequeño, respondiendo bien a las 4 preguntas de demo |

## Qué recortamos si vamos tarde, en este orden

1. **RAG documental**: el asistente queda solo con texto a SQL.
2. **Extracción de PDFs con IA**: solo campos estructurados.
3. **Indicadores de prioridad baja** (R-07 plazo corto, R-08 opacidad documental).
4. **Subvenciones**: el MVP se queda solo con contratos.

Aplicar un recorte = registrar decisión en `decisions.md`.

## Lo que NO se recorta

- Datos limpios de contratos.
- Al menos **tres indicadores**.
- **Ficha de empresa**.
- **Enlace al origen en cada cifra**.

## Fuera de alcance hasta el 26 de noviembre

Todo lo marcado «tras el datatón» o «largo plazo» en [01-vision.md](01-vision.md#posibilidades-más-allá-del-datatón): otras administraciones, comparativa entre comunidades, OCDS, alertas por suscripción, API pública, Registro Mercantil, herramienta interna.

## Estado actual

| Fecha | Fase | Resumen |
| --- | --- | --- |
| 15-nov | 1 | Repositorio, entorno (uv), estructura para agentes y documentación del plan inicial creados. Desarrollo sin empezar. |
| 16-nov | 1 | Fuentes exploradas con datos reales: P-01 y P-02 resueltas. Descargados del portal regional licitaciones, sin publicidad y 1,32 M de menores (2023–sep 2026). Aceptadas D-012 (PLACSP principal) y D-014 (definición de R-03 sin CPV y con IVA); D-010 aplazada. **Sin código de ingesta ni esquema todavía: H1 (17-nov) en riesgo.** |
| 17-nov (madrugada) | 1 | Ingesta de PLACSP y del CSV del portal, normalización y seudonimización, propuesta de esquema (`sql/esquema/001_tablas.sql`) y primera carga real en DuckDB (1,37 M de contratos). P-06 y P-11 resueltas. **Falta para H1:** que el equipo revise y congele el esquema; subvenciones (BDNS) sin incorporar. |
| 19-nov | 2 | Aceptada D-017: esquema v1 congelado (H1 cumplido, con dos días de retraso). Rama `feat/indicadores-r01-r03-r05` con R-01, R-02, R-03 y R-05 pendiente de PR a `main`. |
