"""Animaciones del asistente (D-037): HTML sin scripts y texto que se escribe."""

from ojo_ciudadano.app import animacion
from ojo_ciudadano.asistente import agente
from ojo_ciudadano.asistente.plano import Plano

PLANO = Plano(
    tablas=["contrato_unico", "organo"],
    uniones=[("contrato_unico", "organo", "organo_id")],
    pasos=["Leer contrato_unico, organo", "Unir <x>"],
)


def test_proceso_con_tablas_uniones_pasos_y_resultado():
    html = animacion.consulta(PLANO, filas=12)
    assert "contrato_unico" in html and "organo_id" in html and "organismos" in html
    assert "Unir &lt;x&gt;" in html  # se escapa
    assert "12 filas" in html and "resultado" in html
    assert "<script" not in html
    assert 'role="status"' in html
    assert "oc-anima" in html  # se anima la primera vez


def test_en_el_historial_el_proceso_esta_quieto():
    html = animacion.consulta(PLANO, filas=1, animar=False)
    assert "oc-anima" not in html and "1 fila" in html


def test_css_una_vez_con_movimiento_reducido():
    assert "prefers-reduced-motion" in animacion.CSS
    assert "infinite" not in animacion.CSS.split(".oc-anima")[1].split(".oc-doc")[0]
    assert animacion.duracion(PLANO) < 3


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
        assert '<div class="oc-anim ' in animacion.de_llamada(base.con, llamada)


def test_escribir_devuelve_el_texto_entero_en_pocos_trozos(monkeypatch):
    monkeypatch.setattr(animacion.time, "sleep", lambda s: None)
    texto = " ".join(f"palabra{i}" for i in range(300)) + "\n\nFuente: portal."
    trozos = list(animacion.escribir(texto))
    assert "".join(trozos) == texto
    assert len(trozos) <= 40
