# 2026-11-21 · UTE con personas físicas (D-007)

- **Autor:** Claude (agente), a petición de Ismael
- **Fase del plan:** 2. Corrección de RGPD.
- **Rama:** `fix/ute-personas-fisicas`

## Qué se hizo
- La revisión legal de los contratos atípicos avisó de que una UTE con un autónomo como miembro podía mostrar su nombre. Se ha comprobado en la base: de 59 UTE, 2 están formadas solo por personas físicas, con nombres propios en el de la UTE.
- `normalizacion.nif.identificar`: una UTE con algún miembro persona física se guarda con `tipo_persona = 'fisica'` y sin nombre. Su id sigue siendo `UTE:` con los miembros seudonimizados.
- Para bases cargadas antes de la corrección:
  - `app.datos._sin_personas` deja fuera cualquier `adjudicatario_id` que contenga `PF-`;
  - el asistente (`sql_seguro._ocultar_seudonimos`) oculta también los `UTE:PF-…`.
- Tests: normalización, ficha y búsqueda de empresa con una base antigua, y ocultación en el asistente.
- Base local regenerada (carga, indicadores y anomalías).

## Decisiones tomadas
- Ninguna nueva: es aplicar D-007.

## Desviaciones del plan
- Ninguna.

## Problemas y hallazgos
- Una UTE mixta (empresa más autónomo) también queda agregada, aunque tenga empresas. Se pierde algo de detalle, pero es lo prudente.

## Siguiente paso
- Ninguno.
