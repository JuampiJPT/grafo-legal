"""Digesto UNNOBA, paso 4: muestra de la PI4 (B57, B62).

Muestra de 70 documentos, con semilla 20261120:
  - las 7 ordenanzas del catálogo;
  - todas las resoluciones (no ordenanzas) de las secciones de reglamentos: Reglamentación,
    Cursadas, Regularidades, Reglamento Trabajo Final e Ingreso (48). El criterio dice en cuáles
    está («tema:Cursadas/Regularidades»);
  - 15 documentos al azar del resto: random.Random(20261120).sample(resto, 15), con el resto en
    el orden del catálogo («negativo_aleatorio»: se esperaba que tuvieran pocas relaciones).

Salidas:
  data/corpus_unnoba/muestra_pi4.csv             archivo, titulo, cod, criterio, secciones, tiene_texto
  data/textos/unnoba/muestra_pi4_textos.jsonl     lo mismo y el texto (de txt/, con OCR si es escaneado);
                                                  NO va a git (nombres y DNI)

Uso: python scripts/29_digesto_muestra.py [--verificar] [--cuerpos]
     --verificar compara con los archivos que ya están y no escribe nada.
     --cuerpos   escribe data/textos/unnoba/cuerpos_muestra.txt, el texto de cada documento hasta
                 el artículo «Regístrese/Comuníquese» (+200 caracteres), sin anexos ni firmas: es
                 lo que se leyó para anotar el gold (data/corpus_unnoba/gold_pi4.tsv). No va a git.
"""

import argparse
import json
import random
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
CAT = RAIZ / "data/corpus_unnoba/catalogo.csv"
TEXTOS = RAIZ / "data/corpus_unnoba/textos.csv"
TXT = RAIZ / "data/textos/unnoba/txt"
MUESTRA = RAIZ / "data/corpus_unnoba/muestra_pi4.csv"
JSONL = RAIZ / "data/textos/unnoba/muestra_pi4_textos.jsonl"
CUERPOS = RAIZ / "data/textos/unnoba/cuerpos_muestra.txt"
SEMILLA = 20261120
TEMAS = ["Reglamentación", "Cursadas", "Regularidades", "Reglamento Trabajo Final", "Ingreso"]
N_NEGATIVOS = 15


def armar() -> pd.DataFrame:
    cat = pd.read_csv(CAT, dtype=str, keep_default_na=False)
    tex = pd.read_csv(TEXTOS, dtype=str).set_index("archivo")
    secc = cat.secciones.str.split(" | ", regex=False)
    ordenanza = cat.titulo.str.startswith("Ordenanza")
    temas = secc.map(lambda s: [t for t in TEMAS if t in s])
    cat["criterio"] = ""
    cat.loc[ordenanza, "criterio"] = "ordenanza"
    con_tema = ~ordenanza & (temas.str.len() > 0)
    cat.loc[con_tema, "criterio"] = "tema:" + temas[con_tema].str.join("/")
    elegidos = cat[cat.criterio != ""]
    resto = cat[cat.criterio == ""]
    azar = random.Random(SEMILLA).sample(list(resto.archivo), N_NEGATIVOS)
    neg = resto.set_index("archivo").loc[azar].reset_index().assign(criterio="negativo_aleatorio")
    orden = pd.concat([neg,
                       elegidos[elegidos.criterio == "ordenanza"],
                       elegidos[elegidos.criterio != "ordenanza"].sort_values("criterio", kind="stable")])
    orden["tiene_texto"] = orden.archivo.map(lambda a: str(tex.loc[a, "escaneado"] != "True"))
    return orden[["archivo", "titulo", "cod", "criterio", "secciones", "tiene_texto"]].reset_index(drop=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verificar", action="store_true")
    ap.add_argument("--cuerpos", action="store_true")
    a = ap.parse_args()
    m = armar()
    print(m.criterio.value_counts().to_dict(), "total", len(m))
    if a.verificar:
        viejo = pd.read_csv(MUESTRA, dtype=str, keep_default_na=False)
        igual = viejo.equals(m.astype(str))
        print("muestra igual a la del repositorio:", igual)
        if JSONL.exists():
            js = [json.loads(l) for l in JSONL.read_text(encoding="utf-8").splitlines() if l.strip()]
            textos_iguales = all(j["archivo"] == r.archivo and
                                 j["texto"] == (TXT / (r.archivo[:-4] + ".txt")).read_text(encoding="utf-8")
                                 for j, r in zip(js, m.itertuples()))
            print("textos del jsonl iguales a txt/:", textos_iguales and len(js) == len(m))
        sys.exit(0 if igual else 1)
    m.to_csv(MUESTRA, index=False)
    with JSONL.open("w", encoding="utf-8") as f:
        for r in m.to_dict("records"):
            r["texto"] = (TXT / (r["archivo"][:-4] + ".txt")).read_text(encoding="utf-8")
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("escritos", MUESTRA.relative_to(RAIZ), "y", JSONL.relative_to(RAIZ))
    if a.cuerpos:
        import re
        cierre = re.compile(r"(Reg[ií]strese|Comun[ií]quese)", re.I)
        with CUERPOS.open("w", encoding="utf-8") as f:
            for i, r in enumerate(m.itertuples()):
                t = (TXT / (r.archivo[:-4] + ".txt")).read_text(encoding="utf-8")
                k = cierre.search(t)
                f.write(f"===== DOC {i:02d} | {r.archivo} | {r.titulo} | {r.criterio} =====\n")
                f.write((t[: k.end() + 200] if k else t) + "\n\n")
        print("escrito", CUERPOS.relative_to(RAIZ))


if __name__ == "__main__":
    main()
