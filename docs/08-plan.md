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
- [x] Revisar licencias y avisos legales de reutilización (P-03). Resuelto el 21-nov (ver 02, «Condiciones de reutilización»).
- [x] Descargar una muestra del Atom de PLACSP filtrada a órganos de la Comunidad de Madrid (octubre de 2026).
- [x] Probar la API de la BDNS con concesiones de la Comunidad. Resuelto el 20-nov: filtro por los 27 órganos hijos de la Comunidad (id 16); 849.878 concesiones 2023–2026 cargadas.
- [ ] Decidir proveedor de LLM (D-010). Aplazado el 16-nov: no bloquea datos ni indicadores.
- [x] Asignar nombres a las personas 1–4 de la tabla de responsables. Hecho el 21-nov según el trabajo ya hecho: Ignacio e Ismael.

## Responsables

| Persona | Nombre | Responsabilidad | Entregable para el 21 de noviembre |
| --- | --- | --- | --- |
| 1 | Ismael (contratos); Ignacio (subvenciones, BDNS) | Ingesta y normalización | Contratos 2023–2026 y subvenciones de la Comunidad en DuckDB, deduplicados y con NIF normalizado |
| 2 | Ismael (motor, R-01, R-02, R-03, R-05); Ignacio (R-04, R-06, puntuación D-020) | Indicadores de riesgo | Cinco indicadores de prioridad alta y media en SQL, con puntuación por contrato, órgano y empresa |
| 3 | Ignacio | Interfaz | Mapa del dinero, ficha de empresa, ficha de órgano y panel de alertas en Streamlit |
| 4 | Ignacio | Asistente | Agente con texto a SQL y RAG sobre un corpus pequeño, respondiendo bien a las 4 preguntas de demo |
| 5 | Ismael (con Claude) | Detección de anomalías (D-021) | Para el 23-nov: tabla `anomalia_resultado` con contratos atípicos respecto a sus pares (no supervisado por defecto), con las variables que lo explican y su test |

## Accesibilidad y visualización (D-023)

Tareas A-01 a A-11 en [11-accesibilidad.md](11-accesibilidad.md). Para la demo del 24-nov: A-01 (portada), A-02 (qué mide cada señal), A-03 (panel de alertas con un gráfico por señal), A-05 (ficha de empresa), A-10 y A-11 (revisión y prueba con personas no expertas). El resto, si da tiempo; el 25 no se añaden funciones.

## Qué recortamos si vamos tarde, en este orden

1. **Detección de anomalías con aprendizaje automático** (D-021): quedan solo los indicadores en SQL.
2. **RAG documental**: el asistente queda solo con texto a SQL.
3. **Extracción de PDFs con IA**: solo campos estructurados.
4. **Indicadores de prioridad baja** (R-07 plazo corto, R-08 opacidad documental).
5. **Subvenciones**: el MVP se queda solo con contratos.

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
| 19-nov | 2 | Motor de indicadores y cuatro indicadores implementados con test: R-01 (39,4 % de 20.693 licitaciones), R-02 (31,0 % de 36.297), R-03 (16,9 % de 1,32 M de menores) y R-05 (1,8 % de 31.406). D-015 corrige R-03 (se activaba en el 85 %) y D-016 fija R-05 sin prórrogas. Cubierto el mínimo de «≥3 indicadores». **Pendiente:** R-04, puntuación por contrato, órgano y empresa; H1 cerrado con D-017. |
| 19-nov | 2 | Aceptada D-017: esquema v1 congelado (H1 cumplido, con dos días de retraso). Rama `feat/indicadores-r01-r03-r05` con R-01, R-02, R-03 y R-05 pendiente de PR a `main`. |
| 19-nov (tarde) | 2 | R-04 implementado con test (D-018): 84 contratos activados de 1.348.715. Cinco indicadores listos (R-01 a R-05) para el H2. **Pendiente:** R-06, puntuación por contrato, órgano y empresa. |
| 19-nov (noche) | 2 | R-06 implementado con test (D-019): 2.226 activados de 11.909. Seis indicadores (R-01 a R-06), por encima del mínimo del H2. **Pendiente:** puntuación por contrato, órgano y empresa. |
| 19-nov (noche) | 2 | Puntuación por contrato, órgano y empresa (D-020), incluida en el ejecutor. Entregable de la persona 2 para el H2 completo. **Pendiente:** PR a `main`, revisión por el equipo e interfaz sobre estas tablas. |
| 19-nov (noche) | 2 | Primera interfaz Streamlit sobre las tablas `puntuacion_*`: **panel de alertas** y **ficha de empresa** (rama `feat/app-empresa-alertas`), con aviso de metodología, fecha de datos y enlace al origen en cada contrato. **Pendiente:** ficha de órgano, mapa del dinero, asistente, subvenciones. |
| 19-nov (noche) | 2 | **Ficha de órgano** (rama `feat/app-organo`): puntuación y posición frente a los demás órganos, indicadores del órgano frente al total, evolución anual, procedimientos y principales empresas. Con esto hay tres pantallas de las cuatro del H3. **Pendiente:** mapa del dinero, asistente, subvenciones. |
| 19-nov (noche) | 2 | **Mapa del dinero** (Sankey órgano → empresa, por fuente, año y tipo, con enlace a cada contrato) y primera revisión con `revisor-legal` aplicada a la interfaz (rama `feat/app-mapa-dinero`). **Las cuatro pantallas del H3 existen.** Pendiente: asistente, subvenciones, textos de motivo de R-02, R-03 y R-05, y datos reales de licencia (P-03). |
| 20-nov | 2 | Motivos de R-02, R-03 y R-05 matizados según la revisión legal (rama `fix/motivos-revision-legal`, sobre `feat/app-mapa-dinero`). Cifras de los indicadores sin cambios. **Pendiente:** asistente, subvenciones, DNI/NIE en búsquedas y listados, fecha de descarga por fuente, licencias (P-03). |
| 20-nov (tarde) | 2 | Pendientes de la revisión legal en la interfaz (rama `fix/pendientes-revision-legal`): DNI sin el cero inicial y NIE con erratas pasan a persona física en la normalización (25 personas que se mostraban con nombre y DNI) y la interfaz filtra por la forma del NIF; fecha de descarga de cada fuente; ayuda de cada indicador (incluida R-06), revisada con `revisor-legal`; motivo de R-04 con «Un adjudicatario». Base regenerada; cifras de indicadores sin cambios. **Pendiente:** asistente (D-010), subvenciones, licencias (P-03), responsable de D-021. |
| 20-nov (noche) | 2 | **Asistente, parte sin LLM** (rama `feat/asistente-sql`): validador y ejecutor de SQL de solo lectura (lista blanca de tablas sobre el árbol de `json_serialize_sql`; conexión sin acceso a ficheros, también para toda la interfaz), consultas verificadas de las 4 preguntas de demo y pantalla «Preguntas guiadas», revisada con `revisor-legal`. La pregunta 4 solo cubre contratos (faltan subvenciones). **Pendiente:** cerrar D-010 para conectar el modelo, batería de 20 preguntas, subvenciones. |
| 20-nov (noche) | 2 | **Subvenciones (BDNS)** (rama `feat/ingesta-bdns`): descarga por meses, ampliación aditiva `sql/esquema/002_subvenciones.sql` (tabla `concesion`, D-017), 849.878 concesiones 2023–2026 de 132 órganos (750.424 a personas físicas, seudonimizadas sin nombre). Empresas enlazadas por NIF con sus contratos (2.863 tienen ambos). Pregunta 4 de la demo y ficha de empresa con subvenciones. **Pendiente:** aviso legal de la BDNS (P-03). |
| 20-nov (noche) | 2 | **Subvenciones en la ficha de órgano y en el mapa del dinero** (rama `feat/subvenciones-organo-mapa`): resumen, convocatorias y entidades con más importe por órgano; BDNS como tercera fuente del mapa, con las personas físicas en un único flujo agregado por órgano (y convocatorias con menos de 5 concesiones agrupadas). Revisado con `revisor-legal`. **Pendiente:** D-010, D-021, P-03. |
| 21-nov | 2 | **Detección de anomalías (D-021)** (rama `feat/anomalias`): Isolation Forest por grupo de pares (fuente · licitación o menor · tipo), tabla `anomalia_resultado`, pantalla «Contratos atípicos» y aviso en el panel de alertas; revisado con `revisor-legal`. 13.496 atípicos de 1,35 M (1 %), el 76 % sin ningún indicador activado. Entregable del 23-nov adelantado. **Pendiente:** validarlo con casos de la Cámara de Cuentas antes de pensar en meterlo en la puntuación. |
| 21-nov | 2 | **P-03 resuelta** (rama `fix/licencias-p03`): condiciones de reutilización de portal regional, PLACSP, BDNS y CKAN documentadas; pie de la interfaz con la cita de la IGAE para las subvenciones, sin sugerir patrocinio, con la seudonimización explicada y la fecha de descarga de la BDNS. Revisado con `revisor-legal`. P-05 con los criterios del jurado. **Pendiente:** P-09 (licencia del código, pesa en el criterio de código abierto), D-010. |
| 21-nov | 2 | **Menores recientes incompletos** (rama `fix/aviso-menores-recientes`, P-12): jul–sep 2026 tienen ~3.000 menores al mes frente a ~20.000; probable retraso de publicación trimestral (art. 63.4 LCSP). Aviso en las evoluciones anuales de empresa y órgano y en el mapa con menores. **Pendiente:** reexportar los menores de jul–nov 2026 antes de la entrega. |
| 21-nov | 2 | **Batería de 20 preguntas del asistente** (rama `feat/bateria-preguntas`): 4 de demo, 12 de datos con SQL de referencia y 4 de límites (lenguaje, RGPD, fuera de alcance, inyección), con criterios de respuesta y función `evaluar` que compara el SQL del modelo con la referencia. Hallazgo: las licitaciones del portal casi nunca traen fecha. **Pendiente:** D-010 para conectar el modelo y pasarle la batería. |
| 21-nov | 2 | **UTE con personas físicas** (rama `fix/ute-personas-fisicas`, hallazgo de la revisión legal de D-021): la UTE con algún miembro persona física pasa a persona física sin nombre en la normalización; la interfaz y el asistente ocultan también los `UTE:PF-…` de bases antiguas. Base regenerada. |
| 21-nov | 2 | **Adjudicatarios «otro» sin ficha salvo empresas** (rama `fix/otros-sin-ficha`, D-007): los NIF extranjeros o erróneos solo tienen ficha si el nombre lleva una forma jurídica; quedan fuera 981 de 2.803, entre ellos empresarios individuales y particulares con nombre propio. P-07 cerrada. |
| 21-nov | 2 | **Agente del asistente sin depender del proveedor** (rama `feat/asistente-agente`): instrucciones del modelo con reglas, limitaciones de los datos, esquema leído de la base y ejemplos; bucle de SQL validado con corrección de errores; retención de respuestas con DNI, lenguaje acusatorio o cifras sin consulta; pantalla «Asistente» con chat, datos y SQL. Revisado con `revisor-legal`. **Pendiente:** D-010, que se reduce a escribir el adaptador del proveedor, y pasarle la batería. |
| 21-nov | 2 | **Identidad visual (D-022)** (rama `feat/diseno`): logo vectorial, tema oscuro con acento azul, navegación con iconos, menos texto en pantalla y prohibición de emojis (regla 7 de CLAUDE.md, con test). |
| 21-nov | 2 | **Accesibilidad (D-023), A-01 a A-03** (rama `feat/accesibilidad-alertas`): portada nueva con cifras grandes, tres puertas de entrada y una tarjeta por señal; «Contratos a revisar» con el nombre de cada señal, filtro por señal e interruptor de menores; un gráfico por señal (E-01 a E-06) con su frase en lenguaje claro. Revisado con `revisor-legal`. |
| 21-nov | 2 | **Ficha de empresa visual (D-023, A-05)** (rama `feat/accesibilidad-empresa`): cifras, mapa de áreas por organismo por fuente, contratos por año con y sin señales, señales de la empresa y contratos desplegables con su gráfico por señal. |
| 21-nov | 2 | **Ficha de organismo visual (D-023, A-06)** (rama `feat/accesibilidad-organo`): mapa de áreas de las 20 empresas con más importe por fuente (personas físicas agregadas), comparación por señal frente a todos los organismos, vías de contratación en lenguaje llano, contratos por año y contratos a revisar del organismo. |
| 21-nov | 2 | **Mapa del dinero en burbujas (D-023, A-07)** (rama `feat/accesibilidad-mapa`): burbujas de los organismos que más adjudican, red de cada organismo con sus 10 empresas (área y grosor = importe) y el diagrama de flujos como vista avanzada. |
| 21-nov | 2 | **Contratos atípicos visuales (D-023, A-04)** (rama `feat/accesibilidad-atipicos`): cada contrato atípico frente a una muestra de sus pares (nube de puntos o histograma). La detección guarda `anomalia_variables`. |
| 21-nov | 2 | **Respuestas con gráfico (D-023, A-08)** (rama `feat/accesibilidad-preguntas`): gráfico automático según el tipo de resultado y frase resumen en «Preguntas guiadas»; listo para el asistente. |
| 21-nov | 2 | **Revisión de accesibilidad y glosario (D-023, A-09, A-10, guion de A-11)** (rama `fix/accesibilidad-revision`): contraste medido (todo AA; el gris de las barras sube a 3,5:1), etiqueta además de color en E-01, definiciones en la ayuda de los términos clave, guion para la prueba con personas no expertas. **Pendiente:** hacer la prueba A-11 y la pasada final de A-10 el 24-25. |
| 21-nov (cierre) | 2 | Resumen del día y pasos para retomar en [`bitacora/2026-11-21-cierre-del-dia.md`](bitacora/2026-11-21-cierre-del-dia.md). **H2:** entregables de las personas 1, 2 y 3 hechos; la 4 (asistente) espera a D-010; detección de anomalías (D-021) adelantada. **Siguiente:** D-010, P-09, prueba A-11 antes del H3 (24-nov). |
| 23-nov | 2 | **Contexto de la Comunidad de Madrid (D-024)** (rama `feat/datos-cm-abiertos`): 32 ficheros del catálogo de datos abiertos y del Portal de Transparencia, cinco tablas nuevas (`serie_cm`, `presupuesto_organo`, `convenio`, `entidad_registro`, `plantilla_organismo`), pantalla «Presupuesto y contexto», presupuesto en la ficha de órgano y registros en la ficha de empresa. **Todo el equipo debe bajar los datos antes de seguir: [LO-PRIMERO.md](LO-PRIMERO.md)** (contador de confirmaciones). |
| 23-nov | 2 | **Mapa general del dinero y mapa de nodos arrastrable (D-026)** (rama `feat/datos-cm-abiertos`): pantalla principal con la Comunidad y sus consejerías (tamaño y color = dinero, relleno = gastado), recorrido hasta cada contrato con su ficha, y componente de nodos reutilizado en el «Mapa del dinero». Nueva dependencia `streamlit-agraph` (`uv sync`). |
| 23-nov | 2 | **Fuentes externas candidatas** (rama `docs/fuentes-externas`, solo investigación): 8 fuentes estudiadas en [13-fuentes-externas.md](13-fuentes-externas.md). Viables: recursos del TACPCM, referencias de licitador único (OIReScon: 45,5 % de los lotes autonómicos en 2025, frente al 39,4 % de R-01), DIR3 y fondos europeos (ya en el Atom de PLACSP, 991 expedientes). Descartadas: prohibiciones de contratar, EDES, deudores de la AEAT y CNMC (solo manual). Hallazgo de calidad: filas de relleno con el NIF de la Comunidad como «adjudicatario» (35,2 M€). **Pendiente:** que el equipo decida qué se incorpora antes del H3. |
| 23-nov (tarde) | 2 | **Datos: más cobertura y calidad (D-027 a D-029)** (rama `fix/relleno-y-referencia-r01`): menores de jul–sep de 2026 reexportados (+15.829, P-12); **encargos a medios propios** (944 de 2023–2026, 369,6 M€) en `encargo`; **recursos del TACPCM** (1.097) en `recurso_especial`; fondos europeos en `contrato_financiacion` (966 licitaciones); filas de relleno fuera de los adjudicatarios; noviembre de PLACSP y octubre–noviembre de la BDNS actualizados. Todo fuera de la puntuación salvo el efecto de los datos nuevos en los indicadores. **Pendiente:** mostrar encargos, recursos y fondos europeos en la interfaz; regenerar la base en cada máquina. |
