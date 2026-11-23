"""Resoluciones del Tribunal Administrativo de Contratación Pública de la Comunidad de Madrid.

El Tribunal (TACPCM) resuelve los recursos especiales contra pliegos, exclusiones y
adjudicaciones de los órganos de la Comunidad (Ley 9/2010 de la Comunidad de Madrid). Que un
recurso se presente no es una señal; que se estime solo dice que ese acto no se ajustaba a
derecho. Es contexto oficial del contrato (D-029), no un indicador de riesgo.

Fuente: el buscador público https://www.comunidad.madrid/tacp/busquedaresoluciones (HTML,
5 resoluciones por página, sin descarga masiva). Casi todas las resoluciones tienen una sola
procedencia, un solo tipo de resolución y un solo acto recurrido (el 23-nov-2026 los filtros
sumaban las 451 de consejerías), así que se recorre el listado por combinación de los tres
filtros y cada resolución sale ya etiquetada. Limitación: el listado ordena por fecha y, con
empates, la paginación repite o salta alguna fila (el 23-nov se recogieron 1.097 de 1.109).
Las páginas se guardan en `data/raw/tacp/`, una petición cada vez y con pausa.

Uso:
    uv run python -m ojo_ciudadano.ingesta.tacp          # listado
    uv run python -m ojo_ciudadano.ingesta.tacp --pdf    # y los PDF (D-030, bloque C; ~20 min)
"""

import html
import re
import time
from datetime import date
from pathlib import Path

import httpx
import polars as pl

from ojo_ciudadano.ingesta import documentos

CARPETA = Path("data/raw/tacp")
URL = "https://www.comunidad.madrid/tacp/busquedaresoluciones"
URL_BASE = "https://www.comunidad.madrid"
FUENTE = "tacpcm"
DESDE, HASTA = "01/01/2023", "31/12/2026"
PAUSA = 2.0

# Valores de los filtros del buscador (formulario del 23-nov-2026). Sin municipios: fuera de
# alcance (D-001).
PROCEDENCIAS = {
    "1": "Consejerías",
    "42": "Hospitales",
    "23": "Otros poderes adjudicadores",
    "21": "Universidades",
}
TIPOS_RESOLUCION = {
    "35": "Desestimatoria",
    "41": "Estimatoria",
    "10": "Estimatoria parcial",
    "53": "Inadmisión",
    "45": "Otros",
}
ACTOS_RECURRIDOS = {
    "25": "Pliegos",
    "69": "Anuncio",
    "66": "Admisión",
    "17": "Exclusión",
    "56": "Adjudicación",
    "18": "Otros",
}

_FILA = re.compile(r'<li class="views-row.*?</li>', re.S)
_NUMERO = re.compile(r'href="(/tacp/resolucion/\d+)">(\d+/\d{4})</a>')
_FECHA = re.compile(r'content="(\d{4}-\d{2}-\d{2})T')
_RESUMEN = re.compile(r'views-field-body">\s*<span class="field-content">(.*?)</span>', re.S)
_PDF = re.compile(r'<a href="([^"]+/download[^"]*)"[^>]*>([^<]+\.pdf)</a>')
# Posibles números de expediente de contratación en el resumen: un bloque con alguna cifra y
# alguna barra o guion («BAC01/2026», «A/SER-012345/2025», «PA 3/2024»).
_EXPEDIENTE = re.compile(r"\b[A-Z0-9][A-Z0-9.\-_]*[/\-][A-Z0-9.\-/_]*\d[A-Z0-9.\-/_]*\b")


def _url(procedencia: str, tipo: str, acto: str, pagina: int) -> str:
    return (
        f"{URL}?field_procedencia={procedencia}&im_field_tipo_de_resolucion={tipo}"
        f"&field_acto_recurrido={acto}&field_fecha%5Bdate%5D={DESDE}"
        f"&field_fecha_1%5Bdate%5D={HASTA}&page={pagina}"
    )


def descargar(carpeta: Path = CARPETA, pausa: float = PAUSA) -> int:
    """Guarda las páginas del listado que falten. Devuelve cuántas se han pedido."""
    carpeta.mkdir(parents=True, exist_ok=True)
    pedidas = 0
    with httpx.Client(timeout=60, follow_redirects=True) as cliente:
        for p in PROCEDENCIAS:
            for t in TIPOS_RESOLUCION:
                for a in ACTOS_RECURRIDOS:
                    pagina = 0
                    while True:
                        ruta = carpeta / f"p{p}_t{t}_a{a}_{pagina:03d}.html"
                        if not ruta.exists():
                            respuesta = cliente.get(_url(p, t, a, pagina))
                            respuesta.raise_for_status()
                            ruta.write_text(respuesta.text, encoding="utf-8")
                            pedidas += 1
                            time.sleep(pausa)
                        if not _FILA.search(_listado(ruta.read_text(encoding="utf-8"))):
                            break
                        pagina += 1
    return pedidas


def _listado(pagina: str) -> str:
    """Solo la lista de resultados (la página repite resoluciones destacadas en el menú)."""
    inicio = pagina.find('class="view-content"')
    return pagina[inicio:] if inicio >= 0 else ""


def expedientes_citados(resumen: str) -> list[str]:
    """Candidatos a número de expediente de contratación citados en el resumen.

    Se descartan los cortos sin letras («9/2017», «3/2020»): suelen ser leyes, sentencias o
    expedientes del propio Tribunal, y casarían por azar con algún contrato.
    """
    candidatos = (m.group(0).rstrip(".-/") for m in _EXPEDIENTE.finditer(resumen))
    return list(dict.fromkeys(c for c in candidatos if re.search(r"[A-Z]", c) or len(c) >= 8))


def leer_pagina(texto: str, procedencia: str, tipo: str, acto: str) -> list[dict]:
    filas = []
    for bloque in _FILA.findall(_listado(texto)):
        numero = _NUMERO.search(bloque)
        if not numero:
            continue
        fecha = _FECHA.search(bloque)
        resumen = _RESUMEN.search(bloque)
        pdf = _PDF.search(bloque)
        resumen_texto = html.unescape(re.sub(r"<[^>]+>", " ", resumen.group(1))) if resumen else ""
        filas.append(
            {
                "resolucion_id": f"{FUENTE}:{numero.group(2)}",
                "numero": numero.group(2),
                "fecha": date.fromisoformat(fecha.group(1)) if fecha else None,
                "procedencia": PROCEDENCIAS[procedencia],
                "tipo_resolucion": TIPOS_RESOLUCION[tipo],
                "acto_recurrido": ACTOS_RECURRIDOS[acto],
                "expedientes_citados": expedientes_citados(resumen_texto.upper()),
                "url_origen": URL_BASE + numero.group(1),
                "url_documento": URL_BASE + html.unescape(pdf.group(1)) if pdf else None,
            }
        )
    return filas


def leer(carpeta: Path = CARPETA, fecha_descarga: date | None = None) -> pl.DataFrame:
    """Una fila por resolución, con los candidatos a expediente citados en su resumen.

    El resumen no se guarda: nombra a las empresas recurrentes y puede nombrar a personas.
    """
    filas = []
    for ruta in sorted(carpeta.glob("p*_t*_a*_*.html")):
        p, t, a, _ = ruta.stem.split("_")
        filas += leer_pagina(ruta.read_text(encoding="utf-8"), p[1:], t[1:], a[1:])
    fecha_descarga = fecha_descarga or date.today()
    esquema = {
        "resolucion_id": pl.String,
        "numero": pl.String,
        "fecha": pl.Date,
        "procedencia": pl.String,
        "tipo_resolucion": pl.String,
        "acto_recurrido": pl.String,
        "expedientes_citados": pl.List(pl.String),
        "url_origen": pl.String,
        "url_documento": pl.String,
    }
    return (
        pl.DataFrame(filas, schema=esquema)
        # Una resolución puede salir dos veces: si el listado repite una fila al paginar
        # (ordena por fecha y hay empates) o si resuelve un recurso con dos actos recurridos
        # o dos resultados (acumulación). Se queda una fila con las etiquetas unidas.
        .group_by("resolucion_id", maintain_order=True)
        .agg(
            pl.col("numero", "fecha", "procedencia", "url_origen", "url_documento").first(),
            pl.col("tipo_resolucion").unique(maintain_order=True).str.join("; "),
            pl.col("acto_recurrido").unique(maintain_order=True).str.join("; "),
            pl.col("expedientes_citados").first(),
        )
        .with_columns(
            pl.lit(FUENTE).alias("fuente"), pl.lit(fecha_descarga).alias("fecha_descarga")
        )
        .sort("resolucion_id")
    )


TIPO_DOCUMENTO = "tacpcm"  # subcarpeta de data/raw/documentos/
# Título del contrato recurrido, entre comillas, en el encabezamiento de la resolución
# («… contra el acuerdo … por el que se adjudica el contrato de “Servicios de …”»).
_TITULO_PDF = re.compile(r"[«“\"]([^»”\"]{15,400})[»”\"]")
PAGINAS_ENCABEZADO = 2


def descargar_pdfs(tabla: pl.DataFrame, pausa: float = documentos.PAUSA) -> dict:
    """Baja los PDF de las resoluciones que falten (D-030, bloque C), uno cada vez y con
    pausa. Devuelve {url: ruta o None}."""
    urls = [u for u in tabla["url_documento"].drop_nulls().to_list()]
    return documentos.descargar_varios(urls, TIPO_DOCUMENTO, pausa=pausa)


def _encabezado(url: str | None, carpeta: Path) -> str:
    """Texto de las primeras páginas del PDF si ya está en la caché (sin red)."""
    if not url:
        return ""
    ruta = documentos.ruta_local(url, TIPO_DOCUMENTO, carpeta)
    if not ruta.exists():
        return ""
    try:
        return "\n".join(documentos.paginas(ruta)[:PAGINAS_ENCABEZADO])
    except documentos.DocumentoNoDisponible:
        return ""


def titulos_citados(texto: str) -> list[str]:
    """Textos entre comillas del encabezamiento que pueden ser el título del contrato."""
    plano = re.sub(r"\s+", " ", texto)
    return list(dict.fromkeys(m.group(1).strip() for m in _TITULO_PDF.finditer(plano)))


def con_texto_pdf(tabla: pl.DataFrame, carpeta: Path = documentos.CARPETA) -> pl.DataFrame:
    """Añade los candidatos que salen del PDF ya descargado: más expedientes citados y los
    títulos entre comillas del encabezamiento (`titulos_citados`). Sirve para enlazar más
    resoluciones con su contrato (`carga.cruzar_recursos`). El texto no se guarda en la base."""
    expedientes, titulos = [], []
    filas = tabla.select("url_documento", "expedientes_citados").iter_rows()
    for url, citados in filas:
        encabezado = _encabezado(url, carpeta)
        # Del PDF solo los que llevan letras: los números sin letras del encabezamiento son
        # casi siempre del propio Tribunal («Recurso nº 432/2023»), leyes o fechas.
        extra = [c for c in expedientes_citados(encabezado.upper()) if re.search(r"[A-Z]", c)]
        expedientes.append(list(dict.fromkeys([*(citados or []), *extra])))
        titulos.append(titulos_citados(encabezado) if encabezado else [])
    return tabla.with_columns(
        pl.Series("expedientes_citados", expedientes, dtype=pl.List(pl.String)),
        pl.Series("titulos_citados", titulos, dtype=pl.List(pl.String)),
    )


if __name__ == "__main__":
    import sys

    print(f"Páginas pedidas: {descargar()}")
    tabla = leer()
    print(f"Resoluciones: {tabla.height}")
    print(tabla.group_by("procedencia", "tipo_resolucion").len().sort("procedencia", "len"))
    if "--pdf" in sys.argv:
        bajados = descargar_pdfs(tabla)
        print(f"PDF disponibles: {sum(r is not None for r in bajados.values())} de {len(bajados)}")
