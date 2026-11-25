"""
35_demo_consultas.py
Corre las consultas de la demo del grafo sobre el Neo4j del TP y guarda lo que devuelven (B76).

Sirve para dos cosas: comprobar que cada consulta de docs/demo_grafo.md funciona tal cual está
escrita, y tener los resultados reales para explicarlos en el coloquio. No escribe nada en Neo4j.

Además arma, en Python, la cadena de modificaciones más larga que llega a la LCT (la «profundidad»
de B61), porque con aristas por artículo no se puede pedir directo a Cypher sin APOC.

Uso (en la Mac, con el contenedor neo4j-grafo-legal corriendo):
    export NEO4J_PASSWORD=$(cat .neo4j_password)
    python3 scripts/35_demo_consultas.py            # -> results/demo/consultas.md y consultas.json
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
OUT = RAIZ / "results" / "demo"
URI = os.environ.get("NEO4J_URI", "bolt://localhost:7688")
TIPOS_CAMBIO = "['SUSTITUYE','INCORPORA','DEROGA','MODIFICA','REGLAMENTA']"

# (clave, pregunta, consulta). Las consultas son las mismas que se muestran en la demo.
CONSULTAS = [
    ("panorama_nodos", "¿Qué hay en la base?",
     "MATCH (n) WHERE n:Norma OR n:Articulo RETURN labels(n)[0] AS etiqueta, count(*) AS cantidad"),
    ("panorama_fuentes", "¿Cuántas aristas aportó cada parser?",
     """MATCH (:Articulo)-[r]->() WHERE type(r) <> 'CONTIENE'
RETURN r.fuente AS fuente, count(*) AS aristas,
       sum(CASE WHEN type(r) <> 'CITA' THEN 1 ELSE 0 END) AS no_cita
ORDER BY fuente"""),
    ("ley27802_resumen", "¿Qué le hizo la Ley 27.802 a la LCT? (fuente llm)",
     """MATCH (:Norma {nombre: 'Ley 27802'})-[:CONTIENE]->(a)-[r]->(d:Articulo {id_norma: 25552})
WHERE r.fuente = 'llm' AND type(r) <> 'CITA'
RETURN type(r) AS que_hizo, count(DISTINCT d) AS articulos_de_la_lct
ORDER BY articulos_de_la_lct DESC"""),
    ("ley27802_detalle", "¿Qué artículos de la LCT sustituyó la Ley 27.802, y con qué texto?",
     """MATCH (:Norma {nombre: 'Ley 27802'})-[:CONTIENE]->(a)-[r:SUSTITUYE]->(d:Articulo {id_norma: 25552})
WHERE r.fuente = 'llm'
RETURN a.numero AS art_27802, d.numero AS art_lct, left(r.fragmento, 160) AS evidencia
ORDER BY toInteger(split(d.numero, ' ')[0]) LIMIT 12"""),
    ("historia_245", "Historia del artículo 245 de la LCT (indemnización por despido)",
     """MATCH (n:Norma)-[:CONTIENE]->(o)-[r]->(:Articulo {id_norma: 25552, numero: '245'})
WHERE type(r) <> 'CITA'
RETURN n.nombre AS norma, n.fecha AS fecha, type(r) AS que_hizo, collect(DISTINCT r.fuente) AS fuentes
ORDER BY fecha"""),
    ("lct_por_decada", "¿En qué décadas se reformó más la LCT? (fuente llm)",
     f"""MATCH (n:Norma)-[:CONTIENE]->(:Articulo)-[r]->(d)
WHERE r.fuente = 'llm' AND type(r) IN ['SUSTITUYE','INCORPORA','DEROGA','MODIFICA'] AND d.id_norma = 25552
RETURN (n.anio / 10) * 10 AS decada, count(DISTINCT n) AS normas, count(*) AS cambios
ORDER BY decada"""),
    ("deroga_24013", "¿Qué normas derogaron algo de la Ley de Empleo 24.013? (fuente llm)",
     """MATCH (n:Norma)-[:CONTIENE]->(:Articulo)-[r:DEROGA]->(d)
WHERE r.fuente = 'llm' AND d.id_norma = 412
RETURN DISTINCT n.nombre AS norma, n.fecha AS fecha, coalesce(d.numero, 'toda la ley') AS que_derogo
ORDER BY fecha"""),
    ("reglamenta_lrt", "¿Qué decretos reglamentan la Ley de Riesgos del Trabajo 24.557? (fuente llm)",
     """MATCH (n:Norma {tipo: 'Decreto'})-[:CONTIENE]->(:Articulo)-[r:REGLAMENTA]->(d)
WHERE r.fuente = 'llm' AND d.id_norma = 27971
RETURN n.nombre AS decreto, n.fecha AS fecha, count(*) AS articulos
ORDER BY fecha"""),
    ("ranking", "¿Cuáles son las normas más modificadas? (fuente hibrido)",
     f"""MATCH (m:Norma)-[:CONTIENE]->(:Articulo)-[r]->(d)
WHERE r.fuente = 'hibrido' AND type(r) IN {TIPOS_CAMBIO} AND m.id_norma < 9000000
MATCH (n:Norma {{id_norma: d.id_norma}}) WHERE n <> m
RETURN n.nombre AS norma, left(n.titulo, 60) AS titulo, count(DISTINCT m) AS normas_que_la_modifican
ORDER BY normas_que_la_modifican DESC LIMIT 10"""),
    ("dos_saltos", "Reforma sobre reforma: normas que modifican a una modificatoria de la LCT (fuente hibrido)",
     f"""MATCH (m1:Norma)-[:CONTIENE]->(:Articulo)-[r1]->(d1)
WHERE r1.fuente = 'hibrido' AND type(r1) IN ['SUSTITUYE','INCORPORA','DEROGA','MODIFICA'] AND d1.id_norma = 25552
WITH DISTINCT m1
MATCH (m2:Norma)-[:CONTIENE]->(:Articulo)-[r2]->(d2)
WHERE r2.fuente = 'hibrido' AND type(r2) IN ['SUSTITUYE','INCORPORA','DEROGA','MODIFICA']
  AND d2.id_norma = m1.id_norma AND m2 <> m1
RETURN DISTINCT m2.nombre AS norma, m2.fecha AS fecha, type(r2) AS que_hizo, m1.nombre AS a_la_modificatoria
ORDER BY fecha DESC LIMIT 12"""),
    ("consenso", "¿Cuántos de los 7 parsers de InfoLEG encuentran cada vínculo?",
     """MATCH (m:Norma)-[:CONTIENE]->(:Articulo)-[r]->(d)
WHERE type(r) <> 'CITA' AND m.id_norma < 9000000 AND NOT r.fuente STARTS WITH 'unnoba'
WITH m, d.id_norma AS destino, collect(DISTINCT r.fuente) AS fuentes
WHERE destino <> m.id_norma
RETURN size(fuentes) AS cuantos_parsers, count(*) AS pares
ORDER BY cuantos_parsers DESC"""),
    ("dos_lecturas_conteo", "¿En cuántos artículos las reglas ven una cita y el LLM una acción?",
     """MATCH (n:Norma)-[:CONTIENE]->(o:Articulo)-[r1]->(d1), (o)-[r2]->(d2)
WHERE r1.fuente = 'reglas_v2' AND r2.fuente = 'llm' AND type(r1) = 'CITA' AND type(r2) <> 'CITA'
  AND d1.id_norma = d2.id_norma
RETURN type(r2) AS segun_el_llm, count(DISTINCT o) AS articulos ORDER BY articulos DESC"""),
    ("dos_lecturas", "Ejemplos: mismo artículo, dos lecturas",
     """MATCH (n:Norma)-[:CONTIENE]->(o:Articulo)-[r1]->(d1), (o)-[r2]->(d2)
WHERE r1.fuente = 'reglas_v2' AND r2.fuente = 'llm' AND type(r1) = 'CITA' AND type(r2) = 'SUSTITUYE'
  AND d1.id_norma = d2.id_norma
MATCH (dn:Norma {id_norma: d2.id_norma})
RETURN n.nombre AS norma, o.numero AS articulo, dn.nombre AS destino, type(r1) AS reglas, type(r2) AS llm,
       r2.verbo AS verbo_llm, left(r2.fragmento, 170) AS evidencia
LIMIT 6"""),
    ("evidencia_dnu70", "La evidencia completa de una arista: DNU 70/2023 sobre la LCT (fuente llm)",
     """MATCH (n:Norma {tipo: 'Decreto', numero: '70', anio: 2023})-[:CONTIENE]->(o)-[r]->(d:Articulo {id_norma: 25552})
WHERE r.fuente = 'llm'
RETURN o.numero AS art_dnu, type(r) AS que_hizo, d.numero AS art_lct, r.verbo AS verbo, r.metodo AS metodo,
       r.inicio AS desde, r.fin AS hasta, left(r.fragmento, 150) AS evidencia
ORDER BY toInteger(split(d.numero, ' ')[0]) LIMIT 8"""),
    ("clasificador_dudoso", "Los pares en que el random forest dudó (probabilidad cerca del umbral 0,45)",
     """MATCH (m:Norma)-[:CONTIENE]->(:Articulo)-[r]->(d)
WHERE r.fuente = 'random_forest' AND r.confianza <> ''
WITH m, d.id_norma AS destino, max(toFloat(r.confianza)) AS prob,
     max(CASE WHEN type(r) <> 'CITA' THEN 1 ELSE 0 END) AS acepta
MATCH (dn:Norma {id_norma: destino})
RETURN m.nombre AS origen, dn.nombre AS destino, prob, CASE acepta WHEN 1 THEN 'sí' ELSE 'no' END AS acepta
ORDER BY abs(prob - 0.45) LIMIT 8"""),
    ("texto_completo", "Búsqueda por texto: artículos que hablan de indemnización por despido",
     """CALL db.index.fulltext.queryNodes('articulo_texto', 'indemnización despido') YIELD node, score
MATCH (n:Norma)-[:CONTIENE]->(node)
RETURN n.nombre AS norma, node.numero AS articulo, round(score, 2) AS puntaje, left(node.texto, 120) AS texto
ORDER BY puntaje DESC LIMIT 8"""),
    ("unnoba_fuentes", "Digesto UNNOBA: aristas por parser",
     """MATCH (:Articulo)-[r]->() WHERE r.fuente STARTS WITH 'unnoba'
RETURN r.fuente AS fuente, type(r) AS tipo, count(*) AS aristas ORDER BY fuente, aristas DESC"""),
    ("unnoba_mas_modificadas", "Digesto UNNOBA: las normas más modificadas (fuente unnoba_hibrido)",
     """MATCH (m:Norma)-[:CONTIENE]->(:Articulo)-[r]->(d)
WHERE r.fuente = 'unnoba_hibrido' AND type(r) <> 'CITA'
MATCH (n:Norma {id_norma: d.id_norma}) WHERE n <> m
RETURN n.nombre AS norma, left(n.titulo, 60) AS titulo, count(DISTINCT m) AS documentos_que_la_cambian
ORDER BY documentos_que_la_cambian DESC LIMIT 6"""),
    ("visual_27802", "Para la vista de grafo: Ley 27.802 → artículos de la LCT (filas que dibuja)",
     """MATCH p = (:Norma {nombre: 'Ley 27802'})-[:CONTIENE]->(:Articulo)-[r:SUSTITUYE {fuente: 'llm'}]->(:Articulo)<-[:CONTIENE]-(:Norma {id_norma: 25552})
RETURN count(p) AS caminos"""),
]

# aristas a nivel norma para calcular la cadena más larga hasta la LCT
ARISTAS_NORMA = f"""MATCH (m:Norma)-[:CONTIENE]->(:Articulo)-[r]->(d)
WHERE r.fuente = 'hibrido' AND type(r) IN ['SUSTITUYE','INCORPORA','DEROGA','MODIFICA'] AND m.id_norma < 9000000
MATCH (n:Norma {{id_norma: d.id_norma}}) WHERE n <> m
RETURN DISTINCT m.id_norma AS o, m.nombre AS on, m.fecha AS of, n.id_norma AS d, n.nombre AS dn, n.fecha AS df"""


def cadena_mas_larga(filas, destino=25552):
    """Camino más largo que termina en la LCT, siguiendo solo aristas hacia normas no posteriores
    (la modificatoria es posterior o del mismo día que la modificada), así el grafo es acíclico."""
    nombre, fecha, entran = {}, {}, {}
    for f in filas:
        nombre[f["o"]], fecha[f["o"]], nombre[f["d"]], fecha[f["d"]] = f["on"], f["of"], f["dn"], f["df"]
        if (f["of"] or "") >= (f["df"] or ""):
            entran.setdefault(f["d"], set()).add(f["o"])
    memo = {}

    def mejor(n, visitados):
        if n in memo:
            return memo[n]
        cad = [n]
        for o in entran.get(n, ()):
            if o in visitados:
                continue
            c = mejor(o, visitados | {o})
            if len(c) + 1 > len(cad):
                cad = c + [n]
        memo[n] = cad
        return cad

    cad = mejor(destino, {destino})
    return [{"id_norma": n, "norma": nombre[n], "fecha": fecha[n]} for n in cad]


def main():
    from neo4j import GraphDatabase
    pw = os.environ.get("NEO4J_PASSWORD") or (RAIZ / ".neo4j_password").read_text().strip()
    res = {"fecha": datetime.now(timezone.utc).isoformat(), "uri": URI, "consultas": {}}
    md = ["# Resultados de las consultas de la demo (B76)", "",
          f"Corridas sobre `{URI}` el {res['fecha'][:16].replace('T', ' ')} UTC con `scripts/35_demo_consultas.py`.", ""]
    with GraphDatabase.driver(URI, auth=("neo4j", pw)) as drv, drv.session() as s:
        for clave, pregunta, cypher in CONSULTAS:
            try:
                filas = s.run(cypher).data()
                error = None
            except Exception as e:                      # se registra y se sigue con las demás
                filas, error = [], f"{type(e).__name__}: {e}"
            res["consultas"][clave] = {"pregunta": pregunta, "cypher": cypher, "filas": filas, "error": error}
            md += [f"## {clave}: {pregunta}", "", "```cypher", cypher, "```", ""]
            if error:
                md += [f"**ERROR:** {error}", ""]
            elif not filas:
                md += ["*(sin filas)*", ""]
            else:
                cols = list(filas[0])
                md += ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
                for f in filas:
                    md.append("| " + " | ".join(str(f[c]).replace("|", "/").replace("\n", " ") for c in cols) + " |")
                md.append("")
        cad = cadena_mas_larga(s.run(ARISTAS_NORMA).data())
        # consulta lista para dibujar la cadena en el Neo4j Browser (se prueba acá mismo)
        ids = [c["id_norma"] for c in cad]
        visual = (f"WITH {ids} AS ids\n"
                  "MATCH p = (m:Norma)-[:CONTIENE]->(:Articulo)-[r]->(d)\n"
                  "WHERE m.id_norma IN ids AND d.id_norma IN ids AND d.id_norma <> m.id_norma\n"
                  "  AND r.fuente = 'hibrido' AND type(r) IN ['SUSTITUYE','INCORPORA','DEROGA','MODIFICA']\n"
                  "OPTIONAL MATCH (n:Norma)-[:CONTIENE]->(d)\n"
                  "RETURN p, n")
        filas_visual = len(s.run(visual).data())
    res["cadena_lct"] = cad
    res["cadena_lct_visual"] = {"cypher": visual, "filas": filas_visual}
    md += ["## cadena_lct: la cadena de modificaciones más larga que llega a la LCT (fuente hibrido)", "",
           f"{len(cad) - 1} saltos:", ""] + [f"{i}. {c['norma']} ({c['fecha']}, id {c['id_norma']})" for i, c in enumerate(cad)]
    md += ["", f"Para dibujarla en el Browser ({filas_visual} filas):", "", "```cypher", visual, "```"]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "consultas.json").write_text(json.dumps(res, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    (OUT / "consultas.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    errores = [k for k, v in res["consultas"].items() if v["error"]]
    print("listo:", OUT / "consultas.md", "| errores:", errores or "ninguno", "| cadena:", len(cad) - 1, "saltos")


if __name__ == "__main__":
    sys.exit(main())
