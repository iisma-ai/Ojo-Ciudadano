# 2026-11-24 · Web ligera, versión alternativa (D-043)

**Quién:** El Harrak, con Claude (agente). **Rama:** `feat/web-ligera`. Sale de `origin/feat/mapa-billetes` (la rama que se estaba tocando entonces, de Ignacio, con D-038 a D-042) e incluye `origin/main`.

## Qué se pidió
Una web más fácil y agradable:
- **Inicio** solo con el logo, y la mascota con billetes en «A dónde va el dinero»;
- **desplegables** con un fondo que tape lo de detrás;
- **sin el menú lateral**, con botones a las partes y uno para abrir el menú entero;
- **avisos legales y datos** abajo del todo;
- **entrada animada de 1,5 s**, con el ojo en un mar muy oscuro que se aclara, inspirada en la presentación;
- todo **fluido** y en una rama alternativa.

## Qué se hizo
- **`main.py`:**
  - navegación oculta;
  - `barra_superior()`, con el logo, Inicio, A dónde va el dinero, Contratos a revisar, Asistente y «Menú», que abre todas las pantallas por secciones;
  - `pie()` con el aviso, la metodología, las fuentes y las fechas. Se dibuja antes que la pantalla y el CSS (`order`) lo manda al final, porque varias pantallas se paran con `st.stop()` esperando una elección.
  - `intro()` solo la primera vez en la sesión.
- **`static/intro.html`:** la entrada, primero de 1,5 s (ver la segunda ronda).
  - mar oscuro, nieve marina y el ojo de cristal, al que se le enciende la pupila;
  - después, la luz que se abre y la capa que se desvanece;
  - solo `opacity` y `transform`, sin bloquear clics y sin salir con «reducir movimiento».
  - **Primer intento:** animar también la página hacía que la capa fija dejara de cubrir la pantalla, porque un `transform` en el contenedor cambia la referencia de `position: fixed`. Se quitó.
- **`estilo.css`:**
  - fuera la barra lateral y la cabecera;
  - barra de arriba fija y opaca. El `sticky` va en la envoltura del contenedor, porque en el contenedor no tenía recorrido;
  - pie sin recuadro;
  - desplegables, ventanas emergentes, listas y ayudas con fondo opaco.
- **Pantallas:**
  - **Inicio:** solo el logo y sin el botón «Fuentes».
  - **Mapa del dinero:** las fuentes van al desplegable final.
  - **Atípicos:** «Cómo se calcula» va al pie.
  - **Asistente:** sin las fuentes repetidas al final.
- **Docs:** D-043, plan y esta bitácora.

## Comprobaciones
- **Las nueve pantallas** (AppTest con la navegación): sin errores y todas con pie. Volver a cargar cada una tarda de 0,02 a 0,9 s.
- **Navegador:**
  - la entrada se ve: mar oscuro, el ojo, el nombre y la luz que desvela la página;
  - el menú y «Más filtros» se leen sobre fondo opaco;
  - la barra se queda fija al bajar;
  - scroll a 240 fotogramas por segundo, sin tareas largas.
- **Tests:** 471, todos bien (3 nuevos en `tests/app/test_intro.py`). `ruff` sin avisos.

## Segunda ronda: el ojo de la presentación y 3 s
El Harrak pidió tres cambios en la entrada:
- el ojo de la presentación en vez del logo;
- que ilumine más sin ser agresiva;
- 3 s en vez de 1,5 s.

Cambios:
- **`app/ojo_cristal.py`** dibuja el ojo de `presentacion/ojo3d.js` en dos capas SVG.
  - **Iris:** halo azul, 240 fibras de luz, anillos, escala de lente y pupila oscura. Lleva una semilla fija para que salga siempre igual y gira 50° durante la entrada.
  - **Cristal:** borde luminoso, brillo arriba a la izquierda, reflejo abajo y destello en la pupila.
- **Luz:** ahora es un halo alrededor del ojo, más una luz redonda de caída suave en `vmax`. La primera versión dejaba un óvalo con el borde marcado en pantallas anchas.
- **Duración:** pasa a 3 s, con los tiempos repartidos.
- **Comprobado en el navegador:** el ojo aparece, se ilumina y la página se ve a través mientras la capa se desvanece.
- **Tests:** uno nuevo para el ojo.

## Siguiente paso
- Que el equipo compare con `feat/mapa-billetes`: https://github.com/iisma-ai/Ojo-Ciudadano/compare/main...feat/web-ligera
- Pasar `revisor-legal` por el aviso en el pie, que antes estaba siempre a la vista.
- El desplegable del buscador de empresas va dentro de su propio marco, así que el CSS de la web no le llega.
