# 07 · Riesgos y mitigaciones

**El mayor riesgo no es técnico: es acusar en falso.** Le siguen la falta del número de licitadores en los datos y un alcance demasiado grande para 11 días.

| ID | Categoría | Riesgo | Prob. | Impacto | Mitigación |
| --- | --- | --- | --- | --- | --- |
| K-01 | Legal | Señalar a empresas o cargos como corruptos sin pruebas (derecho al honor, difamación) | Media | Alto | Hablar siempre de «indicadores de riesgo»; aviso visible; metodología pública; cada alerta explica su motivo y enlaza al expediente |
| K-02 | Legal | Datos personales: autónomos adjudicatarios, beneficiarios personas físicas, altos cargos (RGPD) | Alta | Alto | No crear fichas de personas físicas; agregar o seudonimizar sus NIF; altos cargos solo con lo que la ley ya obliga a publicar. En los PDF del TACPCM y los pliegos (D-032) se tapan DNI, NIE, nombres con tratamiento y firmas, y no se muestran las páginas «en nombre propio». Residual: un nombre sin tratamiento puede verse en un extracto |
| K-03 | Legal | Incumplir condiciones de reutilización (catálogo, aviso legal de la BDNS) | Baja | Medio | Citar fuente y fecha de descarga; no alterar el sentido de los datos; fórmula de cita de la IGAE en subvenciones; decir quién disocia los datos personales; no sugerir patrocinio (condiciones revisadas el 21-nov, P-03 resuelta, ver 02) |
| K-04 | Datos | El CSV regional no trae el número de ofertas y caen los indicadores de competencia | Media | Alto | Tomarlo de PLACSP; extraerlo con IA de las actas en una muestra; si no, priorizar indicadores que no lo necesitan |
| K-05 | Datos | El Catálogo de Datos Abiertos no tiene los datasets clave y el proyecto no cumple las bases | Media | Alto | Confirmarlo el día 1; usar como base lo que sí haya y completar con fuentes estatales |
| K-06 | Datos | NIF mal escritos, nombres con variantes, UTE como entidades separadas | Alta | Medio | Normalizar NIF; tabla de alias; modelar las UTE con sus empresas miembro |
| K-07 | Datos | Duplicados entre portal regional y PLACSP; varias versiones de una licitación en Atom | Alta | Medio | Deduplicar por expediente + órgano y quedarse con la última versión |
| K-08 | Datos | Cambios de estructura entre años y cobertura desigual | Media | Medio | Acotar el MVP a 2023–2026; documentar huecos en la propia plataforma |
| K-09 | Datos | Límites de descarga (BDNS trocea; portales que bloquean acceso automatizado) | Media | Medio | Descargas por meses; caché local; descarga manual de los CSV si hace falta |
| K-10 | Expectativas | El público espera «seguir cada euro» desde el presupuesto y los datos no enlazan partida con contrato | Alta | Medio | Decirlo explícitamente; mostrar presupuesto y contratos como dos niveles separados |
| K-11 | Técnico | Falsos positivos: proveedores únicos legítimos (exclusividad técnica, emergencias, mercados pequeños) | Alta | Alto | Comparar con contratos del mismo tipo y CPV; excluir causas legales de exclusividad; puntuación gradual |
| K-12 | Técnico | El LLM genera SQL erróneo o inventa cifras | Media | Alto | SQL solo lectura y validado; mostrar la consulta; responder solo con datos devueltos; batería de 20 preguntas de prueba |
| K-13 | Técnico | Inyección de instrucciones desde textos de pliegos o informes indexados | Baja | Medio | Tratar el corpus como datos; el agente no tiene herramientas que modifiquen nada |
| K-14 | Técnico | La demo falla en directo (API caída, latencia, coste) | Media | Alto | Respuestas de demo cacheadas; vídeo de respaldo; modelo alternativo configurado |
| K-15 | Reputacional | Percepción partidista: la competición la organiza la propia Comunidad | Media | Medio | Enfoque en procesos y métricas comparables entre órganos, no en personas ni partidos; presentarlo como herramienta de mejora |
| K-16 | Reputacional | Usuarios que interpretan una alerta como prueba | Alta | Medio | Textos de ayuda en cada alerta: qué significa y qué no |
| K-17 | Proyecto | Alcance excesivo para 11 días y 4 personas | Alta | Alto | MVP congelado el día 2; lista de recortes priorizada (ver [08-plan.md](08-plan.md)) |
| K-18 | Proyecto | El pipeline de datos bloquea al resto del equipo | Media | Alto | Muestra de datos limpia y esquema fijado el 17-nov para trabajar en paralelo |
| K-19 | Proyecto | El jurado lo ve parecido a Civio o a Gobierto | Media | Medio | Remarcar lo nuevo: ámbito regional, indicadores de riesgo y consulta en lenguaje natural con citas |

## Lenguaje: qué decir y qué no

| Decir | No decir |
| --- | --- |
| «indicador de riesgo», «señal», «alerta» | «corrupción», «fraude», «irregular» (como afirmación) |
| «contrato con licitador único» | «contrato amañado» |
| «posible fraccionamiento según la regla X» | «han fraccionado para evitar licitar» |
| «concentración alta en este mercado» | «empresa favorecida», «enchufe» |
| «merece revisión» | «culpable», «sospechoso» aplicado a personas |

Cualquier texto visible para usuarios (interfaz, README, presentación, respuestas del asistente) puede revisarse con el agente `revisor-legal`.
