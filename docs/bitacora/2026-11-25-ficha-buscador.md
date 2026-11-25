# 2026-11-25 · Fichas que enseñaban siempre la misma empresa

**Quién:** Ismael con Claude (agente). Rama `fix/ficha-buscador`.

## Qué pasaba

Al buscar una empresa desde el Inicio, la ficha enseñaba los datos de otra, siempre la misma (una de material médico). Se reprodujo en Chrome:
1. se elige Fresenius Kabi en el buscador de la ficha de empresa;
2. se vuelve al Inicio y se busca Ferrovial;
3. la dirección dice `?empresa=A28019206` (Ferrovial), pero la ficha enseña Fresenius.

La causa es `buscador or dirección`: lo elegido en el buscador de la ficha queda en la sesión y tapa la dirección. La ficha de organismo tenía el mismo fallo.

## Arreglo (D-058)

- `buscador.con_direccion`: manda la dirección, salvo que se acabe de elegir algo nuevo en el buscador de la ficha (que entonces pasa a la dirección).
- Test `tests/app/test_buscador_direccion.py`.
- Comprobado en Chrome: después de elegir Fresenius en la ficha, buscar Ferrovial desde el Inicio enseña Ferrovial.
- `pytest` en verde.

## Siguiente paso

Integrar en `main`: se publica sola en la web pública (D-056).
