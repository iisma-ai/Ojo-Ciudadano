# 2026-11-25 · «¿De dónde viene el dinero?» en el Mapa del dinero (D-054)

- **Quién:** El Harrak con Claude (agente)
- **Rama:** `feat/de-donde-viene` (sale de `main` en `3127340`)

## Qué se ha hecho

- **Datos:** se comprobó que la base ya tiene lo necesario en `serie_cm` y que cuadra:
  - ingresos consolidados por capítulo, iniciales hasta 2026 y liquidados hasta 2025 (derechos reconocidos, previsión actual, recaudación);
  - sistema de financiación autonómica y ayudas de la UE, hasta 2023.
  - En 2025 los capítulos suman lo mismo que el total: 32.439 M€.
- **Consultas** en `app/datos_contexto.py`: `ingresos_del_anio`, `sistema_financiacion` y `ayudas_ue`.
- **Vista nueva** `app/de_donde_viene.py`:
  - barra de «de cada 100 € que entran»;
  - entradas, saldo neto de transferencias corrientes e ingresos netos;
  - mapa de burbujas con ficha de cada tipo de ingreso;
  - explicación del sistema de financiación;
  - impuestos divididos entre habitantes, ayudas de la UE y fuentes.
- **Selector** en `paginas/mapa_general.py`: un `segmented_control` grande a lo ancho, con «¿A dónde va el dinero?» por defecto. Estilo en `estilo.css`: tarjetas de cristal, la elegida en azul y la otra latiendo cuatro veces.
- **`red.py`:** el cuadro al pasar el ratón acepta `extra["linea_llenado"]`, para no decir «Gastado» en los ingresos.
- **Revisión de `revisor-legal`**, aplicada:
  - explicación técnica y neutra del sistema de financiación (Ley 22/2009, población ajustada, signo de cada fondo);
  - título «El saldo de la Comunidad con el sistema de financiación autonómica»;
  - aviso cuando se mezclan años;
  - fuente bajo cada bloque de cifras;
  - préstamos explicados como cifra bruta;
  - «impuestos divididos entre habitantes».
- **Tests:** `tests/app/test_de_donde_viene.py` (7). Total: 483 en verde, `ruff` limpio. Comprobado en el navegador: selector, barra, burbujas, ficha y textos.

## Cifras que salen (2025, año cerrado)

- Entraron 38.557 M€. De cada 100 €: 49 de impuestos directos, 39 de indirectos, 9 de préstamos y 3 del resto.
- Saldo neto de transferencias corrientes: −6.118 M€. Ingresos netos: 32.439 M€.
- Sistema de financiación de 2023: Fondo de Garantía −5.748 M€ y Fondo de Suficiencia −967 M€.

## Pendiente

- Que el equipo decida si entra en `main`: el plan dice que el 25 no se añaden funciones.
- El estilo del selector depende de cómo pinta Streamlit 1.67 el `segmented_control`.

## Siguiente paso

Enseñar la rama al equipo. Si se acepta, cambiar D-054 a «Aceptada» y fusionar.
