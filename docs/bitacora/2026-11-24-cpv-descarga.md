# 2026-11-24 · Arreglo de la carga de los CPV (`ingesta/cpv.py`)

**Quién:** El Harrak, con Claude (agente). **Rama:** `fix/cpv-descarga`, que sale de `origin/main`.

## Qué se pidió
A una persona del equipo no le funcionaba `uv run python -m ojo_ciudadano.ingesta.cpv`: había que probarlo y buscar los fallos.

## Fallos encontrados
Se probaron en una carpeta temporal, sin tocar la base real.

1. **El portal rechaza la descarga.** Hoy `contrataciondelestado.es` devuelve una página «Request Rejected» de su cortafuegos (244 bytes) con código 200 en vez de la lista (3,3 MB). El 23-nov funcionaba.
   - El módulo guardaba esa página en `data/raw/cpv/` como si fuera la lista y fallaba al leerla con `XMLSyntaxError`.
   - Como la caché no estaba vacía, **seguía fallando aunque el portal volviera a responder**.
   - Es lo más probable en el caso de la persona del equipo.
2. **Base abierta por la web:** el error de DuckDB solo decía «File is already open in …python.exe».
3. **Base que no existe:** se creaba una base vacía con solo la tabla `cpv`.
4. **Lanzado desde otra carpeta:** no encontraba `sql/esquema/008_cpv.sql`.

## Qué se hizo
- **Comprobación del contenido:** `es_lista` comprueba que la respuesta es la lista genericode.
  - La página de rechazo no se guarda y el módulo avisa: prueba más tarde o copia el fichero de quien lo tenga, que es público.
  - Una caché que no es la lista se borra y se vuelve a bajar.
  - No se intenta saltar el bloqueo: ni otro agente de navegador ni reintentos en bucle.
- **Mensajes claros** si la web tiene la base abierta («para la web y vuelve a lanzar esto») o si la base no existe (no se crea). Por consola sale el mensaje sin la traza.
- La plantilla del esquema se busca desde la ruta del propio módulo.
- **Tests:** 4 nuevos en `tests/test_cpv.py` (rechazo, caché rota, base inexistente, base abierta), 6 en total.
- **Docs:** nota en F-10 (02) y una fila en el plan (08).

## Comprobaciones
- **Con el portal real:** la caché rota se borra y sale el aviso del rechazo, sin guardar nada.
- **Con la caché buena y la web abierta:** sale el aviso de parar la web.
- **Suite completa y `ruff`:** en verde.

## Siguiente paso
- **Para quien no pueda bajar la lista:** copiar `data/raw/cpv/CPV2008-2.04.gc` de quien la tenga, con la web parada, y lanzar el módulo.
- **Vigilar** si el cortafuegos también rechaza otras descargas de `contrataciondelestado.es`, como la sindicación de PLACSP.
