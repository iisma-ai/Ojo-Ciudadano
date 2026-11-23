"""Detección de contratos atípicos (D-021) con datos sintéticos."""

from datetime import date, timedelta

import numpy as np

from ojo_ciudadano.anomalias import deteccion


def _licitaciones(base, n=120, semilla=0):
    """n licitaciones de servicios parecidas: ~100.000 €, 4–6 ofertas, baja del 10–20 %."""
    rng = np.random.default_rng(semilla)
    for i in range(n):
        presupuesto = float(rng.uniform(90_000, 110_000))
        base.contrato(
            f"placsp:{i}",
            [
                {
                    "adjudicatario_id": f"B{i % 30}",
                    "importe_sin_iva": presupuesto * float(rng.uniform(0.8, 0.9)),
                    "n_ofertas": int(rng.integers(4, 7)),
                    "resultado": "Formalizado",
                }
            ],
            procedimiento="Abierto",
            tipo_contrato="Servicios",
            presupuesto_sin_iva=presupuesto,
        )


def test_senala_el_contrato_que_se_aleja_de_sus_pares(base):
    _licitaciones(base)
    base.contrato(
        "placsp:raro",
        [
            {
                "adjudicatario_id": "B1",
                "importe_sin_iva": 5_000_000.0,
                "n_ofertas": 1,
                "resultado": "Formalizado",
            }
        ],
        procedimiento="Abierto",
        tipo_contrato="Servicios",
        presupuesto_sin_iva=5_000_000.0,
    )
    resultado = deteccion.calcular(base.con)
    fila = resultado.filter(resultado["contrato_id"] == "placsp:raro").row(0, named=True)
    assert fila["atipico"]
    assert fila["grupo"] == "placsp · licitación · servicios"
    assert fila["puntuacion"] == resultado["puntuacion"].max()
    assert "importe" in fila["variables"]
    assert "por encima de la mediana" in fila["motivo"]
    assert fila["url_origen"] == "https://ejemplo.test/placsp:raro"
    # Solo el ~1 % del grupo queda como atípico.
    assert resultado["atipico"].sum() <= 3


def test_grupos_pequenos_no_se_puntuan(base):
    _licitaciones(base, n=deteccion.MIN_GRUPO - 1)
    assert deteccion.calcular(base.con).height == 0
    assert base.con.sql("SELECT count(*) FROM anomalia_resultado").fetchall()[0][0] == 0


def test_no_mezcla_fuentes_ni_menores_con_licitaciones(base):
    _licitaciones(base)
    inicio = date(2025, 1, 1)
    for i in range(80):
        base.menor(f"portal_cm:m{i}", inicio + timedelta(days=i), 5_000.0, f"M{i % 20}")
    resultado = deteccion.calcular(base.con)
    assert set(resultado["grupo"]) == {
        "placsp · licitación · servicios",
        "portal_cm · menor · servicios",
    }


def test_es_reproducible(base):
    _licitaciones(base)
    primero = deteccion.calcular(base.con)
    segundo = deteccion.calcular(base.con)
    assert primero.equals(segundo)


def test_menores_cuenta_los_del_mismo_adjudicatario_en_12_meses(base):
    inicio = date(2025, 1, 1)
    for i in range(5):
        base.menor(f"portal_cm:m{i}", inicio + timedelta(days=60 * i), 1_000.0, "M1")
    variables = deteccion.leer_variables(base.con).sort("contrato_id")
    # El quinto (día 240) tiene los cinco dentro de los 12 meses anteriores.
    assert variables["menores_12m"].to_list() == [1, 2, 3, 4, 5]


def test_explicar_cita_las_variables_mas_alejadas():
    fila = {"importe": 2_000_000.0, "n_ofertas": 1, "cuota": 0.1}
    desviaciones = {"importe": 8.0, "n_ofertas": -3.0, "cuota": 0.5}
    medianas = {"importe": 100_000.0, "n_ofertas": 5.0, "cuota": 0.05}
    variables, motivo = deteccion.explicar(fila, desviaciones, medianas, "sin IVA")
    assert variables == ["importe", "n_ofertas"]
    assert motivo.startswith("Importe adjudicado de 2.000.000 € sin IVA (por encima de la")
    assert "100.000 € sin IVA de contratos similares" in motivo
    assert "número de ofertas: 1 (por debajo de la mediana de 5" in motivo


def test_explicar_sin_variables_extremas_cita_la_combinacion():
    fila = {"importe": 150_000.0, "baja": -0.12}
    desviaciones = {"importe": 1.5, "baja": -1.8}
    medianas = {"importe": 100_000.0, "baja": 0.15}
    variables, motivo = deteccion.explicar(fila, desviaciones, medianas, "con IVA")
    assert variables == ["baja", "importe"]
    assert motivo.startswith("Ningún valor por sí solo se aleja mucho")
    assert (
        "adjudicado un 12,0 % por encima del presupuesto (en contratos similares la baja " in motivo
    )
    assert "posible error" not in motivo


def test_explicar_avisa_de_posible_error_si_se_adjudica_por_mas_del_doble():
    fila = {"baja": -99.0}
    _, motivo = deteccion.explicar(fila, {"baja": -50.0}, {"baja": 0.135}, "sin IVA")
    assert motivo.startswith("Adjudicado un 9900,0 % por encima del presupuesto, posible error")
    assert "baja mediana es 13,5 %" in motivo


def _encargos(base, n=80):
    """n encargos parecidos (~200.000 € con IVA) de dos órganos a dos medios propios."""
    rng = np.random.default_rng(1)
    for medio in ("A28476208", "A83052407"):
        base.con.execute(
            "INSERT OR IGNORE INTO adjudicatario VALUES (?, ?, 'Medio propio', 'juridica')",
            [medio, medio],
        )
    for i in range(n):
        base.con.execute(
            "INSERT INTO encargo (encargo_id, orden, fuente, organo_id, titulo, anio_publicacion, "
            "medio_propio_id, importe_con_iva, importe_modificaciones_con_iva, url_origen, "
            "fecha_descarga) VALUES (?, 1, 'portal_cm', ?, 'Encargo', 2025, ?, ?, 0, ?, ?)",
            [
                f"portal_cm:C{i}",
                "ORG" if i % 2 else "OTRO",
                "A28476208" if i % 3 else "A83052407",
                float(rng.uniform(180_000, 220_000)),
                f"https://ejemplo.test/C{i}",
                date(2026, 11, 23),
            ],
        )


def test_encargos_atipicos_frente_a_otros_encargos(base):
    _encargos(base)
    base.con.execute(
        "INSERT INTO encargo (encargo_id, orden, fuente, organo_id, titulo, anio_publicacion, "
        "medio_propio_id, importe_con_iva, importe_modificaciones_con_iva, url_origen, "
        "fecha_descarga) VALUES ('portal_cm:CX', 1, 'portal_cm', 'ORG', 'Encargo grande', 2025, "
        "'A28476208', 40000000, 0, 'https://ejemplo.test/CX', DATE '2026-11-23')"
    )
    _licitaciones(base)
    deteccion.calcular(base.con)
    fila = base.con.execute(
        "SELECT atipico, grupo, motivo FROM anomalia_encargo WHERE encargo_id = 'portal_cm:CX'"
    ).fetchall()[0]
    assert fila[0] is True and fila[1] == "portal_cm · encargo"
    assert "importe del encargo" in fila[2].lower() and "encargos similares" in fila[2]
    # Los encargos no se mezclan con los contratos.
    assert (
        base.con.execute(
            "SELECT count(*) FROM anomalia_resultado WHERE contrato_id LIKE 'portal_cm:C%'"
        ).fetchall()[0][0]
        == 0
    )


def test_motivo_de_encargo_sin_lenguaje_de_contratos():
    motivo = (
        "Cuota del adjudicatario en lo que adjudica este órgano en este tipo de contrato "
        "(2023–2026) de 90,0 % (por encima de la mediana de 5,0 % de contratos similares); "
        "importe adjudicado de 1.000 € con IVA"
    )
    texto = deteccion._texto_encargo(motivo)
    assert texto.startswith("Cuota del medio propio en lo que encarga este órgano")
    assert "adjudica" not in texto and "contratos" not in texto
    assert "importe del encargo" in texto


def test_validacion_con_recursos_y_fondos_europeos(base):
    _licitaciones(base)
    deteccion.calcular(base.con)
    base.con.execute(
        "INSERT INTO recurso_especial (resolucion_id, numero, procedencia, tipo_resolucion, "
        "acto_recurrido, contrato_id, fuente, url_origen, fecha_descarga) VALUES "
        "('tacpcm:1/2025', '1/2025', 'Consejerías', 'Estimatoria', 'Pliegos', 'placsp:1', "
        "'tacpcm', 'https://x', DATE '2026-11-23'), "
        "('tacpcm:2/2025', '2/2025', 'Consejerías', 'Desestimatoria', 'Adjudicación', "
        "'placsp:2', 'tacpcm', 'https://x', DATE '2026-11-23')"
    )
    base.con.execute(
        "INSERT INTO contrato_financiacion VALUES ('placsp:3', true, 'PRTR', 'placsp', "
        "'https://x', DATE '2026-11-23')"
    )
    tabla = {f["grupo_validacion"]: f for f in deteccion.validar(base.con).to_dicts()}
    assert tabla["Todos los contratos analizados"]["contratos"] == 120
    assert tabla["Con algún recurso estimado (total o parcial) ante el TACPCM"]["contratos"] == 1
    assert tabla["Con recursos solo desestimados o inadmitidos ante el TACPCM"]["contratos"] == 1
    assert tabla["Licitaciones de PLACSP con fondos europeos"]["contratos"] == 1
    assert tabla["Licitaciones de PLACSP con fondos europeos"]["fecha_descarga"] is not None
    guardada = base.con.execute("SELECT count(*) FROM anomalia_validacion").fetchall()[0][0]
    assert guardada == len(deteccion.VALIDACION)
