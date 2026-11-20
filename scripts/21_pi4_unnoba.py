"""PI4: el mismo pipeline sobre el digesto de la UNNOBA, cambiando solo el adaptador.

Entrada (no va a git: tiene nombres y DNI):
  data/textos/unnoba/muestra_pi4_textos.jsonl   texto de los 70 documentos de la muestra
Gold (anotación manual, va a git):
  data/corpus_unnoba/gold_pi4.tsv               doc, destino, clase (MOD | APLICA | CITA), nota

Qué se cambia y qué no:
  - CAMBIA (adaptador, src/grafo_legal/fuentes/unnoba.py): lectura del texto del PDF, partes del
    documento, menciones y claves de las normas de la fuente.
  - NO CAMBIA: las reglas F (v2) y F3 (v3) tal como se congelaron; el verbo (reglas.VERBOS y
    reglas_v3.verbo_real); el tipo por verbo (relaciones.tipo_por_verbo); el parser LLM
    (llm.SISTEMA, mensaje_usuario, verificación de la cita); el parser híbrido (hibrido.candidatos,
    fragmentos, mensaje, SISTEMA, decidir con la política "previa" y los mismos umbrales).
  - Variante "vocab" (aparte, para medir cuánto pesa el vocabulario de los prompts): los dos
    prompts nombran solo leyes y decretos; se cambian esas frases para que nombren también
    resoluciones, ordenanzas y el estatuto. El resto del prompt queda igual.

Uso:
  python scripts/21_pi4_unnoba.py --estimar        # cuenta pedidos, sin llamar a la API
  python scripts/21_pi4_unnoba.py                  # corre todo (usa la cache)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from grafo_legal.extractores import hibrido, llm  # noqa: E402
from grafo_legal.extractores.reglas import _oracion  # noqa: E402
from grafo_legal.extractores.reglas_v3 import verbo_real  # noqa: E402
from grafo_legal.extractores.relaciones import tipo_por_verbo  # noqa: E402
from grafo_legal.fuentes import unnoba  # noqa: E402

TEXTOS = RAIZ / "data/textos/unnoba/muestra_pi4_textos.jsonl"
GOLD = RAIZ / "data/corpus_unnoba/gold_pi4.tsv"
SALIDA = RAIZ / "results/pi4_unnoba"

# fin del dispositivo: lo que sigue (firmas, anexos) no se procesa, como las notas en InfoLEG
_CIERRE = re.compile(r"Art[ií]c\w*\s*\.?\s*\d+\s*\W{0,3}\s*:?\s*Reg[ií]str", re.I)
_ARTICULO = re.compile(r"\bArt[ií]c\w*\s*\.?\s*(\d+)\s*[°º%\"”*?]?\s*[:.\-–]?", re.I)

# --- variante "vocab": solo las frases que enumeran tipos de norma ----------------------------
_VOCAB_LLM = [
    ("de una norma (ley o decreto)", "de una norma (ley, decreto, resolución u ordenanza)"),
    ("necesidad y urgencia, códigos).", "necesidad y urgencia, códigos, resoluciones, ordenanzas, estatutos)."),
    ('"tipo_norma": "ley|decreto|decreto/ley"', '"tipo_norma": "ley|decreto|decreto/ley|resolucion|ordenanza|estatuto"'),
]
_VOCAB_HIB = [
    ("una norma ORIGEN (ley o decreto)", "una norma ORIGEN (ley, decreto, resolución u ordenanza)"),
    ("Las leyes y decretos que un decreto cita en el VISTO", "Las normas que una resolución o un decreto cita en el VISTO"),
]


def con_vocab(texto: str, cambios) -> str:
    for a, b in cambios:
        assert a in texto, a
        texto = texto.replace(a, b)
    return texto


# ----------------------------------------------------------------------------------------------
# 1. Adaptador: documento -> texto limpio, partes, artículos y evidencias
# ----------------------------------------------------------------------------------------------
def preparar(doc: dict) -> dict:
    t = unnoba.limpiar(doc["texto"])
    m = _CIERRE.search(t)
    if m:
        fin = t.find("\n", m.end())
        t = t[: fin if fin > 0 else len(t)]
    partes = unnoba.segmentar(t)
    art = next(p for p in partes if p.parte == "articulado")
    articulos = []  # (numero, inicio, fin)
    ms = [x for x in _ARTICULO.finditer(t, art.inicio)]
    for i, x in enumerate(ms):
        articulos.append((x.group(1), x.start(), ms[i + 1].start() if i + 1 < len(ms) else len(t)))
    return {"texto": t, "partes": partes, "articulos": articulos}


def articulo_de(articulos, pos: int) -> str:
    for n, a, b in articulos:
        if a <= pos < b:
            return n
    return "0"


def evidencias(i: int, doc: dict, prep: dict) -> list[dict]:
    t, origen = prep["texto"], unnoba.clave_origen(doc["titulo"])
    anio_o = unnoba.anio_de_clave(origen)
    out = []
    for m in unnoba.detectar(t):
        if unnoba.clave_comparable(m.clave) == unnoba.clave_comparable(origen):
            continue                                            # la norma citándose a sí misma
        parte = unnoba.parte_de(prep["partes"], m.inicio)
        if parte == "encabezado":
            continue                                            # "Resolución (CS) Nro. 84/2008" del título
        a, b = _oracion(t, m.inicio, m.fin)
        verbo = verbo_real(t[a:b])
        anio_d = unnoba.anio_de_clave(m.clave)
        out.append({
            "doc": i, "id_origen": origen, "id_destino": unnoba.clave_comparable(m.clave), "clave": m.clave,
            "parte": parte, "zona": "articulado" if parte == "articulado" else "encabezado",
            "articulo": articulo_de(prep["articulos"], m.inicio) if parte == "articulado" else "0",
            "metodo": m.metodo, "superficie": m.superficie, "inicio": m.inicio, "fin": m.fin,
            "verbo_oracion": verbo, "tipo_por_verbo": tipo_por_verbo(verbo),
            "temporal_ok": str(anio_d is None or anio_o is None or anio_d <= anio_o),
            "procedencia": "False", "tipo_origen": "resolucion",
        })
    return out


# las reglas congeladas, escritas sobre las columnas de las evidencias (como en reglas_v2/v3)
def _ok(e):
    return e.temporal_ok == "True" and e.procedencia != "True"


REGLAS = {
    "F_v2": lambda e: _ok(e) and (e.parte == "visto" or (e.zona == "articulado" and e.metodo == "regex_numero"
                                                          and (e.tipo_origen != "decreto" or bool(e.verbo_oracion)))),
    "F3_v3": lambda e: _ok(e) and (e.parte == "visto"
                                   or (e.zona == "articulado" and e.metodo == "regex_numero"
                                       and (e.tipo_origen != "decreto" or bool(e.verbo_oracion)))
                                   or (e.zona == "articulado" and e.metodo == "alias" and bool(e.verbo_oracion))),
}


# ----------------------------------------------------------------------------------------------
# 2. Parser LLM (mismo módulo; las respuestas se pasan a claves de la fuente)
# ----------------------------------------------------------------------------------------------
def clave_llm(r: dict) -> str | None:
    tn = str(r.get("tipo_norma") or "").lower()
    num = re.sub(r"\D", "", str(r.get("numero") or ""))
    anio = re.sub(r"\D", "", str(r.get("anio") or ""))
    if "estatut" in tn:
        return "ESTATUTO"
    if not num:
        return None
    if "ley" in tn and "decreto" not in tn:
        return f"LEY-{int(num)}"
    a = unnoba._anio4(anio) if anio else None
    tipo = "ORD" if "orden" in tn else "RES" if "resol" in tn else "DEC" if "decret" in tn else None
    if tipo is None or a is None:
        return None
    return f"{tipo}-{int(num)}-{a}" if tipo != "DEC" else f"DEC-NAC-{int(num)}-{a}"


def correr_llm(docs, preps, cliente, estimar=False) -> tuple[pd.DataFrame, int]:
    filas, pedidos = [], 0
    for i, (doc, prep) in enumerate(zip(docs, preps)):
        t = prep["texto"]
        segs = []
        enc = [p for p in prep["partes"] if p.parte in ("visto", "considerando")]
        ini, fin = min(p.inicio for p in enc), max(p.fin for p in enc)
        if fin > ini:
            segs.append(llm.Segmento(i, 0, "0", "encabezado", ini, t[ini:fin]))
        for k, (n, a, b) in enumerate(prep["articulos"], 1):
            segs.append(llm.Segmento(i, k, n, "articulado", a, t[a:b]))
        origen = unnoba.clave_origen(doc["titulo"])
        for lote in llm.lotes(segs):
            pedidos += 1
            if estimar:
                continue
            resp = cliente.pedir(llm.mensaje_usuario(doc["titulo"], lote))
            por_seg = {f"S{s.orden}": (s, off, txt) for s, off, txt in lote}
            for r in llm.leer_json(resp["respuesta"]):
                s = por_seg.get(str(r.get("segmento")))
                if s is None:
                    continue
                seg, off, txt = s
                verificada = llm.ubicar(str(r.get("cita") or ""), txt) >= 0
                clave = clave_llm(r)
                if clave is None or clave == unnoba.clave_comparable(origen):
                    continue
                parte = "articulado" if seg.zona == "articulado" else unnoba.parte_de(
                    prep["partes"], seg.inicio + off + max(0, llm.ubicar(str(r.get("cita") or ""), txt)))
                filas.append({"doc": i, "id_destino": clave, "parte_origen": parte,
                              "tipo": str(r.get("tipo") or "CITA").upper(), "verificada": verificada,
                              "cita": r.get("cita")})
    return pd.DataFrame(filas, columns=["doc", "id_destino", "parte_origen", "tipo", "verificada", "cita"]), pedidos


# ----------------------------------------------------------------------------------------------
# 3. Parser híbrido (mismas funciones del módulo; la política y los umbrales del script 20)
# ----------------------------------------------------------------------------------------------
POLITICA, UMBRAL, UMBRAL_BAJO = "previa", 0.5, 0.15


def correr_hibrido(docs, preps, ev: pd.DataFrame, cliente, estimar=False) -> tuple[pd.DataFrame, int]:
    filas, pedidos = [], 0
    for i, (doc, prep) in enumerate(zip(docs, preps)):
        e = ev[ev.doc == i]
        if e.empty:
            continue
        cands = hibrido.candidatos(e)
        gris = cands[cands.zona == "gris"]
        juicios, frags_de = {}, {}
        if not gris.empty:
            lista = []
            for k, c in enumerate(gris.itertuples(index=False), 1):
                fr = hibrido.fragmentos(e[e.id_destino == c.id_destino], prep["texto"])
                frags_de[c.id_destino] = fr
                sup = e[e.id_destino == c.id_destino].superficie.iloc[0]
                lista.append({"id": f"C{k}", "destino": sup, "titulo": c.id_destino, "fragmentos": fr})
            pedidos += 1
            if not estimar:
                resp = cliente.pedir(hibrido.mensaje(unnoba.clave_origen(doc["titulo"]), doc["titulo"], lista))
                leidos = hibrido.leer(resp["respuesta"])
                for c in lista:
                    juicios[c["titulo"]] = leidos.get(c["id"])
        for c in cands.itertuples(index=False):
            j = juicios.get(c.id_destino)
            ver = hibrido.verificar(j, frags_de.get(c.id_destino, []))[0] if j else False
            acepta = hibrido.decidir(c.zona, j, ver, POLITICA, UMBRAL, bool(c.pasa_F3), UMBRAL_BAJO)
            tipos_r = [t for t in e[e.id_destino == c.id_destino].tipo_por_verbo if t != "CITA"]
            tipo = hibrido.tipo_final(j, ver, tipos_r[0] if tipos_r else "MODIFICA")[0] if acepta else "CITA"
            filas.append({"doc": i, "id_destino": c.id_destino, "zona": c.zona, "pasa_F3": c.pasa_F3,
                          "probabilidad": hibrido.probabilidad(j), "verificada": ver, "acepta": acepta,
                          "tipo": tipo, "motivo_llm": (j or {}).get("motivo")})
    return pd.DataFrame(filas), pedidos


# ----------------------------------------------------------------------------------------------
# 4. Evaluación por pares (doc, destino), con claves sin emisor
# ----------------------------------------------------------------------------------------------
def prf(pred: set, gold: set) -> dict:
    tp = len(pred & gold)
    p = tp / len(pred) if pred else 0.0
    r = tp / len(gold) if gold else 0.0
    return {"tp": tp, "fp": len(pred - gold), "fn": len(gold - pred), "P": round(p, 3), "R": round(r, 3),
            "F1": round(2 * p * r / (p + r), 3) if p + r else 0.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--estimar", action="store_true")
    args = ap.parse_args()
    SALIDA.mkdir(parents=True, exist_ok=True)

    docs = [json.loads(l) for l in TEXTOS.read_text(encoding="utf-8").splitlines() if l.strip()]
    preps = [preparar(d) for d in docs]
    ev = pd.DataFrame([x for i, (d, p) in enumerate(zip(docs, preps)) for x in evidencias(i, d, p)])

    gold = pd.read_csv(GOLD, sep="\t", dtype={"doc": int})
    gold["id_destino"] = gold.destino.map(unnoba.clave_comparable)
    g_todo = set(zip(gold.doc, gold.id_destino))
    g_vinc = set(zip(gold[gold.clase != "CITA"].doc, gold[gold.clase != "CITA"].id_destino))
    g_mod = set(zip(gold[gold.clase == "MOD"].doc, gold[gold.clase == "MOD"].id_destino))

    import os
    clave = os.environ.get("ANTHROPIC_API_KEY") or ((RAIZ / ".anthropic_key").read_text().strip()
                                                     if (RAIZ / ".anthropic_key").exists() else None)
    c_llm = llm.ClienteLLM(SALIDA / "cache_llm", clave=clave)
    c_llm_v = llm.ClienteLLM(SALIDA / "cache_llm", clave=clave, sistema=con_vocab(llm.SISTEMA, _VOCAB_LLM),
                             version=llm.VERSION_PROMPT + "+vocab-unnoba")
    c_hib = llm.ClienteLLM(SALIDA / "cache_hibrido", clave=clave, sistema=hibrido.SISTEMA, version=hibrido.VERSION_PROMPT)
    c_hib_v = llm.ClienteLLM(SALIDA / "cache_hibrido", clave=clave, sistema=con_vocab(hibrido.SISTEMA, _VOCAB_HIB),
                             version=hibrido.VERSION_PROMPT + "+vocab-unnoba")

    # las cuatro corridas son independientes: van en paralelo (cada una, en orden y con su cache)
    from concurrent.futures import ThreadPoolExecutor
    trabajos = {"llm": lambda: correr_llm(docs, preps, c_llm, args.estimar),
                "llm_vocab": lambda: correr_llm(docs, preps, c_llm_v, args.estimar),
                "hibrido": lambda: correr_hibrido(docs, preps, ev, c_hib, args.estimar),
                "hibrido_vocab": lambda: correr_hibrido(docs, preps, ev, c_hib_v, args.estimar)}
    with ThreadPoolExecutor(4) as pool:
        fut = {k: pool.submit(f) for k, f in trabajos.items()}
        corridas = {k: f.result() for k, f in fut.items()}
    if args.estimar:
        print({k: v[1] for k, v in corridas.items()}, "pedidos;", len(ev), "evidencias")
        return

    ev.to_csv(SALIDA / "evidencias.csv", index=False)
    gold.to_csv(SALIDA / "gold_normalizado.csv", index=False)
    for k, (df, _) in corridas.items():
        # el "motivo" del LLM puede nombrar a las personas de la resolución: queda solo en la cache
        df.drop(columns=["motivo_llm"], errors="ignore").to_csv(SALIDA / f"relaciones_{k}.csv", index=False)

    # predicciones por método -> conjuntos de pares
    pred, pred_mod = {}, {}
    detect = set(zip(ev.doc, ev.id_destino))
    for nombre, regla in REGLAS.items():
        s = ev[ev.apply(regla, axis=1)]
        pred[nombre] = set(zip(s.doc, s.id_destino))
        sm = s[s.tipo_por_verbo != "CITA"]
        pred_mod[nombre] = set(zip(sm.doc, sm.id_destino))
    for k in ("llm", "llm_vocab"):
        df = corridas[k][0]
        df = df[df.verificada]
        # misma proyección que en InfoLEG ("LLM, regla F"): VISTO, o articulado (el origen no es decreto)
        s = df[(df.parte_origen == "visto") | (df.parte_origen == "articulado")]
        pred[k] = set(zip(s.doc, s.id_destino))
        sm = df[df.tipo != "CITA"]
        pred_mod[k] = set(zip(sm.doc, sm.id_destino))
        pred[k + "_sin_cita"] = set(zip(sm.doc, sm.id_destino))
    for k in ("hibrido", "hibrido_vocab"):
        df = corridas[k][0]
        s = df[df.acepta]
        pred[k] = set(zip(s.doc, s.id_destino))
        # el híbrido acepta "modifica o complementa" (criterio InfoLEG) y no separa MOD de APLICA:
        # su métrica solo_MOD no tiene sentido y no se calcula

    met = {"deteccion_menciones": prf(detect, g_todo),
           "deteccion_LLM": prf(set(zip(corridas["llm"][0].doc, corridas["llm"][0].id_destino)), g_todo),
           "deteccion_LLM_vocab": prf(set(zip(corridas["llm_vocab"][0].doc, corridas["llm_vocab"][0].id_destino)), g_todo),
           "vinculo": {k: prf(v, g_vinc) for k, v in pred.items()},
           "solo_MOD": {k: prf(v, g_mod) for k, v in pred_mod.items()},
           "n": {"docs": len(docs), "pares_gold": len(g_todo), "vinculo": len(g_vinc), "MOD": len(g_mod),
                 "evidencias": len(ev)},
           "uso_api": {k: c.uso for k, c in (("llm", c_llm), ("llm_vocab", c_llm_v), ("hibrido", c_hib),
                                              ("hibrido_vocab", c_hib_v))}}
    # por estrato de la muestra
    crit = {i: d["criterio"] for i, d in enumerate(docs)}
    estr = defaultdict(dict)
    for c in sorted(set(crit.values())):
        ids = {i for i, x in crit.items() if x == c}
        gv = {p for p in g_vinc if p[0] in ids}
        for k, v in pred.items():
            estr[c][k] = prf({p for p in v if p[0] in ids}, gv)
        estr[c]["_pares_gold_vinculo"] = len(gv)
    met["por_estrato"] = estr

    # bootstrap pareado por documento (como en InfoLEG, por norma origen): diferencia de F1
    import random
    def f1(pr, go, ids):
        a = {p for p in pr if p[0] in ids}; b = {p for p in go if p[0] in ids}
        return prf(a, b)["F1"]
    rnd = random.Random(20261120)
    ids_docs = list(range(len(docs)))
    met["bootstrap"] = {}
    for a, b in (("hibrido", "F3_v3"), ("llm_vocab", "F3_v3"), ("hibrido", "llm_vocab"), ("llm_vocab", "llm")):
        difs = []
        for _ in range(2000):
            m_ = [rnd.choice(ids_docs) for _ in ids_docs]
            # con reposición: se repiten documentos, así que se cuentan pares por (copia, doc)
            pa = {(j, d) for j, x in enumerate(m_) for (dd, d) in pred[a] if dd == x}
            pb = {(j, d) for j, x in enumerate(m_) for (dd, d) in pred[b] if dd == x}
            go = {(j, d) for j, x in enumerate(m_) for (dd, d) in g_vinc if dd == x}
            difs.append(prf(pa, go)["F1"] - prf(pb, go)["F1"])
        difs.sort()
        met["bootstrap"][f"{a}_menos_{b}"] = {"dif": round(met["vinculo"][a]["F1"] - met["vinculo"][b]["F1"], 3),
                                               "ic95": [round(difs[49], 3), round(difs[1949], 3)]}
    # sensibilidad (B58): (a) el gold de la revisión 1, con las remisiones como CITA;
    # (b) la política "cascada" del híbrido (el LLM decide solo la zona gris, umbral 0,5)
    antes = gold[gold.nota.astype(str).str.contains("antes CITA", regex=False)]
    g_vinc_r1 = g_vinc - set(zip(antes.doc, antes.id_destino))
    for k in ("hibrido", "hibrido_vocab"):
        df = corridas[k][0]
        c = df[(df.zona == "seguro") | ((df.zona == "gris") & df.verificada & (df.probabilidad >= UMBRAL))]
        pred[k + "_cascada"] = set(zip(c.doc, c.id_destino))
    met["vinculo"].update({k: prf(pred[k], g_vinc) for k in ("hibrido_cascada", "hibrido_vocab_cascada")})
    met["sensibilidad_gold_revision_1"] = {k: prf(v, g_vinc_r1) for k, v in pred.items()}
    (SALIDA / "metricas.json").write_text(json.dumps(met, ensure_ascii=False, indent=1), encoding="utf-8")

    # errores por par, para el análisis
    errores = []
    for k in pred:
        for p in sorted(pred[k] - g_vinc):
            errores.append({"metodo": k, "error": "FP", "doc": p[0], "destino": p[1],
                            "clase_gold": next((r.clase for r in gold.itertuples() if (r.doc, r.id_destino) == p), "")})
        for p in sorted(g_vinc - pred[k]):
            errores.append({"metodo": k, "error": "FN", "doc": p[0], "destino": p[1],
                            "detectada": p in detect})
    pd.DataFrame(errores).to_csv(SALIDA / "errores.csv", index=False)
    print(json.dumps({k: met[k] for k in ("deteccion_menciones", "deteccion_LLM", "deteccion_LLM_vocab", "n")}, indent=1))
    for k in pred:
        print(f"{k:22s} vinculo {met['vinculo'][k]}  MOD {met['solo_MOD'].get(k, '')}")
    print(met["uso_api"]); print(met["bootstrap"])


if __name__ == "__main__":
    main()
