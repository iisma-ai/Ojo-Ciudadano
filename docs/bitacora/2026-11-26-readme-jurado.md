# 2026-11-26 · README para el jurado según los criterios de DataMad

**Quién:** Ignacio, con Claude (agente). **Rama:** `docs/readme-jurado`.

## Qué se ha hecho

- README reescrito para que el jurado lo lea en 5 minutos (D-067): «En 30 segundos», «Probarla en 2 minutos», una tabla de criterios con enlaces y las secciones de datos abiertos de la Comunidad (con los 32 conjuntos del catálogo y del Portal de Transparencia, más el Portal de Contratación y el Tribunal), qué tiene de nuevo, señales con «de cada 100», impacto con casos de uso, viabilidad y mantenimiento, reproducibilidad, presentación y equipo.
- Corregido el enlace del Portal de la Contratación Pública: antes apuntaba a una descarga de nota de prensa y ahora apunta a `contratos-publicos.comunidad.madrid/contratos`.
- `.github/workflows/tests.yml`: tests y ruff en GitHub en cada push, con su insignia en el README.
- Borrado `docs/LO-PRIMERO.md` y su sección de `CLAUDE.md`. Los enlaces que quedaban en el plan y las decisiones ahora apuntan a `12-datos-cm.md`. El estado de `docs/README.md` está al día de la entrega.

## Cifras usadas (base local del 24-nov, tabla `indicador_resultado`)

| Señal | Aplicables | Activados | De cada 100 |
| --- | --- | --- | --- |
| R-01 | 20.763 | 8.178 | 39 |
| R-02 | 36.361 | 11.260 | 31 |
| R-03 | 1.332.957 | 228.122 | 17 |
| R-04 | 1.357.866 | 146 | < 1 |
| R-05 | 31.406 | 573 | 2 |
| R-06 | 11.941 | 2.230 | 19 |

Contratos: 1.387.606 en `contrato`, de 131 organismos. Hay 496 tests en verde.

## Siguiente paso

- Comprobar que la insignia de GitHub Actions sale en verde después del merge.
- Completar los nombres y apellidos del equipo en el README si se quiere.

## Equipo: dos personas

Ignacio ha confirmado que el equipo son dos personas, Ismael El Harrak El Harraq e Ignacio Vallejo Garach. Donde ponía «4 personas» ahora pone 2, con los nombres completos: README, `LICENSE`, `CLAUDE.md`, `01-vision.md`, `07-riesgos.md`, `decisions.md` (contextos de D-001, D-008, D-009, D-011, la congelación del esquema y D-066) y `08-plan.md`. En el plan, la tabla de responsables numera ahora «líneas» de trabajo y no «personas». Las bitácoras antiguas no se tocan porque son historia. Cuando hablan de «la persona 4», se refieren al número de línea del plan.

## README más breve (rama `docs/readme-breve`, pendiente de que Ignacio diga cuándo se integra)

A petición de Ignacio:
- Arriba, «Abrir la página web aquí» en grande y, debajo, el enlace.
- Fuera la nota de DataMad y los apartados «En 30 segundos» (queda solo su primer párrafo como introducción), «Probarla en 2 minutos», «Cómo responde a cada criterio», «Indicadores de riesgo, no acusaciones» y «Para quién».
- Resumidos en un párrafo los apartados de calidad, privacidad y reutilización de los datos, «Qué tiene de nuevo» y «Viabilidad».
- Como desaparece el apartado de indicadores, la aclaración «son indicadores de riesgo, no acusaciones» pasa a «Qué tiene de nuevo» (regla 4 de `CLAUDE.md`).
- Segunda ronda: en «Qué hace» se quita la pantalla Inicio, cada pantalla queda en una frase y «Asistente» pasa a llamarse «Asistente de IA». La sección de datos abiertos presenta la tabla con «Las fuentes utilizadas han sido las siguientes». «Qué tiene de nuevo» lleva «(innovación)» en el título. El impacto social habla de la desconfianza que genera no saber a dónde va el dinero.
