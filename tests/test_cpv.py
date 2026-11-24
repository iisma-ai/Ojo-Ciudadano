from datetime import date

import duckdb

from ojo_ciudadano.ingesta import cpv

LISTA = """<?xml version="1.0" encoding="UTF-8"?>
<gc:CodeList xmlns:gc="http://docs.oasis-open.org/codelist/ns/genericode/1.0/">
  <SimpleCodeList>
    <Row>
      <Value ColumnRef="code"><SimpleValue>33000000</SimpleValue></Value>
      <Value ColumnRef="nombre"><SimpleValue>Equipamiento y art&#237;culos m&#233;dicos.</SimpleValue></Value>
      <Value ColumnRef="name"><SimpleValue>Medical equipments.</SimpleValue></Value>
    </Row>
    <Row>
      <Value ColumnRef="code"><SimpleValue>33100000</SimpleValue></Value>
      <Value ColumnRef="nombre"><SimpleValue>Equipamiento m&#233;dico.</SimpleValue></Value>
    </Row>
  </SimpleCodeList>
</gc:CodeList>"""


def _lista(tmp_path):
    ruta = tmp_path / "CPV2008-2.04.gc"
    ruta.write_text(LISTA, encoding="utf-8")
    return ruta


def test_lee_nombres_y_division(tmp_path):
    tabla = cpv.leer(_lista(tmp_path), date(2026, 11, 23))
    fila = tabla.filter(tabla["codigo"] == "33100000").row(0, named=True)
    assert fila["nombre"] == "Equipamiento médico"  # sin el punto final
    assert fila["division"] == "33"
    assert fila["nombre_division"] == "Equipamiento y artículos médicos"
    assert fila["fuente"] == "placsp" and fila["url_origen"] == cpv.URL
    assert fila["fecha_descarga"] == date(2026, 11, 23)


def test_carga_en_una_base_existente_y_se_puede_repetir(tmp_path):
    ruta_db = tmp_path / "base.duckdb"
    for _ in range(2):
        assert cpv.cargar(ruta_db, _lista(tmp_path)) == 2
    with duckdb.connect(str(ruta_db), read_only=True) as con:
        assert con.execute("SELECT nombre FROM cpv WHERE codigo = '33100000'").fetchall() == [
            ("Equipamiento médico",)
        ]
