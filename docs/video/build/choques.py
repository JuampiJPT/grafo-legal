import json
from playwright.sync_api import sync_playwright
import base, escenas
meta = json.load(open("/home/claude/video/meta.json"))
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1920, "height": 1080})
    for i, fn in enumerate(escenas.ESCENAS, 1):
        n = f"E{i:02d}"
        if n == "E01": continue
        h = fn(); fx = meta[n]["fusi_x"]
        f = base.RAIZ / "tmp_ch.html"; f.write_text(h.replace("%FX%", "0")); pg.goto(f"file://{f}"); pg.wait_for_timeout(150)
        pg.evaluate(f"setStep({meta[n]['pasos']-1}, 5)")
        caja = dict(x0=fx - 85, x1=fx + 85, y0=1080 - 34 - 8 - 160, y1=1040)
        r = pg.evaluate("""(c)=>{ let peor=0; document.querySelectorAll('.body *').forEach(el=>{ const r=el.getBoundingClientRect();
          if (r.width<5||r.height<5) return; if (getComputedStyle(el).opacity==='0') return;
          if (r.right>c.x0 && r.left<c.x1 && r.bottom>c.y0 && r.top<c.y1) peor=Math.max(peor, r.bottom-c.y0); }); return peor; }""", caja)
        if r > 0: print(n, "se superpone", round(r), "px")
    b.close()
