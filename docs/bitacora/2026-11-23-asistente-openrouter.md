# 2026-11-23 · Asistente conectado a OpenRouter y elección de modelo

- **Autor:** Claude (agente), a petición de El Harrak
- **Fase del plan:** 2. Cierra el entregable de la persona 4: el asistente responde preguntas libres.

## Qué se hizo
- **Base local regenerada.** Era del 19-nov y le faltaban la BDNS y las anomalías. Se descargó la BDNS y se ejecutaron la carga, los indicadores y las anomalías. Cifras sin cambios: R-05 con 573 contratos y unos 13.500 atípicos.
- **`asistente/openrouter.py`:**
  - clave desde el entorno o desde `.env`, sin imprimirla nunca;
  - comprobación de la clave y del saldo;
  - adaptador con la forma de `agente.Modelo`, con modelo de respaldo, caché y acumulación del coste.
- **`asistente/comparar_modelos.py`:** compara modelos con la batería, con topes de gasto, y guarda las respuestas en `data/evaluaciones/`.
- **Agente:**
  - `modelo_configurado()` usa OpenRouter si hay clave;
  - una reescritura cuando el filtro de lenguaje retendría la respuesta;
  - se admiten sin consulta las cifras que están en las instrucciones;
  - instrucciones nuevas: no escribir los términos de la tabla de lenguaje ni negados, mínimo de 100 contratos en los rankings por puntuación y años de 2023 a 2026.
- **Evaluador de la batería:**
  - vale cualquiera de las consultas del modelo;
  - se toleran filas de más y rankings más cortos;
  - el código de la fuente equivale a su nombre, y el año como texto equivale al año como número;
  - no falla con columnas de tipo lista.
- **Pantalla del asistente:** aviso, sin traza técnica, si el proveedor falla.
- Tests: de 238 a 249, todos pasan; ruff limpio.

## Decisiones tomadas
- **D-010 aceptada** para el proveedor y los modelos: OpenRouter, `openai/gpt-6.1-terra` de principal y `anthropic/claude-haiku-5.5` de respaldo. La tabla de resultados está en `docs/decisions.md`.

## Desviaciones del plan
- Ninguna en alcance.
- Se propone **no hacer el RAG documental** (recorte 2 del plan). Falta que el equipo lo confirme.

## Problemas y hallazgos
- **El evaluador penalizaba respuestas correctas.** Solo miraba la última consulta, exigía el mismo número de filas y comparaba los valores con su tipo exacto. Con la primera versión, terra sacaba 6/16; revisado a mano, tenía bien los datos de las 16.
- **El filtro de lenguaje retenía negaciones largas.** Ejemplos: «No puedo decir si una empresa es corrupta» o «favorece a quien más contrata». No se ha relajado, porque lo validó `revisor-legal`. Se resuelve con instrucciones y una reescritura.
- **Años raros en `puntuacion_contrato.anio`:**
  - 3.966 contratos son anteriores a 2023;
  - algunos tienen años imposibles (1, 3, 23, 206), que serán fechas mal escritas en origen;
  - 19.174 no tienen año.
  - Conviene revisarlo en la normalización.
- **B-15 (concentración) es ambigua:** cada modelo ordena de una forma (por número de contratos o por cuota) y las tres formas son razonables.
- **Gasto:** 0,47 USD en total en tres rondas y la comprobación final. Saldo de la cuenta: unos 0,93 USD.

## Siguiente paso
- **Integrar en `main`.** Las ramas `feat/datos-cm-abiertos` (D-024, D-025) y `fix/relleno-y-referencia-r01` (D-026) también tocan `agente.py` y `sql_seguro.py`. Quien fusione después debe resolver los conflictos conservando las dos partes.
- **Reiniciar la web** para que cargue el modelo.
- **Ensayar la demo** con las 4 preguntas.
- Confirmar el recorte 2 (RAG). P-09 y A-11 siguen pendientes.
