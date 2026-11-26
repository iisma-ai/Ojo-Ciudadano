# 2026-11-26 · Presupuesto y contexto sin la pestaña de encargos

## Qué se ha hecho

- **Página «Presupuesto y contexto»** (`app/paginas/contexto.py`, a petición de Isma): se quita la pestaña «Encargos a
  medios propios». Los encargos (D-028) sí están en la base local, pero no en la del servidor que sirve la web, así
  que la pestaña solo enseñaba «no están disponibles todavía». La pestaña de recursos ante el Tribunal pasa de la
  posición 6 a la 5.
- No se toca nada más: los encargos siguen en las fichas de órgano y de empresa, en atípicos y en el asistente, y
  `datos_flujos.resumen_encargos` se queda (ahora sin uso en la interfaz) por si se cargan los datos en el servidor.

## Pendiente

- Si se cargan los encargos en el servidor (`despliegue/cargar_datos.ps1`), se puede recuperar la pestaña
  revirtiendo este commit.
