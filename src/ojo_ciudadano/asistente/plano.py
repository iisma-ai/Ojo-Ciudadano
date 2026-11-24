"""Plano de una consulta SQL: qué tablas lee, cómo las une y qué pasos sigue (D-037).

Sirve para la animación del asistente mientras se ejecuta la consulta: se ve qué datos se
están juntando. Sale del árbol de la consulta que da DuckDB (`json_serialize_sql`), el mismo
que usa el validador, así que no ejecuta nada.
"""

from dataclasses import dataclass, field

import duckdb

from ojo_ciudadano.asistente import sql_seguro

# Nombre llano de las tablas más consultadas.
DESCRIPCION = {
    "contrato_unico": "contratos",
    "contrato": "contratos",
    "adjudicacion": "adjudicaciones",
    "adjudicatario": "empresas y entidades",
    "organo": "organismos",
    "indicador_resultado": "señales calculadas",
    "puntuacion_contrato": "puntuación por contrato",
    "puntuacion_organo": "puntuación por organismo",
    "puntuacion_organo_anio": "puntuación por organismo y año",
    "puntuacion_empresa": "puntuación por empresa",
    "puntuacion_empresa_anio": "puntuación por empresa y año",
    "puntuacion_empresa_contrato": "contratos de cada empresa",
    "concesion": "subvenciones",
    "recurso_especial": "recursos ante el Tribunal",
    "cpv": "códigos CPV",
    "entidad_sector_publico": "entes públicos (INVENTE)",
    "anomalia_resultado": "contratos atípicos",
    "anomalia_variables": "variables de los atípicos",
    "anomalia_encargo": "encargos atípicos",
    "anomalia_validacion": "comprobación de los atípicos",
    "contrato_financiacion": "fondos europeos",
    "encargo": "encargos a medios propios",
    "contrato_documento": "pliegos",
}


@dataclass
class Plano:
    tablas: list[str] = field(default_factory=list)  # en orden de aparición, sin repetir
    intermedias: list[str] = field(default_factory=list)  # cálculos intermedios (WITH)
    uniones: list[tuple[str, str, str]] = field(default_factory=list)  # (tabla, tabla, clave)
    pasos: list[str] = field(default_factory=list)


def _origenes(nodo, alias: dict[str, str]) -> list[str]:
    """Tablas (o cálculos intermedios) de un lado de un JOIN, registrando sus alias."""
    if not isinstance(nodo, dict):
        return []
    if nodo.get("type") == "BASE_TABLE":
        nombre = nodo["table_name"].lower()
        if nodo.get("alias"):
            alias[nodo["alias"].lower()] = nombre
        return [nombre]
    if nodo.get("type") == "JOIN":
        return _origenes(nodo.get("left"), alias) + _origenes(nodo.get("right"), alias)
    return []


def _columnas(nodo) -> list[list[str]]:
    """Referencias a columna dentro de una condición."""
    if isinstance(nodo, list):
        return [c for hijo in nodo for c in _columnas(hijo)]
    if not isinstance(nodo, dict):
        return []
    if nodo.get("class") == "COLUMN_REF":
        return [nodo["column_names"]]
    return [c for valor in nodo.values() for c in _columnas(valor)]


def _tiene_columna(con, tabla: str, columna: str) -> bool:
    return bool(
        con.execute(
            "SELECT count(*) FROM information_schema.columns "
            "WHERE table_name = ? AND column_name = ?",
            [tabla, columna],
        ).fetchone()[0]
    )


def _union(con, nodo: dict, alias: dict[str, str]) -> tuple[str, str, str] | None:
    """(tabla de la izquierda, tabla de la derecha, clave) de un JOIN. La tabla de la
    izquierda es la que tiene la clave: la del alias en un ON, o la última que tiene esa
    columna en un USING."""
    izquierda = _origenes(nodo.get("left"), alias)
    derecha = _origenes(nodo.get("right"), alias)
    if not izquierda or not derecha:
        return None
    if nodo.get("join_type") == "CROSS" or nodo.get("ref_type") == "CROSS":
        return izquierda[-1], derecha[0], "todas las combinaciones"
    if nodo.get("using_columns"):
        clave = nodo["using_columns"][0]
        con_clave = [t for t in izquierda if _tiene_columna(con, t, clave)]
        return (con_clave or izquierda)[-1], derecha[0], ", ".join(nodo["using_columns"])
    columnas = _columnas(nodo.get("condition"))
    if not columnas:
        return izquierda[-1], derecha[0], "condición"
    clave = ", ".join(dict.fromkeys(c[-1] for c in columnas))
    tablas = [alias.get(c[0].lower(), c[0].lower()) for c in columnas if len(c) > 1]
    otra = next((t for t in tablas if t in izquierda), izquierda[-1])
    return otra, derecha[0], clave


def _recorrer(con, nodo, plano: Plano, alias: dict[str, str]) -> None:
    if isinstance(nodo, list):
        for hijo in nodo:
            _recorrer(con, hijo, plano, alias)
        return
    if not isinstance(nodo, dict):
        return
    for entrada in nodo.get("cte_map", {}).get("map", []):
        if entrada["key"] not in plano.intermedias:
            plano.intermedias.append(entrada["key"])
    if nodo.get("type") == "BASE_TABLE":
        nombre = nodo["table_name"].lower()
        if nombre not in plano.tablas:
            plano.tablas.append(nombre)
    for valor in nodo.values():  # primero lo de dentro: las uniones salen en su orden
        _recorrer(con, valor, plano, alias)
    if nodo.get("type") == "JOIN":
        union = _union(con, nodo, alias)
        if union and union not in plano.uniones:
            plano.uniones.append(union)


def _limite(nodo: dict) -> int | None:
    for modificador in nodo.get("modifiers") or []:
        if modificador.get("type") == "LIMIT_MODIFIER":
            literal = (modificador.get("limit") or {}).get("literal") or {}
            try:
                return int(literal.get("text"))
            except (TypeError, ValueError):
                return None
    return None


def _pasos(nodo: dict, plano: Plano) -> list[str]:
    pasos = [f"Preparar el cálculo intermedio «{n}»" for n in plano.intermedias]
    reales = [t for t in plano.tablas if t not in plano.intermedias]
    if reales:
        pasos.append("Leer " + ", ".join(reales))
    for a, b, clave in plano.uniones:
        pasos.append(f"Unir {a} con {b} por {clave}")
    if nodo.get("where_clause"):
        pasos.append("Filtrar las filas que cumplen la pregunta")
    if nodo.get("group_expressions"):
        pasos.append("Agrupar y sumar")
    if any(m.get("type") == "ORDER_MODIFIER" for m in nodo.get("modifiers") or []):
        pasos.append("Ordenar el resultado")
    limite = _limite(nodo)
    if limite:
        pasos.append(f"Quedarse con las {limite} primeras filas")
    return pasos


def plano_consulta(con: duckdb.DuckDBPyConnection, sql: str) -> Plano:
    """Plano de la consulta. Si el SQL no se puede leer, un plano vacío (la animación es
    solo una ayuda: nunca debe impedir la respuesta)."""
    try:
        arbol = sql_seguro._arbol(con, sql)
    except (sql_seguro.SQLNoPermitido, duckdb.Error):
        return Plano(pasos=["Consultar la base de datos"])
    plano = Plano()
    _recorrer(con, arbol["statements"], plano, {})
    principal = arbol["statements"][0]["node"] if arbol["statements"] else {}
    plano.pasos = _pasos(principal, plano)
    return plano
