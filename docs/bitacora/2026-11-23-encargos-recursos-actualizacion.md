# 2026-11-23 · Encargos a medios propios, recursos del TACPCM y actualización de datos

- **Autor:** Claude (agente), a petición de una persona del equipo, que pidió obtener los datos más relevantes con la mejor calidad y avisar al terminar
- **Fase del plan:** 2, un día antes del H3
- **Rama:** `fix/relleno-y-referencia-r01` (PR #7). Sigue a [`2026-11-23-relleno-fondos-ue-r01.md`](2026-11-23-relleno-fondos-ue-r01.md)

## Qué se hizo

1. **Encargos a medios propios (D-028).** Tipo de publicación del portal que nunca se había exportado. Exportado a mano (captcha) con el navegador integrado: `data/raw/encargos/encargos_todo_2026-11-23.csv`, 2.405 encargos. El CSV no trae fechas; el año de publicación sale de la referencia `C<número>`, cuyos tramos reproducen exactamente el buscador (236, 226, 260 y 222 de 2023 a 2026). Tabla aditiva `encargo` (`005`), fuera de `contrato` y de los indicadores. Resultado: **944 encargos de 2023–2026, 369,6 M€ con IVA**; Tragsa 245,3 M€, Tragsatec 80,7 M€; el órgano que más encarga es la Agencia de Seguridad y Emergencias Madrid 112 (185,9 M€).
2. **Recursos especiales del TACPCM (D-029).** `ingesta/tacp.py` recorre el buscador del Tribunal por procedencia × resultado × acto recurrido (377 páginas, una petición cada vez, unos 50 minutos). Tabla aditiva `recurso_especial` (`006`), sin el resumen (nombra a empresas y puede nombrar a personas). 1.097 resoluciones de 1.109: la paginación del buscador repite o salta filas cuando hay fechas empatadas. Siete resoluciones con dos actos o dos resultados quedan en una fila con las etiquetas unidas.
   - Enlace con contratos: **solo 6**. Los resúmenes casi nunca citan el expediente y el listado no da el órgano. Se descartaron como candidatos los números con forma de ley («9/2017»), que daban falsos positivos.
   - Como contexto agregado sí sirve: el Tribunal estimó total o parcialmente el 30 % de los recursos contra pliegos, el 25 % contra adjudicaciones y el 18 % contra exclusiones.
3. **Actualización de datos ya incorporados:** zip de noviembre de PLACSP (de 6,5 a 10 MB) y octubre–noviembre de la BDNS (octubre de 47.220 a 68.965 concesiones; noviembre de 4.870 a 6.068). Los ficheros anteriores están en `data/raw/respaldo_2026-11-23/`.
4. **Contexto de la Comunidad (D-024):** descargado y cargado; coincide con la referencia del equipo. Confirmación 1 de 2 en `LO-PRIMERO.md` (PR #8). No se abrió la pantalla «Presupuesto y contexto» a mano.
5. Integrado `origin/main` (D-024 a D-026 de la otra línea). D-026 estaba usada: las decisiones de esta rama quedan como **D-027, D-028 y D-029**.

## Resultados de la regeneración final (9 min 30 s)

| Tabla | Filas |
| --- | --- |
| `contrato` | 1.387.606 |
| `adjudicacion` | 1.420.860 |
| `adjudicatario` | 504.846 |
| `concesion` | 872.821 |
| `contrato_financiacion` | 14.858 (966 con fondos de la UE) |
| `encargo` | 945 (944 encargos) |
| `recurso_especial` | 1.097 (6 con contrato) |

Indicadores: R-01 8.178 de 20.763 (39,4 %), R-02 11.260 de 36.361, R-03 228.122 de 1.332.957, R-04 85, R-05 573, R-06 2.230 de 11.941. Anomalías: 13.659 atípicos de 1.365.430.

## Decisiones y desviaciones

- **D-028** (encargos) y **D-029** (recursos del TACPCM), ambas aditivas y fuera de la puntuación. Amplían D-001 con datos de la propia Comunidad.
- Ninguna dependencia nueva.

## Comprobaciones

- `uv run pytest`: 267 tests en verde. `ruff check` y `ruff format`: limpios.

## Qué falta

1. **Interfaz:** mostrar encargos (ficha de órgano y de empresa, mapa del dinero), recursos (ficha de contrato) y fondos europeos. Lo coordina quien lleva la interfaz; esta rama no toca pantallas.
2. **Cada máquina debe regenerar la base.** Los CSV de menores de jul–sep y de encargos no se bajan por código (captcha): hay que repetir la exportación o pasarse los ficheros por un canal privado. El listado del TACPCM sí se baja con `uv run python -m ojo_ciudadano.ingesta.tacp`.
3. Revisión legal de las descripciones nuevas del asistente (`encargo`, `recurso_especial`) con `revisor-legal`.
4. Línea futura: leer los PDF del TACPCM para enlazar más recursos con su contrato; DIR3 desde las fichas del portal.

## Siguiente paso

Fusionar el PR #7 y avisar al equipo de que hay que regenerar la base.
