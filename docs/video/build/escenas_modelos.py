"""Escenas E15 a E15g: los modelos supervisados (bitácora B69).

Reemplazan la escena E15 original. Todas usan el segmento 15 de la barra de progreso. Cada cifra sale de
los resultados del repositorio:
  - results/clasificador/ (random forest, CV y test), results/modelo_contextual/ (TF-IDF),
  - results/curva_aprendizaje/ (B68),
  - el árbol 0 del random forest y los pesos de la regresión logística se obtuvieron reentrenando con
    todo dev, con las mismas semillas que los scripts 08 y 13.
"""
from base import C, FIG, bar, code, count, esc, img, mk, pagina, st

SEG = 15   # segmento de la barra de progreso


def flecha(k, delay=0.0):
    return st(k, "→", "fade", delay, cls="arrow")


# ---------------------------------------------------------------- E15 · aprender de ejemplos
def e15():
    flujo = f"""<div class="flow" style="gap:16px">
      {st(1, 'Par candidato<br><span style="font-weight:400;font-size:20px">norma A menciona a B</span>', 'pop', 0, cls='node g')}{flecha(1, .1)}
      {st(1, 'Atributos<br><span style="font-weight:400;font-size:20px">o texto</span>', 'pop', .15, cls='node')}{flecha(1, .25)}
      {st(1, 'Modelo', 'pop', .3, cls='node o')}{flecha(1, .4)}
      {st(1, '¿Relación?<br><span style="font-weight:400;font-size:20px">1 sí · 0 no</span>', 'pop', .45, cls='node v')}</div>"""
    ejemplo = st(2, f"""<h3>Un ejemplo con su respuesta</h3>
      <table class="t"><tr><td>Origen</td><td>Ley 24.013 (Empleo)</td></tr>
      <tr><td>Destino</td><td>Ley 20.744 (LCT)</td></tr>
      <tr><td>Menciones</td><td>28, todas en el articulado</td></tr>
      <tr class="hi"><td>en_gold (InfoLEG)</td><td>1 · la relación existe</td></tr></table>""", cls="card")
    nums = f"""<div style="display:flex;gap:40px;align-items:flex-end">
      <div>{count(3, 801)}<div class="numlab">pares de desarrollo</div></div>
      <div>{count(3, 230, delay=.15, style=f'color:{C["muted"]}')}<div class="numlab">normas de origen</div></div></div>
      <div style="margin-top:22px;display:flex;flex-direction:column;gap:10px">
      <div style="display:flex;align-items:center;gap:14px">{bar(3, 472, C['green'], .3)}<span style="font-size:26px">472 relaciones reales</span></div>
      <div style="display:flex;align-items:center;gap:14px">{bar(3, 329, C['red'], .4)}<span style="font-size:26px">329 citas al pasar</span></div></div>"""
    llm = st(4, '<h3>¿Y el modelo de lenguaje?</h3><p>No se entrena: solo se le dan instrucciones en el prompt.</p>', 'pop',
             cls='card', style=f'border-left:10px solid {C["orange"]}')
    cuerpo = (f'<div class="col w2">{st(1, flujo)}{ejemplo}</div>'
              f'<div class="col">{st(3, nums, cls="card")}{llm}</div>')
    return pagina(SEG, "Paso 8 · Aprendizaje supervisado", "Aprender de ejemplos", cuerpo, burbuja="¿Y si aprende solo?")


# ---------------------------------------------------------------- E15b · random forest
def e15b():
    def nodo(k, txt, cls="", d=0.0):
        return st(k, txt, "pop", d, cls=f"node {cls}", style="font-size:22px;padding:12px 16px")

    def rama(k, txt, d=0.0):
        return st(k, txt, "fade", d, style=f"font-size:19px;color:{C['muted']};text-align:center")

    arbol = f"""<div style="display:flex;flex-direction:column;align-items:center;gap:10px">
      {nodo(1, '¿Se la menciona en el VISTO?', 'o')}
      <div style="display:flex;gap:40px;width:100%;justify-content:center">
        <div style="display:flex;flex-direction:column;align-items:center;gap:8px;flex:1">{rama(2, 'no')}
          {nodo(2, '¿El origen es un decreto?', '', .1)}
          <div style="display:flex;gap:12px">{rama(3, 'no')}{nodo(3, '¿Menciones ≤ 4?', 'g', .1)}{rama(3, 'sí', .1)}{nodo(3, '¿Menciones ≤ 2?', 'g', .2)}</div></div>
        <div style="display:flex;flex-direction:column;align-items:center;gap:8px;flex:1">{rama(2, 'sí', .2)}
          {nodo(2, '¿El destino es un decreto?', '', .3)}
          <div style="display:flex;gap:12px">{rama(3, 'no', .2)}{nodo(3, '¿Menciones ≤ 1?', 'g', .3)}{rama(3, 'sí', .3)}{nodo(3, '¿Fracción de artículos ≤ 0,09?', 'g', .4)}</div></div>
      </div>{rama(3, '… y sigue hasta 15 niveles: memoriza los datos', .5)}</div>"""
    izq = st(1, '<h3 style="margin-bottom:14px">Árbol 0 del bosque, tal cual lo aprendió</h3>' + arbol, cls="card")
    arboles = "".join(f'<span style="display:inline-block;width:0;height:0;border-left:9px solid transparent;'
                      f'border-right:7px solid transparent;border-bottom:17px solid {C["green"]};'
                      f'margin:2px"></span>' for i in range(400))
    bosque = st(4, f'<h3>400 árboles, cada uno con otra muestra</h3><div style="line-height:0;margin-top:8px">{arboles}</div>'
                   f'<p style="margin-top:10px">Cada árbol ve una muestra distinta de los pares y, en cada pregunta, solo algunos atributos.</p>',
                cls="card")
    voto = st(5, f"""<h3>Decreto 70/2023 → Ley 20.744</h3>
      <div style="display:flex;align-items:baseline;gap:20px;margin-top:6px">{count(5, 0.70, dec=2, sep=False, style=f'color:{C["green"]}')}
      <span style="font-size:26px;color:{C['muted']}">promedio de los 400 votos</span></div>
      <div style="position:relative;width:700px;height:30px;background:{C['line']};border-radius:6px;margin-top:16px">
        {bar(5, 490, C['green'], .2, h=30)}
        <div style="position:absolute;left:315px;top:-10px;bottom:-10px;width:4px;background:{C['ink']}"></div>
        <div style="position:absolute;left:280px;top:36px;font-size:20px">umbral 0,45</div></div>
      <p style="margin-top:44px">0,70 &gt; 0,45 → <b style="color:{C['green']}">hay relación</b> · y está en InfoLEG ✓</p>""", "pop", cls="card")
    return pagina(SEG, "Modelo 1 · Random forest", "Muchos árboles que votan",
                  f'<div class="col w2">{izq}{voto}</div><div class="col">{bosque}</div>', burbuja="¡Un bosque entero!")


# ---------------------------------------------------------------- E15c · TF-IDF + regresión logística
def e15c():
    original = st(1, '<div class="numlab" style="margin:0 0 8px">Texto original · Ley 23.697, art. 48</div>'
                     '<div class="text" style="font-size:27px">Art. 48.- Sustitúyese el artículo 245 del régimen de contrato de '
                     'trabajo aprobado por la ley Nº 20.744 (t.o. 1976). por el siguiente: …</div>', cls="card")
    limpio = st(2, '<div class="numlab" style="margin:0 0 8px">Lo que lee el modelo</div><div class="text mono" style="font-size:23px;line-height:1.6">'
                   f'{mk(2, "PARTE_articulado", "o")} Art. {mk(2, "##", "b", .15)}.- Sustitúyese el artículo {mk(2, "###", "b", .2)} '
                   f'del régimen de contrato de trabajo aprobado por la {mk(2, "DESTINO", "g", .3)} (t.o. {mk(2, "####", "b", .35)}). por el siguiente: …</div>',
                cls="card")
    vector = st(3, f"""<div style="display:flex;align-items:center;gap:24px">{count(3, 10804)}
      <div style="font-size:26px;line-height:1.35">columnas TF-IDF<br><span style="color:{C['muted']}">palabras y pares de palabras,<br>pesadas por qué tan raras son</span></div></div>""",
                cls="card")
    pos = [("parte_articulado articulo", 4.05), ("la destino", 3.45), ("decreto", 3.39), ("siguiente", 2.85), ("el articulo", 2.42)]
    neg = [("el destino", -2.72), ("por destino", -2.05), ("reemplazado por", -1.73), ("derogado", -1.58), ("concordantes", -1.46)]

    def fila(k, t, v, d, color, raro=False):
        w = int(abs(v) * 70)
        estilo = f"background:#fff3ec;border-radius:8px" if raro else ""
        return st(k, f'<div style="display:flex;align-items:center;gap:12px;margin:5px 0;{estilo}"><span class="mono" style="width:330px;text-align:right;font-size:21px">{esc(t)}</span>'
                     f'{bar(k, w, color, d, h=26)}<span class="mono" style="font-size:20px">{v:+.2f}</span></div>', "fade", d)
    pesos = (st(4, '<h3>Pesos reales de la regresión logística</h3>', cls="") +
             "".join(fila(4, t, v, .08 * i, C["green"]) for i, (t, v) in enumerate(pos)) +
             st(4, f'<div style="height:2px;background:{C["line"]};margin:8px 0"></div>', "fade", .45) +
             "".join(fila(4, t, v, .5 + .08 * i, C["red"]) for i, (t, v) in enumerate(neg)) +
             fila(5, "bs as («Bs. As.»)", 2.34, 0, C["yellow"], raro=True) +
             st(5, f'<p style="font-size:24px;color:{C["muted"]};margin-top:6px">Un rasgo sin sentido: memoriza el formato.</p>', "fade", .2))
    return pagina(SEG, "Modelo 2 · TF-IDF + regresión logística", "Leer el contexto de cada mención",
                  f'<div class="col">{original}{limpio}{vector}</div><div class="col">{st(4, pesos, cls="card")}</div>',
                  burbuja="¡Ahora lee!")


# ---------------------------------------------------------------- E15d · entrenar sin hacer trampa
def e15d():
    linea = f"""<div style="display:flex;height:64px;border-radius:12px;overflow:hidden;font-size:24px;font-weight:700;color:white">
      <div style="flex:801;background:{C['blue']};display:flex;align-items:center;justify-content:center">Desarrollo · hasta 2019 · 801 pares</div>
      <div style="flex:290;background:{C['orange']};display:flex;align-items:center;justify-content:center">Test · 290</div></div>
      <p style="margin-top:12px">El test se usa <b>una sola vez</b>, al final.</p>"""
    colores = [C["blue"], C["green"], C["violet"], C["yellow"], "#a5a49d"]
    filas = ""
    for f in range(5):
        celdas = "".join(f'<div style="flex:1;height:34px;border-radius:5px;background:{C["orange"] if j == f else colores[j]};'
                         f'opacity:{1 if j == f else .35}"></div>' for j in range(5))
        filas += st(2, f'<div style="display:flex;gap:6px;align-items:center"><span style="width:110px;font-size:20px">vuelta {f + 1}</span>{celdas}</div>',
                    "left", .08 * f)
    cv = st(2, f'<h3>Validación cruzada en 5 partes</h3><div style="display:flex;flex-direction:column;gap:8px;margin-top:6px">{filas}</div>'
               f'<p style="margin-top:10px"><span style="color:{C["orange"]};font-weight:700">■</span> valida · el resto entrena</p>', cls="card")
    grupo = st(3, '<h3>Agrupada por norma</h3><p>Todos los pares de una misma norma quedan del mismo lado. '
                  'Si no, el modelo reconocería la norma y el resultado saldría inflado.</p>', "pop", cls="card",
               style=f"border-left:10px solid {C['green']}")
    tabla = st(4, f"""<h3>Qué se eligió, solo con desarrollo</h3><table class="t">
      <tr><th>Modelo</th><th>Umbral</th><th>F1 en CV</th></tr>
      <tr><td>Regresión logística</td><td>0,35</td><td>0,718</td></tr>
      <tr class="hi"><td>Random forest</td><td>0,45</td><td>0,728</td></tr>
      <tr><td>Gradient boosting</td><td>0,20</td><td>0,709</td></tr></table>
      <p style="font-size:22px;margin-top:8px">Umbrales probados: de 0,20 a 0,80</p>""", cls="card")
    final = st(5, f'<div class="flow" style="justify-content:center">{st(5, "Reentrenar con todo desarrollo", "pop", 0, cls="node")}'
                  f'{flecha(5, .15)}{st(5, "Medir en test, una vez", "pop", .3, cls="node o")}</div>', "fade")
    return pagina(SEG, "Cómo entrenamos", "Entrenar sin hacer trampa",
                  f'<div class="col">{st(1, linea, cls="card")}{cv}</div><div class="col">{grupo}{tabla}{final}</div>',
                  burbuja="¡Sin espiar el test!")


# ---------------------------------------------------------------- E15e · resultados
def e15e():
    filas = [(1, "Reglas v2 (referencia)", 0.828, C["muted"]), (1, "Random forest", 0.823, C["blue"]),
             (2, "TF-IDF solo", 0.761, C["red"]), (2, "TF-IDF + atributos", 0.783, C["red"]),
             (3, "Híbrido: reglas + TF-IDF en la zona gris", 0.839, C["green"])]
    escala = lambda v: int((v - 0.70) / 0.15 * 760)   # noqa: E731  eje de 0,70 a 0,85
    barras = "".join(st(k, f'<div style="display:flex;align-items:center;gap:16px"><span style="width:520px;font-size:26px">{t}</span>'
                           f'{bar(k, escala(v), c, .1 * i)}<span style="font-size:28px;font-weight:800">{str(v).replace(".", ",")}</span></div>',
                        "fade", .1 * i) for i, (k, t, v, c) in enumerate(filas))
    nota = st(1, f'<div style="font-size:21px;color:{C["muted"]};margin-left:536px">F1 en test (192 relaciones) · el eje empieza en 0,70</div>', "fade")
    cierre = st(4, '<h3>Empate con las reglas</h3><p>El híbrido mejora 1 punto, pero no es significativo. '
                   '¿Al modelo le faltaba entender, o le faltaban datos?</p>', "pop", cls="card",
                style=f"border-left:10px solid {C['orange']}")
    return pagina(SEG, "Resultados de los modelos", "¿Qué tal les fue?",
                  f'<div class="col"><div class="card" style="display:flex;flex-direction:column;gap:16px">{barras}{nota}</div>{cierre}</div>',
                  burbuja="¡A ver los números!")


# ---------------------------------------------------------------- E15f · curva de aprendizaje
def e15f():
    fig = st(1, img(str(FIG / "fig8_curva_aprendizaje.png"), cap="results/curva_aprendizaje · validación cruzada agrupada, solo desarrollo"), "zoom")
    regla = st(2, f"""<div style="display:flex;gap:18px">
      <div class="card" style="flex:1"><h3>Si se aplana</h3><p>al modelo le falta entender</p></div>
      <div class="card" style="flex:1;border:3px solid {C['green']}"><h3>Si sigue subiendo</h3><p>le faltan datos</p></div></div>""")
    sube = st(3, f'<div style="display:flex;align-items:baseline;gap:16px">{count(3, 2, pre="+", style=f"color:{C["green"]}")}'
                 f'<span style="font-size:28px">puntos de F1 cada vez que se duplican los datos</span></div>', cls="card")
    memo = st(4, f"""<h3>Memorizan</h3><div style="display:flex;gap:30px;margin-top:6px">
      <div>{count(4, 0.94, dec=2, sep=False, style='font-size:58px')}<div class="numlab">con lo que ya vio</div></div>
      <div>{count(4, 0.81, dec=2, sep=False, style=f'font-size:58px;color:{C["orange"]}')}<div class="numlab">con datos nuevos</div></div></div>""",
               cls="card")
    usado = st(5, f'<div style="display:flex;align-items:baseline;gap:16px">{count(5, 1.5, dec=1, suf=" %", sep=False, style=f"color:{C["orange"]};white-space:nowrap")}'
                  f'<span style="font-size:26px">de las normas que InfoLEG podía etiquetar</span></div>', cls="card")
    return pagina(SEG, "¿Faltaban datos?", "La curva de aprendizaje",
                  f'<div class="col w2">{fig}{regla}</div><div class="col">{sube}{memo}{usado}</div>', burbuja="¡Sigue subiendo!")


# ---------------------------------------------------------------- E15g · qué haría falta
def e15g():
    datos = st(1, f"""<h3>Más datos</h3><div style="display:flex;gap:40px;align-items:flex-end;margin-top:8px">
      <div>{count(1, 775, style=f'color:{C["muted"]}')}<div class="numlab">relaciones que usamos</div></div>
      <div>{count(1, 37248, delay=.2)}<div class="numlab">relaciones entre leyes y decretos con texto en InfoLEG</div></div></div>""", cls="card")
    camino = f"""<div class="flow" style="gap:14px">
      {st(2, 'Ampliar el corpus', 'pop', 0, cls='node')}{flecha(2, .1)}{st(2, 'Repetir la curva', 'pop', .2, cls='node')}{flecha(2, .3)}
      {st(3, '¿Sigue subiendo? → más datos', 'pop', 0, cls='node v')}
      {st(4, '¿Se aplana? → modelo de lenguaje en español con la mención marcada', 'pop', 0, cls='node o')}</div>"""
    concl = st(5, '<h3>La conclusión cambia</h3><p style="font-size:30px">El empate no prueba que aprender no sirva: '
                  'prueba que con 800 ejemplos todavía no alcanza.</p>', "pop", cls="card",
               style=f"border-left:10px solid {C['fusi']}")
    return pagina(SEG, "Lo que habría que hacer", "Cómo podrían mejorar", f'<div class="col">{datos}{camino}{concl}</div>',
                  burbuja="¡Más ejemplos!")


MODELOS = [("E15", e15), ("E15b", e15b), ("E15c", e15c), ("E15d", e15d), ("E15e", e15e), ("E15f", e15f), ("E15g", e15g)]
