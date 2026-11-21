# 2026-11-21 · NIF «otro» sin forma jurídica: personas físicas desde la normalización

- **Autor:** Claude (agente)
- **Fase del plan:** 2. Ingesta y normalización, RGPD (D-007).
- **Rama:** `fix/otros-en-normalizacion`

## Qué se hizo
- Continuación de `2026-11-21-otros-sin-ficha.md`. El filtro de la interfaz no protegía las consultas libres del asistente, que leen `adjudicatario` directamente.
- `normalizacion.nif.identificar`: un NIF «otro» (extranjero o erróneo) cuyo nombre no lleva forma jurídica pasa a `tipo_persona = 'fisica'`, con seudónimo `PF-…` y sin NIF ni nombre. El patrón (`PATRON_EMPRESA`) se ha movido a `normalizacion/nif.py` y la interfaz lo importa de ahí. El filtro de la interfaz se mantiene para bases antiguas.
- Test con un empresario individual francés y una GmbH.
- Base local regenerada:
  - 945 de los 2.803 «otro» pasan a persona física; quedan 1.858 con nombre.
  - R-03 pasa de 222.122 a 222.116 activados: cambian las identidades de esos adjudicatarios. Los demás indicadores no cambian.
  - Contratos atípicos: 13.498 (antes 13.496).

## Decisiones tomadas
- Ninguna nueva: aplicación de D-007.

## Problemas y hallazgos
- Un mismo NIF extranjero escrito con forma jurídica en una fuente y sin ella en otra recibe dos identidades distintas. Es raro y se prefiere así por privacidad.
- La BDNS ya quitaba el nombre de todo beneficiario que no sea persona jurídica (`ingesta.bdns.minimizar`).

## Siguiente paso
- Ninguno.
