# 04 · Metodología de indicadores de riesgo

**Calculamos señales de riesgo, no pruebas de corrupción.** Seguimos la [guía de red flags de la Open Contracting Partnership](https://open-contracting.org/redflags), que recoge 73 indicadores de la literatura y de implementaciones reales, y elegimos los que nuestros datos permiten calcular.

## Indicadores seleccionados

| ID | Indicador | Definición operativa | Por qué es una señal | Datos necesarios | Prioridad |
| --- | --- | --- | --- | --- | --- |
| R-01 | Licitador único | Procedimiento abierto o restringido con una sola oferta | Indicador básico del índice de riesgo de corrupción de [Fazekas y Kocsis (2020)](https://doi.org/10.1017/S0007123417000461); indica competencia nula | Nº de ofertas, procedimiento | Alta |
| R-02 | Procedimiento sin publicidad | Peso de negociados sin publicidad y emergencias en el gasto de cada órgano | Evita la concurrencia abierta | Tipo de procedimiento, importe | Alta |
| R-03 | Posible fraccionamiento | Varios contratos menores al mismo NIF, mismo CPV y órgano en 12 meses cuya suma supera el umbral legal (**15.000 €** servicios y suministros, **40.000 €** obras) | Dividir un contrato evita la licitación | Menores con NIF, CPV, fecha, importe | Alta |
| R-04 | Concentración de proveedor | Cuota de una empresa en el gasto de un órgano o CPV; índice HHI por mercado | Dependencia o captura de un mercado | Adjudicaciones por NIF | Alta |
| R-05 | Sobrecoste por modificaciones | (Importe final − adjudicado) / adjudicado, sumando modificaciones y prórrogas | Ganar barato y recuperar después | Importes de modificaciones y prórrogas | Media |
| R-06 | Baja anormal o nula | Diferencia entre presupuesto base y adjudicación cercana a cero, o extrema | Sin baja sugiere poca competencia; baja extrema, riesgo de ejecución | Presupuesto base, importe adjudicado | Media |
| R-07 | Plazo de presentación corto | Días entre anuncio y fin de plazo frente a la mediana del tipo de contrato | Reduce el número de licitadores posibles | Fechas de anuncio y cierre | Baja |
| R-08 | Opacidad documental | Contratos sin acta, sin informe de adjudicación o con documentos clave ausentes | Mide directamente la falta de transparencia | Inventario de documentos adjuntos | Baja |

> R-01 depende de que tengamos el número de ofertas (P-02). Si el CSV regional no lo trae: tomarlo de PLACSP; si no, extraerlo con IA de las actas en una muestra; si no, priorizar los indicadores que no lo necesitan.

## Cómo se combinan

1. **Comparación entre pares.** Cada indicador se calcula por contrato y se compara con contratos del **mismo tipo y CPV**, no con el total, para no castigar mercados pequeños por naturaleza.
2. **Puntuación por contrato** = proporción de indicadores *aplicables* que se activan, de 0 a 1. Un indicador no aplicable (faltan datos o no tiene sentido para ese procedimiento) no cuenta ni a favor ni en contra.
3. **Por órgano y por empresa**: media ponderada por importe y tendencia anual.
4. **Explicabilidad**: toda alerta muestra qué indicador la disparó, con qué valor y el enlace al expediente.
5. **Puntuación gradual, no binaria.** Se excluyen causas legales de exclusividad (exclusividad técnica, emergencias justificadas) para reducir falsos positivos.

## Validación (si hay tiempo)

Comprobar con casos ya fiscalizados por la Cámara de Cuentas o recogidos en prensa: deberían puntuar más alto que la media.

## Reglas de implementación

- Cada indicador es una **consulta SQL versionada** en el repositorio (D-004), transparente y reproducible por el jurado.
- Cada indicador tiene: ID (`R-xx`), definición en este documento, fichero SQL, test con datos sintéticos y nota de limitaciones.
- Cambiar una definición o un umbral = **registrar decisión** en [decisions.md](decisions.md) y actualizar este documento.
- Usa la skill `/nuevo-indicador`.

## Estado de implementación

| ID | Estado | Fichero | Notas |
| --- | --- | --- | --- |
| R-01 | Pendiente | — | Depende de P-02 |
| R-02 | Pendiente | — | |
| R-03 | Pendiente | — | |
| R-04 | Pendiente | — | |
| R-05 | Pendiente | — | |
| R-06 | Pendiente | — | |
| R-07 | Pendiente | — | Recortable |
| R-08 | Pendiente | — | Recortable |
