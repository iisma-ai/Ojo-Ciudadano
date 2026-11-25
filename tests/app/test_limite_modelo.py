"""Límite de consultas al modelo (D-057): 2 seguidas y 5 minutos de espera por persona."""

from ojo_ciudadano.app.limite_modelo import Limitador, mensaje, tiempo


class Reloj:
    def __init__(self) -> None:
        self.ahora = 1000.0

    def __call__(self) -> float:
        return self.ahora


def test_dos_seguidas_y_luego_espera_de_cinco_minutos():
    reloj = Reloj()
    limite = Limitador(reloj=reloj)
    assert limite.intentar("ana") == 0
    reloj.ahora += 30
    assert limite.intentar("ana") == 0
    reloj.ahora += 10
    # tercera: espera desde la segunda consulta (300 - 10 s)
    assert limite.intentar("ana") == 290
    reloj.ahora += 200
    assert limite.restante("ana") == 90
    assert limite.intentar("ana") == 90  # insistir no alarga ni acorta la espera


def test_pasada_la_espera_vuelve_a_tener_dos():
    reloj = Reloj()
    limite = Limitador(reloj=reloj)
    limite.intentar("ana")
    limite.intentar("ana")
    reloj.ahora += 300
    assert limite.intentar("ana") == 0
    assert limite.intentar("ana") == 0
    assert limite.intentar("ana") > 0


def test_cada_persona_cuenta_aparte():
    limite = Limitador(reloj=Reloj())
    limite.intentar("ana")
    limite.intentar("ana")
    assert limite.intentar("ana") > 0
    assert limite.intentar("luis") == 0


def test_mensaje_con_el_tiempo_que_queda():
    assert tiempo(250) == "4 min 10 s"
    assert tiempo(35) == "35 s"
    assert "4 min 10 s" in mensaje(250)
    assert "respuesta preparada" in mensaje(250)
