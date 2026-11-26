/* CONTENIDO DE LA PRESENTACION PARA EL JURADO (jurado.html)
 *
 * Para leer sin quien presente, con mas texto que la de la exposicion (index.html). Usa el mismo
 * motor (escena3d.js) y los mismos tipos de elemento, explicados al principio de diapositivas.js.
 * Escenario de 1920 x 1080. Cada diapositiva aparece entera de una vez (un solo paso). Las bases
 * piden tres diapositivas como maximo; la cuarta (la captura de la web) la pidio Isma.
 *
 *   1. En la roca, sobre el mar: el ojo, el nombre del proyecto, los integrantes y la propuesta.
 *   2. Salto al agua: el ojo ilumina el mar; el problema y los datos, con enlaces, a la vez.
 *   3. Mas abajo: que hacemos con los datos (señales, aprendizaje automatico y agente) y
 *      utilidad, impacto y viabilidad, a la vez.
 *   4. El ojo nos lleva a ver la web: una captura, el enlace y el QR.
 *
 * Cifras de la base de datos (16-nov-2026; subvenciones, 24-nov) y del README del proyecto.
 */

// Logo de Ojo Ciudadano (lo usa el motor en el QR)
const LOGO_OJO = "../src/ojo_ciudadano/app/static/logo-horizontal.svg";

const WEB = "https://ojo-ciudadano.iismael.workers.dev/";
const REPOSITORIO = "https://github.com/iisma-ai/Ojo-Ciudadano";
const CATALOGO = "https://datos.comunidad.madrid";
const DATASET = `${CATALOGO}/dataset/`;

// Conjuntos del Catalogo de Datos Abiertos de la Comunidad de Madrid que usa la plataforma
// (ingesta/cm_abiertos.py): nombre visible e identificador del conjunto en el catalogo
const CONJUNTOS_CATALOGO = [
  ["Presupuestos liquidados de gastos, por órgano y fase de ejecución", "presupuestos_liquidados_gastos_consolidados_por_organo_y_fase_ejecucion"],
  ["Presupuestos liquidados de ingresos, por capítulo", "presupuestos_liquidados_ingresos_consolidados_por_capitulo_y_fase_ejecucion"],
  ["Presupuestos iniciales de gastos, por sección y capítulo", "presupuestos_generales_iniciales_gastos_consolidados_por_seccion_y_capitulo"],
  ["Contratos administrativos por tipo (estadística de la Junta Consultiva)", "1914620"],
  ["Ayudas del presupuesto de la Unión Europea", "1902617"],
  ["Recursos del sistema de financiación autonómica", "1902613"],
  ["Registro de transparencia", "registro_transparencia"],
  ["Personal de la Comunidad de Madrid, por área de actividad", "personal_comunidad_madrid_por_area_actividad_y_sexo"],
];

// Fuentes de contratos y subvenciones registro a registro (el catalogo no los tiene)
const FUENTES_REGISTRO = [
  ["Portal de la Contratación Pública de la Comunidad de Madrid", "https://contratos-publicos.comunidad.madrid/contratos"],
  ["Plataforma de Contratación del Sector Público", "https://www.hacienda.gob.es/es-ES/GobiernoAbierto/Datos%20Abiertos/Paginas/LicitacionesAgregacion.aspx"],
  ["Base de Datos Nacional de Subvenciones", "https://www.infosubvenciones.es/bdnstrans/GE/es/index"],
  ["Tribunal Administrativo de Contratación Pública", "https://www.comunidad.madrid/tacp/busquedaresoluciones"],
  ["Portal de Transparencia: convenios", "https://www.comunidad.madrid/transparencia/convenios"],
];

const enlace = (url, html) => `<a href="${url}" target="_blank" rel="noopener">${html}</a>`;
const sinProtocolo = (url) => url.replace(/^https?:\/\//, "").replace(/\/$/, "");

// Burbujas de datos que el ojo descubre al aclarar el mar (diapositiva 2): x, y, r, llenado, etiqueta
const BURBUJAS_DATOS = [
  [250, 150, 44, 0.8, "Contratos"],
  [560, 120, 34, 0.55, "Subvenciones"],
  [1360, 120, 38, 0.9, "Presupuestos"],
  [1670, 150, 30, 0.45, "Registros"],
  [120, 960, 26, 0.6, ""], [470, 1010, 20, 0.35, ""], [960, 1000, 30, 0.7, ""],
  [1450, 1010, 22, 0.5, ""], [1800, 950, 28, 0.85, ""], [70, 520, 22, 0.4, ""], [1870, 560, 24, 0.65, ""],
];

// Muchas burbujas en el fondo (diapositiva 3): el dinero ya ordenado; las ambar, las señales
const FONDO = (() => {
  let s = 11;
  const azar = () => ((s = (s * 16807) % 2147483647) / 2147483647);
  return Array.from({ length: 44 }, () => [60 + azar() * 1800, 60 + azar() * 960, 8 + azar() * 20, azar()]);
})();

// Burbujas alrededor de la captura de la web (diapositiva 4): x, y, r, llenado
const MARCO_WEB = [
  [60, 140, 30, 0.6], [330, 90, 22, 0.4], [880, 80, 26, 0.75], [1240, 120, 20, 0.5],
  [90, 1000, 24, 0.7], [520, 1030, 18, 0.45], [1000, 1010, 26, 0.8], [1860, 980, 30, 0.55], [1880, 330, 22, 0.35],
];

const DIAPOSITIVAS = [
  // 1. En la roca, sobre el mar: el ojo, el proyecto, los integrantes y la propuesta
  {
    id: "orilla",
    arriba: true,
    profundidad: 0,
    ojo: { x: 960, y: 250, escala: 1.15, mira: { x: 960, y: 700 } },
    elementos: [
      { tipo: "vista", pos: [0, 12.9, 15.5], mira: [0, 9.6, -40], paso: 0 },
      {
        tipo: "panel", clase: "portada", x: 360, y: 640, ancho: 1200, tam: 24, paso: 0,
        etiqueta: "DataMad 2026 · Hackathon de Datos Abiertos de la Comunidad de Madrid",
        titulo: "Ojo Ciudadano",
        bloques: [
          { texto: "Para que cualquier ciudadano pueda consultar y ver a dónde va su dinero: de cada organismo de la Comunidad de Madrid a cada empresa y cada beneficiario, con cada cifra enlazada a su fuente oficial." },
          { texto: "Une contratos y subvenciones, señala dónde hay más riesgo y menos transparencia, y responde preguntas en lenguaje natural." },
          { texto: '<span class="integrantes"><span>Ismael El Harrak</span><span>Ignacio Vallejo Garach</span></span>' },
        ],
      },
    ],
  },

  // 2. Salto al agua: el ojo ilumina el mar y se ven a la vez el problema y los datos
  {
    id: "problema",
    profundidad: 0.45,
    ojo: { x: 960, y: 170, escala: 0.8, mira: { x: 960, y: 620 } },
    elementos: [
      { tipo: "luz", paso: 0 },
      ...BURBUJAS_DATOS.map(([x, y, r, llenado, etiqueta], i) => ({
        tipo: "burbuja", id: `d${i}`, x, y, r, llenado, etiqueta, tono: i % 3 ? "agua" : "azul", paso: 0,
      })),
      {
        tipo: "panel", clase: "lectura", x: 90, y: 600, ancho: 820, tam: 21, paso: 0,
        etiqueta: "El problema",
        titulo: "El gasto es público, pero no se ve",
        bloques: [
          { texto: "La Comunidad de Madrid publica sus contratos, subvenciones y presupuestos, pero en <b>portales distintos</b>, con <b>formatos distintos</b> y <b>sin un identificador común</b>. Datos clave, como cuántas empresas se presentaron a un concurso, solo aparecen en documentos PDF." },
          { texto: "Saber qué empresas reciben más dinero de una consejería, o si contrata casi siempre con las mismas, hoy exige descargar ficheros de varios portales, unirlos a mano y dominar la jerga de la contratación pública." },
          { senales: [
            ["Ver a dónde va el dinero, de cada organismo a cada empresa", true],
            ["Saber dónde mirar primero, sin acusar a nadie", true],
            ["Preguntar con sus palabras y comprobar la fuente", true],
          ], titulo: "Lo que necesita la ciudadanía" },
        ],
      },
      // los datos que usamos, con sus enlaces; primero el catalogo de datos abiertos
      {
        tipo: "panel", clase: "lectura", x: 990, y: 590, ancho: 840, tam: 17, paso: 0,
        etiqueta: "Los datos",
        titulo: "Catálogo de Datos Abiertos de la Comunidad de Madrid",
        bloques: [
          { texto: CONJUNTOS_CATALOGO.map(([nombre, id]) =>
            enlace(DATASET + id, `<span class="dato"><b>${nombre}</b><span>datos.comunidad.madrid/dataset/${id}</span></span>`)).join("") },
          { texto: `Y el ${enlace(CATALOGO, "<b>catálogo completo</b>")}: el asistente busca en sus 2.276 conjuntos de datos para responder.` },
          { texto: "<b>Contratos y subvenciones, registro a registro</b> (el catálogo los publica solo agregados):" },
          { chips: FUENTES_REGISTRO.map(([nombre, url]) => enlace(url, nombre)) },
        ],
      },
    ],
  },

  // 3. Mas abajo: que hacemos con los datos y para que sirve, todo a la vez
  {
    id: "resultados",
    profundidad: 0.8,
    ojo: { x: 960, y: 120, escala: 0.6, mira: { x: 960, y: 600 } },
    elementos: [
      ...FONDO.map(([x, y, r, llenado], i) => ({
        tipo: "burbuja", id: `f${i}`, x, y, r, llenado, tono: i % 5 === 0 ? "ambar" : i % 3 ? "agua" : "azul", paso: 0,
      })),
      {
        tipo: "panel", clase: "lectura", x: 90, y: 590, ancho: 860, tam: 20, paso: 0,
        etiqueta: "Los resultados",
        titulo: "Qué hacemos con los datos",
        bloques: [
          { kpis: [["1.354.441", "contratos"], ["872.821", "subvenciones"], ["132", "organismos"]] },
          { texto: "Unimos las licitaciones de la Plataforma de Contratación, las del portal regional y los contratos menores; quitamos duplicados, normalizamos los NIF y relacionamos a cada organismo con sus empresas, sus subvenciones, su presupuesto y los registros del catálogo." },
          { senales: [
            ["Señales de riesgo", true, "Seis indicadores con metodología abierta comparan cada contrato con otros parecidos y señalan dónde mirar primero."],
            ["Aprendizaje automático", true, "Un modelo no supervisado (Isolation Forest) destaca los contratos más atípicos frente a sus pares."],
            ["El agente de Ojo Ciudadano", true, "Responde en lenguaje natural, consulta los datos en modo de solo lectura y cita la fuente oficial de cada cifra."],
          ], titulo: "Del dato a la respuesta" },
          { texto: "<b>No son acusaciones:</b> indican dónde mirar, siempre con el enlace al expediente oficial." },
        ],
      },
      {
        tipo: "panel", clase: "lectura", x: 1030, y: 590, ancho: 800, tam: 20, paso: 0,
        etiqueta: "Para qué sirve",
        titulo: "Utilidad, impacto y viabilidad",
        bloques: [
          { texto: "<b>Utilidad.</b> Periodistas de datos, ONG, órganos de control como la Cámara de Cuentas, la propia Administración, las empresas y cualquier ciudadano ven en minutos lo que hoy exige días de descargas y cruces." },
          { texto: "<b>Impacto.</b> Más control ciudadano del gasto, con metodología abierta: señala dónde hay más riesgo y menos transparencia, sin acusar a nadie, y siempre con el enlace al documento oficial." },
          { texto: "<b>Viabilidad.</b> Solo usa datos públicos y reutilizables, y el código es abierto (licencia MIT). Se despliega con pocos recursos: un servidor con Docker y una red de distribución gratuita. Como la Plataforma de Contratación reúne también a otras administraciones, el método se puede extender a ellas." },
        ],
      },
    ],
  },

  // 4. El ojo nos acompaña a ver la web: una captura, el enlace y el QR
  {
    id: "web",
    profundidad: 0.55,
    ojo: { x: 1560, y: 130, escala: 0.7, mira: { x: 640, y: 560 } },
    elementos: [
      ...MARCO_WEB.map(([x, y, r, llenado], i) => ({
        tipo: "burbuja", id: `w${i}`, x, y, r, llenado, tono: i % 2 ? "agua" : "azul", paso: 0,
      })),
      {
        tipo: "panel", clase: "captura-web", x: 70, y: 560, ancho: 1180, tam: 20, paso: 0,
        etiqueta: "Así se ve Ojo Ciudadano",
        bloques: [{ texto: enlace(WEB, '<img src="capturas/web-inicio.jpg" alt="Página de inicio de Ojo Ciudadano">') }],
      },
      {
        tipo: "qr", x: 1350, y: 580, ancho: 460, url: WEB, paso: 0,
        texto: `${enlace(WEB, "Pruébalo tú")}<small>${enlace(WEB, sinProtocolo(WEB))}</small><small>${enlace(REPOSITORIO, `Código: ${sinProtocolo(REPOSITORIO)}`)}</small>`,
      },
    ],
  },
];
