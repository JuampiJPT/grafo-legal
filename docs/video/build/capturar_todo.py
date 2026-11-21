"""Captura los cuadros de transición de las 25 escenas y guarda cuántos pasos tiene cada una y la x de Fusi."""
import json, sys, time
from playwright.sync_api import sync_playwright
import base, escenas
sel = sys.argv[1:]  # opcional: solo algunas escenas (E05 E06 ...)
meta_f = base.RAIZ / "meta.json"
meta = json.loads(meta_f.read_text()) if meta_f.exists() else {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for i, fn in enumerate(escenas.ESCENAS, 1):
        nombre = f"E{i:02d}"
        if sel and nombre not in sel:
            continue
        t0 = time.time()
        n, fx = base.capturar(nombre, fn(), b)
        meta[nombre] = {"pasos": n, "fusi_x": fx}
        meta_f.write_text(json.dumps(meta, indent=1))
        print(nombre, n, "pasos", round(time.time() - t0, 1), "s", flush=True)
    b.close()
