"""Ingesta de los CSV exportados a mano del Portal de la Contratación Pública (F-01).

La exportación está protegida por captcha, así que no se descarga por código: una persona
exporta los ficheros a `data/raw/portal_cm/` (procedimiento en docs/02-fuentes-datos.md) y este
módulo los lee. De aquí salen los contratos menores y los importes de modificaciones,
prórrogas y liquidación (D-012).

Cada fichero produce dos tablas:
- contratos: una fila por contrato (la fila «de cabecera» del CSV);
- adjudicaciones: una fila por adjudicatario. En las licitaciones con varios lotes, los
  adjudicatarios adicionales vienen en filas sin cabecera justo debajo de su contrato.

Los importes de esta fuente llevan IVA.
"""

from datetime import date
from pathlib import Path

import polars as pl

from ojo_ciudadano.normalizacion import nif as n_nif
from ojo_ciudadano.normalizacion import texto as n_texto

FUENTE = "portal_cm"
URL_FICHA = "https://contratos-publicos.comunidad.madrid/contrato/"
SEPARADOR_JERARQUIA = "··>"

COLUMNAS = {
    "Tipo de Publicación": "tipo_publicacion",
    "Estado": "estado",
    "Entidad Adjudicadora": "entidad",
    "Nº Expediente": "expediente",
    "Referencia": "referencia",
    "Título del contrato": "titulo",
    "Tipo de contrato": "tipo_contrato",
    "Procedimiento de adjudicación": "procedimiento",
    "Presupuesto de licitación": "presupuesto",
    "Nº de ofertas": "n_ofertas",
    "Resultado": "resultado",
    "NIF del adjudicatario": "nif",
    "Adjudicatario": "adjudicatario",
    "Fecha del contrato": "fecha_contrato",
    "Importe de adjudicación": "importe_adjudicacion",
    "Importe de las modificaciones": "importe_modificaciones",
    "Importe de las prórrogas": "importe_prorrogas",
    "Importe de la liquidación": "importe_liquidacion",
}


def _aplicar(df: pl.DataFrame, columna: str, funcion, tipo: pl.DataType) -> pl.DataFrame:
    """Aplica una función de normalización calculándola una sola vez por valor distinto."""
    valores = df[columna].drop_nulls().unique().to_list()
    tabla = pl.DataFrame(
        {columna: valores, "_nuevo": [funcion(v) for v in valores]},
        schema={columna: pl.String, "_nuevo": tipo},
    )
    return df.join(tabla, on=columna, how="left").drop(columna).rename({"_nuevo": columna})


def _identidades(df: pl.DataFrame, sal: bytes | None) -> pl.DataFrame:
    """Sustituye NIF y nombre por la identidad que guardamos; seudonimiza a las personas físicas."""
    pares = df.select("nif", "adjudicatario").unique()
    filas = [n_nif.identificar(nif, nombre, sal) for nif, nombre in pares.iter_rows()]
    identidades = pl.DataFrame(
        filas,
        schema=dict.fromkeys(("adjudicatario_id", "nif", "nombre", "tipo_persona"), pl.String),
    ).rename({"nif": "nif_normalizado"})
    pares = pl.concat([pares, identidades], how="horizontal")
    return (
        df.join(pares, on=["nif", "adjudicatario"], how="left", nulls_equal=True)
        .drop("nif", "adjudicatario")
        .rename({"nif_normalizado": "nif"})
    )


def leer(
    ruta: Path | str, fecha_descarga: date, sal: bytes | None = None
) -> dict[str, pl.DataFrame]:
    """Lee un CSV exportado del portal y devuelve las tablas `contratos` y `adjudicaciones`."""
    bruto = pl.read_csv(ruta, separator=";", infer_schema_length=0, encoding="utf8-lossy")
    bruto = bruto.rename(COLUMNAS)
    bruto = bruto.with_columns(pl.all().str.strip_chars()).with_columns(
        pl.when(pl.all() == "").then(None).otherwise(pl.all()).name.keep()
    )

    # Una fila es de cabecera si trae tipo de publicación; las demás cuelgan del contrato anterior.
    bruto = bruto.with_row_index("fila").with_columns(
        pl.col("tipo_publicacion").is_not_null().alias("es_cabecera")
    )
    bruto = bruto.with_columns(pl.col("es_cabecera").cum_sum().alias("n_contrato"))

    # Sin referencia no hay enlace a la ficha oficial, y sin enlace al origen la cifra no se
    # muestra: esos contratos (un puñado en todo el portal) no se cargan.
    cabeceras = bruto.filter(pl.col("es_cabecera") & pl.col("referencia").is_not_null())
    # La referencia identifica el contrato; si se repite se le añade el orden en el fichero.
    cabeceras = cabeceras.with_columns(
        pl.when(pl.col("referencia").is_duplicated())
        .then(pl.format("{}:{}#{}", pl.lit(FUENTE), pl.col("referencia"), pl.col("fila")))
        .otherwise(pl.format("{}:{}", pl.lit(FUENTE), pl.col("referencia")))
        .alias("contrato_id"),
        (pl.lit(URL_FICHA) + pl.col("referencia")).alias("url_origen"),
    )

    partes = pl.col("entidad").str.split(SEPARADOR_JERARQUIA)
    contratos = cabeceras.with_columns(
        partes.list.last().str.strip_chars().alias("organo_nombre"),
        pl.when(partes.list.len() > 1)
        .then(partes.list.first().str.strip_chars())
        .alias("consejeria"),
        pl.col("entidad").alias("organo_jerarquia"),
        pl.col("procedimiento")
        .str.to_lowercase()
        .str.contains("menor")
        .fill_null(False)
        .alias("es_menor"),
    )
    contratos = _aplicar(contratos, "presupuesto", n_texto.importe, pl.Float64)
    contratos = _aplicar(contratos, "fecha_contrato", n_texto.fecha_larga, pl.Date)
    contratos = _aplicar(contratos, "tipo_contrato", n_texto.tipo_contrato, pl.String)
    contratos = contratos.select(
        "contrato_id",
        pl.lit(FUENTE).alias("fuente"),
        "referencia",
        "expediente",
        "organo_nombre",
        "organo_jerarquia",
        "consejeria",
        "titulo",
        "tipo_publicacion",
        "tipo_contrato",
        "procedimiento",
        "es_menor",
        "estado",
        "resultado",
        pl.col("presupuesto").alias("presupuesto_con_iva"),
        "fecha_contrato",
        "url_origen",
        pl.lit(fecha_descarga).alias("fecha_descarga"),
    )

    # Adjudicaciones: todas las filas con adjudicatario o importe, enlazadas a su contrato.
    claves = cabeceras.select("n_contrato", "contrato_id", "url_origen")
    adjudicaciones = bruto.join(claves, on="n_contrato", how="inner").filter(
        pl.col("nif").is_not_null() | pl.col("adjudicatario").is_not_null()
    )
    adjudicaciones = adjudicaciones.with_columns(
        pl.col("fila").rank("ordinal").over("n_contrato").alias("orden")
    )
    for columna in (
        "importe_adjudicacion",
        "importe_modificaciones",
        "importe_prorrogas",
        "importe_liquidacion",
    ):
        adjudicaciones = _aplicar(adjudicaciones, columna, n_texto.importe, pl.Float64)
    adjudicaciones = _aplicar(adjudicaciones, "n_ofertas", n_texto.entero, pl.Int64)
    adjudicaciones = _identidades(adjudicaciones, sal).select(
        "contrato_id",
        pl.col("orden").cast(pl.Int32),
        "adjudicatario_id",
        "nif",
        "nombre",
        "tipo_persona",
        "n_ofertas",
        pl.col("importe_adjudicacion").alias("importe_con_iva"),
        pl.col("importe_modificaciones").alias("importe_modificaciones_con_iva"),
        pl.col("importe_prorrogas").alias("importe_prorrogas_con_iva"),
        pl.col("importe_liquidacion").alias("importe_liquidacion_con_iva"),
        pl.lit(FUENTE).alias("fuente"),
        "url_origen",
        pl.lit(fecha_descarga).alias("fecha_descarga"),
    )
    return {
        "contratos": contratos.sort("contrato_id"),
        "adjudicaciones": adjudicaciones.sort("contrato_id", "orden"),
    }
