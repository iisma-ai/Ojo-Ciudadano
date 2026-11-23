"""Contexto de la Comunidad de Madrid (D-024): lectura de los ficheros, privacidad y consultas.

Todo con ficheros y filas sintéticos; nada depende de lo descargado.
"""

from datetime import date

from ojo_ciudadano.app import datos_contexto as dc
from ojo_ciudadano.ingesta import cm_contexto
from ojo_ciudadano.modelo import contexto

HOY = date(2026, 11, 23)
URL = "https://datos.comunidad.madrid/dataset/x"


def _csv(ruta, texto: str) -> None:
    ruta.write_text("﻿" + texto, encoding="utf-8")


def test_serie_pasa_a_euros_y_deja_vacio_el_guion(tmp_path):
    _csv(
        tmp_path / "1502013.csv",
        "Año;Concepto;Tipo territorio;Código territorio;Territorio;Valor;Unidad;Estado dato\n"
        "2025;Total gastos consolidados de los presupuestos generales iniciales;Otros;;;31596.5;"
        "Miles euros;\n"
        "2025;Gastos consolidados en fondo de contingencia;Otros;;;-;Miles euros;\n",
    )
    df = cm_contexto.leer_series(tmp_path)
    assert df.height == 2
    total = df.filter(df["valor"].is_not_null()).row(0, named=True)
    assert total["valor_eur"] == 31_596_500
    assert df["valor"].null_count() == 1


def test_presupuesto_organo_reconoce_la_consejeria(tmp_path):
    _csv(
        tmp_path / "presupuestos_liquidados_gastos_consolidados_por_organo_y_fase_ejecucion.csv",
        "Año;Concepto;Tipo territorio;Código territorio;Territorio;Fase;Valor;Unidad;Estado dato\n"
        "2024;Gastos consolidados de la Consejería de Sanidad en fase de obligaciones reconocidas "
        "de los presupuestos liquidados;Otros;;;Obligaciones reconocidas;13462.5;Miles euros;\n"
        "2024;Gastos consolidados del Consejo Consultivo en fase de pagos realizados de los "
        "presupuestos liquidados;Otros;;;Pagos realizados;-;Miles euros;\n",
    )
    df = cm_contexto.leer_presupuesto_organo(tmp_path, {"CONSEJERIA DE SANIDAD"})
    assert df.height == 1  # la fila sin valor se descarta
    fila = df.row(0, named=True)
    assert fila["organo_id"] == "CONSEJERIA DE SANIDAD"
    assert fila["importe_eur"] == 13_462_500
    assert fila["fase"] == "Obligaciones reconocidas"


def test_entidades_solo_personas_juridicas(tmp_path):
    _csv(
        tmp_path / "registro_fundaciones.csv",
        "denominacion;NIF;protectorado\nFundación Ejemplo;G88614565;Educación\n"
        "Fundación de un particular;12345678Z;Educación\nSin NIF;;Educación\n",
    )
    df = cm_contexto.leer_entidades(tmp_path)
    assert df["nif"].to_list() == ["G88614565"]  # el DNI y el vacío no entran (D-007)


def test_firmantes_de_convenios_se_separan_y_las_personas_no_se_muestran():
    cm, firmantes = cm_contexto._firmantes(
        " Entidad CM: PRESIDENCIA DE LA CM   Entidad: AYUNTAMIENTO MADRID   Entidad: JUAN PEREZ GARCIA"
    )
    assert cm == "PRESIDENCIA DE LA CM"
    assert firmantes == ["AYUNTAMIENTO MADRID", "JUAN PEREZ GARCIA"]
    assert cm_contexto.parece_entidad("PANAMA ROW, SL")
    assert cm_contexto.parece_entidad("AYUNTAMIENTO MADRID")
    assert not cm_contexto.parece_entidad("JUAN PEREZ GARCIA")


def test_cargar_crea_las_tablas_y_no_toca_las_demas(base, tmp_path):
    ruta = tmp_path / "base.duckdb"
    base.con.execute(f"ATTACH '{ruta}' AS destino")
    base.con.execute("COPY FROM DATABASE memory TO destino")
    base.con.execute("DETACH destino")
    carpeta = tmp_path / "raw"
    carpeta.mkdir()
    _csv(
        carpeta / "registro_fundaciones.csv",
        "denominacion;NIF;protectorado\nFundación Ejemplo;G88614565;Educación\n",
    )
    filas = contexto.cargar(ruta, carpeta, contexto.RUTA_DDL)
    assert filas["entidad_registro"] == 1
    assert filas["convenio"] == 0
    # Una segunda carga reemplaza, no duplica.
    assert contexto.cargar(ruta, carpeta, contexto.RUTA_DDL)["entidad_registro"] == 1


def _contexto(base):
    con = base.con
    con.execute(
        "INSERT INTO organo (organo_id, nombre) VALUES ('CONSEJERIA DE SANIDAD', 'Sanidad')"
    )
    for fase, importe in (("Crédito actual", 120.0), ("Obligaciones reconocidas", 100.0)):
        con.execute(
            "INSERT INTO presupuesto_organo VALUES (2024, 'liquidado', ?, 'Consejería de Sanidad', "
            "'CONSEJERIA DE SANIDAD', ?, 'ckan_cm', ?, ?)",
            [fase, importe, URL, HOY],
        )
    con.execute(
        "INSERT INTO convenio (convenio_id, consejeria, referencia, titulo, fecha_firma, "
        "con_financiacion, fuente, url_origen, fecha_descarga) VALUES "
        "('convenio:1', 'CONSEJERÍA DE SANIDAD', '1/2025', 'Prácticas', '2025-01-02', true, "
        "'transparencia_cm', ?, ?)",
        [URL, HOY],
    )
    con.execute(
        "INSERT INTO entidad_registro VALUES ('B12345678', 'transparencia', 'Empresa', "
        "'Consultoras', 'Activa', 'ckan_cm', ?, ?)",
        [URL, HOY],
    )
    con.execute(
        "INSERT INTO serie_cm VALUES ('s', 'Serie', 2024, 'c', NULL, 1, 'Euros', 1, "
        "NULL, 'ckan_cm', ?, ?)",
        [URL, HOY],
    )
    con.execute(
        "INSERT INTO plantilla_organismo VALUES ('SANIDAD', NULL, 3, 'ckan_cm', ?, ?)", [URL, HOY]
    )
    return con


def test_consultas_del_contexto(base):
    con = _contexto(base)
    assert dc.hay_contexto(con)
    assert dc.anios_liquidados(con) == [2024]
    filas = dc.ejecucion_consejerias(con, 2024)
    assert filas[0]["obligaciones"] == 100.0
    assert filas[0]["url_origen"] == URL
    assert dc.ejecucion_organo(con, "CONSEJERIA DE SANIDAD")[0]["credito_actual"] == 120.0
    assert dc.ejecucion_organo(con, "ORG") == []
    assert dc.convenios_por_consejeria(con)[0]["n"] == 1
    assert len(dc.lista_convenios(con, solo_con_financiacion=True)) == 1
    assert dc.registros_de_empresa(con, "B12345678")[0]["registro"] == "transparencia"
    assert dc.registros_de_empresa(con, None) == []
    assert dc.fechas_contexto(con)
    # Series: gasto por capítulo, gastos e ingresos iniciales, ingresos y personal.
    for concepto, dimension in (
        (
            "Gastos de personal consolidados en fase de obligaciones reconocidas",
            "Obligaciones reconocidas",
        ),
    ):
        con.execute(
            "INSERT INTO serie_cm VALUES (?, 'S', 2024, ?, ?, 5, 'Euros', 5, NULL, 'ckan_cm', ?, ?)",
            [dc.SERIE_GASTOS_CAPITULO, concepto, dimension, URL, HOY],
        )
    assert dc.gasto_por_capitulo(con)[0]["capitulo"] == "Personal"
    assert dc.gastos_e_ingresos_iniciales(con) == []
    assert dc.ingresos_por_capitulo(con, 2024) == []
    assert dc.personal_por_area(con) == []
    assert dc.plantilla(con)[0]["n_puestos"] == 3
    assert dc.empresas_en_registros(con)[0]["n_entidades"] == 1
    assert dc.entidades_registradas_con_contratos(con, "transparencia") == []


def test_sin_contexto_se_avisa(base):
    assert not dc.hay_contexto(base.con)
    assert dc.fechas_contexto(base.con) == []
