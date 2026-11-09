"""
07_armar_dataset.py
Arma el dataset del TP a partir de los textos de InfoLEG y las menciones detectadas.

Salidas en data/dataset/:

  articulos.csv        una fila por segmento de cada norma (encabezado, articulo, anexo o notas),
                       con su texto limpio y sus offsets. Es la entrada de los parsers LLM e hibrido.
  pares_candidatos.csv una fila por par (norma origen -> norma destino) que el detector de menciones
                       propone, con atributos numericos y categoricos y la etiqueta en_gold.
                       Es la matriz para un clasificador (scikit-learn) y para elegir ejemplos
                       few-shot.
  resumen.json         conteos, cobertura de los candidatos sobre el gold y descripcion de columnas.

Reglas para no filtrar informacion del gold hacia los atributos:
  - Ningun atributo usa el gold ni los conteos de InfoLEG (modificada_por_total, modifica_a_total),
    que se derivan de las mismas relaciones.
  - La etiqueta en_gold esta en dev y en test. La de test solo se usa para la evaluacion final
    (bitacora B16); cualquier ajuste o entrenamiento usa solo filas con split == "dev".

Uso:
    python scripts/07_armar_dataset.py --corpus data/corpus --res results/reglas --out data/dataset
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from grafo_legal.archivos import escribir_texto            # noqa: E402
from grafo_legal.catalogo import Catalogo                   # noqa: E402
from grafo_legal.fuentes.infoleg import cargar              # noqa: E402

SEMILLAS = {25552, 423680, 412, 27971, 20993, 46379, 401266}

DESCRIPCION_PARES = {
    "id_norma_origen": "norma que contiene la mencion (candidata a modificatoria)",
    "id_norma_destino": "norma mencionada, resuelta contra el catalogo del corpus",
    "split": "dev o test, segun la fecha de la norma origen (corte 31/12/2019)",
    "n_menciones": "menciones del destino en toda la norma origen",
    "n_menc_articulado": "menciones en el articulado",
    "n_menc_encabezado": "menciones en el encabezado (VISTO, CONSIDERANDO)",
    "n_menc_anexo": "menciones en anexos",
    "n_menc_notas": "menciones en notas de InfoLEG",
    "n_articulos": "articulos distintos que mencionan al destino",
    "frac_articulos": "n_articulos / articulos de la norma origen",
    "verbo_en_articulo": "1 si algun articulo con la mencion tiene un verbo modificatorio",
    "verbo_en_oracion": "1 si alguna oracion con la mencion tiene un verbo modificatorio",
    "solo_alias": "1 si el destino solo se menciona por nombre propio, sin numero",
    "temporal_ok": "1 si el destino no es posterior a la norma origen",
    "pos_primera_mencion": "offset de la primera mencion / largo del texto (0 = al principio)",
    "largo_texto": "caracteres del texto limpio de la norma origen",
    "dif_anios": "anios entre la norma origen y la norma destino",
    "tipo_origen": "ley, decreto o decreto/ley",
    "tipo_destino": "ley, decreto o decreto/ley",
    "destino_es_semilla": "1 si el destino es una de las semillas del corpus",
    "en_gold": "ETIQUETA: 1 si el par esta en el gold de InfoLEG",
}


def armar_articulos(corpus: Path, html_dir: Path) -> pd.DataFrame:
    normas = pd.read_csv(corpus / "corpus_normas.csv", dtype=str, keep_default_na=False)
    filas = []
    for r in normas.itertuples(index=False):
        doc = cargar(r.id_norma, html_dir)
        if doc is None:
            continue
        texto, arts = doc
        for orden, a in enumerate(arts):
            filas.append({
                "id_norma": int(r.id_norma), "norma": f"{r.tipo_norma} {r.numero_norma}",
                "tipo_norma": r.tipo_norma, "fecha": r.fecha_boletin or r.fecha_sancion, "split": r.split,
                "orden": orden, "zona": a.zona, "articulo": a.numero,
                "inicio": a.inicio, "fin": a.fin, "n_chars": a.fin - a.inicio,
                "largo_norma": len(texto), "texto": a.texto,
            })
    return pd.DataFrame(filas)


def armar_pares(corpus: Path, res: Path, art: pd.DataFrame) -> pd.DataFrame:
    ev = pd.read_csv(res / "evidencias.csv", dtype={"articulo": str}, keep_default_na=False)
    for c in ("verbo_articulo", "verbo_oracion"):
        ev[c] = (ev[c] != "").astype(int)
    ev["temporal_ok"] = (ev["temporal_ok"].astype(str) == "True").astype(int)
    ev["es_alias"] = (ev["metodo"] == "alias").astype(int)
    for z in ("articulado", "encabezado", "anexo", "notas"):
        ev[f"z_{z}"] = (ev["zona"] == z).astype(int)
    ev["art_mencion"] = ev["articulo"].where(ev["zona"] == "articulado")

    g = ev.groupby(["id_origen", "id_destino"])
    pares = pd.DataFrame({
        "n_menciones": g.size(),
        "n_menc_articulado": g["z_articulado"].sum(),
        "n_menc_encabezado": g["z_encabezado"].sum(),
        "n_menc_anexo": g["z_anexo"].sum(),
        "n_menc_notas": g["z_notas"].sum(),
        "n_articulos": g["art_mencion"].nunique(),
        "verbo_en_articulo": g["verbo_articulo"].max(),
        "verbo_en_oracion": g["verbo_oracion"].max(),
        "solo_alias": g["es_alias"].min(),
        "temporal_ok": g["temporal_ok"].min(),
        "primer_inicio": g["inicio"].min(),
    }).reset_index().rename(columns={"id_origen": "id_norma_origen", "id_destino": "id_norma_destino"})

    largo = art.groupby("id_norma")["largo_norma"].first()
    n_art = art[art.zona == "articulado"].groupby("id_norma").size()
    pares["largo_texto"] = pares.id_norma_origen.map(largo)
    pares["pos_primera_mencion"] = (pares.primer_inicio / pares.largo_texto).round(4)
    pares["frac_articulos"] = (pares.n_articulos / pares.id_norma_origen.map(n_art).fillna(1).clip(lower=1)).round(4)
    pares = pares.drop(columns="primer_inicio")

    cat = Catalogo.desde_corpus(corpus / "corpus_normas.csv")
    split = pd.read_csv(corpus / "corpus_normas.csv", dtype=str).set_index("id_norma")["split"]
    pares["split"] = pares.id_norma_origen.astype(str).map(split)
    pares["tipo_origen"] = pares.id_norma_origen.map(lambda i: cat.normas[i].tipo)
    pares["tipo_destino"] = pares.id_norma_destino.map(lambda i: cat.normas[i].tipo)
    anio = {i: n.anio for i, n in cat.normas.items()}
    pares["dif_anios"] = pares.id_norma_origen.map(anio) - pares.id_norma_destino.map(anio)
    pares["destino_es_semilla"] = pares.id_norma_destino.isin(SEMILLAS).astype(int)

    gold = pd.read_csv(corpus / "gold_relaciones.csv")
    claves = set(zip(gold.id_norma_modificatoria, gold.id_norma_modificada))
    pares["en_gold"] = [int((a, b) in claves) for a, b in zip(pares.id_norma_origen, pares.id_norma_destino)]
    return pares[list(DESCRIPCION_PARES)].sort_values(["split", "id_norma_origen", "id_norma_destino"])


def main(corpus: Path, html_dir: Path, res: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    art = armar_articulos(corpus, html_dir)
    pares = armar_pares(corpus, res, art)

    for nombre, df in (("articulos.csv", art), ("pares_candidatos.csv", pares)):
        tmp = out / f".{nombre}.tmp"
        df.to_csv(tmp, index=False, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        tmp.replace(out / nombre)

    gold = pd.read_csv(corpus / "gold_relaciones.csv")
    resumen = {"articulos": {"filas": len(art), "normas": int(art.id_norma.nunique()),
                             "por_zona": art.zona.value_counts().to_dict(),
                             "chars_total": int(art.n_chars.sum()),
                             "chars_por_articulo_mediana": float(np.median(art.loc[art.zona == "articulado", "n_chars"]))},
               "pares_candidatos": {"filas": len(pares), "por_split": pares.split.value_counts().to_dict(),
                                    "positivos_por_split": pares.groupby("split").en_gold.sum().to_dict()}}
    # cobertura de los candidatos: que parte del gold aparece como candidato (techo del clasificador)
    for s in ("dev", "test"):
        g_s = gold[gold.split == s]
        pos = pares[(pares.split == s) & (pares.en_gold == 1)]
        resumen["pares_candidatos"][f"recall_candidatos_{s}"] = round(len(pos) / len(g_s), 4)
    resumen["columnas_pares_candidatos"] = DESCRIPCION_PARES
    escribir_texto(out / "resumen.json", json.dumps(resumen, indent=2, ensure_ascii=False, default=int))
    print(json.dumps({k: v for k, v in resumen.items() if k != "columnas_pares_candidatos"},
                     indent=2, ensure_ascii=False, default=int))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=Path("data/corpus"))
    ap.add_argument("--html", type=Path, default=Path("data/textos/infoleg/html"))
    ap.add_argument("--res", type=Path, default=Path("results/reglas"))
    ap.add_argument("--out", type=Path, default=Path("data/dataset"))
    a = ap.parse_args()
    main(a.corpus, a.html, a.res, a.out)
