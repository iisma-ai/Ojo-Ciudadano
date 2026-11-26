# 2026-11-26 · Menú «Explorar»: contratos atípicos en segunda posición

## Qué se ha hecho

- `app/main.py` (a petición de Isma): en el menú «Explorar», «Contratos atípicos» pasa de la última posición a la
  segunda, justo después de «Red del dinero». El resto queda en el mismo orden: Presupuesto y contexto, Ficha de
  empresa, Ficha de órgano y Aviso legal y fuentes. La lista `EXPLORAR` se escribe explícita; la navegación lateral
  (`SECCIONES`) no cambia.
- Directamente en `main`, a petición de Isma.
