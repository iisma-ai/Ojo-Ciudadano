# 2026-11-25 · Presentación más nítida y más simple

## Qué se ha hecho

- **Nitidez del ojo y del agua.** Primero se probó antialiasing MSAA de 4 muestras y resolución forzada a 2x en el compositor: dejaba el fondo en negro en el portátil de la demo y se retiró. Queda la calidad de antes (hasta 1,5x) más un pase FXAA al final, que casi no gasta,
  y además la textura de anillos del iris a 1024 px y la mitad de grano.
- **Aristas de los grafos más suaves.** Los enlaces entre burbujas brillan menos (opacidad y pulso más bajos) y son
  algo más finos, para que no quiten protagonismo a las burbujas.
- **Diapositiva del reparto de 2025.** Fuera la nota «Presupuesto de 2025 de cada consejería…»; la burbuja de la
  Comunidad de Madrid pasa de radio 150 a 210 y su etiqueta puede partirse en dos líneas.
- **Fichas de Sanidad y del contrato de la vacuna del VPH.** Reducidas a título, dos cifras grandes y, en el contrato,
  su única señal. Letra de 28 en lugar de 18. La de Sanidad sube a la parte de arriba (y = 310) para no pisar las
  burbujas del fondo y va sin línea de fuente; la del contrato mantiene una corta.
- **«Señales, no acusaciones».** El panel con rejillas de puntos, texto explicativo y fuente se cambia por tres cifras
  grandes (39, 31 y 17 de cada 100) con un rótulo legible cada una. Para separarlas del fondo sin caja, cada cifra y
  rótulo lleva un halo oscuro difuminado detrás (clase `resalte`) y los números van en ámbar, el color de las señales.

Los paneles aceptan ahora `tam` y las cifras también (`escena3d.js`).

## Pendiente

- Probarla en el ordenador y el proyector de la demo (no se ha podido capturar en un navegador sin interfaz).
- La diapositiva de señales ya no muestra la fuente en pantalla: decir de palabra que salen de la Plataforma de
  Contratación y el portal de la Comunidad, o añadirla al cierre si el jurado la pide.
