<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="src/ojo_ciudadano/app/static/logo.svg">
    <img src="src/ojo_ciudadano/app/static/logo-claro.svg" width="96" alt="Logo de Ojo Ciudadano">
  </picture>
</p>

# Ojo Ciudadano

**Seguir el dinero público de la Comunidad de Madrid, de cada órgano a cada empresa.**

Ojo Ciudadano es una plataforma de transparencia del gasto público: une contratos y subvenciones de la Comunidad de Madrid, calcula **indicadores de riesgo** con metodología abierta y permite investigarlo todo **en lenguaje natural**, con cada cifra enlazada a su documento oficial.

<p align="center">
  <a href="https://ojo-ciudadano.iismael.workers.dev/"><strong>Abrir la web: ojo-ciudadano.iismael.workers.dev</strong></a>
</p>

> Proyecto presentado a **[DataMad 2026](https://www.comunidad.madrid/node/120258)**. **Estado (26-nov-2026, entrega):** la web está publicada y funciona con datos reales: más de 1,35 millones de contratos y 872.821 concesiones de subvenciones de 2023 a 2026, 132 organismos, seis indicadores de riesgo, contratos atípicos y un asistente que responde en lenguaje natural con su fuente. No hace falta instalar nada para probarla.

---

## El problema

La información sobre el gasto de la Comunidad de Madrid **es pública, pero no es transparente**. Contratos, subvenciones, presupuestos y altos cargos están en portales distintos, con formatos distintos y sin identificadores comunes. Datos clave, como el número de ofertas de una licitación, solo aparecen en PDF.

Saber qué empresas reciben más dinero de una consejería, o si esa consejería adjudica casi siempre a las mismas, hoy exige descargar ficheros de varios portales, unirlos a mano y dominar la jerga de la contratación pública.

## Qué hace Ojo Ciudadano

Todo está en la web: [ojo-ciudadano.iismael.workers.dev](https://ojo-ciudadano.iismael.workers.dev/).

| Pantalla | Qué enseña |
| --- | --- |
| **Inicio** | Un buscador único de empresas y organismos, las grandes cifras y las seis señales explicadas como «X de cada 100 contratos donde se pudo comprobar». |
| **Mapa del dinero** | Dos vistas. **¿A dónde va?**: la Comunidad, sus consejerías y sus contratos como burbujas que se llenan hasta lo gastado, y lo que toca a cada habitante. **¿De dónde viene?**: los ingresos por capítulo, el sistema de financiación y las ayudas de la UE. |
| **Contratos a revisar** | Contratos ordenados por número de señales, con el motivo de cada una en una frase y el enlace al expediente oficial. |
| **Contratos atípicos** | Contratos que se alejan de otros parecidos según un modelo de aprendizaje automático no supervisado, con las cifras que los alejan. Es una señal experimental, aparte de los indicadores. |
| **Red del dinero** | De cada organismo a las empresas y beneficiarios que más reciben, por año, tipo de contrato y procedimiento. |
| **Ficha de empresa** | Todo lo que ha recibido un NIF: contratos, menores, prórrogas, modificaciones, subvenciones, encargos y registros públicos. |
| **Ficha de órgano** | Cómo contrata cada consejería u organismo frente a los demás, su presupuesto y sus principales empresas. |
| **Presupuesto y contexto** | Presupuesto por consejería, series presupuestarias, convenios y plantillas de la Comunidad. |
| **Asistente** | Preguntas en lenguaje natural («¿qué organismos adjudicaron más importe en 2025?», «¿la Comunidad tiene helicópteros?»). Responde con la consulta usada, los datos y el enlace a cada registro, y busca también en el catálogo de datos abiertos, en los pliegos y en las resoluciones del Tribunal de Contratación. Solo lee los datos y solo responde sobre el gasto público de la Comunidad. |

## Indicadores de riesgo, no acusaciones

Ojo Ciudadano **no detecta corrupción**: señala **dónde hay más riesgo y menos transparencia**, para que periodistas, auditores y ciudadanos sepan dónde mirar primero. Seguimos la [guía de *red flags* de la Open Contracting Partnership](https://open-contracting.org/redflags) y la literatura académica:

- **Licitador único** en procedimientos abiertos.
- **Procedimientos sin publicidad** y emergencias.
- **Posible fraccionamiento** de contratos menores.
- **Concentración** de proveedores en un órgano o mercado.
- **Sobrecostes** por modificaciones y prórrogas.
- **Bajas** anormales o nulas.

Cada indicador se compara con contratos del mismo tipo, se calcula con SQL abierto en este repositorio y cada alerta enlaza al expediente oficial.

Además, un modelo **no supervisado** (Isolation Forest) marca el 1 % de contratos más **atípicos respecto a sus pares**. Atípico no significa irregular: es una señal experimental que no suma a la puntuación. Detalle en [`docs/04-indicadores-riesgo.md`](docs/04-indicadores-riesgo.md).

## Datos

Solo fuentes públicas y reutilizables:

- [Portal de la Contratación Pública de la Comunidad de Madrid](https://www.comunidad.madrid/press-releases/download/77053)
- [Plataforma de Contratación del Sector Público (PLACSP)](https://www.hacienda.gob.es/es-ES/GobiernoAbierto/Datos%20Abiertos/Paginas/LicitacionesAgregacion.aspx)
- [Base de Datos Nacional de Subvenciones (BDNS)](https://www.infosubvenciones.es)
- [Portal de Transparencia de la Comunidad de Madrid](https://www.comunidad.madrid/transparencia)
- Catálogo de Datos Abiertos de la Comunidad de Madrid (presupuesto, convenios, registros y plantillas)
- Tribunal Administrativo de Contratación Pública de la Comunidad de Madrid (recursos y resoluciones)
- INE (habitantes, para las cifras por persona) e INVENTE (entes del sector público)

**Privacidad:** no se crean fichas de personas físicas. Ojo Ciudadano seudonimiza sus identificadores y solo las muestra agregadas.

**Reutilización:** los datos se reutilizan según las condiciones de cada fuente: se cita la fuente y la fecha y no se altera el sentido de los datos. Origen de los datos de subvenciones: Intervención General de la Administración del Estado. Ninguna administración patrocina ni apoya el proyecto. Detalle en [`docs/02-fuentes-datos.md`](docs/02-fuentes-datos.md#condiciones-de-reutilización-p-03-revisado-el-2026-11-21).

## Para quién

Periodistas de datos y ONG de vigilancia · órganos de control y Cámara de Cuentas · la propia Administración · empresas y pymes · ciudadanía.

## Tecnología

Python · [uv](https://docs.astral.sh/uv/) · polars · DuckDB · Streamlit · Plotly · Three.js · scikit-learn (Isolation Forest) · un asistente LLM por OpenRouter con texto a SQL de solo lectura y búsqueda documental (BM25) con citas.

La web pública es [ojo-ciudadano.iismael.workers.dev](https://ojo-ciudadano.iismael.workers.dev/): una portada en Cloudflare que abre la aplicación de Streamlit, servida con Docker y un túnel de Cloudflare, y que se actualiza sola con cada cambio en `main`. Detalle en [`docs/15-despliegue.md`](docs/15-despliegue.md).

## Empezar

Para probarla no hace falta instalar nada: abre [ojo-ciudadano.iismael.workers.dev](https://ojo-ciudadano.iismael.workers.dev/). Para ejecutarla en tu ordenador:

```bash
# Requisito: uv (https://docs.astral.sh/uv/getting-started/installation/)
git clone https://github.com/iisma-ai/Ojo-Ciudadano.git
cd Ojo-Ciudadano
uv sync            # crea el entorno e instala dependencias
uv run pytest      # comprueba que todo funciona
```

Los datos no están en el repositorio: se regeneran en `data/` (ver [`docs/02-fuentes-datos.md`](docs/02-fuentes-datos.md)).

```bash
# 1. Datos brutos en data/raw/. Los CSV del portal regional se exportan a mano (captcha) y
#    el Atom de PLACSP se descarga por meses; las subvenciones, por la API de la BDNS:
uv run python -m ojo_ciudadano.ingesta.bdns
# 2. Base analítica, indicadores y puntuación, y contratos atípicos:
uv run python -m ojo_ciudadano.modelo.carga
uv run python -m ojo_ciudadano.indicadores.ejecutor
uv run python -m ojo_ciudadano.anomalias.deteccion
# 3. Contexto de la Comunidad, nombres de los CPV, entes públicos y búsqueda del asistente:
uv run python -m ojo_ciudadano.modelo.contexto
uv run python -m ojo_ciudadano.ingesta.cpv
uv run python -m ojo_ciudadano.ingesta.invente
uv run python -m ojo_ciudadano.asistente.texto
uv run python -m ojo_ciudadano.asistente.catalogo
# 4. Interfaz (el asistente necesita OPENROUTER_API_KEY en .env; plantilla en .env.example):
uv run streamlit run src/ojo_ciudadano/app/main.py
```

## Cómo colaborar

Antes de escribir código, lee:

1. [`CLAUDE.md`](CLAUDE.md): reglas del proyecto (válidas para personas y agentes de IA).
2. [`docs/08-plan.md`](docs/08-plan.md): el plan y quién hace qué.
3. [`docs/decisions.md`](docs/decisions.md): lo que ya está decidido.

Toda la documentación está en [`docs/`](docs/README.md). Documentamos todo lo que hacemos en [`docs/bitacora/`](docs/bitacora/).

## Licencia

El código y la documentación se publican con licencia [MIT](LICENSE). Los datos no forman parte del repositorio: pertenecen a sus fuentes oficiales y se reutilizan según las condiciones de cada una (ver «Datos»).

## Equipo

Equipo de 4 personas para DataMad 2026.
