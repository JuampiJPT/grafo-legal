"""Consultas a Neo4j para el texto consolidado (B60).

1. --ranking: qué ley tiene más profundidad en el grafo. Para cada norma de InfoLEG con texto
   cuenta, sobre las aristas que no son CITA:
     - modificatorias: cuántas normas distintas actúan sobre ella;
     - articulos_afectados: cuántos de sus artículos reciben una relación;
     - profundidad: el largo de la cadena más larga de modificaciones que llega a ella
       (una norma que la modifica, otra que modifica a esa, y así).
2. --manifiesto ID: la ley con todos sus artículos (con texto) y todas las relaciones que llegan
   a ella o a sus artículos, con el artículo de origen y su texto, ordenadas por fecha. Indica qué
   parsers (fuentes) encontraron cada relación.

Corre donde está Neo4j:
  export NEO4J_PASSWORD=$(cat .neo4j_password)
  python scripts/23_consultar_consolidado.py --ranking
  python scripts/23_consultar_consolidado.py --manifiesto 25552 229909   # LCT y su t.o. (Decreto 390/76)
"""

import argparse
import json
import os
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import pandas as pd
from neo4j import GraphDatabase

OUT = Path("results/consolidado")
FUENTES = ["reglas_v2", "reglas_v3", "llm", "hibrido"]

# aristas entre normas que no son CITA, de una fuente; el destino puede ser la norma o un artículo
ARISTAS = """
MATCH (m:Norma)-[:CONTIENE]->(:Articulo)-[r]->(d)
WHERE r.fuente = $fuente AND type(r) <> 'CITA' AND m.id_norma < 9000000
OPTIONAL MATCH (t:Norma)-[:CONTIENE]->(d)
WITH m, r, d, coalesce(t, d) AS n
WHERE n:Norma AND n <> m
RETURN m.id_norma AS origen, n.id_norma AS destino, n.nombre AS nombre, n.tiene_texto AS tiene_texto,
       type(r) AS tipo, CASE WHEN d:Articulo THEN d.numero ELSE '' END AS articulo
"""

ARTICULOS = """
MATCH (n:Norma {id_norma: $id})-[:CONTIENE]->(a:Articulo)
WHERE a.tiene_texto
RETURN a.id AS id, a.orden AS orden, a.numero AS numero, a.zona AS zona, a.texto AS texto
ORDER BY a.orden
"""

ENTRANTES = """
MATCH (n:Norma) WHERE n.id_norma IN $ids
MATCH (m:Norma)-[:CONTIENE]->(o:Articulo)-[r]->(d)
WHERE type(r) <> 'CITA' AND r.fuente IN $fuentes AND (d = n OR (n)-[:CONTIENE]->(d))
RETURN n.id_norma AS id_destino, m.id_norma AS id_origen, m.nombre AS norma_origen, m.fecha AS fecha_origen, m.tiene_texto AS origen_tiene_texto,
       o.id AS id_articulo_origen, o.numero AS articulo_origen, o.zona AS zona_origen, o.texto AS texto_origen,
       type(r) AS tipo, CASE WHEN d:Articulo THEN d.numero ELSE '' END AS articulo_destino,
       r.fuente AS fuente, r.verbo AS verbo, r.parte_origen AS parte_origen, r.confianza AS confianza,
       r.fragmento AS fragmento
ORDER BY m.fecha, m.id_norma, o.orden
"""


def ranking(s) -> pd.DataFrame:
    filas = []
    for f in FUENTES:
        e = pd.DataFrame(s.run(ARISTAS, fuente=f).data())
        e = e[e.origen < 9_000_000]
        entra = defaultdict(set)
        for o, d in zip(e.origen, e.destino):
            entra[d].add(o)

        @lru_cache(None)
        def prof(n, visit=()):
            # cadena más larga de modificaciones que llega a n (sin ciclos)
            return max((1 + prof(m, visit + (n,)) for m in entra[n] if m not in visit and m != n), default=0)

        for d, g in e.groupby("destino"):
            filas.append({"fuente": f, "id_norma": d, "nombre": g.nombre.iloc[0], "tiene_texto": g.tiene_texto.iloc[0],
                          "modificatorias": g.origen.nunique(),
                          "articulos_afectados": g[g.articulo != ""].articulo.nunique(),
                          "profundidad": prof(d), "aristas": len(g)})
    r = pd.DataFrame(filas)
    return r.sort_values(["fuente", "modificatorias", "profundidad"], ascending=[True, False, False])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--uri", default=os.environ.get("NEO4J_URI", "bolt://localhost:7688"))
    ap.add_argument("--ranking", action="store_true")
    ap.add_argument("--manifiesto", type=int, nargs="+",
                    help="ids de la ley; el primero es el de la ley, los otros sus textos ordenados (p. ej. 25552 229909)")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    with GraphDatabase.driver(a.uri, auth=("neo4j", os.environ["NEO4J_PASSWORD"])) as drv, drv.session() as s:
        if a.ranking:
            r = ranking(s)
            r.to_csv(OUT / "ranking_profundidad.csv", index=False)
            print(r.groupby("fuente").head(8).to_string(index=False))
        if a.manifiesto:
            ids = a.manifiesto
            art = pd.concat([pd.DataFrame(s.run(ARTICULOS, id=i).data()).assign(id_norma=i) for i in ids])
            rel = pd.DataFrame(s.run(ENTRANTES, ids=ids, fuentes=FUENTES).data())
            art.to_json(OUT / f"manifiesto_{ids[0]}_articulos.json", orient="records", force_ascii=False, indent=1)
            rel.to_json(OUT / f"manifiesto_{ids[0]}_relaciones.json", orient="records", force_ascii=False, indent=1)
            print(len(art), "articulos;", len(rel), "relaciones;", rel.id_origen.nunique(), "normas modificatorias")


if __name__ == "__main__":
    main()
