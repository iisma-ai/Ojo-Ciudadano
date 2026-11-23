from datetime import date

import polars as pl
from test_portal_cm import CABECERA

from ojo_ciudadano.ingesta import encargos

# Datos sintéticos con la forma de la exportación real: sin fecha del contrato.
FILAS = [
    # Publicado en 2025 (referencia dentro del tramo de 2025).
    '"Encargos a medios propios";;"Consejería de Pruebas";EG/2025/1;C8000;"Apoyo técnico";'
    'Servicios;"Otro procedimiento";;;Resuelta;A28476208;"TRAGSA, S.A.";;"1.000.000,00";0,00;0,00;0,00',
    # Publicado antes de 2023: referencia sin la forma C<número>.
    '"Encargos a medios propios";;"Consejería de Pruebas";E-2019;2456273;"Antiguo";'
    'Servicios;"Otro procedimiento";;;Resuelta;A28476208;"TRAGSA, S.A.";;"5,00";0,00;0,00;0,00',
    # Medio propio con NIF de persona física: sin nombre ni NIF (D-007).
    '"Encargos a medios propios";;"Consejería de Pruebas";EG/2026/2;C12000;"Otro";'
    'Servicios;"Otro procedimiento";;;Resuelta;12345678Z;"NOMBRE APELLIDO";;"10,00";0,00;0,00;0,00',
]


def _leer(tmp_path):
    ruta = tmp_path / "encargos_todo_2026-11-23.csv"
    ruta.write_bytes(("\r\n".join([CABECERA, *FILAS]) + "\r\n").encode("utf-8-sig"))
    return encargos.leer(ruta, date(2026, 11, 23), sal=b"sal-de-prueba")


def test_anio_de_publicacion_por_referencia():
    refs = pl.Series(["C276", "C3789", "C3886", "C11886", "C15761", "C100", "2456273"])
    anios = pl.select(encargos.anio_publicacion(pl.lit(refs))).to_series().to_list()
    assert anios == [2023, 2023, 2024, 2025, 2026, None, None]


def test_solo_encargos_de_2023_a_2026(tmp_path):
    tabla = _leer(tmp_path)["encargos"]
    assert tabla["encargo_id"].to_list() == ["portal_cm:C12000", "portal_cm:C8000"]
    tragsa = tabla.filter(pl.col("encargo_id") == "portal_cm:C8000").row(0, named=True)
    assert tragsa["anio_publicacion"] == 2025
    assert tragsa["medio_propio_id"] == "A28476208"
    assert tragsa["importe_con_iva"] == 1_000_000.0
    assert tragsa["orden"] == 1


def test_medio_propio_persona_fisica_sin_nombre(tmp_path):
    medios = _leer(tmp_path)["medios_propios"]
    persona = medios.filter(pl.col("adjudicatario_id").str.starts_with("PF-")).row(0, named=True)
    assert persona["nombre"] is None and persona["nif"] is None
