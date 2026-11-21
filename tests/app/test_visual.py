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
    assert "3 contratos menores de Empresa B2 con este organismo" in frase
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
    assert textos.euros(3_871_400_000) == "3,9 mil millones €"
    assert textos.numero(1_354_441) == "1,35 millones"
    assert textos.numero(1_000_000) == "1 millón"
    assert textos.numero(243_945) == "243.945"


def test_ficha_de_empresa(con):
    reparto = datos.reparto_empresa(con, "B1")
    assert [(r["fuente"], r["n"]) for r in reparto] == [("placsp", 3)]
    assert {s["indicador"]: s["n"] for s in datos.senales_empresa(con, "B1")}["R-01"] == 1
    assert graficos.reparto_organismos(reparto) is not None
    assert graficos.partir("Hospital Universitario Gregorio Marañón") == (
        "Hospital Universitario<br>Gregorio Marañón"
    )


def test_procedimientos_agrupa_por_nombre_llano():
    filas = [
        {"procedimiento": "Contrato menor", "n_contratos": 10},
        {"procedimiento": "Contratos Menores", "n_contratos": 2},
        {"procedimiento": "Otros", "n_contratos": 3},
        {"procedimiento": "Abierto", "n_contratos": 5},
    ]
    figura = graficos.procedimientos(filas, textos.PROCEDIMIENTO_LLANO)
    barras = dict(zip(figura.data[0].y, figura.data[0].x, strict=True))
    assert barras["Contrato menor (importe pequeño, sin concurso)"] == 12
    assert barras["Otras vías"] == 3
    assert len(barras) == 3


def test_reparto_de_organismo_agrega_personas(con):
    reparto = datos.reparto_organo(con, "ORG")
    assert {r["nombre"] for r in reparto} >= {"Empresa B1"}


def test_empaquetar_sin_solapes():
    import math

    radios = [1.0, 0.8, 0.5, 0.5, 0.3, 0.2, 0.2, 0.1]
    centros = graficos.empaquetar(radios)
    assert centros[0] == (0.0, 0.0)
    for i in range(len(radios)):
        for j in range(i + 1, len(radios)):
            (xi, yi), (xj, yj) = centros[i], centros[j]
            assert math.hypot(xi - xj, yi - yj) >= radios[i] + radios[j] - 1e-9


def test_mapa_del_dinero(con):
    totales = datos.totales_organos(con, "portal_cm", incluir_menores=True)
    assert totales[0]["organo_id"] == "ORG"
    flujos = datos.flujos(con, "portal_cm", True, organo_id="ORG")
    assert {f["empresa"] for f in flujos} == {"Empresa B2"}
    assert graficos.burbujas_organismos(totales) is not None
    assert graficos.red_organismo("Órgano", flujos, totales[0]["importe"]) is not None


def test_atipico_dibuja_dos_variables_o_una():
    pares = [{"importe": 100.0 * i, "cuota": i / 100, "baja": 0.1} for i in range(1, 60)]
    este = {"importe": 50_000.0, "cuota": 0.9, "baja": -50.0}
    figura = graficos.atipico({"este": este, "pares": pares}, ["importe", "cuota"])
    assert [t.name for t in figura.data] == ["Contratos similares", "Este contrato"]
    figura = graficos.atipico({"este": este, "pares": pares}, ["baja"])
    # El eje se recorta, pero este contrato (rebaja de -5.000 %) sigue dentro.
    assert figura.layout.xaxis.range[0] <= -50.0
