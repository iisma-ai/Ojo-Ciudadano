# 02 · Fuentes de datos

El núcleo son los **contratos de la Comunidad de Madrid**; subvenciones, presupuesto y altos cargos los completan. Todas las fuentes son públicas y reutilizables.

## Inventario

| ID | Fuente | Qué contiene | Formato y acceso | Papel | Limitaciones |
| --- | --- | --- | --- | --- | --- |
| F-01 | [Portal de la Contratación Pública de la Comunidad de Madrid](https://www.comunidad.madrid/press-releases/download/77053) | Licitaciones, adjudicaciones, contratos menores, modificaciones y prórrogas de todos los órganos regionales | Búsqueda filtrable exportable a CSV (con importes de modificaciones y prórrogas); RSS | **Fuente principal** | Número de ofertas y actas a menudo solo en PDF adjunto |
| F-02 | [Plataforma de Contratación del Sector Público (PLACSP)](https://www.hacienda.gob.es/es-ES/GobiernoAbierto/Datos%20Abiertos/Paginas/LicitacionesAgregacion.aspx) | Las mismas licitaciones regionales, consolidadas con el resto de España | Feeds Atom diarios y zip mensuales; datos desde 2012 | Campos más estructurados (licitadores, CPV, procedimiento) y validación cruzada | XML anidado; una licitación aparece una vez por cada cambio → hay que deduplicar |
| F-03 | [Base de Datos Nacional de Subvenciones (BDNS)](https://www.pap.hacienda.gob.es/sitios/pap/es-ES/Documents/Notainformativa-PremioASEDIEalSNPSAP.pdf) | Convocatorias y concesiones de todas las administraciones | API REST en JSON; también CSV y XLSX | Segundo flujo de dinero: órgano → beneficiario | Personas físicas protegidas; descargas grandes hay que trocearlas |
| F-04 | [Portal de Transparencia](https://www.comunidad.madrid/transparencia/taxonomy/term/8522) | Altos cargos (retribuciones, bienes), personal eventual, RPT, convenios, publicidad institucional | Fichas web y ficheros descargables | Contexto organizativo y gasto en publicidad | Formatos heterogéneos; poca serie histórica estructurada |
| F-05 | [Presupuestos Generales](https://comunidad.madrid/sites/default/files/gobierno_abierto/2024-presupuesto-libro-08-ejecucion-liquidacion.pdf) | Crédito y ejecución por sección, centro, programa y capítulo | Libros en PDF; posibles ficheros en el catálogo | Escala: qué parte del presupuesto de cada órgano pasa por contratos | Sin enlace directo partida → contrato |
| F-06 | Catálogo de Datos Abiertos de la Comunidad de Madrid | **Base obligatoria del concurso** | CKAN | Requisito de DataMad | **Pendiente** de revisar qué datasets de contratos y presupuesto ofrece |

Otras referencias útiles:
- [Guía de publicación en el perfil de contratante e interconexión con PLACSP](https://gestiona3.madrid.org/bvirtual/BVCM015814.pdf): explica cómo el portal regional vuelca en PLACSP (clave para deduplicar F-01/F-02).

## Ventana temporal

El MVP se acota a **2023–2026** (ver D-006 en [decisions.md](decisions.md)). Los huecos de cobertura se documentan en la propia plataforma.

## Qué dejamos fuera a propósito

- **Retribuciones individuales de funcionarios.** Solo datos por puesto (RPT) y altos cargos, que ya son públicos por ley. Analizar personas concretas choca con el RGPD y aporta poco.
- **Registro Mercantil (BORME).** Cruzar administradores con cargos públicos sería potente, pero no hay API oficial abierta y limpia. Línea futura.
- **Trazabilidad partida → contrato.** Los datos no la permiten: mostramos ambos niveles por separado y lo decimos explícitamente.

## Problemas de calidad conocidos (a resolver en la normalización)

| Problema | Tratamiento previsto |
| --- | --- |
| NIF mal escritos, nombres con variantes | Normalizar NIF (mayúsculas, sin espacios ni guiones, validar dígito de control); tabla de alias de nombres |
| UTE como entidades separadas | Modelar la UTE y sus empresas miembro |
| Duplicados entre portal regional y PLACSP | Deduplicar por **expediente + órgano** |
| Varias versiones de una licitación en el Atom de PLACSP | Quedarse con la **última versión** |
| Cambios de estructura entre años | Mapeo de columnas por año, documentado |
| Límites de descarga (BDNS, portales que bloquean automatización) | Descargas por meses, caché local, descarga manual si hace falta |

## Reglas para trabajar con datos

1. **Los datos nunca se suben al repositorio** (`data/` está en `.gitignore`). Se regeneran con el pipeline.
2. Cada descarga registra **fuente, URL, fecha y hora** de descarga.
3. Se respetan las condiciones de reutilización: citar fuente y fecha, no alterar el sentido de los datos. Revisar licencias el día 1 (P-03).
4. Cuando se explore o incorpore una fuente, se documenta aquí: campos reales, cobertura, sorpresas. Usa la skill `/nueva-fuente`.

## Pregunta crítica

> Confirmar en el catálogo qué datasets de contratos y presupuesto existen y **si el CSV del Portal de Contratación incluye el número de licitadores**. De eso dependen la mitad de los indicadores. → P-01 y P-02 en [09-preguntas-abiertas.md](09-preguntas-abiertas.md).
