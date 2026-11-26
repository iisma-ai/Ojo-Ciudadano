<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="src/ojo_ciudadano/app/static/logo.svg">
    <img src="src/ojo_ciudadano/app/static/logo-claro.svg" width="96" alt="Logo de Ojo Ciudadano">
  </picture>
</p>

# Ojo Ciudadano

**Seguir el dinero público de la Comunidad de Madrid, de cada órgano a cada empresa.**

<h2 align="center"><a href="https://ojo-ciudadano.iismael.workers.dev/">Abrir la página web aquí</a></h2>
<p align="center">
  <a href="https://ojo-ciudadano.iismael.workers.dev/">https://ojo-ciudadano.iismael.workers.dev/</a>
</p>
<p align="center">
  <a href="https://github.com/iisma-ai/Ojo-Ciudadano/actions/workflows/tests.yml"><img src="https://github.com/iisma-ai/Ojo-Ciudadano/actions/workflows/tests.yml/badge.svg" alt="Tests"></a>
  ·
  <a href="LICENSE">Licencia MIT</a>
</p>

La información sobre el gasto de la Comunidad de Madrid **es pública, pero está dispersa y es difícil de seguir**. Contratos, subvenciones, presupuestos y convenios están en portales distintos, con formatos distintos y sin identificadores comunes. Datos clave, como el número de ofertas de una licitación, a veces solo aparecen en PDF.

## Qué hace Ojo Ciudadano

| Pantalla | Qué hace |
| --- | --- |
| **Mapa del dinero** | Muestra de dónde viene el dinero de la Comunidad y a qué consejerías y contratos va. |
| **Contratos a revisar** | Lista los contratos con más señales de riesgo y explica cada una en una frase. |
| **Contratos atípicos** | Señala los contratos que más se alejan de otros parecidos, con un modelo de aprendizaje automático. |
| **Red del dinero** | Dibuja qué empresas y beneficiarios reciben más de cada organismo. |
| **Ficha de empresa** | Reúne todo lo que ha recibido una empresa: contratos, subvenciones y encargos. |
| **Ficha de órgano** | Enseña cómo contrata cada organismo frente a los demás y con qué presupuesto. |
| **Presupuesto y contexto** | Recoge el presupuesto, los convenios y las plantillas de la Comunidad. |
| **Asistente de IA** | Responde preguntas en lenguaje natural con los datos, la consulta usada y el enlace oficial. |

## Datos abiertos de la Comunidad de Madrid

Cada tabla guarda su `fuente`, su `url_origen` y su `fecha_descarga`, y la web enlaza cada cifra a su registro oficial. Las fuentes utilizadas han sido las siguientes:

| Fuente de la Comunidad de Madrid | Qué usamos | Dónde se ve |
| --- | --- | --- |
| [Portal de la Contratación Pública](https://contratos-publicos.comunidad.madrid/contratos) | Licitaciones, adjudicaciones sin publicidad, contratos menores y encargos a medios propios, con los importes de modificaciones, prórrogas y liquidación | Todas las pantallas de contratos y las señales de sobrecoste |
| [Catálogo de Datos Abiertos](https://datos.comunidad.madrid) (25 conjuntos) | Presupuestos iniciales y liquidados por capítulo, función, sección, centro y órgano; ingresos; sistema de financiación; ayudas de la UE; recaudación; gasto sanitario y educativo; personal; estadística de contratos | Mapa del dinero, Presupuesto y contexto, Ficha de órgano |
| Catálogo de Datos Abiertos (2 conjuntos) | [Presupuesto por clasificación orgánica](https://datos.comunidad.madrid/dataset/1902000) y [liquidado por órgano y fase](https://datos.comunidad.madrid/dataset/presupuestos_liquidados_gastos_consolidados_por_organo_y_fase_ejecucion) | Presupuesto, crédito, gasto y pagos de cada consejería, junto a lo que contrata |
| Catálogo de Datos Abiertos (4 conjuntos) | [Registro de transparencia](https://datos.comunidad.madrid/dataset/registro_transparencia), [fundaciones](https://datos.comunidad.madrid/dataset/registro_fundaciones), [cooperativas](https://datos.comunidad.madrid/dataset/registro_cooperativas) y [RPT de funcionarios](https://datos.comunidad.madrid/dataset/relacion_puestos_trabajo_funcionarios_resumida) | Ficha de empresa (se cruzan por NIF con 1.259 empresas que reciben dinero) y plantillas por organismo |
| [Portal de Transparencia: convenios](https://www.comunidad.madrid/transparencia/convenios) | 4.914 convenios vigentes: el tercer flujo de dinero, además de contratos y subvenciones | Presupuesto y contexto |
| Tribunal Administrativo de Contratación Pública | Recursos especiales y el texto de sus resoluciones | Fichas y asistente, que cita la resolución |

Para completar la información de la Comunidad cruzamos además estas fuentes nacionales: la [Plataforma de Contratación del Sector Público (PLACSP)](https://www.hacienda.gob.es/es-ES/GobiernoAbierto/Datos%20Abiertos/Paginas/LicitacionesAgregacion.aspx), que aporta el número de ofertas y los CPV; la [Base de Datos Nacional de Subvenciones (BDNS)](https://www.infosubvenciones.es); el INE, que da los habitantes para las cifras por persona; e INVENTE, el inventario de entes del sector público.

**Calidad, privacidad y reutilización.** Los portales no comparten identificadores de órgano, y el NIF es lo único que permite unirlos; lo documentamos en [`docs/02-fuentes-datos.md`](docs/02-fuentes-datos.md). No hay fichas de personas físicas: se seudonimizan y solo se muestran agregadas. Cada dato se reutiliza según las condiciones de su fuente, con cita y fecha. Los datos de subvenciones proceden de la Intervención General de la Administración del Estado, y ninguna administración patrocina el proyecto.

## Qué tiene de nuevo (innovación)

Hasta ahora, para saber cuánto dinero público recibe una empresa había que buscar en varios portales, descargar ficheros y cruzarlos a mano. Con Ojo Ciudadano basta con escribir su nombre: aparecen juntos sus contratos, sus subvenciones y sus convenios. Además, la plataforma avisa de lo que conviene mirar con más atención, como un contrato al que solo se presentó una empresa, y lo explica con palabras sencillas. Son indicadores de riesgo, no acusaciones. También se le puede preguntar a un asistente de IA como se le preguntaría a una persona («¿qué organismo gastó más en 2025?»), y responde con los datos y el enlace al documento oficial para comprobarlo.

## Impacto

**Social.** No saber a dónde va nuestro dinero siempre ha sido un problema: esa incertidumbre genera desconfianza en las instituciones. Ojo Ciudadano quiere aportar transparencia y, con ella, confianza: cualquiera puede ver qué recibe una empresa o cómo contrata su consejería, con el enlace al documento oficial.

**Económico.** La competencia en las licitaciones es lo que permite comparar precios. En los procedimientos abiertos donde se pudo comprobar, **39 de cada 100 recibieron una sola oferta**. Saber en qué organismos y mercados ocurre ayuda a la Administración a atraer más empresas, y a las pymes a encontrar mercados donde apenas hay competencia.

**Tecnológico.** Es un método abierto y reutilizable: esquema unificado, indicadores en SQL y asistente con citas. Otras administraciones y la propia Comunidad pueden adoptarlo o auditarlo.

## Viabilidad y mantenimiento

Ya funciona en público con datos reales y se actualiza sola con cada cambio. Todo es software libre y el coste es casi nulo: un ordenador con Docker, el plan gratuito de Cloudflare y unos céntimos por pregunta al asistente. Como PLACSP y BDNS son nacionales, llevarlo a otra comunidad es sobre todo adaptar la fuente regional. Detalle en [`docs/15-despliegue.md`](docs/15-despliegue.md).

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
