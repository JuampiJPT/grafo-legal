# Grafo normativo en Neo4j

`scripts/09_armar_grafo.py` arma los archivos del grafo en `data/grafo/` y, si recibe una conexión, los carga en Neo4j (bitácora B38). La consigna del modelo es que **lo que dice InfoLEG y lo que extrae cada parser no se mezclen**, y que toda arista extraída se pueda rastrear hasta el artículo y el fragmento que la sustentan.

## Modelo

```
(:Norma)-[:TIENE_ARTICULO]->(:Articulo)
(:Norma)-[:RELACION_INFOLEG]->(:Norma)
(:Norma)-[:RELACION_EXTRAIDA {parser}]->(:Norma)
(:Articulo)-[:MENCIONA]->(:Norma)
```

| Elemento | Cantidad | Propiedades principales |
|---|---|---|
| `Norma` | 340 | `id_norma`, `nombre` («Ley 20744»), `tipo`, `numero`, `fecha`, `anio`, `titulo`, `sumario`, `organismo`, `rol` (semilla o expansión), `split`, `tiene_texto`, `url_texto` |
| `Articulo` | 8.066 | `id` («id_norma#orden»), `numero`, `zona`, `inicio`, `fin`, `texto` |
| `TIENE_ARTICULO` | 8.066 | |
| `RELACION_INFOLEG` | 775 | `split`, `fuente`. Es el gold: lo que registra la base complementaria de InfoLEG |
| `RELACION_EXTRAIDA` | 2.308 (771 de reglas_v2, 804 de reglas_v1, 733 del clasificador) | `parser`, `config`, `puntaje`, `n_evidencias`, `articulos`, `en_infoleg`, `split` |
| `MENCIONA` | 4.430 | `parte` (visto, considerando, articulado, anexo, notas), `inicio`, `fin`, `superficie`, `metodo`, `verbo`, `temporal_ok`, `procedencia`, `cuenta_en_reglas_v2`, `fragmento` |

Decisiones del modelo (D15):

- **Una relación extraída por par y por parser.** Así se comparan los parsers con una consulta. Cuando se sumen el parser LLM y el híbrido, se agregan con otro valor de `parser`, sin tocar lo demás.
- **`en_infoleg` en la arista extraída.** Es una copia de si el par está en el gold, para el análisis de errores. Una consulta de usuario («qué modifica a…») tiene que usar `RELACION_INFOLEG` o una `RELACION_EXTRAIDA` de un parser, y decir cuál usó.
- **Los artículos llevan el texto.** Así la evidencia se puede leer desde el grafo, y el índice de texto completo permite buscar en el articulado.
- **Las menciones son todas las que detectó el parser**, incluidas las que la regla no cuenta (`cuenta_en_reglas_v2 = false`). Las aristas de reglas_v2 son exactamente los pares con al menos una mención que cuenta; lo comprueba `tests/test_pipeline.py::test_grafo_trazable`.
- **Las aristas del clasificador no tienen menciones propias.** Su evidencia son las menciones del mismo par, y su `puntaje` es la probabilidad: en dev, la de la validación cruzada.

## Cómo cargarlo

Hace falta Neo4j 5 (Desktop, Docker o AuraDB) y el driver de Python (`pip install neo4j`, ya en `requirements.txt`).

```bash
python scripts/09_armar_grafo.py                    # arma data/grafo/ y muestra los conteos
export NEO4J_PASSWORD=...                            # la contraseña de tu base local
python scripts/09_armar_grafo.py --uri bolt://localhost:7687 --user neo4j --borrar
```

`--borrar` elimina los nodos `Norma` y `Articulo` antes de cargar, para que una recarga no duplique las menciones. El script crea las restricciones de unicidad y un índice de texto completo sobre `Articulo.texto`.

Desde esta sesión de trabajo no se pudo descargar Neo4j. Los CSV y la trazabilidad están verificados, y las consultas 1 y 3 se probaron sobre una copia del grafo en memoria (networkx y grand-cypher). El Cypher de carga se corre por primera vez en la máquina del equipo.

## Consultas de ejemplo

Sirven de base para el text-to-Cypher (F7): cada una responde una pregunta en lenguaje natural.

**1. ¿Qué normas modificaron la Ley de Contrato de Trabajo, según el parser, y dónde lo dicen?**

```cypher
MATCH (o:Norma)-[r:RELACION_EXTRAIDA {parser: 'reglas_v2'}]->(d:Norma {nombre: 'Ley 20744'})
MATCH (o)-[:TIENE_ARTICULO]->(a:Articulo)-[m:MENCIONA {cuenta_en_reglas_v2: true}]->(d)
RETURN o.nombre, o.fecha, a.numero, m.parte, m.fragmento
ORDER BY o.fecha
```

Sobre la copia en memoria: 104 normas, de las cuales 94 también están en InfoLEG, que registra 130.

**2. ¿Qué relaciones registra InfoLEG que el parser no encontró?**

```cypher
MATCH (o:Norma)-[g:RELACION_INFOLEG]->(d:Norma)
WHERE NOT (o)-[:RELACION_EXTRAIDA {parser: 'reglas_v2'}]->(d)
RETURN o.nombre, d.nombre, g.split, o.tiene_texto
```

**3. ¿Qué normas modificaron a las normas que modificaron la LCT?** (dos saltos, solo InfoLEG)

```cypher
MATCH p = (x:Norma)-[:RELACION_INFOLEG]->(y:Norma)-[:RELACION_INFOLEG]->(:Norma {nombre: 'Ley 20744'})
RETURN x.nombre, y.nombre
```

**4. ¿Qué artículos hablan de indemnización por despido?** (índice de texto completo)

```cypher
CALL db.index.fulltext.queryNodes('articulo_texto', 'indemnización despido') YIELD node, score
MATCH (n:Norma)-[:TIENE_ARTICULO]->(node)
RETURN n.nombre, node.numero, score, left(node.texto, 200) ORDER BY score DESC LIMIT 10
```

**5. ¿En qué difieren los parsers?**

```cypher
MATCH (o:Norma)-[r:RELACION_EXTRAIDA]->(d:Norma)
RETURN r.parser, r.split, count(*) AS aristas, avg(CASE WHEN r.en_infoleg THEN 1.0 ELSE 0.0 END) AS precision
```

## Embeddings

El grafo de esta versión no lleva vectores. Si F7 usa recuperación semántica (GraphRAG) además del text-to-Cypher, el lugar natural es una propiedad `embedding` en `Articulo` con un índice vectorial de Neo4j 5. Para eso hay que elegir un modelo de embeddings: un modelo local en español, o la API de un proveedor. Queda como decisión abierta.
