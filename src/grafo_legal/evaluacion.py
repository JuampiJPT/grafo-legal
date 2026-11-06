"""Evaluacion a nivel de par (origen -> destino) contra el gold de InfoLEG."""

from __future__ import annotations

import csv
from pathlib import Path


def cargar_gold(corpus: Path) -> list[dict]:
    with open(corpus / "gold_relaciones.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def prf(pred: set, gold: set) -> dict:
    tp = len(pred & gold)
    p = tp / len(pred) if pred else 0.0
    r = tp / len(gold) if gold else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return {"pred": len(pred), "gold": len(gold), "tp": tp, "fp": len(pred - gold), "fn": len(gold - pred),
            "precision": round(p, 4), "recall": round(r, 4), "f1": round(f, 4)}
