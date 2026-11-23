"""Compara modelos de OpenRouter con la batería de preguntas del asistente (D-010).

Para cada modelo pasa las preguntas elegidas, evalúa el SQL con `bateria.evaluar` y guarda
las respuestas completas en `data/evaluaciones/` (no se sube) para leerlas a mano. Lleva la
cuenta del gasto y para en cuanto un modelo supera su tope o el conjunto supera el tope total.

    uv run python -m ojo_ciudadano.asistente.comparar_modelos \\
        --modelos openai/gpt-6.1-terra,anthropic/claude-haiku-5.5 \\
        --preguntas B-01,B-07,B-17 --tope-modelo 0.25 --tope-total 1.0
"""

import argparse
import json
import time
from datetime import datetime

import duckdb

from ojo_ciudadano.asistente import agente, bateria, openrouter

RUTA_DB = agente.RAIZ / "data" / "ojo_ciudadano.duckdb"
CARPETA = agente.RAIZ / "data" / "evaluaciones"


def _pregunta_con_parametros(pregunta: bateria.PreguntaPrueba) -> str:
    texto = pregunta.pregunta
    if pregunta.parametros:
        texto += " (" + ", ".join(f"{k}: {v}" for k, v in pregunta.parametros.items()) + ")"
    return texto


def evaluar_modelo(
    con: duckdb.DuckDBPyConnection,
    modelo: str,
    preguntas: list[bateria.PreguntaPrueba],
    tope: float,
) -> dict:
    """Pasa las preguntas a un modelo hasta agotarlas o superar el tope de gasto."""
    gasto = openrouter.Gasto()
    llamar = openrouter.modelo_openrouter(modelo, gasto=gasto)
    filas = []
    for pregunta in preguntas:
        if gasto.coste > tope:
            print(f"  {modelo}: tope de {tope} USD superado, paro.")
            break
        antes = (gasto.coste, gasto.llamadas, gasto.segundos)
        inicio = time.monotonic()
        try:
            respuesta = agente.responder(con, llamar, _pregunta_con_parametros(pregunta))
        except Exception as error:  # un fallo del proveedor no debe parar la comparación
            filas.append({"id": pregunta.id, "error": f"{type(error).__name__}: {error}"})
            print(f"  {pregunta.id}: ERROR {error}")
            continue
        sql = respuesta.consultas[-1]["sql"] if respuesta.consultas else None
        evaluacion = bateria.evaluar(con, pregunta, sql, respuesta.texto)
        fila = {
            **evaluacion,
            "pregunta": pregunta.pregunta,
            "texto": respuesta.texto,
            "sql": [c["sql"] for c in respuesta.consultas],
            "errores_sql": respuesta.errores,
            "completa": respuesta.completa,
            "retencion": respuesta.retencion,
            "coste": gasto.coste - antes[0],
            "llamadas": gasto.llamadas - antes[1],
            "segundos": round(time.monotonic() - inicio, 1),
        }
        filas.append(fila)
        print(
            f"  {pregunta.id}: datos_ok={fila['datos_ok']} retencion={fila['retencion']} "
            f"llamadas={fila['llamadas']} errores={len(fila['errores_sql'])} "
            f"coste={fila['coste']:.4f} {fila['segundos']}s"
        )
    return {
        "modelo": modelo,
        "coste": gasto.coste,
        "llamadas": gasto.llamadas,
        "tokens_entrada": gasto.tokens_entrada,
        "tokens_salida": gasto.tokens_salida,
        "segundos": round(gasto.segundos, 1),
        "modelos_usados": gasto.modelos_usados,
        "respuestas": filas,
    }


def resumen(resultado: dict) -> str:
    respuestas = [r for r in resultado["respuestas"] if "error" not in r]
    datos = [r for r in respuestas if r["datos_ok"] is not None]
    aciertos = sum(1 for r in datos if r["datos_ok"])
    retenidas = sum(1 for r in respuestas if r["retencion"])
    incompletas = sum(1 for r in respuestas if not r["completa"])
    fallos = len(resultado["respuestas"]) - len(respuestas)
    return (
        f"{resultado['modelo']}: datos {aciertos}/{len(datos)} · retenidas {retenidas} · "
        f"incompletas {incompletas} · errores de API {fallos} · {resultado['coste']:.4f} USD · "
        f"{resultado['segundos']} s"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--modelos", required=True, help="nombres de OpenRouter, separados por comas"
    )
    parser.add_argument("--preguntas", default="", help="B-01,B-02… (vacío = las 20)")
    parser.add_argument("--tope-modelo", type=float, default=0.25, help="USD por modelo")
    parser.add_argument("--tope-total", type=float, default=1.0, help="USD en total")
    args = parser.parse_args()

    ids = [i.strip() for i in args.preguntas.split(",") if i.strip()]
    preguntas = [p for p in bateria.BATERIA if not ids or p.id in ids]
    con = duckdb.connect(str(RUTA_DB), read_only=True)
    CARPETA.mkdir(parents=True, exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d-%H%M")

    total = 0.0
    resumenes = []
    for modelo in [m.strip() for m in args.modelos.split(",") if m.strip()]:
        if total >= args.tope_total:
            print(f"Tope total de {args.tope_total} USD alcanzado: no pruebo {modelo}.")
            break
        print(f"== {modelo}")
        tope = min(args.tope_modelo, args.tope_total - total)
        resultado = evaluar_modelo(con, modelo, preguntas, tope)
        total += resultado["coste"]
        fichero = CARPETA / f"{marca}-{modelo.replace('/', '_')}.json"
        fichero.write_text(
            json.dumps(resultado, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
        )
        resumenes.append(resumen(resultado))
        print(resumenes[-1])
    print("\n".join(["", "Resumen:", *resumenes, f"Gasto total: {total:.4f} USD"]))


if __name__ == "__main__":
    main()
