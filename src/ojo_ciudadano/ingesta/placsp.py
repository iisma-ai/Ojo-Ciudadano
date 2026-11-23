"""Ingesta de las licitaciones de la Comunidad de Madrid publicadas en PLACSP (F-02).

Fuente principal de licitaciones (D-012). Se usan los zip mensuales de «plataformas
agregadas» (el portal regional vuelca ahí sus expedientes), que no incluyen contratos
menores ni modificaciones. Cada zip trae varios ficheros Atom y una misma licitación
aparece una vez por cada cambio: nos quedamos con la última versión de cada expediente y
órgano.

Los importes de esta fuente van sin IVA.
"""

import zipfile
from datetime import date
from pathlib import Path

import httpx
import polars as pl
from lxml import etree

from ojo_ciudadano.normalizacion import nif as n_nif
from ojo_ciudadano.normalizacion import texto as n_texto

FUENTE = "placsp"
URL_ZIP = (
    "https://contrataciondelsectorpublico.gob.es/sindicacion/sindicacion_1044/"
    "PlataformasAgregadasSinMenores_{anio}{mes:02d}.zip"
)
DOMINIO_CM = "comunidad.madrid"
CARPETA = Path("data/raw/placsp")

NS = {
    "a": "http://www.w3.org/2005/Atom",
    "at": "http://purl.org/atompub/tombstones/1.0",
    "cbc": "urn:dgpe:names:draft:codice:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:dgpe:names:draft:codice:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonAggregateComponents-2",
    "bext": "urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonBasicComponents-2",
}

# Listas de códigos oficiales de https://contrataciondelestado.es/codice/cl/ (consultadas el
# 2026-11-16).
PROCEDIMIENTOS = {
    "1": "Abierto",
    "2": "Restringido",
    "3": "Negociado sin publicidad",
    "4": "Negociado con publicidad",
    "5": "Diálogo competitivo",
    "6": "Contrato menor",
    "7": "Derivado de acuerdo marco",
    "8": "Concurso de proyectos",
    "9": "Abierto simplificado",
    "10": "Asociación para la innovación",
    "11": "Derivado de asociación para la innovación",
    "12": "Basado en un sistema dinámico de adquisición",
    "13": "Licitación con negociación",
    "100": "Normas internas",
    "999": "Otros",
}
TIPOS = {
    "1": "suministros",
    "2": "servicios",
    "3": "obras",
    "7": "administrativo especial",
    "8": "privado",
    "21": "gestion de servicios publicos",
    "22": "concesion de servicios",
    "31": "concesion de obras publicas",
    "32": "concesion de obras",
    "40": "colaboracion entre el sector publico y sector privado",
    "50": "patrimonial",
}
ESTADOS = {
    "PRE": "Anuncio previo",
    "PUB": "En plazo",
    "EV": "Pendiente de adjudicación",
    "ADJ": "Adjudicada",
    "RES": "Resuelta",
    "ANUL": "Anulada",
}
# La lista oficial está en inglés; esta es nuestra traducción.
RESULTADOS = {
    "1": "Adjudicado provisionalmente",
    "2": "Adjudicado definitivamente",
    "3": "Desierto",
    "4": "Desistimiento",
    "5": "Renuncia",
    "6": "Desierto provisionalmente",
    "7": "Desierto definitivamente",
    "8": "Adjudicado",
    "9": "Formalizado",
    "10": "Licitador mejor valorado",
    "11": "Encargo formalizado",
}

ESQUEMA_CONTRATOS = {
    "contrato_id": pl.String,
    "fuente": pl.String,
    "expediente": pl.String,
    "organo_codigo": pl.String,
    "organo_nombre": pl.String,
    "organo_jerarquia": pl.String,
    "consejeria": pl.String,
    "titulo": pl.String,
    "tipo_contrato": pl.String,
    "procedimiento": pl.String,
    "es_menor": pl.Boolean,
    "estado": pl.String,
    "cpv": pl.String,
    "presupuesto_sin_iva": pl.Float64,
    "valor_estimado": pl.Float64,
    "fecha_fin_plazo": pl.Date,
    "financiado_ue": pl.Boolean,
    "programas_ue": pl.String,
    "fecha_actualizacion": pl.String,
    "url_origen": pl.String,
    "fecha_descarga": pl.Date,
}
ESQUEMA_ADJUDICACIONES = {
    "contrato_id": pl.String,
    "orden": pl.Int32,
    "lote": pl.String,
    "adjudicatario_id": pl.String,
    "nif": pl.String,
    "nombre": pl.String,
    "tipo_persona": pl.String,
    "n_ofertas": pl.Int64,
    "resultado": pl.String,
    "importe_sin_iva": pl.Float64,
    "fecha_formalizacion": pl.Date,
    "fuente": pl.String,
    "url_origen": pl.String,
    "fecha_descarga": pl.Date,
}


def descargar_mes(anio: int, mes: int, carpeta: Path = CARPETA) -> Path:
    """Descarga el zip de un mes si no está ya en la caché local y devuelve su ruta."""
    destino = carpeta / f"PlataformasAgregadasSinMenores_{anio}{mes:02d}.zip"
    if destino.exists() and destino.stat().st_size > 0:
        return destino
    carpeta.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_suffix(".parcial")
    with httpx.stream(
        "GET", URL_ZIP.format(anio=anio, mes=mes), timeout=120, follow_redirects=True
    ) as r:
        r.raise_for_status()
        with temporal.open("wb") as f:
            for trozo in r.iter_bytes():
                f.write(trozo)
    temporal.replace(destino)
    return destino


def _texto(nodo, ruta: str) -> str | None:
    valor = nodo.xpath(f"string({ruta})", namespaces=NS).strip()
    return valor or None


def _fecha(texto: str | None) -> date | None:
    try:
        return date.fromisoformat(texto[:10]) if texto else None
    except ValueError:
        return None


def _jerarquia(entrada) -> list[str]:
    """Nombres de los órganos superiores, de la consejería hacia abajo, y al final el órgano."""
    nombres = []
    nodo = entrada.find(".//ext:LocatedContractingParty/ext:ParentLocatedParty", NS)
    while nodo is not None:
        nombre = _texto(nodo, "cac:PartyName/cbc:Name")
        if nombre:
            nombres.append(nombre)
        nodo = nodo.find("ext:ParentLocatedParty", NS)
    organo = _texto(entrada, ".//ext:LocatedContractingParty/cac:Party/cac:PartyName/cbc:Name")
    return [*nombres, organo] if organo else nombres


def _leer_entrada(entrada, fecha_descarga: date, sal: bytes | None) -> tuple[dict, list[dict]]:
    """Convierte una entrada Atom en la fila del contrato y las filas de sus adjudicaciones."""
    url = entrada.find("a:link", NS).get("href")
    contrato_id = f"{FUENTE}:{_texto(entrada, 'a:id').rsplit('/', 1)[-1]}"
    jerarquia = _jerarquia(entrada)
    proyecto = ".//ext:ContractFolderStatus/cac:ProcurementProject"
    codigo_procedimiento = _texto(entrada, ".//cac:TenderingProcess/cbc:ProcedureCode")
    codigo_tipo = _texto(entrada, f"{proyecto}/cbc:TypeCode")
    cpvs = entrada.xpath(
        f"{proyecto}/cac:RequiredCommodityClassification/cbc:ItemClassificationCode/text()",
        namespaces=NS,
    )
    partido = ".//ext:LocatedContractingParty/cac:Party/cac:PartyIdentification"
    # Financiación: «EU» / «NO-EU» y, si hay fondos europeos, el programa (PRTR, FEDER, FSE+…).
    fondos = entrada.xpath(".//cac:TenderingTerms/cbc:FundingProgramCode/text()", namespaces=NS)
    fondos = [f.strip() for f in fondos if f.strip()]
    contrato = {
        "contrato_id": contrato_id,
        "fuente": FUENTE,
        "expediente": _texto(entrada, ".//cbc:ContractFolderID"),
        "organo_codigo": _texto(entrada, f"{partido}/cbc:ID[@schemeName='ID_OC_PLAT']")
        or _texto(entrada, f"{partido}/cbc:ID"),
        "organo_nombre": jerarquia[-1] if jerarquia else None,
        "organo_jerarquia": "··>".join(jerarquia) or None,
        "consejeria": jerarquia[0] if len(jerarquia) > 1 else None,
        "titulo": _texto(entrada, f"{proyecto}/cbc:Name") or _texto(entrada, "a:title"),
        "tipo_contrato": TIPOS.get(codigo_tipo, codigo_tipo),
        "procedimiento": PROCEDIMIENTOS.get(codigo_procedimiento, codigo_procedimiento),
        "es_menor": codigo_procedimiento == "6",
        "estado": ESTADOS.get(
            _texto(entrada, ".//bext:ContractFolderStatusCode"),
            _texto(entrada, ".//bext:ContractFolderStatusCode"),
        ),
        "cpv": cpvs[0].strip() if cpvs else None,
        "presupuesto_sin_iva": n_texto.importe(
            _texto(entrada, f"{proyecto}/cac:BudgetAmount/cbc:TaxExclusiveAmount")
        ),
        "valor_estimado": n_texto.importe(
            _texto(entrada, f"{proyecto}/cac:BudgetAmount/cbc:EstimatedOverallContractAmount")
        ),
        "fecha_fin_plazo": _fecha(
            _texto(
                entrada, ".//cac:TenderingProcess/cac:TenderSubmissionDeadlinePeriod/cbc:EndDate"
            )
        ),
        "financiado_ue": ("EU" in fondos) if fondos else None,
        "programas_ue": ",".join(sorted(set(fondos) - {"EU", "NO-EU"})) or None,
        "fecha_actualizacion": _texto(entrada, "a:updated"),
        "url_origen": url,
        "fecha_descarga": fecha_descarga,
    }

    adjudicaciones = []
    for orden, resultado in enumerate(entrada.iterfind(".//cac:TenderResult", NS), start=1):
        codigo = _texto(resultado, "cbc:ResultCode")
        identidad = n_nif.identificar(
            _texto(resultado, "cac:WinningParty/cac:PartyIdentification/cbc:ID"),
            _texto(resultado, "cac:WinningParty/cac:PartyName/cbc:Name"),
            sal,
        )
        adjudicaciones.append(
            {
                "contrato_id": contrato_id,
                "orden": orden,
                "lote": _texto(resultado, "cac:AwardedTenderedProject/cbc:ProcurementProjectLotID"),
                "adjudicatario_id": identidad["adjudicatario_id"],
                "nif": identidad["nif"],
                "nombre": identidad["nombre"],
                "tipo_persona": identidad["tipo_persona"],
                "n_ofertas": n_texto.entero(_texto(resultado, "cbc:ReceivedTenderQuantity")),
                "resultado": RESULTADOS.get(codigo, codigo),
                "importe_sin_iva": n_texto.importe(
                    _texto(
                        resultado,
                        "cac:AwardedTenderedProject/cac:LegalMonetaryTotal/cbc:TaxExclusiveAmount",
                    )
                ),
                "fecha_formalizacion": _fecha(_texto(resultado, "cac:Contract/cbc:IssueDate")),
                "fuente": FUENTE,
                "url_origen": url,
                "fecha_descarga": fecha_descarga,
            }
        )
    return contrato, adjudicaciones


def leer_atom(
    contenido: bytes, fecha_descarga: date, sal: bytes | None = None
) -> tuple[list, list, set]:
    """Devuelve contratos, adjudicaciones e identificadores borrados de un fichero Atom.

    Solo se leen las entradas cuyo enlace apunta al portal de la Comunidad de Madrid.
    """
    raiz = etree.fromstring(contenido)
    contratos, adjudicaciones = [], []
    for entrada in raiz.iterfind("a:entry", NS):
        enlace = entrada.find("a:link", NS)
        if enlace is None or DOMINIO_CM not in (enlace.get("href") or ""):
            continue
        contrato, suyas = _leer_entrada(entrada, fecha_descarga, sal)
        contratos.append(contrato)
        adjudicaciones.extend(suyas)
    borrados = {
        f"{FUENTE}:{b.get('ref').rsplit('/', 1)[-1]}"
        for b in raiz.iterfind("at:deleted-entry", NS)
        if b.get("ref")
    }
    return contratos, adjudicaciones, borrados


def ultima_version(
    contratos: pl.DataFrame, adjudicaciones: pl.DataFrame
) -> dict[str, pl.DataFrame]:
    """Deja una sola versión, la más reciente, de cada expediente y órgano."""
    ultimos = (
        contratos.sort("fecha_actualizacion", descending=True)
        .unique(["expediente", "organo_codigo"], keep="first", maintain_order=True)
        .unique("contrato_id", keep="first", maintain_order=True)
        .sort("contrato_id")
    )
    # Varias versiones de una entrada comparten contrato_id: las adjudicaciones se toman
    # solo de la versión que se conserva. Una misma versión puede venir en dos ficheros.
    versiones = ultimos.select("contrato_id", "fecha_actualizacion")
    adjudicaciones = adjudicaciones.unique(["contrato_id", "fecha_actualizacion", "orden"]).join(
        versiones, on=["contrato_id", "fecha_actualizacion"], how="inner"
    )
    return {
        "contratos": ultimos,
        "adjudicaciones": adjudicaciones.drop("fecha_actualizacion").sort("contrato_id", "orden"),
    }


def leer_zips(
    rutas: list[Path], fecha_descarga: date, sal: bytes | None = None
) -> dict[str, pl.DataFrame]:
    """Lee uno o varios zip mensuales y devuelve `contratos` y `adjudicaciones` sin repetidos."""
    contratos, adjudicaciones, borrados = [], [], set()
    for ruta in rutas:
        with zipfile.ZipFile(ruta) as z:
            for nombre in z.namelist():
                if not nombre.endswith(".atom"):
                    continue
                c, a, b = leer_atom(z.read(nombre), fecha_descarga, sal)
                versiones = {fila["contrato_id"]: fila["fecha_actualizacion"] for fila in c}
                for fila in a:
                    fila["fecha_actualizacion"] = versiones[fila["contrato_id"]]
                contratos.extend(c)
                adjudicaciones.extend(a)
                borrados |= b
    df_c = pl.DataFrame(contratos, schema=ESQUEMA_CONTRATOS)
    df_a = pl.DataFrame(
        adjudicaciones, schema={**ESQUEMA_ADJUDICACIONES, "fecha_actualizacion": pl.String}
    )
    df_c = df_c.filter(~pl.col("contrato_id").is_in(list(borrados)))
    return ultima_version(df_c, df_a)
