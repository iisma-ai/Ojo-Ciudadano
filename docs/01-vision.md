# 01 · Visión: el problema que resolvemos

## Resumen

Una plataforma que **sigue el dinero público de la Comunidad de Madrid desde cada órgano hasta cada empresa o beneficiario**, calcula **indicadores de riesgo de irregularidad** y permite **investigarlo todo en lenguaje natural**.

- Es viable para DataMad 2026 si se acota a **contratos y subvenciones**: esos datos existen en formato reutilizable (CSV del Portal de la Contratación Pública con modificaciones y prórrogas, feeds diarios de PLACSP y API REST de la BDNS).
- **No prometemos detectar corrupción.** Prometemos señalar dónde hay más riesgo y menos transparencia, con cada alerta enlazada a su documento de origen, para que periodistas, auditores y ciudadanos sepan dónde mirar primero.
- Plazo: la competición **cierra el 26 de noviembre de 2026**. Equipo de **2 personas** (Ismael El Harrak El Harraq e Ignacio Vallejo Garach), 11 días de trabajo.

## Transparencia formal frente a transparencia real

Desde 2020 rige la [Ley 10/2019 de Transparencia y de Participación de la Comunidad de Madrid](https://www.boe.es/boe/dias/2019/07/09/pdfs/BOE-A-2019-10102.pdf), que obliga a publicar información sobre altos cargos, empleo público, retribuciones, contratos, convenios y subvenciones.

La Administración cumple en gran medida: el [Portal de Transparencia](https://www.comunidad.madrid/transparencia/taxonomy/term/28208) ofrece presupuestos, cuentas anuales, informes de fiscalización, subvenciones, contratos, convenios, publicidad institucional, deuda y encomiendas de gestión.

Pero **publicar no equivale a hacer comprensible**. Saber qué empresas reciben más dinero de una consejería, o si esa consejería adjudica casi siempre a los mismos, exige descargar ficheros de varios portales, unirlos a mano y dominar la jerga de la contratación pública.

## Por qué el gasto contratado

La contratación pública es el punto donde el dinero público se convierte en privado. Según la [Open Contracting Partnership](https://open-contracting.org/wp-content/uploads/2024/12/OCP2024-RedFlagProcurement-1.pdf), uno de cada tres dólares que gastan los gobiernos pasa por compras públicas (≈13 billones de dólares al año). Por eso es el ámbito con más riesgo de favoritismo, fraccionamiento o falta de competencia, y la literatura académica ya ha desarrollado indicadores objetivos para medir ese riesgo con datos públicos.

## Qué falla hoy

- **Datos dispersos.** Contratos en el Portal de la Contratación Pública, subvenciones en la BDNS, presupuestos en PDF, altos cargos en el Portal de Transparencia. Nadie los cruza.
- **Información clave en PDF.** Actas de mesas, número de ofertas y ofertas anormales están en adjuntos, no en columnas.
- **Sin visión por proveedor.** No hay una ficha con todo lo que una empresa ha recibido de la Comunidad (contratos, prórrogas, modificaciones, subvenciones).
- **Fiscalizar es caro.** [¿Quién cobra la obra?](https://www.lamarea.com/2016/11/16/quien-cobra-la-obra) de Civio necesitó meses para analizar 8.058 contratos estatales. Ese trabajo no existe a escala regional ni de forma continua.
- **Barrera de lenguaje.** Preguntar a los datos exige SQL o Excel avanzado y conocer la diferencia entre adjudicación, formalización y liquidación.

## Qué proponemos: tres piezas

1. **Modelo de datos unificado** que une contratos, subvenciones y órganos por NIF y código de órgano → flujo órgano → empresa.
2. **Indicadores de riesgo** estándar en la literatura (licitador único, procedimientos sin publicidad, fraccionamiento, concentración, sobrecostes) por contrato, órgano y empresa. Ver [04-indicadores-riesgo.md](04-indicadores-riesgo.md).
3. **Asistente en lenguaje natural** que responde preguntas como «¿qué empresas acumulan más contratos menores en Sanidad en 2025?» y **cita siempre el registro de origen**. Ver [05-asistente.md](05-asistente.md).

**Principio rector:** cada cifra enlaza al registro oficial del que sale. La plataforma no sustituye a la fuente: la hace navegable.

## A quién sirve

- **Periodistas de datos y ONG de vigilancia**: saber dónde investigar primero.
- **Órganos de control interno y Cámara de Cuentas**: priorizar auditorías por riesgo.
- **La propia Administración**: detectar patrones de baja competencia en sus licitaciones.
- **Empresas, sobre todo pymes**: entender qué mercados públicos están concentrados.
- **Ciudadanos**: saber en qué se gasta su dinero sin ser expertos.

## Encaje con DataMad 2026

[DataMad 2026](https://www.comunidad.madrid/node/120258) pide soluciones que generen valor económico, social o medioambiental con el **Catálogo de Datos Abiertos de la Comunidad**. Según las [bases difundidas](https://vivirediciones.es/?p=1130856), permite usar IA y combinar fuentes nacionales e internacionales. Nuestra propuesta: datos regionales como base, fuentes estatales para completarlos, IA para hacerlos consultables.

> **Atención:** el uso del Catálogo es requisito de las bases y aún no hemos confirmado qué datasets ofrece. Ver [09-preguntas-abiertas.md](09-preguntas-abiertas.md) (P-01).

## Qué nos diferencia

Frente a Civio o herramientas comerciales como Gobierto: **ámbito regional**, **indicadores de riesgo calculados** y **consulta en lenguaje natural con citas**.

## Posibilidades más allá del datatón

| Posibilidad | Qué añade | Esfuerzo | Horizonte |
| --- | --- | --- | --- |
| Extracción de PDFs con IA | Número de ofertas, licitadores y bajas desde actas de mesa | Medio | Parcial en el datatón, sobre una muestra |
| Otras administraciones madrileñas | Ayuntamientos y universidades ya publican en PLACSP; mismo pipeline | Bajo | Tras el datatón |
| Comparativa entre comunidades | PLACSP agrega todas las plataformas autonómicas | Medio | Tras el datatón |
| Seguimiento de fondos europeos | Enlazar actuaciones Next Generation con sus contratos | Medio | Tras el datatón |
| Exportación a OCDS | Publicar en el estándar abierto y reutilizar [Cardinal](https://www.open-contracting.org/2024/06/12/cardinal-an-open-source-library-to-calculate-public-procurement-red-flags/) | Medio | Tras el datatón |
| Alertas por suscripción | Avisos cuando un órgano o empresa supera un umbral | Bajo | Tras el datatón |
| API pública | Datos limpios e indicadores para periodistas e investigadores | Bajo | Tras el datatón |
| Cruce con Registro Mercantil | Administradores comunes, empresas recién creadas con contratos grandes | Alto | Largo plazo, depende de acceso a datos |
| Herramienta interna para la Administración | Detectar baja competencia antes de adjudicar | Medio | Largo plazo |

La Comunidad impulsa un [laboratorio de datos e IA](https://www.cio.com/article/4076934/la-comunidad-de-madrid-contara-con-un-laboratorio-de-datos-e-ia.html) y DataMad busca soluciones transferibles: una herramienta de control del gasto encaja en esa estrategia.

> Las posibilidades marcadas «tras el datatón» **no se desarrollan antes del 26 de noviembre** salvo decisión explícita en [decisions.md](decisions.md).
