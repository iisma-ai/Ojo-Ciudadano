# 2026-11-23 · Nombres de los CPV y entes del sector público (D-033)

**Quién:** El Harrak, con Claude (agente). **Rama:** `feat/cpv-invente`.

## Contexto
Tras el análisis de datos libres que podían aportar algo al proyecto, se eligieron los dos más baratos y útiles para la demo: los nombres de los CPV y el inventario INVENTE.

## Qué se hizo
- **CPV:**
  - `ingesta/cpv.py` baja y lee la lista CODICE `CPV2008-2.04.gc` de la Plataforma de Contratación: 9.454 códigos, en la tabla `cpv` (`008_cpv.sql`).
  - Casan los 1.963 códigos distintos de nuestras licitaciones.
  - **Ficha de contrato:** «Objeto (CPV …): nombre · sector: …».
  - **Asistente:** la tabla, en la lista permitida, y la regla de dar el nombre junto al código.
  - La lista de TED devuelve una comprobación de robots: no se forzó.
- **INVENTE:**
  - La aplicación no ofrece ficheros; su API sí. El inventario completo se baja con una sola petición sin filtros, porque el parámetro `ambito` lo bloquea la política de seguridad del portal.
  - `ingesta/invente.py` carga 4.602 entes con NIF en `entidad_sector_publico` (`009_sector_publico.sql`). La administración de la que depende cada ente sale de su código de origen («12000…», Comunidad de Madrid).
  - **Ficha de empresa:** aviso de ente del sector público con su fuente y fecha, o una nota si el nombre no cuadra.
  - **Asistente:** la tabla y su regla.
- **Cruce:** 261 adjudicatarios son entes públicos, con unos 121 M€ con IVA. En 26 el nombre no se parece. En unos casos son siglas, como ASERPINTO o CEDEX; en otros, errores de NIF de la fuente, como PIXELWARE o AUDALIA AUDITORES. Esto confirma el problema de NIF ajenos que ya había visto el estudio de DIR3.

## Comprobaciones
- **Tests:** 351, todos bien (343 al empezar).
- `ruff` sin avisos.
- Los ayudantes de datos, probados con la base real: Complutense, Canal de Isabel II y PIXELWARE.

## Siguiente paso
- Decidir en equipo si los entes públicos dejan de contar en R-04 y en la puntuación de empresa, porque es un cambio de metodología.
- Al fusionar `feat/mapa-vistazo`, renumerar su decisión a D-034.
- En cada instalación: `ingesta.cpv` e `ingesta.invente`.
