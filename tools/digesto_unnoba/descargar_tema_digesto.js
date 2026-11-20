// Descarga los PDF "con firmas" de la pagina de un tema del digesto UNNOBA y los junta en un zip.
// Uso: abrir la pagina del tema (reglamenta.detalle.php?cod=...) en tu navegador,
// abrir la consola (Cmd+Opcion+J), pegar todo esto y Enter. Va de a uno, con una pausa
// entre pedidos, y al final descarga digesto_tema_<cod>.zip (con fallos.json si alguno falla).
(async () => {
  const links = [...document.querySelectorAll('a[href*="documento.frameim.php"]')]
    .map(a => new URL(a.getAttribute('href'), location.href));
  const vistos = new Set(), items = [];
  for (const u of links) {
    const arch = u.searchParams.get('arch');
    if (arch && !vistos.has(arch)) { vistos.add(arch); items.push({ url: u.href, arch }); }
  }
  console.log(`Documentos con firma en esta pagina: ${items.length}`);
  if (!window.JSZip) {
    await new Promise((ok, mal) => {
      const s = document.createElement('script');
      s.src = 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js';
      s.onload = ok; s.onerror = mal; document.head.appendChild(s);
    });
  }
  const esPdf = async (r) => {
    const b = await r.blob();
    const cab = new Uint8Array(await b.slice(0, 4).arrayBuffer());
    return (String.fromCharCode(...cab) === '%PDF') ? b : null;
  };
  const zip = new JSZip(), fallos = [];
  for (const [i, it] of items.entries()) {
    try {
      let r = await fetch(it.url, { credentials: 'include' });
      let pdf = await esPdf(r.clone());
      if (!pdf) {
        // la pagina "frame" embebe el PDF: se busca su direccion (iframe/embed/object/enlace)
        const html = await r.text();
        const cands = [...html.matchAll(/(?:src|data|href)\s*=\s*["']([^"']+)["']/gi)].map(m => m[1])
          .filter(x => /\.pdf|arch=|documento|ver|descarga/i.test(x));
        cands.sort((a, b) => (b.includes(it.arch) - a.includes(it.arch)) || (/\.pdf/i.test(b) - /\.pdf/i.test(a)));
        for (const c of cands) {
          const r2 = await fetch(new URL(c, it.url).href, { credentials: 'include' });
          if (r2.ok && (pdf = await esPdf(r2))) break;
        }
      }
      if (!pdf) throw new Error('no se encontro el PDF');
      zip.file(it.arch, pdf);
    } catch (e) { fallos.push({ ...it, error: String(e) }); }
    console.log(`${i + 1}/${items.length} ${it.arch}`);
    await new Promise(r => setTimeout(r, 1500));   // pausa entre pedidos, para no cargar el servidor
  }
  if (fallos.length) zip.file('fallos.json', JSON.stringify(fallos, null, 1));
  const cod = new URL(location.href).searchParams.get('cod') || 'tema';
  const blob = await zip.generateAsync({ type: 'blob' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = `digesto_tema_${cod}.zip`; a.click();
  console.log(`Listo: ${items.length - fallos.length} PDF en el zip, ${fallos.length} fallos.`);
})();
