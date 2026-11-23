from ojo_ciudadano.ingesta import tacp

# Fragmento con la estructura real del listado del buscador del Tribunal.
PAGINA = """<div class="view-content"><div class="item-list"> 5 registros de 451 <ul>
<li class="views-row views-row-1">
<div class="views-field views-field-field-numero-de-resolucion"><span class="field-content">
<span class="field-content"><a href="/tacp/resolucion/5782026">578/2026</a></span></span></div>
<div class="views-field views-field-field-fecha"><span class="field-content">
<span class="date-display-single" content="2026-11-13T00:00:00+01:00">13/11/2026</span></span></div>
<div class="views-field views-field-body">  <span class="field-content">Desestimación del recurso
contra la adjudicación del contrato «Servicios de mantenimiento», BAC01/2026, años 2029-2030.
</span>  </div>
<div class="views-field views-field-field-documento"><span class="field-content"><span class="file">
<a href="/tacp/file/8865/download?token=abc" type="application/pdf">resolucion_578-2026_expediente_560-2026.pdf</a>
</span></span></div></li></ul></div></div>"""


def test_leer_pagina():
    (fila,) = tacp.leer_pagina(PAGINA, "1", "35", "56")
    assert fila["resolucion_id"] == "tacpcm:578/2026"
    assert fila["fecha"].isoformat() == "2026-11-13"
    assert fila["procedencia"] == "Consejerías"
    assert fila["tipo_resolucion"] == "Desestimatoria"
    assert fila["acto_recurrido"] == "Adjudicación"
    assert "BAC01/2026" in fila["expedientes_citados"]
    assert fila["url_origen"] == "https://www.comunidad.madrid/tacp/resolucion/5782026"
    assert fila["url_documento"].endswith("/tacp/file/8865/download?token=abc")


def test_pagina_sin_resultados():
    assert tacp.leer_pagina("<html>NO HAY RESULTADOS</html>", "1", "35", "56") == []


def test_resolucion_repetida_une_las_etiquetas(tmp_path):
    (tmp_path / "p1_t41_a17_000.html").write_text(PAGINA, encoding="utf-8")
    (tmp_path / "p1_t41_a56_000.html").write_text(PAGINA, encoding="utf-8")
    (tmp_path / "p1_t41_a56_001.html").write_text(PAGINA, encoding="utf-8")
    tabla = tacp.leer(tmp_path)
    assert tabla.height == 1
    assert tabla.row(0, named=True)["acto_recurrido"] == "Exclusión; Adjudicación"


def test_numeros_de_ley_no_son_expedientes():
    citados = tacp.expedientes_citados("LEY 9/2017, EXPEDIENTE A/SER-025050/2026 Y 129-2025")
    assert citados == ["A/SER-025050/2026", "129-2025"]
