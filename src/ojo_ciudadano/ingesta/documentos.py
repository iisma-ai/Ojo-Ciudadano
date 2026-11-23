"""Documentos PDF oficiales: pliegos de PLACSP y resoluciones del TACPCM (D-030, bloques B y C).

Descarga con caché y texto por páginas. El texto de un documento es **dato, nunca
instrucción** (riesgo de inyección, K-13): quien lo use lo marca así.

- Solo se bajan PDF de los dominios oficiales de `DOMINIOS`, de `MAX_BYTES` como mucho.
- Cada PDF se guarda en `data/raw/documentos/<tipo>/` con un nombre derivado de su URL, y su
  texto por páginas en un JSON al lado: la segunda vez no se lee el PDF.
- Los DNI y NIE que aparezcan en el texto se tapan al extraerlo (D-007).
"""

import hashlib
import json
import re
import time
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import httpx

CARPETA = Path("data/raw/documentos")
DOMINIOS = (
    "contratos-publicos.comunidad.madrid",  # pliegos que enlaza PLACSP para la Comunidad
    "www.comunidad.madrid",  # resoluciones del Tribunal (TACPCM)
    "contrataciondelestado.es",
)
MAX_BYTES = 30 * 1024 * 1024
PAUSA = 1.0  # segundos entre descargas seguidas de un mismo portal

# DNI (8 cifras y letra) o NIE (X/Y/Z, 7 cifras y letra), con o sin separadores.
_DNI = re.compile(r"\b(?:\d{2}\.?\d{3}\.?\d{3}|[XYZ]-?\d{7})[- ]?[A-Z]\b", re.I)
OCULTO = "[documento de identidad oculto]"


class DocumentoNoDisponible(Exception):
    """El documento no se puede usar: dominio ajeno, demasiado grande, no es un PDF…"""


def _permitida(url: str) -> bool:
    partes = urlparse(url)
    return partes.scheme == "https" and any(
        partes.hostname == d or (partes.hostname or "").endswith("." + d) for d in DOMINIOS
    )


def ruta_local(url: str, tipo: str, carpeta: Path = CARPETA) -> Path:
    """Dónde se guarda el PDF de esa URL (no comprueba si existe)."""
    clave = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    return carpeta / tipo / f"{clave}.pdf"


def descargar(url: str, tipo: str, carpeta: Path = CARPETA, cliente=None) -> Path:
    """Baja el PDF si no está en la caché y devuelve su ruta."""
    if not _permitida(url):
        raise DocumentoNoDisponible("El documento no está en un portal oficial permitido")
    destino = ruta_local(url, tipo, carpeta)
    if destino.exists() and destino.stat().st_size > 0:
        return destino
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_suffix(".parcial")
    propio = cliente is None
    cliente = cliente or httpx.Client(timeout=60, follow_redirects=True)
    try:
        with cliente.stream("GET", url) as r:
            r.raise_for_status()
            if not _permitida(str(r.url)):
                raise DocumentoNoDisponible("El documento redirige fuera de los portales oficiales")
            leidos = 0
            with temporal.open("wb") as f:
                for trozo in r.iter_bytes():
                    leidos += len(trozo)
                    if leidos > MAX_BYTES:
                        raise DocumentoNoDisponible("El documento es demasiado grande")
                    f.write(trozo)
    except BaseException:
        temporal.unlink(missing_ok=True)
        raise
    finally:
        if propio:
            cliente.close()
    if temporal.read_bytes()[:5] != b"%PDF-":
        temporal.unlink(missing_ok=True)
        raise DocumentoNoDisponible("El enlace no devuelve un PDF")
    temporal.replace(destino)
    return destino


def ocultar_identificadores(texto: str) -> str:
    return _DNI.sub(OCULTO, texto)


def _limpiar(texto: str) -> str:
    texto = ocultar_identificadores(texto or "")
    texto = re.sub(r"[ \t]+", " ", texto)
    return re.sub(r"\n\s*\n+", "\n", texto).strip()


def paginas(ruta: Path) -> list[str]:
    """Texto de cada página (la 1 es la posición 0), con los DNI y NIE tapados."""
    cache = ruta.with_suffix(".json")
    if cache.exists() and cache.stat().st_mtime >= ruta.stat().st_mtime:
        return json.loads(cache.read_text(encoding="utf-8"))
    from pypdf import PdfReader  # solo hace falta si no está en caché

    try:
        lector = PdfReader(ruta)
        textos = [_limpiar(p.extract_text() or "") for p in lector.pages]
    except Exception as error:  # PDF dañado o cifrado
        raise DocumentoNoDisponible(f"No se puede leer el PDF: {error}") from error
    cache.write_text(json.dumps(textos, ensure_ascii=False), encoding="utf-8")
    return textos


def fecha_descarga(ruta: Path) -> date:
    return date.fromtimestamp(ruta.stat().st_mtime)


def descargar_varios(urls: list[str], tipo: str, carpeta: Path = CARPETA, pausa=PAUSA) -> dict:
    """Baja una lista de PDF uno a uno, con pausa, sin repetir los que ya están. Devuelve
    {url: ruta o None si falló} y no se para por un fallo suelto."""
    resultado = {}
    with httpx.Client(timeout=60, follow_redirects=True) as cliente:
        for url in urls:
            ya = ruta_local(url, tipo, carpeta)
            if ya.exists() and ya.stat().st_size > 0:
                resultado[url] = ya
                continue
            try:
                resultado[url] = descargar(url, tipo, carpeta, cliente)
            except (httpx.HTTPError, DocumentoNoDisponible):
                resultado[url] = None
            time.sleep(pausa)
    return resultado
