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
