<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="src/ojo_ciudadano/app/static/logo.svg">
    <img src="src/ojo_ciudadano/app/static/logo-claro.svg" width="96" alt="Logo de Ojo Ciudadano">
  </picture>
</p>

# Ojo Ciudadano

**Seguir el dinero público de la Comunidad de Madrid, de cada órgano a cada empresa.**

Ojo Ciudadano es una plataforma de transparencia del gasto público: une contratos y subvenciones de la Comunidad de Madrid, calcula **indicadores de riesgo** con metodología abierta y permite investigarlo todo **en lenguaje natural**, con cada cifra enlazada a su documento oficial.

> Proyecto presentado a **[DataMad 2026](https://www.comunidad.madrid/node/120258)**. Estado (21-nov): datos, indicadores, las cuatro pantallas, contratos atípicos y preguntas guiadas funcionando con datos reales; el asistente de texto libre está en desarrollo. Entrega el 26 de noviembre de 2026.

---

## El problema

La información sobre el gasto de la Comunidad de Madrid **es pública, pero no es transparente**. Contratos, subvenciones, presupuestos y altos cargos están en portales distintos, con formatos distintos y sin identificadores comunes. Datos clave, como el número de ofertas de una licitación, solo aparecen en PDF.

Saber qué empresas reciben más dinero de una consejería, o si esa consejería adjudica casi siempre a las mismas, hoy exige descargar ficheros de varios portales, unirlos a mano y dominar la jerga de la contratación pública.

## Qué hace Ojo Ciudadano

| | |
| --- | --- |
| **Mapa general** | La Comunidad y sus consejerías en un mapa de nodos arrastrable: dinero disponible, gastado y sin gastar, y los contratos de cada una. |
| **Mapa del dinero** | Flujos órgano → empresa y órgano → beneficiario, por año, tipo de contrato y procedimiento. |
| **Ficha de empresa** | Todo lo que ha recibido un NIF: contratos, menores, prórrogas, modificaciones y subvenciones. |
| **Ficha de órgano** | Cómo contrata cada consejería u organismo, comparado con los demás. |
| **Panel de alertas** | Contratos ordenados por puntuación de riesgo, con el motivo de cada alerta. |
| **Contratos atípicos** | Contratos que se alejan de otros similares según un modelo de aprendizaje automático no supervisado, con las cifras que los alejan. Señal experimental, aparte de los indicadores. |
| **Asistente de investigación** | Hoy, preguntas guiadas con consultas verificadas. En desarrollo: pregunta en lenguaje natural («¿qué empresas acumulan más contratos menores en Sanidad en 2025?») y recibe la respuesta con la consulta usada y el enlace a cada registro. |

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
- Catálogo de Datos Abiertos de la Comunidad de Madrid

**Privacidad:** no se crean fichas de personas físicas. Ojo Ciudadano seudonimiza sus identificadores y solo las muestra agregadas.

**Reutilización:** los datos se reutilizan según las condiciones de cada fuente: se cita la fuente y la fecha y no se altera el sentido de los datos. Origen de los datos de subvenciones: Intervención General de la Administración del Estado. Ninguna administración patrocina ni apoya el proyecto. Detalle en [`docs/02-fuentes-datos.md`](docs/02-fuentes-datos.md#condiciones-de-reutilización-p-03-revisado-el-2026-11-21).

## Para quién

Periodistas de datos y ONG de vigilancia · órganos de control y Cámara de Cuentas · la propia Administración · empresas y pymes · ciudadanía.

## Tecnología

Python · [uv](https://docs.astral.sh/uv/) · polars · DuckDB · Streamlit · un asistente LLM con texto a SQL y búsqueda documental con citas.

## Empezar

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
# 3. Interfaz:
uv run streamlit run src/ojo_ciudadano/app/main.py
```

## Cómo colaborar

Antes de escribir código, lee:

1. [`CLAUDE.md`](CLAUDE.md): reglas del proyecto (válidas para personas y agentes de IA).
2. [`docs/08-plan.md`](docs/08-plan.md): el plan y quién hace qué.
3. [`docs/decisions.md`](docs/decisions.md): lo que ya está decidido.

Toda la documentación está en [`docs/`](docs/README.md). Documentamos todo lo que hacemos en [`docs/bitacora/`](docs/bitacora/).

## Equipo

Equipo de 4 personas para DataMad 2026.
