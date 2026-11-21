"""Las 25 escenas del video. Cada función devuelve el HTML de la escena; los pasos (data-step) siguen los
tiempos de la narración de guion_video.md."""
from base import (ASSETS, C, CSS, FIG, JS, VENTANA, bar, bullets, code, count, esc, img, mk, pagina, st)

FUSI = "/home/claude/video/fusi"


def big_fusi(img_name, k=0, anim="pop", delay=0.3, w=300, style=""):
    return st(k, f'<img src="file://{FUSI}/{img_name}" style="width:{w}px;image-rendering:pixelated">', anim, delay,
              style=style)


# ---------------------------------------------------------------- E01
def e01():
    g = str(ASSETS / "grafo_corpus_oscuro.png")
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
    body{{background:#14161c;color:#ece9e1}}
    .bg{{position:absolute;inset:0;background:url('file://{g}') center/cover no-repeat}}
    .v{{position:absolute;inset:0;background:linear-gradient(90deg,rgba(20,22,28,.97) 0%,rgba(20,22,28,.82) 48%,rgba(20,22,28,.2) 100%)}}
    .t{{position:absolute;left:120px;top:250px;width:1060px}}
    .t h1{{font-size:80px;line-height:1.05;margin:18px 0 26px}}
    .t p{{font-size:31px;color:#b9b6ac}}
    .bubble{{color:#0f3a96}}</style></head><body>
    {st(0, '', 'zoom', cls='bg')}<div class="v"></div>
    <div class="t">{st(0, 'TP Integrador · Problemática III', 'left', 0.1, cls='kicker')}
    {st(0, 'Extracción de relaciones entre normas y grafo normativo trazable', 'up', 0.25, tag='h1')}
    {st(0, 'Sistemas Inteligentes · Ingeniería en Informática · UNNOBA', 'up', 0.45, tag='p')}</div>
    {big_fusi('fusi_feliz.png', 1, w=330, delay=0, style='position:absolute;right:250px;bottom:170px')}
    {st(1, '¡Hola! Soy Fusi y hoy te cuento todo el TP', 'pop', 0.35, cls='bubble', style='right:150px;bottom:470px')}
    <script>{JS.replace('%VENT%', str(VENTANA))}</script></body></html>"""


# ---------------------------------------------------------------- E02
def e02():
    t = (f'ARTICULO 25.- {mk(1, "Sustituyese", "o")} el {mk(2, "artículo 198", "b")}, '
         f'de la {mk(2, "Ley de Contrato de Trabajo", "g", 0.3)} (t.o 1976), por lo siguiente: '
         f'"Artículo 198.- Jornada reducida. La reducción de la jornada máxima legal solamente procederá cuando lo establezcan…"')
    plain = st(0, t, "up", 0.3, cls="card text")
    arista = f"""<div class="flow" style="margin-top:34px;justify-content:center;gap:18px">
      {st(3, 'Ley 24.013<br><span style="font-weight:400;font-size:21px">art. 25</span>', 'pop', 0, cls='node g')}
      {st(3, f'<span class="tag" style="background:{C["orange"]}">SUSTITUYE</span><div style="font-size:64px;color:{C["orange"]};line-height:.8">⟶</div><span style="font-size:21px;color:{C["muted"]}">art. 198</span>', 'draw', 0.25, style='display:flex;flex-direction:column;align-items:center')}
      {st(3, 'Ley 20.744 (LCT)', 'pop', 0.5, cls='node')}</div>
      {st(4, 'Para una persona es una relación. Para una computadora, es solo texto.', 'up', 0, cls='sub', style='text-align:center;margin-top:28px')}"""
    return pagina(2, "El problema", "Las normas se modifican entre sí",
                  f'<div class="col">{plain}{arista}</div>', sub="Ley 24.013 (Ley de Empleo), artículo 25, tal como lo publica InfoLEG",
                  burbuja="¿Cómo lo entiende una máquina?")


# ---------------------------------------------------------------- E03
def e03():
    pasos = [("1", "Ocultar 🔒", "Las relaciones de InfoLEG se guardan bajo llave: el sistema nunca las ve."),
             ("2", "Reconstruir ⚙", "El sistema lee solo el texto de cada norma y propone relaciones."),
             ("3", "Comparar ✓", "Al final se comparan sus relaciones con las de InfoLEG.")]
    cards = "".join(st(i + 1, f'<div class="num">{n}</div><h3 style="margin-top:14px">{t}</h3><p>{d}</p>', "up",
                       cls="card", style="flex:1") for i, (n, t, d) in enumerate(pasos))
    return pagina(3, "La idea", "Un experimento controlado",
                  f'<div style="display:flex;gap:34px;width:100%;align-items:stretch">{cards}</div>',
                  sub="InfoLEG publica el texto de las normas y, aparte, qué norma modifica a cuál",
                  burbuja="InfoLEG es nuestra vara de medir")


# ---------------------------------------------------------------- E04
def e04():
    pis = ["<b>PI1</b> · ¿Qué tan bien funcionan reglas, modelos e híbridos?",
           "<b>PI2</b> · ¿Combinar reglas con modelos mejora?",
           "<b>PI3</b> · ¿Qué formas de escribir producen más errores?",
           "<b>PI4</b> · ¿Se transfiere a otro cuerpo normativo (digesto UNNOBA)?",
           "<b>PI5</b> · ¿Qué aporta un grafo con la evidencia de cada vínculo?"]
    return pagina(4, "Preguntas de investigación", "Cinco preguntas guían el trabajo",
                  f'<div class="col">{bullets(pis)}</div>', burbuja="Estas son las preguntas")


# ---------------------------------------------------------------- E05
def e05():
    filas = [("Normativa nacional", 430834), ("Normas modificatorias", 380481), ("Normas modificadas", 385118)]
    tabla = '<table class="t"><tr><th>Base (Portal de Datos Abiertos de la Justicia)</th><th>Filas</th></tr>' + "".join(
        f'<tr><td>{n}</td><td>{count(1, v, delay=i * 0.15, cls="mono", style="font-size:27px;font-weight:700")}</td></tr>'
        for i, (n, v) in enumerate(filas)) + "</table>"
    js = code('''{
  "fecha_descarga": "2026-11-06T21:53:12",
  "fuentes": {
    "base": {
      "archivo": "base-infoleg-normativa-nacional.csv",
      "sha256_csv": "c9347a2da68c43eb…",
      "filas": 430834
    },
    "modificatorias": { "filas": 380481, … },
    "modificadas":    { "filas": 385118, … }
  }
}''', "json", "data/corpus/procedencia.json", size=22)
    izq = f'{st(1, tabla)}{st(2, "<h3>El gold</h3><p>Las bases complementarias dicen qué norma modifica a cuál: contra eso se mide.</p>", cls="card")}'
    return pagina(5, "Paso 1 · Datos", "De dónde salen los datos",
                  f'<div class="col">{izq}</div><div class="col">{st(3, js)}</div>', burbuja="¡Arrancamos por los datos!")


# ---------------------------------------------------------------- E06
def e06():
    src = '''# --- Expansion a 1 salto ---
corpus = set(expansion) | set(SEMILLAS_SIN_EXPANDIR)
for s in expansion:
    vecinos = set(pares.loc[pares.id_norma_modificatoria == s,
                            "id_norma_modificada"]) | \\
              set(pares.loc[pares.id_norma_modificada == s,
                            "id_norma_modificatoria"])
    corpus |= {v for v in vecinos if tipo.get(v) in TIPOS}'''
    nums = f"""<div style="display:flex;gap:40px">
      {st(3, count(3, 340) + '<div class="numlab">normas</div>', 'fade')}
      {st(3, count(3, 306, delay=0.15) + '<div class="numlab">con texto</div>', 'fade')}
      {st(3, count(3, 775, delay=0.3, style=f'color:{C["orange"]}') + '<div class="numlab">relaciones del gold</div>', 'fade')}</div>"""
    izq = (st(1, code(src, archivo="scripts/01_obtener_corpus.py", hl=[3, 8], size=23)) +
           st(1, '<p>Anclas: Ley 20.744 (LCT), 27.802, 24.013, 24.557 y 23.551. Solo leyes y decretos.</p>', delay=0.2, cls="card") + nums)
    der = st(2, img(str(ASSETS / "grafo_corpus_claro.png"), extra="shot"), "zoom")
    return pagina(6, "Paso 1 · Datos", "Un corpus del derecho laboral", f'<div class="col">{izq}</div><div class="col w2">{der}</div>',
                  burbuja="Cinco leyes ancla y sus vecinas")


# ---------------------------------------------------------------- E07
def e07():
    linea = f"""<div style="position:relative;height:330px;width:100%;margin-top:10px">
      <div style="position:absolute;left:0;right:0;top:150px;height:10px;background:{C['line']};border-radius:5px"></div>
      {st(1, '', 'draw', style=f'position:absolute;left:0;width:72%;top:150px;height:10px;background:{C["blue"]};border-radius:5px')}
      {st(2, '', 'draw', style=f'position:absolute;left:72%;right:0;top:150px;height:10px;background:{C["orange"]};border-radius:5px')}
      {st(1, '', 'fade', 0.4, style=f'position:absolute;left:72%;top:95px;height:120px;border-left:4px dashed {C["ink"]}')}
      {st(1, '31/12/2019', 'pop', 0.5, style='position:absolute;left:68.5%;top:40px;font-size:28px;font-weight:700')}
      <div style="position:absolute;left:0;top:185px;font-size:26px;color:{C['muted']}">1934</div>
      <div style="position:absolute;right:0;top:185px;font-size:26px;color:{C['muted']}">2026</div>
      <div style="position:absolute;left:24%;top:220px">{count(1, 583, delay=0.3)}<div class="numlab">pares para <b>desarrollar</b> (dev)</div></div>
      <div style="position:absolute;left:76%;top:220px">{count(2, 192, delay=0.3, style=f'color:{C["orange"]}')}<div class="numlab">pares de <b>prueba</b> (test)</div></div>
      {st(3, '🔒 se evalúa una sola vez', 'pop', 0, cls='tag', style=f'position:absolute;left:76%;top:330px;background:{C["orange"]};font-size:24px')}
    </div>"""
    return pagina(7, "Paso 1 · Datos", "Desarrollo y prueba, separados en el tiempo", f'<div class="col">{linea}</div>',
                  sub="Simula lo que pasaría con normas nuevas que el sistema nunca vio", burbuja="Nada de hacer trampa")


# ---------------------------------------------------------------- E08
def e08():
    t = f"""<table class="t"><tr><th>Descarga</th><th>Normas</th><th>Pares del gold</th><th>Hashes de las bases</th></tr>
      <tr><td>30/09/2026</td><td>183</td><td>402</td><td class="mono">…</td></tr>
      {st(1, f'<td>31/10/2026</td><td>185</td><td>406</td><td class="mono" style="color:{C["red"]}">cambiaron</td>', 'fade', tag='tr', cls='hi')}</table>"""
    term = code("""$ bash correr_pipeline.sh
== 1/10 Verificacion del corpus: se regenera con los zips de data/raw
   corpus_normas.csv identico al congelado
   gold_relaciones.csv identico al congelado""", "console", "Terminal", size=22)
    izq = st(0, t, delay=0.3) + st(1, '<p>En un mes el portal publicó otra versión y aparecieron dos decretos nuevos. Las anteriores no se guardan.</p>', delay=0.3, cls="card")
    der = st(2, "<h3>Decisión: congelar ❄</h3><p>Corpus único congelado, zips originales guardados y verificación byte a byte.</p>", cls="card") + st(3, term)
    return pagina(8, "Paso 1 · Datos", "El portal cambia: congelamos el corpus", f'<div class="col">{izq}</div><div class="col">{der}</div>',
                  burbuja="¡Sorpresa en el portal!")


# ---------------------------------------------------------------- E09
def e09():
    shot = st(0, img(str(ASSETS / "infoleg_412_art25_crop.jpg"), cap="InfoLEG · Ley 24.013 (data/textos/infoleg/html/412.html)", extra="shot"), "zoom", 0.3)
    zonas = f"""<div class="card text" style="font-size:25px;line-height:1.6">
<span style="color:{C['muted']}">[0] encabezado</span> Bs. As., 22/01/2021 {mk(1, 'VISTO el Expediente N° EX-2021-…, las Leyes Nros. 24.241, 24.557, 26.122…', 'b')}
{mk(1, 'y CONSIDERANDO: Que …', 'g', 0.3)}<br>
<span style="color:{C['muted']}">[1] articulado</span> {mk(1, 'ARTÍCULO 1°.- Sustitúyese el artículo …', 'o', 0.6)}<br>
<span style="color:{C['muted']}">[2] articulado</span> {mk(1, 'ARTÍCULO 2°.- …', 'o', 0.8)}<br>
<span style="color:{C['muted']}">[3] notas</span> <span style="color:{C['muted']}">Nota Infoleg: …</span></div>"""
    src = '''_ART = re.compile(
    r"(?im)^[ \\t]*(?:ART[IÍ]CULO|ART\\.)[ \\t]*(\\d+)[ \\t]*"
    r"(?:[º°o](?![a-z]))?[ \\t]*(bis|ter|qu[aá]ter)?"
    r"[ \\t]*(?:[º°o](?![a-z]))?[ \\t]*[.\\-–—:]")

def segmentar(texto):
    marcas = list(_ART.finditer(texto))
    arts = [Articulo("0", "encabezado", 0, marcas[0].start(), …)]
    for i, m in enumerate(dentro):
        fin = dentro[i+1].start() if i+1 < len(dentro) else fin_art
        arts.append(Articulo(num, "articulado", m.start(), fin))'''
    der = (st(1, zonas) + st(2, code(src, archivo="src/grafo_legal/fuentes/infoleg.py", hl=[1, 2, 3, 4], size=18)) +
           st(3, '<p><b>Clave:</b> cada pedazo guarda su posición exacta (inicio, fin) en el texto.</p>', cls="card"))
    return pagina(9, "Paso 2 · Adaptador", "Del HTML de InfoLEG al texto con estructura",
                  f'<div class="col w2">{shot}</div><div class="col w2">{der}</div>', burbuja="306 textos descargados")


# ---------------------------------------------------------------- E10
def e10():
    src = '''_TIPO = (r"(?P<tipo>decretos?[\\s\\-]+ley(?:es)?|"
         r"decretos?\\s+de\\s+necesidad\\s+y\\s+urgencia|"
         r"decretos?|leyes|ley|dnu)")
_NUM  = r"\\d{1,3}(?:\\.\\d{3})+|\\d+"          # "20.744" o "20744"
_UNO  = rf"(?:{_NUM})(?:\\s*/\\s*\\d{{2,4}})?"     # "1694/06", "70/2023"
_LISTA = rf"(?P<lista>{_UNO}(?:{_RELLENO}{_SEP}(?:{_NRO}\\s*)?{_UNO})*)"'''
    ej = ['<mark class="b">Ley N° 24.557</mark>', '<mark class="b">Decreto 1694/06</mark>',
          'las <mark class="b">Leyes Nros. 23.551</mark> y <mark class="b">25.674</mark>',
          '<mark class="b">DNU 70/2023</mark>',
          'la <mark class="g">Ley de Contrato de Trabajo</mark> <span style="color:#6b6a64;font-size:22px;font-family:Inter">(diccionario de nombres)</span>']
    lis = "".join(st(1 + i // 2, e, "left", 0.3 * (i % 2), tag="li") for i, e in enumerate(ej))
    der = (f'<div class="card text" style="font-size:27px"><ul class="b">{lis}</ul></div>' +
           st(4, f'{count(4, 99.6, dec=1, suf=" %")}<div class="numlab">de las menciones del gold se detectan</div>', cls="card"))
    return pagina(10, "Paso 3 · Detección", "Encontrar cada mención a otra norma",
                  f'<div class="col w2">{st(0, code(src, archivo="src/grafo_legal/extractores/menciones.py", size=22), delay=0.3)}</div><div class="col">{der}</div>',
                  burbuja="¡A cazar menciones!")


# ---------------------------------------------------------------- E11
def e11():
    est = [("Resuelta", "una sola norma posible", C["green"]), ("Ambigua", "falta el año y hay varias", C["yellow"]),
           ("Fuera del corpus", "existe, pero no está entre las 340 (48 %)", C["muted"]),
           ("No encontrada", "no existe en el catálogo", C["red"])]
    cards = "".join(st(1, f'<h3>{t}</h3><p>{d}</p>', "left", i * 0.15, cls="card", style=f"border-left:10px solid {c}")
                    for i, (t, d, c) in enumerate(est))
    ej_v2 = (f'«<mark class="b">Decreto 467</mark> del 14 de abril de <mark class="r">1988</mark>»<div style="font-size:23px;margin-top:12px;'
             f'color:{C["red"]};font-family:Inter">v2: el año no se lee → ambigua (360 de 580 ambiguas)</div>')
    ej_v3 = (f'«<mark class="b">Decreto 467</mark> del 14 de abril de <mark class="g">1988</mark>»<div style="font-size:23px;margin-top:12px;'
             f'color:{C["green"]};font-family:Inter">v3: lee el año de la fecha → resuelta ✓</div>')
    der = st(2, ej_v2, cls="card text", style="font-size:29px") + st(3, ej_v3, cls="card text", style="font-size:29px")
    return pagina(11, "Paso 4 · Normalización", "¿A qué norma concreta se refiere?",
                  f'<div class="col">{cards}</div><div class="col">{der}</div>', burbuja="¿Cuál de todas?")


# ---------------------------------------------------------------- E12
def e12():
    src = '''CONFIGS = {
  "C_articulado_temporal": lambda e: _cuenta(e) and e.zona == "articulado",
  "F_visto_o_articulado_con_verbo_o_ley": lambda e: _cuenta(e) and (
      e.parte == "visto"
      or (e.zona == "articulado" and e.metodo == "regex_numero"
          and (e.tipo_origen != "decreto" or bool(e.verbo_oracion)))),
}
def _cuenta(e):   # no posterior al origen y no es cita de procedencia
    return e.temporal_ok and not e.procedencia'''
    barras = f"""<h3>¿Está en el gold?</h3>
      <div style="display:flex;align-items:center;gap:16px;margin:16px 0"><div style="width:200px;font-size:25px">VISTO</div>
        {bar(1, 330, C['blue'])}{st(1, '80 %', 'fade', 0.5, tag='b', style='font-size:30px;white-space:nowrap')}</div>
      <div style="display:flex;align-items:center;gap:16px"><div style="width:200px;font-size:25px">CONSIDERANDO</div>
        {bar(1, 99, C['muted'], 0.2)}{st(1, '24 %', 'fade', 0.6, tag='b', style='font-size:30px;white-space:nowrap')}</div>"""
    proc = ('Ley 20.744 <mark class="r">(t.o. por Decreto 390/76)</mark><div style="font-family:Inter;font-size:21px;'
            'color:#6b6a64;margin-top:8px">cita de procedencia: se descarta</div>')
    izq = st(0, '<h3>v1</h3><p>Solo menciones en los artículos → perdía vínculos reales del VISTO.</p>', delay=0.3, cls="card") + st(1, barras, cls="card")
    der = st(2, code(src, archivo="src/grafo_legal/extractores/reglas_v2.py", hl=[3, 4, 5, 6], size=19)) + st(3, proc, cls="card text", style="font-size:26px")
    return pagina(12, "Paso 5 · Reglas", "¿Es una relación o solo una cita? La regla F",
                  f'<div class="col">{izq}</div><div class="col w2">{der}</div>', burbuja="El VISTO dice mucho")


# ---------------------------------------------------------------- E13
def e13():
    tipos = [("SUSTITUYE", "«Sustitúyese el artículo 245…»", C["blue"]), ("INCORPORA", "«Incorpórase como artículo 92 bis…»", C["green"]),
             ("DEROGA", "«Derógase la Ley 25.323»", C["red"]), ("REGLAMENTA", "«Reglaméntase el artículo 179…»", C["yellow"]),
             ("MODIFICA", "«Prorrógase…», «Modifícase…»", C["violet"]), ("CITA", "«…previstas en la Ley 24.013»", C["muted"])]
    filas = "".join(st(1, f'<td><span class="tag" style="background:{c}">{t}</span></td><td class="text" style="font-size:25px">{e}</td>',
                       "left", i * 0.12, tag="tr") for i, (t, e, c) in enumerate(tipos))
    tabla = f'<table class="t">{filas}</table>'
    fila = f"""<table class="t" style="font-size:22px"><tr><th>campo</th><th>valor (relaciones_reglas_v2.csv)</th></tr>
      <tr><td>fuente</td><td class="mono">reglas_v2</td></tr><tr><td>origen</td><td class="mono">Ley 24013 · art. 25 · articulado</td></tr>
      <tr class="hi"><td>tipo</td><td class="mono">SUSTITUYE</td></tr><tr><td>destino</td><td class="mono">Ley 20744 · art. 198</td></tr>
      <tr><td>verbo</td><td class="mono">Sustituyese</td></tr><tr class="hi"><td>evidencia</td><td class="mono">caracteres 16.784 a 16.810</td></tr>
      <tr><td>fragmento</td><td style="font-size:20px">«ARTICULO 25.- Sustituyese el artículo 198, de la Ley de Contrato…»</td></tr></table>"""
    return pagina(13, "Paso 6 · Tipo y salida estándar", "Qué tipo de relación, y con qué evidencia",
                  f'<div class="col">{tabla}</div><div class="col">{st(2, "<h3>Salida estándar</h3>" + fila, cls="card")}'
                  f'{st(3, "<p>Cualquier parser escribe esta misma tabla: lo que sigue es intercambiable.</p>", cls="card")}</div>',
                  burbuja="Cada flecha con su prueba")


# ---------------------------------------------------------------- E14
def e14():
    cols = ["id_norma_origen", "id_norma_destino", "n_menciones", "n_menc_articulado", "n_menc_visto", "verbo_en_oracion",
            "tipo_origen", "dif_anios", "en_gold"]
    vals = ["412 (Ley 24.013)", "25552 (LCT)", "28", "28", "0", "1", "ley", "17", "1"]
    filas = "".join(f'<tr class="{"hi" if c == "en_gold" else ""}"><td class="mono" style="font-size:21px">{c}</td><td class="mono" style="font-size:21px">{v}</td></tr>'
                    for c, v in zip(cols, vals))
    py = code('''import pandas as pd
art   = pd.read_csv("data/dataset/articulos.csv")
pares = pd.read_csv("data/dataset/pares_candidatos.csv")
dev = pares[pares.split == "dev"]   # se entrena solo con dev''', archivo="docs/dataset.md", size=22)
    nums = f"""<div style="display:flex;gap:46px">
      {st(1, count(1, 8066) + '<div class="numlab">segmentos · articulos.csv</div>', 'fade')}
      {st(2, count(2, 1091) + '<div class="numlab">pares candidatos · 22 atributos</div>', 'fade')}</div>"""
    izq = nums + st(1, py, delay=0.3)
    der = st(3, f'<h3>Ley 24.013 → Ley 20.744</h3><table class="t">{filas}</table>', cls="card")
    return pagina(14, "Paso 7 · Datasets", "Dos tablas para entrenar y analizar", f'<div class="col">{izq}</div><div class="col">{der}</div>',
                  burbuja="¡Datos en tablas!")


# ---------------------------------------------------------------- E15
def e15():
    def tarjeta(k, titulo, desc, val, color):
        return st(k, f'<h3>{titulo}</h3><p>{desc}</p><div style="margin-top:18px">{count(k, val, dec=3, sep=False, delay=0.3, style=f"color:{color}")}</div>'
                     f'<div class="numlab">F1 en test</div>', cls="card", style="flex:1")
    fila = (tarjeta(1, "Random forest", "22 atributos de superficie: zona, verbo, tipos, años", 0.823, C["blue"]) +
            tarjeta(2, "TF-IDF del contexto", "las palabras alrededor de cada mención", 0.783, C["red"]) +
            tarjeta(0, "Reglas v2 (referencia)", "la regla F", 0.828, C["muted"]))
    return pagina(15, "Paso 8 · Modelos clásicos", "Aprender en lugar de escribir reglas",
                  f'<div class="col"><div style="display:flex;gap:30px">{fila}</div>'
                  f'{st(3, "<h3>Empate</h3><p>Con atributos de superficie no hay mucho más para ganar: hace falta entender la oración.</p>", "pop", cls="card", style="border-left:10px solid " + C["orange"])}</div>',
                  burbuja="¿Y si aprende solo?")


# ---------------------------------------------------------------- E16
def e16():
    nodos = [("Segmentos", "g"), ("Prefiltro", ""), ("Lotes", ""), ("LLM → JSON", "o"), ("¿Cita literal?", "v"), ("Normalización", "")]
    flow = '<div class="flow">' + "".join(
        st(1, n, "pop", i * 0.12, cls=f"node {c}") + (st(1, "→", "fade", i * 0.12 + 0.06, cls="arrow") if i < len(nodos) - 1 else "")
        for i, (n, c) in enumerate(nodos)) + "</div>"
    prompt = code('''SISTEMA = """Sos un analista de técnica legislativa argentina.
Para cada referencia devolvés el TIPO de relación:
- SUSTITUYE: reemplaza el texto ("Sustitúyese el artículo 80 …")
- DEROGA: deja sin efecto ("Derógase", "Déjase sin efecto")
- CITA: solo se menciona ("conforme la Ley …"). Las menciones del
  VISTO y del CONSIDERANDO son CITA salvo que se la modifique.
"cita" debe ser una copia EXACTA y corta del texto…"""''', archivo="src/grafo_legal/extractores/llm.py", hl=[7], size=19)
    resp = code('''{"segmento": "S82",
 "cita": "artículo 245 de la Ley N° 20.744 (t.o. 1976)",
 "numero": "20744", "articulo_destino": "245",
 "tipo": "SUSTITUYE", "verbo": "Sustitúyese"}''', "json", "results/relaciones_llm/cache/fd03ea83…912d.json", size=19)
    verif = f"""<div class="card"><h3>Verificación de la cita</h3>
      <div class="mono" style="font-size:21px;margin:10px 0">texto.find(cita)</div>
      <div style="font-size:24px">{st(3, '✓ «artículo 245 de la Ley N° 20.744» está en el texto', 'left', 0, style=f'color:{C["green"]}')}
      {st(3, '✗ una cita inventada → se descarta', 'left', 0.3, style=f'color:{C["red"]};text-decoration:line-through')}</div>
      {st(3, count(3, 0.1, dec=1, suf=" % de alucinación", delay=0.5, style="font-size:44px"), 'fade')}</div>"""
    cache = st(4, f'<h3>Caché por huella SHA-256</h3><p>Volver a correr no llama a la API y da lo mismo. Todo el corpus: USD 14.</p>', cls="card")
    return pagina(16, "Paso 9 · Modelo de lenguaje", "Un parser con un LLM que tiene que citar",
                  f'<div class="col">{flow}{st(2, prompt)}</div><div class="col">{st(2, resp, delay=0.3)}{verif}{cache}</div>',
                  burbuja="Entra el LLM")


# ---------------------------------------------------------------- E17
def e17():
    venn = f"""<div style="position:relative;height:250px;width:420px">
      <div style="position:absolute;left:20px;top:10px;width:230px;height:230px;border-radius:50%;background:rgba(42,120,214,.25);border:3px solid {C['blue']}"></div>
      <div style="position:absolute;left:170px;top:10px;width:230px;height:230px;border-radius:50%;background:rgba(235,104,52,.25);border:3px solid {C['orange']}"></div>
      <div style="position:absolute;left:60px;top:105px;font-size:26px;font-weight:700">Reglas</div>
      <div style="position:absolute;left:300px;top:105px;font-size:26px;font-weight:700">LLM</div>
      <div style="position:absolute;left:196px;top:110px;font-size:24px;font-weight:800">∩</div></div>"""
    izq = st(1, f'<h3>Combinar las salidas</h3>{venn}<p><b>∩</b> intersección: solo lo que encuentran los dos · <b>∪</b> unión: cualquiera de los dos</p>', cls="card")
    zonas = f"""<div style="display:flex;flex-direction:column;gap:14px">
      {st(2, '<b>Reglas:</b> encuentran, normalizan y separan en tres zonas', 'left', cls='sub', style='margin:0')}
      <div style="display:flex;gap:14px">
        {st(3, 'Descarte<br><span style="font-weight:400;font-size:20px">posterior, solo anexos</span>', 'pop', 0, cls='node g', style='flex:1')}
        {st(3, 'Seguro<br><span style="font-weight:400;font-size:20px">artículo + verbo</span>', 'pop', 0.15, cls='node v', style='flex:1')}
        {st(3, 'Zona gris<br><span style="font-weight:400;font-size:20px">todo lo demás</span>', 'pop', 0.3, cls='node y', style='flex:1')}</div>
      {st(4, f'<div style="text-align:right;margin-right:60px;font-size:40px;color:{C["muted"]}">↓</div>', 'fade')}
      {st(4, 'El LLM decide solo la zona gris<br><span style="font-weight:400;font-size:21px">con la opinión de la regla como punto de partida: umbrales 0,15 y 0,5</span>', 'pop', 0.2, cls='node o')}
      {st(5, '<h3>A un cuarto del costo del LLM puro</h3>', 'up', cls='card')}</div>"""
    return pagina(17, "Paso 10 · Híbridos", "Cada uno hace lo que mejor sabe",
                  f'<div class="col">{izq}</div><div class="col w2">{st(2, "<h3 style='font-size:32px'>Híbrido en cascada</h3>", cls="")}{zonas}</div>',
                  burbuja="¡Trabajo en equipo!")


# ---------------------------------------------------------------- E18
def e18():
    modelo = code('''(:Norma)-[:CONTIENE]->(:Articulo)
(:Articulo)-[:SUSTITUYE|DEROGA|…|CITA]->(:Articulo|:Norma)

MERGE (o)-[r:SUSTITUYE {fuente: f.fuente}]->(d)
SET r.verbo = f.verbo, r.inicio = f.inicio, r.fin = f.fin,
    r.fragmento = f.fragmento''', "cypher", "src/grafo_legal/grafo.py", hl=[4, 5, 6], size=19)
    consulta = code('''MATCH (o:Articulo)-[r]->(d) WHERE o.id = '395521#71'
RETURN r.fuente, type(r), d.id, r.fragmento''', "cypher", "Neo4j Browser · dos lecturas del mismo artículo", size=19)
    res = """<table class="t" style="font-size:21px"><tr><th>r.fuente</th><th>type(r)</th><th>destino</th><th>r.verbo</th></tr>
      <tr class="hi"><td class="mono">reglas_v2</td><td class="mono">SUSTITUYE</td><td class="mono">LCT art. 80</td><td class="mono">Sustitúyese</td></tr>
      <tr><td class="mono">reglas_v2</td><td class="mono">CITA</td><td class="mono">LCT art. 80</td><td></td></tr>
      <tr class="hi"><td class="mono">llm</td><td class="mono">SUSTITUYE</td><td class="mono">LCT art. 80</td><td class="mono">Sustitúyese</td></tr>
      <tr><td class="mono">llm</td><td class="mono">CITA</td><td class="mono">LCT art. 80</td><td></td></tr></table>"""
    ida = f"""<div style="display:flex;gap:30px;align-items:center">{count(4, 3277)}<div style="font-size:40px">=</div>{count(4, 3277, delay=0.3)}</div>
      <div class="numlab">relaciones cargadas = relaciones leídas de vuelta</div>"""
    der = st(1, img(str(ASSETS / "grafo_corpus_claro.png"), extra="shot"), "zoom")
    izq = st(1, modelo, delay=0.2) + st(2, consulta) + st(3, res) + st(4, ida, cls="card")
    return pagina(18, "Paso 11 · Grafo", "El grafo en Neo4j", f'<div class="col w2">{izq}</div><div class="col">{der}</div>',
                  burbuja="¡Todo conectado!")


# ---------------------------------------------------------------- E19
def e19():
    form = f"""<div class="card" style="font-size:34px;line-height:1.9">
      {st(1, f'<b style="color:{C["blue"]}">Precisión</b> = lo correcto / lo encontrado', 'left')}
      {st(1, f'<b style="color:{C["orange"]}">Recall</b> = lo correcto / lo que había', 'left', 0.25)}
      {st(1, f'<b style="color:{C["green"]}">F1</b> = 2·P·R / (P + R)', 'left', 0.5)}</div>"""
    # campana del bootstrap de la diferencia reglas ∩ LLM − reglas: IC 95 % [+0,2; +2,5]
    import math
    pts = []
    for i in range(0, 121):
        x = -1.5 + i * 0.04
        y = math.exp(-((x - 1.0) ** 2) / (2 * 0.6 ** 2))
        pts.append(f"{60 + (x + 1.5) * 150:.1f},{230 - y * 190:.1f}")
    x0 = 60 + 1.5 * 150
    svg = f"""<svg width="820" height="290" viewBox="0 0 820 290">
      <polyline points="{' '.join(pts)}" fill="rgba(42,120,214,.18)" stroke="{C['blue']}" stroke-width="4"/>
      <line x1="{x0}" y1="20" x2="{x0}" y2="240" stroke="{C['ink']}" stroke-width="3" stroke-dasharray="8 6"/>
      <text x="{x0 - 14}" y="268" font-size="22" text-anchor="end" fill="{C['muted']}">0</text>
      <line x1="{60 + 1.7 * 150}" y1="244" x2="{60 + 4.0 * 150}" y2="244" stroke="{C['orange']}" stroke-width="10"/>
      <text x="{60 + 2.85 * 150}" y="282" font-size="22" text-anchor="middle" fill="{C['ink']}">IC 95 %: +0,2 a +2,5 puntos</text></svg>"""
    der = st(2, f'<h3>Bootstrap: 2.000 remuestras de normas <span style="font-weight:400;color:#6b6a64;font-size:22px">(esquema)</span></h3>{svg}<p>Diferencia reglas ∩ LLM − reglas. No toca el cero: la mejora es real.</p>', cls="card")
    return pagina(19, "Paso 12 · Evaluación", "Cómo medimos, y cuándo una mejora es real",
                  f'<div class="col">{form}{st(2, "<p>192 pares de prueba: un punto de diferencia puede ser casualidad.</p>", cls="card")}</div><div class="col w2">{der}</div>',
                  burbuja="Medir bien es clave")


# ---------------------------------------------------------------- E20
def e20():
    fig = st(1, img(str(FIG / "fig3_metodos.png")), "zoom")
    def tarjeta(k, titulo, cuerpo, borde=""):
        return st(k, f'<div style="font-size:24px;font-weight:700;margin-bottom:4px">{titulo}</div>{cuerpo}', cls='card',
                  style=f'padding:14px 22px;{borde}')
    n = lambda k, v, color="", d=0.0: count(k, v, dec=3, sep=False, delay=d, style=f"font-size:52px;{color}")
    tarjetas = f"""<div style="display:flex;flex-direction:column;gap:12px">
      {tarjeta(2, 'Reglas v2', n(2, 0.828) + '<div class="numlab" style="margin-top:2px">F1 en test</div>')}
      {tarjeta(3, 'LLM', n(3, 0.841) + '<div class="numlab" style="margin-top:2px">recall 0,938: encuentra el 94 %</div>')}
      {tarjeta(4, 'Reglas ∩ LLM', n(4, 0.838, f"color:{C['orange']}") + '<div class="numlab" style="margin-top:2px">+1 punto, la única mejora significativa</div>', f"border-left:10px solid {C['orange']}")}
      {tarjeta(5, 'Tipo de relación (macro-F1)', f'<div style="display:flex;align-items:baseline;gap:14px">{n(5, 0.672, "color:" + C["muted"])}<span style="font-size:34px">→</span>{n(5, 0.883, "", 0.4)}</div>')}</div>"""
    return pagina(20, "Resultados", "Todos los métodos, sobre la misma prueba", f'<div class="col w2">{fig}</div><div class="col" style="max-width:560px">{tarjetas}</div>',
                  burbuja="¡Llegaron los números!")


# ---------------------------------------------------------------- E21
def e21():
    return pagina(21, "Resultados", "Dónde se pierde, y por qué",
                  f'<div class="col">{st(1, img(str(FIG / "fig2_embudo.png")), "zoom")}{st(3, img(str(FIG / "fig4_tipos.png")), "zoom")}</div>'
                  f'<div class="col">{st(2, img(str(FIG / "fig5_errores.png")), "zoom")}'
                  f'{st(2, "<h3>Lo difícil es decidir</h3><p>Casi nada se pierde detectando o normalizando. La mitad de los falsos positivos son citas del VISTO.</p>", delay=0.4, cls="card", style="padding:16px 24px")}'
                  f'{st(3, "<h3>Tipos</h3><p>Las reglas toman una mención como acción («la derogación del artículo 2»). El LLM casi no.</p>", delay=0.4, cls="card", style="padding:16px 24px")}</div>',
                  burbuja="Error por error")


# ---------------------------------------------------------------- E22
def e22():
    flow = f"""<div class="flow">{st(1, 'PDF del digesto', 'pop', 0, cls='node o')}{st(1, '→', 'fade', 0.1, cls='arrow')}
      {st(1, 'pdftotext / OCR', 'pop', 0.15, cls='node o')}{st(1, '→', 'fade', 0.25, cls='arrow')}
      {st(1, 'fuentes/unnoba.py', 'pop', 0.3, cls='node o')}{st(1, '→', 'fade', 0.4, cls='arrow')}
      {st(1, 'reglas · LLM · híbrido<br><span style="font-weight:400;font-size:20px">sin tocar</span>', 'pop', 0.45, cls='node')}</div>"""
    ej = st(1, f'{mk(1, "Resolución (CS) Nro. 44/08", "o", 0.6)} · {mk(1, "Ordenanza (CS) 14/09", "o", 0.8)} · {mk(1, "Res. (CD.ET) 64/2013", "o", 1.0)}',
            cls="card text", style="font-size:27px")
    fig = st(2, img(str(FIG / "fig6_pi4.png")), "zoom")
    salto = st(3, f'<h3>El vocabulario importa</h3><div style="display:flex;align-items:baseline;gap:18px">{count(3, 0.405, dec=3, sep=False, style=f"color:{C["red"]};font-size:58px")}'
                  f'<span style="font-size:40px">→</span>{count(3, 0.864, dec=3, sep=False, delay=0.4, style="font-size:58px")}</div>'
                  f'<p>LLM con tres frases nuevas sobre resoluciones y ordenanzas.</p>', cls="card")
    return pagina(22, "Extensión · PI4", "El mismo pipeline sobre el digesto de la UNNOBA",
                  f'<div class="col">{flow}{ej}{salto}</div><div class="col w2">{fig}</div>', burbuja="¡Nuestra universidad!")


# ---------------------------------------------------------------- E23
def e23():
    versiones = [("t.o. 1976", "Decreto 390/76", C["muted"]), ("1989", "Ley 23.697", C["blue"]), ("1991", "Ley 24.013", C["blue"]),
                 ("2004", "Ley 25.877", C["blue"]), ("2023", "DNU 70/2023", C["blue"]), ("2026", "Ley 27.802", C["orange"])]
    linea = '<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;row-gap:12px">' + "".join(
        st(2, f'<div style="font-size:20px;color:{C["muted"]}">{a}</div><div style="font-size:23px;font-weight:700;color:{c}">{n}</div>', "pop", i * 0.2,
           cls="card", style="padding:12px 14px;text-align:center") + (st(2, "→", "fade", i * 0.2 + 0.1, cls="arrow") if i < len(versiones) - 1 else "")
        for i, (a, n, c) in enumerate(versiones)) + "</div>"
    rank = f"""<table class="t"><tr><th>Ley (fuente: híbrido)</th><th>Modificatorias</th><th>Profundidad</th></tr>
      <tr class="hi"><td>Ley 20.744 (LCT)</td><td>{count(1, 105, cls='', style='font-weight:700')}</td><td>{count(1, 16, cls='', style='font-weight:700')}</td></tr>
      <tr><td>Ley 24.013</td><td>81</td><td>14</td></tr><tr><td>Ley 24.241</td><td>62</td><td>10</td></tr></table>"""
    izq = st(1, rank) + st(2, "<h3>Artículo 245 · indemnización por despido</h3>", cls="") + linea
    der = st(3, img(str(FIG / "fig7_consolidado.png")), "zoom") + st(4, f'<div style="display:flex;align-items:baseline;gap:14px">{count(4, 281)}<span style="font-size:40px;color:{C["muted"]}">/ 293</span></div><div class="numlab">artículos iguales a InfoLEG (95,9 %)</div>', cls="card")
    return pagina(23, "Extensión · PI5", "Reconstruir la ley vigente solo con el grafo", f'<div class="col w2">{izq}</div><div class="col">{der}</div>',
                  burbuja="¡La LCT, armada sola!")


# ---------------------------------------------------------------- E24
def e24():
    pis = [("PI1", "Reglas 0,83 · LLM 0,84: el techo es la tarea, no el método"),
           ("PI2", "Reglas ∩ LLM: +1 punto, la única mejora significativa"),
           ("PI3", "El error está en decidir: citas del VISTO, remisiones, decretos sin verbo"),
           ("PI4", "Se transfiere al digesto si el adaptador conoce su vocabulario"),
           ("PI5", "Evidencia en cada arista: ida y vuelta idéntica y la LCT consolidada al 96 %")]
    cards = "".join(st(i + 1, f'<span class="tag" style="background:{C["fusi"]};margin-right:16px">{p}</span>{t}', "left",
                       cls="card", style="font-size:30px;padding:20px 26px") for i, (p, t) in enumerate(pis))
    return pagina(24, "Conclusiones", "Lo que aprendimos", f'<div class="col">{cards}</div>', burbuja="¡Lo logramos!")


# ---------------------------------------------------------------- E25
def e25():
    sig = ["Validación humana y segundo anotador (kappa)", "Muestra independiente del gold",
           "Comparar modelos de lenguaje", "Consultas en lenguaje natural sobre el grafo (text-to-Cypher)"]
    fin = f"""<div style="display:flex;align-items:center;gap:40px;margin-top:10px">
      {st(5, f'<img src="file://{FUSI}/fusi_feliz.png" style="width:190px;image-rendering:pixelated">', 'pop')}
      {st(5, '<div style="font-size:44px;font-weight:800">¡Gracias por ver!</div><div class="mono" style="font-size:28px;color:#2a78d6;margin-top:10px">github.com/JuampiJPT/grafo-legal</div><div class="numlab">código · datos · bitácora · informe</div>', 'up', 0.2)}</div>"""
    return pagina(25, "Lo que sigue", "Para el examen final", f'<div class="col">{bullets(sig)}{fin}</div>', burbuja="¡Hasta la próxima!")


ESCENAS = [e01, e02, e03, e04, e05, e06, e07, e08, e09, e10, e11, e12, e13, e14, e15, e16, e17, e18, e19, e20, e21, e22, e23, e24, e25]
