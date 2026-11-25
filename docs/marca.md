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
| Ámbar | `#E0A032` y `#FFD27A` (tono «ambar» de la presentación) | En los gráficos, **solo lo atípico** (D-055): la burbuja del contrato atípico y su línea. Fuera de los gráficos, la animación del asistente |

**Gráficos (D-055): solo azules y grises azulados; el ámbar, solo para lo atípico.** Para distinguir entidades (organismos, empresas) se usa la paleta categórica de `app/graficos.py` (`CATEGORICOS`), en orden fijo y alternando claros y oscuros: `#3D8BFD`, `#9CC7FF`, `#1E5BB8`, `#38BDF8`, `#6F86A6`, `#2B6CB0`, `#B4C3D6`; del 8.º en adelante, gris `#4A5872`. Las señales en los gráficos van en celeste `#38BDF8`; las líneas de referencia (límites, umbrales), en gris claro punteado.

Tipografía: **Outfit** (Google Fonts, la de Clubed) para todo el texto y **JetBrains Mono** para el código y los nombres de tablas (D-061). Las dos se cargan desde `.streamlit/config.toml`; el buscador, que va en un iframe, la carga aparte.

## Estética «océano» (D-034)

Fondo de mar con luz que baja y burbujas que suben; paneles, botones y campos de cristal esmerilado con un brillo arriba; títulos finos con degradado blanco a azul claro; en los mapas de nodos, burbujas de cristal sobrias y sin recuadro. Las separaciones de los gráficos son líneas claras casi transparentes: **nunca bordes negros**. Misma estética que la presentación (`presentacion/`).

## Reglas

- **Prohibido usar emojis o emoticonos** en cualquier sitio: interfaz, código, documentación, commits, README y presentación. Un test (`tests/test_sin_emojis.py`) falla si aparece alguno en el repositorio.
- Los iconos de la interfaz son **iconos de verdad**: los de [Material Symbols](https://fonts.google.com/icons) que trae Streamlit (`icon=":material/info:"`) o SVG propios en `app/static/`.
- Poco texto en pantalla: una línea bajo cada título; las explicaciones largas van en desplegables («Cómo se calcula», «Cómo leer…») y la metodología, las fuentes y el aviso legal en la barra lateral.
