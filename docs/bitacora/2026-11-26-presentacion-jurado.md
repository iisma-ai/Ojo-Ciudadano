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

## Cambios tras verla (a petición de Isma)

- **Diapositiva 2:** fuera el paso turbio con «Públicos. Pero no accesibles.». Del salto se pasa directamente a la
  escena iluminada, y el problema y los datos aparecen a la vez, con la misma animación de entrada de los paneles.
- **Diapositiva 3:** todo a la vez y resumido. Las señales, el aprendizaje automático y el agente van en un solo
  bloque, sin la lista de los seis indicadores; fuera el chat de los helicópteros. Utilidad, impacto y viabilidad
  **sin decir que la web ya está en marcha** (Isma no quiere divulgarlo todavía): fuera «Ya está en marcha, con
  datos reales» y lo de que se actualiza sola.
- **Diapositiva 4, nueva:** el ojo acompaña hasta una captura de la página de inicio de la web pública
  (`capturas/web-inicio.jpg`, tomada con Chrome el 26-nov), con el enlace, el QR y el enlace al código al lado.
  Las bases piden tres diapositivas como máximo: se avisó a Isma y se añadió igualmente.

- **Sin notas al pie** (a petición de Isma): fuera los textos pequeños en gris de los paneles «Los datos» y «Qué
  hacemos con los datos» (periodo de los datos y fechas de descarga). Los enlaces a las fuentes siguen en el panel
  de los datos.

## Pendiente

- **Verla en el navegador.** Desde esta sesión Chrome no llega al servidor local, así que no se ha comprobado el
  encaje de los textos. Hay que revisar sobre todo que los paneles de la diapositiva 2 y el de viabilidad no se
  salgan por abajo en pantallas de 16:10 o más bajas.
- Revisar los textos con `revisor-legal` antes de mandarla.
- Si se publica en `/presentacion/` de la portada, el comando de build ya copia `presentacion/*.html`, `*.js` y
  `*.css`, así que `jurado.html` iría también.

## Siguiente paso

Revisarla en local y, si gusta, fusionar `feat/presentacion-jurado` en `main`.
