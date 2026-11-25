"""Digesto UNNOBA, paso 1: catálogo de documentos (B56, B62).

El catálogo de 898 documentos únicos está incorporado dentro del descargador
tools/digesto_unnoba/descargar_pdfs_unnoba.py (base85 + zlib, armado en una sesión de
ChatGPT a partir de 11 secciones del digesto guardadas como HTML). Este script lo extrae y le
suma los PDF que se bajaron a mano antes y no están en el catálogo (origen = descarga_manual).

El digesto prohíbe el acceso automático (robots.txt), así que el script no se conecta a nada:
solo lee el descargador y la carpeta de PDF que bajó el equipo.

Salida: data/corpus_unnoba/catalogo.csv
    cod, titulo, archivo, normal, firmas, secciones (separadas por " | "), origen

Uso: python scripts/26_digesto_catalogo.py [--verificar]
     --verificar compara con el catálogo que ya está en el repositorio y no escribe nada.
"""

import argparse
import base64
import json
import re
import sys
import zlib
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
COMMAND = RAIZ / "tools/digesto_unnoba/descargar_pdfs_unnoba.py"   # antes .command (B75)
PDF = RAIZ / "data/textos/unnoba/pdf"
SALIDA = RAIZ / "data/corpus_unnoba/catalogo.csv"


def catalogo_embebido() -> list[dict]:
    lineas = COMMAND.read_text(encoding="utf-8").split("\n")
    i = next(k for k, l in enumerate(lineas) if l.startswith("_DOCUMENTOS = ("))
    partes = []
    for l in lineas[i + 1:]:
        if l.strip() == ")":
            break
        partes.append(l.strip()[1:-1])          # cada línea es un literal '...'
    return json.loads(zlib.decompress(base64.b85decode("".join(partes))).decode("utf-8"))


def titulo_de_archivo(nombre: str) -> str:
    """RES_HCS_Nº_004_07.pdf -> 'Resolución HCS Nº 4/07' (formato de las descargas a mano)."""
    m = re.match(r"(RES|ORD)_([A-Z]+)_N.?_0*(\d+)_(\d+)\.pdf$", nombre)
    if not m:
        return nombre[:-4]
    tipo = "Resolución" if m.group(1) == "RES" else "Ordenanza"
    return f"{tipo} {m.group(2)} Nº {m.group(3)}/{m.group(4)}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verificar", action="store_true")
    a = ap.parse_args()

    docs = catalogo_embebido()
    filas = [{**{k: d[k] for k in ("cod", "titulo", "archivo", "normal", "firmas")},
              "secciones": " | ".join(d["secciones"]), "origen": "catalogo_digesto"} for d in docs]
    en_catalogo = {d["archivo"] for d in docs}
    # PDF bajados a mano antes del descargador (no están en el catálogo ni son copias apartadas)
    for p in sorted(PDF.glob("*.pdf")):
        if p.name not in en_catalogo:
            filas.append({"cod": "", "titulo": titulo_de_archivo(p.name), "archivo": p.name, "normal": "",
                          "firmas": "", "secciones": "", "origen": "descarga_manual"})
    cat = pd.DataFrame(filas)
    print(len(docs), "del catálogo embebido +", (cat.origen == "descarga_manual").sum(), "descargas manuales =", len(cat))

    if a.verificar:
        viejo = pd.read_csv(SALIDA, dtype=str, keep_default_na=False)
        igual = viejo.equals(cat.astype(str))
        print("igual al catálogo del repositorio:", igual)
        sys.exit(0 if igual else 1)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    cat.to_csv(SALIDA, index=False)
    print("escrito", SALIDA.relative_to(RAIZ))


if __name__ == "__main__":
    main()
