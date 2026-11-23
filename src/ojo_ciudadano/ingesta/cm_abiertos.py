"""Descarga del contexto presupuestario y organizativo de la Comunidad de Madrid (F-06 y F-04).

Fuentes, todas de la Comunidad de Madrid y de descarga abierta:
- el catálogo de datos abiertos (https://datos.comunidad.madrid, API CKAN): presupuestos
  iniciales y liquidados, ayudas de la UE, personal, gasto sanitario y educativo, recaudación,
  registro de transparencia, fundaciones, cooperativas y relación de puestos de trabajo;
- el Portal de Transparencia: el listado mensual de convenios vigentes.

Una petición cada vez y con pausa, como pide el resto de la ingesta. Cada fichero se guarda en
`data/raw/cm_abiertos/` y no se vuelve a bajar salvo que se fuerce. El manifiesto
`data/raw/cm_abiertos/manifiesto.json` anota para cada fichero la URL, la fecha, el tamaño y su
huella, para comprobar que todo el equipo tiene lo mismo (docs/datos-cm-referencia.json).

Uso: uv run python -m ojo_ciudadano.ingesta.cm_abiertos [--forzar]
"""

import hashlib
import json
import re
import sys
import time
from datetime import date
from pathlib import Path

import httpx

CARPETA = Path("data/raw/cm_abiertos")
MANIFIESTO = CARPETA / "manifiesto.json"
API_CKAN = "https://datos.comunidad.madrid/api/action/package_show"
URL_DATASET = "https://datos.comunidad.madrid/dataset/"
PAGINA_CONVENIOS = "https://www.comunidad.madrid/transparencia/convenios"
PAUSA_SEGUNDOS = 1.0
CLIENTE = {"User-Agent": "OjoCiudadano-DataMad2026 (proyecto de transparencia)"}

# Series con formato «Año; Concepto; …; Valor; Unidad» que van a la tabla `serie_cm`.
SERIES = [
    "1502013",  # presupuestos iniciales, gastos por capítulos
    "1502012",  # presupuestos iniciales, ingresos por capítulos
    "1901960",  # presupuestos iniciales, gastos por clasificación funcional
    "presupuestos_generales_iniciales_gastos_consolidados_por_seccion_y_capitulo",
    "presupuestos_generales_iniciales_gastos_consolidados_por_centro_presupuestario_y_capitulo",
    "presupuestos_generales_iniciales_ingresos_sin_consolidar_por_centro_presupuestario_y_capitulo",
    "presupuestos_liquidados_gastos_consolidados_por_capitulo_y_fase_ejecucion",
    "presupuestos_liquidados_ingresos_consolidados_por_capitulo_y_fase_ejecucion",
    "1902617",  # ayudas del presupuesto de la UE
    "1914620",  # contratos administrativos por tipo (estadística de la Junta Consultiva)
    "1914621",  # contratos administrativos por forma de adjudicación
    "1933725",  # contratos administrativos por procedimiento de adjudicación
    "1904580",  # gasto sanitario público, clasificación económica
    "1904581",  # gasto sanitario público, clasificación funcional
    "1904582",  # gasto sanitario público, cuenta satélite
    "gasto_publico_educacion_consejeria_competencias_por_capitulo",
    "gasto_publico_educacion_resto_consejerias_por_capitulo",
    "personal_administracion_autonomica_por_sexo_y_tipo_personal",
    "personal_comunidad_madrid_por_area_actividad_y_sexo",
    "1906820",  # personal de entidades públicas empresariales
    "1501018",  # altos cargos (recuentos)
    "1902613",  # recursos del sistema de financiación autonómica
    "1916741",  # recaudación tributaria
    "recaudacion_impuestos_propios_cm_y_recargos_tributos_estatales",
    "tributos_cedidos_gestion_propia",
]
# Series por órgano que van a `presupuesto_organo`.
SERIES_ORGANO = [
    "1902000",  # presupuestos iniciales, gastos por clasificación orgánica
    "presupuestos_liquidados_gastos_consolidados_por_organo_y_fase_ejecucion",
]
# Registros de entidades con NIF y otros ficheros: (id, conjunto de datos, texto del recurso).
REGISTROS = [
    ("registro_transparencia", "registro_transparencia", "simplificado"),
    ("registro_fundaciones", "registro_fundaciones", ""),
    ("registro_cooperativas", "registro_cooperativas", ""),
    ("rpt_funcionarios", "relacion_puestos_trabajo_funcionarios_resumida", ""),
]


def _cliente() -> httpx.Client:
    return httpx.Client(headers=CLIENTE, follow_redirects=True, timeout=120)


def recurso_csv(cliente: httpx.Client, dataset: str, texto: str = "") -> dict:
    """Recurso CSV de un conjunto de datos del catálogo (el primero cuyo nombre lleve `texto`)."""
    r = cliente.get(API_CKAN, params={"id": dataset})
    r.raise_for_status()
    datos = r.json()["result"]
    csv = [
        x
        for x in datos["resources"]
        if x["format"].upper() == "CSV" and texto.lower() in x["name"].lower()
    ]
    if not csv:
        raise ValueError(f"El conjunto {dataset} no tiene un CSV con «{texto}»")
    return {"url": csv[0]["url"], "titulo": datos["title"], "dataset": dataset}


def url_convenios(cliente: httpx.Client) -> str:
    """El listado de convenios vigentes cambia de nombre cada mes: se busca en la página."""
    html = cliente.get(PAGINA_CONVENIOS).text
    enlaces = re.findall(r'href="([^"]*open-data/downloads/[^"]*convenios[^"]*\.xlsx)"', html, re.I)
    if not enlaces:
        raise ValueError("No se encuentra el listado de convenios en la página de transparencia")
    return enlaces[0]


def _huella(contenido: bytes) -> str:
    return hashlib.sha256(contenido).hexdigest()


def _guardar(ruta: Path, contenido: bytes) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_bytes(contenido)


def leer_manifiesto() -> dict:
    if MANIFIESTO.exists():
        return json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    return {}


def _bajar(cliente: httpx.Client, url: str, ruta: Path, manifiesto: dict, extra: dict) -> None:
    contenido = cliente.get(url).raise_for_status().content
    _guardar(ruta, contenido)
    manifiesto[ruta.name] = {
        "url_descarga": url,
        "fecha_descarga": date.today().isoformat(),
        "bytes": len(contenido),
        "sha256": _huella(contenido),
        **extra,
    }
    time.sleep(PAUSA_SEGUNDOS)


def descargar(forzar: bool = False, carpeta: Path = CARPETA) -> dict:
    """Baja lo que falta y devuelve el manifiesto. Un fichero ya bajado no se repite."""
    manifiesto = leer_manifiesto()
    with _cliente() as cliente:
        trabajos = [(s, s, "", ".csv", "serie") for s in SERIES]
        trabajos += [(s, s, "", ".csv", "organo") for s in SERIES_ORGANO]
        trabajos += [(i, d, t, ".csv", "registro") for i, d, t in REGISTROS]
        for nombre, dataset, texto, ext, clase in trabajos:
            ruta = carpeta / f"{nombre}{ext}"
            if ruta.exists() and not forzar and ruta.name in manifiesto:
                continue
            recurso = recurso_csv(cliente, dataset, texto)
            print(f"Descargando {dataset}")
            _bajar(
                cliente,
                recurso["url"],
                ruta,
                manifiesto,
                {
                    "clase": clase,
                    "dataset": dataset,
                    "titulo": recurso["titulo"],
                    "url_origen": URL_DATASET + dataset,
                },
            )
        ruta = carpeta / "convenios_vigentes.xlsx"
        if forzar or not ruta.exists() or ruta.name not in manifiesto:
            print("Descargando convenios vigentes")
            _bajar(
                cliente,
                url_convenios(cliente),
                ruta,
                manifiesto,
                {"clase": "convenios", "url_origen": PAGINA_CONVENIOS},
            )
    carpeta.mkdir(parents=True, exist_ok=True)
    MANIFIESTO.write_text(json.dumps(manifiesto, ensure_ascii=False, indent=1), encoding="utf-8")
    return manifiesto


if __name__ == "__main__":
    resultado = descargar(forzar="--forzar" in sys.argv)
    total = sum(f["bytes"] for f in resultado.values())
    print(f"{len(resultado)} ficheros en {CARPETA} ({total // 1024} KB)")
