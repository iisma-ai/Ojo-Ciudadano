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

// Reparto real de 2025 (presupuesto liquidado): id, nombre, x, y, radio (por el dinero), gastado
const REPARTO_2025 = [
  ["san", "Sanidad", 520, 330, 125, 0.992],
  ["edu", "Educación", 1400, 330, 92, 0.992],
  ["deu", "Deuda pública", 1580, 640, 68, 1],
  ["viv", "Vivienda y Transportes", 1250, 860, 67, 0.844],
  ["fam", "Familia y Asuntos Sociales", 660, 860, 58, 0.954],
  ["emp", "Políticas de Empleo", 300, 660, 34, 0.616],
  ["dig", "Digitalización", 960, 900, 29, 0.85],
];

// Los mayores contratos de Sanidad en 2025 en la Plataforma (id, etiqueta, x, y, radio)
const CONTRATOS_SANIDAD = [
  ["ter", "", 310, 330, 30], // terapias respiratorias, 107,4 M€
  ["gri", "", 335, 240, 15], // vacunas de la gripe, 17,2 M€
  ["cli", "", 390, 170, 15], // obras del Hospital Clínico San Carlos, 17,1 M€
  ["vph", "Vacuna VPH", 330, 425, 14], // vacuna del papiloma humano, 14,4 M€
  ["pro", "", 468, 132, 14], // protonterapia en La Paz, 13,7 M€
  ["vrs", "", 395, 490, 13], // vacuna del virus respiratorio sincitial, 12,0 M€
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

  // 6. Sanidad de cerca: el reparto real de 2025, la camara entra en una consejeria y en un contrato
  {
    id: "sanidad",
    profundidad: 0.6,
    ojo: { x: 150, y: 140, escala: 0.7, mira: { x: 700, y: 540 } },
    elementos: [
      ...REPARTO_2025.map(([id, etiqueta, x, y, r, llenado]) => ({
        tipo: "burbuja", id, x, y, r, llenado, etiqueta, tono: "azul", paso: 0,
      })),
      { tipo: "burbuja", id: "cm25", x: 960, y: 540, r: 150, llenado: 0.954, etiqueta: "Comunidad de Madrid · 2025", valor: "33.296 M€", tono: "azul", paso: 0 },
      ...REPARTO_2025.map(([id]) => ({ tipo: "enlace", de: id, a: "cm25", paso: 0 })),
      { tipo: "texto", x: 960, y: 1040, texto: "Presupuesto de 2025 de cada consejería. El líquido es lo gastado.", tam: 26, clase: "nota", paso: 0, hasta: 0 },

      // paso 1: la camara se acerca a Sanidad y sale su ficha
      { tipo: "foco", de: "san", zoom: 1.7, x: 560, y: 540, paso: 1, hasta: 1 },
      {
        tipo: "panel", x: 1130, y: 540, ancho: 680, paso: 1, hasta: 2,
        etiqueta: "Consejería de Sanidad · 2025",
        titulo: "40 de cada 100 € que gastó la Comunidad",
        bloques: [
          { kpis: [["12.935 M€", "disponible"], ["12.833 M€", "gastado"], ["99,2 %", "del disponible"]] },
          { barras: { titulo: "A quién adjudica · Plataforma, sin IVA", filas: [
            ["OXIMESA, S.L.", 66.1, "66,1 M€"],
            ["Air Liquide Healthcare", 41.9, "41,9 M€"],
            ["UTE Clínico San Carlos", 17.1, "17,1 M€"],
            ["Sanofi Aventis", 15.1, "15,1 M€"],
            ["Merck Sharp & Dohme", 14.5, "14,5 M€"],
          ] } },
          { barras: { titulo: "Cómo contrata · 1.290 contratos", filas: [
            ["Abierto simplificado", 482, "482"],
            ["Abierto", 375, "375"],
            ["Negociado sin publicidad", 246, "246"],
            ["Otros", 186, "186"],
          ] } },
        ],
        fuente: "Presupuesto liquidado: Datos abiertos de la Comunidad de Madrid (23-nov-2026). Contratos: Plataforma de Contratación del Sector Público (16-nov-2026), 54 órganos de la consejería.",
      },

      // paso 2: aparecen sus contratos mayores
      { tipo: "foco", de: "san", zoom: 1.45, x: 560, y: 560, paso: 2, hasta: 2 },
      ...CONTRATOS_SANIDAD.map(([id, etiqueta, x, y, r]) => ({
        tipo: "burbuja", id, x, y, r, llenado: 1, etiqueta, tono: "agua", paso: 2,
      })),
      ...CONTRATOS_SANIDAD.map(([id]) => ({ tipo: "enlace", de: "san", a: id, paso: 2 })),

      // paso 3: la camara entra en un contrato y sale su ficha con sus señales
      { tipo: "foco", de: "vph", zoom: 3.4, x: 600, y: 540, paso: 3 },
      {
        tipo: "panel", x: 1080, y: 540, ancho: 700, paso: 3,
        etiqueta: "Contrato · Consejería de Sanidad",
        titulo: "Vacuna del papiloma humano (VPH), 2025-2026",
        bloques: [
          { filas: [
            ["Adjudicado", "14,4 M€ sin IVA"],
            ["Presupuesto de licitación", "14,4 M€ sin IVA"],
            ["Empresa", "Merck Sharp & Dohme de España"],
            ["Cómo se contrató", "Negociado sin publicidad"],
            ["Ofertas recibidas", "1"],
          ] },
          { titulo: "Indicadores de riesgo", senales: [
            ["Sin anuncio público", true, "Adjudicado por procedimiento negociado sin publicidad. La ley lo permite en supuestos concretos; los datos publicados no indican cuál se alegó."],
            ["Una empresa concentra el gasto", false],
            ["Modificaciones de más del 20 %", false],
          ] },
          { texto: "Una señal no demuestra nada irregular: indica dónde merece la pena mirar, y cada una enlaza al expediente oficial." },
        ],
        fuente: "Plataforma de Contratación del Sector Público, expediente placsp:17910499 (16-nov-2026).",
      },
    ],
  },

  // 7. Señales de cada 100
  {
    id: "senales",
    profundidad: 0.7,
    ojo: { x: 150, y: 140, escala: 0.7, mira: { x: 960, y: 560 } },
    elementos: [
      ...CONTRATOS.map(([x, y, r, llenado], i) => ({
        tipo: "burbuja", id: `s${i}`, x, y: y + 40, r: r * 0.8, llenado, tono: i % 3 ? "agua" : "ambar", paso: 0,
      })),
      { tipo: "texto", x: 960, y: 140, texto: "Señales, no acusaciones", tam: 64, clase: "titulo", paso: 0 },
      {
        tipo: "panel", x: 560, y: 590, ancho: 800, paso: 1,
        etiqueta: "Indicadores de riesgo · 2023 a 2026",
        bloques: [
          { puntos: { valor: 39, texto: "de cada 100 licitaciones recibieron una sola oferta" } },
          { puntos: { valor: 31, texto: "de cada 100 contratos se adjudicaron sin anuncio público" } },
          { puntos: { valor: 17, texto: "de cada 100 contratos menores, con posible fraccionamiento" } },
          { texto: "Cada contrato con señal explica por qué la tiene y enlaza a su expediente. Puede haber razones legítimas: mercados con pocas empresas, urgencias o requisitos técnicos." },
        ],
        fuente: "Indicadores R-01, R-02 y R-03 sobre la Plataforma de Contratación y el portal de la Comunidad de Madrid (noviembre de 2026).",
      },
    ],
  },

  // 8. El asistente: preguntar, relacionar y comparar, con fuentes
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
        pregunta: "¿Qué porcentaje de licitaciones tuvo un único licitador cada año?",
        respuesta: [
          { texto: "Licitaciones que recibieron una sola oferta (señal R-01):" },
          { barras: { titulo: "Por año", max: 100, filas: [
            ["2023", 43.3, "43,3 %"], ["2024", 44.0, "44,0 %"], ["2025", 42.2, "42,2 %"], ["2026", 41.5, "41,5 %"],
          ] } },
          { texto: "Como referencia, en 2025 el 45,5 % de los lotes de las comunidades autónomas recibió una sola oferta. Se cuentan de otra manera: sirve como orden de magnitud." },
          { chips: ["Indicador R-01 · Plataforma y portal regional", "OIReScon · Informe Anual de Supervisión 2026", "Comisión Europea · Single Market Scoreboard"] },
        ],
      },
      {
        tipo: "chat", x: 700, y: 540, ancho: 960, paso: 2,
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
    ],
  },

  // 9. Los modulos (capturas de la aplicacion)
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

  // 10. Cierre
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
