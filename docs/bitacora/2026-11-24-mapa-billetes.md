# 2026-11-24 · Mapa general para el ciudadano: treemap de billetes y presupuesto por habitante (D-038)

**Quién:** Ignacio, con Claude (agente). **Rama:** `feat/mapa-billetes` (sale de `main`, aparte para poder deshacerlo sin tocar el trabajo de nadie).

## Qué se pidió
Repasar la web «dashboard a dashboard» poniéndose en la piel de un ciudadano medio, que no quiere ver tanto texto ni tantos números difíciles de interpretar. Para cada pantalla, el agente explica qué enseña y cómo la haría más visual, e Ignacio decide qué se implementa. Esta sesión cubre la primera pantalla, el **Mapa general**.

Ignacio decidió:
- un treemap «muy visual, que se represente con billetes (cuanto más dinero, más billetes)»;
- el presupuesto por habitante «de manera también gráfica: añade un muñequito»;
- la red de nodos, lo que recomiende el agente (se conserva como vista avanzada);
- entrar por el Inicio.

Todo va en una rama propia.

## Qué se hizo
- **`app/billetes.py`:**
  - treemap *squarified* propio, sin dependencias;
  - billete dibujado en SVG, que se repite: cada billete vale lo mismo en todo el gráfico, con valor redondo 1-2-5, y lo que no llega a uno se pinta como trozo;
  - los billetes grises son lo no gastado;
  - nombres escapados, componente `st.components.v2` que devuelve el bloque pulsado, figura del ciudadano y fila de figuritas por millón de habitantes;
  - animaciones solo con CSS, quietas con «reducir movimiento».
- **`ingesta/ine.py` (fuente F-12):** habitantes del INE a 1 de enero (serie ECP115490), con una petición y caché en `data/raw/ine/`. Si no hay red, la cifra no sale y el resto funciona.
- **`paginas/mapa_general.py`:**
  - la tarjeta del año (frase, barra, por habitante y figura);
  - el treemap general y el de cada consejería con su ficha, con menores y subvenciones en una línea aparte;
  - el gasto por consejería en líneas;
  - «Más opciones» con la vista de datos y la red de D-033;
  - la tabla y «Qué datos no tenemos» en desplegables;
  - la ficha de contrato, en líneas legibles.
- **`main.py`:** el Inicio es la página por defecto y el mapa pasa a llamarse «A dónde va el dinero».
- **Docs:** D-038, F-12 en 02, la sección del módulo en 03 y una fila en el plan (08).

## Comprobaciones
- **Tests:** 454, todos bien, con 10 nuevos (`tests/app/test_billetes.py`, `tests/test_ine.py`). `ruff` sin avisos. Se integró `origin/main` (D-035 a D-037) sin conflictos.
- **Probado en el navegador** (Chromium sin interfaz, sobre la base real):
  - vista general con 14 consejerías, en 2025 con 333 billetes de 100 M€;
  - clic en Sanidad, que muestra sus 15 contratos;
  - clic en un contrato, que muestra su ficha con señales y enlace oficial.
- **Cifras comprobadas:**
  - 2025: 33.296 M€ y 95 de cada 100 € gastados;
  - 7.113.886 habitantes a 1-ene-2025, unos 4.680 € por habitante.
- **Fallos que se encontraron y corrigieron al probar:**
  - el estilo del treemap estiraba la figura;
  - una variable tapada hacía el SVG altísimo;
  - los menores aplastaban a los contratos;
  - en la ficha, las cifras se cortaban.

## Siguiente paso
- Que el equipo vea la rama y decida si se fusiona (`https://github.com/iisma-ai/Ojo-Ciudadano/compare/main...feat/mapa-billetes`). Si no gusta, basta con no fusionarla.
- Seguir el repaso con el **Inicio** y después Contratos a revisar, Contratos atípicos, Mapa del dinero, Presupuesto y contexto, fichas de empresa y de órgano, y Asistente.
- Recordatorio del plan: el 25 no se añaden funciones.

## Segunda ronda: frascos y ojo con manos
Ignacio revisó la primera versión y pidió:
- las opciones junto al mapa;
- las fuentes en un botón de información;
- el gasto por consejería ordenado, solo con el porcentaje y sin la frase explicativa;
- quitar la tabla si no aportaba nada;
- volver al grafo con **frascos de dinero** de 100 billetes;
- cambiar el muñeco por **un ojo con manos**, como el logo;
- decir si lo de cada habitante es al año o al mes.

**Qué se hizo:**
- Fuera el treemap.
- `billetes.py` dibuja el frasco: tapa, cristal con fondo oscuro para que no se vean las líneas detrás, 100 huecos en 5 columnas, trozo de billete para la parte que falta y grises para lo no gastado.
- `red.NodoRed` acepta `imagen` y `tamano` opcionales, así que el «Mapa del dinero» no cambia.
- Frascos de consejería iguales y repartidos en una elipse, porque en círculo las etiquetas chocaban.
- Rótulo corto bajo cada frasco («Sanidad 39 €»).
- Botón «Opciones» al lado del título del mapa y botón «Fuentes» junto al título de la página.
- Gasto ordenado por porcentaje.
- Tabla eliminada.
- Lo que toca a cada habitante, «al año» y «al mes» (unos 390 € en 2025).
- La mascota es el trazo y la pupila del logo, con un brazo que levanta billetes y otro que saluda, y la pupila que mira a los lados.

**Comprobado en el navegador:**
- vista por defecto: 14 frascos sin solaparse;
- botón de fuentes;
- nivel con contratos (se satura un poco, pero es opcional);
- clic en el frasco de Sanidad, que abre su ficha con 39 de cada 100 € y el 99 % gastado.

**Tests:** 453, todos bien (los del treemap se cambiaron por los del frasco y la mascota).

## Tercera ronda: etiqueta en el frasco
Ignacio pidió que la etiqueta del frasco diga los euros que se lleva («solo el número con el símbolo del dinero») y que debajo vaya solo el nombre. Cada frasco lleva ahora una etiqueta de papel con «39 €» (o «<1 €», escapado en el SVG) y debajo, el nombre de la consejería o de la empresa. Los billetes se apilan por debajo de la etiqueta. Comprobado en el navegador; tests del frasco ampliados.
