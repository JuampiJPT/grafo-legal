"""
09_armar_grafo.py
Arma el grafo normativo para Neo4j y, si se le da una conexion, lo carga.

Modelo (docs/grafo.md):

  (:Norma)                      340 normas del corpus, con sus metadatos de InfoLEG
  (:Articulo)                   segmentos de texto de cada norma (data/dataset/articulos.csv)
  (:Norma)-[:TIENE_ARTICULO]->(:Articulo)
  (:Norma)-[:RELACION_INFOLEG]->(:Norma)     el gold: relaciones que registra InfoLEG
  (:Norma)-[:RELACION_EXTRAIDA]->(:Norma)    una por par y por parser (reglas_v1, reglas_v2,
                                              clasificador), con su puntaje y evidencias
  (:Articulo)-[:MENCIONA]->(:Norma)          cada mencion detectada, con offsets, fragmento,
                                              verbo y si la cuenta la regla de reglas_v2

El gold y lo extraido van en tipos de relacion distintos, para que una consulta nunca los mezcle
sin decirlo. Toda RELACION_EXTRAIDA de las reglas se puede rastrear hasta el articulo y el
fragmento que la sustentan, a traves de MENCIONA.

Salidas en data/grafo/: normas.csv, relaciones_infoleg.csv, relaciones_extraidas.csv,
menciones.csv y resumen.json. Los articulos se leen de data/dataset/articulos.csv.

Uso:
    python scripts/09_armar_grafo.py                       # solo arma los CSV y verifica
    NEO4J_PASSWORD=... python scripts/09_armar_grafo.py --uri bolt://localhost:7687 --user neo4j [--borrar]
"""

import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from grafo_legal.archivos import escribir_texto                 # noqa: E402
from grafo_legal.extractores import reglas, reglas_v2            # noqa: E402

LOTE = 1000


def _pares(ev: pd.DataFrame, filtro, campos: list[str]) -> pd.DataFrame:
    """Aplica una configuracion de reglas (filtro por evidencia) y agrega por par."""
    filas = [r for r in ev.itertuples(index=False) if filtro(r)]
    if not filas:
        return pd.DataFrame(columns=["id_origen", "id_destino", "n_evidencias", "articulos"])
    d = pd.DataFrame(filas, columns=campos)
    return (d.groupby(["id_origen", "id_destino"])
             .agg(n_evidencias=("articulo", "size"),
                  articulos=("articulo", lambda s: ";".join(sorted(set(map(str, s)), key=str))))
             .reset_index())


def armar(corpus: Path, dataset: Path, res_v1: Path, res_v2: Path, res_clf: Path, out: Path) -> dict:
    normas = pd.read_csv(corpus / "corpus_normas.csv", dtype=str, keep_default_na=False)
    gold = pd.read_csv(corpus / "gold_relaciones.csv")
    art = pd.read_csv(dataset / "articulos.csv", keep_default_na=False,
                      usecols=["id_norma", "orden", "zona", "articulo", "inicio", "fin"])
    claves_gold = set(zip(gold.id_norma_modificatoria, gold.id_norma_modificada))

    # nodos Norma
    con_texto = set(art.id_norma)
    n = pd.DataFrame({
        "id_norma": normas.id_norma.astype(int),
        "tipo": normas.tipo_norma, "numero": normas.numero_norma,
        "nombre": normas.tipo_norma + " " + normas.numero_norma,
        "fecha": normas.fecha_boletin.where(normas.fecha_boletin != "", normas.fecha_sancion),
        "titulo": normas.titulo_resumido, "sumario": normas.titulo_sumario,
        "organismo": normas.organismo_origen, "rol": normas.rol, "split": normas.split,
        "url_texto": normas.texto_actualizado.where(normas.texto_actualizado != "", normas.texto_original),
    })
    n["tiene_texto"] = n.id_norma.isin(con_texto)

    # relaciones del gold
    rg = gold.rename(columns={"id_norma_modificatoria": "id_origen", "id_norma_modificada": "id_destino"})[
        ["id_origen", "id_destino", "split"]]

    # relaciones extraidas, una tabla con la columna parser
    extra = []
    ev1 = pd.read_csv(res_v1 / "evidencias.csv", keep_default_na=False, dtype={"articulo": str})
    ev1["temporal_ok"] = ev1.temporal_ok.astype(str) == "True"
    p1 = _pares(ev1, reglas.CONFIGS["C_articulado_temporal"], list(ev1.columns))
    extra.append(p1.assign(parser="reglas_v1", config="C_articulado_temporal", puntaje=1.0))

    ev2 = pd.read_csv(res_v2 / "evidencias.csv", keep_default_na=False, dtype={"articulo": str})
    for c in ("temporal_ok", "procedencia"):
        ev2[c] = ev2[c].astype(str) == "True"
    regla = reglas_v2.CONFIGS["F_visto_o_articulado_con_verbo_o_ley"]
    p2 = _pares(ev2, regla, list(ev2.columns))
    extra.append(p2.assign(parser="reglas_v2", config="F_visto_o_articulado_con_verbo_o_ley", puntaje=1.0))

    clf_p = res_clf / "predicciones.csv"
    if clf_p.exists():
        c = pd.read_csv(clf_p)
        c = c[c.predicho == 1].rename(columns={"id_norma_origen": "id_origen", "id_norma_destino": "id_destino",
                                                "prob": "puntaje"})
        meta = json.loads((res_clf / "metricas.json").read_text(encoding="utf-8"))
        extra.append(c[["id_origen", "id_destino", "puntaje"]].assign(
            parser="clasificador", config=f"{meta['elegido']}_umbral_{meta['umbral']}", n_evidencias=0, articulos=""))
    re_ = pd.concat(extra, ignore_index=True)
    re_["en_infoleg"] = [(a, b) in claves_gold for a, b in zip(re_.id_origen, re_.id_destino)]
    split = n.set_index("id_norma").split
    re_["split"] = re_.id_origen.map(split)

    # menciones: cada evidencia de v2 enlazada a su articulo (el que contiene el offset)
    art = art.sort_values(["id_norma", "inicio"])
    art["id_articulo"] = art.id_norma.astype(str) + "#" + art.orden.astype(str)
    m = ev2.copy()
    m["cuenta_en_reglas_v2"] = [regla(r) for r in ev2.itertuples(index=False)]
    m = pd.merge_asof(m.sort_values("inicio"),
                      art[["id_norma", "inicio", "id_articulo"]].rename(columns={"id_norma": "id_origen"})
                      .sort_values("inicio"),
                      on="inicio", by="id_origen", direction="backward")
    m = m[["id_articulo", "id_origen", "id_destino", "parte", "inicio", "fin", "superficie", "metodo",
           "verbo_oracion", "temporal_ok", "procedencia", "cuenta_en_reglas_v2", "fragmento"]]
    # orden explicito: el de merge_asof cambia entre versiones de pandas
    m = m.sort_values(["id_origen", "inicio", "fin", "id_destino", "metodo"], kind="mergesort")

    out.mkdir(parents=True, exist_ok=True)
    for nombre, df in (("normas.csv", n), ("relaciones_infoleg.csv", rg),
                       ("relaciones_extraidas.csv", re_), ("menciones.csv", m)):
        tmp = out / f".{nombre}.tmp"
        df.to_csv(tmp, index=False, lineterminator="\n")
        tmp.replace(out / nombre)

    resumen = {
        "nodos": {"Norma": len(n), "Articulo": len(art)},
        "relaciones": {"TIENE_ARTICULO": len(art), "RELACION_INFOLEG": len(rg),
                       "RELACION_EXTRAIDA": re_.parser.value_counts().to_dict(), "MENCIONA": len(m)},
        "menciones_sin_articulo": int(m.id_articulo.isna().sum()),
        "extraidas_en_infoleg": re_.groupby("parser").en_infoleg.mean().round(4).to_dict(),
    }
    escribir_texto(out / "resumen.json", json.dumps(resumen, indent=2, ensure_ascii=False))
    return resumen


CONSTRAINTS = [
    "CREATE CONSTRAINT norma_id IF NOT EXISTS FOR (n:Norma) REQUIRE n.id_norma IS UNIQUE",
    "CREATE CONSTRAINT articulo_id IF NOT EXISTS FOR (a:Articulo) REQUIRE a.id IS UNIQUE",
    "CREATE INDEX norma_nombre IF NOT EXISTS FOR (n:Norma) ON (n.nombre)",
    "CREATE FULLTEXT INDEX articulo_texto IF NOT EXISTS FOR (a:Articulo) ON EACH [a.texto]",
]

CARGAS = {
    "normas.csv": """UNWIND $filas AS f
        MERGE (n:Norma {id_norma: toInteger(f.id_norma)})
        SET n.tipo = f.tipo, n.numero = f.numero, n.nombre = f.nombre, n.fecha = f.fecha, n.titulo = f.titulo,
            n.sumario = f.sumario, n.organismo = f.organismo, n.rol = f.rol, n.split = f.split,
            n.url_texto = f.url_texto, n.tiene_texto = f.tiene_texto = 'True',
            n.anio = toInteger(left(f.fecha, 4))""",
    "articulos": """UNWIND $filas AS f
        MATCH (n:Norma {id_norma: toInteger(f.id_norma)})
        MERGE (a:Articulo {id: f.id})
        SET a.id_norma = toInteger(f.id_norma), a.orden = toInteger(f.orden), a.numero = f.articulo,
            a.zona = f.zona, a.inicio = toInteger(f.inicio), a.fin = toInteger(f.fin), a.texto = f.texto
        MERGE (n)-[:TIENE_ARTICULO]->(a)""",
    "relaciones_infoleg.csv": """UNWIND $filas AS f
        MATCH (o:Norma {id_norma: toInteger(f.id_origen)}), (d:Norma {id_norma: toInteger(f.id_destino)})
        MERGE (o)-[r:RELACION_INFOLEG]->(d) SET r.split = f.split, r.fuente = 'InfoLEG base complementaria'""",
    "relaciones_extraidas.csv": """UNWIND $filas AS f
        MATCH (o:Norma {id_norma: toInteger(f.id_origen)}), (d:Norma {id_norma: toInteger(f.id_destino)})
        MERGE (o)-[r:RELACION_EXTRAIDA {parser: f.parser}]->(d)
        SET r.config = f.config, r.puntaje = toFloat(f.puntaje), r.n_evidencias = toInteger(f.n_evidencias),
            r.articulos = f.articulos, r.en_infoleg = f.en_infoleg = 'True', r.split = f.split""",
    "menciones.csv": """UNWIND $filas AS f
        MATCH (a:Articulo {id: f.id_articulo}), (d:Norma {id_norma: toInteger(f.id_destino)})
        CREATE (a)-[:MENCIONA {parte: f.parte, inicio: toInteger(f.inicio), fin: toInteger(f.fin),
            superficie: f.superficie, metodo: f.metodo, verbo: f.verbo_oracion,
            temporal_ok: f.temporal_ok = 'True', procedencia: f.procedencia = 'True',
            cuenta_en_reglas_v2: f.cuenta_en_reglas_v2 = 'True', fragmento: f.fragmento}]->(d)""",
}


def cargar_neo4j(out: Path, dataset: Path, uri: str, user: str, password: str, borrar: bool) -> None:
    from neo4j import GraphDatabase
    art = pd.read_csv(dataset / "articulos.csv", keep_default_na=False, dtype=str)
    art["id"] = art.id_norma + "#" + art.orden
    with GraphDatabase.driver(uri, auth=(user, password)) as drv, drv.session() as s:
        if borrar:
            s.run("MATCH (n) WHERE n:Norma OR n:Articulo CALL { WITH n DETACH DELETE n } IN TRANSACTIONS")
        for c in CONSTRAINTS:
            s.run(c)
        for nombre, cypher in CARGAS.items():
            df = art if nombre == "articulos" else pd.read_csv(out / nombre, dtype=str, keep_default_na=False)
            filas = df.to_dict("records")
            for i in range(0, len(filas), LOTE):
                s.run(cypher, filas=filas[i:i + LOTE]).consume()
            print(f"  {nombre}: {len(filas)} filas")
        r = s.run("MATCH (n) RETURN labels(n)[0] AS l, count(*) AS c").data()
        print("  nodos:", {x["l"]: x["c"] for x in r})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=Path("data/corpus"))
    ap.add_argument("--dataset", type=Path, default=Path("data/dataset"))
    ap.add_argument("--res-v1", type=Path, default=Path("results/reglas"))
    ap.add_argument("--res-v2", type=Path, default=Path("results/reglas_v2"))
    ap.add_argument("--res-clf", type=Path, default=Path("results/clasificador"))
    ap.add_argument("--out", type=Path, default=Path("data/grafo"))
    ap.add_argument("--uri", help="bolt://localhost:7687; sin --uri solo se arman los CSV")
    ap.add_argument("--user", default="neo4j")
    ap.add_argument("--borrar", action="store_true", help="borra los nodos Norma y Articulo antes de cargar")
    a = ap.parse_args()
    print(json.dumps(armar(a.corpus, a.dataset, a.res_v1, a.res_v2, a.res_clf, a.out), indent=2, ensure_ascii=False))
    if a.uri:
        pw = os.environ.get("NEO4J_PASSWORD")
        if not pw:
            sys.exit("Falta la variable de entorno NEO4J_PASSWORD")
        cargar_neo4j(a.out, a.dataset, a.uri, a.user, pw, a.borrar)


if __name__ == "__main__":
    main()
