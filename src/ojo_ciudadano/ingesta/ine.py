"""Población residente en la Comunidad de Madrid, del INE (D-038).

Solo sirve para dar escala en el mapa general: el presupuesto de cada año dividido entre los
habitantes («si se repartiera entre todos, a cada uno le tocarían unos X €»). No entra en la
base ni en ningún indicador.

Fuente: Estadística Continua de Población del INE, tabla 56940 («Población residente por
fecha, sexo y edad»), serie ECP115490 (Comunidad de Madrid, total, todas las edades). Se usa
la población a 1 de enero de cada año. Licencia: reutilización libre citando al INE.

Uso:
    uv run python -m ojo_ciudadano.ingesta.ine     # descarga (o refresca) la serie
"""

import json
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx

MADRID = ZoneInfo("Europe/Madrid")
CARPETA = Path("data/raw/ine")
SERIE = "ECP115490"
URL_API = f"https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/{SERIE}?nult=60"
URL_ORIGEN = "https://www.ine.es/jaxiT3/Tabla.htm?t=56940"
FUENTE = "ine_ecp"


def _fichero(carpeta: Path) -> Path:
    return carpeta / f"poblacion_{SERIE}.json"


def descargar(carpeta: Path = CARPETA) -> Path:
    """Baja la serie del INE (una sola petición) y la guarda en la caché."""
    respuesta = httpx.get(URL_API, timeout=30)
    respuesta.raise_for_status()
    carpeta.mkdir(parents=True, exist_ok=True)
    destino = _fichero(carpeta)
    destino.write_text(respuesta.text, encoding="utf-8")
    return destino


def leer_serie(texto: str) -> dict[int, int]:
    """Población a 1 de enero de cada año, a partir del JSON de la API del INE."""
    datos = json.loads(texto)
    poblacion: dict[int, int] = {}
    for punto in datos.get("Data", []):
        # El INE fecha a medianoche hora de Madrid (en UTC, el 1 de enero cae el 31 de diciembre).
        dia = datetime.fromtimestamp(punto["Fecha"] / 1000, tz=MADRID).date()
        if dia.month == 1 and dia.day == 1 and punto.get("Valor") is not None:
            poblacion[dia.year] = int(punto["Valor"])
    return poblacion


def poblacion(carpeta: Path = CARPETA, descargar_si_falta: bool = True) -> dict | None:
    """Serie de población y su procedencia, o None si no se puede obtener.

    Devuelve `{"por_anio": {2025: 7113886, ...}, "fuente", "url_origen", "fecha_descarga"}`.
    """
    fichero = _fichero(carpeta)
    if not fichero.exists():
        if not descargar_si_falta:
            return None
        try:
            descargar(carpeta)
        except httpx.HTTPError:
            return None
    por_anio = leer_serie(fichero.read_text(encoding="utf-8"))
    if not por_anio:
        return None
    return {
        "por_anio": por_anio,
        "fuente": FUENTE,
        "url_origen": URL_ORIGEN,
        "fecha_descarga": date.fromtimestamp(fichero.stat().st_mtime),
    }


def del_anio(serie: dict, anio: int) -> tuple[int, int] | None:
    """(año de referencia, habitantes) para un año: el 1 de enero de ese año o, si aún no está
    publicado, el último disponible anterior."""
    anios = [a for a in serie["por_anio"] if a <= anio]
    if not anios:
        return None
    referencia = max(anios)
    return referencia, serie["por_anio"][referencia]


if __name__ == "__main__":
    ruta = descargar()
    serie = poblacion()
    print(f"Guardado en {ruta}: {serie['por_anio'] if serie else 'sin datos'}")
