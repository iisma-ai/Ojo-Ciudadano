# 2026-11-25 · El ojo del asistente mira a los lados

**Quién:** Claude (agente), a petición del equipo. Rama `feat/ojo-asistente`.

- **Antes:** en la pantalla del asistente el ojo se balanceaba entero.
- **Ahora:**
  - el cristal queda quieto;
  - solo el iris se mueve dentro de él, con saltos rápidos y pausas: centro, izquierda, centro, derecha, arriba a la derecha, centro (ciclo de 12 s);
  - el iris sigue girando (24 s por vuelta) y el ojo flota despacio.
- Sin tarjeta gráfica o con «reducir movimiento», queda quieto.
- Comprobado en Chrome con capturas en varios momentos del ciclo.
