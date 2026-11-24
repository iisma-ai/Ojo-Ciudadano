# 2026-11-24 · Inicio para el ciudadano (D-039)

**Quién:** Ignacio, con Claude (agente). **Rama:** `feat/mapa-billetes` (la misma del mapa, para deshacer el rediseño de una vez).

## Qué se pidió
Segunda pantalla del repaso «dashboard a dashboard»: el Inicio. El agente explicó qué enseñaba y qué fallaba para un ciudadano medio:
- las cuatro cifras sin referencia;
- «249.999 contratos con alguna señal», que asusta y se malinterpreta;
- puertas pequeñas, sin el mapa ni el asistente;
- sin buscador;
- seis párrafos de señales.

Ignacio aceptó las cuatro propuestas: quitar esa cifra, cuadrícula de 100 contratos, buscador directo y las cuatro puertas.

## Qué se hizo
- **`paginas/inicio.py` reescrita:**
  - bienvenida con la mascota y la frase;
  - buscador único (`buscador.todo`);
  - cuatro puertas pulsables enteras: el enlace se estira sobre la tarjeta con CSS, con navegación normal de Streamlit;
  - cifras en una línea;
  - seis tarjetas de señales con cuadrícula ámbar, cifra «de cada 100» y botón «¿Qué significa?»;
  - botón «Fuentes» con el aviso completo, las fuentes y las fechas.
- **`billetes.py`:**
  - `svg_cuadricula`, `cifra_de_100` y `texto_de_100_contratos`;
  - los iconos de las puertas (`ICONOS_PUERTA`);
  - las animaciones del ojo en `CSS_OJO`, compartidas con el mapa.
- **`empresa.py` y `organo.py`:** leen `?empresa=` y `?organo=` cuando se llega desde el buscador.
- `st.html` quita los SVG, así que los dibujos se pintan con el componente de `billetes.pintar`.

## Comprobaciones
- **Tests:** 457, todos bien (dos nuevos: cuadrícula e iconos). `ruff` sin avisos.
- **Navegador:**
  - la portada completa;
  - escribir «Hospital Universitario La Paz» y elegirlo abre `/organo?organo=HOSPITAL+UNIVERSITARIO+LA+PAZ` con su ficha;
  - pulsar en medio de la tarjeta «¿A dónde va el dinero?» abre `/mapa_general`.
- **Cifras de las señales** (base del 23-nov): una sola oferta 39, sin anuncio 31, muchos menores 17, rebaja nula o muy alta 19, modificaciones de más del 20 % 2, y una empresa concentra el gasto menos de 1, de cada 100 contratos comprobados.

## Siguiente paso
- Que el equipo vea la rama (`https://github.com/iisma-ai/Ojo-Ciudadano/compare/main...feat/mapa-billetes`).
- Seguir el repaso con **Contratos a revisar**.
