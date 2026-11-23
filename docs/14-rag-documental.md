# 14 · RAG documental: investigación y plan (23-nov)

El asistente de texto a SQL ya está conectado (D-010, rama `feat/asistente-openrouter`). Este documento recoge lo investigado el 23-nov para decidir si se hace la segunda herramienta del asistente, el **RAG documental** ([05-asistente.md](05-asistente.md)). Es el recorte n.º 2 del plan. Decisión propuesta: [D-030](decisions.md).

## Qué problema resuelve

Las señales dicen **qué** pasa y no **por qué**. El caso más claro es el motivo de R-02: «La ley lo permite en supuestos concretos; los datos publicados no indican cuál se alegó». Ese supuesto está escrito en el pliego. Lo mismo ocurre con otras señales:

| Señal | Lo que el pliego puede explicar |
| --- | --- |
| R-02 · Sin publicidad | El supuesto legal alegado: exclusividad, razones técnicas (art. 168), etc. |
| R-01 · Licitador único | La solvencia exigida y los criterios de adjudicación, que pueden explicar por qué se presentó una sola empresa |
| R-05 · Modificaciones | Las modificaciones **previstas** en el pliego y su límite: el 20 % de D-016 es una referencia general |
| R-06 · Baja anormal | El umbral de oferta anormalmente baja que fija el pliego |

Cada uno de estos datos es una **explicación legítima** posible. Mostrarlos refuerza la regla de no acusar (D-002): la persona ve la señal y lo que dice el propio expediente.

## Qué se ha comprobado

**Con datos reales:**

1. **Los pliegos están enlazados en los datos que ya descargamos.**
   - En el Atom de PLACSP de enero de 2025, 2.283 de las 2.357 entradas de la Comunidad (97 %) traen el pliego de cláusulas administrativas (PCAP), y 2.215 (94 %) el de prescripciones técnicas (PPT).
   - Son enlaces directos a PDF en `contratos-publicos.comunidad.madrid/sites/default/files/PCON/…`.
   - Hoy no los guardamos: la ingesta los ignora.
2. **Se descargan sin captcha.** 3 de 3 PDF con respuesta 200, de 0,9 a 2,9 MB cada uno.
3. **Tienen texto digital, no escaneado.** 146 páginas en total, solo 1 sin texto. Son largos: de 15 a 84 páginas, entre 7.600 y 50.000 tokens cada uno. Por eso no se pueden pasar enteros al modelo y hay que recuperar las páginas relevantes.
4. **La búsqueda BM25 de DuckDB (extensión `fts`, con raíces en español) encuentra la página correcta.**
   - En 5 de 5 preguntas la página buena está entre las 3 primeras, y en 4 de 5 es la primera.
   - Preguntas probadas: supuesto sin publicidad, criterios, solvencia, modificaciones y penalidades.
   - Indexar 146 páginas tarda 0,9 s.
   - No necesita dependencias nuevas, porque DuckDB ya está instalado.
5. **El modelo responde bien con esas páginas.** Pregunta: «¿qué supuesto legal alega el pliego para adjudicarlo sin publicidad?» Respuesta de `gpt-6.1-terra`:

   > El pliego alega el supuesto de **ausencia de competencia por razones técnicas**, previsto en el artículo 168.a.2 de la LCSP. Lo denomina procedimiento negociado sin publicidad por exclusividad y señala que su aplicación está justificada en el expediente de contratación (págs. 6 y 12). Los fragmentos no explican cuáles son esas razones técnicas.

   Es correcta, cita la página y dice lo que el documento no explica. Costó 0,0014 USD (1.008 tokens).

**Límites encontrados:**
- **El portal regional no enlaza pliegos en sus fichas de contratos sin publicidad.** Se probaron 2 fichas, una de ellas de emergencia por COVID. Las emergencias y el «otro procedimiento» no suelen tener pliego.
  - Por tanto, el RAG cubre las **licitaciones de PLACSP**: 3.902 de las 11.250 señales R-02, 4.819 de R-01, 177 de R-05 y 1.065 de R-06.
  - Los contratos menores (R-03) no tienen pliego.
- **OpenRouter no ofrece modelos de embeddings.** La búsqueda semántica obligaría a instalar un modelo local (torch, cientos de MB) o a usar otro proveedor.
  - No hace falta: el modelo escribe las palabras clave de la búsqueda y BM25 acierta con el vocabulario jurídico, que es muy estable («solvencia», «criterios de adjudicación», «artículo 168»).
- **Informes de la Cámara de Cuentas:** no hay ninguno de contratación de 2023 a 2026; los publicados son de ejercicios anteriores (ver [04](04-indicadores-riesgo.md), «Validación»). Servirían como contexto general, pero no sobre nuestros contratos.
- **Resoluciones del TACPCM** (D-029, rama de otra persona): enlazan contratos concretos con el PDF de la resolución. Son un buen segundo corpus, pero D-029 decidió **no guardar el resumen** porque nombra empresas y personas (D-007). Indexar sus PDF necesita revisión legal previa.
- **Muestra pequeña:** 3 PDF y 5 preguntas. Las cifras de acierto hay que confirmarlas en la fase 1.

## Cómo funcionaría

**RAG «bajo demanda» sobre los pliegos de un contrato concreto.** No se descarga un corpus completo: 10.000 pliegos serían unos 15 GB y horas de descarga.

1. **Enlaces de los pliegos:** la ingesta de PLACSP guarda en una tabla aditiva `contrato_documento` cada enlace, con su contrato, su tipo (PCAP, PPT u otro) y su URL.
   - Es un fichero `sql/esquema/00x_documentos.sql`, permitido por D-017 como ampliación aditiva.
   - La tabla lleva `fuente`, `url_origen` y `fecha_descarga`.
2. **Herramienta nueva del agente,** `buscar_en_pliego(contrato_id, consulta)`. El modelo la usa después de identificar el contrato con SQL.
   1. Comprueba que el contrato tiene documentos en `contrato_documento`.
   2. Descarga el PDF si no está en caché (`data/raw/pliegos/`). Una descarga cada vez, solo de los dominios oficiales, con límite de tamaño y de páginas.
   3. Extrae el texto por páginas con `pypdf`, que es la única dependencia nueva: Python puro y ligera. Guarda las páginas en `fragmento_documento` y las indexa con BM25.
   4. Devuelve como mucho 3 páginas (unos 2.500 caracteres cada una) marcadas como **datos, nunca instrucciones**, con el documento, la página y el enlace.
3. **Reglas de respuesta nuevas:**
   - citar la página de cada afirmación, «(pliego administrativo, pág. 6)»;
   - explicar lo que dice el documento sin valorar si el procedimiento es correcto;
   - decir cuándo el pliego no lo explica.
   - Siguen aplicándose la retención por DNI, lenguaje y cifras, también sobre los fragmentos.
4. **Interfaz:** debajo de la respuesta, las páginas usadas con el enlace al PDF oficial en esa página (`…pdf#page=6`).
5. **Precarga para la demo:** se descargan antes los pliegos de unos 50 contratos que salen en las preguntas de demo y en los primeros puestos de R-02, R-01 y R-05. Así la demo no depende de la red.

## Plan de desarrollo

Calculado para una persona. **Total: unas 12 horas, 1,5 días.**

| Fase | Qué | Horas | Resultado comprobable |
| --- | --- | --- | --- |
| 1 | Enlaces de pliegos en la ingesta de PLACSP, tabla `contrato_documento`, regenerar la base. Medir la cobertura en los 47 meses | 3 | % de licitaciones con PCAP, por año y por señal |
| 2 | `asistente/documentos.py`: descarga con caché y límites, extracción por páginas, índice BM25 | 3 | Test con texto sintético; 20 pliegos reales indexados y el tiempo por pliego |
| 3 | Herramienta `buscar_en_pliego` en el agente y en `openrouter.py`, reglas y pantalla | 3 | Una pregunta de R-02 respondida en la interfaz con cita y enlace |
| 4 | 4 preguntas nuevas en la batería (B-21 a B-24, una por señal) con la página esperada; pasada con terra; `revisor-legal`; documentación | 2 | Acierto de página y de respuesta; revisión legal sin bloqueos |
| 5 | Precarga de unos 50 pliegos para la demo | 1 | La demo funciona sin red para esos contratos |

**Calendario y punto de control:**
- **24-nov a las 14:00 (H3):** con las fases 1 a 3 hechas, se decide si sigue.
  - Si la página buena sale entre las 3 primeras en menos del 70 % de las preguntas, o si la herramienta no está integrada, se desactiva y se presenta como «en desarrollo».
  - Desactivarla es retirar la herramienta de la lista del agente. El resto del asistente sigue igual.
- **El 25 no se añaden funciones** (plan): la fase 4 tiene que estar el 24 por la noche.

**Coste:**
- unos 0,002–0,005 USD más por pregunta documental: 3 páginas, unos 2.000 tokens;
- la batería documental, con terra, menos de 0,05 USD;
- la descarga de cada pliego la primera vez, de 1 a 3 s, y la extracción, de 1 a 5 s.

## Resultados esperados

**Si sale bien:**
- **Una respuesta nueva que hoy no tenemos:** «¿por qué este contrato se adjudicó sin publicidad?», con el supuesto legal y la página del pliego. Es el ejemplo más fuerte para la demo.
- **Menos riesgo de lectura acusatoria:** junto a cada señal de una licitación, la explicación que da el propio expediente.
- **Para el jurado:**
  - más uso de información pública de la Comunidad, con los documentos además de los datos;
  - trazabilidad hasta la página del documento oficial;
  - sin dependencias pesadas.

**Lo que no va a hacer:**
- Responder sobre contratos menores (R-03), emergencias o contratos solo del portal: no tienen pliego enlazado. Lo dirá.
- Juzgar si la justificación es suficiente: solo la cita.
- Recorrer miles de pliegos para estadísticas («¿cuántos sin publicidad alegan exclusividad?»). Eso es extracción masiva (recorte n.º 3), una línea posterior a la entrega.

**Riesgos y cómo se cubren:**

| Riesgo | Medida |
| --- | --- |
| Instrucciones escondidas en un pliego (K-13) | El texto se marca como datos; el agente no tiene herramientas que modifiquen nada; los filtros de salida no cambian |
| Nombres o firmas de personas en los pliegos (D-007) | Regla de no dar nombres de personas; retención si hay DNI o NIE en los fragmentos; los PDF del portal ya vienen anonimizados («anon_» en el nombre) |
| PDF escaneados sin texto | Medido en la fase 2; sin OCR (fuera de alcance): el asistente dice que el documento no tiene texto legible |
| Portal lento o caído en la demo | Precarga de la fase 5 y caché local |
| Cargar el portal | Una descarga cada vez, con pausa, solo de lo que se pregunta (ver condiciones de reutilización en [02](02-fuentes-datos.md)) |
| Choque con la ingesta de PLACSP de otra persona | La fase 1 toca `ingesta/placsp.py`: avisar antes y hacerla en una rama corta |

## Recomendación

**Hacerlo, en la versión acotada de este plan:**
- pliegos de PLACSP bajo demanda;
- BM25 de DuckDB, sin embeddings;
- punto de control el 24-nov a las 14:00.

El valor es concreto y está comprobado: responde a la pregunta que más necesitan las señales. El riesgo técnico es bajo, porque no hay dependencias pesadas, la demo no necesita red y se puede desactivar sin romper nada. Lo que se arriesga es tiempo: unas 12 horas el 24-nov, el mismo día de la prueba A-11 y del ensayo.

**No recomiendo para esta entrega:**
- **Informes de la Cámara de Cuentas:** son de otros años.
- **Embeddings:** no aportan sobre BM25 aquí y añaden dependencias pesadas.
- **PDF del TACPCM:** necesitan revisión legal antes.
