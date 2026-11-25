"""Límite de consultas al modelo (D-057): 5 seguidas y 5 minutos de espera, solo desde España."""

from ojo_ciudadano.app.limite_modelo import Limitador, mensaje, pais_permitido, tiempo


class Reloj:
    def __init__(self) -> None:
        self.ahora = 1000.0

    def __call__(self) -> float:
        return self.ahora


def test_cinco_seguidas_por_defecto():
    limite = Limitador(reloj=Reloj())
    assert all(limite.intentar("ana") == 0 for _ in range(5))
    assert limite.intentar("ana") == 300


def test_solo_desde_espana():
    assert pais_permitido("ES") and pais_permitido("es")
    assert pais_permitido(None) and pais_permitido("")  # en local, sin Cloudflare
    assert pais_permitido("XX")  # Cloudflare no sabe de dónde es: no se bloquea por error
    assert not pais_permitido("FR")
    assert not pais_permitido("T1")  # red Tor


def test_dos_seguidas_y_luego_espera_de_cinco_minutos():
    reloj = Reloj()
    limite = Limitador(maximo=2, reloj=reloj)
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
    limite = Limitador(maximo=2, reloj=reloj)
    limite.intentar("ana")
    limite.intentar("ana")
    reloj.ahora += 300
    assert limite.intentar("ana") == 0
    assert limite.intentar("ana") == 0
    assert limite.intentar("ana") > 0


def test_cada_persona_cuenta_aparte():
    limite = Limitador(maximo=2, reloj=Reloj())
    limite.intentar("ana")
    limite.intentar("ana")
    assert limite.intentar("ana") > 0
    assert limite.intentar("luis") == 0


def test_mensaje_con_el_tiempo_que_queda():
    assert tiempo(250) == "4 min 10 s"
    assert tiempo(35) == "35 s"
    assert "4 min 10 s" in mensaje(250)
    assert "demasiadas consultas" in mensaje(250)
    assert "respuesta preparada" in mensaje(250)
