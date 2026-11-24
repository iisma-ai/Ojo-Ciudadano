# 03 · Módulos de la plataforma

Cinco módulos; los cinco entran en la demo, dos de ellos en versión simplificada.

| Módulo | Qué hace | Pregunta que responde | En el MVP |
| --- | --- | --- | --- |
| **Mapa del dinero** | Flujos órgano → empresa y órgano → beneficiario, por año, CPV y procedimiento | ¿A quién paga cada consejería y por qué vía? | Sí |
| **Ficha de empresa** | Todo lo recibido por un NIF: contratos, menores, prórrogas, modificaciones, subvenciones; con sus indicadores | ¿Cuánto ha cobrado esta empresa y de quién? | Sí (**no recortable**) |
| **Ficha de órgano** | Gasto contratado, procedimientos usados, proveedores principales y riesgo agregado | ¿Cómo contrata este órgano comparado con los demás? | Sí |
| **Panel de alertas** | Contratos ordenados por puntuación de riesgo, con el motivo de cada alerta | ¿Qué contratos merece la pena revisar primero? | Sí, simplificado |
| **Asistente de investigación** | Preguntas en lenguaje natural sobre todo lo anterior, con respuestas citadas; las frecuentes, con respuesta preparada y SQL verificado, y las demás con el modelo (D-037) | Cualquier pregunta ad hoc | Sí, con 43 respuestas preparadas |

## A dónde va el dinero (mapa general; D-026, D-033, D-038)

Segunda pantalla, después del Inicio, pensada para un ciudadano cualquiera.

- **Año** arriba (el que aún no tiene gasto publicado sale como «previsto»).
- **Tarjeta del año:**
  - la frase «En 2025 la Comunidad de Madrid tuvo X y gastó N de cada 100 €», con una barra de lo gastado;
  - lo que tocaría a cada habitante si se repartiera (habitantes del INE, F-12), con una figura que sujeta billetes y una figurita por cada millón de habitantes.
- **«¿A dónde van cada 100 €?»:** treemap de billetes (`app/billetes.py`).
  - Cada bloque es una consejería y cada billete vale lo mismo en todo el gráfico; la leyenda dice cuánto.
  - Los billetes grises son lo que quedó sin gastar.
  - Al pulsar un bloque se ven los 15 contratos más grandes de esa consejería en billetes, con la ficha del bloque pulsado al lado, y los menores y las subvenciones en una línea.
- **«¿Cuánto ha gastado cada consejería?»:** una línea por consejería con su barra, el porcentaje gastado, lo que queda y el gasto medio diario.
- **«Más opciones»:** qué dinero ver (presupuesto, contratos de la Plataforma o del portal, subvenciones) y la **red de contratos** de D-033 como vista avanzada (`app/red.py`). Esta conserva los niveles, los contratos por consejería y la ficha lateral.
- **Desplegables:** «Ver los datos en tabla» y «Qué datos no tenemos».
- El «Mapa del dinero» sigue usando el diseño de nodos.

## Búsqueda y filtros (D-025)

Las búsquedas de empresa y de organismo se autocompletan (primero lo que empieza por lo escrito). «Contratos atípicos» ordena por lejanía o importe, filtra por nivel mínimo y variable, y oculta por defecto los posibles errores de introducción de datos (interruptor para verlos). «Contratos a revisar» permite elegir varias señales (cualquiera o todas), año, tipo, orden, mínimo de señales y organismo o empresa concretos.

## Presupuesto y contexto (D-024)

Pantalla de contexto con datos de la Comunidad de Madrid: gasto por consejería con los contratos y subvenciones de sus órganos al lado, evolución por capítulo, gastos e ingresos presupuestados, personal, convenios y registros. La ficha de órgano muestra el presupuesto de su consejería y la de empresa, los registros donde figura su NIF. No son indicadores de riesgo y no se cruzan partida a partida con los contratos. Detalle en [12-datos-cm.md](12-datos-cm.md).

## Encargos, fondos europeos y recursos (D-027 a D-029)

Datos añadidos el 23-nov, ninguno es una señal de riesgo (`app/datos_flujos.py`):
- **Ficha de órgano:** desplegable «Encargos a medios propios» con el total, a qué entidades y la lista de encargos enlazada a su ficha oficial.
- **Ficha de empresa:** «Encargos recibidos como medio propio» por organismo. Además, la ficha y el buscador ya incluyen a las entidades **sin contratos** que reciben subvenciones o encargos (antes no se podían consultar: 22.115 entidades con ficha, ahora 44.926). Si no tiene contratos, la ficha lo dice y oculta las secciones de contratos.
- **Tarjeta de contrato:** «Financiado con fondos de la Unión Europea (programa)» y, si está enlazado, «Recurrido ante el Tribunal de Contratación» con el resultado y el enlace a la resolución.
- **Presupuesto y contexto:** pestañas «Encargos a medios propios» (por año, entidad y organismo) y «Recursos ante el Tribunal» (resultado por acto recurrido).
- Textos de aviso: `textos.AVISO_ENCARGOS` y `textos.AVISO_RECURSOS`.

## Reglas de interfaz (todas las pantallas)

1. **Cada cifra enlaza al registro oficial** del que sale (contrato, concesión, documento).
2. Se habla de **«indicadores de riesgo»**, nunca de «corrupción» ni «irregularidad probada».
3. **Aviso visible** de metodología y de qué significa (y qué no) una alerta, con enlace a la metodología pública.
4. Cada alerta muestra **qué indicador la disparó, con qué valor** y el enlace al expediente.
5. **No hay fichas de personas físicas** (autónomos, beneficiarios particulares). Sus NIF se agregan o seudonimizan.
6. Presupuesto y contratos se muestran como **dos niveles separados**; se explica que no hay enlace partida → contrato.
7. Fecha de actualización de los datos visible.
8. **Primero se ve, luego se lee** (D-023): cada pantalla empieza por un gráfico o una cifra que responde a su pregunta, con lenguaje claro y sin texto repetido. Tareas y estudios en [11-accesibilidad.md](11-accesibilidad.md).

## Tecnología

Streamlit para el MVP (ver D-005). Se puede migrar después del datatón.
