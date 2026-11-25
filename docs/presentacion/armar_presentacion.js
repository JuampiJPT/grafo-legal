// Presentación para el coloquio (examen final oral) del TP Integrador, Problemática III (bitácora B71).
// Se arma con pptxgenjs a partir del contenido del video explicativo y del informe de avance.
// Todas las cifras salen de results/ y del informe; las figuras, de docs/informe_avance/figuras/.
// Uso (desde la raíz del repo): APPLY_THEME=<ruta a apply_theme.js> node docs/presentacion/armar_presentacion.js
//   -> docs/presentacion/presentacion_coloquio.pptx. Requiere pptxgenjs (npm install pptxgenjs).
const pptxgen = require("pptxgenjs");
const path = require("path");
// apply_theme.js escribe la paleta en el tema del .pptx (pptxgenjs no puede). Viene con las herramientas de
// Claude; su ruta se pasa en APPLY_THEME. Sin él, el deck se arma igual pero con la paleta de Office.
let applyTheme = null;
try { applyTheme = require(process.env.APPLY_THEME || "./apply_theme.js").applyTheme; } catch (e) {
  console.warn("sin apply_theme.js: los colores del tema quedan los de Office");
}

const FIG = process.env.FIG || path.join(__dirname, "../informe_avance/figuras");
const ASSETS = process.env.ASSETS || path.join(__dirname, "img");
const SALIDA = process.env.SALIDA || path.join(__dirname, "presentacion_coloquio.pptx");

// Identidad UNNOBA (Manual de identidad institucional, Res. CS 731/2014; B74):
//  - colores institucionales: celeste Pantone 7688 C (#4698CB) y gris Cool Gray 8 (#888B8D / k65 #7C7C7B),
//    con el amarillo institucional (Pantone 136 C, #FFBF3F) como acento;
//  - tipografía principal: familia Century (Century 725 BT; la alternativa oficial es Century Schoolbook,
//    que viene con Office); secundaria: TheSans / Trade Gothic, reemplazadas por Arial porque no vienen
//    instaladas en las computadoras donde se va a proyectar;
//  - el cuadrado del isotipo como motivo, portadas grises con filetes blancos y encabezado con filete.
const GRIS_PORTADA = "7C7C7B";      // Cool Gray 8 C en k65: fondo de portadas y separadores
const GRIS_CLARO = "C6C7C8";        // Cool Gray 4 C: filetes finos y bordes de tablas
const THEME = {
  name: "UNNOBA",
  headFontFace: "Century Schoolbook",
  bodyFontFace: "Arial",
  colors: {
    dk1: "3C3C3B", lt1: "FFFFFF", dk2: "58595B", lt2: "EEEFF0",
    accent1: "4698CB", accent2: "2F6F9F", accent3: "C98A12", accent4: "B5383B",
    accent5: "FFBF3F", accent6: "6D6E71", hlink: "4698CB", folHlink: "6D6E71",
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13,333" x 7,5"
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Extracción de relaciones entre normas y grafo normativo trazable";
pres.subject = "TP Integrador, Problemática III — Sistemas Inteligentes, UNNOBA";
const C = pres.SchemeColor;
const W = 13.333;

// ---------------------------------------------------------------- layouts
const LOGO_POS = path.join(ASSETS, "unnoba_positivo.png");   // isologotipo (extraído del manual), 1371 x 874
const LOGO_NEG = path.join(ASSETS, "unnoba_negativo.png");   // versión negativa, para fondos de menos del 50 % de luz
const RAZON_LOGO = 1371 / 874;
const filete = (y, grosor, color) => ({ line: { x: 0.6, y, w: W - 1.2, h: 0, line: { color, width: grosor } } });
pres.defineSlideMaster({
  title: "PORTADA",
  background: { color: GRIS_PORTADA },
  objects: [
    filete(1.05, 1, "FFFFFF"), filete(6.15, 1, "FFFFFF"),
    { image: { path: LOGO_NEG, x: W - 0.6 - 0.62 * RAZON_LOGO, y: 6.4, w: 0.62 * RAZON_LOGO, h: 0.62 } },
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 1.5, w: 12.1, h: 2.4, fontSize: 40, bold: false, color: C.background1, valign: "bottom", align: "left", fontFace: THEME.headFontFace, margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.6, y: 4.2, w: 12.1, h: 1.7, fontSize: 17, color: "F2F2F2", valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "SECCION",
  background: { color: GRIS_PORTADA },
  objects: [
    filete(1.05, 1, "FFFFFF"), filete(6.15, 1, "FFFFFF"),
    { image: { path: LOGO_NEG, x: W - 0.6 - 0.5 * RAZON_LOGO, y: 6.5, w: 0.5 * RAZON_LOGO, h: 0.5 } },
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 2.75, w: 12.1, h: 1.1, fontSize: 38, bold: false, color: C.background1, align: "center", valign: "middle", fontFace: THEME.headFontFace, margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.6, y: 3.9, w: 12.1, h: 0.9, fontSize: 17, color: "F2F2F2", align: "center", margin: 0 }, text: "" } },
  ],
  slideNumber: { x: 0.6, y: 6.55, w: 0.6, h: 0.3, fontSize: 10, color: "F2F2F2", align: "left" },
});
pres.defineSlideMaster({
  title: "CONTENIDO",
  background: { color: C.background1 },
  objects: [
    // encabezado como en las páginas del manual: filete grueso, rótulo de sección y filete fino
    filete(0.3, 2.25, C.text2), filete(0.64, 0.75, GRIS_CLARO),
    { placeholder: { options: { name: "seccion", type: "body", x: 0.6, y: 0.33, w: 9, h: 0.3, fontSize: 11, bold: true, color: C.accent1, valign: "middle", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.72, w: 12.1, h: 0.72, fontSize: 28, bold: false, color: C.text2, valign: "middle", align: "left", fontFace: THEME.headFontFace, margin: 0 }, text: "" } },
    filete(6.95, 0.75, GRIS_CLARO),
    { text: { text: "Grafo normativo trazable · TP Integrador · Sistemas Inteligentes", options: { x: 0.6, y: 7.02, w: 9, h: 0.3, fontSize: 9, color: C.accent6, margin: 0 } } },
    { image: { path: LOGO_POS, x: W - 0.6 - 0.36 * RAZON_LOGO, y: 7.0, w: 0.36 * RAZON_LOGO, h: 0.36 } },
  ],
  slideNumber: { x: 11.9, y: 0.33, w: 0.8, h: 0.3, fontSize: 11, bold: true, color: C.text2, align: "right" },
});

// ---------------------------------------------------------------- ayudas
function tit(s, t) { s.addText(t, { placeholder: "title" }); }
function card(s, x, y, w, h, nombre, fill) {
  // tarjetas rectas, como los recuadros del manual
  s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: fill || C.background2 }, line: { color: fill || C.background2 }, objectName: nombre });
}
function texto(s, t, o) { s.addText(t, Object.assign({ isTextBox: true, fontSize: 16, color: C.text1, valign: "top", margin: 0.05 }, o)); }
function stat(s, x, y, w, numero, etiqueta, color, nombre) {
  texto(s, numero, { x, y, w, h: 0.9, fontSize: 48, bold: true, color: color || C.accent2, fontFace: THEME.headFontFace, objectName: nombre, valign: "bottom", margin: 0 });
  texto(s, etiqueta, { x, y: y + 0.92, w, h: 0.6, fontSize: 14, color: C.accent6, margin: 0 });
}
function bullets(items, o) {
  return items.map((it, i) => {
    const runs = Array.isArray(it) ? it : [{ text: it }];
    return runs.map((r, j) => ({ text: r.text, options: Object.assign({ bullet: j === 0 ? { indent: 18 } : undefined, breakLine: j === runs.length - 1 && i < items.length - 1, paraSpaceAfter: 8 }, r.options || {}) }));
  }).flat();
}
function img(s, archivo, x, y, w, ratio, nombre) {
  s.addImage({ path: archivo, x, y, w, h: w / ratio, objectName: nombre, altText: nombre });
}
function nodo(s, t, x, y, w, h, fill, colorTexto) {
  s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: fill } });
  texto(s, t, { x, y, w, h, fontSize: 14, bold: true, align: "center", valign: "middle", color: colorTexto || C.background1 });
}
function flecha(s, x, y, w) {
  s.addShape(pres.shapes.LINE, { x, y, w, h: 0, line: { color: C.accent6, width: 2, endArrowType: "triangle" } });
}
function nueva(seccion, master) {
  const sl = pres.addSlide({ masterName: master || "CONTENIDO", sectionTitle: seccion });
  // rótulo del encabezado: la sección, como «Isologotipo / Color» en el manual
  if (!master || master === "CONTENIDO") sl.addText(seccion + "  /  Grafo normativo trazable", { placeholder: "seccion" });
  return sl;
}

// =================================================================== 1. Apertura
pres.addSection({ title: "Apertura" });
let s = nueva("Apertura", "PORTADA");
s.addText("Extracción de relaciones entre normas y grafo normativo trazable", { placeholder: "title" });
s.addText("TP Integrador · Problemática III\nSistemas Inteligentes · Ingeniería en Informática · UNNOBA\nIntegrantes: Cidoni, Valentino · Lodeiro, Bruno · Martino, Lucas · Tagliaferro, Juan Pedro", { placeholder: "body" });
s.addNotes("Presentamos el TP Integrador de la Problemática III: reconstruir, a partir del texto de las normas, qué norma modifica a cuál, y guardarlo en un grafo donde cada vínculo conserva la evidencia textual que lo justifica.");

s = nueva("Apertura");
tit(s, "Las normas se modifican entre sí, en texto libre");
card(s, 0.6, 1.5, 12.1, 1.55, "Texto de InfoLEG");
texto(s, [
  { text: "ARTÍCULO 25.- ", options: { bold: true } },
  { text: "Sustitúyese", options: { bold: true, color: C.accent1 } },
  { text: " el " }, { text: "artículo 198", options: { bold: true, color: C.accent2 } },
  { text: " de la " }, { text: "Ley de Contrato de Trabajo", options: { bold: true, color: C.accent3 } },
  { text: " (t.o. 1976), por lo siguiente: «Artículo 198.- Jornada reducida. La reducción de la jornada máxima legal solamente procederá cuando lo establezcan…»" },
], { x: 0.85, y: 1.65, w: 11.6, h: 1.3, fontSize: 17, fontFace: THEME.headFontFace });
texto(s, "Ley 24.013 (Ley de Empleo), artículo 25, tal como lo publica InfoLEG", { x: 0.6, y: 3.15, w: 12, h: 0.35, fontSize: 12, color: C.accent6 });
nodo(s, "Ley 24.013\nart. 25", 2.4, 4.2, 2.4, 1.1, C.accent6);
flecha(s, 5.0, 4.75, 3.2);
texto(s, "SUSTITUYE", { x: 5.0, y: 4.25, w: 3.2, h: 0.4, fontSize: 16, bold: true, color: C.accent1, align: "center" });
nodo(s, "Ley 20.744 (LCT)\nart. 198", 8.4, 4.2, 2.6, 1.1, C.text2);
texto(s, "Para una persona es una relación; para una computadora es solo texto. El objetivo: que el sistema lo lea y arme el vínculo, con su evidencia.", { x: 1.2, y: 5.8, w: 11, h: 0.8, fontSize: 18, align: "center", color: C.text2, italic: true });
s.addNotes("Un cuerpo normativo es una red: las normas se modifican, sustituyen, derogan y citan entre sí. Acá la Ley de Empleo sustituye el artículo 198 de la Ley de Contrato de Trabajo. Una persona lo lee y entiende la relación; para la computadora es texto. Queremos que el sistema lea ese texto y construya la arista, guardando el fragmento que la justifica.");

s = nueva("Apertura");
tit(s, "Un experimento controlado: InfoLEG como vara de medir");
const pasos = [["1", "Ocultar", "Las relaciones estructuradas de InfoLEG quedan guardadas: el sistema nunca las ve."],
  ["2", "Reconstruir", "El sistema lee solo el texto de cada norma y propone relaciones."],
  ["3", "Comparar", "Al final se comparan sus relaciones con las de InfoLEG (precisión, recall, F1)."]];
pasos.forEach(([n, t, d], i) => {
  const x = 0.6 + i * 4.1;
  card(s, x, 1.6, 3.8, 3.6, "Paso " + n);
  s.addShape(pres.shapes.RECTANGLE, { x: x + 0.3, y: 1.85, w: 0.8, h: 0.8, fill: { color: C.accent1 }, line: { color: C.accent1 } });
  texto(s, n, { x: x + 0.3, y: 1.85, w: 0.8, h: 0.8, fontSize: 28, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0 });
  texto(s, t, { x: x + 0.3, y: 2.85, w: 3.3, h: 0.5, fontSize: 22, bold: true, color: C.text2 });
  texto(s, d, { x: x + 0.3, y: 3.45, w: 3.3, h: 1.6, fontSize: 16 });
});
texto(s, "La relación evaluada es «modifica o complementa», la que registra InfoLEG. Los tipos finos (sustituye, deroga, reglamenta, cita…) se evalúan aparte, sobre 78 casos revisados.", { x: 0.6, y: 5.55, w: 12.1, h: 0.9, fontSize: 16, color: C.accent6 });
s.addNotes("InfoLEG publica el texto de las normas y, por separado, bases estructuradas con qué norma modifica a cuál. Eso permite un experimento controlado: ocultamos las bases, el sistema reconstruye las relaciones solo desde el texto, y después comparamos. Evaluamos la relación general «modifica o complementa», que es la que registra InfoLEG; los tipos finos los medimos aparte.");

s = nueva("Apertura");
tit(s, "Cinco preguntas de investigación");
const pis = [["PI1", "¿Qué efectividad alcanzan reglas, modelos e híbridos para identificar relaciones entre normas?"],
  ["PI2", "¿Un híbrido —reglas que detectan, modelo que decide— mejora a cada enfoque por separado?"],
  ["PI3", "¿Qué formulaciones normativas producen más errores?"],
  ["PI4", "¿Se transfiere, con cambios mínimos, a otro cuerpo normativo (digesto de la UNNOBA)?"],
  ["PI5", "¿Qué aporta un grafo que conserva la evidencia de cada vínculo?"]];
pis.forEach(([p, t], i) => {
  const y = 1.5 + i * 1.0;
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y, w: 1.1, h: 0.75, rectRadius: 0.1, fill: { color: i < 3 ? C.text2 : C.accent1 }, line: { color: i < 3 ? C.text2 : C.accent1 } });
  texto(s, p, { x: 0.6, y, w: 1.1, h: 0.75, fontSize: 20, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0 });
  texto(s, t, { x: 1.95, y, w: 10.7, h: 0.75, fontSize: 18, valign: "middle" });
});
texto(s, "PI1 a PI3: las responde este trabajo · PI4 y PI5: resultados preliminares, adelantados para el final", { x: 0.6, y: 6.5, w: 12.1, h: 0.35, fontSize: 13, color: C.accent6 });
s.addNotes("La consigna pide la PI1 en la cursada y una primera aproximación a la PI2. Respondemos PI1, PI2 y PI3, y adelantamos resultados preliminares de PI4 (transferencia al digesto de la UNNOBA) y PI5 (qué aporta el grafo trazable).");

// =================================================================== 2. Datos y método
pres.addSection({ title: "Datos y método" });
s = nueva("Datos y método");
tit(s, "Un corpus del derecho laboral, congelado y reproducible");
stat(s, 0.6, 1.5, 2.8, "340", "normas (306 con texto)", C.accent2, "Normas");
stat(s, 3.5, 1.5, 2.8, "775", "relaciones del gold de InfoLEG", C.accent1, "Gold");
texto(s, bullets([
  [{ text: "Cinco leyes ancla ", options: { bold: true } }, { text: "(LCT 20.744, 27.802, 24.013, 24.557, 23.551), expandidas un salto en el grafo de InfoLEG." }],
  [{ text: "Corte temporal en 2019: ", options: { bold: true } }, { text: "desarrollo 583 relaciones (hasta 2019) y test 192 (desde 2020, 43 normas)." }],
  [{ text: "Congelado: ", options: { bold: true } }, { text: "el portal cambia cada mes; se verifica byte a byte con SHA-256." }],
  [{ text: "Dataset: ", options: { bold: true } }, { text: "8.066 segmentos de texto y 1.091 pares candidatos con 22 atributos." }],
]), { x: 0.6, y: 3.25, w: 5.9, h: 3.4, fontSize: 16 });
img(s, ASSETS + "/grafo_corpus_claro.png", 6.85, 1.5, 5.85, 1920 / 1080, "Grafo del corpus");
texto(s, "El corpus como grafo: cada punto es una norma, cada línea una relación del gold", { x: 6.85, y: 4.85, w: 5.85, h: 0.4, fontSize: 12, color: C.accent6 });
s.addNotes("El corpus es el dominio laboral: cinco leyes ancla y todo lo que las modifica o es modificado por ellas, un salto. 340 normas, 306 con texto, y 775 relaciones del gold. Separamos en el tiempo: lo de hasta 2019 es desarrollo, y lo de 2020 en adelante es test, que se usa una sola vez. Congelamos los datos porque el portal publica una versión nueva por mes.");

s = nueva("Datos y método");
tit(s, "Pipeline: solo el adaptador depende de la fuente");
img(s, FIG + "/fig1_pipeline.png", 0.6, 1.45, 12.1, 2103 / 504, "Pipeline");
const etapas = [["Adaptador", "HTML o PDF → texto, zonas (VISTO, CONSIDERANDO, articulado) y offsets"],
  ["Detección", "Expresiones regulares + diccionario de nombres: detecta el 99,6 % de las menciones"],
  ["Normalización", "Cada mención → una norma del catálogo; el 48 % nombra normas fuera del corpus"],
  ["Salida estándar", "Una fila por relación con su evidencia: el grafo y la evaluación no cambian con el parser"]];
etapas.forEach(([t, d], i) => {
  const x = 0.6 + i * 3.08;
  card(s, x, 4.6, 2.85, 2.1, "Etapa " + t);
  texto(s, t, { x: x + 0.15, y: 4.72, w: 2.6, h: 0.45, fontSize: 17, bold: true, color: C.text2 });
  texto(s, d, { x: x + 0.15, y: 5.2, w: 2.6, h: 1.4, fontSize: 14 });
});
s.addNotes("El sistema es una cadena de componentes independientes. Solo el adaptador conoce la fuente. Después vienen la detección de menciones, la normalización contra un catálogo, tres parsers intercambiables y una salida estándar: una fila por relación con el fragmento y la posición que la justifican. El grafo y la evaluación se arman solo desde esa salida, así que cambiar de parser o de fuente no cambia nada aguas abajo.");

s = nueva("Datos y método");
tit(s, "Referencia: reglas sobre zona, verbo y tipo de norma");
card(s, 0.6, 1.5, 6.0, 2.4, "Regla F");
texto(s, "Regla F (reglas v2)", { x: 0.85, y: 1.6, w: 5.6, h: 0.45, fontSize: 18, bold: true, color: C.text2 });
texto(s, bullets(["La mención no es posterior a la norma de origen", "No es una cita de procedencia («t.o. por Decreto 390/76»)", "Está en el VISTO, o en el articulado si el origen es una ley o la oración tiene un verbo modificatorio"]), { x: 0.85, y: 2.1, w: 5.6, h: 1.75, fontSize: 15 });
texto(s, "¿Qué zonas predicen un vínculo? (dev)", { x: 7.0, y: 1.5, w: 5.7, h: 0.45, fontSize: 18, bold: true, color: C.text2 });
s.addChart(pres.charts.BAR, [{ name: "En el gold", labels: ["VISTO", "CONSIDERANDO"], values: [80, 24] }], {
  x: 7.0, y: 1.95, w: 5.7, h: 2.0, barDir: "bar", chartColors: [THEME.colors.accent2], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0"%"',
  dataLabelFontFace: "+mn-lt", dataLabelFontSize: 14, catAxisLabelFontFace: "+mn-lt", catAxisLabelFontSize: 14, catAxisLabelColor: THEME.colors.dk1,
  valAxisHidden: true, valAxisMaxVal: 100, valGridLine: { style: "none" }, catGridLine: { style: "none" }, showLegend: false, objectName: "VISTO vs CONSIDERANDO" });
stat(s, 0.6, 4.35, 3.2, "0,828", "F1 en test de las reglas v2", C.accent1, "F1 reglas");
texto(s, [{ text: "El VISTO es la mejor señal y a la vez la principal fuente de error: ", options: { bold: true } }, { text: "el 52 % de los falsos positivos de test son citas del VISTO que solo mencionan la norma." }], { x: 4.0, y: 4.5, w: 8.7, h: 1.3, fontSize: 17 });
s.addNotes("El método de referencia son reglas. La versión 2 acepta un par si la mención no es posterior, no es una cita de procedencia, y aparece en el VISTO o en el articulado con verbo modificatorio. La aceptación del VISTO sale de dev: el 80 % de los pares del VISTO está en el gold, contra el 24 % del CONSIDERANDO. Con eso las reglas llegan a 0,828 de F1 en test. Pero el VISTO también es la principal fuente de falsos positivos.");

// =================================================================== 3. Modelos
pres.addSection({ title: "Modelos" });
s = nueva("Modelos");
tit(s, "Dos modelos supervisados: aprender de ejemplos");
card(s, 0.6, 1.5, 5.95, 4.55, "Random forest");
texto(s, "Random forest (22 atributos)", { x: 0.85, y: 1.6, w: 5.5, h: 0.45, fontSize: 19, bold: true, color: C.accent2 });
texto(s, bullets(["Entrada: zona de las menciones, verbo en la oración, tipos de norma, años de diferencia, posición…",
  "400 árboles de decisión, cada uno con otra muestra de pares y de atributos; la probabilidad es el promedio",
  "Primer árbol real: ¿se la menciona en el VISTO? → ¿el origen es un decreto? → ¿cuántas menciones?",
  "Umbral 0,45 elegido en validación"]), { x: 0.85, y: 2.15, w: 5.5, h: 3.8, fontSize: 17 });
card(s, 6.75, 1.5, 5.95, 4.6, "TF-IDF");
texto(s, "TF-IDF + regresión logística (texto)", { x: 7.0, y: 1.6, w: 5.5, h: 0.45, fontSize: 19, bold: true, color: C.accent1 });
texto(s, bullets(["Entrada: 150 caracteres a cada lado de la mención, con la norma → DESTINO y los dígitos → #",
  "10.804 columnas (palabras y pares de palabras) y un peso aprendido por columna",
  "Pesos reales: «parte_articulado artículo» +4,05; «reemplazado por» −1,73",
  "Memoriza formato: «bs as» (de la fecha) +2,34"]), { x: 7.0, y: 2.15, w: 5.5, h: 3.8, fontSize: 17 });
texto(s, "Entrenados con los 801 pares de desarrollo (472 relaciones reales, 329 citas) · el LLM no se entrena: se le dan instrucciones", { x: 0.6, y: 6.3, w: 12.1, h: 0.5, fontSize: 14, color: C.accent6 });
s.addNotes("Probamos dos modelos que aprenden de ejemplos. Cada ejemplo es un par candidato con su respuesta de InfoLEG. El random forest usa 22 atributos numéricos: 400 árboles, cada uno entrenado con una muestra distinta, y la probabilidad es el promedio de sus votos. El segundo lee el texto alrededor de cada mención: enmascaramos la norma mencionada y los números para que aprenda la forma de la frase, lo pasamos a TF-IDF y una regresión logística aprende un peso por palabra. Los pesos tienen sentido —estar en el articulado suma, «reemplazado por» resta— pero también memoriza formato: «bs as», de la línea de la fecha.");

s = nueva("Modelos");
tit(s, "Entrenar sin hacer trampa");
const prot = [["Test aparte", "Normas posteriores a 2019. Se usan una sola vez, al final."],
  ["Validación agrupada", "5 particiones por norma de origen: los pares de una norma quedan del mismo lado."],
  ["Elegir en desarrollo", "Modelo (logística, random forest, gradient boosting), umbral (0,20 a 0,80) y regularización."],
  ["Reentrenar y medir", "Con todo desarrollo; después, test una vez. Intervalos por bootstrap de normas."]];
prot.forEach(([t, d], i) => {
  const y = 1.5 + i * 1.25;
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: y + 0.1, w: 0.75, h: 0.75, fill: { color: C.text2 }, line: { color: C.text2 } });
  texto(s, String(i + 1), { x: 0.6, y: y + 0.1, w: 0.75, h: 0.75, fontSize: 22, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0 });
  texto(s, t, { x: 1.6, y, w: 4.6, h: 0.45, fontSize: 18, bold: true, color: C.text2 });
  texto(s, d, { x: 1.6, y: y + 0.45, w: 4.6, h: 0.75, fontSize: 14 });
});
s.addTable([
  [{ text: "Modelo (validación en dev)", options: { bold: true, fill: { color: C.background2 } } }, { text: "Umbral", options: { bold: true, fill: { color: C.background2 } } }, { text: "F1", options: { bold: true, fill: { color: C.background2 } } }],
  ["Regresión logística", "0,35", "0,718"],
  [{ text: "Random forest (elegido)", options: { bold: true } }, { text: "0,45", options: { bold: true } }, { text: "0,728", options: { bold: true } }],
  ["Gradient boosting", "0,20", "0,709"],
], { x: 6.7, y: 1.6, w: 6.0, colW: [3.4, 1.3, 1.3], fontSize: 15, color: C.text1, border: { type: "solid", pt: 0.75, color: GRIS_CLARO }, rowH: 0.5, objectName: "Elección del modelo" });
texto(s, "El F1 de validación es contra el gold completo de dev, que incluye pares que el detector no propone: por eso es más bajo que el de test.", { x: 6.7, y: 3.9, w: 6.0, h: 1.0, fontSize: 13, color: C.accent6 });
s.addNotes("Tan importante como el modelo es cómo se evalúa. El test queda aparte y se usa una vez. Para elegir el modelo, el umbral y la regularización usamos validación cruzada en cinco partes, agrupada por norma de origen: si los pares de una misma norma quedaran repartidos, el modelo reconocería la norma y el resultado saldría inflado. Ganó el random forest; recién ahí se reentrena con todo desarrollo y se mide en test.");

s = nueva("Modelos");
tit(s, "¿Faltaban datos? La curva de aprendizaje dice que sí");
img(s, FIG + "/fig8_curva_aprendizaje.png", 0.6, 1.45, 8.1, 1650 / 630, "Curva de aprendizaje");
texto(s, "Entrenamiento con el 10 al 100 % de desarrollo, validación agrupada; la línea punteada son las reglas", { x: 0.6, y: 4.6, w: 8.1, h: 0.4, fontSize: 12, color: C.accent6 });
stat(s, 9.1, 1.5, 3.6, "+2 pts", "de F1 cada vez que se duplican los datos", C.accent3, "Pendiente");
stat(s, 9.1, 3.1, 3.6, "0,94 / 0,81", "F1 en entrenamiento / en validación: memorizan", C.accent1, "Brecha");
texto(s, bullets([[{ text: "En test empatan con las reglas: ", options: { bold: true } }, { text: "random forest 0,823 contra 0,828; TF-IDF solo, 0,761." }],
  [{ text: "Con 801 pares, la limitación medible es la cantidad de datos. ", options: { bold: true } }, { text: "No está probado que la representación alcance: con más datos la curva podría aplanarse." }],
  [{ text: "Usamos el 1,5 % ", options: { bold: true } }, { text: "de las normas que InfoLEG permite etiquetar." }]]), { x: 0.6, y: 5.1, w: 12.1, h: 1.7, fontSize: 15 });
s.addNotes("Los modelos empataron con las reglas, así que preguntamos si les faltaban datos. Entrenamos con fracciones crecientes de desarrollo. Las tres curvas siguen subiendo, unos dos puntos de F1 cada vez que se duplican los datos, y recién al final alcanzan a las reglas. Además, sobre lo que ya vieron aciertan casi todo y sobre lo nuevo bastante menos: memorizan. Conclusión: el empate no prueba que aprender no sirva; prueba que con 800 ejemplos todavía no alcanza.");

s = nueva("Modelos");
tit(s, "Parser LLM: lee la oración y tiene que citar literal");
const fl = ["Segmentos", "Prefiltro", "LLM → JSON", "¿Cita literal?", "Normalización"];
fl.forEach((t, i) => {
  const x = 0.6 + i * 2.5;
  nodo(s, t, x, 1.55, 2.05, 0.8, i === 2 ? C.accent1 : (i === 3 ? C.accent3 : C.text2));
  if (i < fl.length - 1) flecha(s, x + 2.08, 1.95, 0.38);
});
card(s, 0.6, 2.75, 6.0, 3.2, "Respuesta");
texto(s, "Respuesta real del modelo (caché)", { x: 0.85, y: 2.85, w: 5.6, h: 0.4, fontSize: 16, bold: true, color: C.text2 });
texto(s, '{"cita": "artículo 245 de la Ley N° 20.744 (t.o. 1976)",\n "numero": "20744", "articulo_destino": "245",\n "tipo": "SUSTITUYE", "verbo": "Sustitúyese"}', { x: 0.85, y: 3.35, w: 5.6, h: 1.6, fontSize: 13, fontFace: "Courier New" });
texto(s, "Si la cita no aparece tal cual en el texto, la relación se descarta.", { x: 0.85, y: 5.05, w: 5.6, h: 0.8, fontSize: 14, color: C.accent6 });
stat(s, 7.0, 2.75, 2.7, "0,938", "recall en test, el más alto", C.accent1, "Recall LLM");
stat(s, 10.0, 2.75, 2.7, "0,1 %", "citas inventadas, descartadas (8)", C.accent3, "Alucinación");
texto(s, bullets(["F1 en test 0,841: mejor que las reglas, pero no significativo", "Respuestas guardadas en caché: se reproduce sin clave ni costo (USD 14 el corpus completo)"]), { x: 7.0, y: 4.55, w: 5.7, h: 1.5, fontSize: 15 });
s.addNotes("El tercer enfoque es un modelo de lenguaje grande, Claude Sonnet. Lee los artículos que nombran normas y devuelve en JSON la cita, la norma destino, el artículo y el tipo. La condición clave: la cita tiene que estar literal en el texto, si no se descarta. Así la alucinación queda en 0,1 %. Tiene el mejor recall, 0,938, y F1 de 0,841, aunque la ventaja sobre las reglas no es significativa. Todas las respuestas quedan en caché para reproducir sin costo.");

// =================================================================== 4. Resultados
pres.addSection({ title: "Resultados" });
s = nueva("Resultados");
tit(s, "Todos los métodos sobre las mismas 192 relaciones de test");
const met = ["TF-IDF (contexto)", "TF-IDF + atributos", "Clasificador (random forest)", "Reglas v3", "Reglas v2 (referencia)", "Híbrido en cascada", "Reglas ∪ LLM", "Reglas ∩ LLM", "Híbrido reglas + TF-IDF", "Parser LLM"];
const f1 = [0.761, 0.783, 0.823, 0.826, 0.828, 0.829, 0.831, 0.838, 0.839, 0.841];
s.addChart(pres.charts.BAR, [{ name: "F1 en test", labels: met, values: f1 }], {
  x: 0.6, y: 1.4, w: 7.6, h: 5.4, barDir: "bar", chartColors: [THEME.colors.accent1], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.000",
  dataLabelFontFace: "+mn-lt", dataLabelFontSize: 12, dataLabelColor: THEME.colors.dk1, catAxisLabelFontFace: "+mn-lt", catAxisLabelFontSize: 12, catAxisLabelColor: THEME.colors.dk1,
  valAxisMinVal: 0.7, valAxisMaxVal: 0.86, valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" }, showLegend: false, barGapWidthPct: 60,
  showTitle: true, title: "F1 en test (el eje empieza en 0,70)", titleFontFace: "+mn-lt", titleFontSize: 13, titleColor: THEME.colors.accent6, objectName: "F1 por método" });
card(s, 8.6, 1.5, 4.1, 2.2, "Significativo");
texto(s, "La única mejora significativa", { x: 8.8, y: 1.6, w: 3.7, h: 0.4, fontSize: 16, bold: true, color: C.text2 });
texto(s, [{ text: "Reglas ∩ LLM: +1,0 punto", options: { bold: true, color: C.accent3, fontSize: 20 } }, { text: "\nIC 95 % [+0,2; +2,5], por precisión (0,785 → 0,804)", options: { fontSize: 14, breakLine: false } }], { x: 8.8, y: 2.05, w: 3.7, h: 1.5 });
card(s, 8.6, 3.95, 4.1, 2.75, "Lectura");
texto(s, bullets(["Todo queda entre 0,76 y 0,84: el techo es parecido para métodos muy distintos", "Los TF-IDF solos son peores que las reglas (diferencia significativa)", "Con 43 normas de test, los intervalos son de ±4,5 puntos"]), { x: 8.8, y: 4.05, w: 3.75, h: 2.6, fontSize: 14 });
s.addNotes("Esta es la comparación principal, todos los métodos sobre el mismo test. Van de 0,76 a 0,84. Las diferencias significativas, con bootstrap por norma, son pocas: los TF-IDF solos son peores que las reglas, y la intersección de reglas y LLM es mejor, por un punto, ganado en precisión. Que métodos tan distintos lleguen a lo mismo sugiere que el techo está en la tarea, no en el método.");

s = nueva("Resultados");
tit(s, "Dónde se pierde: el error está en decidir, no en detectar");
img(s, FIG + "/fig2_embudo.png", 0.6, 1.4, 6.9, 1757 / 682, "Embudo");
img(s, FIG + "/fig5_errores.png", 0.6, 4.15, 6.5, 1879 / 715, "Causas de error");
texto(s, "Lo que más errores produce (PI3)", { x: 8.0, y: 1.5, w: 4.7, h: 0.45, fontSize: 17, bold: true, color: C.text2 });
texto(s, bullets([[{ text: "Citas del VISTO ", options: { bold: true } }, { text: "que solo nombran la norma: 52 % de los falsos positivos" }],
  [{ text: "Remisiones desde leyes ", options: { bold: true } }, { text: "(«las contribuciones previstas en la Ley 23.660»)" }],
  [{ text: "Decretos que aplican una ley ", options: { bold: true } }, { text: "sin decirlo con un verbo" }],
  [{ text: "Vínculos que el texto no nombra: ", options: { bold: true } }, { text: "80 pares; ningún parser textual los puede encontrar" }]]), { x: 8.0, y: 2.05, w: 4.7, h: 4.0, fontSize: 16 });
texto(s, "Detección 99,6 % · Normalización 99,1 %", { x: 8.0, y: 6.15, w: 4.7, h: 0.45, fontSize: 15, bold: true, color: C.accent3 });
s.addNotes("Evaluamos cada subtarea por separado. La detección encuentra el 99,6 % de las menciones y la normalización acierta el 99,1 %: casi no se pierde nada ahí. La pérdida está en decidir si una cita es un vínculo. Explicamos cada error de test caso por caso: la mitad de los falsos positivos son citas del VISTO, después remisiones desde leyes; y hay 80 pares cuyo vínculo el texto ni siquiera nombra. Sin evaluar por subtarea, habríamos seguido puliendo el detector.");

s = nueva("Resultados");
tit(s, "Tipo de relación: donde el LLM marca la diferencia");
img(s, FIG + "/fig4_tipos.png", 0.6, 1.45, 7.6, 1606 / 832, "Matrices de confusión");
stat(s, 8.7, 1.6, 1.9, "0,672", "macro-F1 reglas", C.accent6, "Tipos reglas");
texto(s, "→", { x: 10.55, y: 1.95, w: 0.45, h: 0.6, fontSize: 32, color: C.accent6, align: "center" });
stat(s, 11.05, 1.6, 1.9, "0,883", "macro-F1 LLM", C.accent1, "Tipos LLM");
texto(s, bullets(["78 casos revisados a mano, 13 por tipo", "Las reglas toman una cita como acción: «la derogación del artículo 2°» → DEROGA (21 de 25 errores)", "El LLM lee la oración y distingue la cita de la acción"]), { x: 8.7, y: 3.4, w: 4.0, h: 3.0, fontSize: 15 });
s.addNotes("Además de si hay vínculo, extraemos de qué tipo es: sustituye, incorpora, deroga, reglamenta, modifica o cita. Sobre 78 casos revisados a mano, las reglas llegan a 0,672 de macro-F1 y el LLM a 0,883. El error típico de las reglas es tomar una mención como acción, por ejemplo una nominalización como «la derogación del artículo 2». Acá es donde el modelo de lenguaje aporta de verdad.");

s = nueva("Resultados");
tit(s, "¿Cuánto explica que el corpus sea chico?");
const filas = [["Los modelos supervisados empatan con las reglas", "Sí, sobre todo", "La curva sigue subiendo y memorizan (0,94 contra 0,81)", C.accent1],
  ["Casi ninguna diferencia es significativa", "Sí: test chico", "43 normas de test: intervalos de ±4,5 puntos", C.accent1],
  ["Reglas y LLM llegan a un techo parecido", "No", "No aprenden del corpus: el 19 % del gold no se nombra en el texto y el criterio del VISTO no se lee", C.accent3],
  ["Se pierde al decidir, no al detectar", "No", "Medido caso por caso, igual en dev y en test", C.accent3]];
s.addTable([[
  { text: "Conclusión", options: { bold: true, fill: { color: C.text2 }, color: C.background1 } },
  { text: "¿Pesa el tamaño?", options: { bold: true, fill: { color: C.text2 }, color: C.background1 } },
  { text: "Por qué", options: { bold: true, fill: { color: C.text2 }, color: C.background1 } }],
  ...filas.map(([a, b, c, col]) => [a, { text: b, options: { bold: true, color: col } }, c])],
  { x: 0.6, y: 1.55, w: 12.1, colW: [4.0, 2.1, 6.0], fontSize: 15, color: C.text1, border: { type: "solid", pt: 0.75, color: GRIS_CLARO }, rowH: 0.85, valign: "middle", objectName: "Efecto del tamaño" });
texto(s, "El tamaño limita a los modelos que aprenden y a la potencia estadística; no explica el techo de las reglas ni del LLM. Ampliar el corpus queda en el plan de maduración.", { x: 0.6, y: 6.0, w: 12.1, h: 0.8, fontSize: 16, italic: true, color: C.text2 });
s.addNotes("Una pregunta esperable: ¿las conclusiones no son por usar un corpus chico? Depende de cuál. A los modelos supervisados sí los limita, lo mostró la curva. Y el test chico hace que casi ninguna diferencia sea significativa. Pero el techo de reglas y LLM no viene del tamaño: ninguno de los dos aprende del corpus, y lo que los limita son propiedades de la tarea, como vínculos que el texto no nombra. Con más datos tendríamos intervalos más angostos, no un techo más alto.");

// =================================================================== 5. Grafo y extensiones
pres.addSection({ title: "Grafo y extensiones" });
s = nueva("Grafo y extensiones");
tit(s, "El grafo en Neo4j: cada arista con su evidencia y su fuente");
card(s, 0.6, 1.5, 6.3, 2.0, "Modelo del grafo");
texto(s, "(:Norma)-[:CONTIENE]->(:Articulo)\n(:Articulo)-[:SUSTITUYE|INCORPORA|DEROGA|\n   REGLAMENTA|MODIFICA|CITA]->(:Articulo|:Norma)", { x: 0.85, y: 1.65, w: 5.9, h: 1.7, fontSize: 14, fontFace: "Courier New" });
texto(s, bullets(["El origen es siempre un artículo; el destino, un artículo cuando el texto lo dice", "Cada arista guarda fragmento, posición, verbo y qué parser la produjo", "Varios parsers conviven: se comparan dos lecturas del mismo artículo con una consulta"]), { x: 0.6, y: 3.75, w: 6.3, h: 2.6, fontSize: 15 });
stat(s, 7.3, 1.5, 2.6, "3.277", "relaciones cargadas = leídas de vuelta", C.accent2, "Ida y vuelta");
stat(s, 10.1, 1.5, 2.6, "0,828", "F1 leyendo desde Neo4j, igual al de los CSV", C.accent3, "F1 Neo4j");
card(s, 7.3, 3.75, 5.4, 2.6, "Números");
texto(s, bullets(["340 normas, 8.129 artículos y 3.277 relaciones tipadas (reglas v2)", "Siete fuentes de InfoLEG (cuatro extractores y tres clasificadores, B73) y tres del digesto: 444 normas", "InfoLEG no está en el grafo: se usa solo para medirlo"]), { x: 7.5, y: 3.9, w: 5.0, h: 2.4, fontSize: 15 });
s.addNotes("El grafo se arma solo desde la salida estándar. Normas y artículos son nodos; la relación es una arista tipada que guarda el fragmento, la posición, el verbo y qué parser la produjo. Verificamos la ida y vuelta: lo que se lee de Neo4j es exactamente lo que se cargó, y el F1 calculado desde el grafo da igual que desde los archivos.");

s = nueva("Grafo y extensiones");
tit(s, "PI5: con el grafo se reconstruye el texto vigente de la LCT");
img(s, FIG + "/fig7_consolidado.png", 0.6, 1.45, 7.6, 1877 / 628, "Consolidado");
stat(s, 8.7, 1.5, 4.0, "95,9 %", "de los 293 artículos coinciden con InfoLEG", C.accent3, "Consolidado");
texto(s, bullets(["105 normas modificatorias, cadenas de hasta 16 saltos", "Art. 245 pasa por cinco normas; art. 92 bis tiene seis versiones", "6 errores reales, ninguno de la consolidación: falta un vínculo en el grafo, una sustitución descartada y una derogación de modificatoria", "Costo: USD 2,4 de LLM"]), { x: 0.6, y: 4.2, w: 12.1, h: 2.5, fontSize: 15 });
s.addNotes("Como prueba de qué aporta la trazabilidad, reconstruimos el texto vigente de la Ley de Contrato de Trabajo solo desde el grafo: tomamos sus 105 modificatorias, extraemos la operación de cada artículo y las aplicamos en orden. El 95,9 % de los artículos coincide con el texto actualizado de InfoLEG. Los errores que quedan no son de la consolidación sino del grafo o de casos que el método no modela.");

s = nueva("Grafo y extensiones");
tit(s, "PI4: el mismo pipeline sobre el digesto de la UNNOBA");
img(s, FIG + "/fig6_pi4.png", 0.6, 1.45, 7.4, 1582 / 629, "PI4");
texto(s, bullets(["70 documentos (912 PDF en el digesto, bajados a mano por el robots.txt)", "Solo se cambió el adaptador: ninguna regla ni umbral", "Detección: F1 0,986 sobre 109 pares"]), { x: 0.6, y: 4.6, w: 7.4, h: 2.0, fontSize: 15 });
stat(s, 8.4, 1.5, 4.3, "0,958", "F1 del híbrido sobre el vínculo", C.accent3, "PI4 híbrido");
card(s, 8.4, 3.3, 4.3, 2.9, "Vocabulario");
texto(s, "El vocabulario va en el adaptador", { x: 8.6, y: 3.4, w: 3.9, h: 0.45, fontSize: 16, bold: true, color: C.text2 });
texto(s, [{ text: "0,405 → 0,864", options: { bold: true, color: C.accent1, fontSize: 26 } }, { text: "\nF1 del LLM al agregar tres frases sobre resoluciones y ordenanzas", options: { fontSize: 14 } }], { x: 8.6, y: 3.9, w: 3.9, h: 2.0 });
s.addNotes("Para la transferencia aplicamos el mismo pipeline a 70 documentos del digesto de la UNNOBA, cambiando solo el adaptador. La detección se transfiere casi perfecta y el híbrido llega a 0,958. La lección es que el vocabulario de la fuente tiene que estar en el adaptador: el prompt de InfoLEG solo hablaba de leyes y decretos, y con tres frases sobre resoluciones el LLM pasa de 0,405 a 0,864. Es preliminar: 70 documentos anotados en una sola pasada.");

// =================================================================== 6. Cierre
pres.addSection({ title: "Cierre" });
s = nueva("Cierre");
tit(s, "Conclusiones");
const conc = [["PI1", "Reglas bien diseñadas ya llegan a 0,83; el LLM, a 0,84. El techo es la tarea, no el método."],
  ["PI2", "Reglas ∩ LLM: +1 punto, la única mejora significativa. La cascada logra lo mismo a un cuarto del costo."],
  ["PI3", "El error está en decidir: citas del VISTO, remisiones desde leyes, decretos sin verbo."],
  ["PI4", "Se transfiere al digesto si el adaptador conoce su vocabulario (preliminar)."],
  ["PI5", "Evidencia en cada arista: ida y vuelta idéntica y la LCT consolidada al 96 %."],
  ["+", "Los modelos supervisados empatan por falta de datos, no está probado que por representación."]];
conc.forEach(([p, t], i) => {
  const y = 1.45 + i * 0.88;
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y, w: 1.0, h: 0.68, rectRadius: 0.1, fill: { color: i === 5 ? C.accent1 : C.text2 }, line: { color: i === 5 ? C.accent1 : C.text2 } });
  texto(s, p, { x: 0.6, y, w: 1.0, h: 0.68, fontSize: 18, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0 });
  texto(s, t, { x: 1.85, y, w: 10.85, h: 0.68, fontSize: 17, valign: "middle" });
});
s.addNotes("Para cerrar. Uno: reglas bien diseñadas ya funcionan muy bien, y el límite está en la tarea: hay relaciones que el texto no dice. Dos: combinar reglas con un LLM mejora poco, y en precisión. Tres: el error está en decidir, sobre todo con las citas del VISTO. Cuatro: se transfiere a otro digesto si el adaptador lleva su vocabulario. Cinco: un grafo con evidencia alcanza para reconstruir el texto vigente de una ley. Y los modelos supervisados necesitan más datos para decir algo definitivo.");

s = nueva("Cierre");
tit(s, "Limitaciones y lo que sigue");
card(s, 0.6, 1.5, 5.95, 4.3, "Limitaciones");
texto(s, "Limitaciones", { x: 0.85, y: 1.6, w: 5.5, h: 0.45, fontSize: 19, bold: true, color: C.accent4 });
texto(s, bullets(["El gold mide un vínculo amplio y tiene errores (3 de 30 falsos positivos eran vínculos reales)", "Test de 192 pares: diferencias de 1 o 2 puntos no se pueden afirmar", "Anotaciones manuales sin segundo anotador (sin kappa)", "Un solo dominio (laboral) y dos tipos de norma"]), { x: 0.85, y: 2.15, w: 5.5, h: 3.5, fontSize: 18 });
card(s, 6.75, 1.5, 5.95, 4.3, "Plan");
texto(s, "Antes del examen final", { x: 7.0, y: 1.6, w: 5.5, h: 0.45, fontSize: 19, bold: true, color: C.accent3 });
texto(s, bullets(["Validación humana y kappa de Cohen", "Muestra independiente del gold y reglas v4", "Comparar modelos de lenguaje (costo y desempeño)", "Ampliar el corpus y repetir la curva de aprendizaje", "Text-to-Cypher: consultas en lenguaje natural sobre el grafo"]), { x: 7.0, y: 2.15, w: 5.5, h: 3.5, fontSize: 18 });
s.addNotes("Las limitaciones principales: el gold de InfoLEG mide un vínculo amplio y tiene errores; el test es chico; las revisiones manuales no tienen segundo anotador; y es un solo dominio. Para el final planeamos la validación humana con kappa, una muestra independiente del gold, comparar modelos de lenguaje, ampliar el corpus para los modelos supervisados y consultas en lenguaje natural sobre el grafo.");

s = nueva("Cierre", "PORTADA");
s.addText("Gracias", { placeholder: "title" });
s.addText("Código, datos, bitácora e informe: github.com/JuampiJPT/grafo-legal\nPreguntas", { placeholder: "body" });
s.addNotes("Gracias. Todo el código, los datos congelados, la bitácora y el informe están en el repositorio. Quedamos a disposición para preguntas.");

// pptxgenjs escribe un segundo <a:pPr> (sin viñeta) dentro del párrafo cuando un ítem con viñeta tiene varios
// tramos de texto (por ejemplo, una etiqueta en negrita y el resto normal). PowerPoint y LibreOffice toman ese
// segundo y la viñeta desaparece. Se borra: un párrafo solo puede tener su <a:pPr> al principio.
async function quitarPPrRepetidos(archivo) {
  const fs = require("fs");
  const JSZip = require(require.resolve("jszip", { paths: [path.dirname(require.resolve("pptxgenjs"))] }));
  const zip = await JSZip.loadAsync(fs.readFileSync(archivo));
  for (const nombre of Object.keys(zip.files).filter((n) => /^ppt\/slides\/slide\d+\.xml$/.test(n))) {
    const xml = await zip.file(nombre).async("string");
    zip.file(nombre, xml.replace(/<\/a:r><a:pPr[^>]*>(?:(?!<\/a:pPr>).)*<\/a:pPr>/g, "</a:r>"));
  }
  fs.writeFileSync(archivo, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
}

(async () => {
  await pres.writeFile({ fileName: SALIDA });
  await quitarPPrRepetidos(SALIDA);
  if (applyTheme) await applyTheme(SALIDA, THEME);
  console.log("escrito", SALIDA);
})();
