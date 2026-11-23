# 2026-11-23 · Mapa general del dinero y mapa de nodos arrastrable

- **Autor:** Claude (agente), a petición de la persona que coordina
- **Fase del plan:** 2, un día antes del hito H3. Decisión D-026.

## Qué se hizo

1. **Componente de nodos** (`app/red.py`): círculos arrastrables al estilo Neo4j con `streamlit-agraph`. Tamaño y color = dinero, relleno = parte gastada (resto en gris), líneas todas iguales, sin zoom, física que arrastra a los nodos conectados, dibujo repetible (`randomSeed`). Los círculos son imágenes SVG generadas con el relleno.
2. **Mapa general** (`paginas/mapa_general.py`, `app/datos_mapa.py`), primera pantalla y por defecto:
   - La Comunidad en el centro y sus consejerías y órganos alrededor, con selector de periodo y de vista (presupuesto y gasto, contratos de la Plataforma, contratos del portal, subvenciones).
   - Cifras de arriba: dinero disponible, gastado (con %), sin gastar y pagado. Barras de «dinero sin gastar» y tabla por consejería.
   - Al pulsar una consejería: sus cifras y su mapa de contratos (los 15 más grandes del año, más los menores y las subvenciones agrupados).
   - Al pulsar un contrato: importe, presupuesto de licitación, ofertas recibidas, cómo se contrató, adjudicataria, **qué parte del dinero de la consejería supone**, señales y enlace al expediente.
   - 2026 solo tiene presupuesto inicial: se dice que el gasto no está publicado y no se inventa.
3. **«Mapa del dinero»** (organismo y sus empresas) pasa al nuevo componente.
4. Tests: `tests/app/test_mapa_general.py` (periodos, reparto con y sin gasto, contratos de una consejería, detalle, SVG y texto).

## Resultados (base del 23-nov)

- 2025: 33.286 M€ disponibles, 31.770 M€ gastados (95,4 %), 1.516 M€ sin gastar. Sanidad: 12.935 M€, 99,2 % gastado, 38,8 % del dinero de la Comunidad.

## Decisiones y desviaciones

- **D-026**: nueva dependencia `streamlit-agraph` y «Mapa general» como pantalla por defecto (la portada «Inicio» sigue como segunda entrada; si se prefiere al revés, es un parámetro en `main.py`).
- Se encontró un fallo sutil: si un nombre de un nodo cambia entre ejecuciones (el orden de las adjudicatarias no era fijo), Streamlit ve un componente nuevo y se pierde el clic. Las consultas ordenan ahora los nombres.

## Lenguaje y privacidad (D-002, D-007)

- No hay acusaciones: solo importes, porcentajes y procedimiento. Las personas físicas salen agregadas y sin nombre.
- Importes de la Plataforma (sin IVA) y del portal (con IVA) nunca se suman; presupuesto y contratos no se cruzan partida a partida y la pantalla lo avisa.

## Qué falta

1. Pasar los textos nuevos por `revisor-legal` (leyenda, «Qué datos no tenemos», fichas de contrato).
2. Probar el mapa en móvil y con teclado (D-023, A-10): el componente no tiene alternativa de teclado; la tabla de debajo contiene las mismas cifras.
3. Ir a por el dato que falta: ejecución de 2026 cuando la Comunidad la publique, y los criterios de adjudicación (no están en los datos abiertos).
4. Llevar el «% del dinero disponible» a más sitios (ficha de órgano, ficha de empresa).
