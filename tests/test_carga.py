from datetime import date
from pathlib import Path

import duckdb
import polars as pl

from ojo_ciudadano.modelo import carga

HOY = date(2026, 11, 16)
ESQUEMA = Path(__file__).parent.parent / "sql" / "esquema"


def _portal():
    """Tablas como las que devuelve portal_cm.leer: un menor y una licitación."""
    contratos = pl.DataFrame(
        {
            "contrato_id": ["portal_cm:D1", "portal_cm:C7"],
            "fuente": ["portal_cm"] * 2,
            "referencia": ["D1", "C7"],
            "expediente": ["CM-1/2026", "EXP-1"],
            "organo_nombre": ["Hospital de Ejemplo"] * 2,
            "organo_jerarquia": [
                "Consejería de Pruebas··>Hospital de Ejemplo",
                "Hospital de Ejemplo",
            ],
            "consejeria": ["Consejería de Pruebas", None],
            "titulo": ["Material", "Limpieza"],
            "tipo_publicacion": ["Contratos menores", "Convocatoria anunciada a licitación"],
            "tipo_contrato": ["suministros", "servicios"],
            "procedimiento": ["Contrato menor", "Abierto"],
            "es_menor": [True, False],
            "estado": ["Resuelto", "Resuelta / Finalizada"],
            "resultado": ["Formalizado", "Resuelta"],
            "presupuesto_con_iva": [1210.0, 121000.0],
            "fecha_contrato": [date(2026, 2, 11), date(2025, 1, 23)],
            "url_origen": [
                "https://contratos-publicos.comunidad.madrid/contrato/D1",
                "https://contratos-publicos.comunidad.madrid/contrato/C7",
            ],
            "fecha_descarga": [HOY] * 2,
        }
    )
    adjudicaciones = pl.DataFrame(
        {
            "contrato_id": ["portal_cm:D1", "portal_cm:C7"],
            "orden": pl.Series([1, 1], dtype=pl.Int32),
            "adjudicatario_id": ["B11111111", "A22222222"],
            "nif": ["B11111111", "A22222222"],
            "nombre": ["EMPRESA UNO, S.L.", "EMPRESA DOS, S.A."],
            "tipo_persona": ["juridica"] * 2,
            "n_ofertas": [3, 2],
            "importe_con_iva": [1210.0, 96800.0],
            "importe_modificaciones_con_iva": [None, 0.0],
            "importe_prorrogas_con_iva": [None, 12100.0],
            "importe_liquidacion_con_iva": [None, 0.0],
            "fuente": ["portal_cm"] * 2,
            "url_origen": [
                "https://contratos-publicos.comunidad.madrid/contrato/D1",
                "https://contratos-publicos.comunidad.madrid/contrato/C7",
            ],
            "fecha_descarga": [HOY] * 2,
        }
    )
    return {"contratos": contratos, "adjudicaciones": adjudicaciones}


def _placsp():
    """Tablas como las que devuelve placsp.leer_zips: la misma licitación EXP-1."""
    contratos = pl.DataFrame(
        {
            "contrato_id": ["placsp:100"],
            "fuente": ["placsp"],
            "expediente": ["EXP-1"],
            "organo_codigo": ["A00000001"],
            "organo_nombre": ["HOSPITAL DE EJEMPLO"],
            "organo_jerarquia": ["Consejería de Pruebas··>HOSPITAL DE EJEMPLO"],
            "consejeria": ["Consejería de Pruebas"],
            "titulo": ["Limpieza"],
            "tipo_contrato": ["servicios"],
            "procedimiento": ["Abierto"],
            "es_menor": [False],
            "estado": ["Resuelta"],
            "cpv": ["90910000"],
            "presupuesto_sin_iva": [100000.0],
            "valor_estimado": [120000.0],
            "fecha_fin_plazo": [date(2024, 12, 1)],
            "fecha_actualizacion": ["2025-02-01T10:00:00+01:00"],
            "url_origen": ["https://contratos-publicos.comunidad.madrid/contrato-publico/limpieza"],
            "fecha_descarga": [HOY],
        }
    )
    adjudicaciones = pl.DataFrame(
        {
            "contrato_id": ["placsp:100"],
            "orden": pl.Series([1], dtype=pl.Int32),
            "lote": [None],
            "adjudicatario_id": ["A22222222"],
            "nif": ["A22222222"],
            "nombre": ["EMPRESA DOS SA"],
            "tipo_persona": ["juridica"],
            "n_ofertas": [2],
            "resultado": ["Formalizado"],
            "importe_sin_iva": [80000.0],
            "fecha_formalizacion": [date(2025, 1, 23)],
            "fuente": ["placsp"],
            "url_origen": ["https://contratos-publicos.comunidad.madrid/contrato-publico/limpieza"],
            "fecha_descarga": [HOY],
        },
        schema_overrides={"lote": pl.String},
    )
    return {"contratos": contratos, "adjudicaciones": adjudicaciones}


def test_la_licitacion_del_portal_se_marca_como_duplicada_de_placsp():
    contrato = carga.unificar([_portal()], _placsp())["contrato"]
    duplicados = dict(zip(contrato["contrato_id"], contrato["duplicado_de"], strict=True))
    assert duplicados == {"placsp:100": None, "portal_cm:D1": None, "portal_cm:C7": "placsp:100"}


def test_un_organo_y_un_adjudicatario_por_identificador():
    tablas = carga.unificar([_portal()], _placsp())
    assert tablas["organo"]["organo_id"].to_list() == ["HOSPITAL DE EJEMPLO"]
    assert tablas["organo"]["codigo_placsp"].to_list() == ["A00000001"]
    assert tablas["organo"]["consejeria"].to_list() == ["Consejería de Pruebas"]
    assert tablas["adjudicatario"]["adjudicatario_id"].to_list() == ["A22222222", "B11111111"]


def test_sin_placsp_no_hay_duplicados():
    contrato = carga.unificar([_portal()], None)["contrato"]
    assert contrato.height == 2
    assert contrato["duplicado_de"].null_count() == 2


def test_la_base_se_crea_con_el_esquema_y_la_vista_no_repite(tmp_path):
    ruta = tmp_path / "prueba.duckdb"
    carga.escribir(carga.unificar([_portal()], _placsp()), ruta, ESQUEMA)
    con = duckdb.connect(str(ruta), read_only=True)
    try:
        assert con.execute("SELECT count(*) FROM contrato").fetchone()[0] == 3
        assert con.execute("SELECT count(*) FROM contrato_unico").fetchone()[0] == 2
        assert con.execute("SELECT count(*) FROM adjudicacion").fetchone()[0] == 3
        # Toda tabla de hechos lleva fuente, URL de origen y fecha de descarga.
        for tabla in ("contrato", "adjudicacion"):
            sin_origen = con.execute(
                f"SELECT count(*) FROM {tabla} "
                "WHERE fuente IS NULL OR url_origen IS NULL OR fecha_descarga IS NULL"
            ).fetchone()[0]
            assert sin_origen == 0
    finally:
        con.close()


def test_financiacion_ue_se_carga_solo_si_la_entrada_la_trae(tmp_path):
    placsp = _placsp()
    placsp["contratos"] = placsp["contratos"].with_columns(
        pl.lit(True).alias("financiado_ue"), pl.lit("PRTR,FEDER").alias("programas_ue")
    )
    ruta = tmp_path / "prueba.duckdb"
    carga.escribir(carga.unificar([_portal()], placsp), ruta, ESQUEMA)
    con = duckdb.connect(str(ruta), read_only=True)
    try:
        filas = con.execute(
            "SELECT contrato_id, financiado_ue, programas_ue, fuente FROM contrato_financiacion"
        ).fetchall()
    finally:
        con.close()
    assert filas == [("placsp:100", True, "PRTR,FEDER", "placsp")]


def test_encargos_van_a_su_tabla_y_no_a_contrato(tmp_path):
    encargos = pl.DataFrame(
        {
            "encargo_id": ["portal_cm:C8000"],
            "orden": pl.Series([1], dtype=pl.Int32),
            "fuente": ["portal_cm"],
            "expediente": ["EG/2025/1"],
            "referencia_portal": ["C8000"],
            "organo_nombre": ["Consejería de Encargos"],
            "organo_jerarquia": [None],
            "consejeria": [None],
            "titulo": ["Apoyo técnico"],
            "tipo_contrato": ["servicios"],
            "anio_publicacion": pl.Series([2025], dtype=pl.Int32),
            "medio_propio_id": ["A28476208"],
            "importe_con_iva": [1_000_000.0],
            "importe_modificaciones_con_iva": [0.0],
            "url_origen": ["https://contratos-publicos.comunidad.madrid/contrato/C8000"],
            "fecha_descarga": [HOY],
        },
        schema_overrides={"organo_jerarquia": pl.String, "consejeria": pl.String},
    )
    medios = pl.DataFrame(
        {
            "adjudicatario_id": ["A28476208"],
            "nif": ["A28476208"],
            "nombre": ["TRAGSA"],
            "tipo_persona": ["juridica"],
        }
    )
    tablas = {"encargos": encargos, "medios_propios": medios}
    ruta = tmp_path / "prueba.duckdb"
    carga.escribir(carga.unificar([_portal()], _placsp(), None, tablas), ruta, ESQUEMA)
    con = duckdb.connect(str(ruta), read_only=True)
    try:
        assert con.execute("SELECT count(*) FROM encargo").fetchone()[0] == 1
        assert con.execute("SELECT count(*) FROM contrato").fetchone()[0] == 3
        organo = con.execute("SELECT o.nombre FROM encargo e JOIN organo o USING (organo_id)")
        assert organo.fetchone()[0] == "Consejería de Encargos"
    finally:
        con.close()
