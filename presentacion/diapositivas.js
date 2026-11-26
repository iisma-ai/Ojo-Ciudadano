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
 *   {tipo:"cifra",   x, y, valor, formato, texto, tam, clase, paso}  numero que sube hasta `valor`
 *                    clase "resalte": numero en ambar, el color de las señales
 *   {tipo:"burbuja", id, x, y, r, llenado, etiqueta, valor, tono, paso}
 *                    llenado 0..1 = lo gastado; tono: "azul" | "ambar" | "agua"
 *   {tipo:"enlace",  de, a, paso}                                 linea de agua entre dos burbujas
 *   {tipo:"captura", id, x, y, r, src, etiqueta, paso}           burbuja con una imagen o video dentro
 *   {tipo:"niebla",  fuerza, paso, hasta}                         capa turbia (lo que no se ve); fuerza 0..1
 *                    (por defecto 1; con menos, solo apaga el fondo para que se lean los textos)
 *   {tipo:"luz",     paso}                                        el ojo ilumina la escena
 *   {tipo:"foco",    de, zoom, x, y, paso, hasta}                 la camara se acerca a la burbuja `de`
 *                    y la deja en (x, y) de la pantalla; `hasta` = ultimo paso en que dura
 *   {tipo:"panel",   x, y, ancho, etiqueta, titulo, bloques, fuente, paso, hasta}
 *                    panel de cristal fijo en pantalla (x = borde izquierdo, y = centro). Bloques:
 *                    {kpis:[[valor, texto]]} {barras:{titulo, filas:[[nombre, valor, texto]], max}}
 *                    {medidor:{titulo, valor 0..1, izq, der}} {puntos:{valor, texto}} (de cada 100)
 *                    {senales:[[nombre, activa, texto]], titulo} {filas:[[nombre, valor]]}
 *                    {chips:[...]} {texto}
 *   {tipo:"chat",    x, y, ancho, pregunta, respuesta:[bloques], paso, hasta}
 *                    el asistente escribe la pregunta, piensa y contesta con esos bloques
 *   {tipo:"vista",   pos:[x,y,z], mira:[x,y,z], paso, hasta}       camara libre (escena fuera del agua)
 *   {tipo:"qr",      x, y, ancho, url, texto, paso}                codigo QR en un panel de cristal
 *   {tipo:"imagen",  x, y, ancho, src, paso}                       imagen fija en pantalla
 *   En una burbuja, `logo` (url de un svg) y `color` ponen un logo dentro.
 *
 * En la diapositiva: `arriba: true` = fuera del agua (cielo, mar visto desde arriba y rocas);
 * `ojo: null` = sin ojo.
 */

// Cifras reales de la base de datos (23-nov-2026). Cambialas aqui si se regenera.
const DATOS = {
  contratosPortal: 1354441, // contratos del portal de la Comunidad
  adjudicadoMillones: 22857, // adjudicado en la Plataforma de Contratacion, sin IVA
  subvenciones: 872821, // concesiones de subvenciones (BDNS), de ene-2023 a nov-2026 (base del 24-nov)
  organismos: 132,
  indicadores: 6,
  urlApp: "https://ojo-ciudadano.iismael.workers.dev/", // direccion publica de la web para el QR de la escena 8 (vacia: sale un hueco)
};

// Muchas burbujas pequeñas para la escena del millon de contratos (siempre las mismas)
const ENJAMBRE = (() => {
  let s = 7;
  const azar = () => ((s = (s * 16807) % 2147483647) / 2147483647);
  return Array.from({ length: 70 }, () => [80 + azar() * 1760, 80 + azar() * 920, 8 + azar() * 22, azar()]);
})();

// Logo de Ojo Ciudadano (el de la web)
const LOGO_OJO = "../src/ojo_ciudadano/app/static/logo-horizontal.svg";

// Tecnologias de Ojo Ciudadano con su logo real: nombre, logo y color para teñir los de un color.
// Devicon (a color) y Simple Icons (de un color), servidos por jsDelivr en versiones fijas.
const DEVICON = "https://cdn.jsdelivr.net/gh/devicons/devicon@v2.16.0/icons";
const SIMPLE = "https://cdn.jsdelivr.net/npm/simple-icons@13.0.0/icons";
const TECNOLOGIAS = [
  ["Python", `${DEVICON}/python/python-original.svg`, null],
  ["DuckDB", `${SIMPLE}/duckdb.svg`, "#FFF000"],
  ["Polars", `${SIMPLE}/polars.svg`, "#7FB3FF"],
  ["Streamlit", `${DEVICON}/streamlit/streamlit-original.svg`, null],
  ["Plotly", `${DEVICON}/plotly/plotly-original.svg`, null],
  ["scikit-learn", `${DEVICON}/scikitlearn/scikitlearn-original.svg`, null],
  ["GPT · OpenRouter", `${SIMPLE}/openai.svg`, "#FFFFFF"],
  ["Claude · OpenRouter", `${SIMPLE}/anthropic.svg`, "#E3A57E"],
  ["Three.js", `${DEVICON}/threejs/threejs-original.svg`, "#FFFFFF"],
].map(([nombre, logo, color], i, todas) => {
  const a = -Math.PI / 2 + (2 * Math.PI * i) / todas.length;
  return { nombre, logo, color, x: 960 + Math.cos(a) * 560, y: 545 + Math.sin(a) * 360 };
});

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

// De donde viene el dinero en 2025: los tres capitulos de ingresos que mas aportan (ingresos
// consolidados liquidados, derechos reconocidos; catalogo de datos abiertos, serie
// presupuestos_liquidados_ingresos_consolidados_por_capitulo_y_fase_ejecucion, 23-nov).
// «De cada 100 €» sobre lo que entra antes de restar el saldo con el sistema de financiacion,
// como en la web (app/de_donde_viene.py): directos 18.714 M€, indirectos 15.063 M€,
// prestamos 3.445 M€. id, nombre, x, y, radio, llenado (entrado / previsto)
const INGRESOS_2025 = [
  ["dir", "Impuestos directos · 49 de cada 100 €", 560, 120, 80, 1],
  ["ind", "Impuestos indirectos · 39 de cada 100 €", 1360, 120, 72, 1],
  ["pre", "Préstamos · 9 de cada 100 €", 960, 95, 34, 0.93],
];

// A donde va: reparto real de 2025 (presupuesto liquidado), solo las cuatro mayores
// id, nombre, x, y, radio (por el dinero), gastado
const REPARTO_2025 = [
  ["san", "Sanidad", 460, 840, 115, 0.992],
  ["viv", "Vivienda y Transportes", 830, 910, 62, 0.844],
  ["edu", "Educación", 1220, 880, 88, 0.992],
  ["deu", "Deuda pública", 1560, 845, 66, 1],
];

// En que se gasta Sanidad en 2025: ejemplos sueltos de licitaciones, un contrato menor y una
// subvencion, con nombre corto (se explican de palabra). En arco a la izquierda de Sanidad.
// id, etiqueta, x, y, radio
const CONTRATOS_SANIDAD = [
  ["pro", "Protonterapia", 420, 613, 14], // licitacion: protonterapia en La Paz, 13,7 M€ sin IVA
  ["cli", "Obras Clínico", 312, 664, 15], // licitacion: obras del Hospital Clinico San Carlos, 17,1 M€
  ["gri", "Vacuna gripe", 244, 761, 15], // licitacion: vacunas de la gripe, 17,2 M€
  ["ter", "Terapias respiratorias", 233, 880, 30], // licitacion: terapias respiratorias, 107,4 M€
  // contrato menor: cafe del Hospital Universitario La Paz, 2.860 € con IVA (23-ene-2025);
  // Sanidad firmo 330.085 menores en 2025 (portal de contratacion de la Comunidad)
  ["caf", "Café", 284, 988, 8],
  // subvencion: AECC, cuidados paliativos 2025, 0,6 M€ (BDNS)
  ["pal", "Cuidados paliativos", 381, 1056, 11],
];

const DIAPOSITIVAS = [
  // 1. Fuera del agua, sin ojo: las rocas desde las que se salta (Ignacio cuenta la historia)
  {
    id: "rocas",
    arriba: true,
    profundidad: 0,
    ojo: null,
    elementos: [
      { tipo: "vista", pos: [0, 12.9, 15.5], mira: [0, 9.6, -40], paso: 0, hasta: 0 },
      // paso 1: asomarse al borde y mirar el agua: no se ve lo que hay debajo
      { tipo: "vista", pos: [0, 12.6, 10.4], mira: [0, 7.2, 0], paso: 1 },
    ],
  },

  // 2. Bajo el agua: oscuro, las rocas estan pero no se ven
  {
    id: "oscuro",
    profundidad: 0.75,
    ojo: null,
    elementos: [
      { tipo: "niebla", paso: 0 },
      { tipo: "texto", x: 960, y: 540, texto: "Públicos. Pero no accesibles.", tam: 76, clase: "titulo", paso: 1 },
    ],
  },

  // 3. Aparece el ojo: Ojo Ciudadano ilumina lo que estaba oculto
  {
    id: "ojo",
    profundidad: 0.5,
    ojo: { x: 960, y: 380, escala: 2.2, mira: { x: 960, y: 560 } },
    elementos: [
      ...ORBITA.map(([x, y, r, llenado], i) => ({
        tipo: "burbuja", id: `l${i}`, x, y, r, llenado, tono: i % 3 === 0 ? "azul" : "agua", paso: 0,
      })),
      { tipo: "imagen", x: 620, y: 770, ancho: 680, src: LOGO_OJO, paso: 0 },
      { tipo: "texto", x: 960, y: 880, texto: "El gasto público de Madrid, a la vista", tam: 40, clase: "subtitulo", paso: 1 },
      { tipo: "luz", paso: 2 },
    ],
  },

  // 4. El mapa: el reparto de 2025, una consejería y un contrato: el reparto real de 2025, la camara entra en una consejeria y en un contrato
  {
    id: "sanidad",
    profundidad: 0.6,
    ojo: { x: 150, y: 140, escala: 0.7, mira: { x: 700, y: 540 } },
    elementos: [
      // paso 0: de donde viene; el dinero baja de los ingresos a la Comunidad
      ...INGRESOS_2025.map(([id, etiqueta, x, y, r, llenado]) => ({
        tipo: "burbuja", id, x, y, r, llenado, etiqueta, tono: "agua", paso: 0,
      })),
      { tipo: "burbuja", id: "cm25", x: 960, y: 470, r: 170, llenado: 0.954, etiqueta: "Comunidad de Madrid · 2025", valor: "33.296 M€", tono: "azul", paso: 0 },
      ...INGRESOS_2025.map(([id]) => ({ tipo: "enlace", de: id, a: "cm25", paso: 0 })),

      // paso 1: a donde va; el dinero sale de la Comunidad hacia las consejerias
      ...REPARTO_2025.map(([id, etiqueta, x, y, r, llenado]) => ({
        tipo: "burbuja", id, x, y, r, llenado, etiqueta, tono: "azul", paso: 1,
      })),
      ...REPARTO_2025.map(([id]) => ({ tipo: "enlace", de: "cm25", a: id, paso: 1 })),

      // paso 2: la camara se acerca a Sanidad y sale su ficha
      { tipo: "foco", de: "san", zoom: 1.7, x: 560, y: 540, paso: 2, hasta: 2 },
      {
        tipo: "panel", x: 1080, y: 310, ancho: 700, paso: 2, hasta: 3,
        tam: 28,
        etiqueta: "Sanidad · 2025",
        titulo: "40 de cada 100 € que gastó la Comunidad",
        bloques: [
          { kpis: [["12.833 M€", "gastados"], ["1.290", "contratos"]] },
        ],
      },

      // paso 3: aparecen sus contratos mayores
      { tipo: "foco", de: "san", zoom: 1.45, x: 560, y: 560, paso: 3, hasta: 3 },
      ...CONTRATOS_SANIDAD.map(([id, etiqueta, x, y, r]) => ({
        tipo: "burbuja", id, x, y, r, llenado: 1, etiqueta, tono: "agua", paso: 3,
      })),
      ...CONTRATOS_SANIDAD.map(([id]) => ({ tipo: "enlace", de: "san", a: id, paso: 3 })),
    ],
  },


  // 5. Mas de un millon de contratos: abruma
  {
    id: "millon",
    profundidad: 0.65,
    ojo: { x: 150, y: 140, escala: 0.7, mira: { x: 960, y: 540 } },
    elementos: [
      ...ENJAMBRE.map(([x, y, r, llenado], i) => ({
        tipo: "burbuja", id: `e${i}`, x, y, r, llenado, tono: i % 4 ? "agua" : "azul", paso: 0,
      })),
      { tipo: "cifra", x: 960, y: 430, valor: DATOS.contratosPortal, texto: "contratos públicos", paso: 1 },
      { tipo: "cifra", x: 960, y: 740, valor: DATOS.subvenciones, texto: "subvenciones", tam: 24, paso: 1 },
    ],
  },

  // 6. Señales de cada 100 y contratos atípicos
  {
    id: "senales",
    profundidad: 0.7,
    ojo: { x: 150, y: 140, escala: 0.7, mira: { x: 960, y: 560 } },
    elementos: [
      ...CONTRATOS.map(([x, y, r, llenado], i) => ({
        tipo: "burbuja", id: `s${i}`, x, y: y + 40, r: r * 0.8, llenado, tono: i % 3 ? "agua" : "ambar", paso: 0,
      })),
      // paso 0: solo las burbujas, sin texto
      // paso 1: «6 señales» y tres cifras grandes, una idea cada una; el fondo se apaga un poco para que se lean
      { tipo: "texto", x: 960, y: 220, texto: "6 señales", tam: 64, clase: "titulo", paso: 1, hasta: 1 },
      { tipo: "niebla", fuerza: 0.45, paso: 1, hasta: 1 },
      ...[[480, 39, "Una sola oferta"], [960, 31, "Sin anuncio público"], [1440, 17, "Posible fraccionamiento"]].flatMap(([x, valor, texto]) => [
        { tipo: "cifra", x, y: 500, valor, texto: "de cada 100", tam: 34, clase: "resalte", paso: 1, hasta: 1 },
        { tipo: "texto", x, y: 690, texto, tam: 36, clase: "subtitulo resalte", paso: 1, hasta: 1 },
      ]),
      // paso 2: un contrato que se separa de los de su grupo (buscador de atipicos)
      { tipo: "burbuja", id: "atipico", x: 1700, y: 250, r: 34, llenado: 0.9, etiqueta: "Atípico", tono: "ambar", paso: 2 },
      { tipo: "foco", de: "atipico", zoom: 1.6, x: 1250, y: 420, paso: 2, hasta: 2 },
      {
        // x es el borde izquierdo del panel: acaba a la izquierda del atipico (en pantalla, x 1250)
        tipo: "panel", x: 620, y: 420, ancho: 540, paso: 2, hasta: 2,
        tam: 32,
        bloques: [
          // puntos ambar luminosos (senal activa); titulo vacio: sin cabecera «Señales»
          { senales: [
            ["Aprende de las cifras", true],
            ["Destaca lo que se sale de lo habitual", true],
          ], titulo: "" },
        ],
      },
      // paso 3: resumen; señales a un lado, atípicos al otro y debajo que no son acusaciones
      { tipo: "niebla", fuerza: 0.45, paso: 3 },
      { tipo: "texto", x: 560, y: 470, texto: "Señales", tam: 72, clase: "titulo", paso: 3 },
      { tipo: "texto", x: 1360, y: 470, texto: "Atípicos", tam: 72, clase: "titulo", paso: 3 },
      { tipo: "texto", x: 960, y: 720, texto: "No son acusaciones", tam: 44, clase: "subtitulo", paso: 3 },
    ],
  },

  // 7. El asistente: preguntar, relacionar y comparar, con fuentes
  {
    id: "asistente",
    profundidad: 0.78,
    ojo: { x: 360, y: 540, escala: 1.25, mira: { x: 1100, y: 500 } },
    elementos: [
      ...ORBITA.map(([x, y, r, llenado], i) => ({
        tipo: "burbuja", id: `a${i}`, x, y, r: r * 0.7, llenado, tono: "azul", paso: 0,
      })),
      {
        tipo: "chat", x: 700, y: 540, ancho: 960, paso: 1, hasta: 1,
        pregunta: "¿Qué organismos adjudicaron más importe en la Plataforma de Contratación en 2025?",
        respuesta: [
          { barras: { titulo: "Millones de euros sin IVA · 2025", filas: [
            ["Consejería de Familia, Juventud y Asuntos Sociales", 594.3, "594,3"],
            ["Metro de Madrid", 451.8, "451,8"],
            ["Canal de Isabel II", 432.6, "432,6"],
            ["Consejería de Presidencia, Justicia y Adm. Local", 234.0, "234,0"],
            ["Agencia de Contratación Sanitaria", 203.3, "203,3"],
          ] } },
          { texto: "El año es el de formalización. Solo incluye la Plataforma, con importes sin IVA." },
          { chips: ["Plataforma de Contratación del Sector Público · 16-nov-2026"] },
        ],
      },
      {
        tipo: "chat", x: 700, y: 540, ancho: 960, paso: 2, hasta: 2,
        pregunta: "¿Qué proporción de los recursos ante el Tribunal de Contratación Pública se estima, según el acto recurrido?",
        respuesta: [
          { tarta: { titulo: "Resoluciones del Tribunal por acto recurrido", centro: ["1.104", "resoluciones"], filas: [
            ["Adjudicación", 452, "452 · 24,8 % estimadas", "#3d8bfd"],
            ["Exclusión", 389, "389 · 18,3 % estimadas", "#7db3ff"],
            ["Pliegos", 209, "209 · 30,6 % estimadas", "#1f5fd6"],
            ["Otros actos", 54, "54 · 14,8 % estimadas", "#f2b544"],
          ] } },
          { texto: "Presentar un recurso no es una señal. Que se estime significa que el Tribunal dio la razón a quien recurrió ese acto; no implica una conducta reprochable de la empresa adjudicataria." },
          { chips: ["Tribunal Administrativo de Contratación Pública de la Comunidad de Madrid · 23-nov-2026"] },
        ],
      },
      {
        tipo: "chat", x: 700, y: 540, ancho: 960, paso: 3,
        // pregunta de alguien que no sabe nada del tema; cifras de la busqueda por palabras
        // en los titulos (asistente/texto.py, «helicoptero», base del 16-nov)
        pregunta: "Oye, ¿es verdad que la Comunidad de Madrid tiene helicópteros?",
        respuesta: [
          { texto: "Sí. Hay 12 contratos que hablan de helicópteros: los usan los servicios de emergencia para rescates, para apagar incendios y para la asistencia sanitaria del SUMMA 112." },
          { kpis: [["52,8 M€", "4 licitaciones · sin IVA"], ["2,6 M€", "8 contratos · con IVA"]] },
          { texto: "Son servicios de helicóptero y lo que necesitan, como la base de Las Rozas. Las dos cifras no se suman: una va sin IVA y la otra con IVA." },
          { chips: ["Plataforma de Contratación del Sector Público · 16-nov-2026", "Portal de la Contratación Pública de la Comunidad de Madrid · 16-nov-2026"] },
        ],
      },
    ],
  },

  // 8. Ya esta en marcha: el QR para entrar
  {
    id: "en-marcha",
    profundidad: 0.55,
    ojo: { x: 560, y: 540, escala: 1.6, mira: { x: 1300, y: 540 } },
    elementos: [
      ...ORBITA.map(([x, y, r, llenado], i) => ({
        tipo: "burbuja", id: `q${i}`, x, y, r: r * 0.8, llenado, tono: "azul", paso: 0,
      })),
      { tipo: "qr", x: 1100, y: 540, ancho: 420, url: DATOS.urlApp, texto: "Pruébalo", paso: 1 },
    ],
  },

  // 9. Con qué está hecho
  {
    id: "tecnologias",
    profundidad: 0.45,
    ojo: { x: 960, y: 540, escala: 1.2, mira: { x: 960, y: 600 } },
    elementos: TECNOLOGIAS.map(({ nombre, logo, color, x, y }, i) => ({
      tipo: "burbuja", id: `t${i}`, x, y, r: 68, llenado: 0.18, etiqueta: nombre, logo, color, tono: "azul", paso: 0,
    })),
  },

  // 10. Cierre
  {
    id: "cierre",
    profundidad: 0.15,
    ojo: { x: 960, y: 400, escala: 2, mira: { x: 960, y: 560 } },
    elementos: [
      { tipo: "texto", x: 960, y: 740, texto: "Ojo, ciudadano", tam: 84, clase: "titulo", paso: 0 },
      { tipo: "imagen", x: 790, y: 870, ancho: 340, src: LOGO_OJO, paso: 1 },
    ],
  },
];
