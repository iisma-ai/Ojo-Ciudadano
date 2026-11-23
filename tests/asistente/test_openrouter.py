import json

import pytest

from ojo_ciudadano.asistente import openrouter
from ojo_ciudadano.asistente.agente import LlamadaSQL, TextoFinal


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


def test_traduce_la_conversacion_al_formato_openai():
    mensajes = [
        {"rol": "usuario", "contenido": "¿Cuántos contratos hay?"},
        {"rol": "llamada", "sql": "SELECT count(*) FROM contrato_unico"},
        {"rol": "resultado", "contenido": "Datos: 5"},
        {"rol": "modelo", "contenido": "Hay 5."},
    ]
    salida = openrouter.mensajes_openai("Reglas", mensajes)
    assert [m["role"] for m in salida] == ["system", "user", "assistant", "tool", "assistant"]
    llamada = salida[2]["tool_calls"][0]
    assert llamada["function"]["name"] == "consultar_sql"
    assert json.loads(llamada["function"]["arguments"]) == {
        "sql": "SELECT count(*) FROM contrato_unico"
    }
    assert salida[3]["tool_call_id"] == llamada["id"]


def test_marca_las_instrucciones_para_la_cache():
    salida = openrouter.mensajes_openai("Reglas", [], cache=True)
    assert salida[0]["content"][0]["cache_control"] == {"type": "ephemeral"}


def _respuesta(mensaje):
    return {"choices": [{"message": mensaje}]}


def test_interpreta_llamada_sql_y_texto_final():
    llamada = _respuesta(
        {
            "content": None,
            "tool_calls": [
                {"function": {"name": "consultar_sql", "arguments": '{"sql": "SELECT 1"}'}}
            ],
        }
    )
    assert openrouter.interpretar(llamada) == LlamadaSQL("SELECT 1")
    assert openrouter.interpretar(_respuesta({"content": " Hola "})) == TextoFinal("Hola")


def test_argumentos_rotos_llegan_vacios_al_validador():
    rota = _respuesta(
        {"tool_calls": [{"function": {"name": "consultar_sql", "arguments": "{sql: SELECT"}}]}
    )
    assert openrouter.interpretar(rota) == LlamadaSQL("")
