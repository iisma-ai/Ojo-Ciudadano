# 2026-11-21 · Aviso de menores recientes incompletos (P-12)

- **Autor:** Claude (agente)
- **Fase del plan:** 2. Calidad de datos.
- **Rama:** `fix/aviso-menores-recientes`

## Qué se hizo
- Contados los contratos menores por mes en la base del 21-nov (CSV del portal descargados el 16-nov):
  - entre enero de 2025 y junio de 2026 hay entre 18.500 y 36.000 al mes;
  - en julio, agosto y septiembre de 2026 hay 3.565, 2.312 y 3.218.
- Explicación más probable: la LCSP (art. 63.4) solo obliga a publicar los menores **al menos cada trimestre**, así que el tercer trimestre de 2026 aún no estaba completo.
- Añadido el aviso `textos.AVISO_MENORES_RECIENTES` en tres sitios:
  - la evolución anual de la ficha de empresa;
  - la evolución anual de la ficha de órgano;
  - el mapa del dinero, cuando se incluyen menores y el año es 2026 o «Todos».
- Test del texto en `tests/app/test_textos.py`.
- Actualizados P-12 (parcial), la tabla de problemas de calidad de `docs/02` y el estado del plan.

## Decisiones tomadas
- Ninguna.

## Desviaciones del plan
- Ninguna.

## Problemas y hallazgos
- 2026 también baja en el primer semestre: de unos 21.000 al mes frente a unos 30.000 en 2025. Puede ser también retraso, o un cambio real. No se ha podido confirmar sin volver a descargar.
- Los CSV del portal se exportan a mano (D-012), así que la comprobación no se puede automatizar.

## Siguiente paso
- Volver a exportar los menores de julio a noviembre de 2026 antes de la entrega y comparar los recuentos para cerrar P-12.
