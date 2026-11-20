"""Normalización de NIF y seudonimización de personas físicas (D-007).

Un NIF de persona jurídica se muestra tal cual. El de una persona física (DNI o NIE)
nunca se guarda: se sustituye por un seudónimo estable calculado con una sal local.
"""

import hashlib
import os
import re
import secrets
from pathlib import Path

RUTA_SAL = Path("data/.sal_seudonimos")

# Letra inicial de las personas jurídicas españolas (antiguo CIF).
_JURIDICA = re.compile(r"^[ABCDEFGHJNPQRSUVW]\d{7}[0-9A-J]$")
_FISICA = re.compile(r"^(\d{8}[A-Z]|[XYZ]\d{7}[A-Z]|[KLM]\d{7}[0-9A-Z])$")
# DNI al que la fuente quitó el cero inicial o NIE con una cifra de más. Algunos NIF-IVA
# extranjeros tienen la misma forma, pero prima la privacidad (D-007): se tratan como físicas.
_FISICA_ERRATA = re.compile(r"^(\d{7}[A-Z]|[XYZ]\d{8}[A-Z])$")
_SEPARADOR_UTE = re.compile(r"\s*[-/;,+]\s*")
_PREFIJO = re.compile(r"^(NIF|CIF|DNI|NIE)[:.\s]*")


def normalizar_nif(texto: str | None) -> str | None:
    """Mayúsculas, sin espacios, puntos ni guiones, y sin prefijos como «NIF:» o «ES»."""
    if texto is None:
        return None
    nif = _PREFIJO.sub("", texto.strip().upper())
    nif = re.sub(r"[\s.\-]", "", nif)
    if not nif:
        return None
    if nif.startswith("ES") and (_JURIDICA.match(nif[2:]) or _FISICA.match(nif[2:])):
        nif = nif[2:]
    return nif


def separar_nifs(texto: str | None) -> list[str]:
    """Devuelve los NIF de un campo. Una UTE trae varios separados por guiones o barras."""
    if texto is None or not texto.strip():
        return []
    entero = normalizar_nif(texto)
    if entero and (_JURIDICA.match(entero) or _FISICA.match(entero)):
        return [entero]
    partes = [normalizar_nif(p) for p in _SEPARADOR_UTE.split(texto.strip())]
    partes = [p for p in partes if p]
    if len(partes) > 1 and all(_JURIDICA.match(p) or _FISICA.match(p) for p in partes):
        return partes
    return [entero] if entero else []


def tipo_persona(nif: str | None) -> str:
    """Clasifica un NIF normalizado: juridica, fisica, otro (extranjero o erróneo) o desconocido."""
    if not nif:
        return "desconocido"
    if "*" in nif:
        return "fisica"  # las fuentes enmascaran con asteriscos a las personas físicas
    if _JURIDICA.match(nif):
        return "juridica"
    if _FISICA.match(nif) or _FISICA_ERRATA.match(nif):
        return "fisica"
    return "otro"


def _sal() -> bytes:
    """Sal secreta para los seudónimos: variable SEUDONIMO_SAL o un fichero local que no se sube."""
    valor = os.environ.get("SEUDONIMO_SAL")
    if valor:
        return valor.encode()
    if not RUTA_SAL.exists():
        RUTA_SAL.parent.mkdir(parents=True, exist_ok=True)
        RUTA_SAL.write_text(secrets.token_hex(32), encoding="ascii")
    return RUTA_SAL.read_text(encoding="ascii").strip().encode()


def seudonimo(nif: str, sal: bytes | None = None) -> str:
    """Identificador estable de una persona física que no permite recuperar su NIF sin la sal."""
    resumen = hashlib.sha256((sal or _sal()) + nif.encode()).hexdigest()
    return f"PF-{resumen[:16]}"


def identificar(texto_nif: str | None, nombre: str | None, sal: bytes | None = None) -> dict:
    """Convierte el NIF y el nombre de una fuente en la identidad que guardamos.

    Las personas físicas salen sin NIF ni nombre, solo con su seudónimo.
    """
    nifs = separar_nifs(texto_nif)
    nombre = nombre.strip() if nombre and nombre.strip() else None
    if not nifs:
        return {
            "adjudicatario_id": None,
            "nif": None,
            "nombre": nombre,
            "tipo_persona": "desconocido",
        }
    if len(nifs) > 1:
        miembros = [seudonimo(n, sal) if tipo_persona(n) == "fisica" else n for n in nifs]
        return {
            "adjudicatario_id": "UTE:" + "+".join(sorted(miembros)),
            "nif": None,
            "nombre": nombre,
            "tipo_persona": "ute",
        }
    nif = nifs[0]
    tipo = tipo_persona(nif)
    if tipo == "fisica":
        return {
            "adjudicatario_id": seudonimo(nif, sal),
            "nif": None,
            "nombre": None,
            "tipo_persona": tipo,
        }
    return {"adjudicatario_id": nif, "nif": nif, "nombre": nombre, "tipo_persona": tipo}
