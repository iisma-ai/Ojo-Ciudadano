"""Conexión con OpenRouter (D-010): clave desde el entorno o desde `.env` y adaptador del agente.

OpenRouter da acceso a modelos de varios proveedores con la API de OpenAI, así que el adaptador
es el mismo para todos y se puede comparar modelos cambiando solo su nombre. La clave nunca se
imprime ni se guarda fuera de `.env`.

Comprobación rápida (gasta una fracción de céntimo):
    uv run python -m ojo_ciudadano.asistente.openrouter
"""

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path

import httpx

from ojo_ciudadano.asistente.agente import HERRAMIENTA_SQL, LlamadaSQL, TextoFinal

URL_BASE = "https://openrouter.ai/api/v1"
RUTA_ENV = Path(__file__).resolve().parents[3] / ".env"
VARIABLE = "OPENROUTER_API_KEY"
MODELO_PRUEBA = "openai/gpt-4o-mini"
# Elegidos con la batería de 20 preguntas (D-010, bitácora del 23-nov).
MODELO_PRINCIPAL = "anthropic/claude-haiku-5.5"
MODELOS_RESPALDO = ["deepseek/deepseek-v4.1-flash"]
MAX_TOKENS_RESPUESTA = 2500
REINTENTOS = 2  # ante límites de ritmo (429) o errores del proveedor (5xx)

HERRAMIENTAS = [
    {
        "type": "function",
        "function": {
            "name": HERRAMIENTA_SQL["nombre"],
            "description": HERRAMIENTA_SQL["descripcion"],
            "parameters": HERRAMIENTA_SQL["parametros"],
        },
    }
]


def _leer_env(variable: str, ruta_env: Path = RUTA_ENV) -> str | None:
    """Valor de la variable de entorno o, si no está, de `.env`."""
    valor = os.environ.get(variable)
    if not valor and ruta_env.exists():
        for linea in ruta_env.read_text(encoding="utf-8-sig").splitlines():
            nombre, _, resto = linea.partition("=")
            if nombre.strip() == variable:
                valor = resto.strip().strip('"').strip("'")
    return valor or None


def clave(ruta_env: Path = RUTA_ENV) -> str:
    """Devuelve la clave de la variable de entorno o, si no está, de `.env`."""
    valor = _leer_env(VARIABLE, ruta_env)
    if not valor:
        raise RuntimeError(f"Falta {VARIABLE} en el entorno o en .env")
    return valor


def hay_clave(ruta_env: Path = RUTA_ENV) -> bool:
    return _leer_env(VARIABLE, ruta_env) is not None


def modelo_elegido(ruta_env: Path = RUTA_ENV) -> str:
    """Modelo principal: `LLM_MODEL` del entorno o de `.env`, o el elegido en D-010."""
    return _leer_env("LLM_MODEL", ruta_env) or MODELO_PRINCIPAL


def _cabeceras() -> dict[str, str]:
    return {"Authorization": f"Bearer {clave()}", "X-Title": "Ojo Ciudadano"}


def estado_clave() -> dict:
    """Uso y límite de la clave. No consume créditos."""
    r = httpx.get(f"{URL_BASE}/key", headers=_cabeceras(), timeout=30)
    r.raise_for_status()
    return r.json().get("data", {})


def saldo() -> float | None:
    """Créditos que quedan en la cuenta, o None si la clave no puede consultarlos."""
    r = httpx.get(f"{URL_BASE}/credits", headers=_cabeceras(), timeout=30)
    if r.status_code != 200:
        return None
    datos = r.json().get("data", {})
    return datos["total_credits"] - datos["total_usage"]


def completar(mensajes: list[dict], modelo: str, **opciones) -> dict:
    """Llamada de chat en formato OpenAI. Devuelve la respuesta JSON completa."""
    for intento in range(REINTENTOS + 1):
        r = httpx.post(
            f"{URL_BASE}/chat/completions",
            headers=_cabeceras(),
            json={"model": modelo, "messages": mensajes, **opciones},
            timeout=180,
        )
        if r.status_code in (429, 500, 502, 503, 504) and intento < REINTENTOS:
            time.sleep(5 * (intento + 1))
            continue
        r.raise_for_status()
        datos = r.json()
        if "error" in datos:  # algunos proveedores devuelven 200 con un error dentro
            raise RuntimeError(f"OpenRouter: {datos['error']}")
        return datos
    raise AssertionError("inalcanzable")


def mensajes_openai(instrucciones: str, mensajes: list[dict], cache: bool = False) -> list[dict]:
    """Traduce la conversación neutra del agente al formato de OpenAI.

    Cada `llamada` va seguida de su `resultado`; se enlazan con un identificador por posición.
    Con `cache`, las instrucciones (iguales en cada vuelta) se marcan para la caché del
    proveedor, que las cobra más baratas a partir de la segunda llamada."""
    sistema: dict = {"role": "system", "content": instrucciones}
    if cache:
        sistema["content"] = [
            {"type": "text", "text": instrucciones, "cache_control": {"type": "ephemeral"}}
        ]
    salida = [sistema]
    llamada_abierta = None
    for numero, mensaje in enumerate(mensajes):
        rol = mensaje["rol"]
        if rol == "usuario":
            salida.append({"role": "user", "content": mensaje["contenido"]})
        elif rol == "modelo":
            salida.append({"role": "assistant", "content": mensaje["contenido"]})
        elif rol == "llamada":
            llamada_abierta = f"consulta_{numero}"
            argumentos = json.dumps({"sql": mensaje["sql"]}, ensure_ascii=False)
            salida.append(
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": llamada_abierta,
                            "type": "function",
                            "function": {
                                "name": HERRAMIENTA_SQL["nombre"],
                                "arguments": argumentos,
                            },
                        }
                    ],
                }
            )
        elif rol == "resultado":
            salida.append(
                {"role": "tool", "tool_call_id": llamada_abierta, "content": mensaje["contenido"]}
            )
    return salida


def interpretar(respuesta: dict) -> LlamadaSQL | TextoFinal:
    """Convierte la respuesta del modelo en una llamada SQL o en el texto final."""
    mensaje = respuesta["choices"][0]["message"]
    for llamada in mensaje.get("tool_calls") or []:
        funcion = llamada.get("function", {})
        if funcion.get("name") != HERRAMIENTA_SQL["nombre"]:
            continue
        try:
            sql = json.loads(funcion.get("arguments") or "{}").get("sql", "")
        except json.JSONDecodeError:
            sql = ""  # el validador lo rechaza y el error vuelve al modelo
        return LlamadaSQL(sql)
    return TextoFinal((mensaje.get("content") or "").strip())


@dataclass
class Gasto:
    """Coste y tokens acumulados por un modelo (lo que informa OpenRouter en cada llamada)."""

    llamadas: int = 0
    coste: float = 0.0
    tokens_entrada: int = 0
    tokens_salida: int = 0
    segundos: float = 0.0
    modelos_usados: dict = field(default_factory=dict)

    def sumar(self, respuesta: dict, segundos: float) -> None:
        uso = respuesta.get("usage") or {}
        self.llamadas += 1
        self.coste += float(uso.get("cost") or 0)
        self.tokens_entrada += int(uso.get("prompt_tokens") or 0)
        self.tokens_salida += int(uso.get("completion_tokens") or 0)
        self.segundos += segundos
        usado = respuesta.get("model", "?")
        self.modelos_usados[usado] = self.modelos_usados.get(usado, 0) + 1


def _usa_cache_explicita(modelo: str) -> bool:
    # OpenAI, DeepSeek y Gemini cachean solos; Anthropic necesita la marca.
    return modelo.startswith("anthropic/")


def modelo_openrouter(modelo: str, respaldo: list[str] | None = None, gasto: Gasto | None = None):
    """Adaptador con la forma `agente.Modelo`. `respaldo`: modelos a los que OpenRouter pasa si
    el principal falla o no está disponible. `gasto` acumula coste y tokens."""

    def llamar(instrucciones: str, mensajes: list[dict]) -> LlamadaSQL | TextoFinal:
        opciones = {
            "tools": HERRAMIENTAS,
            "tool_choice": "auto",
            "parallel_tool_calls": False,
            "temperature": 0,
            "max_tokens": MAX_TOKENS_RESPUESTA,
            "usage": {"include": True},
        }
        if respaldo:
            opciones["models"] = [modelo, *respaldo]
        inicio = time.monotonic()
        respuesta = completar(
            mensajes_openai(instrucciones, mensajes, cache=_usa_cache_explicita(modelo)),
            modelo,
            **opciones,
        )
        if gasto is not None:
            gasto.sumar(respuesta, time.monotonic() - inicio)
        return interpretar(respuesta)

    return llamar


def main() -> None:
    print(f"Clave encontrada ({len(clave())} caracteres).")
    datos = estado_clave()
    print(f"Gastado con esta clave: {datos.get('usage')} USD · límite: {datos.get('limit')}")
    print(f"Restante según el límite: {datos.get('limit_remaining')}")
    print(f"Nivel gratuito: {datos.get('is_free_tier')}")
    print(f"Saldo de la cuenta: {saldo()}")
    try:
        respuesta = completar(
            [{"role": "user", "content": "Responde solo: OK"}], MODELO_PRUEBA, max_tokens=5
        )
        print("Respuesta del modelo:", respuesta["choices"][0]["message"]["content"])
        print("Tokens:", respuesta.get("usage"))
    except httpx.HTTPStatusError as error:
        codigo = error.response.status_code
        aviso = " (sin créditos)" if codigo == 402 else ""
        print(f"La llamada al modelo falló: HTTP {codigo}{aviso}")


if __name__ == "__main__":
    main()
