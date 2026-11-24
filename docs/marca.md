# Identidad visual

Logo, paleta y reglas de estilo de Ojo Ciudadano (D-022). El tema de la interfaz está en `.streamlit/config.toml` y los ajustes finos, en `src/ojo_ciudadano/app/static/estilo.css`.

## Logo

Un ojo abierto y trazado a mano alzada, con la pupila en azul. Es vectorial (SVG), con trazo de grosor uniforme y extremos redondeados.

| Fichero | Uso |
| --- | --- |
| [`logo.svg`](../src/ojo_ciudadano/app/static/logo.svg) | Símbolo sobre fondo oscuro (icono de la pestaña, barra lateral contraída) |
| [`logo-horizontal.svg`](../src/ojo_ciudadano/app/static/logo-horizontal.svg) | Símbolo y nombre sobre fondo oscuro (barra lateral, README, presentación) |
| [`logo-claro.svg`](../src/ojo_ciudadano/app/static/logo-claro.svg) | Símbolo sobre fondo claro (documentos impresos) |

No se deforma, no se rota y no se cambian sus colores fuera de esta paleta.

## Paleta

| Nombre | Color | Uso |
| --- | --- | --- |
| Fondo | `#041627` | Fondo de la aplicación (mar profundo; en pantalla, degradado de `#0A3A55` arriba a `#020C17` abajo, D-034) |
| Superficie | `#0B2236` (y cristal: blanco al 3-10 %) | Tarjetas, desplegables, métricas |
| Barra lateral | `#06202F` (cristal) | Fondo de la navegación |
| Borde | `#1E3A52` (en el cristal, `rgba(170,225,255,.16)`) | Bordes y separadores |
| Texto | `#E7ECF3` | Texto principal y trazo del logo |
| Texto secundario | `#93A1B8` | Notas, fuentes, fechas |
| Azul (acento) | `#3D8BFD` | Color principal: botones, selección, pupila del logo |
| Azul claro | `#7DB3FF` | Enlaces |
| Azul de señal | `#7DB3FF` (etiquetas: cristal `rgba(125,179,255,.13)` con borde `rgba(125,179,255,.35)`) | Señales en las tarjetas de contrato, sus subcajas y la cuadrícula del Inicio (D-042, sustituye al ámbar); nunca rojo «de peligro» (lenguaje no acusatorio, D-002) |
| Ámbar | `#F2B544` | Solo líneas de referencia de los gráficos (límites y umbrales) y la animación del asistente |

Para distinguir entidades en un gráfico (p. ej. organismos en el mapa del dinero) se usa la paleta categórica de `app/graficos.py` (`CATEGORICOS`), en orden fijo y validada sobre el fondo oscuro: `#3987E5`, `#D95926`, `#199E70`, `#C98500`, `#D55181`, `#0CA30C`, `#9085E9`; del 8.º en adelante, gris.

Tipografía: **Inter** (Google Fonts) para todo el texto y una monoespaciada para el SQL.

## Estética «océano» (D-034)

Fondo de mar con luz que baja y burbujas que suben; paneles, botones y campos de cristal esmerilado con un brillo arriba; títulos finos con degradado blanco a azul claro; en los mapas de nodos, burbujas de cristal sobrias y sin recuadro. Las separaciones de los gráficos son líneas claras casi transparentes: **nunca bordes negros**. Misma estética que la presentación (`presentacion/`).

## Reglas

- **Prohibido usar emojis o emoticonos** en cualquier sitio: interfaz, código, documentación, commits, README y presentación. Un test (`tests/test_sin_emojis.py`) falla si aparece alguno en el repositorio.
- Los iconos de la interfaz son **iconos de verdad**: los de [Material Symbols](https://fonts.google.com/icons) que trae Streamlit (`icon=":material/info:"`) o SVG propios en `app/static/`.
- Poco texto en pantalla: una línea bajo cada título; las explicaciones largas van en desplegables («Cómo se calcula», «Cómo leer…») y la metodología, las fuentes y el aviso legal en la barra lateral.
