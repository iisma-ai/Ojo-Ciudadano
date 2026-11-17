from datetime import date

import polars as pl

from ojo_ciudadano.ingesta import portal_cm

CABECERA = (
    '"Tipo de Publicación";Estado;"Entidad Adjudicadora";"Nº Expediente";Referencia;"Título del contrato";'
    '"Tipo de contrato";"Procedimiento de adjudicación";"Presupuesto de licitación";"Nº de ofertas";Resultado;'
    '"NIF del adjudicatario";Adjudicatario;"Fecha del contrato";"Importe de adjudicación";'
    '"Importe de las modificaciones";"Importe de las prórrogas";"Importe de la liquidación"'
)
# Datos sintéticos: un menor de empresa, un menor de persona física y una licitación con dos lotes.
FILAS = [
    '"Contratos menores";Resuelto;"Consejería de Pruebas··>Hospital de Ejemplo";CM-1/2026;D1_1;"Material de oficina";'
    'Suministro;"Contrato menor";"1.210,00";3;Formalizado;b-11111111;"EMPRESA UNO, S.L.";'
    '"11 de febrero del 2026";"1.210,00";;;',
    '"Contratos menores";Resuelto;"Consejería de Pruebas";CM-2/2026;D1_2;"Ponencia";Servicios;"Contrato menor";'
    '400,00;;Formalizado;12345678Z;"NOMBRE APELLIDO";"05 de marzo del 2026";400,00;;;',
    '"Convocatoria anunciada a licitación";"Resuelta / Finalizada";"Hospital de Ejemplo";PA-3/2025;C77;'
    '"Servicio de limpieza";Servicios;Abierto;121000.0;2;Resuelta;A22222222;"EMPRESA DOS, S.A.";'
    '"23 de enero del 2025";"60.500,00";"0,00";"12.100,00";"0,00"',
    ';;;;;;;;;1;;" B33333333";"EMPRESA TRES, S.L.";;"36.300,00";"0,00";"0,00";"0,00"',
]


def _leer(tmp_path, filas=FILAS):
    ruta = tmp_path / "export.csv"
    # utf-8-sig y write_bytes para conservar el BOM y los CRLF tal como los exporta el portal.
    ruta.write_bytes(("\r\n".join([CABECERA, *filas]) + "\r\n").encode("utf-8-sig"))
    return portal_cm.leer(ruta, date(2026, 11, 16), sal=b"sal-de-prueba")


def _fila(tabla, columna, valor):
    return tabla.filter(pl.col(columna) == valor).row(0, named=True)


def test_un_contrato_por_fila_de_cabecera(tmp_path):
    contratos = _leer(tmp_path)["contratos"]
    assert contratos.height == 3
    assert set(contratos["contrato_id"]) == {"portal_cm:D1_1", "portal_cm:D1_2", "portal_cm:C77"}


def test_campos_del_contrato(tmp_path):
    contratos = _leer(tmp_path)["contratos"]
    menor = _fila(contratos, "referencia", "D1_1")
    assert menor["es_menor"] is True
    assert menor["organo_nombre"] == "Hospital de Ejemplo"
    assert menor["consejeria"] == "Consejería de Pruebas"
    assert menor["tipo_contrato"] == "suministros"
    assert menor["presupuesto_con_iva"] == 1210.0
    assert menor["fecha_contrato"] == date(2026, 2, 11)
    licitacion = _fila(contratos, "referencia", "C77")
    assert licitacion["es_menor"] is False
    assert licitacion["consejeria"] is None
    assert licitacion["presupuesto_con_iva"] == 121000.0


def test_toda_fila_lleva_fuente_url_y_fecha_de_descarga(tmp_path):
    for tabla in _leer(tmp_path).values():
        assert tabla["fuente"].unique().to_list() == ["portal_cm"]
        assert tabla["fecha_descarga"].unique().to_list() == [date(2026, 11, 16)]
        assert tabla["url_origen"].null_count() == 0
        assert (
            tabla["url_origen"]
            .str.starts_with("https://contratos-publicos.comunidad.madrid/contrato/")
            .all()
        )


def test_las_filas_de_continuacion_son_adjudicaciones_del_mismo_contrato(tmp_path):
    adjudicaciones = _leer(tmp_path)["adjudicaciones"]
    lotes = adjudicaciones.filter(adjudicaciones["contrato_id"] == "portal_cm:C77").sort("orden")
    assert lotes["adjudicatario_id"].to_list() == ["A22222222", "B33333333"]
    assert lotes["orden"].to_list() == [1, 2]
    assert lotes["importe_con_iva"].to_list() == [60500.0, 36300.0]
    assert lotes["n_ofertas"].to_list() == [2, 1]
    assert lotes["importe_prorrogas_con_iva"].to_list() == [12100.0, 0.0]


def test_la_persona_fisica_no_aparece_con_nif_ni_nombre(tmp_path):
    tablas = _leer(tmp_path)
    fila = _fila(tablas["adjudicaciones"], "contrato_id", "portal_cm:D1_2")
    assert fila["tipo_persona"] == "fisica"
    assert fila["nif"] is None
    assert fila["nombre"] is None
    assert fila["adjudicatario_id"].startswith("PF-")
    for tabla in tablas.values():
        assert "12345678Z" not in tabla.write_csv()
        assert "NOMBRE APELLIDO" not in tabla.write_csv()


def test_nif_de_empresa_normalizado(tmp_path):
    adjudicaciones = _leer(tmp_path)["adjudicaciones"]
    fila = _fila(adjudicaciones, "contrato_id", "portal_cm:D1_1")
    assert fila["nif"] == "B11111111"
    assert fila["nombre"] == "EMPRESA UNO, S.L."
    assert fila["importe_modificaciones_con_iva"] is None


def test_contrato_sin_referencia_no_se_carga(tmp_path):
    sin_referencia = (
        '"Convocatoria anunciada a licitación";"Resuelta / Finalizada";"Hospital de Ejemplo";PA-9/2019;;'
        '"Sin ficha";Servicios;Abierto;1000.0;1;Resuelta;A22222222;"EMPRESA DOS, S.A.";;"900,00";"0,00";"0,00";"0,00"'
    )
    tablas = _leer(tmp_path, [FILAS[0], sin_referencia])
    assert tablas["contratos"]["contrato_id"].to_list() == ["portal_cm:D1_1"]
    assert tablas["adjudicaciones"]["contrato_id"].to_list() == ["portal_cm:D1_1"]
