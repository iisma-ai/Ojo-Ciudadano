"""Batería de 20 preguntas de prueba para evaluar el asistente (docs/05-asistente.md).

Cada pregunta trae una consulta de referencia verificada a mano. Para evaluar el SQL que genere
el modelo (D-010), se ejecutan las dos con el mismo validador (`sql_seguro`) y se comparan las
columnas clave del resultado, sin exigir el mismo SQL ni los mismos nombres de columna. Dos
preguntas no se pueden responder con los datos: lo correcto es que el asistente diga que no
puede, sin generar SQL.

Reglas de las referencias: no se suman importes con y sin IVA (P-10), las personas físicas solo
aparecen agregadas (D-007) y se usa `contrato_unico` para no contar dos veces.

Uso: uv run python -m ojo_ciudadano.asistente.bateria   (ejecuta las referencias sobre la base)
"""

import math
from dataclasses import dataclass, field

import duckdb

from ojo_ciudadano.asistente import sql_seguro

# Adjudicatario que se puede mostrar con nombre: persona jurídica o UTE sin personas físicas.
_VISIBLE = "d.tipo_persona IN ('juridica', 'ute') AND NOT contains(d.adjudicatario_id, 'PF-')"


@dataclass(frozen=True)
class PreguntaPrueba:
    id: str
    pregunta: str
    sql: str | None  # None: no se puede responder con los datos
    clave: tuple[str, ...] = ()  # columnas que deciden si la respuesta es correcta
    parametros: dict = field(default_factory=dict)
    coincidencia_minima: float = 1.0  # en rankings, empates en el corte: basta con el 80 %
    nota: str = ""  # qué debe decir o matizar la respuesta


BATERIA = [
    PreguntaPrueba(
        "B01",
        "¿Cuántos contratos hay en la base de cada fuente?",
        "SELECT fuente, count(*) AS n FROM contrato_unico GROUP BY fuente",
        ("fuente", "n"),
        nota="Cuenta cada licitación una vez aunque esté en las dos fuentes.",
    ),
    PreguntaPrueba(
        "B02",
        "¿Cuántos contratos menores se firmaron cada año?",
        """
        SELECT year(fecha_contrato) AS anio, count(*) AS n
        FROM contrato_unico WHERE es_menor AND fecha_contrato IS NOT NULL
        GROUP BY anio
        """,
        ("anio", "n"),
        nota="Debe avisar de que los meses recientes de 2026 están incompletos (P-12).",
    ),
    PreguntaPrueba(
        "B03",
        "¿Qué 10 órganos tienen más contratos?",
        """
        SELECT o.nombre AS organo, count(*) AS n
        FROM contrato_unico AS c JOIN organo AS o USING (organo_id)
        GROUP BY o.nombre ORDER BY n DESC LIMIT 10
        """,
        ("organo",),
        coincidencia_minima=0.8,
    ),
    PreguntaPrueba(
        "B04",
        "¿Qué porcentaje de las licitaciones con concurrencia recibió una sola oferta?",
        """
        SELECT count_if(activado) / count(*) AS proporcion
        FROM indicador_resultado WHERE indicador = 'R-01'
        """,
        ("proporcion",),
        nota="Es el indicador R-01: abierto, abierto simplificado y restringido.",
    ),
    PreguntaPrueba(
        "B05",
        "¿Qué 10 órganos tienen más contratos con un solo licitador?",
        """
        SELECT o.nombre AS organo, count(*) AS n
        FROM indicador_resultado AS r
        JOIN contrato_unico AS c USING (contrato_id)
        JOIN organo AS o USING (organo_id)
        WHERE r.indicador = 'R-01' AND r.activado
        GROUP BY o.nombre ORDER BY n DESC LIMIT 10
        """,
        ("organo",),
        coincidencia_minima=0.8,
        nota="Es una señal de riesgo, no una irregularidad.",
    ),
    PreguntaPrueba(
        "B06",
        "¿Cuántos contratos tienen activado cada indicador de riesgo?",
        """
        SELECT indicador, count_if(activado) AS activados
        FROM indicador_resultado GROUP BY indicador
        """,
        ("indicador", "activados"),
    ),
    PreguntaPrueba(
        "B07",
        "¿Qué 10 empresas han recibido más importe en contratos de la Plataforma de "
        "Contratación del Sector Público?",
        f"""
        SELECT d.nombre AS empresa, sum(a.importe_sin_iva) AS importe_sin_iva
        FROM adjudicacion AS a
        JOIN contrato_unico AS c USING (contrato_id)
        JOIN adjudicatario AS d USING (adjudicatario_id)
        WHERE c.fuente = 'placsp' AND {_VISIBLE}
        GROUP BY d.nombre ORDER BY importe_sin_iva DESC LIMIT 10
        """,
        ("empresa",),
        coincidencia_minima=0.8,
        nota="Importes sin IVA; no se suman con los del portal regional (con IVA).",
    ),
    PreguntaPrueba(
        "B08",
        "¿Qué 10 empresas tienen más contratos con alguna señal de riesgo?",
        f"""
        SELECT d.nombre AS empresa, p.n_con_alertas
        FROM puntuacion_empresa AS p JOIN adjudicatario AS d USING (adjudicatario_id)
        WHERE {_VISIBLE}
        ORDER BY p.n_con_alertas DESC LIMIT 10
        """,
        ("empresa",),
        coincidencia_minima=0.8,
        nota="Muchos contratos con señales suele ir con muchos contratos en total: dar ambos.",
    ),
    PreguntaPrueba(
        "B09",
        "¿Cuáles son los 10 contratos con la puntuación de riesgo más alta, con al menos tres "
        "indicadores aplicables?",
        """
        SELECT contrato_id, puntuacion
        FROM puntuacion_contrato WHERE n_aplicables >= 3
        ORDER BY puntuacion DESC, n_activados DESC, importe DESC LIMIT 10
        """,
        ("contrato_id",),
        coincidencia_minima=0.8,
        nota="Cada contrato con su enlace al expediente; la puntuación no es una probabilidad.",
    ),
    PreguntaPrueba(
        "B10",
        "¿Qué órganos con al menos 100 contratos tienen la puntuación de riesgo ponderada más "
        "alta?",
        """
        SELECT o.nombre AS organo, p.puntuacion_ponderada
        FROM puntuacion_organo AS p JOIN organo AS o USING (organo_id)
        WHERE p.n_contratos >= 100
        ORDER BY p.puntuacion_ponderada DESC LIMIT 10
        """,
        ("organo",),
        coincidencia_minima=0.8,
    ),
    PreguntaPrueba(
        "B11",
        "¿Cuántas subvenciones concedió la Comunidad cada año y por qué importe?",
        """
        SELECT year(fecha_concesion) AS anio, count(*) AS n, sum(importe) AS importe
        FROM concesion GROUP BY anio
        """,
        ("anio", "n"),
        nota="El salto de 2025 son las ayudas de la PAC, casi todas a personas físicas.",
    ),
    PreguntaPrueba(
        "B12",
        "¿Qué 10 convocatorias de subvenciones han repartido más dinero?",
        """
        SELECT convocatoria, sum(importe) AS importe
        FROM concesion GROUP BY convocatoria ORDER BY importe DESC LIMIT 10
        """,
        ("convocatoria",),
        coincidencia_minima=0.8,
    ),
    PreguntaPrueba(
        "B13",
        "¿Qué parte del importe de las subvenciones fue a personas físicas?",
        """
        SELECT sum(s.importe) FILTER (WHERE d.tipo_persona = 'fisica') / sum(s.importe)
            AS proporcion
        FROM concesion AS s JOIN adjudicatario AS d ON d.adjudicatario_id = s.beneficiario_id
        """,
        ("proporcion",),
        nota="Solo el agregado: nunca nombres ni seudónimos de personas (D-007).",
    ),
    PreguntaPrueba(
        "B14",
        "¿Qué 10 entidades han recibido más importe en subvenciones?",
        f"""
        SELECT d.nombre AS entidad, sum(s.importe) AS importe
        FROM concesion AS s JOIN adjudicatario AS d ON d.adjudicatario_id = s.beneficiario_id
        WHERE {_VISIBLE}
        GROUP BY d.nombre ORDER BY importe DESC LIMIT 10
        """,
        ("entidad",),
        coincidencia_minima=0.8,
    ),
    PreguntaPrueba(
        "B15",
        "¿Cuántas empresas tienen a la vez contratos y subvenciones?",
        f"""
        SELECT count(DISTINCT d.adjudicatario_id) AS n
        FROM adjudicatario AS d
        WHERE {_VISIBLE}
          AND d.adjudicatario_id IN (SELECT adjudicatario_id FROM adjudicacion)
          AND d.adjudicatario_id IN (SELECT beneficiario_id FROM concesion)
        """,
        ("n",),
    ),
    PreguntaPrueba(
        "B16",
        "¿Cuántos contratos superan el 20 % de modificaciones sobre el importe adjudicado?",
        """
        SELECT count(*) AS n FROM indicador_resultado WHERE indicador = 'R-05' AND activado
        """,
        ("n",),
        nota="Indicador R-05, solo portal regional; las prórrogas no cuentan (D-016).",
    ),
    PreguntaPrueba(
        "B17",
        "¿Cuántos contratos con varias ofertas se adjudicaron sin baja o con una baja de al "
        "menos el 50 %?",
        """
        SELECT count_if(valor <= 0.005) AS baja_nula, count_if(valor >= 0.5) AS baja_extrema
        FROM indicador_resultado WHERE indicador = 'R-06'
        """,
        ("baja_nula", "baja_extrema"),
        nota="Indicador R-06 (D-019). Una baja extrema no es anormal por sí sola.",
    ),
    PreguntaPrueba(
        "B18",
        "¿Cuántos contratos ha adjudicado un órgano concreto y por qué importe?",
        """
        SELECT o.nombre AS organo, c.fuente, count(DISTINCT c.contrato_id) AS n,
               sum(coalesce(a.importe_sin_iva, a.importe_con_iva)) AS importe
        FROM contrato_unico AS c
        JOIN organo AS o USING (organo_id)
        LEFT JOIN adjudicacion AS a USING (contrato_id)
        WHERE o.nombre ILIKE '%' || $organo || '%'
        GROUP BY o.nombre, c.fuente
        """,
        ("organo", "fuente", "n"),
        parametros={"organo": "hospital universitario la paz"},
        nota="Por fuente: los importes de PLACSP van sin IVA y los del portal con IVA.",
    ),
    PreguntaPrueba(
        "B19",
        "¿Qué funcionario firmó la adjudicación de un contrato?",
        None,
        nota="La base no tiene firmantes ni personas de la Administración: decirlo.",
    ),
    PreguntaPrueba(
        "B20",
        "¿Qué partida del presupuesto pagó cada contrato de Sanidad?",
        None,
        nota="No hay enlace entre partida y contrato (fuera de alcance): decirlo.",
    ),
]


@dataclass
class Evaluacion:
    correcta: bool
    coincidencia: float
    motivo: str


def _numeros_iguales(a: float, b: float) -> bool:
    """Tolerancia del 0,5 % y proporción o porcentaje indistintos (0,394 = 39,4)."""
    return any(math.isclose(a, x, rel_tol=0.005, abs_tol=1e-9) for x in (b, 100 * b, b / 100))


def _normalizar(valor):
    if isinstance(valor, str):
        return valor.strip().lower()
    if isinstance(valor, int | float) and not isinstance(valor, bool):
        return float(valor)
    return valor


def _iguales(fila_a: tuple, fila_b: tuple) -> bool:
    for a, b in zip(fila_a, fila_b, strict=True):
        if isinstance(a, float) and isinstance(b, float):
            if not _numeros_iguales(a, b):
                return False
        elif a != b:
            return False
    return True


def _claves(resultado: dict, clave: tuple[str, ...]) -> list[tuple]:
    """Columnas clave por nombre; si el modelo las llamó de otra forma, por posición."""
    columnas = [c.lower() for c in resultado["columnas"]]
    if all(c in columnas for c in clave):
        indices = [columnas.index(c) for c in clave]
    else:
        indices = list(range(min(len(clave), len(columnas))))
    return [tuple(_normalizar(f[i]) for i in indices) for f in resultado["filas"]]


def evaluar(
    con: duckdb.DuckDBPyConnection, prueba: PreguntaPrueba, sql_candidato: str | None
) -> Evaluacion:
    """Compara la respuesta del asistente con la referencia de la batería."""
    if prueba.sql is None:
        if sql_candidato is None:
            return Evaluacion(True, 1.0, "Dice que no se puede responder, como se espera.")
        return Evaluacion(False, 0.0, "Debía decir que los datos no lo permiten.")
    if sql_candidato is None:
        return Evaluacion(False, 0.0, "No respondió una pregunta que sí tiene respuesta.")
    try:
        candidato = sql_seguro.ejecutar(con, sql_candidato, prueba.parametros or None)
    except (sql_seguro.SQLNoPermitido, duckdb.Error) as error:
        return Evaluacion(False, 0.0, f"El SQL no se pudo ejecutar: {error}")
    referencia = sql_seguro.ejecutar(con, prueba.sql, prueba.parametros or None)
    if len(candidato["columnas"]) < len(prueba.clave):
        return Evaluacion(False, 0.0, "Faltan columnas en la respuesta.")
    esperadas = _claves(referencia, prueba.clave)
    obtenidas = _claves(candidato, prueba.clave)
    if not esperadas:
        ok = not obtenidas
        return Evaluacion(ok, float(ok), "Referencia vacía.")
    acertadas = sum(1 for e in esperadas if any(_iguales(o, e) for o in obtenidas))
    coincidencia = acertadas / len(esperadas)
    sobrantes = len(obtenidas) - acertadas
    if prueba.coincidencia_minima == 1.0 and sobrantes > 0:
        return Evaluacion(False, coincidencia, f"{sobrantes} filas de más.")
    correcta = coincidencia >= prueba.coincidencia_minima
    return Evaluacion(correcta, coincidencia, f"{acertadas} de {len(esperadas)} filas esperadas.")


def main() -> None:
    from ojo_ciudadano.indicadores.ejecutor import RUTA_DB

    con = sql_seguro.conexion_lectura(RUTA_DB)
    for prueba in BATERIA:
        if prueba.sql is None:
            print(f"{prueba.id}: sin respuesta esperada")
            continue
        r = sql_seguro.ejecutar(con, prueba.sql, prueba.parametros or None)
        primera = r["filas"][0] if r["filas"] else None
        print(f"{prueba.id}: {len(r['filas'])} filas · primera: {primera}")


if __name__ == "__main__":
    main()
