"""Buscadores con autocompletado: al escribir, sugieren las empresas u órganos que existen.

Usan `streamlit-searchbox`: cada letra que se escribe lanza la consulta de `app.datos` y muestra
la lista de sugerencias (primero las que empiezan por lo escrito). Sin personas físicas (D-007).
"""

import streamlit as st
from streamlit_searchbox import st_searchbox

from ojo_ciudadano.app import datos, textos
from ojo_ciudadano.app.conexion import conexion

PAUSA_MS = 120  # espera tras la última letra antes de consultar


def _empresas(texto: str) -> list[tuple[str, str]]:
    return [
        (f"{e['nombre']} · {e['nif'] or 'UTE'}", e["adjudicatario_id"])
        for e in datos.sugerir_empresas(conexion(), texto)
    ]


def _organos(texto: str) -> list[tuple[str, str]]:
    return [
        (f"{o['nombre']} · {textos.numero(o['n_contratos'])} contratos", o["organo_id"])
        for o in datos.sugerir_organos(conexion(), texto)
    ]


def empresa(clave: str, etiqueta: str = "Empresa", valor: str = "adjudicatario_id") -> str | None:
    """Autocompletado de empresas. Devuelve el `adjudicatario_id` (o su NIF o nombre si
    `valor` es «nif» o «nombre»); None mientras no se elija ninguna."""
    _transparente(key=f"oc_transparente_{clave}")
    elegida = st_searchbox(
        _empresas,
        label=etiqueta,
        placeholder="Escribe el nombre o el NIF y elige de la lista",
        key=clave,
        default_options=_empresas(""),
        debounce=PAUSA_MS,
        style_overrides=ESTILO_BARRA,
    )
    if elegida is None or valor == "adjudicatario_id":
        return elegida
    cursor = (
        conexion()
        .execute("SELECT nif, nombre FROM adjudicatario WHERE adjudicatario_id = ?", [elegida])
        .fetchone()
    )
    if cursor is None:
        return None
    return cursor[0] if valor == "nif" and cursor[0] else cursor[1]


def organo(clave: str, etiqueta: str = "Organismo") -> str | None:
    """Autocompletado de órganos. Devuelve el `organo_id`; None mientras no se elija ninguno."""
    _transparente(key=f"oc_transparente_{clave}")
    return st_searchbox(
        _organos,
        label=etiqueta,
        placeholder="Escribe el nombre y elige de la lista",
        key=clave,
        default_options=_organos(""),
        debounce=PAUSA_MS,
        style_overrides=ESTILO_BARRA,
    )


def esperar(elegido: str | None, mensaje: str) -> None:
    """Si todavía no se ha elegido nada, muestra el mensaje y detiene la pantalla."""
    if elegido is None:
        st.info(mensaje)
        st.stop()


def _todo(texto: str) -> list[tuple[str, str]]:
    """Organismos y empresas a la vez (primero los organismos, que son pocos). Sin texto, una
    muestra variada para empezar: consejerías, hospitales y las empresas con más contratos (si no,
    solo saldrían hospitales, que son los que más contratan)."""
    if not texto.strip():
        return _sugerencias_iniciales()
    organos = [
        (f"Organismo · {o['nombre']}", f"organo:{o['organo_id']}")
        for o in datos.sugerir_organos(conexion(), texto, limite=5)
    ]
    empresas = [
        (f"Empresa · {e['nombre']} · {e['nif'] or 'UTE'}", f"empresa:{e['adjudicatario_id']}")
        for e in datos.sugerir_empresas(conexion(), texto, limite=10)
    ]
    return organos + empresas


def _sugerencias_iniciales() -> list[tuple[str, str]]:
    """Lo que sale al pulsar el buscador sin haber escrito nada."""
    con = conexion()
    opciones = []
    for prefijo in ("Consejería", "Hospital"):
        opciones += [
            (f"Organismo · {o['nombre']}", f"organo:{o['organo_id']}")
            for o in datos.sugerir_organos(con, prefijo, limite=4)
            if o["nombre"].startswith(prefijo)
        ]
    opciones += [
        (f"Empresa · {e['nombre']} · {e['nif'] or 'UTE'}", f"empresa:{e['adjudicatario_id']}")
        for e in datos.sugerir_empresas(con, "", limite=6)
    ]
    return opciones


# Barra de búsqueda de la portada con la estética de la web: cápsula de cristal con una lupa a la
# izquierda y sin la flecha de desplegable (si no, parece un selector y no un buscador). El
# componente va en un iframe: el estilo se le pasa con `style_overrides` (estilos de react-select).
LUPA = (
    "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' "
    "viewBox='0 0 24 24' fill='none' stroke='%237DB3FF' stroke-width='2.2' "
    "stroke-linecap='round'%3E%3Ccircle cx='11' cy='11' r='7'/%3E%3Cpath d='m20 20-4.2-4.2'/%3E"
    '%3C/svg%3E")'
)
ESTILO_BARRA = {
    "dropdown": {"width": 0, "height": 0, "fill": "transparent"},
    "clear": {"icon": "cross", "clearable": "always", "stroke": "#9FB6CC", "width": 18},
    "searchbox": {
        "control": {
            "minHeight": "58px",
            "borderRadius": "999px",
            "paddingLeft": "48px",
            "paddingRight": "10px",
            "backgroundColor": "rgba(12, 44, 70, 0.78)",
            "backgroundImage": LUPA,
            "backgroundRepeat": "no-repeat",
            "backgroundPosition": "20px center",
            "border": "1px solid rgba(170, 225, 255, 0.28)",
            "boxShadow": "inset 0 1px 0 rgba(255,255,255,0.14), 0 8px 28px rgba(0,8,22,0.35)",
            "cursor": "text",
            "fontSize": "1.05rem",
        },
        "placeholder": {"color": "#8FA7BF"},
        "input": {"color": "#E7ECF3"},
        "singleValue": {"color": "#E7ECF3"},
        "menuList": {"backgroundColor": "#0B2236", "borderRadius": "16px"},
        "option": {
            "color": "#E7ECF3",
            "backgroundColor": "#0B2236",
            "highlightColor": "rgba(61, 139, 253, 0.35)",
        },
        "optionEmpty": "hidden",
    },
}


# El iframe del buscador pinta su fondo con el color del tema: un rectángulo oscuro alrededor de
# la cápsula. Este componente (sin iframe, corre en la página) le quita ese fondo; el iframe es del
# mismo origen. Se repite al cambiar la página, porque Streamlit vuelve a crear el iframe.
JS_TRANSPARENTE = """
export default function () {
  if (globalThis.__ocBuscador) return;
  globalThis.__ocBuscador = true;
  const limpiar = () => {
    for (const f of document.querySelectorAll('iframe[title="streamlit_searchbox.searchbox"]')) {
      f.style.colorScheme = 'normal';
      try {
        const d = f.contentDocument;
        if (d && d.body && !d.getElementById('oc-transparente')) {
          const s = d.createElement('style');
          s.id = 'oc-transparente';
          s.textContent = 'html, body { background: transparent !important; }' +
            '[class*="-menu"] { background: #0B2236 !important; border-radius: 16px !important;' +
            ' overflow: hidden; border: 1px solid rgba(170,225,255,.18);' +
            ' box-shadow: 0 12px 30px rgba(0,8,22,.5) !important; }' +
            '[class*="-option"] { font-size: 0.98rem; padding: 10px 18px !important; }';
          d.head.appendChild(s);
        }
      } catch (e) { /* otro origen: se queda como está */ }
    }
  };
  limpiar();
  new MutationObserver(limpiar).observe(document.body, { childList: true, subtree: true });
  setInterval(limpiar, 1500);
}
"""
_transparente = st.components.v2.component("oc_buscador_transparente", js=JS_TRANSPARENTE)


def todo(clave: str, etiqueta: str = "") -> tuple[str, str] | None:
    """Buscador único de la portada: devuelve («empresa» u «organo», id) al elegir."""
    _transparente(key=f"oc_transparente_{clave}")
    elegido = st_searchbox(
        _todo,
        label=etiqueta,
        placeholder="Busca una empresa, un hospital o una consejería",
        key=clave,
        # al pulsarlo sin escribir nada ya salen opciones para empezar
        default_options=_sugerencias_iniciales(),
        debounce=PAUSA_MS,
        style_overrides=ESTILO_BARRA,
        # la lista de sugerencias sale por encima de la página, sin empujar lo de debajo
        style_absolute=True,
    )
    if not elegido:
        return None
    tipo, _, ident = elegido.partition(":")
    return tipo, ident
