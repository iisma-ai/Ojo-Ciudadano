# 2026-11-23 · Datos nuevos en la interfaz

- **Autor:** Claude (agente), a petición de una persona del equipo
- **Fase del plan:** 2, un día antes del H3
- **Rama:** `feat/interfaz-datos-nuevos`

## Qué se hizo

Los datos añadidos hoy (D-027 a D-029) solo los veía el asistente. Ahora se ven en la plataforma (detalle en [`../03-modulos.md`](../03-modulos.md)):

1. `app/datos_flujos.py`: consultas de encargos, fondos europeos y recursos, que funcionan también en una base sin esas tablas. Los medios propios que son personas físicas solo aparecen sumados (D-007).
2. **Ficha de órgano:** desplegable de encargos a medios propios. Ejemplo: la Agencia de Seguridad y Emergencias Madrid 112 tiene 44 encargos por 185,9 M€ con IVA (Tragsa 135,5 M€, Canal de Isabel II 40,0 M€).
3. **Ficha de empresa:** encargos recibidos como medio propio. Ejemplo: Tragsa, 137 encargos por 245,3 M€ de 11 organismos.
4. **Fallo que ya existía, corregido:** la ficha y el buscador de empresas exigían tener contratos puntuados, así que quien solo recibía subvenciones (por ejemplo, el Ayuntamiento de Madrid, 257,9 M€) no se podía consultar, aunque la pantalla decía que sí. `datos._entidades_con_datos` une contratos, subvenciones y encargos: de 22.115 a 44.926 entidades con ficha. El buscador tarda unos 0,2 s por consulta (antes 0,12 s). Sin contratos, la ficha lo dice y oculta esas secciones.
5. **Tarjeta de contrato:** fondos de la UE con el nombre del programa y, si está enlazado, el recurso ante el Tribunal con su resultado y enlace.
6. **Presupuesto y contexto:** pestañas «Encargos a medios propios» y «Recursos ante el Tribunal».
7. `.claude/launch.json` con la configuración `interfaz` para arrancar Streamlit desde el navegador integrado.

## Comprobaciones

- Tests nuevos en `tests/app/test_datos_flujos.py`; `uv run pytest` con 272 tests en verde, `ruff` limpio.
- Fichas de órgano y de empresa y tarjeta de contrato ejecutadas con `streamlit.testing.AppTest` sobre la base real, sin excepciones. Las pestañas nuevas, vistas en el navegador integrado: en pantallas estrechas se ajustaron las cifras (en millones) y el orden de las columnas.
- El buscador con autocompletado no se pudo probar a mano en el navegador integrado (es un componente en un iframe); su consulta tiene test.

## Decisiones y desviaciones

- Ninguna decisión nueva: aplica D-027 a D-029 y D-023 (accesibilidad). La corrección de la ficha de empresa hace que se cumpla lo que la pantalla ya prometía.

## Siguiente paso

Revisión legal hecha con `revisor-legal` (aplicados la fuente y la fecha en la línea del recurso y la redacción del art. 32). Falta el PR a `main` y probar la demo del H3 con estas pantallas.
