"""Grafo normativo generico: se arma solo a partir de la salida estandar de relaciones.

Modelo (docs/grafo.md):
  (:Norma)-[:CONTIENE]->(:Articulo)
  (:Articulo)-[:SUSTITUYE|INCORPORA|DEROGA|REGLAMENTA|MODIFICA|CITA {fuente, ...}]->(:Articulo | :Norma)

La relacion va a un Articulo cuando la salida dice cual (articulo_destino); si no, a la Norma.
Un articulo destino que no tiene texto en el corpus se crea igual, con tiene_texto = false.

Las mismas funciones sirven para cargar Neo4j y para una copia en memoria (networkx), que usa la
evaluacion cuando no hay un Neo4j a mano. Las dos se leen con la misma logica de exportacion.
"""

from __future__ import annotations

import pandas as pd

from .salida import TIPOS

PROPS_REL = ["fuente", "parte_origen", "verbo", "metodo", "confianza", "n_menciones", "inicio", "fin", "fragmento"]


def construir(normas: pd.DataFrame, articulos: pd.DataFrame, rel: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """normas: corpus_normas.csv. articulos: data/dataset/articulos.csv (con texto).
    rel: salida estandar. Devuelve las tablas de nodos y aristas."""
    n = pd.DataFrame({
        "id_norma": normas.id_norma.astype(int), "tipo": normas.tipo_norma, "numero": normas.numero_norma,
        "nombre": normas.tipo_norma + " " + normas.numero_norma,
        "fecha": normas.fecha_boletin.where(normas.fecha_boletin != "", normas.fecha_sancion),
        "titulo": normas.titulo_resumido, "sumario": normas.titulo_sumario,
        "organismo": normas.organismo_origen, "split": normas.split,
    })
    a = articulos.copy()
    a["id"] = a.id_norma.astype(str) + "#" + a.orden.astype(str)
    a = a.rename(columns={"articulo": "numero"})
    a["tiene_texto"] = True
    n["tiene_texto"] = n.id_norma.isin(set(a.id_norma))

    # articulo destino -> nodo: el primer articulo del articulado con ese numero
    numerados = a[a.zona == "articulado"].drop_duplicates(["id_norma", "numero"])
    por_numero = {(int(i), str(k)): v for i, k, v in zip(numerados.id_norma, numerados.numero, numerados.id)}
    rel = rel.copy()
    rel["articulo_destino"] = rel.articulo_destino.fillna("").astype(str)
    con_art = rel.articulo_destino != ""
    ids = [por_numero.get((int(i), k), f"{i}#art {k}") for i, k in
           zip(rel.id_norma_destino[con_art], rel.articulo_destino[con_art])]
    rel["destino"] = rel.id_norma_destino.astype(str)
    rel.loc[con_art, "destino"] = ids
    rel["destino_es_articulo"] = con_art

    faltan = sorted(set(ids) - set(a.id))
    stubs = pd.DataFrame({"id": faltan,
                          "id_norma": [int(x.split("#")[0]) for x in faltan],
                          "numero": [x.split("#art ")[1] for x in faltan]})
    stubs = stubs.assign(orden=-1, zona="articulado", inicio=-1, fin=-1, texto="", tiene_texto=False)
    a = pd.concat([a[["id", "id_norma", "orden", "numero", "zona", "inicio", "fin", "texto", "tiene_texto"]],
                   stubs], ignore_index=True)
    return {"normas": n, "articulos": a, "relaciones": rel}


# ---------- copia en memoria ----------

def a_networkx(g: dict[str, pd.DataFrame]):
    import networkx as nx
    G = nx.MultiDiGraph()
    for r in g["normas"].to_dict("records"):
        G.add_node(("Norma", r["id_norma"]), **r)
    for r in g["articulos"].drop(columns="texto").to_dict("records"):
        G.add_node(("Articulo", r["id"]), **r)
        G.add_edge(("Norma", r["id_norma"]), ("Articulo", r["id"]), key="CONTIENE", tipo="CONTIENE")
    for r in g["relaciones"].to_dict("records"):
        d = ("Articulo", r["destino"]) if r["destino_es_articulo"] else ("Norma", int(r["destino"]))
        G.add_edge(("Articulo", r["id_articulo_origen"]), d, key=(r["tipo"], r["fuente"]), tipo=r["tipo"],
                   **{k: r[k] for k in PROPS_REL})
    return G


def exportar_networkx(G) -> pd.DataFrame:
    """Recorre el grafo y devuelve las relaciones con las columnas de la clave (mismo formato que Neo4j)."""
    filas = []
    for o, d, k, p in G.edges(keys=True, data=True):
        if p["tipo"] not in TIPOS:
            continue
        no = next(u for u, _, kk in G.in_edges(o, keys=True) if kk == "CONTIENE")
        if d[0] == "Articulo":
            nd = next(u for u, _, kk in G.in_edges(d, keys=True) if kk == "CONTIENE")
            id_dest, art_dest = nd[1], str(G.nodes[d]["numero"])
        else:
            id_dest, art_dest = d[1], ""
        filas.append({"fuente": p["fuente"], "id_norma_origen": no[1], "tipo_norma_origen": G.nodes[no]["tipo"],
                      "id_articulo_origen": o[1], "tipo": p["tipo"], "id_norma_destino": id_dest,
                      "articulo_destino": art_dest, "parte_origen": p["parte_origen"], "metodo": p["metodo"]})
    return pd.DataFrame(filas)


# ---------- Neo4j ----------

CONSTRAINTS = [
    "CREATE CONSTRAINT norma_id IF NOT EXISTS FOR (n:Norma) REQUIRE n.id_norma IS UNIQUE",
    "CREATE CONSTRAINT articulo_id IF NOT EXISTS FOR (a:Articulo) REQUIRE a.id IS UNIQUE",
    "CREATE INDEX norma_nombre IF NOT EXISTS FOR (n:Norma) ON (n.nombre)",
    "CREATE FULLTEXT INDEX articulo_texto IF NOT EXISTS FOR (a:Articulo) ON EACH [a.texto]",
]

CARGA_NORMAS = """UNWIND $filas AS f
MERGE (n:Norma {id_norma: f.id_norma})
SET n.tipo = f.tipo, n.numero = f.numero, n.nombre = f.nombre, n.fecha = f.fecha, n.titulo = f.titulo,
    n.sumario = f.sumario, n.organismo = f.organismo, n.split = f.split, n.tiene_texto = f.tiene_texto,
    n.anio = toInteger(left(f.fecha, 4))"""

CARGA_ARTICULOS = """UNWIND $filas AS f
MATCH (n:Norma {id_norma: f.id_norma})
MERGE (a:Articulo {id: f.id})
SET a.id_norma = f.id_norma, a.orden = f.orden, a.numero = f.numero, a.zona = f.zona,
    a.inicio = f.inicio, a.fin = f.fin, a.texto = f.texto, a.tiene_texto = f.tiene_texto
MERGE (n)-[:CONTIENE]->(a)"""


def carga_relaciones(tipo: str, a_articulo: bool) -> str:
    assert tipo in TIPOS
    destino = "(d:Articulo {id: f.destino})" if a_articulo else "(d:Norma {id_norma: toInteger(f.destino)})"
    return f"""UNWIND $filas AS f
MATCH (o:Articulo {{id: f.id_articulo_origen}}), {destino}
MERGE (o)-[r:{tipo} {{fuente: f.fuente}}]->(d)
SET r.parte_origen = f.parte_origen, r.verbo = f.verbo, r.metodo = f.metodo, r.confianza = f.confianza,
    r.n_menciones = f.n_menciones, r.inicio = f.inicio, r.fin = f.fin, r.fragmento = f.fragmento"""


EXPORTAR = """MATCH (n:Norma)-[:CONTIENE]->(o:Articulo)-[r]->(d)
WHERE type(r) IN $tipos
OPTIONAL MATCH (nd:Norma)-[:CONTIENE]->(d)
RETURN r.fuente AS fuente, n.id_norma AS id_norma_origen, n.tipo AS tipo_norma_origen,
       o.id AS id_articulo_origen, type(r) AS tipo,
       CASE WHEN d:Articulo THEN nd.id_norma ELSE d.id_norma END AS id_norma_destino,
       CASE WHEN d:Articulo THEN d.numero ELSE '' END AS articulo_destino,
       r.parte_origen AS parte_origen, r.metodo AS metodo"""


def _registros(df: pd.DataFrame) -> list[dict]:
    """Filas para Neo4j: tipos de Python nativos y sin NaN."""
    return [{k: (None if pd.isna(v) else (v.item() if hasattr(v, "item") else v)) for k, v in r.items()}
            for r in df.to_dict("records")]


def cargar_neo4j(g: dict[str, pd.DataFrame], uri: str, user: str, password: str, borrar: bool,
                 lote: int = 1000) -> dict:
    from neo4j import GraphDatabase
    with GraphDatabase.driver(uri, auth=(user, password)) as drv, drv.session() as s:
        if borrar:
            s.run("MATCH (n) WHERE n:Norma OR n:Articulo CALL { WITH n DETACH DELETE n } IN TRANSACTIONS").consume()
        for c in CONSTRAINTS:
            s.run(c).consume()
        tareas = [(CARGA_NORMAS, g["normas"]), (CARGA_ARTICULOS, g["articulos"])]
        rel = g["relaciones"]
        for tipo in TIPOS:
            for a_art in (True, False):
                sub = rel[(rel.tipo == tipo) & (rel.destino_es_articulo == a_art)]
                if len(sub):
                    tareas.append((carga_relaciones(tipo, a_art), sub))
        for cypher, df in tareas:
            filas = _registros(df)
            for i in range(0, len(filas), lote):
                s.run(cypher, filas=filas[i:i + lote]).consume()
        nodos = {r["l"]: r["c"] for r in s.run("MATCH (n) WHERE n:Norma OR n:Articulo "
                                                 "RETURN labels(n)[0] AS l, count(*) AS c").data()}
        aristas = {r["t"]: r["c"] for r in s.run("MATCH (:Articulo)-[r]->() RETURN type(r) AS t, count(*) AS c").data()}
    return {"nodos": nodos, "aristas": aristas}


def exportar_neo4j(uri: str, user: str, password: str) -> pd.DataFrame:
    from neo4j import GraphDatabase
    with GraphDatabase.driver(uri, auth=(user, password)) as drv, drv.session() as s:
        return pd.DataFrame(s.run(EXPORTAR, tipos=list(TIPOS)).data())
