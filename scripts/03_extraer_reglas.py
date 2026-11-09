"""
03_extraer_reglas.py
Corre el parser de reglas (regex/AST) sobre todas las normas del corpus con texto y guarda
una evidencia por mencion resuelta. No lee el gold.

Uso:
    python scripts/03_extraer_reglas.py --corpus data/corpus --out results/reglas
    python scripts/03_extraer_reglas.py --parser v2 --out results/reglas_v2
"""

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from grafo_legal.archivos import abrir_para_escribir, escribir_texto  # noqa: E402
from grafo_legal.catalogo import Catalogo                              # noqa: E402
import importlib                                                       # noqa: E402


def main(corpus: Path, html_dir: Path, out: Path, parser: str = "v1") -> None:
    mod = importlib.import_module("grafo_legal.extractores." + ("reglas" if parser == "v1" else "reglas_v2"))
    a_dict, extraer = mod.a_dict, mod.extraer
    cat = Catalogo.desde_corpus(corpus / "corpus_normas.csv")
    out.mkdir(parents=True, exist_ok=True)
    filas, sin_texto = [], []
    for id_norma in sorted(cat.normas):
        ev = extraer(id_norma, html_dir, cat)
        if ev is None:
            sin_texto.append(id_norma)
            continue
        filas += [a_dict(e) for e in ev]
    with abrir_para_escribir(out / "evidencias.csv") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(filas)
    print(f"{len(filas)} evidencias de {len(cat.normas) - len(sin_texto)} normas; "
          f"{len(sin_texto)} normas sin texto")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=Path("data/corpus"))
    ap.add_argument("--html", type=Path, default=Path("data/textos/infoleg/html"))
    ap.add_argument("--out", type=Path, default=Path("results/reglas"))
    ap.add_argument("--parser", choices=["v1", "v2"], default="v1")
    a = ap.parse_args()
    main(a.corpus, a.html, a.out, a.parser)
