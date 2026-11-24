"""Animaciones del asistente (D-037): HTML sin scripts y texto que se escribe."""

from ojo_ciudadano.app import animacion
from ojo_ciudadano.asistente import agente
from ojo_ciudadano.asistente.plano import Plano


def test_consulta_dibuja_tablas_uniones_y_pasos():
    p = Plano(
        tablas=["contrato_unico", "organo"],
        uniones=[("contrato_unico", "organo", "organo_id")],
        pasos=["Leer contrato_unico, organo", "Unir <x>"],
    )
    html = animacion.consulta(p)
    assert "contrato_unico" in html and "organo_id" in html and "organismos" in html
    assert "Unir &lt;x&gt;" in html  # se escapa
    assert "<script" not in html
    assert "prefers-reduced-motion" in html
    assert 'role="status"' in html


def test_cada_herramienta_tiene_su_animacion(base):
    llamadas = [
        agente.LlamadaSQL("SELECT count(*) FROM contrato_unico"),
        agente.LlamadaBuscarDocumento("placsp:1", "solvencia"),
        agente.LlamadaBuscarResoluciones("juicio de valor"),
        agente.LlamadaBuscarTexto("ambulancias", "contrato"),
        agente.LlamadaBuscarConjunto("lista de espera"),
        agente.LlamadaConsultarConjunto("conjunto", "SELECT 1"),
    ]
    for llamada in llamadas:
        assert 'class="oc-anim"' in animacion.de_llamada(base.con, llamada)


def test_escribir_devuelve_el_texto_entero(monkeypatch):
    monkeypatch.setattr(animacion.time, "sleep", lambda s: None)
    texto = "Hay **3** contratos.\n\nFuente: portal."
    assert "".join(animacion.escribir(texto)) == texto
