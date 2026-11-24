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
