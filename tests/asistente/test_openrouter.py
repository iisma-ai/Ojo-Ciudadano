import pytest

from ojo_ciudadano.asistente import openrouter


def test_lee_la_clave_de_env_si_no_esta_en_el_entorno(tmp_path, monkeypatch):
    monkeypatch.delenv(openrouter.VARIABLE, raising=False)
    env = tmp_path / ".env"
    env.write_text('OTRA=1\nOPENROUTER_API_KEY="sk-or-prueba"\n', encoding="utf-8")
    assert openrouter.clave(env) == "sk-or-prueba"


def test_el_entorno_manda_sobre_env(tmp_path, monkeypatch):
    monkeypatch.setenv(openrouter.VARIABLE, "sk-or-entorno")
    env = tmp_path / ".env"
    env.write_text("OPENROUTER_API_KEY=sk-or-fichero\n", encoding="utf-8")
    assert openrouter.clave(env) == "sk-or-entorno"


def test_sin_clave_avisa_sin_mostrar_nada(tmp_path, monkeypatch):
    monkeypatch.delenv(openrouter.VARIABLE, raising=False)
    with pytest.raises(RuntimeError, match="Falta OPENROUTER_API_KEY"):
        openrouter.clave(tmp_path / "no_existe.env")
