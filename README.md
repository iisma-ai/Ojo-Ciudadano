<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="src/ojo_ciudadano/app/static/logo.svg">
    <img src="src/ojo_ciudadano/app/static/logo-claro.svg" width="96" alt="Logo de Ojo Ciudadano">
  </picture>
</p>

# Ojo Ciudadano

**Seguir el dinero público de la Comunidad de Madrid, de cada órgano a cada empresa.**

<p align="center">
  <a href="https://ojo-ciudadano.iismael.workers.dev/"><strong>Abrir la web: ojo-ciudadano.iismael.workers.dev</strong></a>
  ·
  <a href="https://github.com/iisma-ai/Ojo-Ciudadano/actions/workflows/tests.yml"><img src="https://github.com/iisma-ai/Ojo-Ciudadano/actions/workflows/tests.yml/badge.svg" alt="Tests"></a>
  ·
  <a href="LICENSE">Licencia MIT</a>
</p>

> Proyecto presentado a **[DataMad 2026](https://www.comunidad.madrid/node/120258)**. La web está publicada con datos reales y no hace falta instalar nada para probarla.

## En 30 segundos

La información sobre el gasto de la Comunidad de Madrid **es pública, pero está dispersa y es difícil de seguir**. Contratos, subvenciones, presupuestos y convenios están en portales distintos, con formatos distintos y sin identificadores comunes. Datos clave, como el número de ofertas de una licitación, a veces solo aparecen en PDF.

Ojo Ciudadano **une todo eso en un solo sitio** y lo explica para cualquiera:

- **1.387.606 contratos** y **872.821 concesiones de subvenciones** de 2023 a 2026, de **131 organismos**, unidos por el NIF de cada empresa.
- **Seis indicadores de riesgo** con metodología abierta, explicados como «X de cada 100 contratos donde se pudo comprobar».
- **Un asistente en lenguaje natural** que responde con la consulta que ha usado y el enlace a cada registro oficial.
- **Cada cifra enlaza a su fuente oficial.** Sin enlace al origen, la cifra no se muestra.

Las cifras de este README salen de los datos descargados entre el 16 y el 23 de noviembre de 2026 (base del 24-nov), igual que las de la web.

## Probarla en 2 minutos

1. Abre **[ojo-ciudadano.iismael.workers.dev](https://ojo-ciudadano.iismael.workers.dev/)**. En **Inicio** escribe una empresa o una consejería en el buscador y abre su ficha: verás todo lo que ha recibido, con sus señales y el enlace a cada expediente.
2. Entra en **Contratos a revisar**: los contratos con más señales, el motivo de cada una en una frase y el expediente oficial.
3. Abre el **Asistente** y pregunta, por ejemplo, «¿qué organismos adjudicaron más importe en 2025?». Debajo de la respuesta están los datos, la consulta SQL usada y los enlaces.

## Cómo responde a cada criterio

| Criterio | Qué aportamos | Detalle |
| --- | --- | --- |
| **Uso de datos abiertos de la Comunidad de Madrid** | 32 conjuntos del catálogo y del Portal de Transparencia de la Comunidad, más su Portal de Contratación y su Tribunal de Contratación, cruzados con fuentes nacionales. El asistente consulta el catálogo de la Comunidad mientras responde. | [Datos abiertos que usamos](#datos-abiertos-de-la-comunidad-de-madrid) |
| **Originalidad e innovación** | Une tres flujos de dinero por NIF, explica cada señal en una frase, tiene un asistente que enseña su consulta y cita la fuente, y añade un modelo de anomalías no supervisado. | [Qué tiene de nuevo](#qué-tiene-de-nuevo) |
| **Impacto** | Señala dónde mirar primero a periodistas, órganos de control, la propia Administración, pymes y ciudadanía. Las señales ya muestran patrones relevantes, como que 39 de cada 100 licitaciones abiertas donde se pudo comprobar recibieron una sola oferta. | [Impacto](#impacto) |
| **Viabilidad y aplicabilidad** | Ya funciona en público, con un coste casi nulo, se actualiza con comandos y se puede replicar en otras comunidades porque las fuentes principales son nacionales. | [Viabilidad](#viabilidad-y-mantenimiento) |
| **Tecnologías abiertas y reproducibilidad** | Código y documentación con licencia MIT, todo con herramientas libres, la base se regenera con comandos y hay 496 tests que se ejecutan en GitHub en cada cambio. | [Reproducibilidad](#código-abierto-y-reproducibilidad) |
| **Presentación** | Web pensada para el ciudadano, presentación en 3D en tiempo real y toda la documentación del proyecto en `docs/`. | [Presentación](#presentación) |

---

## Qué hace Ojo Ciudadano

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

## Datos abiertos de la Comunidad de Madrid

Los datos de la Comunidad son el núcleo del proyecto, no un complemento. Cada tabla guarda su `fuente`, su `url_origen` y su `fecha_descarga`, y la web enlaza cada cifra a su registro oficial.

| Fuente de la Comunidad de Madrid | Qué usamos | Dónde se ve |
| --- | --- | --- |
| [Portal de la Contratación Pública](https://contratos-publicos.comunidad.madrid/contratos) | Licitaciones, adjudicaciones sin publicidad, contratos menores y encargos a medios propios, con los importes de modificaciones, prórrogas y liquidación | Todas las pantallas de contratos y las señales de sobrecoste |
| [Catálogo de Datos Abiertos](https://datos.comunidad.madrid) (25 conjuntos) | Presupuestos iniciales y liquidados por capítulo, función, sección, centro y órgano; ingresos; sistema de financiación; ayudas de la UE; recaudación; gasto sanitario y educativo; personal; estadística de contratos | Mapa del dinero, Presupuesto y contexto, Ficha de órgano |
| Catálogo de Datos Abiertos (2 conjuntos) | [Presupuesto por clasificación orgánica](https://datos.comunidad.madrid/dataset/1902000) y [liquidado por órgano y fase](https://datos.comunidad.madrid/dataset/presupuestos_liquidados_gastos_consolidados_por_organo_y_fase_ejecucion) | Presupuesto, crédito, gasto y pagos de cada consejería, junto a lo que contrata |
| Catálogo de Datos Abiertos (4 conjuntos) | [Registro de transparencia](https://datos.comunidad.madrid/dataset/registro_transparencia), [fundaciones](https://datos.comunidad.madrid/dataset/registro_fundaciones), [cooperativas](https://datos.comunidad.madrid/dataset/registro_cooperativas) y [RPT de funcionarios](https://datos.comunidad.madrid/dataset/relacion_puestos_trabajo_funcionarios_resumida) | Ficha de empresa (se cruzan por NIF con 1.259 empresas que reciben dinero) y plantillas por organismo |
| [Portal de Transparencia: convenios](https://www.comunidad.madrid/transparencia/convenios) | 4.914 convenios vigentes: el tercer flujo de dinero, además de contratos y subvenciones | Presupuesto y contexto |
| Tribunal Administrativo de Contratación Pública | Recursos especiales y el texto de sus resoluciones | Fichas y asistente, que cita la resolución |

Para completar la información de la Comunidad cruzamos además estas fuentes nacionales: la [Plataforma de Contratación del Sector Público (PLACSP)](https://www.hacienda.gob.es/es-ES/GobiernoAbierto/Datos%20Abiertos/Paginas/LicitacionesAgregacion.aspx), que aporta el número de ofertas y los CPV; la [Base de Datos Nacional de Subvenciones (BDNS)](https://www.infosubvenciones.es); el INE, que da los habitantes para las cifras por persona; e INVENTE, el inventario de entes del sector público.

**Qué hemos aprendido de los datos.** Los portales no comparten identificadores de órgano, y el NIF es lo único que permite unirlos. Del número de ofertas, que es clave para medir la competencia, solo una parte de los contratos lo publica en datos abiertos. La exportación del Portal de Contratación tiene captcha y un límite de 50.000 filas. Lo documentamos en [`docs/02-fuentes-datos.md`](docs/02-fuentes-datos.md) por si sirve para mejorar la publicación.

**Privacidad:** no se crean fichas de personas físicas. Los autónomos y los beneficiarios particulares se seudonimizan y solo se muestran agregados.

**Reutilización:** los datos se reutilizan según las condiciones de cada fuente: se cita la fuente y la fecha y no se altera el sentido de los datos. Origen de los datos de subvenciones: Intervención General de la Administración del Estado. Ninguna administración patrocina ni apoya el proyecto. Detalle en [`docs/02-fuentes-datos.md`](docs/02-fuentes-datos.md#condiciones-de-reutilización-p-03-revisado-el-2026-11-21) y [`docs/12-datos-cm.md`](docs/12-datos-cm.md).

## Qué tiene de nuevo

- **Une tres flujos de dinero por empresa.** Contratos, subvenciones y convenios, más encargos y registros públicos, en una sola ficha por NIF. Hoy hay que buscarlos en portales distintos.
- **Señales explicadas para el ciudadano.** Cada indicador se muestra como «X de cada 100 contratos donde se pudo comprobar» y se compara con contratos parecidos, con su motivo en una frase. No es una puntuación opaca.
- **Un asistente que enseña su trabajo.** Traduce la pregunta a una consulta SQL de solo lectura y validada, la enseña, enlaza cada registro, y busca además en el catálogo de la Comunidad, en los pliegos y en las resoluciones del Tribunal.
- **Aprendizaje automático con prudencia.** Un modelo no supervisado (Isolation Forest) marca el 1 % de contratos más atípicos respecto a sus pares y explica qué cifras los alejan. Se mantiene aparte de la puntuación hasta poder validarlo.
- **El dinero se ve.** El mapa representa cada contrato como una burbuja que se llena hasta lo gastado, y la presentación se hace en 3D en tiempo real.

## Indicadores de riesgo, no acusaciones

Ojo Ciudadano **no detecta corrupción**: señala **dónde hay más riesgo y menos transparencia**, para que periodistas, auditores y ciudadanos sepan dónde mirar primero. Seguimos la [guía de *red flags* de la Open Contracting Partnership](https://open-contracting.org/redflags) y la literatura académica. Cada indicador es un fichero SQL abierto en [`sql/indicadores/`](sql/indicadores/), con su test.

| Señal | Qué mide | De cada 100 contratos donde se pudo comprobar |
| --- | --- | --- |
| Licitador único | Procedimientos abiertos o restringidos con una sola oferta | 39 |
| Sin publicidad | Negociados sin publicidad y emergencias | 31 |
| Posible fraccionamiento | Contratos menores repetidos con la misma empresa que, sumados, superan el umbral legal | 17 |
| Baja anormal o nula | Adjudicaciones muy por debajo del presupuesto, o justo en el presupuesto | 19 |
| Sobrecoste | Modificaciones que superan el 20 % del importe | 2 |
| Concentración | Una empresa que concentra casi todo el importe de un mercado de un organismo | menos de 1 |

Una señal no significa irregularidad: puede haber razones legítimas, como una urgencia, un proveedor exclusivo o un mercado pequeño. Definiciones, umbrales y limitaciones en [`docs/04-indicadores-riesgo.md`](docs/04-indicadores-riesgo.md).

## Impacto

**Social.** El dinero público se puede seguir sin conocer la jerga de la contratación ni unir ficheros a mano. Cualquiera puede ver qué recibe una empresa o cómo contrata su consejería.

**Económico.** La competencia en las licitaciones es lo que permite comparar precios. En los procedimientos abiertos donde se pudo comprobar, **39 de cada 100 recibieron una sola oferta**. Saber en qué organismos y mercados ocurre ayuda a la Administración a atraer más empresas, y a las pymes a encontrar mercados donde apenas hay competencia.

**Tecnológico.** Es un método abierto y reutilizable: esquema unificado, indicadores en SQL y asistente con citas. Otras administraciones y la propia Comunidad pueden adoptarlo o auditarlo.

**Para quién, con ejemplos:**

| Quién | Para qué le sirve |
| --- | --- |
| Periodistas de datos y ONG de vigilancia | Ver en minutos qué empresas concentran los contratos de una consejería y llegar al expediente oficial. |
| Cámara de Cuentas y órganos de control | Decidir qué revisar primero según las señales, comparando cada organismo con los demás. |
| La propia Administración | Ver sus licitaciones con una sola oferta o sus modificaciones altas, y mejorar la competencia. |
| Empresas y pymes | Descubrir qué compra cada organismo y dónde compiten pocas empresas. |
| Ciudadanía | Saber en qué se gasta su dinero y cuánto toca a cada habitante, preguntando en lenguaje natural. |

## Viabilidad y mantenimiento

- **Ya funciona.** La web pública tiene datos reales y se actualiza sola, en uno o dos minutos, con cada cambio en `main`.
- **Coste casi nulo.** Todo es software libre. La aplicación corre en un ordenador con Docker detrás de un túnel de Cloudflare, con la portada en el plan gratuito de Cloudflare. El único gasto variable es el asistente: unos céntimos por pregunta a través de OpenRouter, con topes de gasto. Detalle en [`docs/15-despliegue.md`](docs/15-despliegue.md).
- **Actualización.** Se vuelven a ejecutar los comandos de [Empezar](#empezar). Las descargas se trocean por meses y quedan en caché, para no cargar los portales.
- **Se puede replicar.** PLACSP y BDNS son nacionales y el esquema no depende de Madrid, así que llevarlo a otra comunidad es sobre todo adaptar la fuente regional.
- **Siguientes pasos.** Registro Mercantil, publicación en el estándar abierto OCDS, una API pública y seguir el dinero de cada partida del presupuesto hasta sus contratos. Quedaron fuera a propósito para entregar a tiempo algo sólido ([`docs/08-plan.md`](docs/08-plan.md)).

## Código abierto y reproducibilidad

- **Licencia MIT** para el código y la documentación ([LICENSE](LICENSE)).
- **Solo tecnologías abiertas:** Python, [uv](https://docs.astral.sh/uv/), polars, DuckDB, Streamlit, Plotly, Three.js y scikit-learn. El asistente usa un modelo de lenguaje por OpenRouter, sin depender de ningún proveedor: el adaptador es HTTP simple y se puede cambiar de modelo.
- **Reproducible por código.** Cada descarga, limpieza, indicador y modelo es un comando. El entorno está fijado en `uv.lock`.
- **Probado.** Hay 496 tests con datos sintéticos, que no necesitan descargar nada, y [se ejecutan en GitHub](https://github.com/iisma-ai/Ojo-Ciudadano/actions/workflows/tests.yml) en cada cambio.
- **Documentado.** Cada decisión está razonada en [`docs/decisions.md`](docs/decisions.md) y cada sesión de trabajo en [`docs/bitacora/`](docs/bitacora/). El índice está en [`docs/README.md`](docs/README.md).

### Empezar

Para probarla no hace falta instalar nada: abre [ojo-ciudadano.iismael.workers.dev](https://ojo-ciudadano.iismael.workers.dev/). Para ejecutarla en tu ordenador:

```bash
# Requisito: uv (https://docs.astral.sh/uv/getting-started/installation/)
git clone https://github.com/iisma-ai/Ojo-Ciudadano.git
cd Ojo-Ciudadano
uv sync            # crea el entorno e instala dependencias
uv run pytest      # comprueba que todo funciona
```

Los datos no están en el repositorio: se regeneran en `data/`.

```bash
# 1. Datos brutos en data/raw/. El Portal de Contratación de la Comunidad exporta a CSV con captcha:
#    se descarga a mano desde https://contratos-publicos.comunidad.madrid/contratos (filtros y pasos
#    exactos en docs/02-fuentes-datos.md, F-01). El Atom de PLACSP se descarga por meses y las
#    subvenciones por la API de la BDNS:
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

## Presentación

La presentación es una página en 3D en tiempo real (Three.js), en [`presentacion/`](presentacion/): un viaje bajo el mar en el que el ojo de cristal ilumina el dinero disperso entre portales. Para verla, ejecuta `uv run python -m http.server 8600` desde la raíz y abre `http://127.0.0.1:8600/presentacion/index.html` en Chrome. Guion en [`presentacion/README.md`](presentacion/README.md).

## Cómo colaborar

Antes de escribir código, lee:

1. [`CLAUDE.md`](CLAUDE.md): reglas del proyecto (válidas para personas y agentes de IA).
2. [`docs/08-plan.md`](docs/08-plan.md): el plan y quién hace qué.
3. [`docs/decisions.md`](docs/decisions.md): lo que ya está decidido.

## Licencia

El código y la documentación se publican con licencia [MIT](LICENSE). Los datos no forman parte del repositorio: pertenecen a sus fuentes oficiales y se reutilizan según las condiciones de cada una (ver «Datos abiertos de la Comunidad de Madrid»).

## Equipo

Dos personas, para DataMad 2026:

- **Ignacio Vallejo Garach**: subvenciones, indicadores de concentración y bajas, puntuación, interfaz y asistente.
- **Ismael El Harrak El Harraq**: ingesta de contratos, motor de indicadores, detección de anomalías, despliegue y presentación.
