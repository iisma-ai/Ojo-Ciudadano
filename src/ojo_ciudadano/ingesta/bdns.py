"""Ingesta de las concesiones de subvenciones de la Comunidad de Madrid desde la BDNS (F-03).

La API pública del Sistema Nacional de Publicidad de Subvenciones (sin clave) se consulta por
meses, una petición cada vez y con pausa, para no abusar del servicio (lo pide su aviso
legal). Cada mes se guarda en `data/raw/bdns/AAAA-MM.json` y no se vuelve a descargar salvo
que se fuerce.

Personas físicas (D-007): la BDNS enmascara su NIF («***4209**») pero publica el nombre. El
nombre no se guarda nunca y el beneficiario se identifica con un seudónimo del `idPersona`
interno de la BDNS.

Uso: uv run python -m ojo_ciudadano.ingesta.bdns [AAAA ...]
"""

import json
import sys
import time
from datetime import date
from pathlib import Path

import httpx
import polars as pl

from ojo_ciudadano.normalizacion import nif as n_nif
from ojo_ciudadano.normalizacion import texto as n_texto

FUENTE = "bdns"
API = "https://www.infosubvenciones.es/bdnstrans/api"
URL_CONVOCATORIA = "https://www.infosubvenciones.es/bdnstrans/GE/es/convocatorias/"
CARPETA = Path("data/raw/bdns")
ID_COMUNIDAD = 16  # «COMUNIDAD DE MADRID» entre las administraciones autonómicas
NIVEL2 = "COMUNIDAD DE MADRID"
TAMANO_PAGINA = 10_000
PAUSA_SEGUNDOS = 1.0
ANIOS = (2023, 2024, 2025, 2026)


def organos_comunidad(cliente: httpx.Client) -> list[int]:
    """Identificadores BDNS de los órganos de la Comunidad. La BDNS asigna las concesiones
    antiguas al nombre actual del órgano, así que basta con la lista vigente."""
    respuesta = cliente.get(f"{API}/organos", params={"vpd": "GE", "idAdmon": "A"})
    respuesta.raise_for_status()
    comunidad = next(o for o in respuesta.json() if o["id"] == ID_COMUNIDAD)
    return [hijo["id"] for hijo in comunidad["children"]]


def descargar_mes(
    cliente: httpx.Client, organos: list[int], anio: int, mes: int, carpeta: Path = CARPETA
) -> Path:
    """Descarga todas las concesiones de un mes (paginando) y las guarda en un JSON."""
    inicio = date(anio, mes, 1)
    fin = date(anio + (mes == 12), mes % 12 + 1, 1)
    filas, pagina = [], 0
    while True:
        respuesta = cliente.get(
            f"{API}/concesiones/busqueda",
            params={
                "vpd": "GE",
                "page": pagina,
                "pageSize": TAMANO_PAGINA,
                "organos": ",".join(map(str, organos)),
                "fechaDesde": inicio.strftime("%d/%m/%Y"),
                "fechaHasta": date.fromordinal(fin.toordinal() - 1).strftime("%d/%m/%Y"),
            },
        )
        respuesta.raise_for_status()
        datos = respuesta.json()
        filas.extend(datos["content"])
        time.sleep(PAUSA_SEGUNDOS)
        if datos["last"]:
            break
        pagina += 1
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{anio}-{mes:02d}.json"
    ruta.write_text(json.dumps(filas, ensure_ascii=False), encoding="utf-8")
    return ruta


def descargar(anios=ANIOS, carpeta: Path = CARPETA, forzar: bool = False) -> list[Path]:
    """Descarga los meses que falten (o todos si `forzar`). Nunca meses futuros."""
    hoy = date.today()
    rutas = []
    with httpx.Client(timeout=120, headers={"User-Agent": "ojo-ciudadano/0.1"}) as cliente:
        organos = organos_comunidad(cliente)
        for anio in anios:
            for mes in range(1, 13):
                if (anio, mes) > (hoy.year, hoy.month):
                    break
                ruta = carpeta / f"{anio}-{mes:02d}.json"
                if forzar or not ruta.exists():
                    ruta = descargar_mes(cliente, organos, anio, mes, carpeta)
                    print(f"{ruta.name}: {len(json.loads(ruta.read_text('utf-8')))} concesiones")
                rutas.append(ruta)
    return rutas


def separar_beneficiario(texto: str | None) -> tuple[str | None, str | None]:
    """«B12345678 EMPRESA SL» → («B12345678», «EMPRESA SL»). El NIF es la primera palabra."""
    if not texto or not texto.strip():
        return None, None
    primera, _, resto = texto.strip().partition(" ")
    if any(ch.isdigit() for ch in primera) or "*" in primera:
        return primera, resto.strip() or None
    return None, texto.strip()


def identificar_beneficiario(texto: str | None, id_persona, sal: bytes | None = None) -> dict:
    """Identidad que guardamos. Si el NIF está enmascarado o solo hay un nombre, se trata como
    persona física: sin NIF ni nombre, con el seudónimo de su idPersona (D-007)."""
    nif_texto, nombre = separar_beneficiario(texto)
    identidad = n_nif.identificar(nif_texto, nombre, sal)
    if identidad["tipo_persona"] != "fisica" and nif_texto is not None:
        return identidad
    seudonimo = n_nif.seudonimo(f"BDNS:{id_persona}", sal) if id_persona is not None else None
    return {"adjudicatario_id": seudonimo, "nif": None, "nombre": None, "tipo_persona": "fisica"}


def leer(rutas: list[Path], fecha_descarga: date, sal: bytes | None = None) -> dict:
    """Lee los JSON mensuales y devuelve las tablas `concesiones`, `beneficiarios` y `organos`."""
    filas = [f for ruta in rutas for f in json.loads(Path(ruta).read_text("utf-8"))]
    filas = [f for f in filas if (f.get("nivel2") or "").upper() == NIVEL2]
    vistos, concesiones, identidades = set(), [], {}
    for f in filas:
        concesion_id = f"{FUENTE}:{f['codConcesion']}"
        if concesion_id in vistos:
            continue
        vistos.add(concesion_id)
        clave = (f.get("beneficiario"), f.get("idPersona"))
        if clave not in identidades:
            identidades[clave] = identificar_beneficiario(*clave, sal)
        numero = f.get("numeroConvocatoria")
        concesiones.append(
            {
                "concesion_id": concesion_id,
                "fuente": FUENTE,
                "organo_nombre": (f.get("nivel3") or "").strip() or None,
                "beneficiario_id": identidades[clave]["adjudicatario_id"],
                "id_convocatoria": f.get("idConvocatoria"),
                "numero_convocatoria": numero,
                "convocatoria": f.get("convocatoria"),
                "instrumento": (f.get("instrumento") or "").strip() or None,
                "fecha_concesion": date.fromisoformat(f["fechaConcesion"])
                if f.get("fechaConcesion")
                else None,
                "importe": f.get("importe"),
                "ayuda_equivalente": f.get("ayudaEquivalente"),
                "url_bases": f.get("urlBR"),
                "url_origen": URL_CONVOCATORIA + numero if numero else URL_CONVOCATORIA,
                "fecha_descarga": fecha_descarga,
            }
        )
    esquema = {
        "concesion_id": pl.String,
        "fuente": pl.String,
        "organo_nombre": pl.String,
        "beneficiario_id": pl.String,
        "id_convocatoria": pl.Int64,
        "numero_convocatoria": pl.String,
        "convocatoria": pl.String,
        "instrumento": pl.String,
        "fecha_concesion": pl.Date,
        "importe": pl.Float64,
        "ayuda_equivalente": pl.Float64,
        "url_bases": pl.String,
        "url_origen": pl.String,
        "fecha_descarga": pl.Date,
    }
    tabla = pl.DataFrame(concesiones, schema=esquema)
    nombres = tabla["organo_nombre"].drop_nulls().unique().to_list()
    organos = pl.DataFrame(
        {
            "organo_id": [n_texto.clave(n) for n in nombres],
            "nombre": [n.capitalize() if n.isupper() else n for n in nombres],
        },
        schema={"organo_id": pl.String, "nombre": pl.String},
    ).unique("organo_id")
    claves = pl.DataFrame(
        {"organo_nombre": nombres, "organo_id": [n_texto.clave(n) for n in nombres]},
        schema={"organo_nombre": pl.String, "organo_id": pl.String},
    )
    tabla = tabla.join(claves, on="organo_nombre", how="left").drop("organo_nombre")
    beneficiarios = pl.DataFrame(
        list(identidades.values()),
        schema=dict.fromkeys(("adjudicatario_id", "nif", "nombre", "tipo_persona"), pl.String),
    ).filter(pl.col("adjudicatario_id").is_not_null())
    return {
        "concesiones": tabla,
        "beneficiarios": beneficiarios.unique("adjudicatario_id"),
        "organos": organos,
    }


if __name__ == "__main__":
    anios = tuple(int(a) for a in sys.argv[1:]) or ANIOS
    print(f"{len(descargar(anios))} meses en {CARPETA}")
