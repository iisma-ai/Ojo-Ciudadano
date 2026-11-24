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
    elegida = st_searchbox(
        _empresas,
        label=etiqueta,
        placeholder="Escribe el nombre o el NIF y elige de la lista",
        key=clave,
        default_options=_empresas(""),
        debounce=PAUSA_MS,
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
    return st_searchbox(
        _organos,
        label=etiqueta,
        placeholder="Escribe el nombre y elige de la lista",
        key=clave,
        default_options=_organos(""),
        debounce=PAUSA_MS,
    )


def esperar(elegido: str | None, mensaje: str) -> None:
    """Si todavía no se ha elegido nada, muestra el mensaje y detiene la pantalla."""
    if elegido is None:
        st.info(mensaje)
        st.stop()


def _todo(texto: str) -> list[tuple[str, str]]:
    """Organismos y empresas a la vez (primero los organismos, que son pocos)."""
    organos = [
        (f"Organismo · {o['nombre']}", f"organo:{o['organo_id']}")
        for o in datos.sugerir_organos(conexion(), texto, limite=5)
    ]
    empresas = [
        (f"Empresa · {e['nombre']} · {e['nif'] or 'UTE'}", f"empresa:{e['adjudicatario_id']}")
        for e in datos.sugerir_empresas(conexion(), texto, limite=10)
    ]
    return organos + empresas


def todo(clave: str, etiqueta: str = "") -> tuple[str, str] | None:
    """Buscador único de la portada: devuelve («empresa» u «organo», id) al elegir."""
    elegido = st_searchbox(
        _todo,
        label=etiqueta,
        placeholder="Busca una empresa, un hospital o una consejería",
        key=clave,
        debounce=PAUSA_MS,
    )
    if not elegido:
        return None
    tipo, _, ident = elegido.partition(":")
    return tipo, ident
