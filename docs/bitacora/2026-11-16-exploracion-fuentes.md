# 2026-11-16 · Exploración de fuentes y descarga del portal regional

- **Autor:** Claude (agente), trabajando con El Harrak
- **Fase del plan:** 1 · Datos y alcance

## Qué se hizo
- Recorrido completo del Catálogo de Datos Abiertos (CKAN, 2.276 datasets): no hay contratos a nivel de registro (P-01 resuelta).
- Muestra de PLACSP (plataformas agregadas, octubre de 2026): 3.423 entradas de la Comunidad de Madrid; perfilados los campos clave. Trae nº de ofertas en todos los resultados.
- Portal regional: la exportación a CSV exige captcha y tiene un límite de 50.000 filas. Con el navegador asistido y El Harrak resolviendo cada captcha se exportaron:
  - licitaciones (24.796) y adjudicaciones sin publicidad (11.333), todos los años;
  - contratos menores de 2023-01-01 a 2026-09-30: 42 ficheros, 1.317.983 contratos, sin referencias repetidas.
- Cada fichero de menores se comprobó al llegar (recuento igual al del portal y fechas dentro del periodo) y al final se hizo una comprobación global.
- Prueba de la API de la BDNS: responde sin clave.
- Documentación: detalle por fuente en 02, preguntas P-01/P-02/P-06 y nuevas P-10 a P-12 en 09, notas en 04, tareas y estado en 08.

## Decisiones tomadas
- **D-012 aceptada** por El Harrak: PLACSP principal, portal como complemento manual.
- **D-014 aceptada** (sustituye a la propuesta D-013): R-03 por adjudicatario + órgano + tipo de contrato, con el umbral legal × 1,21 porque los importes van con IVA.
- **D-010 aplazada**: el proveedor de LLM se decide más adelante.

## Desviaciones del plan
- El portal regional deja de ser la fuente principal prevista (D-012, propuesta).
- La parte del portal no es reproducible por código: depende de exportaciones manuales con captcha.
- El esquema es una propuesta: falta que el equipo lo congele (H1, 17-nov).

## Problemas y hallazgos
- El portal toma los filtros de la sesión de búsqueda: entrar a la exportación con el filtro pegado en la dirección da «error inesperado». Hay que llegar desde la página de resultados.
- El filtro de fechas exige `dd-mm-aaaa`; con barras devuelve cero resultados o error.
- Marzo de 2023 supera las 50.000 filas (52.371) y se partió en dos quincenas.
- Importes del CSV con IVA; PLACSP sin IVA (P-10).
- Menores sin CPV; DNI/NIE de personas físicas sin enmascarar en el CSV (seudonimizar en la ingesta, D-007).
- Julio–septiembre de 2026 casi vacíos de menores: parece retraso de publicación (P-12).
- Dos cortes de conexión con el navegador durante las descargas; no se perdió ningún fichero.
- Los scripts de exploración se quedaron en una carpeta temporal y no están en el repositorio; lo útil pasó a los módulos de ingesta.

## Segunda parte de la sesión: código de ingesta, esquema y primera carga
- `src/ojo_ciudadano/normalizacion/`: NIF (prefijos, UTE, clasificación), seudonimización de personas físicas con sal secreta, importes, fechas y tipos de contrato.
- `src/ojo_ciudadano/ingesta/portal_cm.py`: lee los CSV exportados; separa contratos y adjudicaciones (las filas sin cabecera son lotes del contrato anterior). Los contratos sin referencia no se cargan porque no tienen enlace a su ficha.
- `src/ojo_ciudadano/ingesta/placsp.py`: descarga con caché de los zip mensuales y lectura de los Atom; última versión por expediente y órgano; entradas borradas descartadas. Descargados los 47 meses de 2023-01 a 2026-11.
- `sql/esquema/001_tablas.sql` y `src/ojo_ciudadano/modelo/carga.py`: propuesta de esquema (organo, adjudicatario, contrato, adjudicacion y la vista contrato_unico) y carga completa en DuckDB.
- Tests con datos sintéticos: 27, todos en verde; `ruff` limpio. Se añadió en `pyproject.toml` la excepción de longitud de línea para `tests/` (filas CSV y XML sintéticas).
- Primera carga real: 1.371.693 contratos, 1.404.789 adjudicaciones, 28.045 adjudicatarios, 131 órganos. Ningún DNI en claro.
- Cruce entre fuentes medido (P-06 y P-11 resueltas): 98 % de PLACSP tiene pareja en el portal.

### Hallazgos de esta parte
- El percentil 99 del importe de los menores es 18.148,80 € (15.000 € × 1,21): confirma que el CSV va con IVA y el umbral de D-014.
- Hay menores muy por encima del umbral (suscripciones a bases de datos y revistas, hasta 266.000 €): existe una excepción legal para esas suscripciones, a tener en cuenta en R-03 para no señalarlas.
- En PLACSP falta el importe de adjudicación en buena parte de los resultados sin lotes; hay que tomarlo del portal.
- 2.292 adjudicaciones no tienen adjudicatario identificado (desiertos, desistimientos o NIF vacío).
- Los órganos se identifican por nombre normalizado; las consejerías cambian de nombre entre legislaturas y aparecen como órganos distintos.

## Siguiente paso
- Que el equipo revise y congele el esquema (H1) y comparta la sal de seudónimos.
- Incorporar las subvenciones (BDNS) y los datasets del catálogo CKAN.
- Unificar nombres de órganos y consejerías (tabla de alias).
- Empezar los indicadores con `/nuevo-indicador`: R-01, R-03 (D-014) y R-05 ya tienen datos.
