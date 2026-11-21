"""Captura el estado final (y uno intermedio) de las escenas pedidas, para revisarlas."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
import base, escenas, escenas_modelos
for _n, _f in escenas_modelos.MODELOS:
    setattr(escenas, _n.lower(), _f)
OUT = Path("/home/claude/video/preview"); OUT.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1920, "height": 1080})
    for nombre in sys.argv[1:]:
        h = getattr(escenas, nombre.lower())()
        f = base.RAIZ / "tmp_prev.html"; f.write_text(h.replace("%FX%", "0"), encoding="utf-8")
        pg.goto(f"file://{f}"); pg.wait_for_timeout(250)
        fx = pg.evaluate("fusiX()")
        f.write_text(h.replace("%FX%", str(int(max(60, min(1500, fx - 60))))), encoding="utf-8")
        pg.goto(f"file://{f}"); pg.wait_for_timeout(250)
        n = base.pasos_de(h)
        pg.evaluate("setStep(0, 0.9)"); pg.screenshot(path=str(OUT / f"{nombre}_a.jpg"), type="jpeg", quality=80)
        pg.evaluate(f"setStep({n-1}, 5)"); pg.screenshot(path=str(OUT / f"{nombre}_z.jpg"), type="jpeg", quality=80)
        print(nombre, "pasos", n, "fusi_x", fx)
    b.close()
