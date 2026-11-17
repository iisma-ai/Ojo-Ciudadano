# 02 · Fuentes de datos

El núcleo son los **contratos de la Comunidad de Madrid**; subvenciones, presupuesto y altos cargos los completan. Todas las fuentes son públicas y reutilizables.

## Inventario

| ID | Fuente | Qué contiene | Formato y acceso | Papel | Limitaciones |
| --- | --- | --- | --- | --- | --- |
| F-01 | [Portal de la Contratación Pública de la Comunidad de Madrid](https://contratos-publicos.comunidad.madrid/contratos) | Licitaciones, adjudicaciones sin publicidad, contratos menores, encargos; importes de modificaciones, prórrogas y liquidación | Buscador con exportación a CSV **protegida por captcha** y limitada a 50.000 filas; no descargable por código | **Complemento** (propuesta D-012): menores e importes de modificaciones y prórrogas | Sin CPV, sin fechas de publicación, sin lotes ni código de órgano; importes con IVA; ver detalle |
| F-02 | [Plataforma de Contratación del Sector Público (PLACSP)](https://www.hacienda.gob.es/es-ES/GobiernoAbierto/Datos%20Abiertos/Paginas/LicitacionesAgregacion.aspx) | Las licitaciones regionales, agregadas con otras plataformas autonómicas | Zip mensuales de ficheros Atom (`PlataformasAgregadasSinMenores_AAAAMM.zip`, unos 15 MB/mes), descarga abierta | **Fuente principal de licitaciones** (propuesta D-012): nº de ofertas, NIF, CPV, lotes, jerarquía de órganos | No trae contratos menores ni modificaciones/prórrogas; varias versiones por expediente → deduplicar; ver detalle |
| F-03 | [Base de Datos Nacional de Subvenciones (BDNS)](https://www.pap.hacienda.gob.es/sitios/pap/es-ES/Documents/Notainformativa-PremioASEDIEalSNPSAP.pdf) | Convocatorias y concesiones de todas las administraciones | API REST en JSON; también CSV y XLSX | Segundo flujo de dinero: órgano → beneficiario | Personas físicas protegidas; descargas grandes hay que trocearlas |
| F-04 | [Portal de Transparencia](https://www.comunidad.madrid/transparencia/taxonomy/term/8522) | Altos cargos (retribuciones, bienes), personal eventual, RPT, convenios, publicidad institucional | Fichas web y ficheros descargables | Contexto organizativo y gasto en publicidad | Formatos heterogéneos; poca serie histórica estructurada |
| F-05 | [Presupuestos Generales](https://comunidad.madrid/sites/default/files/gobierno_abierto/2024-presupuesto-libro-08-ejecucion-liquidacion.pdf) | Crédito y ejecución por sección, centro, programa y capítulo | Libros en PDF; posibles ficheros en el catálogo | Escala: qué parte del presupuesto de cada órgano pasa por contratos | Sin enlace directo partida → contrato |
| F-06 | [Catálogo de Datos Abiertos de la Comunidad de Madrid](https://datos.comunidad.madrid) | **Base obligatoria del concurso** | CKAN (API en `/api/action/`) | Contexto y validación de totales: presupuestos por órgano, agregados de contratos, altos cargos, RPT | **No tiene contratos fila a fila** (P-01 resuelta); ver detalle |

Otras referencias útiles:
- [Guía de publicación en el perfil de contratante e interconexión con PLACSP](https://gestiona3.madrid.org/bvirtual/BVCM015814.pdf): explica cómo el portal regional vuelca en PLACSP (clave para deduplicar F-01/F-02).

## Detalle por fuente (explorado el 2026-11-16)

### F-06 · Catálogo de Datos Abiertos (CKAN)

- 2.276 datasets (recorrido completo por la API el 2026-11-16). Licencia indicada: Creative Commons Attribution.
- **Ninguno contiene contratos ni subvenciones a nivel de registro.** Lo relevante es agregado:
  - `1914620`, `1914621`, `1933725`: contratos administrativos por tipo, forma y procedimiento de adjudicación (estadística).
  - `presupuestos_liquidados_gastos_consolidados_por_organo_y_fase_ejecucion` y otros de presupuestos iniciales y liquidados.
  - `1501018` (altos cargos), `relacion_puestos_trabajo`, `registro_transparencia`.
- Uso previsto: escala presupuestaria por órgano y validación cruzada de nuestros totales de contratos. Pendiente de incorporar al pipeline.

### F-02 · PLACSP, plataformas agregadas

- URL de cada mes: `https://contrataciondelsectorpublico.gob.es/sindicacion/sindicacion_1044/PlataformasAgregadasSinMenores_AAAAMM.zip`. Responde a una petición GET normal; las peticiones HEAD se cortan.
- Las entradas de la Comunidad de Madrid se reconocen porque su `link` apunta a `contratos-publicos.comunidad.madrid`. Muestra de octubre de 2026: 3.423 entradas, 1.731 expedientes distintos (822 con más de una versión en el mes).
- Campos comprobados en esa muestra: expediente (`ContractFolderID`), código de órgano (`ID_OC_PLAT`) y jerarquía (consejería → … → órgano), CPV y presupuesto base sin IVA en el 100 %, tipo de contrato, procedimiento, fechas de fin de plazo, documentos (pliegos) y, en los resultados, **nº de ofertas en el 100 %** (`ReceivedTenderQuantity`), NIF del adjudicatario, lote e importe de adjudicación sin IVA.
- Carencias: sin contratos menores, sin modificaciones ni prórrogas, sin fecha de adjudicación en el resultado (sí la de formalización, cuando la hay).
- **El importe de adjudicación falta en parte de los resultados**: en octubre de 2026, tras quedarse con la última versión de cada expediente, 775 de 2.164 resultados formalizados y 703 de 1.281 adjudicados no lo traen. Casi todos son resultados sin número de lote. Para esos contratos el importe hay que tomarlo del CSV del portal (con IVA).
- Módulo de ingesta: `src/ojo_ciudadano/ingesta/placsp.py` (descarga con caché en `data/raw/placsp/`, una petición cada vez). Las listas de códigos de procedimiento, tipo, estado y resultado se tomaron de `https://contrataciondelestado.es/codice/cl/` el 2026-11-16; la de resultados está en inglés y la traducción es nuestra.
- Descargados los 47 zip de enero de 2023 a noviembre de 2026 (494 MB en `data/raw/placsp/`, fuera de git) el 2026-11-16. Tras quedarse con la última versión de cada expediente y órgano quedan **17.589 licitaciones** de la Comunidad de Madrid.
- **Cruce con el portal** (por expediente y órgano): 17.244 de las 17.589 tienen su fila en el CSV del portal. Los fallos se deben sobre todo a nombres de órgano escritos de forma distinta en cada fuente («Hospital Dr. Rodríguez Lafora» / «Hospital Universitario Dr. Rodríguez Lafora», consejerías renombradas).

### F-01 · Portal de la Contratación Pública (exportación CSV)

- La exportación exige resolver una pregunta matemática (captcha) y está limitada a 50.000 filas. **No se automatiza el captcha**: lo resuelve una persona; la preparación de filtros y la descarga se hicieron con el navegador asistido (Claude in Chrome) el 2026-11-16.
- Módulo de ingesta: `src/ojo_ciudadano/ingesta/portal_cm.py` (lee todos los CSV de `data/raw/portal_cm/`; los 44 ficheros se procesan en unos 6 segundos).
- Hay que llegar a la exportación desde la página de resultados (el portal toma los filtros de la sesión de búsqueda). El filtro de fechas del buscador avanzado exige formato `dd-mm-aaaa`. Para menores se usó «Fecha del contrato o encargo».
- Ficheros descargados en `data/raw/portal_cm/` (494 MB, fuera de git):

| Fichero | Contenido | Contratos |
| --- | --- | --- |
| `licitaciones_todo_2026-11-16.csv` | «Convocatoria anunciada a licitación», todos los años | 24.796 |
| `sin_publicidad_todo_2026-11-16.csv` | «Contratos adjudicados por procedimientos sin publicidad», todos los años | 11.333 |
| `menores_AAAA-MM-DD_AAAA-MM-DD.csv` (42 ficheros) | Contratos menores con fecha de contrato de 2023-01-01 a 2026-09-30 | 1.317.983 |
| `muestras_por_texto/` | Dos búsquedas por palabra, solo para explorar el formato | — |

- Menores por año: 443.460 (2023), 387.924 (2024), 349.726 (2025), 136.873 (2026). Sin referencias repetidas entre ficheros. **Julio–septiembre de 2026 están incompletos en origen** (3.565, 2.312 y 3.218 frente a unos 20.000 de un mes normal) y no hay menores con fecha posterior: parecen publicarse con retraso (P-12).
- 36 contratos aparecen en el fichero del periodo anterior al de su fecha (un día de desfase en el filtro del portal); no hay duplicados dentro de la ventana.
- Columnas (18): tipo de publicación, estado, entidad adjudicadora (nombre con jerarquía separada por `··>`), nº de expediente, referencia, título, tipo de contrato, procedimiento, presupuesto de licitación, nº de ofertas, resultado, NIF y nombre del adjudicatario, fecha del contrato, importe de adjudicación, importes de modificaciones, prórrogas y liquidación.
- `https://contratos-publicos.comunidad.madrid/contrato/<Referencia>` devuelve la ficha oficial (comprobado con 5 referencias) → sirve de `url_origen`.
- Problemas de calidad vistos:
  - **Importes con IVA** (PLACSP los da sin IVA); el CSV no trae el importe sin IVA (P-10).
  - Sin CPV, sin fecha de publicación, sin número de lote, sin código de órgano.
  - En licitaciones, los adjudicatarios adicionales van en filas de continuación sin cabecera (24.383 en el fichero de licitaciones).
  - «Fecha del contrato» vacía en 15.239 de 24.796 licitaciones; fechas en texto («11 de febrero del 2026») y algunos años imposibles.
  - Formatos de importe mezclados (`130680.0` y `3.630,00`), variantes de tipo de contrato («Suministro», «Suministros», «SERVICIOS»).
  - NIF con prefijos (`ES…`, `NIF: …`) y extranjeros; **DNI/NIE de personas físicas sin enmascarar** (8 % de los menores en una muestra) → seudonimizar en la ingesta (D-007).
  - Nº de ofertas presente solo en parte de los menores (53 % en una muestra).

### F-03 · BDNS

- `https://www.infosubvenciones.es/bdnstrans/api/concesiones/busqueda` responde en JSON sin clave. Campos vistos: `codConcesion`, `fechaConcesion`, `beneficiario` (NIF y nombre en un solo texto, personas físicas ya enmascaradas), `importe`, `instrumento`, `convocatoria`, `nivel1/2/3` (administración y órgano), `urlBR`.
- Pendiente: el filtro correcto para quedarse solo con la Comunidad de Madrid y el volumen 2023–2026.

## Ventana temporal

El MVP se acota a **2023–2026** (ver D-006 en [decisions.md](decisions.md)). Los huecos de cobertura se documentan en la propia plataforma.

## Qué dejamos fuera a propósito

- **Retribuciones individuales de funcionarios.** Solo datos por puesto (RPT) y altos cargos, que ya son públicos por ley. Analizar personas concretas choca con el RGPD y aporta poco.
- **Registro Mercantil (BORME).** Cruzar administradores con cargos públicos sería potente, pero no hay API oficial abierta y limpia. Línea futura.
- **Trazabilidad partida → contrato.** Los datos no la permiten: mostramos ambos niveles por separado y lo decimos explícitamente.

## Problemas de calidad conocidos (a resolver en la normalización)

| Problema | Tratamiento previsto |
| --- | --- |
| NIF mal escritos, nombres con variantes | Normalizar NIF (mayúsculas, sin espacios ni guiones, validar dígito de control); tabla de alias de nombres |
| UTE como entidades separadas | Modelar la UTE y sus empresas miembro |
| Duplicados entre portal regional y PLACSP | Deduplicar por **expediente + órgano** |
| Varias versiones de una licitación en el Atom de PLACSP | Quedarse con la **última versión** |
| Cambios de estructura entre años | Mapeo de columnas por año, documentado |
| Límites de descarga (BDNS, portales que bloquean automatización) | Descargas por meses, caché local, descarga manual si hace falta |

## Reglas para trabajar con datos

1. **Los datos nunca se suben al repositorio** (`data/` está en `.gitignore`). Se regeneran con el pipeline.
2. Cada descarga registra **fuente, URL, fecha y hora** de descarga.
3. Se respetan las condiciones de reutilización: citar fuente y fecha, no alterar el sentido de los datos. Revisar licencias el día 1 (P-03).
4. Cuando se explore o incorpore una fuente, se documenta aquí: campos reales, cobertura, sorpresas. Usa la skill `/nueva-fuente`.

## Pregunta crítica

> Confirmar en el catálogo qué datasets de contratos y presupuesto existen y **si el CSV del Portal de Contratación incluye el número de licitadores**. De eso dependen la mitad de los indicadores. → P-01 y P-02 en [09-preguntas-abiertas.md](09-preguntas-abiertas.md).
