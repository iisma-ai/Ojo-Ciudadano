"""Buscador de la portada: sin escribir nada ya ofrece opciones variadas."""

from ojo_ciudadano.app import buscador

ORGANOS = {
    "Consejería": [
        {"organo_id": "c1", "nombre": "Consejería de Sanidad", "n_contratos": 10},
        # contiene la palabra pero no empieza por ella: no entra en la muestra
        {"organo_id": "x", "nombre": "Secretaría de la Consejería", "n_contratos": 9},
    ],
    "Hospital": [{"organo_id": "h1", "nombre": "Hospital La Paz", "n_contratos": 50}],
}
EMPRESAS = [{"adjudicatario_id": "e1", "nombre": "Empresa A, S.A.", "nif": "A00000000"}]


def test_sin_texto_salen_consejerias_hospitales_y_empresas(monkeypatch):
    monkeypatch.setattr(buscador, "conexion", lambda: None)
    monkeypatch.setattr(
        buscador.datos, "sugerir_organos", lambda con, texto, limite: ORGANOS[texto]
    )
    monkeypatch.setattr(buscador.datos, "sugerir_empresas", lambda con, texto, limite: EMPRESAS)
    opciones = buscador._todo("")
    assert [valor for _, valor in opciones] == ["organo:c1", "organo:h1", "empresa:e1"]
    assert opciones[0][0] == "Organismo · Consejería de Sanidad"
    assert opciones[-1][0] == "Empresa · Empresa A, S.A. · A00000000"
