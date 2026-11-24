from datetime import date

import duckdb
import pytest

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
    duckdb.connect(str(ruta_db)).close()  # la base ya construida
    for _ in range(2):
        assert cpv.cargar(ruta_db, _lista(tmp_path)) == 2
    with duckdb.connect(str(ruta_db), read_only=True) as con:
        assert con.execute("SELECT nombre FROM cpv WHERE codigo = '33100000'").fetchall() == [
            ("Equipamiento médico",)
        ]


RECHAZO = (
    b"<html><head><title>Request Rejected</title></head><body>The requested URL was rejected."
    b"</body></html>"
)


class _Respuesta:
    def __init__(self, contenido: bytes):
        self.content = contenido

    def raise_for_status(self):
        pass


def test_no_guarda_la_pagina_de_rechazo_del_portal(tmp_path, monkeypatch):
    monkeypatch.setattr(cpv.httpx, "get", lambda *a, **k: _Respuesta(RECHAZO))
    destino = tmp_path / "CPV2008-2.04.gc"
    with pytest.raises(cpv.ListaNoValida, match="Request Rejected"):
        cpv.descargar(destino)
    assert not destino.exists()


def test_rehace_una_cache_que_no_es_la_lista(tmp_path, monkeypatch):
    destino = tmp_path / "CPV2008-2.04.gc"
    destino.write_bytes(RECHAZO)  # lo que guardaban las versiones anteriores
    monkeypatch.setattr(cpv.httpx, "get", lambda *a, **k: _Respuesta(LISTA.encode()))
    assert cpv.descargar(destino) == destino
    assert cpv.es_lista(destino.read_bytes())


def test_no_crea_una_base_vacia(tmp_path):
    with pytest.raises(FileNotFoundError):
        cpv.cargar(tmp_path / "no_existe.duckdb", _lista(tmp_path))
    assert not (tmp_path / "no_existe.duckdb").exists()


def test_avisa_si_la_base_esta_abierta(tmp_path, monkeypatch):
    ruta_db = tmp_path / "base.duckdb"
    duckdb.connect(str(ruta_db)).close()

    def ocupada(*a, **k):
        raise duckdb.IOException("File is already open in python.exe")

    monkeypatch.setattr(cpv.duckdb, "connect", ocupada)
    with pytest.raises(RuntimeError, match="para la web"):
        cpv.cargar(ruta_db, _lista(tmp_path))
