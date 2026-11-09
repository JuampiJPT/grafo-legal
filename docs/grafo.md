# Grafo normativo en Neo4j

El grafo representa qué hace cada norma sobre otras: qué artículos sustituye, incorpora, deroga, reglamenta, modifica o cita. Se arma solo a partir de la salida estándar de los parsers (`docs/salida_estandar.md`), así que sirve para cualquier documento normativo y para cualquier parser (bitácora B41 y B42). InfoLEG no forma parte del grafo: se usa como referencia para evaluarlo (`scripts/11_evaluar_grafo.py`).

## Modelo

```
(:Norma)-[:CONTIENE]->(:Articulo)
(:Articulo)-[:SUSTITUYE | INCORPORA | DEROGA | REGLAMENTA | MODIFICA | CITA]->(:Articulo)
(:Articulo)-[...el mismo tipo...]->(:Norma)
```

- **El destino es un artículo** cuando el texto dice cuál («Sustitúyese el artículo 245 de la Ley 20.744»).
- **El destino es la norma** cuando se la nombra entera («Derógase la Ley 25.323», «conforme a la Ley 24.013»).
- **El origen es siempre un artículo** de la norma que contiene el texto. Las menciones del VISTO y el CONSIDERANDO salen del encabezado, que es el artículo 0.

Ejemplo: `(art. 70 del Decreto 70/2023)-[:SUSTITUYE]->(art. 80 de la Ley 20.744)`.

| Elemento | Cantidad (reglas v2) | Propiedades |
|---|---|---|
| `Norma` | 340 | `id_norma`, `nombre` («Ley 20744»), `tipo`, `numero`, `fecha`, `anio`, `titulo`, `sumario`, `organismo`, `split`, `tiene_texto` |
| `Articulo` | 8.129 | `id` («id_norma#orden»), `id_norma`, `numero`, `zona`, `inicio`, `fin`, `texto`, `tiene_texto` |
| `CONTIENE` | 8.129 | |
| Relaciones tipadas | 3.277: 2.332 `CITA`, 375 `SUSTITUYE`, 181 `INCORPORA`, 176 `MODIFICA`, 155 `DEROGA`, 58 `REGLAMENTA` | `fuente`, `parte_origen`, `verbo`, `metodo`, `confianza`, `n_menciones`, `inicio`, `fin`, `fragmento` |

Decisiones del modelo:

- **La relación es una arista con tipo**, no un nodo. Así una pregunta como «¿qué derogó la Ley 27.802?» se escribe directo en Cypher, con `[:DEROGA]`.
- **La evidencia va en la arista.** Toda relación lleva el fragmento de texto y su posición, para que una respuesta se pueda justificar con el texto de la norma.
- **`fuente` identifica al parser.** Si se cargan varios parsers, cada uno tiene sus propias aristas, y una consulta elige cuál usa con `{fuente: 'reglas_v2'}`.
- **Artículos sin texto.** 63 artículos destino no están en el texto segmentado del corpus: su norma no tiene texto, o el número no se encontró. Se crean igual, con `tiene_texto = false`.

## Cómo cargarlo

El TP usa un contenedor de Neo4j propio, para no pisar otra base de la misma máquina. Tiene otros puertos (7475 para el navegador, 7688 para Bolt) y su propio volumen. La clave va en `.neo4j_password`, que git ignora.

```bash
docker run -d --name neo4j-grafo-legal \
  -p 7475:7474 -p 7688:7687 \
  -v neo4j-grafo-legal:/data \
  -e NEO4J_AUTH=neo4j/$(cat .neo4j_password) \
  neo4j:5
```

Después, un solo comando arma las relaciones, carga el grafo y lo evalúa leyéndolo de Neo4j:

```bash
bash cargar_y_evaluar_grafo.sh
```

El navegador queda en http://localhost:7475, conectándose a `bolt://localhost:7688` con el usuario `neo4j`. El contenedor se frena con `docker stop neo4j-grafo-legal` y se vuelve a levantar con `docker start neo4j-grafo-legal`.

## Evaluación del grafo

`scripts/11_evaluar_grafo.py` lee las relaciones **desde el grafo**, no desde los archivos del parser, y mide tres cosas:

1. **Ida y vuelta.** Las relaciones que devuelve el grafo tienen que ser exactamente las que se cargaron. Cualquier diferencia es un error de carga.
2. **Comparación con InfoLEG.** Las relaciones se proyectan a pares de normas y se comparan con las que registra InfoLEG, por split. Como InfoLEG no dice el tipo, también se mide qué proporción de cada tipo coincide con un vínculo de InfoLEG.
3. **Por norma semilla.** Para cada una, cuántas de sus modificatorias según InfoLEG aparecen en el grafo.

Los resultados están en `results/evaluacion_grafo/RESULTADOS.md`.

## Consultas de ejemplo

Son la base para el text-to-Cypher (F7): cada una responde una pregunta en lenguaje natural.

**1. ¿Qué artículos de la Ley de Contrato de Trabajo sustituyó la Ley 27.802, y con qué texto?**

```cypher
MATCH (n:Norma {nombre: 'Ley 27802'})-[:CONTIENE]->(a)-[r:SUSTITUYE]->(d:Articulo)<-[:CONTIENE]-(:Norma {nombre: 'Ley 20744'})
RETURN a.numero AS articulo_27802, d.numero AS articulo_lct, r.fragmento
ORDER BY toInteger(split(d.numero, ' ')[0])
```

**2. ¿Qué normas derogaron algo de la Ley 24.013?**

```cypher
MATCH (n:Norma)-[:CONTIENE]->(:Articulo)-[r:DEROGA]->(d)
WHERE (d:Norma AND d.nombre = 'Ley 24013') OR (d:Articulo AND d.id_norma = 412)
RETURN DISTINCT n.nombre, n.fecha, coalesce(d.numero, 'toda la ley') AS que
ORDER BY n.fecha
```

**3. ¿Quién cambió por última vez el artículo 245 de la LCT?**

```cypher
MATCH (n:Norma)-[:CONTIENE]->(:Articulo)-[r:SUSTITUYE|MODIFICA|INCORPORA|DEROGA]->(d:Articulo {id_norma: 25552, numero: '245'})
RETURN n.nombre, n.fecha, type(r) AS que_hizo, r.fragmento
ORDER BY n.fecha DESC LIMIT 1
```

**4. ¿Qué decretos reglamentan la Ley de Riesgos del Trabajo?**

```cypher
MATCH (n:Norma {tipo: 'Decreto'})-[:CONTIENE]->(:Articulo)-[:REGLAMENTA]->(d)
WHERE (d:Norma AND d.id_norma = 27971) OR (d:Articulo AND d.id_norma = 27971)
RETURN DISTINCT n.nombre, n.fecha ORDER BY n.fecha
```

**5. ¿Qué artículos hablan de indemnización por despido?** (índice de texto completo)

```cypher
CALL db.index.fulltext.queryNodes('articulo_texto', 'indemnización despido') YIELD node, score
MATCH (n:Norma)-[:CONTIENE]->(node)
RETURN n.nombre, node.numero, score, left(node.texto, 200) ORDER BY score DESC LIMIT 10
```

## Embeddings

El grafo no lleva vectores. Si F7 usa recuperación semántica (GraphRAG) además del text-to-Cypher, el lugar natural es una propiedad `embedding` en `Articulo` con un índice vectorial de Neo4j 5. Antes hay que elegir el modelo de embeddings: uno local en español o la API de un proveedor.
