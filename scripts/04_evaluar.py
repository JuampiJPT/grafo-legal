"""
04_evaluar.py
Evalua las evidencias del parser contra el gold, por configuracion de la ablacion y por split.

Protocolo: se itera SOLO sobre dev. El split test se evalua una sola vez, con --incluir-test,
cuando las reglas estan congeladas (queda registrado en metricas.json con la fecha).

Uso:
    python scripts/04_evaluar.py --corpus data/corpus --res results/reglas
    python scripts/04_evaluar.py --corpus data/corpus --res results/reglas --incluir-test
    python scripts/04_evaluar.py --parser v2 --res results/reglas_v2 --config-final F_visto_o_articulado_con_verbo_o_ley
"""

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from grafo_legal.archivos import abrir_para_escribir, escribir_texto  # noqa: E402
from grafo_legal.evaluacion import cargar_gold, prf          # noqa: E402
from grafo_legal.extractores import reglas, reglas_v2         # noqa: E402


def leer_evidencias(p: Path, clase) -> list:
    """Lee evidencias.csv en la clase de evidencia del parser (v1 o v2), con sus tipos."""
    campos = clase.__dataclass_fields__
    out = []
    with open(p, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            v = {}
            for k, c in campos.items():
                t = c.type if isinstance(c.type, str) else c.type.__name__
                v[k] = int(r[k]) if t == "int" else (r[k] == "True") if t == "bool" else r[k]
            out.append(clase(**v))
    return out


def main(corpus: Path, res: Path, incluir_test: bool, config_final: str, parser: str = "v1") -> None:
    mod = reglas if parser == "v1" else reglas_v2
    CONFIGS = mod.CONFIGS
    gold_rows = cargar_gold(corpus)
    split_de = {}
    with open(corpus / "corpus_normas.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            split_de[int(r["id_norma"])] = r["split"]
    cobertura = {}
    cob_p = corpus / "cobertura_textual_gold.csv"
    if cob_p.exists():
        with open(cob_p, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                cobertura[(int(r["id_norma_modificatoria"]), int(r["id_norma_modificada"]))] = r["mencion_en_texto"]

    vistos = set()
    v_p = corpus / "pares_evaluados_en_v1.csv"
    if v_p.exists():
        with open(v_p, encoding="utf-8") as f:
            vistos = {(int(r["id_norma_modificatoria"]), int(r["id_norma_modificada"])) for r in csv.DictReader(f)}

    ev = leer_evidencias(res / "evidencias.csv", mod.Evidencia if parser == "v1" else mod.EvidenciaV2)
    splits = ["dev"] + (["test"] if incluir_test else [])
    metricas = {"fecha": datetime.now(timezone.utc).isoformat(), "parser": parser, "splits": splits, "configs": {}}

    for nombre, filtro in CONFIGS.items():
        pares = {(e.id_origen, e.id_destino) for e in ev if filtro(e)}
        metricas["configs"][nombre] = {}
        for s in splits:
            gold = {(int(g["id_norma_modificatoria"]), int(g["id_norma_modificada"]))
                    for g in gold_rows if g["split"] == s}
            gold_con_texto = {p for p in gold if cobertura.get(p) != "sin_texto"}
            pred = {p for p in pares if split_de.get(p[0]) == s}
            metricas["configs"][nombre][s] = {"todo_el_gold": prf(pred, gold),
                                              "gold_con_texto": prf(pred, gold_con_texto)}
            if vistos:
                # pares que no se usaron cuando se diseñaron las reglas (corpus v1, decision D11)
                metricas["configs"][nombre][s]["sin_pares_de_v1"] = prf(pred - vistos, gold - vistos)

    # analisis de errores de la configuracion final
    filtro = CONFIGS[config_final]
    pares = {(e.id_origen, e.id_destino) for e in ev if filtro(e)}
    todos = {(e.id_origen, e.id_destino) for e in ev}
    errores = []
    for s in splits:
        gold = {(int(g["id_norma_modificatoria"]), int(g["id_norma_modificada"]))
                for g in gold_rows if g["split"] == s}
        pred = {p for p in pares if split_de.get(p[0]) == s}
        for p in sorted(gold - pred):
            c = cobertura.get(p, "")
            motivo = {"sin_texto": "FN_sin_texto", "sin_mencion": "FN_sin_mencion"}.get(c)
            if not motivo:
                motivo = "FN_filtrado_por_reglas" if p in todos else f"FN_mencion_no_detectada({c})"
            errores.append({"split": s, "tipo": "FN", "id_origen": p[0], "id_destino": p[1], "categoria": motivo})
        for p in sorted(pred - gold):
            evs = [e for e in ev if (e.id_origen, e.id_destino) == p and filtro(e)]
            cat = "FP_solo_alias" if all(e.metodo == "alias" for e in evs) else "FP_mencion_con_verbo"
            errores.append({"split": s, "tipo": "FP", "id_origen": p[0], "id_destino": p[1], "categoria": cat,
                            "fragmento": evs[0].fragmento[:300] if evs else ""})
    metricas["config_final"] = config_final
    metricas["errores_por_categoria"] = {s: dict(Counter(e["categoria"] for e in errores if e["split"] == s))
                                         for s in splits}

    escribir_texto(res / "metricas.json", json.dumps(metricas, indent=2, ensure_ascii=False))
    with abrir_para_escribir(res / "errores.csv") as f:
        w = csv.DictWriter(f, fieldnames=["split", "tipo", "id_origen", "id_destino", "categoria", "fragmento"],
                           lineterminator="\n")
        w.writeheader()
        w.writerows(errores)

    print(f"{'config':32s} {'split':5s} {'P':>6s} {'R':>6s} {'F1':>6s}   (R gold con texto)  [F1 sin pares de v1]")
    for n, d in metricas["configs"].items():
        for s, m in d.items():
            a, b = m["todo_el_gold"], m["gold_con_texto"]
            c = m.get("sin_pares_de_v1")
            extra = f"  [{c['f1']:.3f}, {c['gold']} pares]" if c else ""
            print(f"{n:32s} {s:5s} {a['precision']:6.3f} {a['recall']:6.3f} {a['f1']:6.3f}   ({b['recall']:.3f}){extra}")
    print(json.dumps(metricas["errores_por_categoria"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=Path("data/corpus"))
    ap.add_argument("--res", type=Path, default=Path("results/reglas"))
    ap.add_argument("--incluir-test", action="store_true")
    ap.add_argument("--config-final", default="E_C_mas_verbo_en_oracion")
    ap.add_argument("--parser", choices=["v1", "v2"], default="v1")
    a = ap.parse_args()
    main(a.corpus, a.res, a.incluir_test, a.config_final, a.parser)
