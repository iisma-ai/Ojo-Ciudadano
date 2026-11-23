"""Descarga, carga y comprobación del contexto de la Comunidad de Madrid (D-024).

Un solo comando para todo el equipo:
    uv run python -m ojo_ciudadano.modelo.contexto

1. Baja lo que falta de `data/raw/cm_abiertos/` (catálogo de datos abiertos y Portal de
   Transparencia).
2. Carga las cinco tablas nuevas en `data/ojo_ciudadano.duckdb` SIN tocar las demás: no hace
   falta regenerar contratos ni indicadores. Cierra la interfaz antes: DuckDB no deja escribir
   con la base abierta.
3. Compara lo cargado con `docs/datos-cm-referencia.json` e imprime si coincide con lo que
   tiene el resto del equipo.

Opciones: `--forzar` (volver a bajar todo), `--sin-descarga` (solo cargar),
`--escribir-referencia` (reescribe la referencia; solo quien amplía las fuentes).
"""

import json
import sys
from pathlib import Path

import duckdb

from ojo_ciudadano.ingesta import cm_abiertos, cm_contexto

RUTA_DB = Path("data/ojo_ciudadano.duckdb")
RUTA_DDL = Path("sql/esquema/003_contexto_cm.sql")
RUTA_REFERENCIA = Path("docs/datos-cm-referencia.json")
# Orden de borrado: ninguna depende de otra, pero todas dependen de `organo`.
TABLAS = ("serie_cm", "presupuesto_organo", "convenio", "entidad_registro", "plantilla_organismo")


def cargar(
    ruta_db: Path = RUTA_DB,
    carpeta: Path = cm_abiertos.CARPETA,
    ruta_ddl: Path = RUTA_DDL,
) -> dict[str, int]:
    """Crea de nuevo las tablas del contexto y las rellena. Devuelve las filas de cada una."""
    con = duckdb.connect(str(ruta_db))
    try:
        organos = {f[0] for f in con.execute("SELECT organo_id FROM organo").fetchall()}
        tablas = cm_contexto.leer_todo(carpeta, organos)
        for nombre in TABLAS:
            con.execute(f"DROP TABLE IF EXISTS {nombre}")
        con.execute(ruta_ddl.read_text(encoding="utf-8"))
        for nombre in TABLAS:
            df = tablas[nombre].to_arrow()  # noqa: F841 (DuckDB lo lee por su nombre)
            con.execute(f"INSERT INTO {nombre} BY NAME SELECT * FROM df")
        return {n: con.execute(f"SELECT count(*) FROM {n}").fetchone()[0] for n in TABLAS}
    finally:
        con.close()


def huellas(manifiesto: dict) -> dict[str, str]:
    return {nombre: datos["sha256"] for nombre, datos in sorted(manifiesto.items())}


def escribir_referencia(filas: dict[str, int], manifiesto: dict) -> None:
    referencia = {
        "nota": "Estado del contexto de la Comunidad de Madrid al descargarlo. Si cambian las "
        "fuentes, las huellas y los recuentos pueden diferir: no es un error, apúntalo.",
        "tablas": filas,
        "ficheros": huellas(manifiesto),
    }
    RUTA_REFERENCIA.write_text(
        json.dumps(referencia, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )


def comparar(filas: dict[str, int], manifiesto: dict) -> list[str]:
    """Diferencias con la referencia del equipo (lista vacía si todo coincide)."""
    if not RUTA_REFERENCIA.exists():
        return ["No existe docs/datos-cm-referencia.json"]
    ref = json.loads(RUTA_REFERENCIA.read_text(encoding="utf-8"))
    avisos = [
        f"tabla {t}: {filas.get(t)} filas, la referencia tiene {n}"
        for t, n in ref["tablas"].items()
        if filas.get(t) != n
    ]
    propias = huellas(manifiesto)
    avisos += [
        f"fichero {f}: huella distinta (la fuente se habrá actualizado)"
        for f, h in ref["ficheros"].items()
        if propias.get(f) != h
    ]
    return avisos


if __name__ == "__main__":
    args = sys.argv[1:]
    manifiesto = (
        cm_abiertos.leer_manifiesto()
        if "--sin-descarga" in args
        else cm_abiertos.descargar(forzar="--forzar" in args)
    )
    filas = cargar()
    for tabla, n in filas.items():
        print(f"{tabla}: {n} filas")
    if "--escribir-referencia" in args:
        escribir_referencia(filas, manifiesto)
        print(f"Referencia escrita en {RUTA_REFERENCIA}")
    else:
        diferencias = comparar(filas, manifiesto)
        print(
            "Coincide con la referencia del equipo." if not diferencias else "\n".join(diferencias)
        )
