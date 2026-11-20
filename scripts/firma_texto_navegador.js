// Firmas de los artículos del texto actualizado de InfoLEG, calculadas en el navegador (B61, B62).
//
// Para qué: desde el entorno de Claude no se puede descargar InfoLEG. Este código se pegó en la
// consola (o se ejecutó con la herramienta de JavaScript del navegador) sobre la página
//   https://servicios.infoleg.gob.ar/infolegInternet/anexos/25000-29999/25552/texact.htm
// y devuelve, por artículo, el hash exacto del texto normalizado y un MinHash de 32 valores sobre
// 4-gramas de palabras. scripts/firma_texto.py calcula lo mismo en Python sobre el consolidado,
// así se comparan los textos sin sacarlos de la página. Después el equipo guardó el texact.htm y
// la evaluación definitiva se hace con el texto completo (scripts/25_evaluar_consolidado.py).
//
// Uso en la consola de la página:  copy(JSON.stringify(firmasInfoleg()))
// Formato de salida: [[numero, palabras, hash_exacto_base36, "minhash.minhash...(32)", notas], ...]

function firmasInfoleg() {
  let T = document.body.innerText;
  const corte = T.indexOf('\n\nAntecedentes Normativos');      // historia editorial al final
  if (corte > 0) T = T.slice(0, corte);
  const NOTA = /\((?:art[íi]culo|p[áa]rrafo|inciso|incisos|texto|expresi[óo]n|denominaci[óo]n|cap[íi]tulo|t[íi]tulo|nota|observad|ver |[úu]ltimo|segundo|primer|tercer|cuarto|quinto|sexto|apartado|punto)[^)]{0,600}\)/gi;
  const fnv = s => { let h = 0x811c9dc5; for (const ch of s) { h ^= ch.codePointAt(0); h = Math.imul(h, 16777619) >>> 0; } return h >>> 0; };
  const fmix = h => { h ^= h >>> 16; h = Math.imul(h, 0x85ebca6b) >>> 0; h ^= h >>> 13; h = Math.imul(h, 0xc2b2ae35) >>> 0; h ^= h >>> 16; return h >>> 0; };
  const N = t => t.normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim()
                 .replace(/^(?:art|artículo|articulo)\s+\d+(?:\s+(?:bis|ter|quater|quáter))?\s+/, '');
  const seeds = [...Array(32).keys()].map(i => fmix(i * 2654435761 >>> 0));
  // «Art. 92 TER. —», «Art. 189. Bis —»: el sufijo puede ir en mayúsculas o después del punto
  const ms = [...T.matchAll(/(?:^|\n)\s*(?:Art[íi]culo|Art\.)\s*(\d+)\s*[°º]?\s*\.?\s*(bis|ter|qu[aá]ter)?\s*[.—–:-]/gi)];
  const out = [];
  for (let i = 0; i < ms.length; i++) {
    const m = ms[i];
    const num = m[1] + (m[2] ? ' ' + m[2].toLowerCase().replace('á', 'a') : '');
    let txt = T.slice(m.index, i + 1 < ms.length ? ms[i + 1].index : T.length);
    txt = txt.split(/\n\s*(?:TITULO|CAPITULO|Título|Capítulo)\s+[IVXL]+/)[0];
    const notas = (txt.match(NOTA) || []).map(x => x.replace(/\s+/g, ' ').slice(0, 160));
    const raw = txt.replace(NOTA, ' ').replace(/^(\s*(?:Art[íi]culo|Art\.)\s*\d+\s*[°º]?\s*)\.\s*(bis|ter)/i, '$1 $2');
    const n = N(raw); const w = n ? n.split(' ') : [];
    const sh = new Set();
    for (let j = 0; j + 4 <= w.length; j++) sh.add(fnv(w.slice(j, j + 4).join(' ')));
    if (w.length && w.length < 4) sh.add(fnv(w.join(' ')));
    const mh = seeds.map(s => { let mn = 4294967295; for (const h of sh) { const v = fmix((h ^ s) >>> 0); if (v < mn) mn = v; } return mn.toString(36); });
    out.push([num, w.length, fnv(n).toString(36), mh.join('.'), notas.slice(-2).join(' | ')]);
  }
  return out;
}
