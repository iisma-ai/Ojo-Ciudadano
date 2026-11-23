"""Contratos atípicos respecto a contratos similares (D-021).

Señal complementaria a los indicadores con reglas: un Isolation Forest (no supervisado, sin
etiquetas) busca, dentro de cada grupo de contratos parecidos, los que se alejan de sus pares.
No entra en la puntuación de riesgo (D-020) hasta validarla. «Atípico» no es «irregular»: puede
haber explicaciones legítimas (un contrato grande, un mercado con un único proveedor posible…).

Grupo de pares = fuente + licitación o menor + tipo de contrato. Se separa por fuente porque
PLACSP da importes sin IVA y el portal regional con IVA (nunca se mezclan bases).

Variables (todas ya están en la base):
  * importe adjudicado (en escala logarítmica),
  * número de ofertas (solo licitaciones),
  * baja sobre el presupuesto base (solo licitaciones, misma base de IVA),
  * modificaciones sobre el importe adjudicado (solo portal regional),
  * cuota del adjudicatario en el importe del órgano para ese tipo de contrato,
  * nº de menores del mismo adjudicatario y órgano en los 12 meses anteriores (solo menores).

Cada contrato atípico se explica con las variables en las que más se aleja de la mediana de su
grupo (desviación robusta). Reproducible: semilla fija y parámetros en este fichero.

Datos de D-027 a D-029 (D-031):
  * Encargos a medios propios (D-028): no son contratos licitados, así que no se mezclan con
    ellos; forman su propio grupo de pares («portal_cm · encargo») con importe, modificaciones
    y cuota del medio propio en lo que encarga el órgano. Resultado aparte: `anomalia_encargo`.
    * Recursos ante el TACPCM (D-029) y fondos europeos (D-027): **no son variables**. En un
    recurso estimado el Tribunal dio la razón, total o parcialmente, a quien recurrió el acto:
    **validar** la señal (¿hay más atípicos entre los contratos con recurso estimado?), y
    usarlo como variable haría que el modelo solo aprendiera a marcar los recurridos. Los
    fondos europeos no indican nada sobre el riesgo. Ambos van a `anomalia_validacion`.

Uso: uv run python -m ojo_ciudadano.anomalias.deteccion
"""

from pathlib import Path

import duckdb
import numpy as np
import polars as pl
from sklearn.ensemble import IsolationForest

RAIZ = Path(__file__).resolve().parents[3]
RUTA_DB = RAIZ / "data" / "ojo_ciudadano.duckdb"

SEMILLA = 42
PROPORCION_ATIPICOS = 0.01  # el 1 % más alejado de cada grupo
MIN_GRUPO = 50  # con menos contratos no hay pares suficientes para comparar
N_ARBOLES = 200
MAX_VARIABLES_MOTIVO = 2
MIN_DESVIACION_MOTIVO = 2.0  # desviación robusta mínima para citar una variable en el motivo

VARIABLES = ["importe", "n_ofertas", "baja", "modificaciones", "cuota", "menores_12m"]

COLUMNAS = [
    "contrato_id",
    "grupo",
    "n_grupo",
    "puntuacion",
    "atipico",
    "variables",
    "motivo",
    "url_origen",
]

CONSULTA_VARIABLES = """
WITH adjudicaciones AS (
    SELECT
        c.contrato_id, c.fuente, c.es_menor, c.tipo_contrato, c.organo_id, c.url_origen,
        c.fecha_contrato,
        CASE WHEN c.fuente = 'placsp' THEN c.presupuesto_sin_iva
             ELSE c.presupuesto_con_iva END AS presupuesto,
        a.adjudicatario_id,
        CASE WHEN c.fuente = 'placsp' THEN a.importe_sin_iva ELSE a.importe_con_iva END AS importe,
        a.n_ofertas,
        a.importe_modificaciones_con_iva AS modificaciones
    FROM contrato_unico AS c
    JOIN adjudicacion AS a USING (contrato_id)
    WHERE c.tipo_contrato IS NOT NULL
      AND (a.resultado IS NULL OR a.resultado IN ('Adjudicado', 'Formalizado'))
),

por_empresa AS (
    SELECT fuente, organo_id, tipo_contrato, adjudicatario_id, sum(importe) AS importe
    FROM adjudicaciones
    WHERE adjudicatario_id IS NOT NULL AND importe > 0
    GROUP BY ALL
),

cuotas AS (
    SELECT fuente, organo_id, tipo_contrato, adjudicatario_id,
           importe / sum(importe) OVER (PARTITION BY fuente, organo_id, tipo_contrato) AS cuota
    FROM por_empresa
),

menores AS (
    SELECT
        contrato_id,
        count(*) OVER (
            PARTITION BY organo_id, adjudicatario_id ORDER BY fecha_contrato
            RANGE BETWEEN INTERVAL 365 DAYS PRECEDING AND CURRENT ROW
        ) AS menores_12m
    FROM adjudicaciones
    WHERE es_menor AND adjudicatario_id IS NOT NULL AND fecha_contrato IS NOT NULL
)

SELECT
    a.contrato_id,
    a.fuente || ' · ' || CASE WHEN a.es_menor THEN 'menor' ELSE 'licitación' END
        || ' · ' || lower(a.tipo_contrato) AS grupo,
    any_value(a.es_menor) AS es_menor,
    any_value(a.url_origen) AS url_origen,
    sum(a.importe) AS importe,
    min(a.n_ofertas) AS n_ofertas,
    CASE WHEN any_value(a.presupuesto) > 0 AND sum(a.importe) > 0
         THEN 1 - sum(a.importe) / any_value(a.presupuesto) END AS baja,
    CASE WHEN sum(a.importe) > 0 THEN sum(a.modificaciones) / sum(a.importe) END
        AS modificaciones,
    max(q.cuota) AS cuota,
    max(m.menores_12m) AS menores_12m
FROM adjudicaciones AS a
LEFT JOIN cuotas AS q USING (fuente, organo_id, tipo_contrato, adjudicatario_id)
LEFT JOIN menores AS m USING (contrato_id)
GROUP BY a.contrato_id, a.fuente, a.es_menor, a.tipo_contrato
HAVING sum(a.importe) > 0
"""


CONSULTA_ENCARGOS = """
WITH encargos AS (
    SELECT encargo_id, any_value(organo_id) AS organo_id, any_value(url_origen) AS url_origen,
           arg_min(medio_propio_id, orden) AS medio_propio_id,
           sum(importe_con_iva) AS importe,
           sum(importe_modificaciones_con_iva) AS modificaciones
    FROM encargo
    GROUP BY encargo_id
    HAVING sum(importe_con_iva) > 0
),
por_medio AS (
    SELECT organo_id, medio_propio_id, sum(importe) AS importe
    FROM encargos
    WHERE medio_propio_id IS NOT NULL
    GROUP BY 1, 2
),
cuotas AS (
    SELECT organo_id, medio_propio_id,
           importe / sum(importe) OVER (PARTITION BY organo_id) AS cuota
    FROM por_medio
)
SELECT e.encargo_id AS contrato_id, 'portal_cm · encargo' AS grupo, false AS es_menor,
       e.url_origen, e.importe, NULL::INTEGER AS n_ofertas, NULL::DOUBLE AS baja,
       e.modificaciones / e.importe AS modificaciones, q.cuota, NULL::BIGINT AS menores_12m
FROM encargos AS e
LEFT JOIN cuotas AS q USING (organo_id, medio_propio_id)
"""


def _hay_tabla(con: duckdb.DuckDBPyConnection, tabla: str) -> bool:
    return bool(
        con.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_name = ?", [tabla]
        ).fetchall()[0][0]
    )


def leer_encargos(con: duckdb.DuckDBPyConnection) -> pl.DataFrame:
    """Una fila por encargo con las variables que tienen sentido para un encargo."""
    if not _hay_tabla(con, "encargo"):
        return pl.DataFrame()
    return con.sql(CONSULTA_ENCARGOS).pl().sort("contrato_id")


def _texto_encargo(motivo: str | None) -> str | None:
    """El motivo habla de contratos y adjudicatarios; en un encargo son encargos y medios
    propios, y el importe es el del encargo."""
    if motivo is None:
        return None
    cambios = {
        "contratos similares": "encargos similares",
        "cuota del adjudicatario en lo que adjudica este órgano en este tipo de contrato": (
            "cuota del medio propio en lo que encarga este órgano"
        ),
        "importe adjudicado": "importe del encargo",
    }
    for viejo, nuevo in cambios.items():
        # `explicar` pone en mayúscula la primera letra del motivo: también esa forma.
        motivo = motivo.replace(viejo, nuevo).replace(viejo.capitalize(), nuevo.capitalize())
    return motivo


def calcular_encargos(con: duckdb.DuckDBPyConnection) -> pl.DataFrame:
    """Encargos atípicos respecto a los demás encargos, en `anomalia_encargo`."""
    datos = leer_encargos(con)
    resultado = puntuar_grupo(datos) if datos.height else pl.DataFrame(schema=_esquema())
    resultado = resultado.with_columns(
        pl.col("motivo").map_elements(_texto_encargo, return_dtype=pl.String)
    ).rename({"contrato_id": "encargo_id"})
    tabla = resultado.to_arrow()  # noqa: F841 (DuckDB lo lee por su nombre)
    con.execute("CREATE OR REPLACE TABLE anomalia_encargo AS SELECT * FROM tabla")
    return resultado


# Grupos de la validación: (nombre, condición sobre el contrato `r`). Solo se calculan los que
# tienen sus tablas en la base.
VALIDACION = [
    ("Todos los contratos analizados", None, "TRUE"),
    (
        "Con algún recurso estimado (total o parcial) ante el TACPCM",
        "recurso_especial",
        "r.contrato_id IN (SELECT contrato_id FROM recurso_especial "
        "WHERE tipo_resolucion IN ('Estimatoria', 'Estimatoria parcial'))",
    ),
    (
        "Con recursos solo desestimados o inadmitidos ante el TACPCM",
        "recurso_especial",
        "r.contrato_id IN (SELECT contrato_id FROM recurso_especial) AND r.contrato_id NOT IN "
        "(SELECT contrato_id FROM recurso_especial WHERE contrato_id IS NOT NULL AND "
        "tipo_resolucion IN ('Estimatoria', 'Estimatoria parcial'))",
    ),
    (
        "Licitaciones de PLACSP con fondos europeos",
        "contrato_financiacion",
        "r.contrato_id IN (SELECT contrato_id FROM contrato_financiacion WHERE financiado_ue)",
    ),
    (
        "Licitaciones de PLACSP sin fondos europeos",
        "contrato_financiacion",
        "r.contrato_id IN (SELECT contrato_id FROM contrato_financiacion WHERE NOT financiado_ue)",
    ),
]


def validar(con: duckdb.DuckDBPyConnection) -> pl.DataFrame:
    """Proporción de atípicos y puntuación de riesgo media por grupo de validación, en
    `anomalia_validacion`. Es una comprobación descriptiva, no un entrenamiento: si la señal
    sirve, los contratos con recurso estimado deberían ser atípicos más a menudo que el 1 %."""
    filas = []
    con_puntuacion = _hay_tabla(con, "puntuacion_contrato")
    puntuacion_sql = "avg(p.puntuacion)" if con_puntuacion else "NULL"
    union = "LEFT JOIN puntuacion_contrato AS p USING (contrato_id)" if con_puntuacion else ""
    for nombre, tabla, condicion in VALIDACION:
        if tabla and not _hay_tabla(con, tabla):
            continue
        n, atipicos, puntuacion = con.execute(
            f"""
            SELECT count(*), count_if(r.atipico), {puntuacion_sql}
            FROM anomalia_resultado AS r {union}
            WHERE {condicion}
            """
        ).fetchall()[0]
        filas.append(
            {
                "grupo_validacion": nombre,
                "contratos": n,
                "atipicos": atipicos,
                "proporcion_atipicos": atipicos / n if n else None,
                "puntuacion_riesgo_media": puntuacion,
                "fuente": tabla or "contrato_unico",
                "fecha_descarga": con.execute(
                    f"SELECT max(fecha_descarga) FROM {tabla or 'contrato_unico'}"
                ).fetchall()[0][0],
            }
        )
    resultado = pl.DataFrame(
        filas,
        schema={
            "grupo_validacion": pl.String,
            "contratos": pl.Int64,
            "atipicos": pl.Int64,
            "proporcion_atipicos": pl.Float64,
            "puntuacion_riesgo_media": pl.Float64,
            "fuente": pl.String,
            "fecha_descarga": pl.Date,
        },
    )
    tabla = resultado.to_arrow()  # noqa: F841
    con.execute("CREATE OR REPLACE TABLE anomalia_validacion AS SELECT * FROM tabla")
    return resultado


def leer_variables(con: duckdb.DuckDBPyConnection) -> pl.DataFrame:
    """Una fila por contrato con su grupo de pares y sus variables."""
    return con.sql(CONSULTA_VARIABLES).pl().sort("contrato_id")  # orden fijo: reproducible


def _matriz(grupo: pl.DataFrame, variables: list[str]) -> np.ndarray:
    """Variables del grupo listas para el modelo: importe en logaritmo y huecos con la mediana."""
    columnas = []
    for v in variables:
        x = grupo[v].cast(pl.Float64)
        if v == "importe":
            x = x.log1p()
        columnas.append(x.fill_null(x.median()).to_numpy())
    return np.column_stack(columnas)


def _variables_utiles(grupo: pl.DataFrame) -> list[str]:
    """Variables con datos y con variación en el grupo (las demás no distinguen a nadie)."""
    utiles = []
    for v in VARIABLES:
        x = grupo[v].drop_nulls()
        if x.len() >= MIN_GRUPO and x.n_unique() > 1:
            utiles.append(v)
    return utiles


def desviaciones_robustas(matriz: np.ndarray) -> np.ndarray:
    """(x - mediana) / (1,4826 · MAD) por columna: cuánto se aleja cada contrato de su grupo."""
    mediana = np.median(matriz, axis=0)
    mad = 1.4826 * np.median(np.abs(matriz - mediana), axis=0)
    escala = np.where(mad > 0, mad, np.std(matriz, axis=0))
    escala = np.where(escala > 0, escala, 1.0)
    return (matriz - mediana) / escala


def _formato(valor: float, variable: str, iva: str = "") -> str:
    if variable == "importe":
        return f"{valor:,.0f} €".replace(",", ".") + (f" {iva}" if iva else "")
    if variable in ("baja", "modificaciones", "cuota"):
        return f"{100 * valor:.1f} %".replace(".", ",")
    return f"{valor:.0f}"


NOMBRES = {
    "importe": "importe adjudicado",
    "n_ofertas": "número de ofertas",
    "baja": "baja sobre el presupuesto",
    "modificaciones": "modificaciones sobre el importe adjudicado",
    "cuota": "cuota del adjudicatario en lo que adjudica este órgano en este tipo de contrato "
    "(2023–2026)",
    "menores_12m": "contratos menores con el mismo adjudicatario y órgano en los 12 meses "
    "anteriores (incluido este)",
}

RECUENTOS = ("n_ofertas", "menores_12m")


def _parte(variable: str, valor: float, desviacion: float, mediana: float, iva: str) -> str:
    """«<variable> de <valor> (por encima de la mediana de <m> de contratos similares)»."""
    if variable == "baja" and valor < 0:
        texto = f"adjudicado un {_formato(-valor, variable)} por encima del presupuesto"
        if valor < -1:  # más del doble del presupuesto: suele ser un error de la fuente
            texto += ", posible error en los datos de la fuente"
        return f"{texto} (en contratos similares la baja mediana es {_formato(mediana, variable)})"
    if variable in RECUENTOS:
        texto = f"{NOMBRES[variable]}: {_formato(valor, variable)}"
    else:
        texto = f"{NOMBRES[variable]} de {_formato(valor, variable, iva)}"
    lado = "por encima" if desviacion > 0 else "por debajo"
    referencia = _formato(mediana, variable, iva)
    return f"{texto} ({lado} de la mediana de {referencia} de contratos similares)"


def explicar(
    fila: dict, desviaciones: dict[str, float], medianas: dict[str, float], iva: str = ""
) -> tuple[list[str], str]:
    """Variables que más alejan al contrato de sus pares y una frase que lo cuenta.
    `iva` es «sin IVA» (PLACSP) o «con IVA» (portal regional) para los importes."""
    ordenadas = [
        v
        for v in sorted(desviaciones, key=lambda v: abs(desviaciones[v]), reverse=True)
        if fila[v] is not None
    ]
    elegidas = [v for v in ordenadas if abs(desviaciones[v]) >= MIN_DESVIACION_MOTIVO][
        :MAX_VARIABLES_MOTIVO
    ]
    if elegidas:
        partes = [_parte(v, fila[v], desviaciones[v], medianas[v], iva) for v in elegidas]
        texto = "; ".join(partes)
        return elegidas, texto[0].upper() + texto[1:]
    # Ninguna variable se aleja mucho por sí sola: se citan igualmente las dos que más.
    elegidas = ordenadas[:MAX_VARIABLES_MOTIVO]
    partes = [_parte(v, fila[v], desviaciones[v], medianas[v], iva) for v in elegidas]
    return elegidas, (
        "Ningún valor por sí solo se aleja mucho de contratos similares; lo poco habitual es "
        "la combinación de " + " y ".join(partes)
    )


IVA_FUENTE = {"placsp": "sin IVA", "portal_cm": "con IVA"}


def puntuar_grupo(grupo: pl.DataFrame) -> pl.DataFrame:
    """Isolation Forest sobre un grupo de pares. Devuelve las columnas de COLUMNAS."""
    variables = _variables_utiles(grupo)
    if grupo.height < MIN_GRUPO or not variables:
        return pl.DataFrame(schema=_esquema())
    matriz = _matriz(grupo, variables)
    modelo = IsolationForest(
        n_estimators=N_ARBOLES,
        contamination=PROPORCION_ATIPICOS,
        random_state=SEMILLA,
    ).fit(matriz)
    rareza = -modelo.score_samples(matriz)  # más alto = más atípico
    atipico = modelo.predict(matriz) == -1
    percentil = pl.Series(rareza).rank("average") / len(rareza)
    desviaciones = desviaciones_robustas(matriz)
    # Las medianas para el texto van en la escala original (no en logaritmo).
    medianas = {v: float(grupo[v].cast(pl.Float64).median()) for v in variables}
    filas = grupo.select(["contrato_id", *variables]).to_dicts()
    iva = IVA_FUENTE.get(grupo["grupo"][0].split(" · ")[0], "")
    variables_txt, motivos = [], []
    for i, fila in enumerate(filas):
        if not atipico[i]:
            variables_txt.append(None)
            motivos.append(None)
            continue
        elegidas, motivo = explicar(
            fila, dict(zip(variables, desviaciones[i], strict=True)), medianas, iva
        )
        variables_txt.append(", ".join(elegidas) or None)
        motivos.append(motivo)
    return pl.DataFrame(
        {
            "contrato_id": grupo["contrato_id"],
            "grupo": grupo["grupo"],
            "n_grupo": [grupo.height] * grupo.height,
            "puntuacion": percentil.round(4),
            "atipico": atipico,
            "variables": variables_txt,
            "motivo": motivos,
            "url_origen": grupo["url_origen"],
        },
        schema=_esquema(),
    )


def _esquema() -> dict:
    return {
        "contrato_id": pl.String,
        "grupo": pl.String,
        "n_grupo": pl.Int64,
        "puntuacion": pl.Float64,
        "atipico": pl.Boolean,
        "variables": pl.String,
        "motivo": pl.String,
        "url_origen": pl.String,
    }


def calcular(con: duckdb.DuckDBPyConnection) -> pl.DataFrame:
    """Calcula y guarda las tablas derivadas anomalia_resultado y anomalia_variables (los
    valores de cada contrato, para dibujarlo frente a sus pares en la interfaz). No tocan el
    esquema congelado (D-017)."""
    datos = leer_variables(con)
    partes = [puntuar_grupo(g) for _, g in datos.group_by("grupo", maintain_order=True)]
    resultado = pl.concat(partes) if partes else pl.DataFrame(schema=_esquema())
    tabla = resultado.to_arrow()  # noqa: F841 (DuckDB lo lee por su nombre)
    con.execute("CREATE OR REPLACE TABLE anomalia_resultado AS SELECT * FROM tabla")
    variables = datos.select(["contrato_id", "grupo", *VARIABLES]).to_arrow()  # noqa: F841
    con.execute("CREATE OR REPLACE TABLE anomalia_variables AS SELECT * FROM variables")
    calcular_encargos(con)
    validar(con)
    return resultado


def resumen(con: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyRelation:
    return con.sql(
        """
        SELECT grupo, any_value(n_grupo) AS contratos, count_if(atipico) AS atipicos
        FROM anomalia_resultado
        GROUP BY grupo
        ORDER BY contratos DESC
        """
    )


def main() -> None:
    with duckdb.connect(str(RUTA_DB)) as con:
        calcular(con)
        resumen(con).show(max_rows=100)
        con.sql(
            "SELECT count(*) AS encargos, count_if(atipico) AS atipicos FROM anomalia_encargo"
        ).show()
        con.sql("SELECT * FROM anomalia_validacion").show()


if __name__ == "__main__":
    main()
