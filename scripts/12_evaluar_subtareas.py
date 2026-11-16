"""
12_evaluar_subtareas.py
Evaluacion por subtareas, como pide la consigna: deteccion, normalizacion y extraccion por
separado, y clasificacion de errores con las categorias de la consigna.

El parser es una cadena de tres pasos. Un par del gold puede perderse en cualquiera de ellos, y
la metrica final (P/R/F1 por par) no dice en cual. Este script mide cada eslabon por separado:

  1. DETECCION      ¿el detector encontro la mencion a la norma en el texto?
                    Referencia independiente del detector: una busqueda "laxa" del numero de la
                    norma destino ("20.744" o "20744" como numero suelto) y de sus nombres propios.
                    Si el numero aparece y el detector no lo vio, es un fallo de deteccion.
  2. NORMALIZACION  ¿la mencion detectada se vinculo a la norma correcta?
                    Se resuelve cada mencion contra dos catalogos: el del corpus (el que usa el
                    parser, mundo cerrado) y el catalogo completo de InfoLEG (~430 mil normas).
                    De ahi salen: resueltas, fuera del corpus, ambiguas y no encontradas.
  3. EXTRACCION     dado que la mencion se detecto y se normalizo, ¿la regla decide bien si hay
                    relacion? Se mide sobre los pares candidatos (los que tienen al menos una
                    mencion resuelta), aislando la decision de las reglas de los pasos previos.

El gold se usa solo para medir, nunca como entrada del parser.

Salidas en results/subtareas/:
  metricas.json        metricas de cada subtarea, embudo de perdidas y taxonomia de errores
  menciones.csv        todas las menciones detectadas, con su estado de normalizacion
  errores.csv          cada FN y FP de la configuracion F con su categoria de la consigna
  deteccion_fallos.csv pares donde el numero aparece en el texto pero el detector no lo vio

Uso:
    python scripts/12_evaluar_subtareas.py            # usa data/raw/base.zip
"""

import argparse
import csv
import io
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from grafo_legal.archivos import abrir_para_escribir, escribir_texto      # noqa: E402
from grafo_legal.catalogo import ALIAS, Catalogo, Norma, norm_numero, tipo_canonico, sin_tildes  # noqa: E402
from grafo_legal.evaluacion import cargar_gold, prf                         # noqa: E402
from grafo_legal.extractores import reglas_v2                               # noqa: E402
from grafo_legal.extractores.menciones import detectar, detectar_alias      # noqa: E402
from grafo_legal.fuentes.infoleg import cargar                              # noqa: E402

CONFIG = "F_visto_o_articulado_con_verbo_o_ley"
# parser evaluado: v2 (por defecto) o v3 (--parser v3). Se fija antes de main().
PARSER = {"modulo": reglas_v2, "config": CONFIG, "anio_por_fecha": False, "alias": None}
TIPOS_BASE = {"Ley", "Decreto", "Decreto/Ley"}


# --------------------------------------------------------------------------------------------
# Catalogo completo de InfoLEG (para medir la normalizacion fuera del mundo cerrado)
# --------------------------------------------------------------------------------------------
def catalogo_completo(base_zip: Path) -> Catalogo:
    """Arma un Catalogo con todas las leyes, decretos y decretos-leyes de la base de InfoLEG."""
    normas = []
    with zipfile.ZipFile(base_zip) as z:
        nombre = next(n for n in z.namelist() if n.endswith(".csv"))
        with z.open(nombre) as fb:
            for r in csv.DictReader(io.TextIOWrapper(fb, encoding="utf-8", errors="replace")):
                if r["tipo_norma"] not in TIPOS_BASE:
                    continue
                fecha = r["fecha_sancion"] or r["fecha_boletin"]
                normas.append(Norma(
                    id=int(r["id_norma"]), tipo=tipo_canonico(r["tipo_norma"]),
                    numero=norm_numero(r["numero_norma"]),
                    anio=int(fecha[:4]) if fecha[:4].isdigit() else None,
                    fecha=r["fecha_boletin"] or r["fecha_sancion"],
                    etiqueta=f"{r['tipo_norma']} {r['numero_norma']}"))
    return Catalogo(normas)


# --------------------------------------------------------------------------------------------
# 2. Normalizacion: estado de cada mencion
# --------------------------------------------------------------------------------------------
def estado_normalizacion(m, cat: Catalogo, completo: Catalogo, origen: Norma | None = None
                         ) -> tuple[str, int | None, int]:
    """Clasifica una mencion por numero en uno de estos estados:

      resuelta              el corpus tiene una sola norma compatible y el catalogo completo
                            tambien, o tiene varias pero solo una es anterior a la norma que cita
                            (la vinculacion es inequivoca)
      resuelta_mundo_cerrado  el corpus tiene una sola, pero InfoLEG tiene varias (tipicamente un
                            decreto citado sin ano): el parser acierta solo porque el corpus es chico
      fuera_del_corpus      no esta en el corpus pero si (una sola) en InfoLEG: destino ausente
      ambigua               no resuelve en el corpus y en InfoLEG tiene varias candidatas
      no_encontrada         no existe en ninguno de los dos catalogos (error de OCR, norma
                            provincial, numero mal leido)
    Devuelve (estado, id resuelto en el corpus o None, cantidad de candidatos en InfoLEG).
    """
    en_corpus = cat.resolver(m.tipo, m.numero, m.anio)
    cands = completo.candidatos(m.tipo, m.numero, m.anio)
    # un decreto-ley de facto puede estar catalogado como Ley (ver Catalogo.resolver)
    if not cands and tipo_canonico(m.tipo) == "decreto/ley":
        cands = completo.candidatos("ley", m.numero, None)
    if en_corpus is not None:
        if len(cands) <= 1:
            return "resuelta", en_corpus.id, len(cands)
        # varias candidatas en InfoLEG: si solo una es anterior a la norma que cita, la eleccion del
        # corpus es la unica posible (una norma no puede citar a otra que todavia no existe)
        previas = [c for c in cands if origen is None or not (c.fecha and origen.fecha and c.fecha > origen.fecha)]
        if len(previas) == 1 and previas[0].id == en_corpus.id:
            return "resuelta", en_corpus.id, len(cands)
        return "resuelta_mundo_cerrado", en_corpus.id, len(cands)
    if len(cands) == 1:
        return "fuera_del_corpus", None, 1
    if len(cands) > 1:
        return "ambigua", None, len(cands)
    return "no_encontrada", None, 0


# --------------------------------------------------------------------------------------------
# 1. Deteccion: busqueda laxa, independiente del detector
# --------------------------------------------------------------------------------------------
def patron_laxo(numero: str) -> re.Pattern:
    """'20744' -> encuentra '20.744' o '20744' como numero suelto (no dentro de otro numero)."""
    n = norm_numero(numero)
    if len(n) > 3:
        cuerpo = n[:-3] + r"\.?" + n[-3:]
    else:
        cuerpo = n
    return re.compile(rf"(?<![\d.,]){cuerpo}(?![\d]|\.\d)")


def pares_infoleg(mod_zip: Path) -> set[tuple[int, int]]:
    """Todos los pares (modificatoria, modificada) de InfoLEG, sin filtrar al corpus."""
    with zipfile.ZipFile(mod_zip) as z:
        nombre = next(n for n in z.namelist() if n.endswith(".csv"))
        with z.open(nombre) as fb:
            return {(int(r["id_norma_modificatoria"]), int(r["id_norma_modificada"]))
                    for r in csv.DictReader(io.TextIOWrapper(fb, encoding="utf-8", errors="replace"))}


# --------------------------------------------------------------------------------------------
# Diagnosticos que el parser NO usa (solo explican errores)
# --------------------------------------------------------------------------------------------
# Nombres con los que el texto nombra una norma y que NO estan en el gazetteer del detector
# (ALIAS). Sirven para que la referencia de la deteccion sea independiente del detector: si el
# texto dice "Ley de Ministerios" y el detector no lo vio, es un fallo de deteccion.
NOMBRES_EXTRA = {
    48853: [r"\bley de ministerios\b"],          # Ley 22.520
    25552: [r"\bl\.\s?c\.\s?t\b"],          # "L.C.T." (Ley de Contrato de Trabajo)
}
_MESES = r"(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|sep?tiembre|octubre|noviembre|diciembre)"
# "Decreto N° 1694 del 22 de noviembre de 2006": el ano esta en la fecha, no en "1694/06"
_ANIO_FECHA = re.compile(rf"^\s*,?\s*(?:de\s+fecha|del|de)\s+\d{{1,2}}\s*[°º]?\s+de\s+{_MESES}\s+(?:de|del)\s+(\d{{4}})",
                         re.I)


def anio_por_fecha(texto: str, fin: int) -> int | None:
    """Ano de la fecha que sigue a la mencion, si la hay ("... del 22 de noviembre de 2006")."""
    m = _ANIO_FECHA.match(texto[fin:fin + 70])
    return int(m.group(1)) if m else None


def recuperables(arts, cat: Catalogo, origen: Norma | None) -> dict[int, bool]:
    """Destinos que el parser no resolvio en alguna mencion por no leer el ano escrito como fecha.

    Devuelve {id_destino: True si esa mencion, ya resuelta, pasaria la regla F}. Es un
    diagnostico: el parser congelado no lee estas fechas (queda como mejora, bitacora B51).
    """
    out: dict[int, bool] = {}
    for art in arts:
        cons = reglas_v2._CONSIDERANDO.search(art.texto) if art.zona == "encabezado" else None
        for m in detectar(art.texto, anio_por_fecha=PARSER["anio_por_fecha"]):
            if m.anio is not None or cat.resolver(m.tipo, m.numero, None) is not None:
                continue
            anio = anio_por_fecha(art.texto, m.fin)
            n = cat.resolver(m.tipo, m.numero, anio) if anio else None
            if n is None or (origen and n.id == origen.id):
                continue
            parte = art.zona
            if art.zona == "encabezado":
                parte = "considerando" if cons and m.inicio >= cons.start() else "visto"
            oa, ob = reglas_v2._oracion(art.texto, m.inicio, m.fin)
            verbo = reglas_v2.verbo_real(art.texto[oa:ob])
            temporal = not (origen and n.fecha and origen.fecha and n.fecha > origen.fecha)
            pasa = temporal and (parte == "visto" or (art.zona == "articulado"
                                                       and (origen is None or origen.tipo != "decreto" or bool(verbo))))
            out[n.id] = out.get(n.id, False) or pasa
    return out


def main(corpus: Path, html_dir: Path, base_zip: Path, ev_csv: Path, out: Path,
         mod_zip: Path | None = None) -> None:
    cat = Catalogo.desde_corpus(corpus / "corpus_normas.csv")
    print("cargando catalogo completo de InfoLEG ...")
    completo = catalogo_completo(base_zip)
    print(f"  {len(completo.normas)} leyes, decretos y decretos-leyes")

    split_de = {}
    with open(corpus / "corpus_normas.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            split_de[int(r["id_norma"])] = r["split"]
    gold_rows = cargar_gold(corpus)
    gold = {s: {(int(g["id_norma_modificatoria"]), int(g["id_norma_modificada"]))
                for g in gold_rows if g["split"] == s} for s in ("dev", "test")}

    # ---- recorrer los textos: todas las menciones, resueltas o no -------------------------
    filas_m = []
    textos = {}
    recup = {}             # id_origen -> {id_destino: pasaria F} (ano escrito como fecha)
    for id_o in sorted(split_de):
        doc = cargar(id_o, html_dir)
        if doc is None:
            continue
        texto, arts = doc
        textos[id_o] = texto
        recup[id_o] = recuperables(arts, cat, cat.normas.get(id_o))
        for art in arts:
            for m in detectar(art.texto, anio_por_fecha=PARSER["anio_por_fecha"]):
                est, id_d, ncand = estado_normalizacion(m, cat, completo, cat.normas.get(id_o))
                if id_d == id_o:
                    continue      # la norma citandose a si misma ("el presente decreto 70/2023")
                filas_m.append({"id_origen": id_o, "split": split_de[id_o], "articulo": art.numero,
                                "zona": art.zona, "metodo": "regex_numero", "tipo": m.tipo,
                                "numero": norm_numero(m.numero), "anio": m.anio or "",
                                "estado": est, "id_destino": id_d or "", "candidatos_infoleg": ncand,
                                # ano escrito como fecha despues de la mencion (diagnostico, el parser no lo usa)
                                "anio_en_fecha": anio_por_fecha(art.texto, m.fin) or "",
                                "superficie": m.superficie[-80:]})
            for id_d, a, b, sup in detectar_alias(art.texto, PARSER["alias"]):
                if id_d == id_o:
                    continue
                # un alias apunta por construccion a una norma del corpus: se vincula sin ambiguedad
                filas_m.append({"id_origen": id_o, "split": split_de[id_o], "articulo": art.numero,
                                "zona": art.zona, "metodo": "alias", "tipo": "", "numero": "", "anio": "",
                                "estado": "resuelta", "id_destino": id_d, "candidatos_infoleg": 1, "anio_en_fecha": "",
                                "superficie": sup})

    # ---- 1. DETECCION ----------------------------------------------------------------------
    # Para cada par del gold con texto: ¿aparece el numero (o un alias) de la norma destino?
    # ¿lo detecto y resolvio el detector?
    detectados = defaultdict(set)              # id_origen -> destinos con mencion resuelta
    detectados_numero = defaultdict(set)       # id_origen -> numeros detectados (resueltos o no)
    for r in filas_m:
        if r["id_destino"] != "":
            detectados[r["id_origen"]].add(int(r["id_destino"]))
        if r["numero"]:
            detectados_numero[r["id_origen"]].add(r["numero"])
    deteccion = {}
    fallos_det = []
    estado_par = {}       # (o, d) -> en que eslabon se pierde
    for s in ("dev", "test"):
        c = Counter()
        for (o, d) in sorted(gold[s]):
            if o not in textos:
                estado_par[(o, d)] = "sin_texto"
                c["sin_texto"] += 1
                continue
            dest = cat.normas[d]
            plano = sin_tildes(textos[o]).lower()
            aparece_num = bool(patron_laxo(dest.numero).search(textos[o]))
            aparece_alias = any(a in plano for a in ALIAS.get(d, [])) or any(
                re.search(p, plano) for p in NOMBRES_EXTRA.get(d, []))
            if d in detectados[o]:
                estado_par[(o, d)] = "detectada_y_normalizada"
                c["detectada_y_normalizada"] += 1
            elif dest.numero in detectados_numero[o]:
                # el detector vio el numero pero no lo vinculo a esta norma: falla la normalizacion
                estado_par[(o, d)] = "detectada_mal_normalizada"
                c["detectada_mal_normalizada"] += 1
            elif aparece_num or aparece_alias:
                estado_par[(o, d)] = "no_detectada"
                c["no_detectada"] += 1
                i = patron_laxo(dest.numero).search(textos[o]) if aparece_num else None
                if i is None:
                    for p_ in NOMBRES_EXTRA.get(d, []) + [re.escape(a) for a in ALIAS.get(d, [])]:
                        i = re.search(p_, plano)
                        if i:
                            break
                fallos_det.append({"split": s, "id_origen": o, "id_destino": d, "norma_destino": dest.etiqueta,
                                   "contexto": re.sub(r"\s+", " ", (textos[o] if aparece_num else plano)
                                                      [max(0, i.start() - 120): i.end() + 60]) if i else ""})
            else:
                estado_par[(o, d)] = "sin_mencion"
                c["sin_mencion"] += 1
        con_mencion = c["detectada_y_normalizada"] + c["detectada_mal_normalizada"] + c["no_detectada"]
        deteccion[s] = {**c, "pares_gold": len(gold[s]),
                        "recall_deteccion": round((c["detectada_y_normalizada"] + c["detectada_mal_normalizada"])
                                                  / con_mencion, 4) if con_mencion else 0.0}

    # ---- 2. NORMALIZACION ------------------------------------------------------------------
    normalizacion = {}
    for s in ("dev", "test", "total"):
        filas = [r for r in filas_m if s == "total" or r["split"] == s]
        num = [r for r in filas if r["metodo"] == "regex_numero"]
        e = Counter(r["estado"] for r in num)
        n = len(num)
        resueltas = e["resuelta"] + e["resuelta_mundo_cerrado"]
        # las resueltas solo por mundo cerrado se pueden verificar cuando el texto escribe el ano
        # como fecha despues de la mencion ("Decreto 84 del 3 de febrero de 2014")
        mc = [r for r in num if r["estado"] == "resuelta_mundo_cerrado"]
        conf = sum(1 for r in mc if r["anio_en_fecha"] != "" and cat.normas[int(r["id_destino"])].anio == r["anio_en_fecha"])
        contra = sum(1 for r in mc if r["anio_en_fecha"] != "" and cat.normas[int(r["id_destino"])].anio != r["anio_en_fecha"])
        normalizacion[s] = {
            "menciones": len(filas), "menciones_por_numero": n,
            "menciones_por_alias": len(filas) - n,
            "estados": dict(e),
            # proporcion de menciones por numero que el parser no vincula a ninguna norma del corpus
            "proporcion_no_resueltas": round(1 - resueltas / n, 4) if n else 0.0,
            # de las no resueltas, cuantas son normas reales de InfoLEG fuera del corpus
            "proporcion_fuera_del_corpus": round(e["fuera_del_corpus"] / n, 4) if n else 0.0,
            # exactitud de vinculacion verificable: de las resueltas, las que tambien son unicas en
            # el catalogo completo. Las "mundo cerrado" son una cota inferior de error posible.
            "exactitud_vinculacion_verificable": round(e["resuelta"] / resueltas, 4) if resueltas else 0.0,
            "mundo_cerrado": {"confirmadas_por_fecha": conf, "contradichas_por_fecha": contra,
                              "sin_verificar": len(mc) - conf - contra},
            # exactitud sobre todas las vinculaciones que se pueden verificar (unicas en InfoLEG o
            # confirmadas/contradichas por la fecha); las contradichas son vinculaciones erroneas
            "exactitud_vinculacion_estimada": round((e["resuelta"] + conf) / (e["resuelta"] + conf + contra), 4)
            if resueltas else 0.0,
            "vinculaciones_erroneas": contra,
        }

    # ---- 3. EXTRACCION ---------------------------------------------------------------------
    ev = [e for e in _leer_ev(ev_csv)]
    filtro = PARSER["modulo"].CONFIGS[PARSER["config"]]
    pred_todo = {(e.id_origen, e.id_destino) for e in ev if filtro(e)}
    cand_todo = {(e.id_origen, e.id_destino) for e in ev}
    extraccion = {}
    for s in ("dev", "test"):
        pred = {p for p in pred_todo if split_de.get(p[0]) == s}
        cand = {p for p in cand_todo if split_de.get(p[0]) == s}
        extraccion[s] = {
            # metrica de punta a punta (la que se venia reportando)
            "punta_a_punta": prf(pred, gold[s]),
            # solo la decision de la regla, sobre los pares que ya pasaron deteccion y normalizacion
            "condicional_a_candidatos": prf(pred, gold[s] & cand),
            "candidatos": len(cand), "candidatos_en_gold": len(gold[s] & cand),
        }

    # ---- Taxonomia de errores de la consigna ----------------------------------------------
    # Catalogo completo para detectar "destino ausente del corpus": las mismas reglas, pero
    # resolviendo contra todo InfoLEG. Lo que pase la regla F con destino fuera del corpus es una
    # relacion que el parser hubiera extraido si el destino estuviera en el catalogo.
    ausentes = defaultdict(set)      # split -> pares (origen, destino fuera del corpus)
    ausentes_ej = []
    for id_o in sorted(textos):
        evs = PARSER["modulo"].extraer(id_o, html_dir, completo) or []
        for e in evs:
            if e.id_destino not in cat.normas and filtro(e):
                if (id_o, e.id_destino) in ausentes[split_de[id_o]]:
                    continue
                ausentes[split_de[id_o]].add((id_o, e.id_destino))
                if len(ausentes_ej) < 15:
                    ausentes_ej.append(f"{cat.normas[id_o].etiqueta} -> {e.norma_destino}")
    ambiguas_por_par = defaultdict(int)
    for r in filas_m:
        if r["estado"] == "resuelta_mundo_cerrado" and r["id_destino"] != "" and not (
                r["anio_en_fecha"] != "" and cat.normas[int(r["id_destino"])].anio == r["anio_en_fecha"]):
            # si la fecha que sigue a la mencion confirma el ano, la vinculacion no es dudosa
            ambiguas_por_par[(r["id_origen"], int(r["id_destino"]))] += 1

    errores = []
    for s in ("dev", "test"):
        pred = {p for p in pred_todo if split_de.get(p[0]) == s}
        gold_inv = {(d, o) for (o, d) in gold[s] | gold["dev" if s == "test" else "test"]}
        for p in sorted(gold[s] - pred):
            est = estado_par[p]
            if est == "detectada_y_normalizada" and recup.get(p[0], {}).get(p[1]):
                # una mencion que pasaria la regla no se resolvio porque el ano estaba escrito como
                # fecha ("Decreto 1694 del 22 de noviembre de 2006"): es un error de normalizacion
                est = "detectada_mal_normalizada"
                estado_par[p] = est
            cat_err = {"sin_texto": "fuera_de_alcance_sin_texto",
                       "sin_mencion": "relacion_sin_mencion_explicita",
                       "no_detectada": "norma_no_detectada",
                       "detectada_mal_normalizada": "norma_mal_normalizada",
                       "detectada_y_normalizada": "relacion_descartada_por_la_regla"}[est]
            errores.append({"split": s, "error": "FN", "id_origen": p[0], "id_destino": p[1],
                            "origen": cat.normas[p[0]].etiqueta, "destino": cat.normas[p[1]].etiqueta,
                            "categoria": cat_err})
        for p in sorted(pred - gold[s]):
            pasan = [e for e in ev if (e.id_origen, e.id_destino) == p and filtro(e)]
            destino = cat.normas[p[1]]

            def contradicha(e):
                # el ano escrito como fecha despues de la mencion no es el de la norma vinculada
                a = anio_por_fecha(textos.get(p[0], ""), e.fin) if e.metodo == "regex_numero" else None
                return a is not None and a != destino.anio
            if p in gold_inv:
                cat_err = "relacion_invertida"
            elif pasan and all(contradicha(e) for e in pasan):
                cat_err = "norma_mal_normalizada"    # se vinculo a otro decreto con el mismo numero
            elif ambiguas_por_par.get(p):
                cat_err = "referencia_ambigua"
            elif all(e.metodo == "alias" for e in ev if (e.id_origen, e.id_destino) == p and filtro(e)):
                cat_err = "referencia_ambigua"       # solo por nombre propio ("impuesto a las ganancias")
            else:
                cat_err = "relacion_inexistente"     # cita real a la norma, pero InfoLEG no registra vinculo
            errores.append({"split": s, "error": "FP", "id_origen": p[0], "id_destino": p[1],
                            "origen": cat.normas[p[0]].etiqueta, "destino": cat.normas[p[1]].etiqueta,
                            "categoria": cat_err})
    # ---- Embudo: donde se pierde cada par del gold -----------------------------------------
    embudo = {}
    for s in ("dev", "test"):
        pred = {p for p in pred_todo if split_de.get(p[0]) == s}
        c = Counter(estado_par[p] for p in gold[s])
        recuperados = len(gold[s] & pred)
        embudo[s] = {
            "1_pares_gold": len(gold[s]),
            "2_con_texto": len(gold[s]) - c["sin_texto"],
            "3_con_mencion_en_el_texto": len(gold[s]) - c["sin_texto"] - c["sin_mencion"],
            "4_detectados": c["detectada_y_normalizada"] + c["detectada_mal_normalizada"],
            "5_normalizados": c["detectada_y_normalizada"],
            "6_extraidos_por_la_regla": recuperados,
        }

    # Los pares con destino fuera del corpus no estan en el gold (que se filtro al corpus), pero si
    # pueden estar en la base complementaria completa. Su precision contra esa base mide si el
    # parser generaliza mas alla del corpus.
    fuera = {}
    if mod_zip and mod_zip.exists():
        todos_infoleg = pares_infoleg(mod_zip)
        for s in ("dev", "test"):
            fuera[s] = prf(ausentes[s], ausentes[s] & todos_infoleg)
    taxonomia = {s: {"FN": dict(Counter(e["categoria"] for e in errores if e["split"] == s and e["error"] == "FN")),
                     "FP": dict(Counter(e["categoria"] for e in errores if e["split"] == s and e["error"] == "FP")),
                     # pares (no menciones) que la regla F extraeria si el destino estuviera en el catalogo
                     "destino_ausente_del_corpus": len(ausentes[s])}
                 for s in ("dev", "test")}

    metricas = {"fecha": datetime.now(timezone.utc).isoformat(), "config": PARSER["config"],
                "parser": PARSER["modulo"].__name__.split(".")[-1],
                "catalogo_completo_normas": len(completo.normas),
                "deteccion": deteccion, "normalizacion": normalizacion, "extraccion": extraccion,
                "embudo": embudo, "taxonomia_errores": taxonomia,
                "ejemplos_destino_ausente": ausentes_ej,
                "precision_fuera_del_corpus_contra_infoleg_completo": fuera}
    escribir_texto(out / "metricas.json", json.dumps(metricas, indent=2, ensure_ascii=False))
    _csv(out / "menciones.csv", filas_m)
    _csv(out / "errores.csv", errores)
    _csv(out / "deteccion_fallos.csv", fallos_det or [{"split": "", "id_origen": "", "id_destino": "",
                                                        "norma_destino": "", "contexto": ""}])
    print(json.dumps({k: metricas[k] for k in ("deteccion", "normalizacion", "embudo", "taxonomia_errores")},
                     indent=1, ensure_ascii=False))
    for s in ("dev", "test"):
        print(s, "extraccion punta a punta", extraccion[s]["punta_a_punta"])
        print(s, "extraccion condicional  ", extraccion[s]["condicional_a_candidatos"])


def _leer_ev(p: Path):
    campos = reglas_v2.EvidenciaV2.__dataclass_fields__
    with open(p, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            v = {}
            for k, c in campos.items():
                t = c.type if isinstance(c.type, str) else c.type.__name__
                v[k] = int(r[k]) if t == "int" else (r[k] == "True") if t == "bool" else r[k]
            yield reglas_v2.EvidenciaV2(**v)


def _csv(p: Path, filas: list[dict]) -> None:
    with abrir_para_escribir(p) as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(filas)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=Path("data/corpus"))
    ap.add_argument("--html", type=Path, default=Path("data/textos/infoleg/html"))
    ap.add_argument("--base", type=Path, default=Path("data/raw/base.zip"))
    ap.add_argument("--modificatorias", type=Path, default=Path("data/raw/modificatorias.zip"))
    ap.add_argument("--evidencias", type=Path, default=Path("results/reglas_v2/evidencias.csv"))
    ap.add_argument("--out", type=Path)
    ap.add_argument("--parser", choices=["v2", "v3"], default="v2")
    a = ap.parse_args()
    if a.parser == "v3":
        from grafo_legal.extractores import reglas_v3
        PARSER.update(modulo=reglas_v3, config="F3_alias_con_verbo", anio_por_fecha=True, alias=reglas_v3.ALIAS_V3)
        if a.evidencias == Path("results/reglas_v2/evidencias.csv"):
            a.evidencias = Path("results/reglas_v3/evidencias.csv")
    main(a.corpus, a.html, a.base, a.evidencias, a.out or Path("results/subtareas" + ("_v3" if a.parser == "v3" else "")),
         a.modificatorias)
