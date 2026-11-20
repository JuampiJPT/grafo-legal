"""Digesto UNNOBA, paso 3: texto de los PDF (B57, B62).

  1. pdftotext -layout para cada PDF del catálogo -> data/textos/unnoba/txt/<archivo>.txt
  2. Un PDF es escaneado si pdftotext no devuelve texto (menos de 200 caracteres). A esos se
     les puede hacer OCR: cada página a imagen (pdftoppm -r 200 -gray) y tesseract en español
     (-l spa). El texto del OCR reemplaza al de pdftotext en el mismo .txt.
  3. data/corpus_unnoba/textos.csv: archivo, caracteres de pdftotext, escaneado, ocr.

Los .txt NO van a git (tienen nombres y DNI). textos.csv sí (solo nombres de archivo).

OCR: tesseract necesita los datos de idioma. Si no están instalados, bajar spa.traineddata
(https://github.com/tesseract-ocr/tessdata) a una carpeta y exportar TESSDATA_PREFIX.
El OCR no es reproducible byte a byte entre versiones o parámetros: los resultados de la PI4
corresponden a los textos guardados (data/textos/unnoba/muestra_pi4_textos.jsonl). Por eso,
por defecto, no se rehace un .txt que ya existe.

Uso:
  python scripts/28_digesto_textos.py                 # pdftotext de lo que falte, sin OCR
  python scripts/28_digesto_textos.py --ocr muestra   # OCR de los escaneados de la muestra PI4
  python scripts/28_digesto_textos.py --ocr todos     # OCR de todos los escaneados (lleva horas)
  python scripts/28_digesto_textos.py --rehacer       # vuelve a generar aunque exista el .txt
"""

import argparse
import subprocess
import tempfile
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
PDF = RAIZ / "data/textos/unnoba/pdf"
TXT = RAIZ / "data/textos/unnoba/txt"
CAT = RAIZ / "data/corpus_unnoba/catalogo.csv"
MUESTRA = RAIZ / "data/corpus_unnoba/muestra_pi4.csv"
SALIDA = RAIZ / "data/corpus_unnoba/textos.csv"
MIN_CHARS = 200


def pdftotext(pdf: Path) -> str:
    return subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout


def ocr(pdf: Path) -> str:
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["pdftoppm", "-r", "200", "-gray", "-png", str(pdf), f"{d}/p"], check=True)
        partes = []
        for img in sorted(Path(d).glob("p*.png")):
            r = subprocess.run(["tesseract", str(img), "stdout", "-l", "spa"], capture_output=True, text=True)
            partes.append(r.stdout)
        return "\n".join(partes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ocr", choices=["no", "muestra", "todos"], default="no")
    ap.add_argument("--rehacer", action="store_true")
    a = ap.parse_args()
    TXT.mkdir(parents=True, exist_ok=True)
    cat = pd.read_csv(CAT, dtype=str, keep_default_na=False)
    en_muestra = set(pd.read_csv(MUESTRA, dtype=str).archivo) if MUESTRA.exists() else set()
    previo = pd.read_csv(SALIDA, dtype=str).set_index("archivo") if SALIDA.exists() else pd.DataFrame()

    filas = []
    for i, arch in enumerate(cat.archivo, 1):
        pdf, txt = PDF / arch, TXT / (arch[:-4] + ".txt")
        if not pdf.exists():
            filas.append({"archivo": arch, "chars_pdftotext": "", "escaneado": "", "ocr": "falta el PDF"})
            continue
        crudo = pdftotext(pdf)
        escaneado = len(crudo.strip()) < MIN_CHARS
        hizo_ocr = str(previo.loc[arch, "ocr"]) if arch in previo.index else "no"
        if a.rehacer or not txt.exists():
            txt.write_text(crudo, encoding="utf-8")
            hizo_ocr = "no"
        quiere_ocr = escaneado and (a.ocr == "todos" or (a.ocr == "muestra" and arch in en_muestra))
        if quiere_ocr and (a.rehacer or len(txt.read_text(encoding="utf-8", errors="ignore").strip()) < MIN_CHARS):
            print(f"[{i}/{len(cat)}] OCR {arch}", flush=True)
            txt.write_text(ocr(pdf), encoding="utf-8")
            hizo_ocr = "tesseract spa, pdftoppm 200 dpi gris"
        elif escaneado and len(txt.read_text(encoding="utf-8", errors="ignore").strip()) >= MIN_CHARS and hizo_ocr == "no":
            hizo_ocr = "tesseract spa (texto guardado antes)"
        filas.append({"archivo": arch, "chars_pdftotext": len(crudo.strip()), "escaneado": escaneado, "ocr": hizo_ocr})
    t = pd.DataFrame(filas)
    t.to_csv(SALIDA, index=False)
    print(f"{len(t)} documentos; escaneados: {int((t.escaneado == True).sum())}; con OCR: {int(t.ocr.str.startswith('tesseract').sum())}")


if __name__ == "__main__":
    main()
