"""Entes del sector público institucional (INVENTE, Intervención General de la Administración del
Estado): estatal, autonómico y local, con su NIF y su forma jurídica.

Sirve para reconocer qué adjudicatarios son entes públicos (universidades, fundaciones del sector
público, sociedades mercantiles públicas, organismos autónomos…) y no empresas privadas (D-035).
Es contexto: no es una señal ni cambia ningún indicador.

Fuente: la API pública de INVENTE (`/Invente2/api/EntidadesSPI_ConFiltros` sin filtros devuelve
el inventario de entes vivos, unos 4.800, en una sola petición; documentada en el fichero YAML
de la aplicación INVENTE). Acceso libre, sin alta. Condiciones: aviso legal del Ministerio de
Hacienda (citar la fuente). No contiene datos de personas.

Uso:
    uv run python -m ojo_ciudadano.ingesta.invente      # baja el inventario y lo carga en la base
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

import duckdb
import httpx
import polars as pl

from ojo_ciudadano.normalizacion import texto as n_texto

FUENTE = "invente"
URL = "https://www.pap.hacienda.gob.es/Invente2/api/EntidadesSPI_ConFiltros"
URL_CONSULTA = "https://www.pap.hacienda.gob.es/invente2/pagMenuPrincipalV2.aspx"
CARPETA = Path("data/raw/invente")
FICHERO = CARPETA / "entidades_spi.json"
RUTA_DB = Path("data/ojo_ciudadano.duckdb")
RUTA_DDL = Path("sql/esquema/009_sector_publico.sql")

# Palabras que no distinguen a una entidad de otra al comparar nombres.
_GENERICAS = set(
    [
        "S",
        "A",
        "L",
        "U",
        "SA",
        "SL",
        "SAU",
        "SLU",
        "MP",
        "SME",
        "DE",
        "DEL",
        "LA",
        "LAS",
        "LOS",
        "EL",
        "Y",
        "E",
        "EN",
        "PARA",
        "M",
        "P",
        "O",
        "A",
        "FUNDACION",
        "SOCIEDAD",
        "EMPRESA",
        "MUNICIPAL",
        "PUBLICA",
        "PUBLICO",
        "MADRID",
        "COMUNIDAD",
    ]
)


def descargar(destino: Path = FICHERO) -> Path:
    """Baja el inventario completo (una petición) si no está en la caché."""
    if destino.exists() and destino.stat().st_size > 0:
        return destino
    destino.parent.mkdir(parents=True, exist_ok=True)
    r = httpx.get(URL, headers={"Accept": "application/json"}, timeout=300)
    r.raise_for_status()
    datos = r.json()
    if not datos.get("EntidadesSPI"):
        raise ValueError("INVENTE no ha devuelto entidades")
    destino.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
    return destino


def leer(ruta: Path = FICHERO, fecha_descarga: date | None = None) -> pl.DataFrame:
    """Una fila por ente con NIF: código INVENTE, nombre, NIF normalizado, forma jurídica,
    código DIR3 y la administración de la que depende, con fuente y fecha de descarga."""
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    filas = [
        {
            "codigo_invente": e.get("CodigoInvente"),
            "nombre": (e.get("DenominacionSocial") or "").strip() or None,
            "nif": re.sub(r"[^0-9A-Z]", "", (e.get("NIF") or "").upper()) or None,
            "forma_juridica": e.get("FormaJuridica_Descripcion"),
            "codigo_dir3": e.get("codigoDir3") or None,
            "codigo_origen": e.get("codigoOrigen") or None,
        }
        for e in datos.get("EntidadesSPI", [])
    ]
    fecha = fecha_descarga or date.fromtimestamp(ruta.stat().st_mtime)
    return (
        pl.DataFrame(filas)
        .filter(pl.col("nif").is_not_null())
        .unique("nif", keep="first", maintain_order=True)
        .with_columns(
            pl.col("codigo_origen")
            .map_elements(administracion, return_dtype=pl.String)
            .alias("administracion"),
            pl.lit(FUENTE).alias("fuente"),
            pl.lit(URL_CONSULTA).alias("url_origen"),
            pl.lit(fecha).alias("fecha_descarga"),
        )
        .sort("nif")
    )


def administracion(codigo_origen: str | None) -> str | None:
    """De qué administración depende, por el código de origen del inventario. Empieza por las
    dos cifras de la comunidad (Madrid es «12»): «12000…» son entes de la propia Comunidad
    («1200000BP017» Planifica Madrid, «1200048HH000» su Fundación Orquesta y Coro) y «12» más
    un código de municipio, entes locales («1228079AP001» EMT de Madrid). Los que empiezan por
    letras (OE, NF, SE…) son del sector público estatal."""
    if not codigo_origen:
        return None
    if not codigo_origen[:2].isdigit():
        return "Estado"
    autonomico = codigo_origen[2:5] == "000"
    if codigo_origen[:2] == "12":
        return "Comunidad de Madrid" if autonomico else "Entidad local de Madrid"
    return "Otra comunidad autónoma" if autonomico else "Entidad local de otra comunidad"


def nombres_compatibles(a: str | None, b: str | None) -> bool:
    """Si dos nombres comparten alguna palabra que distinga a la entidad. Un NIF que casa con un
    nombre muy distinto suele ser un error de la fuente (un NIF de otra entidad)."""
    if not a or not b:
        return False
    palabras = [set((n_texto.clave(x) or "").split()) - _GENERICAS for x in (a, b)]
    return bool(palabras[0] & palabras[1])


def cargar(ruta_db: Path = RUTA_DB, ruta: Path = FICHERO) -> int:
    """Crea o rehace la tabla `entidad_sector_publico` en una base ya construida."""
    tabla = leer(ruta)  # noqa: F841 (DuckDB la lee por su nombre)
    with duckdb.connect(str(ruta_db)) as con:
        con.execute("DROP TABLE IF EXISTS entidad_sector_publico")
        con.execute(RUTA_DDL.read_text(encoding="utf-8"))
        con.execute("INSERT INTO entidad_sector_publico BY NAME SELECT * FROM tabla")
        return con.execute("SELECT count(*) FROM entidad_sector_publico").fetchall()[0][0]


if __name__ == "__main__":
    ruta_db = Path(sys.argv[1]) if len(sys.argv) > 1 else RUTA_DB
    descargar()
    print(f"entidad_sector_publico: {cargar(ruta_db)} entes cargados en {ruta_db}")
