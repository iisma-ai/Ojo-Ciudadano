# 2026-11-26 · Presentación para el jurado (tres diapositivas)

## Qué se ha hecho

- **`presentacion/jurado.html`** (a petición de Isma), con su contenido en `diapositivas-jurado.js` y sus estilos
  en `jurado.css`. Mismo motor 3D que la presentación de la exposición. Sigue los requisitos de la entrega, con
  tres diapositivas como máximo:
  1. **En la roca, sobre el mar, con el ojo:** nombre del proyecto, integrantes (Ismael El Harrak e Ignacio Vallejo
     Garach, nombres dados por Isma) y la propuesta, que cualquier ciudadano pueda ver a dónde va su dinero.
  2. **Salto al agua:** el mar turbio («Públicos. Pero no accesibles.») se aclara con la luz del ojo; panel del
     problema y panel de los datos. Los enlaces principales son los del Catálogo de Datos Abiertos de la Comunidad
     (ocho conjuntos de `ingesta/cm_abiertos.py` y el catálogo completo). Debajo, las fuentes de contratos y
     subvenciones registro a registro, porque el catálogo no las tiene (docs/02-fuentes-datos.md, F-06).
  3. **Más abajo:** qué hacemos con los datos (unión y limpieza, seis indicadores, Isolation Forest), el agente
     con una pregunta animada (la de los helicópteros, con las cifras de la presentación), utilidad, impacto y
     viabilidad, y el QR con los enlaces a la web y al repositorio.
- **Motor (`escena3d.js`), dos cambios pequeños que no afectan a `index.html`:** un panel admite `clase` para
  estilos propios, y un clic sobre un enlace abre su página en lugar de pasar de diapositiva.
- `presentacion/README.md`: sección de la versión para el jurado.

## Pendiente

- **Verla en el navegador.** Desde esta sesión Chrome no llega al servidor local, así que no se ha comprobado el
  encaje de los textos. Hay que revisar sobre todo que los paneles de la diapositiva 2 y el de viabilidad no se
  salgan por abajo en pantallas de 16:10 o más bajas.
- Revisar los textos con `revisor-legal` antes de mandarla.
- Si se publica en `/presentacion/` de la portada, el comando de build ya copia `presentacion/*.html`, `*.js` y
  `*.css`, así que `jurado.html` iría también.

## Siguiente paso

Revisarla en local y, si gusta, fusionar `feat/presentacion-jurado` en `main`.
