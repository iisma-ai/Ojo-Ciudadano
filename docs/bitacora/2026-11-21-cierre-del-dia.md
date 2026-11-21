# 2026-11-21 · Cierre del día: qué ha cambiado y qué hacer ahora

- **Autor:** Claude (agente)
- **Fase del plan:** 2, al final del día del hito H2. Esta entrada resume las bitácoras del 21-nov para quien retome el trabajo.

## Antes de seguir trabajando
1. `git pull` en `main` y `uv sync`: hay una dependencia nueva, scikit-learn.
2. **Regenerar la base:** han cambiado la normalización y la detección de anomalías, y hay tablas derivadas nuevas.
   ```bash
   uv run python -m ojo_ciudadano.modelo.carga
   uv run python -m ojo_ciudadano.indicadores.ejecutor
   uv run python -m ojo_ciudadano.anomalias.deteccion
   ```
   Para la BDNS hace falta `data/raw/bdns/`; si no lo tienes, descárgalo antes con `uv run python -m ojo_ciudadano.ingesta.bdns`. Cierra la interfaz mientras regeneras: DuckDB no deja escribir con la base abierta.
3. Lee **D-022** (identidad visual y sin emojis) y **D-023** (accesibilidad), y `docs/11-accesibilidad.md`, antes de tocar la interfaz.

## Qué ha cambiado hoy

### Datos y privacidad
- **Detección de anomalías (D-021):**
  - Isolation Forest por grupo de pares;
  - tablas `anomalia_resultado` y `anomalia_variables`;
  - 13.498 contratos atípicos (1 %).
- **D-007:**
  - Una UTE con alguna persona física y un NIF extranjero o erróneo sin forma jurídica en el nombre se guardan ya como persona física, sin nombre.
  - La interfaz y el asistente los filtran también en bases antiguas.
  - R-03 pasa de 222.122 a 222.116 activados.
- **P-03 resuelta:** condiciones de reutilización de las cuatro fuentes y pie de la interfaz con la cita de la IGAE. **P-07 resuelta.**
- **P-12 parcial:** los menores de julio a septiembre de 2026 están incompletos (publicación trimestral); hay un aviso en la interfaz.

### Interfaz (D-022 y D-023)
- **Identidad visual:**
  - logo vectorial en `app/static/`;
  - tema oscuro con acento azul en `.streamlit/config.toml`;
  - iconos Material;
  - **prohibidos los emojis**: regla 7 de `CLAUDE.md`, y `tests/test_sin_emojis.py` falla si aparece alguno.
- **Pantallas nuevas o rehechas:**

  | Pantalla | Qué tiene ahora |
  | --- | --- |
  | Portada | Nueva |
  | Contratos a revisar | Antes «Panel de alertas»; tarjetas desplegables y un gráfico por señal |
  | Ficha de empresa | Rehecha |
  | Ficha de organismo | Rehecha |
  | Mapa del dinero | Burbujas y red de cada organismo |
  | Contratos atípicos | Cada contrato frente a sus pares |
  | Preguntas guiadas y asistente | Gráfico automático en cada respuesta |

- **Código compartido de la interfaz:**
  - `app/graficos.py`: todos los gráficos y la paleta validada;
  - `app/senales.py`: la frase y el gráfico de cada señal, y `tarjeta_contrato`;
  - `app/textos.py`: lenguaje claro, glosario y formato español de cifras.
- La conexión a DuckDB es un cursor por sesión (`app/conexion.py`), para evitar el error «connection is busy».
- Todos los textos nuevos pasaron por `revisor-legal`.

### Asistente
- `anomalia_resultado` está en `TABLAS_PERMITIDAS`, con su regla de lenguaje.
- La batería de 20 preguntas que está en `main` es la de `feat/bateria-preguntas` (PR #5).

## Para el responsable de la interfaz
- Las fichas de empresa y de organismo, el mapa del dinero y «Contratos a revisar» se han reescrito enteras. Parte de `main` antes de tocarlas.
- Para un contrato con señales usa `senales.tarjeta_contrato`, y para una consulta cualquiera, `graficos.automatico`. No copies el código.

## Pendiente (por prioridad)
1. **Decisiones del equipo:**
   - D-010, proveedor de LLM: el asistente no responde preguntas libres sin él;
   - P-09, licencia del código: pesa en el criterio de «código abierto» del jurado;
   - P-08, despliegue público o solo local.
2. **A-11:** prueba con 2 o 3 personas no expertas, con el guion de `docs/11`. Antes de la demo del 24-nov.
3. **A-10, pasada final** el 24-25: móvil real y longitud de los textos de las fichas.
4. **Antes de la entrega:**
   - volver a exportar a mano (captcha) los menores del portal de julio a noviembre de 2026;
   - volver a descargar noviembre de PLACSP y la BDNS con `forzar`;
   - regenerar la base.
5. Validar los indicadores o las anomalías con casos de prensa de 2023-2026. Con la Cámara de Cuentas no es posible: sus informes son de años anteriores. Si no se hace, la presentación debe decir que no están validados.

## Ramas
Todo lo de hoy está fusionado en `main`. Quedan en remoto dos ramas que no hay que fusionar:
- `feat/bateria-asistente`: duplicaba la batería del PR #5;
- `docs/responsables`: su contenido ya está en `main`.

No se han borrado porque `CLAUDE.md` no permite borrar ramas remotas. Puede borrarlas quien las creó.
