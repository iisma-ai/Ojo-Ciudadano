# 2026-11-23 · Buscadores con autocompletado y más filtros en las señales

- **Autor:** Claude (agente), a petición de la persona que coordina
- **Fase del plan:** 2, un día antes del hito H3. Decisión D-025.

## Qué se hizo

1. **Autocompletado** (`app/buscador.py`, `datos.sugerir_empresas` y `datos.sugerir_organos`): al escribir «am» salen las empresas que empiezan por «am» (AMGEN, AMEBIL, AMPLIFON…), y con tres letras o más también las que lo contienen. Sin texto, las de más contratos. Se aplica a la ficha de empresa, la de organismo, las preguntas guiadas y los filtros de «Contratos a revisar». Las búsquedas por palabra del título (contratos a revisar) y del texto de los convenios siguen siendo de texto libre, porque no buscan nombres.
2. **Contratos atípicos:** orden (más o menos alejado, mayor o menor importe), nivel mínimo de lejanía (99–100 %), variable en la que se aleja, búsqueda por organismo, empresa o título, e interruptor **«Mostrar posibles errores de datos»** apagado por defecto. Con el interruptor apagado la pantalla dice cuántos contratos oculta (44 en la base actual) y cada contrato con valores sin sentido lleva un aviso.
3. **Contratos a revisar:** varias señales a la vez (cualquiera o todas), año, tipo de contrato, orden (puntuación, más señales, importe, recientes), mínimo de señales, cuántos mostrar y organismo o empresa concretos.
4. Tests nuevos con datos sintéticos para los filtros, el orden y las sugerencias.

## Decisiones y desviaciones

- **D-025**: nueva dependencia `streamlit-searchbox` (hay que hacer `uv sync`) y criterio de «posible error de datos».
- El criterio de «posible error» (baja inferior a -100 %, modificaciones de más de cinco veces el importe o importe inferior a 1 euro) solo oculta contratos **en la pantalla**; no cambia el modelo de anomalías (D-021) ni la puntuación.

## Lenguaje (D-002)

Los avisos dicen «posible error al introducir los datos en la fuente» y que no se puede asegurar sin ver el expediente. No se afirma nada sobre el contrato ni sobre quien lo adjudicó.

## Qué falta

1. Pasar los textos nuevos (`textos.AYUDA_POSIBLES_ERRORES`, `aviso_errores_ocultos`) por `revisor-legal`.
2. Probar el autocompletado en móvil y con teclado (D-023, A-10).
3. Si se quiere, mover la búsqueda por palabra del título a sugerencias de organismos.
