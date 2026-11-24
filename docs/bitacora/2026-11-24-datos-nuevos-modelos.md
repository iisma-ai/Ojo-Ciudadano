# 2026-11-24 · CPV y entes públicos en R-04, la puntuación y los atípicos (D-036)

**Quién:** El Harrak, con Claude (agente). **Rama:** `feat/datos-nuevos-modelos`, que sale de `feat/cpv-invente`.

## Contexto
Los nombres de los CPV e INVENTE (D-035) solo eran contexto en la web y el asistente. El Harrak pidió tres cosas:
1. preguntas de CPV e INVENTE en la batería;
2. que los entes públicos no cuenten en R-04 ni en la puntuación de empresa;
3. el CPV en los grupos de pares de los atípicos;

y llevar a los indicadores y a las anomalías todo lo que tuviera sentido.

## Qué se hizo
- **Fusión de `main` en `feat/cpv-invente`:** la decisión de CPV e INVENTE pasa de D-033 a D-035, porque D-033 y D-034 ya eran del mapa de un vistazo y de la estética.
- **R-04:**
  - en PLACSP, el mercado se divide por división CPV;
  - los entes públicos cuentan en el mercado, pero no activan la señal;
  - la ficha E-04 dibuja el mismo mercado y nombra la división.
- **Qué cuenta como ente público:** NIF en INVENTE y nombre compatible.
  - Lo guarda la tabla derivada `adjudicatario_ente_publico`, con 235 adjudicatarios.
  - Primero se probó solo con el NIF. Así, una empresa con un NIF mal puesto en la fuente, como PIXELWARE, perdía sus señales. Se corrigió antes de subir.
- **Puntuación de empresa:** los entes públicos conservan ficha y contratos, pero con la puntuación vacía y la marca `sector_publico`.
- **Atípicos:**
  - grupos de pares por división CPV en las licitaciones de PLACSP;
  - las divisiones pequeñas van a «otras divisiones CPV», y un tipo no se divide si el resto es pequeño o si no hay ninguna división grande;
  - grupo nuevo de entes públicos en la validación.
- **Asistente:**
  - B-35 a B-37 en la batería;
  - reglas del CPV y de los entes públicos;
  - la referencia de B-35 usa ahora la misma definición de año que B-06.
- `indicadores.ejecutor` crea vacías las tablas de contexto si faltan.

## Resultados (base del 16-nov, recalculada)
- **R-04:**
  - en PLACSP, de 29 a 92 activados, con 22 en común, y de 14.537 a 11.686 aplicables;
  - en el portal regional, los mismos 54.
- **Puntuación de órgano:** cambia en 83 de 131 órganos, 0,10 como mucho.
- **Puntuación de empresa:** 209 entes públicos se quedan sin puntuación. Antes, algunos estaban en lo alto, como la FNMT y Renfe Viajeros, con 0,42.
- **Atípicos:**
  - 48 grupos;
  - en PLACSP, de 151 a 165, con 97 en común;
  - recursos estimados: siguen con 0 atípicos de 55;
  - entes públicos: 5 de 3.961.
- **Batería:** las tres preguntas, bien con terra (0,028 USD).

## Comprobaciones
- **Tests:** 366, todos bien (353 al empezar).
- `ruff` sin avisos.
- Indicadores y atípicos recalculados en la base local. Para hacerlo hubo que parar la web, que después se volvió a arrancar.

## Siguiente paso
- **Equipo:** conocer D-036 antes de fusionarla, porque cambia las cifras de R-04, de los atípicos y de la puntuación el día de la demo.
- **Orden de fusión:** primero `feat/cpv-invente` y luego esta rama.
- **En cada instalación:** `ingesta.cpv` e `ingesta.invente`, después `indicadores.ejecutor` y por último `anomalias.deteccion`.
