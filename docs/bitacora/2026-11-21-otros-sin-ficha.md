# 2026-11-21 · Adjudicatarios con NIF «otro» (D-007, P-07)

- **Autor:** Claude (agente)
- **Fase del plan:** 2. Corrección de RGPD.
- **Rama:** `fix/otros-sin-ficha`

## Qué se hizo
- Revisados los 2.803 adjudicatarios con NIF «otro» (extranjeros o erróneos). La mayoría son empresas extranjeras, pero también hay personas con nombre propio que tenían ficha con su nombre:
  - un empresario individual francés («… EI»);
  - pasaportes;
  - NIE mal escritos.
- `app.datos._sin_personas`: un adjudicatario «otro» solo pasa si su nombre lleva una forma jurídica o un tipo de entidad (`PATRON_EMPRESA`: S.A., S.L., GmbH, LLC, Ltd, AG, B.V., fundación, asociación, universidad…). Se aplica en búsqueda, ficha de empresa, proveedores del órgano y mapa del dinero.
- Resultado en la base del 21-nov: se muestran 1.822 y quedan fuera 981. Algunas empresas extranjeras sin forma jurídica en el nombre también quedan fuera; se prefiere así por privacidad.
- Tests con nombres reales de cada caso. P-07 cerrada en `docs/09`.

## Decisiones tomadas
- Ninguna nueva: es aplicar D-007 («prima la privacidad»).

## Desviaciones del plan
- Ninguna.

## Problemas y hallazgos
- Hay NIF basura como «VERENRESOLUCIONDEADJUDICACIÓN» o «000000000». Sin forma jurídica en el nombre, también quedan fuera.
- Las consultas libres del asistente (cuando llegue D-010) no pasan por este filtro. El validador debería aplicar la misma regla o limitar los nombres a `tipo_persona IN ('juridica', 'ute')`.

## Siguiente paso
- Aplicar la misma regla en el asistente cuando se conecte el modelo.
