"""Nombres oficiales de los códigos CPV (Vocabulario Común de Contratos Públicos, Reglamento (CE)
213/2008), en español.

Fuente: la lista de códigos CODICE que publica la Dirección General del Patrimonio del Estado
para la Plataforma de Contratación del Sector Público (`CPV2008-2.04.gc`, formato genericode).
Es la misma lista con la que PLACSP clasifica sus licitaciones, así que casan todos los códigos
de nuestra base (1.963 de 1.963 el 23-nov-2026). La de TED pide pasar una comprobación de robots.

Sirve para que cada CPV se lea con su nombre («33100000 · Equipamientos médicos») en la web y
en el asistente. Es un diccionario: no es una señal ni cambia ningún indicador.

Uso (desde la carpeta del repositorio, con la base ya construida y la web parada):
    uv run python -m ojo_ciudadano.ingesta.cpv          # baja la lista y la carga en la base

El portal a veces rechaza la petición con una página «Request Rejected» de su cortafuegos y
código 200. Esa página no se guarda en la caché: se avisa y se puede repetir más tarde o
copiar `data/raw/cpv/CPV2008-2.04.gc` de quien ya lo tenga (es un fichero público).
"""

import sys
from datetime import date
from pathlib import Path

import duckdb
import httpx
import polars as pl
from lxml import etree

FUENTE = "placsp"
URL = "https://contrataciondelestado.es/codice/cl/2.04/CPV2008-2.04.gc"
CARPETA = Path("data/raw/cpv")
FICHERO = CARPETA / "CPV2008-2.04.gc"
RUTA_DB = Path("data/ojo_ciudadano.duckdb")
RUTA_DDL = (
    Path(__file__).resolve().parents[3] / "sql/esquema/008_cpv.sql"
)  # vale desde cualquier carpeta


class ListaNoValida(RuntimeError):
    """Lo descargado (o lo que hay en la caché) no es la lista de códigos CPV."""


def es_lista(contenido: bytes) -> bool:
    """¿Es la lista genericode de CPV (y no una página de error)? Se mira el principio."""
    inicio = contenido[:4000].lstrip()
    return inicio.startswith(b"<?xml") and b"CodeList" in contenido[:20000]


def descargar(destino: Path = FICHERO) -> Path:
    """Baja la lista si no está en la caché. Una caché que no es la lista (una página de error
    guardada por versiones anteriores) se descarta y se vuelve a bajar."""
    if destino.exists() and destino.stat().st_size > 0:
        if es_lista(destino.read_bytes()):
            return destino
        destino.unlink()
    destino.parent.mkdir(parents=True, exist_ok=True)
    r = httpx.get(URL, timeout=120, follow_redirects=True)
    r.raise_for_status()
    if not es_lista(r.content):
        rechazo = b"Request Rejected" in r.content
        raise ListaNoValida(
            (
                "El portal de la Plataforma de Contratación ha rechazado la descarga (página "
                "«Request Rejected» de su cortafuegos)"
                if rechazo
                else "La respuesta del portal no es la lista de códigos CPV"
            )
            + f". No se ha guardado nada. Prueba más tarde o copia {destino.as_posix()} de "
            "alguien del equipo que ya lo tenga (es un fichero público) y vuelve a lanzar esto."
        )
    destino.write_bytes(r.content)
    return destino


def leer(ruta: Path = FICHERO, fecha_descarga: date | None = None) -> pl.DataFrame:
    """Una fila por código: `codigo` (8 cifras), `nombre` en español, `division` (2 cifras) y
    el nombre de su división, con la fuente y la fecha de descarga."""
    raiz = etree.parse(str(ruta)).getroot()
    filas = []
    for fila in raiz.iter("Row"):
        valores = {
            v.get("ColumnRef"): (v.findtext("SimpleValue") or "").strip()
            for v in fila.iter("Value")
        }
        if valores.get("code"):
            filas.append({"codigo": valores["code"], "nombre": valores.get("nombre") or None})
    tabla = pl.DataFrame(filas, schema={"codigo": pl.String, "nombre": pl.String})
    tabla = tabla.with_columns(
        pl.col("nombre").str.strip_chars_end(".").alias("nombre"),
        pl.col("codigo").str.slice(0, 2).alias("division"),
    )
    divisiones = tabla.filter(pl.col("codigo").str.ends_with("000000")).select(
        "division", pl.col("nombre").alias("nombre_division")
    )
    fecha = fecha_descarga or date.fromtimestamp(ruta.stat().st_mtime)
    return (
        tabla.join(divisiones, on="division", how="left")
        .with_columns(
            pl.lit(FUENTE).alias("fuente"),
            pl.lit(URL).alias("url_origen"),
            pl.lit(fecha).alias("fecha_descarga"),
        )
        .unique("codigo", keep="first")
        .sort("codigo")
    )


def cargar(ruta_db: Path = RUTA_DB, ruta: Path = FICHERO) -> int:
    """Crea o rehace la tabla `cpv` en una base ya construida, sin regenerar lo demás."""
    if not ruta_db.exists():
        raise FileNotFoundError(
            f"No existe la base {ruta_db.as_posix()}: constrúyela antes con el pipeline "
            "(modelo.carga) y lanza esto desde la carpeta del repositorio."
        )
    if not es_lista(ruta.read_bytes()):
        raise ListaNoValida(f"{ruta.as_posix()} no es la lista de códigos CPV: bórralo y repite.")
    tabla = leer(ruta)  # noqa: F841 (DuckDB la lee por su nombre)
    try:
        con = duckdb.connect(str(ruta_db))
    except duckdb.IOException as error:
        raise RuntimeError(
            f"La base {ruta_db.as_posix()} está abierta en otro programa (normalmente la web): "
            "para la web y vuelve a lanzar esto."
        ) from error
    with con:
        con.execute("DROP TABLE IF EXISTS cpv")
        con.execute(RUTA_DDL.read_text(encoding="utf-8"))
        con.execute("INSERT INTO cpv BY NAME SELECT * FROM tabla")
        return con.execute("SELECT count(*) FROM cpv").fetchall()[0][0]


if __name__ == "__main__":
    ruta_db = Path(sys.argv[1]) if len(sys.argv) > 1 else RUTA_DB
    try:
        descargar()
        print(f"cpv: {cargar(ruta_db)} códigos cargados en {ruta_db}")
    except (ListaNoValida, FileNotFoundError, RuntimeError, httpx.HTTPError) as error:
        sys.exit(f"cpv: {error}")
