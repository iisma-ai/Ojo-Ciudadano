# 03 · Módulos de la plataforma

Cinco módulos; los cinco entran en la demo, dos de ellos en versión simplificada.

| Módulo | Qué hace | Pregunta que responde | En el MVP |
| --- | --- | --- | --- |
| **Mapa del dinero** | Flujos órgano → empresa y órgano → beneficiario, por año, CPV y procedimiento | ¿A quién paga cada consejería y por qué vía? | Sí |
| **Ficha de empresa** | Todo lo recibido por un NIF: contratos, menores, prórrogas, modificaciones, subvenciones; con sus indicadores | ¿Cuánto ha cobrado esta empresa y de quién? | Sí (**no recortable**) |
| **Ficha de órgano** | Gasto contratado, procedimientos usados, proveedores principales y riesgo agregado | ¿Cómo contrata este órgano comparado con los demás? | Sí |
| **Panel de alertas** | Contratos ordenados por puntuación de riesgo, con el motivo de cada alerta | ¿Qué contratos merece la pena revisar primero? | Sí, simplificado |
| **Asistente de investigación** | Preguntas en lenguaje natural sobre todo lo anterior, con respuestas citadas | Cualquier pregunta ad hoc | Sí, con preguntas de demo preparadas |

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
