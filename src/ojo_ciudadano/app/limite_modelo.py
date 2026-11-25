"""Límite de consultas al modelo de lenguaje por persona (D-057).

Cada persona puede hacer 2 preguntas seguidas al modelo; después espera 5 minutos desde la
última, sin excepciones. Las respuestas preparadas no cuentan: no llaman al modelo ni gastan.

Quién es «cada persona»: la IP real del visitante (la cabecera `CF-Connecting-IP`, que pone
Cloudflare y el visitante no puede falsear) junto con su navegador (`User-Agent`). Así, recargar
la página no reinicia el contador, y dos personas en la misma wifi con dispositivos distintos no
se bloquean entre sí. No se guarda ninguna IP: solo un resumen (hash) en la memoria del servidor,
que se pierde al reiniciarlo.
"""

import hashlib
import threading
import time
from collections.abc import Callable

import streamlit as st

CONSULTAS_SEGUIDAS = 2
ESPERA_SEGUNDOS = 5 * 60


class Limitador:
    """Cuenta las consultas de cada persona. Seguro con varias sesiones a la vez."""

    def __init__(
        self,
        maximo: int = CONSULTAS_SEGUIDAS,
        espera: float = ESPERA_SEGUNDOS,
        reloj: Callable[[], float] = time.monotonic,
    ) -> None:
        self.maximo = maximo
        self.espera = espera
        self._reloj = reloj
        self._cerrojo = threading.Lock()
        self._usos: dict[str, list[float]] = {}

    def _vigentes(self, quien: str, ahora: float) -> list[float]:
        usos = self._usos.get(quien, [])
        # Pasada la espera desde la última consulta, el contador vuelve a cero.
        if usos and ahora - usos[-1] >= self.espera:
            usos = []
        self._usos[quien] = usos
        return usos

    def intentar(self, quien: str) -> float:
        """Si la persona puede consultar, apunta la consulta y devuelve 0. Si no, devuelve los
        segundos que le quedan de espera (y no apunta nada)."""
        with self._cerrojo:
            ahora = self._reloj()
            usos = self._vigentes(quien, ahora)
            if len(usos) >= self.maximo:
                return usos[-1] + self.espera - ahora
            usos.append(ahora)
            return 0.0

    def restante(self, quien: str) -> float:
        """Segundos de espera que le quedan, sin apuntar nada (0 si puede preguntar)."""
        with self._cerrojo:
            ahora = self._reloj()
            usos = self._vigentes(quien, ahora)
            return usos[-1] + self.espera - ahora if len(usos) >= self.maximo else 0.0


@st.cache_resource
def limitador() -> Limitador:
    """Uno para todo el servidor: lo comparten todas las sesiones."""
    return Limitador()


def _cabecera(nombre: str) -> str:
    cabeceras = st.context.headers
    return cabeceras.get(nombre) or cabeceras.get(nombre.lower()) or ""


def identidad() -> str:
    """Resumen de la IP real y del navegador del visitante. Nunca se guarda la IP. Si no se
    puede leer (no debería pasar), el límite se aplica a la sesión: el asistente no se rompe."""
    try:
        ip = (
            _cabecera("CF-Connecting-IP")
            or _cabecera("X-Forwarded-For").split(",")[0].strip()
            or (st.context.ip_address or "")
        )
        navegador = _cabecera("User-Agent")
    except Exception:
        ip, navegador = "", ""
    if not ip:
        ip = "sesion:" + st.session_state.setdefault(
            "_oc_id_limite", hashlib.sha256(str(time.time_ns()).encode()).hexdigest()
        )
    return hashlib.sha256(f"{ip}|{navegador}".encode()).hexdigest()[:20]


def tiempo(segundos: float) -> str:
    """«4 min 10 s», «35 s»."""
    s = max(1, int(round(segundos)))
    minutos, s = divmod(s, 60)
    return f"{minutos} min {s} s" if minutos else f"{s} s"


def mensaje(segundos: float) -> str:
    return (
        f"Has hecho {CONSULTAS_SEGUIDAS} preguntas seguidas al modelo de lenguaje. Para repartir "
        f"su uso entre todas las personas, podrás volver a preguntarle dentro de "
        f"**{tiempo(segundos)}**. Mientras tanto, las preguntas con respuesta preparada (las de "
        "la lista de arriba) siguen funcionando sin espera."
    )
