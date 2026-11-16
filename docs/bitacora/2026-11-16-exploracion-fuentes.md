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
- No se ha escrito código de ingesta ni esquema. H1 es mañana, 17-nov.

## Problemas y hallazgos
- El portal toma los filtros de la sesión de búsqueda: entrar a la exportación con el filtro pegado en la dirección da «error inesperado». Hay que llegar desde la página de resultados.
- El filtro de fechas exige `dd-mm-aaaa`; con barras devuelve cero resultados o error.
- Marzo de 2023 supera las 50.000 filas (52.371) y se partió en dos quincenas.
- Importes del CSV con IVA; PLACSP sin IVA (P-10).
- Menores sin CPV; DNI/NIE de personas físicas sin enmascarar en el CSV (seudonimizar en la ingesta, D-007).
- Julio–septiembre de 2026 casi vacíos de menores: parece retraso de publicación (P-12).
- Dos cortes de conexión con el navegador durante las descargas; no se perdió ningún fichero.
- Los scripts de exploración se quedaron en una carpeta temporal y no están en el repositorio.

## Siguiente paso
- Módulos de ingesta de PLACSP y del CSV del portal, normalización (NIF, importes, fechas, seudonimización) y DDL en `sql/esquema/` para congelar el esquema (H1).
- Descargar PLACSP 2023–2026 y medir la cobertura frente al portal (P-11).
