# 2026-11-21 · Identidad visual y menos texto en pantalla (D-022)

- **Autor:** Claude (agente)
- **Fase del plan:** 2. Interfaz.
- **Rama:** `feat/diseno`

## Qué se hizo
- **Logo vectorial** a partir de un boceto del equipo: un ojo abierto de trazo uniforme con la pupila azul. Hay tres variantes en `src/ojo_ciudadano/app/static/`: símbolo, horizontal con el nombre y versión para fondo claro.
- **Tema oscuro** en `.streamlit/config.toml`:
  - fondo `#0B1120` y superficie `#131C2E`;
  - acento azul `#3D8BFD`;
  - tipografía Inter;
  - barra de herramientas mínima.
- Ajustes finos en `app/static/estilo.css`: tarjetas, títulos y anchura del contenido.
- **Navegación** agrupada en «Señales», «Explorar» y «Preguntar», con iconos Material. El logo aparece en la barra lateral y en la pestaña del navegador.
- **Menos texto:**
  - el aviso, la metodología, las fechas de descarga y el aviso legal pasan de la cabecera a la barra lateral;
  - cada pantalla tiene una sola línea bajo el título y las explicaciones largas van en desplegables («Cómo se calcula», «Cómo leer el mapa»);
  - se quitan los avisos repetidos en «Preguntas guiadas» y «Asistente».
- **Mapa del dinero:** el diagrama usa la paleta del proyecto (órganos en azul, empresas en gris azulado, flujos azules translúcidos). El filtro de tipo muestra «Todos» en vez de «None».
- **Sin emojis:** quitados del README, `CLAUDE.md`, `docs/01`, `docs/07` y la pantalla del asistente. Hay una regla nueva en `CLAUDE.md` (regla 7) y en D-022, y el test `tests/test_sin_emojis.py` falla si aparece alguno.
- `docs/marca.md` recoge el logo, la paleta y las reglas de estilo. El README muestra el logo.

## Decisiones tomadas
- D-022.

## Desviaciones del plan
- Ninguna en alcance: es trabajo de interfaz dentro del MVP.

## Problemas y hallazgos
- Los textos legales no se han quitado, solo se han movido a la barra lateral y a los desplegables. El contenido revisado con `revisor-legal` no cambia.

## Siguiente paso
- Revisar con el equipo el aspecto de cada pantalla y seguir quitando texto de las fichas.
