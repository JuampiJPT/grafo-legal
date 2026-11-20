"""Evaluación del texto consolidado de la LCT contra el texto actualizado de InfoLEG (B61).

Referencia: data/textos/infoleg/html/25552_texact.html (guardado a mano desde InfoLEG el
20/11/2026; solo se usa para medir, nunca como entrada). Repite con el texto completo la
comparación que en B61 se hizo con firmas en el navegador, y además compara la historia:
qué modificaciones registra InfoLEG en sus notas y cuáles aplicó el consolidado.

  1. Por artículo: igualdad después de normalizar y similitud de secuencia (difflib, palabras).
  2. Por evento: (artículo, operación, norma) de las notas de InfoLEG contra las operaciones
     aplicadas en el consolidado.

Salidas en results/consolidado/evaluacion/: por_articulo.csv, eventos.csv, metricas.json.
"""

import difflib
import html
import json
import re
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
from firma_texto import NOTA, normalizar  # noqa: E402

OUT = RAIZ / "results/consolidado/evaluacion"
# notas editoriales de InfoLEG: cualquier paréntesis (con paréntesis adentro) que cite el Boletín
# Oficial o sea una "Nota Infoleg"; el texto de la ley no tiene paréntesis así
NOTA_BO = re.compile(r"\((?:[^()]|\([^()]*\))*?(?:B\.\s*O\.|Nota\s+Infoleg)(?:[^()]|\([^()]*\))*\)", re.I)
ART = re.compile(r"(?:^|\n)\s*(?:Art[íi]culo|Art\.)\s*(\d+)\s*[°º]?\s*\.?\s*(bis|ter|qu[aá]ter)?\s*[.—–:-]", re.I)


def texto_infoleg(p: Path) -> tuple[str, str]:
    crudo = p.read_bytes()
    try:
        h = crudo.decode("utf-8")
    except UnicodeDecodeError:
        h = crudo.decode("windows-1252")
    h = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?i)<br\s*/?>|</p>|</div>|<p[^>]*>", "\n", h)
    t = html.unescape(re.sub(r"<[^>]+>", " ", h))
    t = re.sub(r"[ \t\xa0]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n\n", t)
    corte = t.rfind("Antecedentes Normativos")   # el primero es el enlace "Ver Antecedentes Normativos"
    return t[:corte], t[corte:]


def articulos(t: str) -> dict[str, dict]:
    ms = list(ART.finditer(t))
    out = {}
    for i, m in enumerate(ms):
        num = m.group(1) + (" " + m.group(2).lower().replace("á", "a") if m.group(2) else "")
        txt = t[m.start(): ms[i + 1].start() if i + 1 < len(ms) else len(t)]
        txt = re.split(r"\n\s*(?:TITULO|CAPITULO|Título|Capítulo)\s+[IVXL]+", txt)[0]
        notas = NOTA_BO.findall(txt) + NOTA.findall(NOTA_BO.sub(" ", txt))
        cuerpo = NOTA.sub(" ", NOTA_BO.sub(" ", txt))
        cuerpo = re.sub(r"^(\s*(?:Art[íi]culo|Art\.)\s*\d+\s*[°º]?\s*)\.\s*(bis|ter)", r"\1 \2", cuerpo, flags=re.I)
        out.setdefault(num, {"texto": cuerpo, "notas": notas})
    return out


_OP = {"sustituid": "SUSTITUYE", "derogad": "DEROGA", "incorporad": "INCORPORA", "modificad": "MODIFICA_PARCIAL"}
_EV = re.compile(r"(Artículo|Inciso|Incisos|Párrafo|Párrafos|Capítulo|Expresión|Texto|Apartado|Punto)?\s*([^()]{0,60}?)"
                 r"(sustituid|derogad|incorporad|modificad)[oa]s?\s+por\s+(?:el\s+)?art\.?\s*([\d°º]+)[^)]*?\s(Ley|Decreto)"
                 r"(?:\s+Nacional)?\s+N?[°º]?\s*([\d.]+)(?:/(\d{2,4}))?", re.I)


def eventos_infoleg(arts: dict) -> pd.DataFrame:
    filas = []
    for num, a in arts.items():
        for n in a["notas"]:
            for m in _EV.finditer(n):
                parte = (m.group(1) or "Artículo").lower()
                op = _OP[m.group(3).lower()]
                if parte not in ("artículo",) and op != "DEROGA":
                    op = "MODIFICA_PARCIAL"
                filas.append({"articulo": num, "operacion": op, "parte": parte,
                              "norma": f"{m.group(5).capitalize()} {m.group(6).replace('.', '')}"})
    return pd.DataFrame(filas).drop_duplicates()


def main():
    cuerpo, _ = texto_infoleg(RAIZ / "data/textos/infoleg/html/25552_texact.html")
    inf = articulos(cuerpo)
    con = {x["articulo"]: x for x in json.loads((RAIZ / "results/consolidado/lct_consolidada.json").read_text())}

    filas = []
    for num in sorted(set(inf) | set(con), key=lambda n: (int(re.match(r"\d+", n).group()), n)):
        a, c = inf.get(num), con.get(num)
        ni = normalizar(a["texto"]) if a else ""
        nc = normalizar(c["texto"]) if c and c["vigente"] else ""
        der_i = a is not None and len(ni.split()) <= 10 and any("derogad" in n.lower() for n in a["notas"])
        der_c = c is not None and not c["vigente"]
        ratio = difflib.SequenceMatcher(None, ni.split(), nc.split(), autojunk=False).ratio() if ni and nc else 0.0
        if der_i and der_c:
            clase = "derogado en los dos"
        elif der_i != der_c:
            clase = "InfoLEG derogado, consolidado vigente" if der_i else "consolidado derogado, InfoLEG vigente"
        elif ni == nc:
            clase = "idéntico"
        elif ratio >= 0.95:
            clase = "casi idéntico (>=0,95)"
        elif ratio >= 0.8:
            clase = "diferencias menores (0,8-0,95)"
        else:
            clase = "diferencia sustantiva (<0,8)"
        hist = [h for h in (c or {}).get("historia", []) if h["operacion"] != "TEXTO_ORDENADO"]
        filas.append({"articulo": num, "en_infoleg": a is not None, "en_consolidado": c is not None,
                      "palabras_infoleg": len(ni.split()), "palabras_consolidado": len(nc.split()),
                      "similitud": round(ratio, 3), "clase": clase, "modificado_consolidado": bool(hist or der_c),
                      "modificado_infoleg": bool(a and a["notas"]),
                      "ultima_nota_infoleg": (a["notas"][-1][:160] if a and a["notas"] else "")})
    pa = pd.DataFrame(filas)
    OUT.mkdir(parents=True, exist_ok=True)
    pa.to_csv(OUT / "por_articulo.csv", index=False)

    # eventos: notas de InfoLEG contra operaciones aplicadas (posteriores al t.o.)
    ev_i = eventos_infoleg(inf)
    ops = pd.read_csv(RAIZ / "results/consolidado/operaciones.csv", dtype=str)
    noap = pd.read_csv(RAIZ / "results/consolidado/no_aplicadas.csv", dtype=str)
    clave = lambda a, n: (str(a).strip().lower(), re.sub(r"\D", "", str(n)))
    aplic = {clave(r.articulo, r.norma) for r in ops.itertuples()} - {clave(r.articulo, r.norma) for r in noap.itertuples()}
    ev_i["clave"] = [clave(a, n) for a, n in zip(ev_i.articulo, ev_i.norma)]
    ev_i = ev_i.drop_duplicates("clave")
    ev_i["aplicado_en_consolidado"] = ev_i.clave.isin(aplic)
    ev_i.drop(columns="clave").to_csv(OUT / "eventos.csv", index=False)
    rec = float(ev_i.aplicado_en_consolidado.mean()) if len(ev_i) else 0.0
    ev_infoleg = set(ev_i.clave)
    prec = len(aplic & ev_infoleg) / len(aplic) if aplic else 0.0

    cambian = pa[pa.modificado_consolidado | pa.modificado_infoleg]
    ok = cambian.clase.isin(["idéntico", "casi idéntico (>=0,95)", "derogado en los dos"])
    met = {"articulos_infoleg": len(inf), "articulos_consolidado": len(con),
           "por_clase": pa.clase.value_counts().to_dict(),
           "coinciden_idem_o_casi": int(pa.clase.isin(["idéntico", "casi idéntico (>=0,95)", "derogado en los dos"]).sum()),
           "articulos_que_cambian": len(cambian), "cambian_y_coinciden": int(ok.sum()),
           "eventos_infoleg": len(ev_i), "eventos_aplicados": len(aplic),
           "recall_eventos": round(rec, 3), "precision_eventos": round(prec, 3),
           "nota": "eventos: (artículo, norma) de las notas de InfoLEG; las notas solo guardan la última versión de cada parte, así que el recall es aproximado"}
    (OUT / "metricas.json").write_text(json.dumps(met, ensure_ascii=False, indent=1))
    print(json.dumps(met, ensure_ascii=False, indent=1))
    print(pa[~pa.clase.isin(["idéntico", "casi idéntico (>=0,95)", "derogado en los dos"]) & (pa.modificado_consolidado | pa.modificado_infoleg)]
          [["articulo", "palabras_infoleg", "palabras_consolidado", "similitud", "clase", "ultima_nota_infoleg"]].to_string(index=False))


if __name__ == "__main__":
    main()
