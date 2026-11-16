"""
16_evaluar_tipos.py
Evalua el TIPO de relacion (SUSTITUYE, INCORPORA, DEROGA, REGLAMENTA, MODIFICA, CITA) y el
articulo destino contra la revision manual (docs/revision_manual/revision_tipos_78.csv).

InfoLEG no registra el tipo, asi que esta es la unica medida posible. La muestra es estratificada:
13 relaciones por cada tipo que predijo el parser de reglas. Eso tiene dos consecuencias:

  - La matriz de confusion de la muestra se reporta tal cual (conteos).
  - Para estimar metricas de la POBLACION (todas las relaciones del parser), cada caso pesa
    N_tipo / n_tipo (ponderacion por la inversa de la probabilidad de muestreo): un caso de CITA
    representa a ~180 relaciones y uno de REGLAMENTA a ~4. La macro-F1 ponderada y la exactitud
    ponderada salen de esa matriz expandida.

Si existe la salida del parser LLM, se evalua sobre los mismos casos (se busca la relacion del LLM
con el mismo articulo origen y la misma norma destino). Como la muestra se eligio con las
predicciones de las reglas, la comparacion vale para las relaciones que las reglas encontraron.

Salidas en results/tipos/: metricas.json y matrices.csv.

Uso:
    python scripts/16_evaluar_tipos.py
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from grafo_legal.archivos import escribir_texto       # noqa: E402
from grafo_legal.salida import TIPOS                  # noqa: E402


def metricas_tipo(real: pd.Series, pred: pd.Series, peso: pd.Series) -> dict:
    """P, R y F1 por tipo, macro-F1 y exactitud, con pesos por caso."""
    out, f1s = {}, []
    for t in TIPOS:
        tp = peso[(pred == t) & (real == t)].sum()
        fp = peso[(pred == t) & (real != t)].sum()
        fn = peso[(pred != t) & (real == t)].sum()
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        f = 2 * p * r / (p + r) if p + r else 0.0
        out[t] = {"precision": round(p, 3), "recall": round(r, 3), "f1": round(f, 3)}
        f1s.append(f)
    return {"por_tipo": out, "macro_f1": round(sum(f1s) / len(f1s), 3),
            "exactitud": round(peso[pred == real].sum() / peso.sum(), 3)}


def main(revision: Path, rel_reglas: Path, rel_llm: Path, out: Path) -> None:
    rev = pd.read_csv(revision, keep_default_na=False, dtype=str)
    pob = pd.read_csv(rel_reglas, keep_default_na=False, dtype=str).tipo.value_counts()
    n = rev.tipo.value_counts()
    rev["peso"] = rev.tipo.map(lambda t: pob[t] / n[t])
    uno = pd.Series(1.0, index=rev.index)

    res = {"casos": len(rev), "por_estrato": n.to_dict(), "poblacion": pob.to_dict()}
    matrices = []
    res["reglas_v2"] = {"muestra": metricas_tipo(rev.tipo_correcto, rev.tipo, uno),
                        "poblacion_ponderada": metricas_tipo(rev.tipo_correcto, rev.tipo, rev.peso),
                        "articulo_destino_ok": round(rev.articulo_ok.astype(int).mean(), 3)}
    m = pd.crosstab(rev.tipo, rev.tipo_correcto).reindex(index=TIPOS, columns=TIPOS, fill_value=0)
    matrices.append(m.assign(metodo="reglas_v2").reset_index().rename(columns={"tipo": "predicho"}))

    if rel_llm.exists():
        llm = pd.read_csv(rel_llm, keep_default_na=False, dtype=str)
        # tipo del LLM para el mismo articulo origen y la misma norma destino; si el LLM dio varios
        # (por ejemplo SUSTITUYE el articulo 10 y CITA a la ley), gana el que no es CITA
        prioridad = {t: i for i, t in enumerate(["SUSTITUYE", "INCORPORA", "DEROGA", "REGLAMENTA", "MODIFICA", "CITA"])}
        llm["prio"] = llm.tipo.map(prioridad)
        llm = llm.sort_values("prio").drop_duplicates(["norma_origen", "articulo_origen", "norma_destino"])
        j = rev.merge(llm[["norma_origen", "articulo_origen", "norma_destino", "tipo"]].rename(columns={"tipo": "tipo_llm"}),
                      on=["norma_origen", "articulo_origen", "norma_destino"], how="left")
        j["tipo_llm"] = j.tipo_llm.fillna("NO_EXTRAIDA")
        res["llm"] = {"no_extraidas": int((j.tipo_llm == "NO_EXTRAIDA").sum()),
                      "muestra": metricas_tipo(j.tipo_correcto, j.tipo_llm, uno),
                      "poblacion_ponderada": metricas_tipo(j.tipo_correcto, j.tipo_llm, j.peso)}
        m = pd.crosstab(j.tipo_llm, j.tipo_correcto).reindex(columns=TIPOS, fill_value=0)
        matrices.append(m.assign(metodo="llm").reset_index().rename(columns={"tipo_llm": "predicho"}))
        j.to_csv(out / "casos_con_llm.csv", index=False, lineterminator="\n") if out.exists() else None

    out.mkdir(parents=True, exist_ok=True)
    escribir_texto(out / "metricas.json", json.dumps(res, indent=2, ensure_ascii=False))
    pd.concat(matrices).to_csv(out / "matrices.csv", index=False, lineterminator="\n")
    print(json.dumps(res, indent=1, ensure_ascii=False))
    print(pd.concat(matrices).to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--revision", type=Path, default=Path("docs/revision_manual/revision_tipos_78.csv"))
    ap.add_argument("--reglas", type=Path, default=Path("results/relaciones/relaciones_reglas_v2.csv"))
    ap.add_argument("--llm", type=Path, default=Path("results/relaciones_llm/relaciones_llm.csv"))
    ap.add_argument("--out", type=Path, default=Path("results/tipos"))
    a = ap.parse_args()
    main(a.revision, a.reglas, a.llm, a.out)
