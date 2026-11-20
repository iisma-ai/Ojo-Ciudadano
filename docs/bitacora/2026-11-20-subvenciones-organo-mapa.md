# 2026-11-20 · Subvenciones en la ficha de órgano y en el mapa del dinero

- **Autor:** Claude (agente), a petición de Ignacio
- **Fase del plan:** 2 · Construcción en paralelo (interfaz)

## Qué se hizo
- Rama `feat/subvenciones-organo-mapa` desde `origin/main`, después de integrar la BDNS (PR #3).
- `app/datos.py`:
  - `hay_subvenciones`;
  - `subvenciones_organo`, `convocatorias_organo` y `beneficiarios_organo`;
  - `flujos_subvenciones` y `concesiones_flujo`;
  - `fecha_subvenciones`.
  Solo tienen nombre los beneficiarios `juridica`/`ute` con NIF verificable. El resto forma el grupo «Personas físicas y otros beneficiarios (agregados)» (D-007).
- **Ficha de órgano:** sección «Subvenciones concedidas» con el total, el agregado de personas, las convocatorias y las entidades con más importe, la fuente con su fecha y los enlaces a cada convocatoria.
- **Mapa del dinero:** la BDNS es una tercera fuente. Los filtros de tipo de contrato y de menores se desactivan con esa fuente. El detalle lista las convocatorias. Con contratos, ahora también se muestra la fecha de descarga.
- Revisión con `revisor-legal`, aplicada:
  - fuente y fecha en el mapa;
  - aviso de que un flujo grande no es una señal de riesgo;
  - las filas sin enlace no se muestran como enlace;
  - el mismo texto del agregado en las dos pantallas;
  - en el flujo agregado, las convocatorias con menos de 5 concesiones se suman en «Otras convocatorias», para que una convocatoria con una o dos personas no permita identificarlas.
- 140 tests y `ruff` en verde. Las pantallas probadas con la base real: el mapa de la BDNS responde en 0,4 s.

## Decisiones tomadas
- Ninguna.

## Desviaciones del plan
- Ninguna.

## Problemas y hallazgos
- Los mayores flujos de subvenciones son becas y ayudas a personas físicas (Educación, 299 M€; Familia, 280 M€, agregados). Entre las entidades destacan los programas que se gestionan enteros a través de una entidad (Consejo de Colegios de Abogados, 199 M€, asistencia jurídica gratuita), y el texto lo explica.

## Siguiente paso
- Integrar en `main`.
- Pendientes del equipo: D-010 (LLM), D-021 (responsable de anomalías) y P-03 (aviso legal de la BDNS).
