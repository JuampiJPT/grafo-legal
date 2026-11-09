"""
01_obtener_corpus.py
TP Integrador - Sistemas Inteligentes (UNNOBA) - Problematica III

Descarga la Base Infoleg de Normativa Nacional y las Bases Complementarias de Normas
Modificatorias y Modificadas desde el Portal de Datos Abiertos de la Justicia Argentina y arma:

  - corpus_normas.csv     -> nodos del corpus (leyes, decretos y decretos-leyes)
  - gold_relaciones.csv   -> pares (modificatoria -> modificada) dentro del corpus
  - procedencia.json      -> URLs, fecha de descarga, SHA-256 de cada CSV y conteos

Corpus unico del TP (decision D11, bitacora B33): dominio laboral ampliado.
  Semillas de expansion: Ley 20.744 (LCT), Ley 27.802 (Modernizacion Laboral),
  Ley 24.013 (Empleo), Ley 24.557 (Riesgos del Trabajo) y Ley 23.551 (Asociaciones Sindicales).
  Se agregan como nodos, sin expandir, la Ley 14.250 y la Ley 27.742.

Criterio comun:
  1. Expansion a 1 salto desde las semillas: toda norma que modifica a una semilla o es
     modificada por ella, si es Ley, Decreto o Decreto/Ley.
  2. Gold = todos los pares de la base complementaria con origen y destino en el corpus.
  3. Split temporal por fecha (fecha_boletin, o fecha_sancion si falta): <= 2019-12-31 dev,
     posterior test. En el gold el split lo define la norma modificatoria.

El corpus oficial esta congelado en data/corpus (snapshot de InfoLEG del 06/11/2026).
Este script NO lo sobrescribe: escribe en otra carpeta y, con los mismos zips de data/raw,
tiene que dar exactamente los mismos archivos (correr_pipeline.sh lo verifica).

Uso:
    pip install -r requirements.txt
    python scripts/01_obtener_corpus.py --out data/verificacion/corpus_regenerado
"""

import argparse
import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

BASE = "https://datos.jus.gob.ar/dataset/d9a963ea-8b1d-4ca3-9dd9-07a4773e8c23/resource"
URLS = {
    "base": f"{BASE}/bf0ec116-ad4e-4572-a476-e57167a84403/download/base-infoleg-normativa-nacional.zip",
    "modificatorias": f"{BASE}/dea3c247-5a5d-408f-a224-39ae0f8eb371/download/base-complementaria-infoleg-normas-modificatorias.zip",
    "modificadas": f"{BASE}/0c4fdafe-f4e8-4ac2-bc2e-acf50c27066d/download/base-complementaria-infoleg-normas-modificadas.zip",
}
HEADERS = {"User-Agent": "TP-UNNOBA-SistemasInteligentes/1.0 (uso academico)"}

SEMILLAS_EXPANSION = {25552, 423680, 412, 27971, 20993}  # Leyes 20.744, 27.802, 24.013, 24.557, 23.551
SEMILLAS_SIN_EXPANDIR = {46379, 401266}  # Ley 14.250, Ley 27.742
TIPOS = {"Ley", "Decreto", "Decreto/Ley"}
CORTE = "2019-12-31"
CONGELADO = Path("data/corpus")


def descargar(nombre: str, url: str, raw_dir: Path) -> tuple[pd.DataFrame, dict]:
    """Descarga el zip (con cache local), registra su SHA-256 y devuelve el CSV."""
    destino = raw_dir / f"{nombre}.zip"
    if not destino.exists():
        print(f"descargando {nombre} ...", flush=True)
        r = requests.get(url, timeout=600, headers=HEADERS)
        r.raise_for_status()
        destino.write_bytes(r.content)
    with zipfile.ZipFile(destino) as z:
        csv_name = [n for n in z.namelist() if n.endswith(".csv")][0]
        data = z.read(csv_name)
    sha = hashlib.sha256(data).hexdigest()
    df = pd.read_csv(io.BytesIO(data), dtype=str, keep_default_na=False, encoding="utf-8-sig")
    return df, {"archivo": csv_name, "sha256_csv": sha, "filas": len(df),
                "sha256_zip": hashlib.sha256(destino.read_bytes()).hexdigest()}


def main(out: Path, raw_dir: Path) -> None:
    if out.resolve() == CONGELADO.resolve():
        raise SystemExit("data/corpus esta congelado (snapshot 06/11/2026); usa otra carpeta de salida")
    raw_dir.mkdir(parents=True, exist_ok=True)
    expansion = SEMILLAS_EXPANSION

    procedencia = {"fecha_descarga": datetime.now(timezone.utc).isoformat(),
                   "semillas_expansion": sorted(expansion), "semillas_sin_expandir": sorted(SEMILLAS_SIN_EXPANDIR),
                   "fuentes": {}}
    tablas = {}
    for nombre in ("base", "modificatorias", "modificadas"):
        df, info = descargar(nombre, URLS[nombre], raw_dir)
        tablas[nombre] = df
        procedencia["fuentes"][nombre] = {"url": URLS[nombre], **info}
    base, mod = tablas["base"], tablas["modificatorias"]

    base["id_norma"] = base["id_norma"].astype(int)
    mod["id_norma_modificatoria"] = mod["id_norma_modificatoria"].astype(int)
    mod["id_norma_modificada"] = mod["id_norma_modificada"].astype(int)

    pares = mod[["id_norma_modificatoria", "id_norma_modificada"]].drop_duplicates()
    procedencia["pares_unicos_base_completa"] = len(pares)
    info_base = base.drop_duplicates("id_norma").set_index("id_norma")
    tipo = info_base["tipo_norma"].to_dict()
    fecha = (info_base["fecha_boletin"].where(info_base["fecha_boletin"] != "", info_base["fecha_sancion"])).to_dict()

    # --- Expansion a 1 salto ---
    corpus = set(expansion) | set(SEMILLAS_SIN_EXPANDIR)
    for s in expansion:
        vecinos = set(pares.loc[pares.id_norma_modificatoria == s, "id_norma_modificada"]) | \
                  set(pares.loc[pares.id_norma_modificada == s, "id_norma_modificatoria"])
        corpus |= {v for v in vecinos if tipo.get(v) in TIPOS}

    def split(i):
        return "dev" if fecha.get(i, "") <= CORTE else "test"

    # --- Nodos ---
    cols = ["id_norma", "tipo_norma", "numero_norma", "clase_norma", "organismo_origen",
            "fecha_sancion", "fecha_boletin", "titulo_resumido", "titulo_sumario",
            "texto_actualizado", "texto_original", "modificada_por", "modifica_a"]
    nodos = base[base.id_norma.isin(corpus)].drop_duplicates("id_norma")[cols].copy()
    nodos = nodos.rename(columns={"modificada_por": "modificada_por_total", "modifica_a": "modifica_a_total"})
    semillas = expansion | SEMILLAS_SIN_EXPANDIR
    nodos["rol"] = nodos.id_norma.map(lambda i: "semilla" if i in semillas else "expansion")
    nodos["split"] = nodos.id_norma.map(split)
    nodos["tiene_link_texto"] = ((nodos.texto_original != "") | (nodos.texto_actualizado != "")).map({True: "si", False: "no"})
    nodos["_f"] = nodos.id_norma.map(fecha)
    nodos = nodos.sort_values(["_f", "id_norma"]).drop(columns="_f")

    # --- Gold ---
    g = pares[pares.id_norma_modificatoria.isin(corpus) & pares.id_norma_modificada.isin(corpus)].copy()

    def etiqueta(i):
        return f"{tipo[i]} {info_base.at[i, 'numero_norma']}"

    g["norma_modificatoria"] = g.id_norma_modificatoria.map(etiqueta)
    g["fecha_modificatoria"] = g.id_norma_modificatoria.map(fecha)
    g["norma_modificada"] = g.id_norma_modificada.map(etiqueta)
    g["split"] = g.id_norma_modificatoria.map(split)
    g = g.sort_values(["fecha_modificatoria", "id_norma_modificatoria", "id_norma_modificada"])
    g = g[["id_norma_modificatoria", "norma_modificatoria", "fecha_modificatoria",
           "id_norma_modificada", "norma_modificada", "split"]]

    out.mkdir(parents=True, exist_ok=True)
    nodos.to_csv(out / "corpus_normas.csv", index=False, lineterminator="\n")
    g.to_csv(out / "gold_relaciones.csv", index=False, lineterminator="\n")

    procedencia["resultado"] = {
        "normas": len(nodos),
        "normas_con_link_texto": int((nodos.tiene_link_texto == "si").sum()),
        "pares_gold": len(g),
        "pares_por_split": g.split.value_counts().to_dict(),
        "sha256_corpus_normas": hashlib.sha256((out / "corpus_normas.csv").read_bytes()).hexdigest(),
        "sha256_gold_relaciones": hashlib.sha256((out / "gold_relaciones.csv").read_bytes()).hexdigest(),
    }
    (out / "procedencia.json").write_text(json.dumps(procedencia, indent=2, ensure_ascii=False))
    print(json.dumps(procedencia["resultado"], indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--raw", type=Path, default=Path("data/raw"))
    a = ap.parse_args()
    main(a.out, a.raw)
