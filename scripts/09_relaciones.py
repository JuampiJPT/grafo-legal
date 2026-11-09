"""
09_relaciones.py
Convierte las menciones del parser de reglas v2 en relaciones tipadas, en la salida estandar
que comparten todos los parsers (src/grafo_legal/salida.py, docs/salida_estandar.md).
No lee el gold.

Salidas en results/relaciones/: relaciones_reglas_v2.csv y resumen.json.

Uso:
    python scripts/09_relaciones.py
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from grafo_legal.archivos import escribir_texto                      # noqa: E402
from grafo_legal.extractores.relaciones import desde_evidencias       # noqa: E402
from grafo_legal.fuentes.infoleg import cargar                        # noqa: E402
from grafo_legal.salida import validar                                # noqa: E402


def main(corpus: Path, html: Path, dataset: Path, res_v2: Path, out: Path) -> None:
    normas = pd.read_csv(corpus / "corpus_normas.csv", dtype=str, keep_default_na=False)
    etiquetas = {int(r.id_norma): f"{r.tipo_norma} {r.numero_norma}" for r in normas.itertuples()}
    ev = pd.read_csv(res_v2 / "evidencias.csv", keep_default_na=False, dtype={"articulo": str})
    textos = {i: cargar(i, html)[0] for i in sorted(set(ev.id_origen))}
    art = pd.read_csv(dataset / "articulos.csv", keep_default_na=False, dtype={"articulo": str},
                      usecols=["id_norma", "orden", "zona", "articulo", "inicio", "fin"])
    rel = desde_evidencias(ev, textos, art, etiquetas)
    errores = validar(rel)
    if errores:
        sys.exit("La salida no cumple el formato: " + "; ".join(errores))

    out.mkdir(parents=True, exist_ok=True)
    tmp = out / ".relaciones_reglas_v2.csv.tmp"
    rel.to_csv(tmp, index=False, lineterminator="\n")
    tmp.replace(out / "relaciones_reglas_v2.csv")
    resumen = {
        "relaciones": len(rel),
        "por_tipo": rel.tipo.value_counts().to_dict(),
        "por_parte_origen": rel.parte_origen.value_counts().to_dict(),
        "con_articulo_destino": int((rel.articulo_destino != "").sum()),
        "con_articulo_destino_sin_citas": round(float((rel[rel.tipo != "CITA"].articulo_destino != "").mean()), 4),
        "pares_de_normas": int(rel[["id_norma_origen", "id_norma_destino"]].drop_duplicates().shape[0]),
    }
    escribir_texto(out / "resumen.json", json.dumps(resumen, indent=2, ensure_ascii=False))
    print(json.dumps(resumen, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=Path("data/corpus"))
    ap.add_argument("--html", type=Path, default=Path("data/textos/infoleg/html"))
    ap.add_argument("--dataset", type=Path, default=Path("data/dataset"))
    ap.add_argument("--res-v2", type=Path, default=Path("results/reglas_v2"))
    ap.add_argument("--out", type=Path, default=Path("results/relaciones"))
    a = ap.parse_args()
    main(a.corpus, a.html, a.dataset, a.res_v2, a.out)
