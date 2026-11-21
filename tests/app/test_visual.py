"""Portada y explicación visual de las señales (D-023), con una base sintética."""

from datetime import date, timedelta

import pytest

from ojo_ciudadano.app import datos, graficos, senales, textos
from ojo_ciudadano.indicadores import ejecutor


@pytest.fixture
def con(base):
    # R-01: una licitación con una sola oferta y otras dos con varias.
    for cid, ofertas in (("l1", 1), ("l2", 4), ("l3", 5)):
        base.contrato(
            cid,
            [
                {
                    "adjudicatario_id": "B1",
                    "importe_sin_iva": 900,
                    "n_ofertas": ofertas,
                    "resultado": "Formalizado",
                }
            ],
            procedimiento="Abierto",
            tipo_contrato="servicios",
            presupuesto_sin_iva=1000,
            fecha_fin_plazo="2025-02-01",
        )
    # R-03: tres menores de 7.000 € con IVA a la misma empresa en pocos meses (21.000 > 18.150).
    for n in range(3):
        base.menor(f"m{n}", date(2025, 1, 1) + timedelta(days=30 * n), 7000.0, "B2")
    base.con.execute("UPDATE adjudicatario SET nombre = 'Empresa ' || adjudicatario_id")
    ejecutor.calcular_todos(base.con)
    return base.con


def test_resumen_y_conteo(con):
    resumen = datos.resumen_portada(con)
    assert resumen["n_contratos"] == 6
    conteo = datos.conteo_senales(con)
    assert conteo["R-01"]["encontrados"] == 1
    assert conteo["R-03"]["encontrados"] == 3


def test_r01_compara_con_contratos_parecidos(con):
    detalle = datos.detalle_r01(con, "l1")
    assert detalle["ofertas"] == 1
    assert dict(detalle["distribucion"]) == {1: 1, 4: 1, 5: 1}
    frase, figura = senales.frase_y_grafico(con, "R-01", "l1")
    assert "recibió **1 oferta**" in frase
    assert "el 67 % recibió dos o más" in frase
    assert figura is not None


def test_r03_suma_doce_meses_y_limite(con):
    detalle = datos.detalle_r03(con, "m1")
    assert detalle["umbral"] == 18150
    assert detalle["empresa"] == "Empresa B2"
    assert graficos.suma_doce_meses(detalle["contratos"]) == [7000, 14000, 21000]
    frase, _ = senales.frase_y_grafico(con, "R-03", "m1")
    assert "3 contratos menores de Empresa B2" in frase
    assert "21.000 €" in frase


def test_r03_sin_nombre_de_persona_fisica(base, con):
    base.con.execute(
        "UPDATE adjudicatario SET tipo_persona = 'fisica', nombre = NULL "
        "WHERE adjudicatario_id = 'B2'"
    )
    assert datos.detalle_r03(con, "m1")["empresa"] is None
    frase, _ = senales.frase_y_grafico(con, "R-03", "m1")
    assert "la misma adjudicataria" in frase


def test_r04_reparto_del_organismo(con):
    detalle = datos.detalle_r04(con, "l1")
    assert detalle["partes"][0]["es_este"]
    assert detalle["cuota"] == pytest.approx(1.0)


def test_importes_y_rebaja(con):
    detalle = datos.detalle_importes(con, "l1")
    assert detalle["presupuesto"] == 1000 and detalle["adjudicado"] == 900
    frase, figura = senales.frase_y_grafico(con, "R-06", "l1")
    assert "la rebaja fue del **10,0 %**" in frase
    assert figura is not None


def test_sin_datos_no_hay_grafico(con):
    assert senales.frase_y_grafico(con, "R-02", "no-existe") == (None, None)


def test_euros_y_numeros_legibles():
    assert textos.euros(1_234_567.8, "sin IVA") == "1,2 millones € sin IVA"
    assert textos.euros(45_300) == "45.300 €"
    assert textos.numero(1_354_441) == "1,35 millones"
    assert textos.numero(1_000_000) == "1 millón"
    assert textos.numero(243_945) == "243.945"
