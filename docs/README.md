# Documentación de Ojo Ciudadano

Esta carpeta es la **memoria del proyecto**. Todo lo que sabemos, decidimos y hacemos queda aquí. Si no está en `docs/`, para el equipo (y para los agentes) no existe.

Estado a 21 de noviembre de 2026: **fase 2 (construcción) casi cerrada.** Datos de contratos y subvenciones cargados, seis indicadores con puntuación, detección de anomalías, interfaz rediseñada para la ciudadanía (D-022, D-023) y asistente sin proveedor de LLM todavía (D-010). Resumen y siguientes pasos en [`bitacora/2026-11-21-cierre-del-dia.md`](bitacora/2026-11-21-cierre-del-dia.md).

## Índice

| Documento | Qué contiene | Cuándo leerlo |
| --- | --- | --- |
| [decisions.md](decisions.md) | Registro de decisiones (qué, por qué, alternativas) | **Siempre**, antes de proponer un cambio de enfoque |
| [01-vision.md](01-vision.md) | Problema, propuesta, usuarios y encaje con DataMad 2026 | Al incorporarte al proyecto |
| [02-fuentes-datos.md](02-fuentes-datos.md) | Fuentes oficiales, formatos, limitaciones y lo que dejamos fuera | Antes de tocar ingesta o datos |
| [03-modulos.md](03-modulos.md) | Los cinco módulos de la plataforma y su alcance en el MVP | Antes de tocar la interfaz |
| [04-indicadores-riesgo.md](04-indicadores-riesgo.md) | Metodología de indicadores y puntuación de riesgo | Antes de tocar indicadores |
| [05-asistente.md](05-asistente.md) | Diseño del asistente (texto a SQL + RAG) y reglas de respuesta | Antes de tocar el asistente |
| [06-arquitectura.md](06-arquitectura.md) | Capas, tecnologías y estructura del repositorio | Antes de crear carpetas o módulos nuevos |
| [07-riesgos.md](07-riesgos.md) | Riesgos legales, de datos, técnicos y de proyecto, con mitigaciones | Antes de publicar cualquier texto o dato |
| [08-plan.md](08-plan.md) | **El plan**: fases, hitos, responsables y lista de recortes | **Siempre**, al empezar cada sesión |
| [09-preguntas-abiertas.md](09-preguntas-abiertas.md) | Lo que aún no sabemos y hay que confirmar | Al empezar cada sesión |
| [10-glosario.md](10-glosario.md) | Jerga de contratación pública y siglas | Cuando dudes de un término |
| [11-accesibilidad.md](11-accesibilidad.md) | **Accesibilidad y visualización**: principios, tareas A-xx por pantalla y estudios de visualización por indicador | Antes de tocar cualquier pantalla |
| [marca.md](marca.md) | Logo, paleta, tipografía y reglas de estilo (sin emojis) | Antes de tocar la interfaz o la presentación |
| [bitacora/](bitacora/) | Registro de lo hecho en cada sesión de trabajo | **Siempre**: al empezar (leer) y al terminar (escribir) |

## Reglas de esta carpeta

1. **Se documenta todo lo que se hace.** Cada sesión de trabajo (humana o de un agente) termina con una entrada en `bitacora/` y con los documentos afectados actualizados.
2. **El plan manda.** `08-plan.md` y `decisions.md` se respetan en la medida de lo posible. Si algo obliga a desviarse, se registra una decisión nueva en `decisions.md` antes (o justo después) de desviarse, nunca en silencio.
3. **Las preguntas abiertas se cierran por escrito.** Cuando se confirme algo de `09-preguntas-abiertas.md`, se marca como resuelto, se anota la respuesta y la fuente, y se actualizan los documentos que dependían de ello.
4. **Hechos con fuente.** Cualquier afirmación sobre datos, leyes o portales lleva enlace y fecha de consulta.
5. **Español** como idioma de la documentación.

## Origen

Estos documentos se derivan de la propuesta *«Plataforma de transparencia del gasto público de la Comunidad de Madrid»* (Propuesta para DataMad 2026, 15 nov 2026, El Harrak). El original se conserva en local y no se sube al repositorio; su contenido está íntegramente trasladado aquí y, a partir de ahora, **la fuente de verdad es `docs/`**.
