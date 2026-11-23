# 2026-11-23 · Presentación animada

## Qué se hizo
- Carpeta `presentacion/`: presentación HTML animada (sin dependencias) con tema submarino y el ojo como guía.
- 8 diapositivas, cada una con pasos para controlar el ritmo con las flechas: portada, contratos como burbujas
  (llenado = gastado), Comunidad de Madrid y consejerías, datos públicos pero no accesibles, el ojo ilumina,
  módulos, señales y asistente, cierre.
- Todo el contenido está en `presentacion/diapositivas.js`; las cifras salen de la base (23-nov-2026) y están
  en el objeto `DATOS`. Cómo editarla: `presentacion/LEEME.md`.

## Segunda versión: 3D realista
- La primera versión (SVG y CSS) parecía de dibujos animados. Se rehace en WebGL con Three.js 0.169 (CDN,
  sin instalar nada): burbujas de cristal con reflejos e irisación y líquido dentro, globo ocular 3D con
  iris de fibras y córnea, superficie del mar vista desde abajo, rayos de sol, partículas, niebla de
  profundidad y posproceso (resplandor, aberración, viñeta, grano). El contenido sigue en `diapositivas.js`.
- Detalles técnicos: el cristal suma solo sus reflejos (mezcla aditiva) para que el líquido conserve el color;
  tono `Neutral` porque ACES volvía morados los azules; se fija `pow` con `clamp` (un NaN dejaba la imagen en
  negro a través del resplandor).
- Hay que servirla por HTTP (módulos ES): ver `presentacion/LEEME.md`.

## Pendiente
- Capturas o vídeos de la aplicación en las burbujas de tipo `captura` (carpeta `presentacion/media/`).
- Pasar los textos por `revisor-legal` antes de la demo.
- Probar en el proyector o pantalla final; ajustar tiempos.
