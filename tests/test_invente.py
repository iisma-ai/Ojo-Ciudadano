import json
from datetime import date

import duckdb

from ojo_ciudadano.ingesta import invente

INVENTARIO = {
    "Total": 4,
    "EntidadesSPI": [
        {
            "CodigoInvente": "INV1",
            "DenominacionSocial": "Canal de Isabel II, Sociedad Anónima, M.P.",
            "FormaJuridica_Descripcion": "Sociedad mercantil",
            "NIF": "A86488087",
            "codigoDir3": "A13037475",
            "codigoOrigen": "1200000BP001",
        },
        {
            "CodigoInvente": "INV2",
            "DenominacionSocial": "Empresa Municipal de Transportes de Madrid",
            "FormaJuridica_Descripcion": "Sociedad mercantil",
            "NIF": "A-28046316",
            "codigoDir3": "",
            "codigoOrigen": "1228079AP001",
        },
        {
            "CodigoInvente": "INV3",
            "DenominacionSocial": "Universidad Complutense de Madrid",
            "FormaJuridica_Descripcion": "Universidad pública",
            "NIF": "Q2818011E",
            "codigoDir3": "",
            "codigoOrigen": "OE123",
        },
        {
            "CodigoInvente": "INV4",
            "DenominacionSocial": "Ente sin NIF",
            "FormaJuridica_Descripcion": "Consorcio",
            "NIF": "",
            "codigoOrigen": "0900000BC001",
        },
    ],
}


def _fichero(tmp_path):
    ruta = tmp_path / "entidades_spi.json"
    ruta.write_text(json.dumps(INVENTARIO), encoding="utf-8")
    return ruta


def test_lee_entes_con_nif_normalizado_y_administracion(tmp_path):
    tabla = invente.leer(_fichero(tmp_path), date(2026, 11, 23))
    assert tabla["nif"].to_list() == ["A28046316", "A86488087", "Q2818011E"]  # sin el que no tiene
    por_nif = {f["nif"]: f for f in tabla.iter_rows(named=True)}
    assert por_nif["A86488087"]["administracion"] == "Comunidad de Madrid"
    assert por_nif["A28046316"]["administracion"] == "Entidad local de Madrid"
    assert por_nif["Q2818011E"]["administracion"] == "Estado"
    assert por_nif["A86488087"]["fuente"] == "invente"
    assert por_nif["A86488087"]["fecha_descarga"] == date(2026, 11, 23)


def test_administracion_de_otras_comunidades():
    assert invente.administracion("0900000BC001") == "Otra comunidad autónoma"
    assert invente.administracion("0908019AP001") == "Entidad local de otra comunidad"
    assert invente.administracion(None) is None


def test_nombres_compatibles():
    assert invente.nombres_compatibles("CANAL DE ISABEL II S.A.", "Canal de Isabel II, S.A., M.P.")
    assert not invente.nombres_compatibles("PIXELWARE, S.A.", "Planifica Madrid, Proyectos y Obras")
    # Solo palabras genéricas en común no basta.
    assert not invente.nombres_compatibles("EMPRESA MUNICIPAL X SA", "Empresa Municipal Y, S.A.")


def test_carga_en_una_base_existente(tmp_path):
    ruta_db = tmp_path / "base.duckdb"
    for _ in range(2):
        assert invente.cargar(ruta_db, _fichero(tmp_path)) == 3
    with duckdb.connect(str(ruta_db), read_only=True) as con:
        fila = con.execute(
            "SELECT forma_juridica FROM entidad_sector_publico WHERE nif = 'Q2818011E'"
        ).fetchall()
    assert fila == [("Universidad pública",)]
