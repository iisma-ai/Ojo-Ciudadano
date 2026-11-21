# 2026-11-21 · Portada y contratos a revisar con un gráfico por señal (D-023)

- **Autor:** Claude (agente)
- **Fase del plan:** 2. Tareas A-01, A-02 y A-03 de `docs/11-accesibilidad.md`.
- **Rama:** `feat/accesibilidad-alertas`

## Qué se hizo
- **Portada** (`paginas/inicio.py`, página por defecto):
  - una frase de qué es;
  - cuatro cifras grandes (contratos, subvenciones, organismos, contratos con alguna señal);
  - tres puertas de entrada;
  - una tarjeta por señal con su frase y una barra con cuántos contratos la tienen de los comprobados.
- **«Contratos a revisar»** (antes «Panel de alertas»):
  - filtro por señal con su nombre y su número;
  - interruptor «Incluir contratos menores», en vez del control de «mínimo de indicadores aplicables»;
  - tarjetas con título, organismo, año e importe (con o sin IVA);
  - insignias con el nombre de cada señal encontrada y «de N señales comprobadas»;
  - el botón «Ver gráficos» muestra un gráfico por señal, el aviso de contrato atípico y el enlace al expediente. Los gráficos solo se calculan al pedirlos.
- **Gráficos por señal (estudios E-01 a E-06):**
  - `app/datos.py`: consultas `detalle_r01`, `detalle_r02`, `detalle_r03`, `detalle_r04` y `detalle_importes`;
  - `app/graficos.py`: los gráficos;
  - `app/senales.py`: frase con cifras más gráfico;
  - las alternativas valoradas y la elección de cada estudio están en `docs/11`.
- **Lenguaje claro** en `textos.py`: nombre corto y frase de cada señal, y formato español de importes, números y porcentajes.
- **Revisión legal** con `revisor-legal`, todo aplicado:
  - R-03 ya no da a entender que se incumplió la ley;
  - R-04 dice «recibe» y «concentra», no «se lleva» ni «domina»;
  - R-02, R-05 y R-06 son más precisos;
  - la nota de las señales recupera «cálculo nuestro» y «sin señales no queda avalado»;
  - la presentación tiene un tono neutro.
- Tests en `tests/app/test_visual.py`. Probadas las seis señales con 200 contratos reales cada una: todas tienen gráfico.

## Decisiones tomadas
- Ninguna nueva (aplicación de D-023).

## Problemas y hallazgos
- Algunos contratos con R-02 no tienen adjudicación registrada. La consulta los cuenta con importe 0 para que tengan gráfico.
- En suministros, la mediana de ofertas también es 1. Por eso E-01 muestra la distribución y el porcentaje con dos o más ofertas, no la mediana.

## Siguiente paso
- A-05 (ficha de empresa), A-06 (ficha de organismo) y A-07 (mapa del dinero), con su estudio previo. Después, A-10 y A-11.
