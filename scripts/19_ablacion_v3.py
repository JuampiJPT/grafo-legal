"""
19_ablacion_v3.py
Ablacion de las reglas v3 sobre DEV: cuanto aporta cada cambio. Se apaga un cambio por vez y se
mide la configuracion F3; tambien se prende uno por vez sobre la v2. No mira test.

Uso:
    python scripts/19_ablacion_v3.py
"""

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from grafo_legal.archivos import escribir_texto        # noqa: E402
from grafo_legal.catalogo import Catalogo              # noqa: E402
from grafo_legal.evaluacion import prf                 # noqa: E402
from grafo_legal.extractores import reglas_v3          # noqa: E402

TODOS = set(reglas_v3.CAMBIOS)


def medir(cambios: set, cat, gold, split_de) -> dict:
    reglas_v3.CAMBIOS.clear()
    reglas_v3.CAMBIOS.update(cambios)
    filtro = reglas_v3.CONFIGS["F3_alias_con_verbo"]
    pred = set()
    for i in sorted(cat.normas):
        if split_de[i] != "dev":
            continue
        for e in reglas_v3.extraer(i, Path("data/textos/infoleg/html"), cat) or []:
            if filtro(e):
                pred.add((e.id_origen, e.id_destino))
    return prf(pred, gold)


def main() -> None:
    cat = Catalogo.desde_corpus(Path("data/corpus/corpus_normas.csv"))
    normas = pd.read_csv("data/corpus/corpus_normas.csv")
    split_de = dict(zip(normas.id_norma, normas.split))
    g = pd.read_csv("data/corpus/gold_relaciones.csv")
    gold = set(zip(g[g.split == "dev"].id_norma_modificatoria, g[g.split == "dev"].id_norma_modificada))
    filas = [{"variante": "v3 completa", **medir(TODOS, cat, gold, split_de)},
             {"variante": "v2 (ningun cambio)", **medir(set(), cat, gold, split_de)}]
    for c in sorted(TODOS):
        filas.append({"variante": f"v3 sin {c}", **medir(TODOS - {c}, cat, gold, split_de)})
        filas.append({"variante": f"v2 + {c}", **medir({c}, cat, gold, split_de)})
    reglas_v3.CAMBIOS.clear()
    reglas_v3.CAMBIOS.update(TODOS)
    df = pd.DataFrame(filas)
    out = Path("results/reglas_v3")
    df.to_csv(out / "ablacion_dev.csv", index=False, lineterminator="\n")
    escribir_texto(out / "ablacion_dev.json", json.dumps(filas, indent=2, ensure_ascii=False))
    print(df[["variante", "pred", "tp", "fp", "fn", "precision", "recall", "f1"]].to_string(index=False))


if __name__ == "__main__":
    main()
