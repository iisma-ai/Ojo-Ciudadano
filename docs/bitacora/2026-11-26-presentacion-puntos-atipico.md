# 2026-11-26 · Presentación: vuelven los puntos ámbar del atípico

## Qué se ha hecho

- **Diapositiva 6, paso del atípico** (a petición de Isma): las dos frases que están al lado de la burbuja «Atípico»
  («Aprende de las cifras» y «Destaca lo que se sale de lo habitual») vuelven a ser una lista de señales activas, con
  su punto ámbar luminoso. El último cambio (`b45a3d8`) las había dejado como texto suelto. Se mantienen el
  tamaño 32, la posición (x 620, ancho 540) y la lista sigue sin cabecera «Señales» (`titulo: ""`).
- `estilo.css`: la separación mayor entre las dos frases ahora también se aplica a las señales de los paneles que no
  son el chat (`.senal + .senal`).
- **Diapositiva 8, QR:** `DATOS.urlApp` pasa a ser `https://ojo-ciudadano.pages.dev`, la web pública (D-056). El QR lo
  genera la propia página con `qrcode-generator` dentro del panel de cristal con el logo; ya no sale el hueco.

## Pendiente

- Verlo en el navegador: desde esta sesión no se pudo arrancar el servidor local.
- Escanear el QR con un móvil en el proyector de la demo.

## Siguiente paso

Fusionar `fix/presentacion-puntos-atipico` en `main` antes de presentar.
