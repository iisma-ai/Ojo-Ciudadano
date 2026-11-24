# 2026-11-24 · Web fluida con el Inicio y el mapa de billetes (D-041)

**Quién:** El Harrak, con Claude (agente). **Rama:** `feat/billetes-fluido`, que sale de `origin/feat/mapa-billetes`, de Ignacio.

## Qué se pidió
Coger lo que ha hecho Ignacio (Inicio y mapa de frascos de billetes) y hacerlo más fluido, como en la web fluida.

## Qué se hizo
- **Fusión de `feat/web-fluida`** en la rama de Ignacio.
  - Hubo conflictos solo en `docs/decisions.md` y `docs/08-plan.md`, porque las dos ramas usaban D-038. Se conservan las dos partes: la web fluida pasa a **D-040**, también en `docs/05-asistente.md` y en su bitácora.
  - El código se juntó sin conflictos.
- **Medición:**
  - **Servidor (AppTest con perfil):** al volver a cargar, el Inicio tarda 0,03 s y el mapa, 0,07 s. Las consultas de Ignacio ya tenían `st.cache_data`. Cada año nuevo del mapa tarda unos 0,3 s la primera vez.
  - **Navegador:** scroll a 240 fotogramas por segundo, sin tareas largas. El grafo se queda quieto unos 0,3 s después de cambiar de año.
- **Mascota (`billetes.CSS_OJO`):**
  - antes, 7 animaciones infinitas dentro del SVG, que se repintaban en cada fotograma;
  - ahora se mueve unas vueltas y se para, y vuelve a moverse al pasar el ratón;
  - lleva `contain: layout paint`.
  - Comprobado en el navegador:
    - al llegar hay 7 animaciones en marcha;
    - a los 25 s no queda ninguna;
    - con el ratón encima vuelven las 7;
    - al quitarlo, ninguna.

## Comprobaciones
462 tests, todos bien (uno nuevo). `ruff` sin avisos.

## Siguiente paso
- Que Ignacio vea la rama: https://github.com/iisma-ai/Ojo-Ciudadano/compare/main...feat/billetes-fluido
- Si se fusiona, sustituye a fusionar `feat/mapa-billetes` y `feat/web-fluida` por separado.
