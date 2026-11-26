# 2026-11-26 · README: enlaces a las dos presentaciones y nombres del equipo

## Qué se ha hecho

- Rama `docs/readme-presentaciones`, que parte de `docs/readme-breve` (el README más breve de Ignacio), a petición de
  Isma.
- Debajo del enlace a la web, dos enlaces que se pueden pulsar, en este orden: **Presentación para el jurado**
  (`/presentacion/jurado.html`) y **Presentación de la exposición** (`/presentacion/`). Debajo, los nombres del
  equipo, tal como están en la sección «Equipo» de Ignacio.
- La sección «Presentación» explica las dos y cómo verlas en local.

## Pendiente

- Los dos enlaces solo funcionan cuando Cloudflare publique `/presentacion/` (comando de build del Worker, con la
  carpeta `capturas/`) y `feat/presentacion-jurado` esté en `main`. Hasta entonces dan 404.
- El nombre de Isma: en la presentación del jurado es «Ismael El Harrak» y en el README «Ismael El Harrak El
  Harraq». Hay que dejar uno.
