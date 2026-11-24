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

## Segunda tanda (D-047)

- Mapa de burbujas redibujado en un lienzo propio con la estética de la presentación (`app/burbujas.py`): cristal, líquido con superficie ondulada, motas de luz por las líneas, cuadro al pasar el ratón y clic que abre la ficha.
- Barra única por consejería: dinero disponible con lo gastado dentro, en HTML. Las dos gráficas anteriores quedan en «Gráficas por separado».
- Pie: aviso legal plegado y el logo centrado al final. En el Inicio, solo el logo.
- Logo arriba en todas las pantallas menos el Inicio.
- Buscadores de las fichas como barra.
- Arreglado: volver al Inicio después de buscar llevaba otra vez a la ficha.
- Comprobado en Chrome: el mapa con burbujas, el clic en Sanidad (sale su ficha), la barra, el pie, la cabecera y la vuelta al Inicio después de buscar «hospital».

## Tercera tanda, 25-nov (D-048 y D-049)

- **Portada nueva:**
  - título centrado y buscador más estrecho;
  - «Siempre fueron públicos. Ahora, por fin, accesibles.» con un mapa de burbujas vivo que lleva a cada ficha;
  - tres puertas (sale «Busca una empresa»);
  - el asistente de IA con el ojo de cristal;
  - «Contratos que destacan» con tres señales en dinero, cada una con su dibujo y sus fuentes enlazadas.
- **Mapa del dinero:** sin frascos y en dos niveles por defecto. Las cifras de la ficha ya no se cortan.
- **Comprobado en Chrome:** la portada completa y el clic en Sanidad desde la vista previa (abre el mapa con Sanidad marcada y su ficha). `pytest`: 476 en verde.
- **Datos de la portada** (base local, 25-nov):
  - 5.999 M€ con una sola oferta, de 26.488 M€ comprobados;
  - +226 M€ por modificaciones en 396 contratos;
  - Metro de Madrid, 96 %.

## Cuarta tanda, 25-nov (D-050)

- Logo arriba también en el Inicio, sin el logo grande encima del título.
- Inicio:
  - mapa a la izquierda y texto a la derecha, sin el texto de debajo del mapa;
  - la lista del buscador por encima de la página;
  - barras para las modificaciones y anillo partido para la concentración.
- Mapa del dinero: pulsar una consejería la pone en el centro con sus 15 contratos, menores y subvenciones.
- Red del dinero con las burbujas del lienzo. Arreglado el error `StreamlitWidgetAlreadyInstantiatedError` al pulsar un organismo: la elección se guarda y se aplica antes del desplegable.
- Comprobado en Chrome:
  - el buscador del Inicio, escribiendo «hospital»;
  - las tarjetas;
  - Sanidad al centro;
  - Metro de Madrid en la Red del dinero.

  `pytest`: 476 en verde.

## Quinta tanda, 25-nov (D-051)

- Logo a la izquierda del título del Inicio; arriba solo el nombre en el Inicio.
- Buscador entre el mapa y «Qué ofrecemos».
- El aviso de las señales y las fuentes pasan de la portada a «Contratos a revisar».

## Sexta tanda, 25-nov (D-052 y D-053)

- Tarjetas de «Qué ofrecemos» pulsables enteras (comprobado: un clic en una zona vacía de la tarjeta lleva a «Contratos a revisar»).
- Mapa del dinero: «Presupuesto 2025» en una barra (total, gastado y sin gastar). Lo de cada habitante, en un desplegable al final.
- Portada: el mapa de burbujas con la animación de la presentación (ondas dentro, perlas de luz en las líneas y la cifra en el centro), comparado en Chrome con la escena 4 de la presentación.
