"""Plano de una consulta para la animación del asistente (D-037)."""

from ojo_ciudadano.asistente import plano


def test_tablas_uniones_y_pasos(base):
    sql = """
    WITH ultima AS (SELECT max(fecha_contrato) AS fecha FROM contrato_unico)
    SELECT o.nombre, count(*) AS n
    FROM contrato_unico AS c
    JOIN organo AS o USING (organo_id)
    JOIN adjudicacion AS a USING (contrato_id)
    JOIN adjudicatario AS d ON d.adjudicatario_id = a.adjudicatario_id
    CROSS JOIN ultima
    WHERE c.es_menor
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT 5
    """
    p = plano.plano_consulta(base.con, sql)
    assert p.tablas[:4] == ["contrato_unico", "organo", "adjudicacion", "adjudicatario"]
    assert p.intermedias == ["ultima"]
    assert ("contrato_unico", "organo", "organo_id") in p.uniones
    assert ("contrato_unico", "adjudicacion", "contrato_id") in p.uniones
    assert ("adjudicacion", "adjudicatario", "adjudicatario_id") in p.uniones
    assert ("adjudicatario", "ultima", "todas las combinaciones") in p.uniones
    assert p.pasos[0] == "Preparar el cálculo intermedio «ultima»"
    assert "Filtrar las filas que cumplen la pregunta" in p.pasos
    assert "Agrupar y sumar" in p.pasos
    assert p.pasos[-1] == "Quedarse con las 5 primeras filas"


def test_sql_que_no_se_puede_leer_da_un_plano_minimo(base):
    p = plano.plano_consulta(base.con, "DELETE FROM contrato")
    assert p.tablas == [] and p.pasos == ["Consultar la base de datos"]
