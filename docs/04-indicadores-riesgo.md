# 04 · Metodología de indicadores de riesgo

**Calculamos señales de riesgo, no pruebas de corrupción.** Seguimos la [guía de red flags de la Open Contracting Partnership](https://open-contracting.org/redflags), que recoge 73 indicadores de la literatura y de implementaciones reales, y elegimos los que nuestros datos permiten calcular.

## Indicadores seleccionados

| ID | Indicador | Definición operativa | Por qué es una señal | Datos necesarios | Prioridad |
| --- | --- | --- | --- | --- | --- |
| R-01 | Licitador único | Procedimiento abierto o restringido con una sola oferta | Indicador básico del índice de riesgo de corrupción de [Fazekas y Kocsis (2020)](https://doi.org/10.1017/S0007123417000461); indica competencia nula | Nº de ofertas, procedimiento | Alta |
| R-02 | Procedimiento sin publicidad | Peso de negociados sin publicidad y emergencias en el gasto de cada órgano | Evita la concurrencia abierta | Tipo de procedimiento, importe | Alta |
| R-03 | Posible fraccionamiento | Dos o más contratos menores al mismo adjudicatario, mismo órgano y mismo tipo de contrato en una ventana móvil de 12 meses cuya suma **con IVA** supera **18.150 €** (servicios y suministros) o **48.400 €** (obras), es decir, el umbral legal de 15.000 € / 40.000 € × 1,21 (D-014). Solo suman los menores de al menos un tercio del umbral: 6.050 € / 16.133,33 € con IVA (D-015). Se excluyen las suscripciones a publicaciones y bases de datos (LCSP, disposición adicional novena) | Dividir un contrato evita la licitación | Menores con NIF, órgano, tipo, fecha e importe con IVA | Alta |
| R-04 | Concentración de proveedor | Una empresa con más del **50 %** del importe adjudicado por un órgano en un mismo tipo de contrato (mercado de al menos 10 contratos y 3 empresas); se muestra también el índice HHI (D-018) | Dependencia o captura de un mercado | Adjudicaciones por NIF | Alta |
| R-05 | Sobrecoste por modificaciones | Modificaciones / importe adjudicado > **20 %**, el límite de las modificaciones previstas (art. 204 LCSP). Las prórrogas no cuentan: suelen ser anualidades previstas en el pliego (D-016) | Ganar barato y recuperar después | Importes adjudicado y de modificaciones | Media |
| R-06 | Baja anormal o nula | Baja = 1 − adjudicado / presupuesto base. Se activa con baja **≤ 0,5 %** (sin baja o por encima del presupuesto) o **≥ 50 %**, en abierto, abierto simplificado y restringido con al menos dos ofertas (D-019) | Sin baja sugiere poca competencia; baja extrema, riesgo de ejecución | Presupuesto base, importe adjudicado | Media |
| R-07 | Plazo de presentación corto | Días entre anuncio y fin de plazo frente a la mediana del tipo de contrato | Reduce el número de licitadores posibles | Fechas de anuncio y cierre | Baja |
| R-08 | Opacidad documental | Contratos sin acta, sin informe de adjudicación o con documentos clave ausentes | Mide directamente la falta de transparencia | Inventario de documentos adjuntos | Baja |

> R-01 depende de que tengamos el número de ofertas (P-02). Si el CSV regional no lo trae: tomarlo de PLACSP; si no, extraerlo con IA de las actas en una muestra; si no, priorizar los indicadores que no lo necesitan.

## Cómo se combinan

1. **Comparación entre pares.** Cada indicador se calcula por contrato y se compara con contratos del **mismo tipo y CPV**, no con el total, para no castigar mercados pequeños por naturaleza.
2. **Puntuación por contrato** = proporción de indicadores *aplicables* que se activan, de 0 a 1. Un indicador no aplicable (faltan datos o no tiene sentido para ese procedimiento) no cuenta ni a favor ni en contra.
3. **Por órgano y por empresa**: media ponderada por importe y tendencia anual.
4. **Explicabilidad**: toda alerta muestra qué indicador la disparó, con qué valor y el enlace al expediente.
5. **Puntuación gradual, no binaria.** Se excluyen causas legales de exclusividad (exclusividad técnica, emergencias justificadas) para reducir falsos positivos.

## Implementación de la puntuación

`sql/indicadores/900_puntuacion.sql` (D-020) crea `puntuacion_contrato`, `puntuacion_organo[_anio]` y `puntuacion_empresa[_anio]`. Con los datos del 16-nov: la mayoría de contratos (1,3 M menores) tiene solo 2 indicadores aplicables (R-03, R-04); las licitaciones tienen 3–5. Hay que mostrar siempre `n_aplicables` y comparar entre pares.

## Detección de anomalías (complementaria, D-021)

Además de los indicadores con reglas, un modelo de aprendizaje automático marca los contratos **atípicos respecto a contratos similares**. Por defecto se usa un método no supervisado: clustering por tipo de contrato y distancia a su grupo, o Isolation Forest. Solo se usaría uno supervisado si hubiera etiquetas legítimas (p. ej. casos de la Cámara de Cuentas), nunca etiquetas de «corrupción» (D-002). Cada contrato atípico se muestra con las variables que más lo alejan de sus pares y el enlace al expediente. **No entra en la puntuación** hasta validarlo. Es el primer recorte si vamos tarde.

**Implementación (21-nov, `src/ojo_ciudadano/anomalias/deteccion.py`):**
- **Grupo de pares:** fuente + licitación o menor + tipo de contrato (14 grupos con 50 contratos o más; los más pequeños no se analizan). Se separa por fuente porque los importes de PLACSP van sin IVA y los del portal con IVA.
- **Variables** (las que tienen datos y variación en cada grupo):
  - importe adjudicado, en logaritmo;
  - número de ofertas;
  - baja sobre el presupuesto (misma base de IVA);
  - modificaciones sobre el importe (solo portal);
  - cuota del adjudicatario en lo que adjudica el órgano en ese tipo de contrato;
  - nº de menores con el mismo adjudicatario y órgano en los 12 meses anteriores (solo menores).
  Los huecos se rellenan con la mediana del grupo, así que no alejan a nadie.
- **Modelo:** Isolation Forest por grupo (200 árboles, semilla 42). Se marca como atípico el 1 % más alejado de cada grupo. `puntuacion` es el percentil de rareza dentro del grupo, una posición relativa y no una probabilidad.
- **Explicación:**
  - Se citan las dos variables con mayor desviación robusta ((x − mediana) / (1,4826 · MAD)) de al menos 2, con su valor y la mediana del grupo (importes «sin IVA» o «con IVA» según la fuente).
  - Si ninguna llega a 2, se citan igualmente las dos que más se alejan, como combinación poco habitual.
- **Resultado con los datos del 21-nov:** 1.349.510 contratos puntuados, **13.496 atípicos (1,0 %)**.
  - 3.262 de los atípicos (24 %) tienen además algún indicador de riesgo activado, así que la señal aporta sobre todo contratos que las reglas no ven.
  - 27 son de personas físicas: solo se cuentan, no se listan (D-007).
  - Solo 4 motivos son de «combinación».
- **Hallazgos y limitaciones:**
  - En los menores (1,3 M), lo que más separa es el número de menores del mismo adjudicatario y órgano: proveedores recurrentes de hospitales con miles de pedidos al año. Es el mismo patrón que obligó a ajustar R-03 (D-015) y suele tener explicación legítima (suministro continuo sin acuerdo marco).
  - En las licitaciones aparecen acuerdos marco muy grandes y obras con una cuota del 100 % o modificaciones del 100 % del importe. Estas últimas pueden ser errores de la fuente; hay que revisarlas en el expediente.
  - Sin CPV, los grupos mezclan objetos distintos dentro de un mismo tipo de contrato.
  - No está validado con casos reales: por eso no entra en la puntuación.

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
| R-01 | Implementado | [`r01_licitador_unico.sql`](../sql/indicadores/r01_licitador_unico.sql) | Abierto, abierto simplificado y restringido; por contrato, activado si algún lote resuelto tuvo una sola oferta. Datos del 16-nov: 20.693 aplicables, **8.144 activados (39,4 %)**. Hallazgo: tasa alta; revisarla por procedimiento, tipo y CPV al construir la puntuación |
| R-02 | Implementado | [`r02_sin_publicidad.sql`](../sql/indicadores/r02_sin_publicidad.sql) | Señal por contrato; el peso en el gasto de cada órgano se calcula al agregar. Activado si es negociado sin publicidad (PLACSP o portal) o si el portal lo publica como «otro procedimiento» en su lista de adjudicados sin publicidad, donde están las emergencias. No aplica a contratos derivados de acuerdo marco o sistema dinámico. 36.297 aplicables, **11.250 activados (31,0 %)**: 6.937 negociados y 4.313 «otro procedimiento» |
| R-03 | Implementado | [`r03_posible_fraccionamiento.sql`](../sql/indicadores/r03_posible_fraccionamiento.sql) | D-014 + D-015. Con D-014 sola se activaba el 84,8 % (pedidos recurrentes de los hospitales); con D-015: 1.317.145 aplicables, **222.122 activados (16,9 %)**. Limitaciones: agrupa por tipo de contrato (sin CPV), umbral con IVA conservador, no ve la división en muchos trozos pequeños. 1.661 alertas son de personas físicas seudonimizadas: solo agregadas (D-007) |
| R-04 | Implementado | [`r04_concentracion_proveedor.sql`](../sql/indicadores/r04_concentracion_proveedor.sql) | D-018. Mercado = fuente + órgano + tipo de contrato (sin CPV, sin mezclar importes con y sin IVA). 1.348.715 aplicables, **84 activados (0,006 %)**. Muy selectivo: su valor está en la cuota y el HHI de las fichas de órgano y empresa. No distingue exclusividades legítimas |
| R-05 | Implementado | [`r05_sobrecoste_modificaciones.sql`](../sql/indicadores/r05_sobrecoste_modificaciones.sql) | D-016. Solo portal regional (con IVA). 31.406 aplicables, **573 activados (1,8 %)**, superando el 20 % en más de 1 € para que no decida el redondeo. Hallazgo: 362 contratos tienen las modificaciones justo en el 20 %, el máximo legal. Las prórrogas se muestran en el motivo |
| R-06 | Implementado | [`r06_baja_anormal_o_nula.sql`](../sql/indicadores/r06_baja_anormal_o_nula.sql) | D-019. Presupuesto e importe de la misma base (sin IVA en PLACSP, con IVA en el portal). 11.909 aplicables, **2.226 activados (18,7 %)**. Hallazgo: tasa alta; revisar por separado baja nula y baja extrema al construir la puntuación. No usa las demás ofertas (art. 149 LCSP) porque no las tenemos |
| Anomalías | Implementado (señal aparte) | [`anomalias/deteccion.py`](../src/ojo_ciudadano/anomalias/deteccion.py) | D-021. 13.496 atípicos de 1.349.510 (1,0 %). Fuera de la puntuación hasta validarla |
| R-07 | Pendiente | — | Recortable |
| R-08 | Pendiente | — | Recortable |
