import zipfile
from datetime import date

from ojo_ciudadano.ingesta import placsp

SAL = b"sal-de-prueba"
CABECERA = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:at="http://purl.org/atompub/tombstones/1.0"
      xmlns:cbc="urn:dgpe:names:draft:codice:schema:xsd:CommonBasicComponents-2"
      xmlns:cac="urn:dgpe:names:draft:codice:schema:xsd:CommonAggregateComponents-2"
      xmlns:cac-place-ext="urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonAggregateComponents-2"
      xmlns:cbc-place-ext="urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonBasicComponents-2">
"""


def _entrada(
    numero,
    expediente,
    actualizado,
    estado,
    resultados="",
    dominio="contratos-publicos.comunidad.madrid",
    fondos="",
):
    """Entrada Atom sintética con la misma estructura que las de PLACSP."""
    return f"""
<entry>
  <id>https://contrataciondelestado.es/sindicacion/PlataformasAgregadasSinMenores/{numero}</id>
  <link href="https://{dominio}/contrato-publico/ejemplo-{numero}"/>
  <title>Título {expediente}</title>
  <updated>{actualizado}</updated>
  <cac-place-ext:ContractFolderStatus>
    <cbc:ContractFolderID>{expediente}</cbc:ContractFolderID>
    <cbc-place-ext:ContractFolderStatusCode>{estado}</cbc-place-ext:ContractFolderStatusCode>
    <cac-place-ext:LocatedContractingParty>
      <cac:Party>
        <cac:PartyIdentification><cbc:ID schemeName="ID_OC_PLAT">A00000001</cbc:ID></cac:PartyIdentification>
        <cac:PartyName><cbc:Name>Hospital de Ejemplo</cbc:Name></cac:PartyName>
      </cac:Party>
      <cac-place-ext:ParentLocatedParty>
        <cac:PartyName><cbc:Name>Consejería de Pruebas</cbc:Name></cac:PartyName>
        <cac-place-ext:ParentLocatedParty>
          <cac:PartyName><cbc:Name>Servicio de Ejemplo</cbc:Name></cac:PartyName>
        </cac-place-ext:ParentLocatedParty>
      </cac-place-ext:ParentLocatedParty>
    </cac-place-ext:LocatedContractingParty>
    <cac:ProcurementProject>
      <cbc:Name>Suministro de prueba {expediente}</cbc:Name>
      <cbc:TypeCode>1</cbc:TypeCode>
      <cac:BudgetAmount>
        <cbc:EstimatedOverallContractAmount currencyID="EUR">120000</cbc:EstimatedOverallContractAmount>
        <cbc:TaxExclusiveAmount currencyID="EUR">100000.5</cbc:TaxExclusiveAmount>
      </cac:BudgetAmount>
      <cac:RequiredCommodityClassification>
        <cbc:ItemClassificationCode>33100000</cbc:ItemClassificationCode>
      </cac:RequiredCommodityClassification>
    </cac:ProcurementProject>
    <cac:TenderingProcess>
      <cbc:ProcedureCode>1</cbc:ProcedureCode>
      <cac:TenderSubmissionDeadlinePeriod><cbc:EndDate>2026-09-30</cbc:EndDate></cac:TenderSubmissionDeadlinePeriod>
    </cac:TenderingProcess>
    {fondos}
    {resultados}
  </cac-place-ext:ContractFolderStatus>
</entry>"""


def _resultado(lote, nif, nombre, ofertas, importe, codigo="9"):
    return f"""
    <cac:TenderResult>
      <cbc:ResultCode>{codigo}</cbc:ResultCode>
      <cbc:ReceivedTenderQuantity>{ofertas}</cbc:ReceivedTenderQuantity>
      <cac:Contract><cbc:ID>C-{lote}</cbc:ID><cbc:IssueDate>2026-10-10</cbc:IssueDate></cac:Contract>
      <cac:WinningParty>
        <cac:PartyIdentification><cbc:ID schemeName="NIF">{nif}</cbc:ID></cac:PartyIdentification>
        <cac:PartyName><cbc:Name>{nombre}</cbc:Name></cac:PartyName>
      </cac:WinningParty>
      <cac:AwardedTenderedProject>
        <cbc:ProcurementProjectLotID>{lote}</cbc:ProcurementProjectLotID>
        <cac:LegalMonetaryTotal><cbc:TaxExclusiveAmount currencyID="EUR">{importe}</cbc:TaxExclusiveAmount></cac:LegalMonetaryTotal>
      </cac:AwardedTenderedProject>
    </cac:TenderResult>"""


FONDOS_PRTR = """<cac:TenderingTerms>
      <cbc:FundingProgramCode name="Financiación con fondos de la UE">EU</cbc:FundingProgramCode>
      <cbc:FundingProgramCode name="Asociado al Plan de Recuperacion">PRTR</cbc:FundingProgramCode>
    </cac:TenderingTerms>"""


def _zip(tmp_path, ficheros):
    ruta = tmp_path / "PlataformasAgregadasSinMenores_202610.zip"
    with zipfile.ZipFile(ruta, "w") as z:
        for nombre, entradas in ficheros.items():
            z.writestr(nombre, (CABECERA + "".join(entradas) + "\n</feed>").encode("utf-8"))
    return ruta


def _leer(tmp_path):
    adjudicada = _resultado(1, "A22222222", "EMPRESA DOS, S.A.", 1, 40000) + _resultado(
        2, "12345678Z", "NOMBRE APELLIDO", 3, 50000.25
    )
    ruta = _zip(
        tmp_path,
        {
            # Primera versión del expediente EXP-1 (en evaluación) y una entrada de otra comunidad.
            "a_20261001.atom": [
                _entrada(100, "EXP-1", "2026-10-01T10:00:00+02:00", "EV"),
                _entrada(
                    200,
                    "OTRA-1",
                    "2026-10-01T10:00:00+02:00",
                    "PUB",
                    dominio="contractaciopublica.cat",
                ),
            ],
            # Versión posterior de EXP-1, ya resuelta, y un segundo expediente.
            "b_20261015.atom": [
                _entrada(100, "EXP-1", "2026-10-15T12:00:00+02:00", "RES", adjudicada),
                _entrada(300, "EXP-2", "2026-10-15T09:00:00+02:00", "PUB", fondos=FONDOS_PRTR),
            ],
        },
    )
    return placsp.leer_zips([ruta], date(2026, 11, 16), SAL)


def test_solo_entradas_de_la_comunidad_de_madrid_y_ultima_version(tmp_path):
    contratos = _leer(tmp_path)["contratos"]
    assert contratos["expediente"].to_list() == ["EXP-1", "EXP-2"]
    exp1 = contratos.row(0, named=True)
    assert exp1["contrato_id"] == "placsp:100"
    assert exp1["estado"] == "Resuelta"


def test_campos_del_contrato(tmp_path):
    exp1 = _leer(tmp_path)["contratos"].row(0, named=True)
    assert exp1["organo_codigo"] == "A00000001"
    assert exp1["organo_nombre"] == "Hospital de Ejemplo"
    assert exp1["consejeria"] == "Consejería de Pruebas"
    assert (
        exp1["organo_jerarquia"]
        == "Consejería de Pruebas··>Servicio de Ejemplo··>Hospital de Ejemplo"
    )
    assert exp1["tipo_contrato"] == "suministros"
    assert exp1["procedimiento"] == "Abierto"
    assert exp1["es_menor"] is False
    assert exp1["cpv"] == "33100000"
    assert exp1["presupuesto_sin_iva"] == 100000.5
    assert exp1["valor_estimado"] == 120000.0
    assert exp1["fecha_fin_plazo"] == date(2026, 9, 30)
    assert exp1["fuente"] == "placsp"
    assert (
        exp1["url_origen"]
        == "https://contratos-publicos.comunidad.madrid/contrato-publico/ejemplo-100"
    )
    assert exp1["fecha_descarga"] == date(2026, 11, 16)


def test_adjudicaciones_por_lote_de_la_ultima_version(tmp_path):
    adjudicaciones = _leer(tmp_path)["adjudicaciones"]
    assert adjudicaciones["contrato_id"].to_list() == ["placsp:100", "placsp:100"]
    assert adjudicaciones["lote"].to_list() == ["1", "2"]
    assert adjudicaciones["n_ofertas"].to_list() == [1, 3]
    assert adjudicaciones["importe_sin_iva"].to_list() == [40000.0, 50000.25]
    assert adjudicaciones["resultado"].unique().to_list() == ["Formalizado"]
    assert adjudicaciones["fecha_formalizacion"].to_list() == [date(2026, 10, 10)] * 2
    assert adjudicaciones["url_origen"].null_count() == 0


def test_persona_fisica_seudonimizada(tmp_path):
    tablas = _leer(tmp_path)
    fisica = tablas["adjudicaciones"].row(1, named=True)
    assert fisica["tipo_persona"] == "fisica"
    assert fisica["nif"] is None
    assert fisica["nombre"] is None
    assert fisica["adjudicatario_id"].startswith("PF-")
    for tabla in tablas.values():
        assert "12345678Z" not in tabla.write_csv()
        assert "NOMBRE APELLIDO" not in tabla.write_csv()


def test_entrada_borrada_se_descarta(tmp_path):
    borrado = (
        '<at:deleted-entry ref="https://contrataciondelestado.es/sindicacion/'
        'PlataformasAgregadasSinMenores/300" when="2026-10-20T00:00:00+02:00"/>'
    )
    ruta = _zip(
        tmp_path,
        {"a.atom": [_entrada(300, "EXP-2", "2026-10-15T09:00:00+02:00", "PUB"), borrado]},
    )
    assert placsp.leer_zips([ruta], date(2026, 11, 16), SAL)["contratos"].height == 0


def test_financiacion_con_fondos_europeos(tmp_path):
    contratos = _leer(tmp_path)["contratos"]
    exp1, exp2 = contratos.row(0, named=True), contratos.row(1, named=True)
    assert exp1["financiado_ue"] is None  # la entrada no trae el campo
    assert exp2["financiado_ue"] is True
    assert exp2["programas_ue"] == "PRTR"
