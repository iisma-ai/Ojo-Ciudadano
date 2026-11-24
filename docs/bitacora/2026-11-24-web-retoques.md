# 2026-11-24 · Retoques de la web: mapa con burbujas o frascos, buscador, fondo y cabecera

**Quién:** Lucas con Claude (agente). Rama `feat/web-retoques`, sacada de `feat/web-ligera`.

## Qué se ha hecho (D-046)

- **Cabecera:** solo «Ojo Ciudadano», sin el icono.
- **Pie:** el logo con el nombre.
- **Inicio:**
  - sin el subtítulo ni la línea de cifras;
  - buscador como barra de búsqueda: cápsula de cristal con lupa, sin flecha y sin el recuadro oscuro del iframe.
- **Fondo:** burbujas más realistas, sin trazo de rotulador.
- **Mapa del dinero** (antes «A dónde va el dinero»):
  - interruptor entre burbujas (por defecto) y frascos de 100 €;
  - las burbujas recuperan el llenado según lo gastado, los menores y las subvenciones agrupados, las cifras de la ficha y las tablas;
  - frascos redibujados.
  - La red de adjudicaciones pasa a llamarse «Red del dinero».
- **Doble clic en un nodo del mapa:** ya no abre una pestaña rota.
- **Error de «Contratos a revisar»** (`adjudicatario_ente_publico does not exist`): la base local era anterior a D-036. Se cargó INVENTE (`ingesta.invente`, 4.602 entes) y se recalcularon los indicadores (`indicadores.ejecutor`, 237 adjudicatarios marcados como ente público). El ejecutor falla al imprimir el resumen final en la consola de Windows (cp1252), pero el cálculo queda guardado.

## Comprobado

- En Chrome:
  - el Inicio con el buscador escribiendo «hospital»;
  - el pie;
  - el mapa en burbujas y en frascos;
  - el doble clic en un frasco pequeño: no abre pestaña y sale la ficha.
- `pytest`: 476 en verde. Se ajustó `test_nodos_svg_y_texto` al nuevo dibujo de la burbuja.

## Siguiente paso

- Lucas sigue con más cambios.
- Cuando estén revisados, integrar con `feat/web-ligera` y `main`.
