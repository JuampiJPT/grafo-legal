"""Digesto UNNOBA, paso 2: copias repetidas de los PDF (B56, B62).

Al juntar las descargas (el descargador del catálogo y bajadas a mano anteriores) quedaron
archivos con el mismo contenido y distinto nombre («RES_HCS_Nº_044_08.pdf» y
«RESOLUCION200844.pdf») y copias «(1)», «(2)». Se deja un PDF por documento y las copias van a
data/textos/unnoba/pdf/_duplicados/ con el motivo en LEEME.csv. No se borra nada.

Regla para elegir cuál queda: el nombre del catálogo del digesto; si ninguno está en el
catálogo, el nombre sin «(n)»; si no, el más corto.

Uso:
  python scripts/27_digesto_duplicados.py            # informa, no mueve nada
  python scripts/27_digesto_duplicados.py --mover    # mueve las copias nuevas a _duplicados/
"""

import argparse
import hashlib
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
PDF = RAIZ / "data/textos/unnoba/pdf"
DUP = PDF / "_duplicados"
COMMAND_CAT = RAIZ / "data/corpus_unnoba/catalogo.csv"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mover", action="store_true")
    a = ap.parse_args()
    cat = pd.read_csv(COMMAND_CAT, dtype=str, keep_default_na=False)
    del_digesto = set(cat[cat.origen == "catalogo_digesto"].archivo)

    grupos = defaultdict(list)
    for p in PDF.glob("*.pdf"):
        grupos[sha(p)].append(p)
    nuevas = []
    for h, ps in grupos.items():
        if len(ps) < 2:
            continue
        ps.sort(key=lambda p: (p.name not in del_digesto, bool(re.search(r"\(\d+\)", p.name)), len(p.name), p.name))
        queda = ps[0]
        for p in ps[1:]:
            motivo = (f"copia de {queda.name}" if re.sub(r" \(\d+\)", "", p.name) == queda.name
                      else f"mismo contenido que {queda.name}")
            nuevas.append((p, motivo))

    # verificación de lo que ya está apartado: cada copia tiene su original en pdf/ o en _duplicados/
    leeme = pd.read_csv(DUP / "LEEME.csv", dtype=str) if (DUP / "LEEME.csv").exists() else pd.DataFrame(columns=["archivo", "motivo"])
    hashes_pdf = set(grupos)
    sin_original = [f for f in leeme.archivo if (DUP / f).exists() and sha(DUP / f) not in hashes_pdf]
    print(f"PDF en pdf/: {sum(len(v) for v in grupos.values())} ({len(grupos)} contenidos distintos)")
    print(f"copias ya apartadas: {len(leeme)}; sin original en pdf/: {len(sin_original)} {sin_original[:5]}")
    print(f"copias nuevas: {len(nuevas)}")
    for p, m in nuevas:
        print("  ", p.name, "->", m)

    if a.mover and nuevas:
        DUP.mkdir(exist_ok=True)
        for p, m in nuevas:
            p.rename(DUP / p.name)
        leeme = pd.concat([leeme, pd.DataFrame([{"archivo": p.name, "motivo": m} for p, m in nuevas])])
        leeme.sort_values("archivo").to_csv(DUP / "LEEME.csv", index=False)
        print("movidas", len(nuevas))


if __name__ == "__main__":
    main()
