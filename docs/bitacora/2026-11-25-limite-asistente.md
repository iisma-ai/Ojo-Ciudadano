# 2026-11-25 · Límite de preguntas al modelo (D-057)

- **Quién:** El Harrak con Claude (agente)
- **Rama:** `fix/limite-asistente` (sale de `main` en `d9af34c`)

## Qué se ha hecho

- **`app/limite_modelo.py`:**
  - `Limitador`: 2 preguntas seguidas y 5 minutos de espera desde la última; seguro con varias sesiones a la vez y compartido por todo el servidor (`st.cache_resource`).
  - Identidad: resumen de la IP de Cloudflare y del navegador.
  - El aviso para el visitante.
- **`paginas/asistente.py`:** se comprueba justo antes de llamar al modelo. Las preguntas preparadas no pasan por el límite.
- **Tests:** `tests/app/test_limite_modelo.py` (4, con reloj simulado). Total: 492 en verde.
- **El contenedor en marcha** ya usa esta rama: imagen reconstruida y sana.
- **Saldo de OpenRouter**, consultado sin gastar:
  - en la cuenta quedan **0,35 USD**;
  - la clave tiene un límite de 6 USD semanales, con 1,06 USD gastados y 4,94 USD disponibles;
  - a unos 0,008 USD por pregunta, dan para unas 40 preguntas.
- **Incidencia:** el DNS del router de casa (`liveboxfibra`) guardó «no existe» para `oc-origen.sourcia.solutions` de antes de crear la ruta. Desde fuera (8.8.8.8 y 1.1.1.1) se resuelve y responde en 0,10 s. Se corrige solo al caducar esa respuesta o reiniciando el router.

## Siguiente paso

- Fusionar en `main`: la carpeta de despliegue sigue a `main`.
- Recargar saldo en OpenRouter.
