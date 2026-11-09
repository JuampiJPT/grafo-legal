"""
11_evaluar_grafo.py
Evalua el grafo normativo leyendolo de vuelta (no de los CSV del parser).

1. Ida y vuelta: las relaciones que devuelve el grafo tienen que ser exactamente las que se
   cargaron desde la salida estandar del parser. Cualquier diferencia es un error de carga.
2. Comparacion con InfoLEG: las relaciones del grafo se proyectan a pares de normas y se comparan
   con las relaciones que registra InfoLEG, por split. InfoLEG no dice el tipo de relacion, asi
   que se reporta tambien que tan seguido cada tipo coincide con un vinculo de InfoLEG.
3. Por norma destino: para las semillas del corpus, cuantas de las normas que InfoLEG registra
   como modificatorias aparecen en el grafo.

Proyeccion a pares de normas (la misma regla F de reglas v2, aplicada sobre las aristas):
un par (origen, destino) es un vinculo si tiene alguna relacion que
  - sale del VISTO, o
  - sale del articulado, con numero, y no es una CITA o la norma origen no es un decreto.
Tambien se reporta la proyeccion sin filtro (cualquier relacion).

Backend: con --uri lee el Neo4j cargado por 10_armar_grafo.py; sin --uri arma la misma estructura
en memoria (networkx) con el mismo codigo de construccion y la recorre.

Salidas en results/evaluacion_grafo/: metricas.json y discrepancias.csv.

Uso:
    python scripts/11_evaluar_grafo.py                                    # en memoria
    export NEO4J_PASSWORD=$(cat .neo4j_password)
    python scripts/11_evaluar_grafo.py --uri bolt://localhost:7688        # sobre Neo4j
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from grafo_legal.archivos import escribir_texto                         # noqa: E402
from grafo_legal.evaluacion import prf                                  # noqa: E402
from grafo_legal.grafo import a_networkx, construir, exportar_neo4j, exportar_networkx  # noqa: E402
from grafo_legal.salida import CLAVE, TIPOS                             # noqa: E402

SEMILLAS = {25552: "Ley 20.744 (LCT)", 423680: "Ley 27.802", 412: "Ley 24.013", 27971: "Ley 24.557",
            20993: "Ley 23.551", 46379: "Ley 14.250", 401266: "Ley 27.742"}


def proyectar(g: pd.DataFrame) -> pd.Series:
    """Que relaciones del grafo cuentan como vinculo entre normas (regla F de reglas v2)."""
    art = (g.parte_origen == "articulado") & (g.metodo == "regex_numero") & \
          ((g.tipo != "CITA") | (g.tipo_norma_origen != "Decreto"))
    return (g.parte_origen == "visto") | art


def pares(df: pd.DataFrame) -> set:
    return set(zip(df.id_norma_origen.astype(int), df.id_norma_destino.astype(int)))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=Path("data/corpus"))
    ap.add_argument("--dataset", type=Path, default=Path("data/dataset"))
    ap.add_argument("--relaciones", type=Path, default=Path("results/relaciones/relaciones_reglas_v2.csv"))
    ap.add_argument("--fuente", default="reglas_v2")
    ap.add_argument("--out", type=Path, default=Path("results/evaluacion_grafo"))
    ap.add_argument("--uri", help="bolt://localhost:7688; sin --uri evalua una copia en memoria")
    ap.add_argument("--user", default="neo4j")
    a = ap.parse_args()

    normas = pd.read_csv(a.corpus / "corpus_normas.csv", dtype=str, keep_default_na=False)
    gold = pd.read_csv(a.corpus / "gold_relaciones.csv")
    cargado = pd.read_csv(a.relaciones, keep_default_na=False, dtype={"articulo_destino": str})
    cargado = cargado[cargado.fuente == a.fuente]

    if a.uri:
        pw = os.environ.get("NEO4J_PASSWORD") or sys.exit("Falta la variable de entorno NEO4J_PASSWORD")
        g = exportar_neo4j(a.uri, a.user, pw)
        backend = f"neo4j {a.uri}"
    else:
        art = pd.read_csv(a.dataset / "articulos.csv", keep_default_na=False, dtype={"articulo": str},
                          usecols=["id_norma", "orden", "zona", "articulo", "inicio", "fin", "texto"])
        g = exportar_networkx(a_networkx(construir(normas, art, cargado)))
        backend = "memoria (networkx)"
    g = g[g.fuente == a.fuente].copy()
    g["articulo_destino"] = g.articulo_destino.fillna("").astype(str)

    # 1. ida y vuelta
    def claves(df):
        return set(map(tuple, df[CLAVE].astype(str).values.tolist()))
    k_cargado, k_grafo = claves(cargado), claves(g)
    ida_vuelta = {"cargadas": len(k_cargado), "devueltas": len(k_grafo),
                  "faltan_en_el_grafo": len(k_cargado - k_grafo), "sobran_en_el_grafo": len(k_grafo - k_cargado),
                  "identicas": k_cargado == k_grafo}

    # 2. comparacion con InfoLEG, por split
    split = normas.set_index(normas.id_norma.astype(int)).split
    g["split"] = g.id_norma_origen.astype(int).map(split)
    g["vinculo"] = proyectar(g)
    v = pd.read_csv(a.corpus / "pares_evaluados_en_v1.csv")
    vistos = set(zip(v.id_norma_modificatoria, v.id_norma_modificada))
    metricas = {"fecha": datetime.now(timezone.utc).isoformat(), "backend": backend, "fuente": a.fuente,
                "ida_y_vuelta": ida_vuelta, "nodos_y_aristas": {"relaciones_por_tipo": g.tipo.value_counts().to_dict()},
                "infoleg": {}, "por_tipo": {}, "por_semilla": {}}
    disc = []
    for s in ("dev", "test"):
        gs = gold[gold.split == s]
        ref = set(zip(gs.id_norma_modificatoria, gs.id_norma_modificada))
        sub = g[g.split == s]
        pred = pares(sub[sub.vinculo])
        metricas["infoleg"][s] = {"vinculos_del_grafo": prf(pred, ref),
                                  "cualquier_relacion": prf(pares(sub), ref),
                                  "sin_pares_de_v1": prf(pred - vistos, ref - vistos)}
        for t in TIPOS:
            pt = pares(sub[sub.tipo == t])
            metricas["por_tipo"].setdefault(t, {})[s] = {
                "pares": len(pt), "en_infoleg": len(pt & ref),
                "proporcion_en_infoleg": round(len(pt & ref) / len(pt), 4) if pt else None}
        for o, d in sorted(ref - pred):
            disc.append({"split": s, "error": "FN", "id_norma_origen": o, "id_norma_destino": d,
                         "tipos_en_el_grafo": ";".join(sorted(set(sub[(sub.id_norma_origen == o) &
                                                                       (sub.id_norma_destino == d)].tipo)))})
        for o, d in sorted(pred - ref):
            disc.append({"split": s, "error": "FP", "id_norma_origen": o, "id_norma_destino": d,
                         "tipos_en_el_grafo": ";".join(sorted(set(sub[(sub.id_norma_origen == o) &
                                                                       (sub.id_norma_destino == d)].tipo)))})

    # 3. por norma destino (todas las splits): modificatorias de cada semilla
    todos = pares(g[g.vinculo])
    ref_todo = set(zip(gold.id_norma_modificatoria, gold.id_norma_modificada))
    for id_s, nombre in SEMILLAS.items():
        r_s = {p for p in ref_todo if p[1] == id_s}
        p_s = {p for p in todos if p[1] == id_s}
        metricas["por_semilla"][nombre] = prf(p_s, r_s)

    etiqueta = {int(r.id_norma): f"{r.tipo_norma} {r.numero_norma}" for r in normas.itertuples()}
    d = pd.DataFrame(disc)
    d.insert(3, "norma_origen", d.id_norma_origen.map(etiqueta))
    d.insert(5, "norma_destino", d.id_norma_destino.map(etiqueta))
    a.out.mkdir(parents=True, exist_ok=True)
    d.to_csv(a.out / "discrepancias.csv", index=False, lineterminator="\n")
    escribir_texto(a.out / "metricas.json", json.dumps(metricas, indent=2, ensure_ascii=False))

    print(f"backend: {backend}")
    print("ida y vuelta:", json.dumps(ida_vuelta, ensure_ascii=False))
    for s, m in metricas["infoleg"].items():
        x, y, z = m["vinculos_del_grafo"], m["cualquier_relacion"], m["sin_pares_de_v1"]
        print(f"{s}: vinculos P={x['precision']:.3f} R={x['recall']:.3f} F1={x['f1']:.3f} | "
              f"cualquier relacion P={y['precision']:.3f} R={y['recall']:.3f} | sin v1 F1={z['f1']:.3f}")
    for t, m in metricas["por_tipo"].items():
        print(f"  {t:10s} " + "  ".join(f"{s}: {x['pares']} pares, {x['proporcion_en_infoleg']}" for s, x in m.items()))
    for n_, m in metricas["por_semilla"].items():
        print(f"  {n_:18s} InfoLEG {m['gold']:3d}  grafo {m['pred']:3d}  R={m['recall']:.3f} P={m['precision']:.3f}")
    if not ida_vuelta["identicas"]:
        sys.exit("ATENCION: el grafo no devuelve exactamente lo que se cargo")


if __name__ == "__main__":
    main()
