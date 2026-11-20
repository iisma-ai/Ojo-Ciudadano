# 2026-11-20 · Subvenciones de la BDNS (F-03)

- **Autor:** Claude (agente), a petición de Ignacio
- **Fase del plan:** 2 · Construcción en paralelo (entregable de la persona 1 para H2: «contratos y subvenciones en DuckDB»)

## Qué se hizo
- Rama `feat/ingesta-bdns` desde `origin/main`, con `/nueva-fuente`.
- **Exploración de la API** (sin clave):
  - La Comunidad es la administración autonómica `id 16` y tiene 27 órganos hijos. Se filtra por los hijos: con el id del padre la API devuelve 0.
  - La BDNS asigna las concesiones antiguas al nombre actual de cada órgano.
  - Volumen por año: 25.547 (2023), 31.140 (2024), 457.978 (2025) y 335.213 (2026). El salto se debe a la PAC.
  - Detalle en `docs/02-fuentes-datos.md` (F-03).
- **`ingesta/bdns.py`:**
  - Descarga por meses con páginas de 10.000, una petición cada vez y 1 s de pausa. Caché en `data/raw/bdns/AAAA-MM.json`.
  - `leer` devuelve concesiones, beneficiarios y órganos.
  - `minimizar` quita el nombre de las personas físicas antes de guardar la caché.
  - `EQUIVALENCIAS_ORGANO` recoge 5 órganos que la BDNS nombra distinto que los portales (SERMAS, IMIDRA, IRSST, ASEM 112 y Economía).
- **Esquema:** `sql/esquema/002_subvenciones.sql` crea la tabla `concesion`. Es una ampliación aditiva permitida por D-017 y no cambia ninguna tabla existente.
- **`modelo.carga`:** lee la BDNS si hay ficheros. Los beneficiarios van a `adjudicatario` con la misma identidad que en los contratos, y los órganos nuevos a `organo`, conservando el nombre que traen los contratos.
- **Datos cargados:** 849.878 concesiones y 132 órganos (solo uno nuevo: la Asamblea).
  - 750.431 concesiones son de personas físicas, seudonimizadas con `idPersona` y sin nombre ni NIF.
  - 2.863 entidades tienen contratos y subvenciones.
  - Las cifras de los indicadores no cambian. La base ocupa 740 MB.
- **Asistente:** `concesion` entra en la lista blanca. La pregunta 4 suma contratos y subvenciones por fuente y año (2023–2026), sin mezclar bases.
- **Ficha de empresa:** desplegable «Subvenciones concedidas» con el total real, las 20 convocatorias de mayor importe y el enlace a su ficha en la BDNS.
- Revisión con `revisor-legal`, aplicada:
  - fecha de descarga y explicación del enlace;
  - aviso de que el beneficiario puede ser una entidad pública o sin ánimo de lucro;
  - en la pregunta 4, «entidad» e «importes adjudicados/concedidos», y `url_origen` por fuente;
  - caché sin nombres;
  - los NIF `otro` de la BDNS se tratan como persona física.
- 138 tests y `ruff` en verde. Las cinco pantallas cargan con la base real.

## Decisiones tomadas
- Ninguna nueva. El esquema 002 es la ampliación aditiva prevista en D-017 (hay que avisar al equipo; va en el PR).

## Desviaciones del plan
- Ninguna. Es el entregable de subvenciones del H2, que nadie había empezado.

## Problemas y hallazgos
- La BDNS **publica el nombre completo** de las personas físicas junto al NIF enmascarado. No se guarda en ningún sitio.
- El NIF enmascarado lo comparten muchas personas, así que no sirve como identificador. Por eso se usa `idPersona`. Estas personas no se pueden cruzar con las de los contratos.
- La página del aviso legal de la BDNS se carga con JavaScript y no se ha podido leer por código. **P-03 sigue abierta para la BDNS:** hay que leerla a mano.
- Entre los «beneficiarios» hay ayuntamientos, universidades y colegios profesionales. La pantalla se sigue llamando «Ficha de empresa», con un aviso.
- `data/raw/bdns` ocupa 550 MB en local (no se sube).

## Siguiente paso
- **Cada persona del equipo**: `uv run python -m ojo_ciudadano.ingesta.bdns` (unos 20 min), después `modelo.carga` y después `indicadores.ejecutor`.
- Leer a mano el aviso legal de la BDNS (P-03).
- Para cuando se conecte el LLM (D-010): impedir que el asistente agrupe o filtre por seudónimos `PF-…` en `concesion`, para que no arme perfiles de personas físicas (lo señaló `revisor-legal`).
- Opcional si da tiempo: subvenciones en la ficha de órgano y en el mapa del dinero.
