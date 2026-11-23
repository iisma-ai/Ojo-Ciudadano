"""Conexión con OpenRouter (D-010, en prueba): clave desde el entorno o desde `.env`.

La clave nunca se imprime ni se guarda fuera de `.env`.

Comprobación rápida (gasta una fracción de céntimo):
    uv run python -m ojo_ciudadano.asistente.openrouter
"""

import os
from pathlib import Path

import httpx

URL_BASE = "https://openrouter.ai/api/v1"
RUTA_ENV = Path(__file__).resolve().parents[3] / ".env"
VARIABLE = "OPENROUTER_API_KEY"
MODELO_PRUEBA = "openai/gpt-4o-mini"


def clave(ruta_env: Path = RUTA_ENV) -> str:
    """Devuelve la clave de la variable de entorno o, si no está, de `.env`."""
    valor = os.environ.get(VARIABLE)
    if not valor and ruta_env.exists():
        for linea in ruta_env.read_text(encoding="utf-8-sig").splitlines():
            nombre, _, resto = linea.partition("=")
            if nombre.strip() == VARIABLE:
                valor = resto.strip().strip('"').strip("'")
    if not valor:
        raise RuntimeError(f"Falta {VARIABLE} en el entorno o en .env")
    return valor


def _cabeceras() -> dict[str, str]:
    return {"Authorization": f"Bearer {clave()}"}


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
    r = httpx.post(
        f"{URL_BASE}/chat/completions",
        headers=_cabeceras(),
        json={"model": modelo, "messages": mensajes, **opciones},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


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
