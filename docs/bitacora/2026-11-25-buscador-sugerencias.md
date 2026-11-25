# 2026-11-25 · El buscador de la portada sugiere opciones sin escribir nada

- **Quién:** El Harrak con Claude (agente)
- **Rama:** `fix/buscador-sugerencias` (sale de `main` en `3127340`)

## Qué se ha hecho

- **Problema:** al abrir la web y pulsar el buscador de la portada sin escribir, no salía nada. Los buscadores de empresa y de organismo ya traían opciones iniciales (`default_options`); el de la portada (`buscador.todo`), no.
- **Arreglo:** `buscador.todo` pasa ahora unas opciones iniciales.
  - Sin texto, la consulta devolvía solo hospitales, que son los que más contratan. Por eso la muestra se arma variada: las 4 consejerías y los 4 hospitales con más contratos, y las 6 empresas con más contratos.
  - Al escribir, todo sigue igual.
- **Test:** `tests/app/test_buscador.py`. Total: 477 tests en verde, `ruff` limpio.
- **Comprobado en el navegador:** al pulsar el buscador vacío se despliega la lista.

## Siguiente paso

Fusionar en `main`. Es un arreglo, no una función nueva.
