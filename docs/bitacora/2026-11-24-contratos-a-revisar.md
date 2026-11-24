# 2026-11-24 · «Contratos a revisar» para el ciudadano (D-042)

**Quién:** Ignacio, con Claude (agente). **Rama:** `feat/mapa-billetes`.

## Antes de empezar
- **Ramas de Ismael:**
  - `feat/web-fluida` (D-040): caché de consultas, fondo sin repintar y asistente sin SQL.
  - `feat/billetes-fluido` (D-041): nuestra rama más la web fluida, con la mascota que se para tras unas vueltas.
  - Por decisión de Ignacio se integró `feat/billetes-fluido` en `feat/mapa-billetes`, sin conflictos y con 462 tests en verde. `main` solo traía cambios de la presentación.
- **Base local:**
  - «Contratos a revisar» fallaba al abrir un contrato con la señal de concentración, porque faltaba la tabla `adjudicatario_ente_publico` de D-036.
  - Se ejecutaron `ingesta.invente` (4.602 entes), `indicadores.ejecutor` y `anomalias.deteccion` con la web parada.
  - **`ingesta.cpv` falló:** el portal de la Plataforma devolvió una página «Request Rejected» y el módulo la guardó como si fuera la lista de CPV. Se borró ese fichero y no se reintentó, para no insistir contra el portal. Sin la lista, solo falta la línea «Objeto (CPV…)» en las fichas.
  - **Para Ismael:** `ingesta/cpv.py` debería comprobar que lo descargado es XML antes de guardarlo.

## Qué se pidió
Tercera pantalla del repaso. Ignacio aceptó las cuatro propuestas:
- filtros sencillos;
- tarjeta clara con importe, adjudicataria y etiquetas;
- interior con lo justo;
- orden por defecto «Más señales primero».

## Qué se hizo
- **`paginas/alertas.py`:**
  - título con el aviso en el icono de información;
  - buscador y botón «Más filtros» en una línea;
  - señales como botones con icono y recuento;
  - «Ver más contratos» de 30 en 30 (vuelve a 30 al cambiar los filtros).
- **`senales.py`:**
  - `cabecera_contrato`: título limpio, importe, adjudicataria, organismo, año y etiquetas ámbar;
  - `tarjeta_contrato`: el expediente arriba y el atípico en una frase con «Ver el detalle»;
  - `mostrar`: icono, frase con cifras, gráfico y «¿Qué significa?» (con el contexto de R-01).
- **`datos.alertas`:** trae `adjudicatarios`, con las personas físicas agregadas.
- **`textos`:** `titulo_limpio`; `ORDEN_ALERTAS` empieza por «Más señales primero».

## Comprobaciones
- **Tests:** 463, todos bien (uno nuevo, de `titulo_limpio`). `ruff` sin avisos.
- **Navegador:**
  - lista de 30 tarjetas;
  - el botón «Una sola oferta» deja 30 contratos y todos tienen esa señal;
  - «Ver más contratos» pasa de 30 a 60;
  - el contrato de la vacuna del herpes zóster se abre con el expediente arriba, las dos señales con gráfico y el atípico;
  - las fichas de empresa (GSK) y de organismo (La Paz) cargan sin errores con la tarjeta nueva.

## Siguiente paso
- Que el equipo vea la rama: `https://github.com/iisma-ai/Ojo-Ciudadano/compare/main...feat/mapa-billetes`.
- Seguir con **Contratos atípicos**.

## Ajuste: una subcaja por señal
Ignacio pidió más explicabilidad dentro de cada contrato, para que se distingan mejor las explicaciones de cada señal, con dos subcajas que encajen con el formato.

Cada señal va ahora en su propia caja con borde:
- de dos en dos y con la misma altura, que con tres señales pasan a dos filas;
- con borde ámbar a la izquierda;
- con el nombre en ámbar y su icono, la etiqueta «En este contrato», la frase con las cifras, el gráfico y «¿Qué significa?» abajo, alineado.

Detalles técnicos:
- en `senales.py`, la clave `cajasenal_…` de cada caja usa un resumen del `contrato_id`;
- en `estilo.css`, hay que reforzar el selector y usar una sombra interior para que el borde ámbar gane al estilo de cristal.

Comprobado en el navegador: las dos cajas del contrato de la vacuna miden 546 px.

## Ajuste: color, «sin anuncio público» y gráfico de concentración
Ignacio pidió tres cambios:
- otra visualización para la concentración: eligió el ranking de barras con la línea de «la mitad»;
- que se entendiera qué significa el 85 % de «sin anuncio público»;
- sustituir el naranja: eligió el azul de cristal.

**Qué se hizo:**
- **R-02:**
  - «En este contrato» (la vía de adjudicación, en lenguaje llano) y «Para comparar» (de cada 100 € del organismo en esa fuente, cuántos fueron sin anuncio).
  - Al revisarlo se encontró que la frase decía «de este tipo» y el cálculo no filtra por tipo. Corregido.
- **R-04:**
  - `graficos.reparto` es ahora un ranking de barras de «de cada 100 €», con la empresa del contrato en azul y una línea de puntos en 50.
  - Frase nueva que explica cuándo salta la señal.
  - En esta base local el nombre del sector no sale porque la lista de CPV no se pudo bajar; se dice «de este sector».
- **Color:**
  - etiquetas `:blue-badge` con estilo de cristal (`.stMarkdownBadge` en `estilo.css`);
  - nombre y borde de las subcajas en #7DB3FF;
  - cuadrícula del Inicio en el mismo azul (`billetes.COLOR_SENAL`);
  - `docs/marca.md` actualizado: el ámbar queda para las líneas de referencia de los gráficos.

**Comprobaciones:** comprobado en el navegador con el contrato de la vacuna (cajas de 550 px, iguales). Tests en verde.

## Arreglo: «Muchos contratos menores» sin resultados
Ignacio vio que al elegir «Muchos contratos menores» no salía nada.
- **Causa:** la lista excluye por defecto los contratos menores (exige 3 señales comprobables y en un menor solo se comprueban 2), y R-03 solo se calcula en menores.
- **Arreglo:** si se elige una señal que solo se comprueba en menores (`SOLO_MENORES = {"R-03"}`), la lista los incluye sola y lo dice en una línea.
- **Comprobado en el navegador:** 30 contratos, todos con la señal, y el contrato abierto sin errores.
- **De paso:** `titulo_limpio` pasa a frase normal los títulos escritos todo en mayúsculas.

## Ajuste: gráficos y frases de menores, modificaciones y rebaja
Ignacio dijo que los gráficos de R-03 y R-05 eran poco intuitivos, feos o sosos, y preguntó qué significa R-06 y cómo sabemos que la empresa «ganó». Ganó porque es a quien se adjudicó el contrato, y eso lo publican los datos oficiales; la rebaja compara el precio adjudicado con el precio de salida.

**Qué se hizo:**
- **R-03:**
  - bloques de los contratos menores de la ventana de 12 meses en que más suman, frente al máximo;
  - frase «es uno de los N… juntos suman X».
- **R-05:**
  - columnas «precio adjudicado» y «con modificaciones», con dos tramos (hasta el 20 % y por encima), línea del +20 %, subida en grande y leyenda;
  - frase «En este contrato» y «Para comparar».
- **R-06:**
  - regla de la rebaja con las zonas de la señal, el contrato y lo habitual (`datos.baja_habitual`, mediana de los parecidos);
  - frase con el precio de salida, las ofertas y el precio adjudicado. Admite adjudicaciones por encima del precio de salida (hasta un 70 % en la base).
- Textos de «¿Qué significa?» de R-05 y R-06 reescritos (también salen en el Inicio).

**Comprobaciones:**
- tests de los gráficos actualizados y uno nuevo;
- comprobado en el navegador abriendo un contrato de cada señal, sin errores.

## Integración de `main` y nueva vista de los contratos menores
- **Pull de `main`** (a petición de Ismael, antes de seguir): traía el arreglo de `ingesta/cpv.py` y un cambio en la presentación.
  - El único conflicto estaba en `docs/08-plan.md` (filas añadidas por las dos partes) y se conservaron las dos.
  - 468 tests y las nueve pantallas sin errores.
  - Con el arreglo, la descarga de CPV sigue rechazada por el portal, pero ya no guarda nada falso. Para tener los nombres de los sectores hay que copiar `data/raw/cpv/CPV2008-2.04.gc` de alguien del equipo.
- **R-03 a petición de Ignacio:**
  - un contrato grande con la suma de los contratos menores, el máximo de un contrato menor y cuántas veces el máximo;
  - debajo, un icono por contrato menor (este en azul) con su precio, fecha y título al pasar el ratón;
  - `billetes.html_menores`; se quita el gráfico de bloques.
  - Comprobado en el navegador: 9 iconos, etiqueta al pasar el ratón y sin errores.
