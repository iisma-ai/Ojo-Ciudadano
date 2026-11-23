"""Construye la base analítica DuckDB a partir de las tablas que devuelven los módulos de ingesta.

Uso:
    uv run python -m ojo_ciudadano.modelo.carga
"""

from datetime import date
from pathlib import Path

import duckdb
import polars as pl

from ojo_ciudadano.ingesta import bdns, encargos, placsp, portal_cm, tacp
from ojo_ciudadano.normalizacion import texto as n_texto

RUTA_DB = Path("data/ojo_ciudadano.duckdb")
RUTA_ESQUEMA = Path("sql/esquema")
CARPETA_PORTAL = Path("data/raw/portal_cm")
CARPETA_PLACSP = Path("data/raw/placsp")
CARPETA_BDNS = Path("data/raw/bdns")
CARPETA_CM = Path("data/raw/cm_abiertos")  # contexto de la Comunidad (D-024)

COLUMNAS_CONTRATO = {
    "contrato_id": pl.String,
    "fuente": pl.String,
    "expediente": pl.String,
    "referencia_portal": pl.String,
    "organo_id": pl.String,
    "titulo": pl.String,
    "tipo_publicacion": pl.String,
    "tipo_contrato": pl.String,
    "procedimiento": pl.String,
    "es_menor": pl.Boolean,
    "estado": pl.String,
    "cpv": pl.String,
    "presupuesto_sin_iva": pl.Float64,
    "presupuesto_con_iva": pl.Float64,
    "valor_estimado": pl.Float64,
    "fecha_contrato": pl.Date,
    "fecha_fin_plazo": pl.Date,
    "duplicado_de": pl.String,
    "url_origen": pl.String,
    "fecha_descarga": pl.Date,
}
COLUMNAS_ENCARGO = {
    "encargo_id": pl.String,
    "orden": pl.Int32,
    "fuente": pl.String,
    "expediente": pl.String,
    "referencia_portal": pl.String,
    "organo_id": pl.String,
    "titulo": pl.String,
    "tipo_contrato": pl.String,
    "anio_publicacion": pl.Int32,
    "medio_propio_id": pl.String,
    "importe_con_iva": pl.Float64,
    "importe_modificaciones_con_iva": pl.Float64,
    "url_origen": pl.String,
    "fecha_descarga": pl.Date,
}
COLUMNAS_ADJUDICACION = {
    "contrato_id": pl.String,
    "orden": pl.Int32,
    "lote": pl.String,
    "adjudicatario_id": pl.String,
    "n_ofertas": pl.Int64,
    "resultado": pl.String,
    "importe_sin_iva": pl.Float64,
    "importe_con_iva": pl.Float64,
    "importe_modificaciones_con_iva": pl.Float64,
    "importe_prorrogas_con_iva": pl.Float64,
    "importe_liquidacion_con_iva": pl.Float64,
    "fecha_formalizacion": pl.Date,
    "fuente": pl.String,
    "url_origen": pl.String,
    "fecha_descarga": pl.Date,
}


def _con_columnas(df: pl.DataFrame, columnas: dict) -> pl.DataFrame:
    """Devuelve el DataFrame con exactamente esas columnas; las que falten quedan vacías."""
    faltan = [
        pl.lit(None, dtype=tipo).alias(c) for c, tipo in columnas.items() if c not in df.columns
    ]
    return df.with_columns(faltan).select([pl.col(c).cast(t) for c, t in columnas.items()])


def _con_organo_id(contratos: pl.DataFrame) -> pl.DataFrame:
    nombres = contratos["organo_nombre"].unique().to_list()
    claves = pl.DataFrame(
        {
            "organo_nombre": nombres,
            "organo_id": [n_texto.clave(n) or "DESCONOCIDO" for n in nombres],
        },
        schema={"organo_nombre": pl.String, "organo_id": pl.String},
    )
    return contratos.join(claves, on="organo_nombre", how="left", nulls_equal=True)


def marcar_duplicados(portal: pl.DataFrame, de_placsp: pl.DataFrame) -> pl.DataFrame:
    """Rellena `duplicado_de` en los contratos del portal que también están en PLACSP.

    Dos filas son el mismo contrato si coinciden el expediente y el órgano. Los menores no
    están en PLACSP y nunca se marcan.
    """
    claves = de_placsp.select(
        "expediente", "organo_id", pl.col("contrato_id").alias("duplicado_de")
    ).unique(["expediente", "organo_id"], keep="first")
    cruzado = portal.join(claves, on=["expediente", "organo_id"], how="left")
    return cruzado.with_columns(
        pl.when(pl.col("es_menor"))
        .then(None)
        .otherwise(pl.col("duplicado_de"))
        .alias("duplicado_de")
    )


def unificar(
    tablas_portal: list[dict],
    tablas_placsp: dict | None,
    tablas_bdns: dict | None = None,
    tablas_encargos: dict | None = None,
) -> dict[str, pl.DataFrame]:
    """Combina las tablas de las fuentes en las tablas del esquema. Las subvenciones (BDNS) y
    los encargos a medios propios son opcionales: añaden `concesion` y `encargo`, con sus
    órganos y sus beneficiarios o medios propios."""
    c_portal = pl.concat([t["contratos"] for t in tablas_portal]).unique(
        "contrato_id", keep="first"
    )
    a_portal = pl.concat([t["adjudicaciones"] for t in tablas_portal]).unique(
        ["contrato_id", "orden"], keep="first"
    )
    c_portal = _con_organo_id(c_portal).rename({"referencia": "referencia_portal"})
    crudos_contratos = [c_portal]
    crudos_adjudicaciones = [a_portal]

    if tablas_placsp is not None:
        c_placsp = _con_organo_id(tablas_placsp["contratos"])
        c_portal = marcar_duplicados(c_portal, c_placsp)
        crudos_contratos = [c_placsp, c_portal]
        crudos_adjudicaciones = [tablas_placsp["adjudicaciones"], a_portal]
    e_portal = _con_organo_id(tablas_encargos["encargos"]) if tablas_encargos else None

    organos = (
        pl.concat(
            [
                c.select(
                    "organo_id",
                    pl.col("organo_nombre").alias("nombre"),
                    "consejeria",
                    pl.col("organo_jerarquia").alias("jerarquia"),
                    (
                        pl.col("organo_codigo")
                        if "organo_codigo" in c.columns
                        else pl.lit(None, dtype=pl.String)
                    ).alias("codigo_placsp"),
                )
                for c in crudos_contratos + ([e_portal] if e_portal is not None else [])
            ]
            + _organos_bdns(tablas_bdns)
        )
        .group_by("organo_id", maintain_order=True)
        .agg(
            pl.col("nombre").drop_nulls().first(),
            pl.col("consejeria").drop_nulls().first(),
            pl.col("jerarquia").drop_nulls().first(),
            pl.col("codigo_placsp").drop_nulls().first(),
        )
        .with_columns(pl.col("nombre").fill_null("Desconocido"))
        .sort("organo_id")
    )
    adjudicatarios = (
        pl.concat(
            [
                a.select("adjudicatario_id", "nif", "nombre", "tipo_persona")
                for a in crudos_adjudicaciones
            ]
            + ([tablas_bdns["beneficiarios"]] if tablas_bdns else [])
            + ([tablas_encargos["medios_propios"]] if tablas_encargos else [])
        )
        .filter(pl.col("adjudicatario_id").is_not_null())
        .group_by("adjudicatario_id", maintain_order=True)
        .agg(
            pl.col("nif").first(),
            pl.col("nombre").drop_nulls().first(),
            pl.col("tipo_persona").first(),
        )
        .sort("adjudicatario_id")
    )
    concesiones = tablas_bdns["concesiones"] if tablas_bdns else None
    return {
        "contrato_financiacion": _financiacion(tablas_placsp),
        "contrato_documento": _documentos(tablas_placsp),
        "encargo": _con_columnas(e_portal, COLUMNAS_ENCARGO) if e_portal is not None else None,
        "organo": organos,
        "adjudicatario": adjudicatarios,
        "concesion": concesiones,
        "contrato": pl.concat([_con_columnas(c, COLUMNAS_CONTRATO) for c in crudos_contratos]),
        "adjudicacion": pl.concat(
            [_con_columnas(a, COLUMNAS_ADJUDICACION) for a in crudos_adjudicaciones]
        ),
    }


def _financiacion(tablas_placsp: dict | None) -> pl.DataFrame | None:
    """Contratos de PLACSP que dicen si tienen fondos europeos (004_financiacion_ue.sql)."""
    if tablas_placsp is None or "financiado_ue" not in tablas_placsp["contratos"].columns:
        return None
    return (
        tablas_placsp["contratos"]
        .filter(pl.col("financiado_ue").is_not_null())
        .select(
            "contrato_id",
            "financiado_ue",
            "programas_ue",
            "fuente",
            "url_origen",
            "fecha_descarga",
        )
    )


def _documentos(tablas_placsp: dict | None) -> pl.DataFrame | None:
    """Pliegos enlazados en cada licitación de PLACSP (007_documentos.sql)."""
    if tablas_placsp is None:
        return None
    return tablas_placsp.get("documentos")


def _expediente(columna: pl.Expr) -> pl.Expr:
    """Expediente comparable: mayúsculas y sin espacios."""
    return columna.str.to_uppercase().str.replace_all(r"\s", "")


MIN_TITULO = 25  # caracteres: títulos más cortos («Servicio de limpieza») se repiten


def _unicos(contratos: pl.DataFrame, clave: pl.Expr) -> pl.DataFrame:
    """Claves que corresponden a un único contrato (sin menores ni duplicados del portal)."""
    return (
        contratos.filter(~pl.col("es_menor") & pl.col("duplicado_de").is_null())
        .select("contrato_id", clave.alias("clave"))
        .filter(pl.col("clave").is_not_null())
        .group_by("clave")
        .agg(pl.col("contrato_id").first(), pl.len().alias("n"))
        .filter(pl.col("n") == 1)
        .drop("n")
    )


def _clave_titulo(columna: pl.Expr) -> pl.Expr:
    """Título comparable: mayúsculas, sin tildes ni signos; vacío si es demasiado corto."""
    clave = columna.map_elements(n_texto.clave, return_dtype=pl.String)
    return pl.when(clave.str.len_chars() >= MIN_TITULO).then(clave)


def cruzar_recursos(recursos: pl.DataFrame, contratos: pl.DataFrame) -> pl.DataFrame:
    """Enlaza cada resolución con su contrato, solo si todo apunta a un único contrato (sin
    contar los menores ni las filas del portal que duplican una de PLACSP):

    - por el expediente que cita su resumen o su PDF (`expedientes_citados`), y
    - si la tabla trae `titulos_citados` (texto entre comillas del encabezamiento del PDF,
      `tacp.con_texto_pdf`), por el título exacto del contrato, de `MIN_TITULO` caracteres
      o más, una vez normalizado.

    Si no casa o es ambiguo (dos contratos distintos), `contrato_id` queda vacío.
    `expediente_citado` solo se rellena cuando casa un expediente."""
    por_expediente = (
        recursos.select("resolucion_id", "expedientes_citados")
        .explode("expedientes_citados")
        .with_columns(_expediente(pl.col("expedientes_citados")).alias("clave"))
        .join(_unicos(contratos, _expediente(pl.col("expediente"))), on="clave", how="inner")
        .select(
            "resolucion_id", pl.col("expedientes_citados").alias("expediente_citado"), "contrato_id"
        )
    )
    por_titulo = por_expediente.clear()
    if "titulos_citados" in recursos.columns and "titulo" in contratos.columns:
        por_titulo = (
            recursos.select("resolucion_id", "titulos_citados")
            .explode("titulos_citados")
            .with_columns(_clave_titulo(pl.col("titulos_citados")).alias("clave"))
            .join(_unicos(contratos, _clave_titulo(pl.col("titulo"))), on="clave", how="inner")
            .select(
                "resolucion_id",
                pl.lit(None, dtype=pl.String).alias("expediente_citado"),
                "contrato_id",
            )
        )
    candidatos = (
        pl.concat([por_expediente, por_titulo])
        .group_by("resolucion_id", maintain_order=True)
        .agg(
            pl.col("expediente_citado").drop_nulls().first(),
            pl.col("contrato_id").unique().alias("contratos"),
        )
        .with_columns(
            pl.when(pl.col("contratos").list.len() == 1)
            .then(pl.col("contratos").list.first())
            .alias("contrato_id")
        )
        .drop("contratos")
    )
    sobran = [c for c in ("expedientes_citados", "titulos_citados") if c in recursos.columns]
    return recursos.join(candidatos, on="resolucion_id", how="left").drop(sobran)


def _organos_bdns(tablas_bdns: dict | None) -> list[pl.DataFrame]:
    """Órganos de la BDNS con las mismas columnas que los de contratos. Van detrás, así que
    si el órgano ya existe en los contratos se conserva su nombre y su consejería."""
    if not tablas_bdns:
        return []
    return [
        tablas_bdns["organos"].with_columns(
            pl.lit(None, dtype=pl.String).alias("consejeria"),
            pl.lit(None, dtype=pl.String).alias("jerarquia"),
            pl.lit(None, dtype=pl.String).alias("codigo_placsp"),
        )
    ]


def escribir(
    tablas: dict[str, pl.DataFrame], ruta_db: Path = RUTA_DB, ruta_esquema: Path = RUTA_ESQUEMA
) -> None:
    """Crea la base desde cero con el DDL de `sql/esquema/` y carga las cuatro tablas."""
    ruta_db.parent.mkdir(parents=True, exist_ok=True)
    ruta_db.unlink(missing_ok=True)
    con = duckdb.connect(str(ruta_db))
    try:
        for ddl in sorted(ruta_esquema.glob("*.sql")):
            con.execute(ddl.read_text(encoding="utf-8"))
        for nombre in (
            "organo",
            "adjudicatario",
            "contrato",
            "adjudicacion",
            "concesion",
            "contrato_financiacion",
            "contrato_documento",
            "encargo",
            "recurso_especial",
        ):
            if tablas.get(nombre) is None:
                continue
            df = tablas[nombre].to_arrow()  # noqa: F841 (DuckDB lo lee por su nombre)
            con.execute(f"INSERT INTO {nombre} BY NAME SELECT * FROM df")
    finally:
        con.close()


def _fecha_fichero(ruta: Path) -> date:
    """Fecha de descarga de un fichero bruto: la de su última modificación."""
    return date.fromtimestamp(ruta.stat().st_mtime)


def construir(
    carpeta_portal: Path = CARPETA_PORTAL,
    carpeta_placsp: Path = CARPETA_PLACSP,
    carpeta_bdns: Path = CARPETA_BDNS,
    ruta_db: Path = RUTA_DB,
    carpeta_cm: Path | None = None,
    carpeta_tacp: Path = tacp.CARPETA,
) -> dict[str, pl.DataFrame]:
    """Lee los ficheros brutos y regenera la base analítica. Con `carpeta_cm` carga además el
    contexto de la Comunidad de Madrid (presupuesto, convenios, registros; D-024)."""
    csv_portal = sorted(carpeta_portal.glob("*.csv"))
    if not csv_portal:
        raise FileNotFoundError(
            f"No hay CSV del portal en {carpeta_portal} (ver docs/02-fuentes-datos.md)"
        )
    tablas_portal = [portal_cm.leer(f, _fecha_fichero(f)) for f in csv_portal]
    zips = sorted(carpeta_placsp.glob("*.zip"))
    tablas_placsp = placsp.leer_zips(zips, max(_fecha_fichero(z) for z in zips)) if zips else None
    meses_bdns = sorted(carpeta_bdns.glob("*.json"))
    tablas_bdns = (
        bdns.leer(meses_bdns, max(_fecha_fichero(m) for m in meses_bdns)) if meses_bdns else None
    )
    ruta_encargos = encargos.fichero()
    tablas_encargos = (
        encargos.leer(ruta_encargos, _fecha_fichero(ruta_encargos)) if ruta_encargos else None
    )
    tablas = unificar(tablas_portal, tablas_placsp, tablas_bdns, tablas_encargos)
    if any(carpeta_tacp.glob("*.html")):
        recursos = tacp.leer(carpeta_tacp, _fecha_fichero(max(carpeta_tacp.glob("*.html"))))
        # Con los PDF ya bajados (`tacp --pdf`), también los expedientes y títulos de su
        # encabezamiento (D-030, bloque C). Sin ellos, solo el resumen del listado.
        tablas["recurso_especial"] = cruzar_recursos(
            tacp.con_texto_pdf(recursos), tablas["contrato"]
        )
    escribir(tablas, ruta_db)
    if carpeta_cm is not None and any(carpeta_cm.glob("*.csv")):
        from ojo_ciudadano.modelo import contexto

        contexto.cargar(ruta_db, carpeta_cm)
    return tablas


if __name__ == "__main__":
    for nombre, tabla in construir(carpeta_cm=CARPETA_CM).items():
        if tabla is not None:
            print(f"{nombre}: {tabla.height} filas")
