# 2026-11-19 · Mapa del dinero y revisión legal de la interfaz

- **Autor:** Claude (agente), a petición de Ignacio
- **Fase del plan:** 2 · Construcción en paralelo (módulos de interfaz)

## Qué se hizo
- Rama `feat/app-mapa-dinero`, sobre `feat/app-organo`.
- `paginas/mapa.py` y consultas `flujos`, `contratos_flujo` y `tipos_contrato` en `app/datos.py`. Diagrama Sankey órgano → empresa con los mayores flujos; una sola fuente cada vez (sin IVA en PLACSP, con IVA en el portal) para no sumar bases distintas; filtros de año, tipo y contratos menores; sin personas físicas. Cada flujo se abre en la lista de sus contratos con enlace a la ficha oficial. Aviso de que no hay enlace partida → contrato.
- **Dependencia nueva: `plotly`** (`uv add plotly`, 7.1.0), para el diagrama Sankey, que Streamlit no trae. Streamlit ya era D-005; no cambia la tecnología.
- Revisión con el agente `revisor-legal` de todos los textos. Aplicado: aviso corto siempre visible y expander «Metodología y fuentes»; texto del percentil corregido (estaba invertido); «Nivel medio de señales» con ayuda; encabezados «n de m señales» en vez de un porcentaje suelto; valor de los indicadores con unidad y umbral; avisos en los gráficos y en el listado de empresas por órgano; enlaces a las fuentes en las fichas; «Sin resultados» genérico en la búsqueda de empresas; tratamiento de contratos sin enlace; R-04 dice «Un adjudicatario».
- 91 tests y `ruff` en verde; las cuatro pantallas comprobadas con `AppTest` sobre la base real.

## Decisiones tomadas
- Ninguna.

## Desviaciones del plan
- Ninguna.

## Problemas y hallazgos
- Pendiente de la revisión legal: matizar los motivos de R-02 (emergencia), R-03 («posible») y R-05 (superar el 20 % no implica incumplimiento) en sus SQL y tests; excluir también NIF con formato DNI/NIE en la búsqueda y los listados, no solo `tipo_persona = 'fisica'`; fecha de descarga por fuente en vez de la global; licencia exacta de las fuentes (P-03 sigue abierta, falta la BDNS) y enlace a la metodología pública; ayuda de R-06.
- Las URL de las fuentes del pie son las de `docs/02-fuentes-datos.md`; hay que confirmar la redacción final con el equipo.

## Siguiente paso
- Abrir el PR a `main` de la cadena de ramas.
- Pendientes de la revisión legal (arriba).
- Asistente (D-010 sigue sin decidir) y subvenciones (BDNS).
