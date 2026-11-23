"""Validación y ejecución de SQL de solo lectura para el asistente (docs/05-asistente.md).

El SQL lo escribe un modelo de lenguaje, así que se trata como no fiable. Hay tres barreras:

1. **Validación** antes de ejecutar: una sola sentencia SELECT, solo tablas de la lista
   blanca y sin funciones que lean ficheros o la configuración.
2. **Conexión** de solo lectura y sin acceso a ficheros externos (no se puede reactivar
   desde SQL una vez abierta).
3. **Resultado** acotado: límite de filas, tiempo máximo y sin seudónimos de personas
   físicas (D-007).
"""

import json
import threading
from pathlib import Path

import duckdb

# Tablas que puede consultar el asistente: las del esquema congelado (D-017), las subvenciones
# (002) y las derivadas
# de los indicadores. `contrato` no está: se usa `contrato_unico` para no contar dos veces.
TABLAS_PERMITIDAS = {
    "organo",
    "adjudicatario",
    "contrato_unico",
    "adjudicacion",
    "concesion",
    # Fondos europeos de cada licitación de PLACSP (004, D-027): contexto, no señal.
    "contrato_financiacion",
    # Encargos a medios propios (005, D-028): no son contratos licitados ni entran en señales.
    "encargo",
    "indicador_resultado",
    "puntuacion_contrato",
    "puntuacion_empresa_contrato",
    "puntuacion_organo",
    "puntuacion_organo_anio",
    "puntuacion_empresa",
    "puntuacion_empresa_anio",
    # Contratos atípicos (D-021): señal experimental, aparte de la puntuación. Las respuestas
    # deben decir que «atípico» no es «irregular» (docs/05-asistente.md).
    "anomalia_resultado",
    # Contexto de la Comunidad de Madrid (D-024, sql/esquema/003): presupuesto, convenios,
    # registros con NIF y plantilla. No son indicadores de riesgo.
    "serie_cm",
    "presupuesto_organo",
    "convenio",
    "entidad_registro",
    "plantilla_organismo",
}

# Tipos de referencia a tabla admitidos en FROM. Fuera quedan las funciones de tabla
# (read_csv…), SHOW/DESCRIBE/SUMMARIZE, PIVOT y cualquier otro.
_REFERENCIAS_PERMITIDAS = {"BASE_TABLE", "JOIN", "SUBQUERY", "EMPTY", "EXPRESSION_LIST"}

# Funciones escalares que no tienen sentido en una pregunta sobre contratos y podrían dar
# información del sistema. Las de ficheros ya fallan por la conexión, pero se rechazan antes.
_PREFIJOS_PROHIBIDOS = ("read_", "parquet_", "sniff_", "duckdb_", "pragma_", "glob", "query")
_FUNCIONES_PROHIBIDAS = {"getenv", "current_setting", "getvariable", "set_variable"}

LIMITE_FILAS = 200
SEGUNDOS_MAXIMOS = 20
SEUDONIMO_VISIBLE = "Persona física (seudonimizada)"


class SQLNoPermitido(ValueError):
    """El SQL no pasa la validación; el mensaje explica por qué (se le devuelve al modelo)."""


def conexion_lectura(ruta: Path | str) -> duckdb.DuckDBPyConnection:
    """Conexión de solo lectura y sin acceso a ficheros externos."""
    return duckdb.connect(str(ruta), read_only=True, config={"enable_external_access": False})


def _arbol(con: duckdb.DuckDBPyConnection, sql: str) -> dict:
    sentencias = con.extract_statements(sql)
    if len(sentencias) != 1:
        raise SQLNoPermitido("Se admite exactamente una sentencia SQL.")
    if sentencias[0].type != duckdb.StatementType.SELECT:
        raise SQLNoPermitido("Solo se admiten consultas SELECT (o WITH … SELECT).")
    resultado = json.loads(con.execute("SELECT json_serialize_sql(?)", [sql]).fetchone()[0])
    if resultado.get("error"):
        raise SQLNoPermitido(f"SQL no válido: {resultado.get('error_message')}")
    return resultado


def _nombres_cte(nodo: dict) -> set[str]:
    return {entrada["key"] for entrada in nodo.get("cte_map", {}).get("map", [])}


def _revisar(nodo, ctes: set[str]) -> None:
    """Recorre el árbol de la consulta y rechaza lo que no está permitido."""
    if isinstance(nodo, list):
        for hijo in nodo:
            _revisar(hijo, ctes)
        return
    if not isinstance(nodo, dict):
        return
    ctes = ctes | _nombres_cte(nodo)
    # Las referencias a tabla cuelgan de FROM o de los lados de un JOIN y, a diferencia de
    # las expresiones (que también tienen left/right), no llevan «class».
    for clave in ("from_table", "left", "right"):
        hijo = nodo.get(clave)
        es_tabla = isinstance(hijo, dict) and "class" not in hijo
        if es_tabla and hijo.get("type") not in _REFERENCIAS_PERMITIDAS:
            raise SQLNoPermitido(f"Origen de datos no permitido ({hijo.get('type')}).")
    tipo = nodo.get("type")
    if tipo == "BASE_TABLE":
        tabla = nodo["table_name"].lower()
        esquema = (nodo.get("schema_name") or "").lower()
        if nodo.get("catalog_name") or esquema not in ("", "main"):
            raise SQLNoPermitido(f"Solo se pueden consultar tablas de la base principal: {tabla}.")
        if tabla not in TABLAS_PERMITIDAS and not (esquema == "" and tabla in ctes):
            raise SQLNoPermitido(
                f"Tabla no permitida: {tabla}. Tablas disponibles: "
                + ", ".join(sorted(TABLAS_PERMITIDAS))
            )
    if nodo.get("class") == "FUNCTION":
        nombre = nodo.get("function_name", "").lower()
        if nombre in _FUNCIONES_PROHIBIDAS or nombre.startswith(_PREFIJOS_PROHIBIDOS):
            raise SQLNoPermitido(f"Función no permitida: {nombre}.")
    for valor in nodo.values():
        _revisar(valor, ctes)


def validar(con: duckdb.DuckDBPyConnection, sql: str) -> None:
    """Lanza SQLNoPermitido si el SQL no es una consulta de solo lectura permitida."""
    _revisar(_arbol(con, sql)["statements"], set())


def _ocultar_seudonimos(valor):
    if isinstance(valor, str) and "PF-" in valor:  # también «UTE:PF-…+B…»
        return SEUDONIMO_VISIBLE
    return valor


def ejecutar(
    con: duckdb.DuckDBPyConnection,
    sql: str,
    parametros: list | dict | None = None,
    limite: int = LIMITE_FILAS,
) -> dict:
    """Valida y ejecuta. Devuelve columnas, filas, si se recortó y el SQL usado (se muestra
    siempre al usuario para que pueda comprobarlo)."""
    validar(con, sql)
    temporizador = threading.Timer(SEGUNDOS_MAXIMOS, con.interrupt)
    temporizador.start()
    try:
        cursor = con.execute(sql, parametros or [])
        columnas = [d[0] for d in cursor.description]
        filas = cursor.fetchmany(limite + 1)
    except duckdb.InterruptException as error:
        raise SQLNoPermitido(f"La consulta superó {SEGUNDOS_MAXIMOS} s.") from error
    finally:
        temporizador.cancel()
    return {
        "sql": sql,
        "columnas": columnas,
        "filas": [[_ocultar_seudonimos(v) for v in fila] for fila in filas[:limite]],
        "recortado": len(filas) > limite,
    }
