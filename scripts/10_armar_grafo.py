"""
10_armar_grafo.py
Arma el grafo normativo a partir de la salida estandar de relaciones y, si se le da una conexion,
lo carga en Neo4j. El grafo no lee el gold de InfoLEG: InfoLEG se usa solo para evaluar
(scripts/11_evaluar_grafo.py).

Modelo (docs/grafo.md):
  (:Norma)-[:CONTIENE]->(:Articulo)
  (:Articulo)-[:SUSTITUYE|INCORPORA|DEROGA|REGLAMENTA|MODIFICA|CITA {fuente, evidencia}]->(:Articulo | :Norma)

Salidas en data/grafo/: normas.csv, articulos.csv (sin el texto, que esta en
data/dataset/articulos.csv), relaciones.csv y resumen.json.

Uso:
    python scripts/10_armar_grafo.py                         # solo arma los CSV
    export NEO4J_PASSWORD=$(cat .neo4j_password)
    python scripts/10_armar_grafo.py --uri bolt://localhost:7688 --borrar
"""

import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from grafo_legal.archivos import escribir_texto       # noqa: E402
from grafo_legal.grafo import cargar_neo4j, construir  # noqa: E402


def leer(corpus: Path, dataset: Path, relaciones: list[Path]):
    normas = pd.read_csv(corpus / "corpus_normas.csv", dtype=str, keep_default_na=False)
    art = pd.read_csv(dataset / "articulos.csv", keep_default_na=False, dtype={"articulo": str},
                      usecols=["id_norma", "orden", "zona", "articulo", "inicio", "fin", "texto"])
    rel = pd.concat([pd.read_csv(p, keep_default_na=False, dtype={"articulo_destino": str, "articulo_origen": str})
                     for p in relaciones], ignore_index=True)
    return construir(normas, art, rel)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=Path("data/corpus"))
    ap.add_argument("--dataset", type=Path, default=Path("data/dataset"))
    ap.add_argument("--relaciones", type=Path, nargs="+",
                    default=[Path("results/relaciones/relaciones_reglas_v2.csv")],
                    help="una o mas tablas en la salida estandar (una por parser)")
    ap.add_argument("--out", type=Path, default=Path("data/grafo"))
    ap.add_argument("--uri", help="bolt://localhost:7688; sin --uri solo se arman los CSV")
    ap.add_argument("--user", default="neo4j")
    ap.add_argument("--borrar", action="store_true", help="borra los nodos Norma y Articulo antes de cargar")
    a = ap.parse_args()

    g = leer(a.corpus, a.dataset, a.relaciones)
    a.out.mkdir(parents=True, exist_ok=True)
    for nombre, df in (("normas.csv", g["normas"]), ("articulos.csv", g["articulos"].drop(columns="texto")),
                       ("relaciones.csv", g["relaciones"])):
        tmp = a.out / f".{nombre}.tmp"
        df.to_csv(tmp, index=False, lineterminator="\n")
        tmp.replace(a.out / nombre)
    rel = g["relaciones"]
    resumen = {
        "nodos": {"Norma": len(g["normas"]), "Articulo": len(g["articulos"]),
                  "Articulo_sin_texto": int((~g["articulos"].tiene_texto).sum())},
        "aristas": {"CONTIENE": len(g["articulos"]), **rel.tipo.value_counts().to_dict()},
        "relaciones_a_articulo": int(rel.destino_es_articulo.sum()),
        "relaciones_a_norma": int((~rel.destino_es_articulo).sum()),
        "fuentes": rel.fuente.value_counts().to_dict(),
    }
    escribir_texto(a.out / "resumen.json", json.dumps(resumen, indent=2, ensure_ascii=False))
    print(json.dumps(resumen, indent=2, ensure_ascii=False))

    if a.uri:
        pw = os.environ.get("NEO4J_PASSWORD")
        if not pw:
            sys.exit("Falta la variable de entorno NEO4J_PASSWORD")
        print("Neo4j:", json.dumps(cargar_neo4j(g, a.uri, a.user, pw, a.borrar), ensure_ascii=False))


if __name__ == "__main__":
    main()
