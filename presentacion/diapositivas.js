/* CONTENIDO DE LA PRESENTACION
 *
 * Aqui esta todo lo que se ve. Para cambiar un texto, una cifra o una burbuja, edita este fichero;
 * no hace falta tocar nada mas. Las coordenadas son de un escenario de 1920 x 1080 (x a la derecha,
 * y hacia abajo) y se escala solo a cualquier pantalla.
 *
 * Cada diapositiva tiene:
 *   profundidad  0 (superficie, luz) a 1 (fondo oscuro): cambia el color del agua
 *   ojo          {x, y, escala, mira:{x,y}}  donde esta el ojo y hacia donde mira
 *   elementos    lista de cosas que aparecen; `paso` dice con que pulsacion (0 = al entrar)
 *
 * Elementos:
 *   {tipo:"texto",   x, y, texto, tam, clase, paso}              clase: "titulo" | "subtitulo" | "nota"
 *   {tipo:"cifra",   x, y, valor, formato, texto, paso}          numero que sube hasta `valor`
 *   {tipo:"burbuja", id, x, y, r, llenado, etiqueta, valor, tono, paso}
 *                    llenado 0..1 = lo gastado; tono: "azul" | "ambar" | "agua"
 *   {tipo:"enlace",  de, a, paso}                                 linea de agua entre dos burbujas
 *   {tipo:"captura", id, x, y, r, src, etiqueta, paso}           burbuja con una imagen o video dentro
 *   {tipo:"niebla",  paso}                                        capa turbia (lo que no se ve)
 *   {tipo:"luz",     paso}                                        el ojo ilumina la escena
 */

// Cifras reales de la base de datos (23-nov-2026). Cambialas aqui si se regenera.
const DATOS = {
  contratosPortal: 1354441, // contratos del portal de la Comunidad
  adjudicadoMillones: 22857, // adjudicado en la Plataforma de Contratacion, sin IVA
  subvenciones: 863510, // concesiones de subvenciones (BDNS)
  organismos: 132,
  indicadores: 6,
};

// Tamano y llenado de las burbujas de contratos de la escena 2 (x, y, r, llenado)
const CONTRATOS = [
  [330, 640, 34, 0.85], [470, 400, 26, 0.35], [620, 760, 40, 0.6], [760, 330, 30, 0.95],
  [900, 700, 24, 0.2], [1060, 380, 38, 0.7], [1200, 780, 30, 0.45], [1360, 450, 34, 0.9],
  [1500, 700, 26, 0.55], [1620, 360, 32, 0.3], [1740, 620, 22, 0.75], [1100, 590, 28, 0.5],
];

// Burbujas que rodean la escena de la luz (apagadas hasta que el ojo las ilumina)
const ORBITA = [
  [190, 700, 70, 0.7], [520, 860, 56, 0.4], [880, 930, 44, 0.8], [1330, 900, 62, 0.55],
  [1740, 760, 74, 0.3], [1500, 250, 50, 0.85], [320, 250, 58, 0.6], [1750, 880, 40, 0.5],
];

const CONSEJERIAS = [
  ["sanidad", "Sanidad", 560, 400, 110, 0.82],
  ["educacion", "Educación", 1360, 380, 92, 0.74],
  ["transportes", "Vivienda y Transportes", 440, 760, 84, 0.58],
  ["familia", "Familia y Asuntos Sociales", 1480, 760, 78, 0.69],
  ["cultura", "Cultura y Turismo", 960, 870, 58, 0.5],
];

const DIAPOSITIVAS = [
  // 1. Portada
  {
    id: "portada",
    profundidad: 0,
    ojo: { x: 960, y: 400, escala: 2.4, mira: { x: 960, y: 520 } },
    elementos: [
      { tipo: "texto", x: 960, y: 770, texto: "Ojo Ciudadano", tam: 128, clase: "titulo", paso: 0 },
      { tipo: "texto", x: 960, y: 880, texto: "El gasto público de Madrid, a la vista", tam: 40, clase: "subtitulo", paso: 1 },
    ],
  },

  // 2. Bajamos: un contrato es una burbuja
  {
    id: "contratos",
    profundidad: 0.3,
    ojo: { x: 170, y: 160, escala: 0.8, mira: { x: 900, y: 560 } },
    elementos: [
      ...CONTRATOS.map(([x, y, r, llenado], i) => ({
        tipo: "burbuja", id: `c${i}`, x, y, r, llenado, tono: "agua", paso: 1,
      })),
      { tipo: "texto", x: 960, y: 960, texto: "Cada burbuja es un contrato.", tam: 44, clase: "subtitulo", paso: 2 },
      { tipo: "texto", x: 960, y: 1020, texto: "Cuanto más llena, más se ha gastado.", tam: 30, clase: "nota", paso: 3 },
    ],
  },

  // 3. Se juntan en consejerias y en la Comunidad
  {
    id: "comunidad",
    profundidad: 0.5,
    ojo: { x: 170, y: 160, escala: 0.8, mira: { x: 960, y: 540 } },
    elementos: [
      ...CONSEJERIAS.map(([id, etiqueta, x, y, r, llenado]) => ({
        tipo: "burbuja", id, x, y, r, llenado, etiqueta, tono: "azul", paso: 0,
      })),
      { tipo: "burbuja", id: "cm", x: 960, y: 560, r: 190, llenado: 0.7, etiqueta: "Comunidad de Madrid", valor: `${DATOS.adjudicadoMillones.toLocaleString("es-ES")} M€`, tono: "azul", paso: 1 },
      ...CONSEJERIAS.map(([id]) => ({ tipo: "enlace", de: id, a: "cm", paso: 1 })),
      { tipo: "texto", x: 960, y: 1040, texto: "Adjudicado en contratos, sin IVA. Datos de 2023 a 2026.", tam: 26, clase: "nota", paso: 2 },
    ],
  },

  // 4. Es publico, pero no se ve
  {
    id: "opaco",
    profundidad: 0.7,
    ojo: { x: 170, y: 160, escala: 0.8, mira: { x: 960, y: 540 } },
    elementos: [
      ...CONTRATOS.map(([x, y, r, llenado], i) => ({
        tipo: "burbuja", id: `o${i}`, x, y, r: r * 1.7, llenado, tono: "agua", paso: 0,
      })),
      { tipo: "niebla", paso: 1 },
      { tipo: "cifra", x: 960, y: 400, valor: DATOS.contratosPortal, texto: "contratos públicos", paso: 0 },
      { tipo: "texto", x: 960, y: 700, texto: "Públicos. Pero no accesibles.", tam: 76, clase: "titulo", paso: 1 },
      { tipo: "texto", x: 960, y: 810, texto: "Hay que saber programar para leerlos.", tam: 38, clase: "subtitulo", paso: 2 },
    ],
  },

  // 5. El ojo ilumina
  {
    id: "luz",
    profundidad: 0.55,
    ojo: { x: 960, y: 150, escala: 1.7, mira: { x: 960, y: 700 } },
    elementos: [
      ...ORBITA.map(([x, y, r, llenado], i) => ({
        tipo: "burbuja", id: `l${i}`, x, y, r, llenado, tono: i % 3 === 0 ? "azul" : "agua", paso: 0,
      })),
      { tipo: "luz", paso: 1 },
      { tipo: "texto", x: 960, y: 640, texto: "Ojo Ciudadano lo hace transparente", tam: 76, clase: "titulo", paso: 2 },
      { tipo: "texto", x: 960, y: 750, texto: "Los mismos datos públicos, para cualquiera.", tam: 38, clase: "subtitulo", paso: 3 },
    ],
  },

  // 6. Los modulos
  {
    id: "modulos",
    profundidad: 0.6,
    ojo: { x: 170, y: 160, escala: 0.8, mira: { x: 960, y: 560 } },
    elementos: [
      { tipo: "captura", id: "m1", x: 410, y: 450, r: 190, src: "", etiqueta: "Mapa del dinero", paso: 1 },
      { tipo: "captura", id: "m2", x: 960, y: 700, r: 190, src: "", etiqueta: "Ficha de empresa", paso: 2 },
      { tipo: "captura", id: "m3", x: 1510, y: 450, r: 190, src: "", etiqueta: "Ficha de organismo", paso: 3 },
      { tipo: "texto", x: 960, y: 150, texto: "Todo el dinero, a un vistazo", tam: 60, clase: "titulo", paso: 0 },
    ],
  },

  // 7. Senales y asistente
  {
    id: "senales",
    profundidad: 0.75,
    ojo: { x: 170, y: 160, escala: 0.8, mira: { x: 960, y: 560 } },
    elementos: [
      { tipo: "captura", id: "s1", x: 600, y: 580, r: 230, src: "", etiqueta: "Contratos a revisar", paso: 1 },
      { tipo: "captura", id: "s2", x: 1320, y: 580, r: 230, src: "", etiqueta: "Asistente con citas", paso: 2 },
      { tipo: "texto", x: 960, y: 170, texto: "Señales, no acusaciones", tam: 60, clase: "titulo", paso: 0 },
      { tipo: "texto", x: 960, y: 1000, texto: `${DATOS.indicadores} indicadores de riesgo. Cada cifra enlaza a su fuente oficial.`, tam: 30, clase: "nota", paso: 3 },
    ],
  },

  // 8. Cierre
  {
    id: "cierre",
    profundidad: 0.15,
    ojo: { x: 960, y: 400, escala: 2, mira: { x: 960, y: 560 } },
    elementos: [
      { tipo: "texto", x: 960, y: 740, texto: "Lo público, a la vista de todos", tam: 84, clase: "titulo", paso: 0 },
      { tipo: "texto", x: 960, y: 850, texto: "Ojo Ciudadano", tam: 44, clase: "subtitulo", paso: 1 },
    ],
  },
];
