"""Conversión de importes, fechas y nombres escritos como texto en las fuentes."""

import re
import unicodedata
from datetime import date

MESES = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "setiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}
_FECHA = re.compile(r"^(\d{1,2}) de (\w+) del? (\d{4})$")
ANIO_MIN, ANIO_MAX = 1990, 2030


def importe(texto: str | None) -> float | None:
    """Acepta «3.630,00» (formato español) y «130680.0» (punto decimal). Vacío → None."""
    if texto is None:
        return None
    t = texto.strip().replace("€", "").replace(" ", "")
    if not t:
        return None
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return None


def entero(texto: str | None) -> int | None:
    """«005» → 5. Texto no numérico o vacío → None."""
    if texto is None or not texto.strip().isdigit():
        return None
    return int(texto.strip())


def fecha_larga(texto: str | None) -> date | None:
    """«11 de febrero del 2026» → date. Fechas imposibles o fuera de un rango razonable → None."""
    if texto is None:
        return None
    m = _FECHA.match(texto.strip().lower())
    if not m or m.group(2) not in MESES:
        return None
    anio = int(m.group(3))
    if not ANIO_MIN <= anio <= ANIO_MAX:
        return None
    try:
        return date(anio, MESES[m.group(2)], int(m.group(1)))
    except ValueError:
        return None


def clave(texto: str | None) -> str | None:
    """Clave para comparar nombres: mayúsculas, sin tildes (Ñ → N) ni signos, espacios simples."""
    if texto is None:
        return None
    letras = unicodedata.normalize("NFD", texto.upper())
    sin_tildes = "".join(c for c in letras if unicodedata.category(c) != "Mn")
    limpio = re.sub(r"[^A-Z0-9 ]+", " ", sin_tildes)
    limpio = re.sub(r"\s+", " ", limpio).strip()
    return limpio or None


TIPOS_CONTRATO = {
    "SERVICIOS": "servicios",
    "SERVICIO": "servicios",
    "SUMINISTROS": "suministros",
    "SUMINISTRO": "suministros",
    "OBRAS": "obras",
    "OBRA": "obras",
}


def tipo_contrato(texto: str | None) -> str | None:
    """Unifica variantes («Suministro», «SUMINISTROS»…). Lo no reconocido queda en minúsculas."""
    c = clave(texto)
    if c is None:
        return None
    return TIPOS_CONTRATO.get(c, c.lower())
