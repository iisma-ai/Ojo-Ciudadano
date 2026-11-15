# Ojo Ciudadano

**Seguir el dinero público de la Comunidad de Madrid, de cada órgano a cada empresa.**

Ojo Ciudadano es una plataforma de transparencia del gasto público: une contratos y subvenciones de la Comunidad de Madrid, calcula **indicadores de riesgo** con metodología abierta y permite investigarlo todo **en lenguaje natural**, con cada cifra enlazada a su documento oficial.

> Proyecto presentado a **[DataMad 2026](https://www.comunidad.madrid/node/120258)**. Estado: 🚧 planificación terminada, desarrollo en curso hasta el 26 de noviembre de 2026.

---

## El problema

La información sobre el gasto de la Comunidad de Madrid **es pública, pero no es transparente**. Contratos, subvenciones, presupuestos y altos cargos están en portales distintos, con formatos distintos y sin identificadores comunes. Datos clave, como el número de ofertas de una licitación, solo aparecen en PDF.

Saber qué empresas reciben más dinero de una consejería, o si esa consejería adjudica casi siempre a las mismas, hoy exige descargar ficheros de varios portales, unirlos a mano y dominar la jerga de la contratación pública.

## Qué hace Ojo Ciudadano

| | |
| --- | --- |
| 🗺️ **Mapa del dinero** | Flujos órgano → empresa y órgano → beneficiario, por año, tipo de contrato y procedimiento. |
| 🏢 **Ficha de empresa** | Todo lo que ha recibido un NIF: contratos, menores, prórrogas, modificaciones y subvenciones. |
| 🏛️ **Ficha de órgano** | Cómo contrata cada consejería u organismo, comparado con los demás. |
| 🚩 **Panel de alertas** | Contratos ordenados por puntuación de riesgo, con el motivo de cada alerta. |
| 💬 **Asistente de investigación** | Pregunta en lenguaje natural («¿qué empresas acumulan más contratos menores en Sanidad en 2025?») y recibe la respuesta con la consulta usada y el enlace a cada registro. |

## Indicadores de riesgo, no acusaciones

Ojo Ciudadano **no detecta corrupción**: señala **dónde hay más riesgo y menos transparencia**, para que periodistas, auditores y ciudadanos sepan dónde mirar primero. Seguimos la [guía de *red flags* de la Open Contracting Partnership](https://open-contracting.org/redflags) y la literatura académica:

- **Licitador único** en procedimientos abiertos.
- **Procedimientos sin publicidad** y emergencias.
- **Posible fraccionamiento** de contratos menores.
- **Concentración** de proveedores en un órgano o mercado.
- **Sobrecostes** por modificaciones y prórrogas.
- **Bajas** anormales o nulas.

Cada indicador se compara con contratos del mismo tipo, se calcula con SQL abierto en este repositorio y cada alerta enlaza al expediente oficial.

## Datos

Solo fuentes públicas y reutilizables:

- [Portal de la Contratación Pública de la Comunidad de Madrid](https://www.comunidad.madrid/press-releases/download/77053)
- [Plataforma de Contratación del Sector Público (PLACSP)](https://www.hacienda.gob.es/es-ES/GobiernoAbierto/Datos%20Abiertos/Paginas/LicitacionesAgregacion.aspx)
- [Base de Datos Nacional de Subvenciones (BDNS)](https://www.infosubvenciones.es)
- [Portal de Transparencia de la Comunidad de Madrid](https://www.comunidad.madrid/transparencia)
- Catálogo de Datos Abiertos de la Comunidad de Madrid

**Privacidad:** no se crean fichas de personas físicas; sus identificadores se agregan o seudonimizan.

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

## Cómo colaborar

Antes de escribir código, lee:

1. [`CLAUDE.md`](CLAUDE.md): reglas del proyecto (válidas para personas y agentes de IA).
2. [`docs/08-plan.md`](docs/08-plan.md): el plan y quién hace qué.
3. [`docs/decisions.md`](docs/decisions.md): lo que ya está decidido.

Toda la documentación está en [`docs/`](docs/README.md). Documentamos todo lo que hacemos en [`docs/bitacora/`](docs/bitacora/).

## Equipo

Equipo de 4 personas para DataMad 2026.
