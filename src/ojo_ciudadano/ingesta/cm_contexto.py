"""Lee los ficheros de `data/raw/cm_abiertos/` y devuelve las tablas del contexto de la Comunidad
de Madrid (sql/esquema/003_contexto_cm.sql). Sin acceso a la red: solo lee lo ya descargado.

Privacidad (D-007): los registros solo guardan NIF de persona jurídica y los convenios solo
muestran firmantes con forma de entidad; los demás firmantes se cuentan pero no se guardan.
"""

import csv
import re
from datetime import date
from pathlib import Path

import polars as pl

from ojo_ciudadano.ingesta.cm_abiertos import (
    CARPETA,
    PAGINA_CONVENIOS,
    SERIES,
    SERIES_ORGANO,
    leer_manifiesto,
)
from ojo_ciudadano.normalizacion import nif as n_nif
from ojo_ciudadano.normalizacion import texto as n_texto

FUENTE_CKAN = "ckan_cm"
FUENTE_TRANSPARENCIA = "transparencia_cm"
FACTOR_EUROS = {"miles euros": 1_000.0, "millones euros": 1_000_000.0, "euros": 1.0}
DIMENSIONES = ("Fase", "Capítulo", "Recaudación")
FASES = {
    "crédito actual": "Crédito actual",
    "obligaciones reconocidas": "Obligaciones reconocidas",
    "pagos realizados": "Pagos realizados",
    "saldo pendiente de pago": "Saldo pendiente de pago",
}
_ENTIDAD_LIQUIDADO = re.compile(
    r"^Gastos consolidados del?(?: la| el| los| las)? (.+?) en fase de ([a-záéíóú ]+?) de los",
    re.IGNORECASE,
)
_ENTIDAD_INICIAL = re.compile(
    r"^Total gastos consolidados del?(?: la| el| los| las)? (.+?) de los presupuestos",
    re.IGNORECASE,
)
# Firmantes de convenios que parecen una entidad (y no una persona).
_PATRON_ENTIDAD = re.compile(
    n_nif.PATRON_EMPRESA[:-1]
    + r"|\bAYUNTAMIENTO|\bCONSEJER|\bMINISTERIO|\bCOLEGIO|\bFEDERACI|\bCONSORCIO|\bAGENCIA|"
    r"\bCRUZ ROJA|\bC[AÁ]MARA|\bJUNTA\b|\bDIPUTACI|\bCOMUNIDAD|\bMANCOMUNIDAD|\bORGANIZACI|"
    r"\bCONFEDERACI|\bSINDICATO|\bUNI[OÓ]N|\bHOSPITAL|\bCENTRO|\bEMPRESA|\bCOOPERATIVA|"
    r"\bESCUELA|\bCLUB\b|\bREAL\b|\bACADEMIA|\bCOFRAD|\bPARROQUIA|\bARZOBISPADO|\bOBISPADO|"
    r"\bCONGREGACI|\bIGLESIA|\bEDITORIAL|\bFUNDACI|\bCOMISI|\bPATRONATO|\bINSTITUCI|"
    r"\bAYTO|\bGOBIERNO|\bSERVICIO|\bMUSEO|\bTEATRO|\bORQUESTA|\bPOLICIA|\bGUARDIA CIVIL|"
    r"\bEJERCITO|\bMETRO\b|\bCANAL\b|\bBANCO|\bCAJA|\bSOCIEDAD|\bS\.?L\.?\b|\bS\.?A\.?\b)",
    re.IGNORECASE,
)


def _numero(texto: str | None) -> float | None:
    """Valores del catálogo: «153285.69», «-» (sin dato) o vacío."""
    if texto is None or texto.strip() in ("", "-"):
        return None
    try:
        return float(texto.strip())
    except ValueError:
        return None


def _filas_csv(ruta: Path) -> list[dict]:
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def _valor_eur(valor: float | None, unidad: str | None) -> float | None:
    if valor is None:
        return None
    factor = FACTOR_EUROS.get((unidad or "").strip().lower())
    return valor * factor if factor else None


def leer_series(carpeta: Path = CARPETA) -> pl.DataFrame:
    """Todas las series «Año; Concepto; Valor; Unidad» en una sola tabla larga."""
    manifiesto = leer_manifiesto() if carpeta == CARPETA else {}
    filas = []
    for dataset in SERIES:
        ruta = carpeta / f"{dataset}.csv"
        if not ruta.exists():
            continue
        info = manifiesto.get(ruta.name, {})
        fecha = _fecha_fichero(ruta, info)
        for r in _filas_csv(ruta):
            if not (r.get("Año") or "").strip().isdigit() or not r.get("Concepto"):
                continue
            dim = next((r[d] for d in DIMENSIONES if d in r), None)
            valor, unidad = _numero(r.get("Valor")), r.get("Unidad")
            filas.append(
                {
                    "serie_id": dataset,
                    "serie": info.get("titulo") or dataset,
                    "anio": int(r["Año"]),
                    "concepto": r["Concepto"].strip(),
                    "dimension": (dim or "").strip() or None,
                    "valor": valor,
                    "unidad": unidad,
                    "valor_eur": _valor_eur(valor, unidad),
                    "estado_dato": (r.get("Estado dato") or "").strip() or None,
                    "fuente": FUENTE_CKAN,
                    "url_origen": info.get("url_origen")
                    or f"https://datos.comunidad.madrid/dataset/{dataset}",
                    "fecha_descarga": fecha,
                }
            )
    return (
        pl.DataFrame(filas, schema=ESQUEMA_SERIE, orient="row")
        if filas
        else pl.DataFrame(schema=ESQUEMA_SERIE)
    )


def leer_presupuesto_organo(
    carpeta: Path = CARPETA, organos: set[str] | None = None
) -> pl.DataFrame:
    """Presupuesto por órgano: iniciales (clasificación orgánica) y liquidados por fase."""
    manifiesto = leer_manifiesto() if carpeta == CARPETA else {}
    organos = organos or set()
    filas = []
    for dataset in SERIES_ORGANO:
        ruta = carpeta / f"{dataset}.csv"
        if not ruta.exists():
            continue
        info = manifiesto.get(ruta.name, {})
        fecha = _fecha_fichero(ruta, info)
        url = info.get("url_origen") or f"https://datos.comunidad.madrid/dataset/{dataset}"
        for r in _filas_csv(ruta):
            valor = _numero(r.get("Valor"))
            if valor is None or not (r.get("Año") or "").strip().isdigit():
                continue
            if dataset == "1902000":
                m, tipo, fase = _ENTIDAD_INICIAL.match(r["Concepto"].strip()), "inicial", None
            else:
                m, tipo = _ENTIDAD_LIQUIDADO.match(r["Concepto"].strip()), "liquidado"
                fase = FASES.get((r.get("Fase") or "").strip().lower())
            if not m or m.group(1).lower().startswith("total"):
                continue
            entidad = m.group(1).strip()
            clave = n_texto.clave(entidad)
            filas.append(
                {
                    "anio": int(r["Año"]),
                    "tipo": tipo,
                    "fase": fase,
                    "entidad": entidad,
                    "organo_id": clave if clave in organos else None,
                    "importe_eur": _valor_eur(valor, r.get("Unidad")) or valor,
                    "fuente": FUENTE_CKAN,
                    "url_origen": url,
                    "fecha_descarga": fecha,
                }
            )
    return (
        pl.DataFrame(filas, schema=ESQUEMA_PRESUPUESTO, orient="row")
        if filas
        else pl.DataFrame(schema=ESQUEMA_PRESUPUESTO)
    )


def _fecha_fichero(ruta: Path, info: dict) -> date:
    if info.get("fecha_descarga"):
        return date.fromisoformat(info["fecha_descarga"])
    return date.fromtimestamp(ruta.stat().st_mtime)


def parece_entidad(nombre: str) -> bool:
    """Un firmante se muestra solo si su nombre tiene forma de entidad (D-007)."""
    return bool(_PATRON_ENTIDAD.search(nombre or ""))


def _fecha_iso(valor) -> date | None:
    texto = str(valor or "").strip()[:10]
    try:
        return date.fromisoformat(texto)
    except ValueError:
        return None


def _firmantes(texto: str | None) -> tuple[str | None, list[str]]:
    """« Entidad CM: X   Entidad: Y   Entidad: Z» → («X», [«Y», «Z»])."""
    texto = texto or ""
    cm = re.search(r"Entidad CM:\s*(.+?)(?=\s+Entidad(?: CM)?:|$)", texto)
    firmantes = re.findall(r"Entidad:\s*(.+?)(?=\s+Entidad(?: CM)?:|$)", texto)
    return (cm.group(1).strip() if cm else None), [f.strip() for f in firmantes if f.strip()]


def leer_convenios(carpeta: Path = CARPETA, organos: set[str] | None = None) -> pl.DataFrame:
    """Convenios vigentes del Portal de Transparencia (Excel mensual)."""
    ruta = carpeta / "convenios_vigentes.xlsx"
    if not ruta.exists():
        return pl.DataFrame(schema=ESQUEMA_CONVENIO)
    info = leer_manifiesto().get(ruta.name, {}) if carpeta == CARPETA else {}
    fecha = _fecha_fichero(ruta, info)
    organos = organos or set()
    bruto = pl.read_excel(ruta, has_header=False, engine="calamine", infer_schema_length=0)
    filas, vistos, cabecera = [], set(), False
    for fila in bruto.iter_rows():
        if not cabecera:
            cabecera = (fila[0] or "").strip().upper().startswith("CONSEJER") and fila[
                1
            ] == "REFERENCIA"
            continue
        consejeria, referencia = (fila[0] or "").strip(), (fila[1] or "").strip()
        if not consejeria or not referencia or referencia in vistos:
            continue
        vistos.add(referencia)
        cm, firmantes = _firmantes(fila[8])
        financiacion = (fila[9] or "").strip() or None
        clave = n_texto.clave(consejeria)
        filas.append(
            {
                "convenio_id": f"convenio:{referencia}",
                "consejeria": consejeria,
                "organo_id": clave if clave in organos else None,
                "referencia": referencia,
                "titulo": (fila[2] or "").strip() or None,
                "fecha_firma": _fecha_iso(fila[3]),
                "vigencia_desde": _fecha_iso(fila[4]),
                "vigencia_hasta": _fecha_iso(fila[5]),
                "indefinido": "INDEFINID" in (fila[6] or "").upper(),
                "prorroga": (fila[7] or "").strip() or None,
                "entidad_cm": cm,
                "entidades": " ; ".join(f for f in firmantes if parece_entidad(f)) or None,
                "n_firmantes": len(firmantes),
                "financiacion": financiacion[:800] if financiacion else None,
                "con_financiacion": financiacion is not None,
                "fuente": FUENTE_TRANSPARENCIA,
                "url_origen": PAGINA_CONVENIOS,
                "fecha_descarga": fecha,
            }
        )
    return (
        pl.DataFrame(filas, schema=ESQUEMA_CONVENIO, orient="row")
        if filas
        else pl.DataFrame(schema=ESQUEMA_CONVENIO)
    )


def leer_entidades(carpeta: Path = CARPETA) -> pl.DataFrame:
    """Registros con NIF: transparencia, fundaciones y cooperativas. Solo personas jurídicas."""
    manifiesto = leer_manifiesto() if carpeta == CARPETA else {}
    filas = []
    for registro, fichero, k_nif, k_nombre, k_detalle, k_estado in (
        (
            "transparencia",
            "registro_transparencia",
            "nif",
            "denominacion",
            "categoria",
            "estado_inscripcion",
        ),
        ("fundaciones", "registro_fundaciones", "NIF", "denominacion", "protectorado", None),
        ("cooperativas", "registro_cooperativas", "NIF", "denominacion_social", "clase", None),
    ):
        ruta = carpeta / f"{fichero}.csv"
        if not ruta.exists():
            continue
        info = manifiesto.get(ruta.name, {})
        fecha = _fecha_fichero(ruta, info)
        url = info.get("url_origen") or f"https://datos.comunidad.madrid/dataset/{fichero}"
        for r in _filas_csv(ruta):
            nif = n_nif.normalizar_nif(r.get(k_nif))
            if not nif or n_nif.tipo_persona(nif) != "juridica":
                continue
            filas.append(
                {
                    "nif": nif,
                    "registro": registro,
                    "nombre": (r.get(k_nombre) or "").strip() or None,
                    "detalle": (r.get(k_detalle) or "").strip() or None if k_detalle else None,
                    "estado": (r.get(k_estado) or "").strip() or None if k_estado else None,
                    "fuente": FUENTE_CKAN,
                    "url_origen": url,
                    "fecha_descarga": fecha,
                }
            )
    df = (
        pl.DataFrame(filas, schema=ESQUEMA_ENTIDAD, orient="row")
        if filas
        else pl.DataFrame(schema=ESQUEMA_ENTIDAD)
    )
    return df.unique(subset=["nif", "registro"], keep="first", maintain_order=True)


def leer_plantilla(carpeta: Path = CARPETA, organos: set[str] | None = None) -> pl.DataFrame:
    """Número de puestos de la RPT de funcionarios por organismo."""
    ruta = carpeta / "rpt_funcionarios.csv"
    if not ruta.exists():
        return pl.DataFrame(schema=ESQUEMA_PLANTILLA)
    info = leer_manifiesto().get(ruta.name, {}) if carpeta == CARPETA else {}
    fecha = _fecha_fichero(ruta, info)
    url = (
        info.get("url_origen")
        or "https://datos.comunidad.madrid/dataset/relacion_puestos_trabajo_funcionarios_resumida"
    )
    organos = organos or set()
    cuenta: dict[str, int] = {}
    for r in _filas_csv(ruta):
        nombre = (r.get("organismo_desc") or "").strip()
        if nombre:
            cuenta[nombre] = cuenta.get(nombre, 0) + 1
    filas = [
        {
            "organismo": nombre,
            "organo_id": n_texto.clave(nombre) if n_texto.clave(nombre) in organos else None,
            "n_puestos": n,
            "fuente": FUENTE_CKAN,
            "url_origen": url,
            "fecha_descarga": fecha,
        }
        for nombre, n in sorted(cuenta.items())
    ]
    return (
        pl.DataFrame(filas, schema=ESQUEMA_PLANTILLA, orient="row")
        if filas
        else pl.DataFrame(schema=ESQUEMA_PLANTILLA)
    )


ESQUEMA_SERIE = {
    "serie_id": pl.String, "serie": pl.String, "anio": pl.Int32, "concepto": pl.String,
    "dimension": pl.String, "valor": pl.Float64, "unidad": pl.String, "valor_eur": pl.Float64,
    "estado_dato": pl.String, "fuente": pl.String, "url_origen": pl.String,
    "fecha_descarga": pl.Date,
}  # fmt: skip
ESQUEMA_PRESUPUESTO = {
    "anio": pl.Int32, "tipo": pl.String, "fase": pl.String, "entidad": pl.String,
    "organo_id": pl.String, "importe_eur": pl.Float64, "fuente": pl.String,
    "url_origen": pl.String, "fecha_descarga": pl.Date,
}  # fmt: skip
ESQUEMA_CONVENIO = {
    "convenio_id": pl.String, "consejeria": pl.String, "organo_id": pl.String,
    "referencia": pl.String, "titulo": pl.String, "fecha_firma": pl.Date,
    "vigencia_desde": pl.Date, "vigencia_hasta": pl.Date, "indefinido": pl.Boolean,
    "prorroga": pl.String, "entidad_cm": pl.String, "entidades": pl.String,
    "n_firmantes": pl.Int32, "financiacion": pl.String, "con_financiacion": pl.Boolean,
    "fuente": pl.String, "url_origen": pl.String, "fecha_descarga": pl.Date,
}  # fmt: skip
ESQUEMA_ENTIDAD = {
    "nif": pl.String, "registro": pl.String, "nombre": pl.String, "detalle": pl.String,
    "estado": pl.String, "fuente": pl.String, "url_origen": pl.String,
    "fecha_descarga": pl.Date,
}  # fmt: skip
ESQUEMA_PLANTILLA = {
    "organismo": pl.String, "organo_id": pl.String, "n_puestos": pl.Int32,
    "fuente": pl.String, "url_origen": pl.String, "fecha_descarga": pl.Date,
}  # fmt: skip


def leer_todo(carpeta: Path = CARPETA, organos: set[str] | None = None) -> dict[str, pl.DataFrame]:
    """Las cinco tablas del contexto, listas para cargar en DuckDB."""
    organos = organos or set()
    return {
        "serie_cm": leer_series(carpeta),
        "presupuesto_organo": leer_presupuesto_organo(carpeta, organos),
        "convenio": leer_convenios(carpeta, organos),
        "entidad_registro": leer_entidades(carpeta),
        "plantilla_organismo": leer_plantilla(carpeta, organos),
    }
