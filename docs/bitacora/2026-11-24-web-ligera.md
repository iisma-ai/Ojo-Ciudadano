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

## Tercera ronda: «Explorar» y el ojo en 3D
- **«Menú» pasa a «Explorar»** y solo lleva lo que no está en la barra: Mapa del dinero, Presupuesto y contexto, Ficha de empresa y Ficha de órgano. También Contratos atípicos, que no tiene botón arriba.
- **El ojo de la entrada es el 3D de la presentación.** `app/intro3d.py` es un componente de Streamlit:
  - carga Three.js 0.169.0, la misma versión que la presentación;
  - importa `presentacion/ojo3d.js` tal cual, cambiando solo la importación de `three`;
  - mueve el ojo en 3 s: aparece hasta 0,9 s, se acerca de 0,9 a 1,5 s y se va a la izquierda y al fondo de 1,5 a 2,7 s, pasando la mirada del espectador a los datos;
  - al terminar libera WebGL y quita el lienzo.
- **La capa CSS espera quieta** hasta que el ojo está listo (`en-marcha`). Añade un haz de luz que sale del ojo y se abre sobre los datos.
- **Reservas:**
  - si el 3D no llega en 1,2 s, sale el ojo plano con el mismo recorrido (`sin3d`);
  - si nada arranca, la capa se quita sola a los 2,5 s.
- **Comprobado en el navegador:**
  - el ojo 3D aparece, se acerca, se va a la izquierda y la página se ve debajo;
  - al final no queda lienzo y la capa está oculta;
  - la reserva plana, simulada, se ve y se oculta;
  - «Explorar» se abre con las cinco pantallas.
- **Tests:** dos nuevos.

## Cuarta ronda: el ojo sube y es la fuente de luz
El Harrak pidió que el ojo subiera en vez de ir a la izquierda, para que también se vea en el móvil y para que la luz venga de arriba, como los rayos. También pidió una luz desde el núcleo al apartarse y un ojo menos oscuro, como en la presentación.

Cambios en `app/intro3d.py`:
- **Iluminación como en la presentación:**
  - importa también `presentacion/agua.js` para el entorno de reflejos (`entorno`) y el color del agua cerca de la superficie (`colorProfundidad(0,15)`);
  - usa `NeutralToneMapping`, cielo `0xa8ecff` y sol `0xe6f9ff`.
  - Antes el ojo usaba ACES, sin entorno y con agua oscura, y la bola se veía casi negra.
  - No se usa el `UnrealBloomPass` de la presentación: sobre un lienzo transparente oscurece el fondo. Lo sustituyen tres luces redondas sumadas (núcleo, aura y destello) que van con el ojo.
- **Recorrido:** se acerca hasta 1,5 s; de 1,5 a 2,7 s sube (y 2,3) y se aleja (z -3,5), con la mirada de la cámara a la página.
- **Luz:** el núcleo se enciende desde 1,35 s. El haz de CSS baja ahora desde arriba (50 % 12 %) y el ojo plano de reserva también sube.
- **Primera prueba en el navegador:** el destello deslumbraba. Se bajó a 0,42 de opacidad y 8 veces su tamaño.
- **Comprobado en el navegador:** el ojo se ve claro, sube, y su luz baja sobre la página mientras se desvela.

## Quinta ronda: el ojo sale por arriba y despliega rayos
El Harrak pidió que el ojo subiera mucho más, hasta salir de la página, y que desplegara más luz, con rayos que aclaren la página poco a poco.
- **Recorrido:** sube de 1,4 a 3,0 s, acelerando (curva cuadrática), hasta y 3,9 y z -2. Sale por arriba hacia 2,85 s.
- **Sin desvanecerse:** el lienzo ya no baja la opacidad y la capa tampoco se desvanece entera; solo el mar se aclara, desde el 45 %.
- **Rayos:** una textura de 46 cuñas de luz con caída radial, en dos coronas detrás del cristal que giran en sentidos contrarios. Crecen hasta 22 veces el ojo con el encendido (1,3-2,3 s) y se apagan del todo de 2,55 a 3,0 s, para que no se corten de golpe al quitar el lienzo.
- El haz de CSS sale ahora del borde de arriba. El ojo plano de reserva sube un 70 % de la altura de la pantalla.
- **Comprobado en el navegador:** los rayos salen del ojo y aclaran la página mientras sube; el ojo sale por arriba de la barra.

## Siguiente paso
- Que el equipo compare con `feat/mapa-billetes`: https://github.com/iisma-ai/Ojo-Ciudadano/compare/main...feat/web-ligera
- Pasar `revisor-legal` por el aviso en el pie, que antes estaba siempre a la vista.
- La entrada 3D necesita internet la primera vez (Three.js de jsDelivr). Sin red sale el ojo plano.
- El desplegable del buscador de empresas va dentro de su propio marco, así que el CSS de la web no le llega.
