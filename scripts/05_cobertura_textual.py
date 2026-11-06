"""
05_cobertura_textual.py
Techo de recall textual: para cada par del gold, mira si el texto de la norma modificatoria
menciona a la norma modificada.

  numero       el texto cita la norma por tipo y numero (resuelve contra el catalogo)
  solo_nombre  la cita solo por su nombre propio (ej. "Ley de Contrato de Trabajo")
  sin_mencion  hay texto pero no la menciona: ningun extractor textual puede recuperar el par
  sin_texto    InfoLEG no publica texto de la modificatoria

Es un analisis del dataset, no un extractor: usa el gold para elegir que pares mirar.

Uso:
    python scripts/05_cobertura_textual.py --corpus data/corpus_v1
"""

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from grafo_legal.catalogo import Catalogo                     # noqa: E402
from grafo_legal.extractores.menciones import detectar, detectar_alias  # noqa: E402
from grafo_legal.fuentes.infoleg import cargar                # noqa: E402


def main(corpus: Path, html_dir: Path, out: Path) -> None:
    cat = Catalogo.desde_corpus(corpus / "corpus_normas.csv")
    with open(corpus / "gold_relaciones.csv", encoding="utf-8") as f:
        gold = list(csv.DictReader(f))

    cache: dict[int, tuple[set[int], set[int]] | None] = {}
    filas = []
    for g in gold:
        src, dst = int(g["id_norma_modificatoria"]), int(g["id_norma_modificada"])
        if src not in cache:
            doc = cargar(src, html_dir)
            if doc is None:
                cache[src] = None
            else:
                texto, _ = doc
                por_num = {n.id for m in detectar(texto) if (n := cat.resolver(m.tipo, m.numero, m.anio))}
                por_alias = {a[0] for a in detectar_alias(texto)}
                cache[src] = (por_num, por_alias)
        c = cache[src]
        if c is None:
            cat_ = "sin_texto"
        elif dst in c[0]:
            cat_ = "numero"
        elif dst in c[1]:
            cat_ = "solo_nombre"
        else:
            cat_ = "sin_mencion"
        filas.append({"id_norma_modificatoria": src, "norma_modificatoria": g["norma_modificatoria"],
                      "id_norma_modificada": dst, "norma_modificada": g["norma_modificada"],
                      "split": g["split"], "mencion_en_texto": cat_})

    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(filas)
    print(Counter(r["mencion_en_texto"] for r in filas))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=Path("data/corpus_v1"))
    ap.add_argument("--html", type=Path, default=Path("data/textos/infoleg/html"))
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    main(a.corpus, a.html, a.out or a.corpus / "cobertura_textual_gold.csv")
