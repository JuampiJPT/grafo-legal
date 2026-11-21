"""Base del video: estilos, componentes con animación por pasos y captura de cuadros (1920x1080).

Cada escena es una página HTML. Cada elemento animado lleva data-step (en qué paso entra), data-anim
(cómo entra) y data-delay (escalonado dentro del paso). Para cada paso se capturan VENTANA segundos
de transición a 30 fps; después el último cuadro queda quieto hasta el paso siguiente.
"""
import html as H
from pathlib import Path

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

RAIZ = Path("/home/claude/video")
REPO = RAIZ / "repo"
ASSETS = RAIZ / "assets"
FIG = REPO / "docs/informe_avance/figuras"
FRAMES = RAIZ / "frames"
VENTANA = 1.4     # segundos de animación al empezar cada paso
FPS = 30
TOTAL = 25

C = dict(bg="#f7f6f2", ink="#1f1e1a", muted="#6b6a64", line="#dedcd5", blue="#2a78d6", orange="#eb6834",
         green="#1baf7a", red="#e34948", yellow="#eda100", violet="#6250d6", card="#ffffff", fusi="#0f3a96")

FMT = HtmlFormatter(style="github-dark", cssclass="hl")
CSS = f"""
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: {C['bg']}; color: {C['ink']};
  font-family: 'Inter', sans-serif; }}
.page {{ position: absolute; inset: 0; padding: 64px 110px 200px 110px; display: flex; flex-direction: column; }}
.kicker {{ font-size: 22px; letter-spacing: .14em; text-transform: uppercase; color: {C['orange']}; font-weight: 700; }}
h1 {{ font-size: 58px; font-weight: 800; letter-spacing: -.01em; margin-top: 8px; line-height: 1.1; }}
.sub {{ font-size: 28px; color: {C['muted']}; margin-top: 12px; line-height: 1.35; }}
.body {{ flex: 1; display: flex; gap: 52px; margin-top: 36px; min-height: 0; }}
.col {{ flex: 1; display: flex; flex-direction: column; gap: 20px; min-width: 0; }}
.col.w2 {{ flex: 1.35; }}
ul.b {{ list-style: none; display: flex; flex-direction: column; gap: 18px; }}
ul.b li {{ font-size: 34px; line-height: 1.35; padding-left: 40px; position: relative; }}
ul.b li::before {{ content: ''; position: absolute; left: 4px; top: 14px; width: 14px; height: 14px; border-radius: 50%;
  background: {C['blue']}; }}
.card {{ background: {C['card']}; border: 1px solid {C['line']}; border-radius: 18px; padding: 24px 30px;
  box-shadow: 0 2px 10px rgba(0,0,0,.04); }}
.card h3 {{ font-size: 30px; margin-bottom: 8px; }}
.card p {{ font-size: 27px; color: {C['muted']}; line-height: 1.4; }}
.num {{ font-size: 74px; font-weight: 800; color: {C['blue']}; line-height: 1; font-variant-numeric: tabular-nums; }}
.numlab {{ font-size: 23px; color: {C['muted']}; margin-top: 8px; }}
.code {{ border-radius: 16px; overflow: hidden; line-height: 1.45; background: #0d1117; }}
.code .file {{ background: #161b22; color: #8b949e; font-family: 'DejaVu Sans Mono', monospace; font-size: 18px;
  padding: 10px 22px; border-bottom: 1px solid #30363d; }}
.code pre {{ padding: 16px 22px; font-family: 'DejaVu Sans Mono', monospace; white-space: pre; }}
.img {{ border-radius: 14px; overflow: hidden; border: 1px solid {C['line']}; background: white; }}
.img img {{ display: block; width: 100%; }}
.shot {{ box-shadow: 0 18px 50px rgba(0,0,0,.16); }}
.cap {{ font-size: 19px; color: {C['muted']}; margin-top: 8px; }}
table.t {{ border-collapse: collapse; font-size: 25px; width: 100%; }}
table.t th {{ text-align: left; color: {C['muted']}; font-weight: 600; font-size: 20px; padding: 9px 14px;
  border-bottom: 2px solid {C['line']}; }}
table.t td {{ padding: 11px 14px; border-bottom: 1px solid {C['line']}; }}
table.t tr.hi td {{ background: #fff3ec; font-weight: 700; }}
.mono {{ font-family: 'DejaVu Sans Mono', monospace; }}
.tag {{ display: inline-block; padding: 4px 14px; border-radius: 999px; font-size: 21px; font-weight: 700; color: white; }}
.flow {{ display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }}
.node {{ background: #eef4fc; border: 2px solid {C['blue']}; border-radius: 16px; padding: 14px 20px; font-size: 24px;
  font-weight: 600; text-align: center; }}
.node.o {{ background: #fdf0ea; border-color: {C['orange']}; }}
.node.g {{ background: #f2f1ee; border-color: #a5a49d; }}
.node.v {{ background: #e9f8f1; border-color: {C['green']}; }}
.node.y {{ background: #fdf5e0; border-color: {C['yellow']}; }}
.arrow {{ font-size: 34px; color: {C['muted']}; }}
.text {{ font-family: 'Charter', 'Bitstream Charter', serif; font-size: 31px; line-height: 1.55; }}
mark {{ background: none; padding: 1px 4px; border-radius: 6px; color: inherit; }}
mark.b {{ background: rgba(42,120,214,.18); box-shadow: inset 0 -3px {C['blue']}; }}
mark.o {{ background: rgba(235,104,52,.2); box-shadow: inset 0 -3px {C['orange']}; }}
mark.g {{ background: rgba(27,175,122,.2); box-shadow: inset 0 -3px {C['green']}; }}
mark.r {{ background: rgba(227,73,72,.18); text-decoration: line-through; }}
.bar {{ height: 44px; border-radius: 6px; }}
.foot {{ position: absolute; left: 110px; right: 110px; bottom: 34px; display: flex; gap: 8px; align-items: center; }}
.foot .seg {{ flex: 1; height: 8px; border-radius: 4px; background: {C['line']}; }}
.foot .seg.done {{ background: #a9c6ec; }}
.foot .seg.cur {{ background: {C['fusi']}; }}
.foot .lab {{ font-size: 17px; color: {C['muted']}; margin-left: 18px; white-space: nowrap; }}
.bubble {{ position: absolute; background: white; border: 3px solid {C['fusi']}; border-radius: 22px; padding: 14px 22px;
  font-size: 25px; font-weight: 700; color: {C['fusi']}; white-space: nowrap; box-shadow: 0 6px 18px rgba(0,0,0,.08); }}
.bubble::after {{ content: ''; position: absolute; bottom: -18px; left: 34px; border: 9px solid transparent;
  border-top: 12px solid {C['fusi']}; }}
{FMT.get_style_defs('.hl')}
.hl {{ background: #0d1117 !important; }}
.hl .hll {{ background-color: rgba(235,104,52,.3) !important; display: block; }}
"""

JS = """
const VENT = %VENT%;
function ease(q){ return q<0?0:q>1?1:1-Math.pow(1-q,3); }
function fmt(v, dec, sep){ let s=v.toFixed(dec); if(sep){ let [a,b]=s.split('.'); a=a.replace(/\\B(?=(\\d{3})+(?!\\d))/g,'.'); s=b?a+','+b:a; } else s=s.replace('.',','); return s; }
function setStep(k, t){
  document.querySelectorAll('[data-step]').forEach(el=>{
    const s=+el.dataset.step, d=+(el.dataset.delay||0), a=el.dataset.anim||'up', u=el.dataset.until;
    let q = s<k ? 1 : (s>k ? 0 : ease((t-d)/0.6));
    if (u!==undefined && k>=+u) q = (k==+u) ? 1-ease(t/0.35) : 0;
    if (a=='up'){ el.style.opacity=q; el.style.transform=`translateY(${(1-q)*36}px)`; }
    else if (a=='fade'){ el.style.opacity=q; }
    else if (a=='left'){ el.style.opacity=q; el.style.transform=`translateX(${(1-q)*-60}px)`; }
    else if (a=='pop'){ el.style.opacity=Math.min(1,q*1.6); el.style.transform=`scale(${0.7+0.3*q})`; }
    else if (a=='grow'){ el.style.width=(q*(+el.dataset.w))+'px'; el.style.opacity=q>0?1:0; }
    else if (a=='draw'){ el.style.transformOrigin='left center'; el.style.transform=`scaleX(${q})`; el.style.opacity=q>0?1:0; }
    else if (a=='zoom'){ el.style.opacity=Math.min(1,q*2); el.style.transform=`scale(${1.08-0.08*q})`; }
    else if (a=='mk'){ const c=el.dataset.c; el.style.background=`rgba(${c},${0.2*q})`; el.style.boxShadow=`inset 0 -3px rgba(${c},${q})`; }
    else if (a=='count'){ el.style.opacity=q>0?1:0; el.textContent=(el.dataset.pre||'')+fmt(q*(+el.dataset.target), +(el.dataset.dec||0), el.dataset.sep=='1')+(el.dataset.suf||''); }
  });
}
function fusiX(){ const c=document.querySelector('.seg.cur'); if(!c) return 0; const r=c.getBoundingClientRect(); return r.left+r.width/2; }
"""


def esc(s):
    return H.escape(s)


def st(k, contenido, anim="up", delay=0.0, until=None, tag="div", cls="", style=""):
    u = f' data-until="{until}"' if until is not None else ""
    return f'<{tag} data-step="{k}" data-anim="{anim}" data-delay="{delay}"{u} class="{cls}" style="{style}">{contenido}</{tag}>'


def count(k, target, dec=0, suf="", pre="", sep=True, delay=0.0, cls="num", style=""):
    return (f'<div data-step="{k}" data-anim="count" data-delay="{delay}" data-target="{target}" data-dec="{dec}" '
            f'data-suf="{esc(suf)}" data-pre="{esc(pre)}" data-sep="{1 if sep else 0}" class="{cls}" style="{style}">0</div>')


MK = {"b": "42,120,214", "o": "235,104,52", "g": "27,175,122", "r": "227,73,72"}


def mk(k, texto, color="b", delay=0.0):
    """Texto siempre visible; lo que se anima es el resaltado."""
    return (f'<span data-step="{k}" data-anim="mk" data-delay="{delay}" data-c="{MK[color]}" '
            f'style="padding:1px 4px;border-radius:6px">{texto}</span>')


def bar(k, w, color, delay=0.0, h=44):
    return (f'<div data-step="{k}" data-anim="grow" data-delay="{delay}" data-w="{w}" class="bar" '
            f'style="background:{color};height:{h}px;width:{w}px"></div>')


def code(src, lang="python", archivo="", hl=(), size=21):
    fmt = HtmlFormatter(style="github-dark", cssclass="hl", hl_lines=list(hl))
    cuerpo = highlight(src.strip("\n"), get_lexer_by_name(lang), fmt)
    head = f'<div class="file">{esc(archivo)}</div>' if archivo else ""
    return f'<div class="code" style="font-size:{size}px">{head}{cuerpo}</div>'


def img(path, cap="", extra="", style=""):
    c = f'<div class="cap">{cap}</div>' if cap else ""
    return f'<div class="img {extra}" style="{style}"><img src="file://{path}"></div>{c}'


def bullets(items, desde=1, cada=1):
    """Cada ítem entra en un paso distinto (desde, desde+cada, ...)."""
    li = "".join(st(desde + i * cada, it, "left", tag="li") for i, it in enumerate(items))
    return f'<ul class="b">{li}</ul>'


def foot(escena):
    segs = "".join(f'<div class="seg {"done" if i < escena - 1 else ("cur" if i == escena - 1 else "")}"></div>'
                   for i in range(TOTAL))
    return f'<div class="foot">{segs}<div class="lab">{escena:02d} / {TOTAL}</div></div>'


def pagina(escena, kicker, titulo, cuerpo, sub="", burbuja="", extra=""):
    s = st(0, sub, delay=0.2, cls="sub") if sub else ""
    b = st(0, esc(burbuja), "pop", delay=0.5, until=1, cls="bubble", style="left:%FX%px;bottom:225px") if burbuja else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body><div class="page">{st(0, kicker, "left", cls="kicker")}{st(0, titulo, delay=0.08, tag="h1")}{s}
<div class="body">{cuerpo}</div></div>{foot(escena)}{b}{extra}<script>{JS.replace('%VENT%', str(VENTANA))}</script></body></html>"""


def pasos_de(html_str):
    import re
    ks = [int(k) for k in re.findall(r'data-step="(\d+)"', html_str)]
    return max(ks) + 1 if ks else 1


def capturar(nombre, html_str, browser):
    """Escribe FRAMES/nombre/p{k}_{i:03d}.jpg (transición de cada paso) y devuelve la cantidad de pasos y la x de Fusi."""
    d = FRAMES / nombre
    d.mkdir(parents=True, exist_ok=True)
    pg = browser.new_page(viewport={"width": 1920, "height": 1080})
    f = RAIZ / f"tmp_{nombre}.html"
    # la burbuja se ubica sobre Fusi: primero se mide su x con la página real
    f.write_text(html_str.replace("%FX%", "0"), encoding="utf-8")
    pg.goto(f"file://{f}")
    pg.wait_for_timeout(200)
    fx = pg.evaluate("fusiX()")
    f.write_text(html_str.replace("%FX%", str(int(max(60, min(1500, fx - 60))))), encoding="utf-8")
    pg.goto(f"file://{f}")
    pg.wait_for_timeout(250)
    n = pasos_de(html_str)
    cuadros = int(VENTANA * FPS)
    for k in range(n):
        for i in range(cuadros):
            pg.evaluate(f"setStep({k}, {i / FPS})")
            pg.screenshot(path=str(d / f"p{k}_{i:03d}.jpg"), type="jpeg", quality=92)
    pg.close()
    return n, fx
