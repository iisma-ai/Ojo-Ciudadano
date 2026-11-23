"""Encargos a medios propios del Portal de la Contratación Pública de la Comunidad de Madrid.

Un encargo es un trabajo que un órgano asigna sin licitación a una entidad del sector público
que actúa como su medio propio (Tragsa, Canal de Isabel II…), art. 32 de la Ley 9/2017. Es un
flujo de dinero aparte de los contratos: va a su propia tabla, `encargo`, y no entra en los
indicadores de riesgo (D-028).

Fichero: `data/raw/encargos/encargos_todo_AAAA-MM-DD.csv`, exportación CSV del buscador con
«Encargos a medios propios» (se baja a mano: la exportación tiene captcha). Tiene el mismo
formato que el resto de CSV del portal, pero **no trae ninguna fecha**.

Año de publicación: la referencia del portal (`C<número>`) crece con la fecha de publicación.
El 23-nov-2026 se comprobó en el buscador, filtrando por «Fecha de publicación en el Portal»
año a año, que estos tramos dan exactamente los mismos encargos (236, 226, 260 y 222). Las
referencias sin la forma `C<número>` son de años anteriores.
"""

from datetime import date
from pathlib import Path

import polars as pl

from ojo_ciudadano.ingesta import portal_cm

CARPETA = Path("data/raw/encargos")
# Año de publicación → (primera, última) referencia numérica publicada ese año.
LIMITES_REFERENCIA = {
    2023: (276, 3789),
    2024: (3886, 7818),
    2025: (7833, 11886),
    2026: (11940, 10**9),  # 2026 sigue abierto: todo lo posterior a la primera de 2026
}


def anio_publicacion(referencia: pl.Expr) -> pl.Expr:
    """Año de publicación según la referencia del portal; nulo fuera de 2023–2026."""
    numero = referencia.str.extract(r"^C(\d+)$").cast(pl.Int64)
    anio = pl.lit(None, dtype=pl.Int32)
    for a, (desde, hasta) in LIMITES_REFERENCIA.items():
        anio = (
            pl.when(numero.is_between(desde, hasta)).then(pl.lit(a, dtype=pl.Int32)).otherwise(anio)
        )
    return anio


def leer(ruta: Path, fecha_descarga: date, sal: bytes | None = None) -> dict:
    """Devuelve `encargos` (una fila por encargo y medio propio, solo 2023–2026) y
    `medios_propios` (identidades con las columnas de `adjudicatario`)."""
    tablas = portal_cm.leer(ruta, fecha_descarga, sal)
    encargos = (
        tablas["contratos"]
        .with_columns(anio_publicacion(pl.col("referencia")).alias("anio_publicacion"))
        .filter(pl.col("anio_publicacion").is_not_null())
        .join(
            tablas["adjudicaciones"].drop("fuente", "url_origen", "fecha_descarga"),
            on="contrato_id",
            how="left",
        )
        .select(
            pl.col("contrato_id").alias("encargo_id"),
            "fuente",
            "expediente",
            pl.col("referencia").alias("referencia_portal"),
            "organo_nombre",
            "organo_jerarquia",
            "consejeria",
            "titulo",
            "tipo_contrato",
            "anio_publicacion",
            "orden",
            pl.col("adjudicatario_id").alias("medio_propio_id"),
            "nif",
            "nombre",
            "tipo_persona",
            "importe_con_iva",
            "importe_modificaciones_con_iva",
            "url_origen",
            "fecha_descarga",
        )
        # Un encargo sin medio propio en el CSV se queda con una fila (orden 1).
        .with_columns(pl.col("orden").fill_null(1))
        .sort("encargo_id", "orden")
    )
    medios_propios = encargos.select(
        pl.col("medio_propio_id").alias("adjudicatario_id"), "nif", "nombre", "tipo_persona"
    ).filter(pl.col("adjudicatario_id").is_not_null())
    return {"encargos": encargos, "medios_propios": medios_propios}


def fichero(carpeta: Path = CARPETA) -> Path | None:
    """La exportación de encargos más reciente, o None si no hay ninguna."""
    csv = sorted(carpeta.glob("encargos_todo_*.csv"))
    return csv[-1] if csv else None
