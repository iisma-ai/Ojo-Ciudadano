# 2026-11-23 · Mapa general de un vistazo, sin recortes (D-032)

- **Autor:** Claude (agente), a petición de la persona que coordina
- **Fase del plan:** 2, víspera del H3. Decisión D-032, que ajusta D-026.

## Qué se hizo

1. **Círculos cortados:** la distribución por física dejaba nodos fuera del lienzo. Ahora el diseño es **radial y calculado** (`red.posiciones_radiales`, `red.alternar_tamanos`): los nodos nacen en su sitio, el lienzo se dimensiona para el diseño y la física solo aporta el efecto elástico al arrastrar. Mismo dibujo en cada carga.
2. **Todo de un vistazo:** el mapa dibuja a la vez la Comunidad, sus consejerías y los contratos más grandes de cada una (1 a 5 por consejería). Selector de **niveles** (solo consejerías, o consejerías y contratos) y opción de añadir menores y subvenciones agrupados. Los contratos principales de todas las consejerías salen de una sola consulta (`datos_mapa.contratos_principales`) con caché de una hora.
3. **Ficha lateral:** al pulsar un círculo, su ficha aparece a la derecha, sin mover el mapa. Botón para ampliar una consejería a sus 15 contratos más grandes.
4. **Escalas por grupo:** consejerías, contratos y agrupados tienen su propia escala de tamaño y color.
5. **«Mapa del dinero»:** mismo diseño radial.
6. Tests: contratos principales por consejería, menores y subvenciones agrupados, diseño radial y orden alternado.

## Por qué ya no hay que entrar en cada consejería

Con una sola capa de consejerías se veía lo que gasta cada una; el segundo nivel (sus contratos) antes exigía pulsar. Ahora se ve todo a la vez, y quien prefiera menos ruido elige «Solo consejerías».

## Datos

Esta máquina estaba 73 commits por detrás de `main` (D-027 a D-031 de otras personas). Se regeneró la base: `ingesta.tacp`, `modelo.carga`, `indicadores.ejecutor`, `anomalias.deteccion`, `asistente.texto`.

## Qué falta

1. Revisión con `revisor-legal` de los textos nuevos del mapa.
2. Probar el mapa en un móvil real (las columnas se apilan, pero el diseño radial no está medido en ese ancho).
