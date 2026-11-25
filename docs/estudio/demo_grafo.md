# Guía de la demo del grafo en Neo4j

Guion para mostrar el grafo en el coloquio. Cada consulta tiene la pregunta en castellano, el Cypher para pegar, **el resultado real** (corrido sobre la base del equipo el 25/11/2026 con `scripts/35_demo_consultas.py`; la salida completa está en `results/demo/consultas.md`) y qué decir al mostrarlo.

---

## 0. Antes de entrar (preparación, 5 minutos)

1. **Levantar la base:** `docker start neo4j-grafo-legal` (si estaba frenada).
2. **Abrir el navegador de Neo4j:** http://localhost:7475. Conectar a `bolt://localhost:7688`, usuario `neo4j`, con la clave de `.neo4j_password`.
3. **Que los nodos muestren nombres y no números:** en cualquier resultado con vista de grafo, hacé clic en la etiqueta `Norma` de la parte de arriba y elegí como *caption* `nombre`; en `Articulo`, elegí `numero`. Si querés, poné `Norma` de un color y `Articulo` de otro.
4. **Guardar las consultas como favoritas** (la estrella del editor). En vivo no se tipea: se hace clic.
5. **Probar una vez cada consulta** antes de entrar. Si alguna tarda, ya quedó en caché.
6. **Tener a mano** `results/demo/consultas.md` por si algo falla: tiene todos los resultados.

**Si algo falla en vivo:** si la base no responde, `docker start neo4j-grafo-legal` y esperar 10 segundos. Si una consulta tira error de sintaxis, mostrar el resultado guardado y seguir.

---

## 1. El guion corto (4 a 5 minutos, lo imperdible)

| # | Qué mostrar | Por qué impresiona | Vista |
|---|---|---|---|
| 1 | Qué hay en la base (sec. 2.1) | 444 normas, 8.545 artículos, 10 fuentes | Tabla |
| 2 | La Ley 27.802 sobre la LCT (sec. 2.2) | 52 artículos sustituidos, con su evidencia | **Grafo** + tabla |
| 3 | Historia del art. 245 (sec. 2.3) | Siete normas en 50 años, y qué parsers vieron cada una | Tabla |
| 4 | La cadena más larga hasta la LCT (sec. 2.4) | 14 saltos de reformas encadenadas | **Grafo** |
| 5 | Mismo artículo, dos lecturas (sec. 2.6) | Las reglas ven una cita y el LLM una sustitución | Tabla |
| 6 | La evidencia de una arista (sec. 2.7) | Cada arista dice de dónde sale: artículo, verbo, offsets, texto | Tabla |

Si queda tiempo o preguntan: secciones 3 y 4.

---

## 2. Las consultas principales

### 2.1 ¿Qué hay en la base?

```cypher
MATCH (n) WHERE n:Norma OR n:Articulo
RETURN labels(n)[0] AS etiqueta, count(*) AS cantidad
```

| etiqueta | cantidad |
|---|---|
| Articulo | 8.545 |
| Norma | 444 |

```cypher
MATCH (:Articulo)-[r]->() WHERE type(r) <> 'CONTIENE'
RETURN r.fuente AS fuente, count(*) AS aristas,
       sum(CASE WHEN type(r) <> 'CITA' THEN 1 ELSE 0 END) AS no_cita
ORDER BY fuente
```

| fuente | aristas | no CITA |
|---|---|---|
| hibrido | 3.147 | 1.356 |
| hibrido_tfidf | 3.273 | 1.427 |
| llm | 3.247 | 1.022 |
| random_forest | 3.283 | 1.327 |
| reglas_v2 | 3.277 | 945 |
| reglas_v3 | 3.149 | 848 |
| tfidf | 3.280 | 1.384 |
| unnoba_hibrido | 150 | 62 |
| unnoba_llm | 156 | 23 |
| unnoba_reglas_v3 | 150 | 13 |

**Qué decir.**
- «Son 340 normas de InfoLEG y 104 del digesto de la UNNOBA, y cada artículo es un nodo.»
- «Cada parser escribe sus propias aristas sobre los mismos nodos, con la propiedad `fuente`. Así conviven siete lecturas de InfoLEG y tres del digesto sin pisarse, y se pueden comparar con una consulta.»
- «La mayoría de las aristas son CITA: la norma nombra a otra pero no la cambia. Las que no son CITA son las acciones: sustituye, incorpora, deroga, reglamenta, modifica.»
- Si preguntan por qué las reglas tienen menos aristas «no CITA» que el LLM: las reglas tipan por verbo y muchas menciones quedan como CITA; el LLM lee la oración y encuentra más acciones (por ejemplo, reglamentaciones).

### 2.2 ¿Qué le hizo la Ley 27.802 (reforma laboral 2026) a la LCT?

**Resumen:**
```cypher
MATCH (:Norma {nombre: 'Ley 27802'})-[:CONTIENE]->(a)-[r]->(d:Articulo {id_norma: 25552})
WHERE r.fuente = 'llm' AND type(r) <> 'CITA'
RETURN type(r) AS que_hizo, count(DISTINCT d) AS articulos_de_la_lct
ORDER BY articulos_de_la_lct DESC
```

| qué hizo | artículos de la LCT |
|---|---|
| SUSTITUYE | 52 |
| DEROGA | 9 |
| INCORPORA | 3 |

**Detalle con evidencia:**
```cypher
MATCH (:Norma {nombre: 'Ley 27802'})-[:CONTIENE]->(a)-[r:SUSTITUYE]->(d:Articulo {id_norma: 25552})
WHERE r.fuente = 'llm'
RETURN a.numero AS art_27802, d.numero AS art_lct, left(r.fragmento, 160) AS evidencia
ORDER BY toInteger(split(d.numero, ' ')[0]) LIMIT 12
```

Primeras filas: art. 1 → art. 2 de la LCT («Sustitúyese el artículo 2° de la Ley de Contrato de Trabajo N° 20.744 (t.o. 1976)…»), art. 2 → art. 4, art. 3 → art. 9, art. 4 → art. 11…

**Para la vista de grafo** (dibuja 52 caminos):
```cypher
MATCH p = (:Norma {nombre: 'Ley 27802'})-[:CONTIENE]->(:Articulo)-[r:SUSTITUYE {fuente: 'llm'}]->(:Articulo)<-[:CONTIENE]-(:Norma {id_norma: 25552})
RETURN p
```

**Qué decir.**
- «Esta es la pregunta que motivó el trabajo: qué cambió la reforma de 2026. Se responde con un patrón directo porque la relación es una arista tipada.»
- «Cada arista sale de un artículo de la 27.802 y llega a un artículo de la LCT: el grafo sabe *qué artículo* cambió, no solo *qué ley*.»
- En la vista de grafo: «a la izquierda la Ley 27.802 con sus artículos, a la derecha la LCT; cada flecha es una sustitución con su texto».
- Uso `fuente = 'llm'` porque es el mejor tipando (macro-F1 0,883). Con `reglas_v2` sale casi lo mismo en las sustituciones, porque el verbo «Sustitúyese» es explícito.

### 2.3 Historia del artículo 245 de la LCT (indemnización por despido)

```cypher
MATCH (n:Norma)-[:CONTIENE]->(o)-[r]->(:Articulo {id_norma: 25552, numero: '245'})
WHERE type(r) <> 'CITA'
RETURN n.nombre AS norma, n.fecha AS fecha, type(r) AS que_hizo, collect(DISTINCT r.fuente) AS fuentes
ORDER BY fecha
```

| norma | fecha | qué hizo | cuántos parsers la ven |
|---|---|---|---|
| Ley 23.697 | 1989-09-25 | SUSTITUYE | 7 de 7 |
| Ley 24.013 | 1991-12-17 | SUSTITUYE | 7 de 7 |
| Ley 25.323 | 2000-10-11 | MODIFICA | 6 (todos menos el LLM; ver abajo) |
| Ley 25.877 | 2004-03-19 | SUSTITUYE | 7 de 7 |
| DNU 70/2023 | 2023-12-21 | SUSTITUYE | 7 de 7 |
| Ley 27.742 | 2024-07-08 | SUSTITUYE | 6 (todos menos el LLM; ver abajo) |
| Ley 27.802 | 2026-03-06 | SUSTITUYE | 7 de 7 |

**Qué decir.**
- «El artículo más litigado de la LCT, la indemnización por despido, cambió siete veces en 37 años, y el grafo tiene cada una con su norma y su fecha.»
- «La última modificación es la de la Ley 27.802. Esto es lo que usamos para reconstruir el texto vigente: aplicar estas cadenas en orden.»
- «La columna de fuentes muestra el consenso: cinco de los siete cambios los encuentran los siete parsers.»
- **Los dos que no ve el LLM son un ejemplo de por qué el LLM tipa mejor.** Ahí el LLM tiene razón y las reglas no:
  - la **Ley 25.323** duplica la indemnización «prevista en el artículo 245» sin tocar su texto: es una remisión. Las reglas la marcaron MODIFICA porque tomaron «texto ordenado» como si fuera un verbo; el LLM la deja como CITA;
  - el **art. 96 de la Ley 27.742** dice que un fondo de cese laboral puede «sustituir» la indemnización del 245: el verbo no actúa sobre el texto. Las reglas lo tomaron como SUSTITUYE; el LLM, como CITA. La reforma de la 27.742 a la LCT está en otros artículos (88 a 95), y el LLM los ve.
  - Los clasificadores heredan el tipo de las reglas, por eso también los listan.
  - Las sustituciones reales del 245 son las de 1989, 1991, 2004, 2023 y 2026.

### 2.4 La cadena de reformas más larga que llega a la LCT

Se calcula en Python (`scripts/35_demo_consultas.py`), porque las aristas van de artículo a artículo y Cypher sin APOC no proyecta la cadena a nivel norma. Cada salto va de una norma a otra anterior que ella modifica (fuente `hibrido`).

**14 saltos:** Decreto 551/2022 → Decreto 711/2021 → Decreto 493/2021 → Decreto 191/2021 → Ley 27.541 (2019) → Ley 27.260 (2016) → Ley 26.940 (2014) → Ley 26.476 (2008) → Ley 25.877 (2004) → Ley 25.250 (2000) → Ley 25.013 (1998) → Ley 24.465 (1995) → Ley 24.013 (1991) → Ley 23.697 (1989) → **Ley 20.744 (LCT, 1974)**.

**Para dibujarla** (89 filas):
```cypher
WITH [370565, 355459, 352666, 348194, 333564, 263691, 230592, 148719, 93595, 63208, 53159, 15931, 412, 15, 25552] AS ids
MATCH p = (m:Norma)-[:CONTIENE]->(:Articulo)-[r]->(d)
WHERE m.id_norma IN ids AND d.id_norma IN ids AND d.id_norma <> m.id_norma
  AND r.fuente = 'hibrido' AND type(r) IN ['SUSTITUYE','INCORPORA','DEROGA','MODIFICA']
OPTIONAL MATCH (n:Norma)-[:CONTIENE]->(d)
RETURN p, n
```

**Qué decir.**
- «Esto muestra por qué hace falta un grafo y no una tabla: una norma de 2022 modifica a un decreto, que modifica a otro, y así hasta la LCT de 1974. Para saber qué rige hoy hay que recorrer la cadena.»
- **Si te preguntan por el «16» del informe:** el ranking de B61 cuenta cualquier relación que no sea CITA (incluida REGLAMENTA) y no exige orden de fechas; da 16. Esta cadena solo sigue cambios reales y exige que cada modificatoria sea posterior a la modificada: da 14. Las dos son correctas, con criterios distintos.

### 2.5 ¿Cuáles son las normas más modificadas?

```cypher
MATCH (m:Norma)-[:CONTIENE]->(:Articulo)-[r]->(d)
WHERE r.fuente = 'hibrido' AND type(r) IN ['SUSTITUYE','INCORPORA','DEROGA','MODIFICA','REGLAMENTA'] AND m.id_norma < 9000000
MATCH (n:Norma {id_norma: d.id_norma}) WHERE n <> m
RETURN n.nombre AS norma, left(n.titulo, 60) AS titulo, count(DISTINCT m) AS normas_que_la_modifican
ORDER BY normas_que_la_modifican DESC LIMIT 10
```

| norma | normas que la modifican |
|---|---|
| Ley 20.744 (LCT) | 105 |
| Ley 24.013 (Empleo) | 81 |
| Ley 24.241 (Jubilaciones) | 62 |
| Ley 24.557 (Riesgos del Trabajo) | 61 |
| Ley 23.551 (Asociaciones Sindicales) | 20 |
| Ley 14.250 (Convenios Colectivos) | 20 |
| Ley 23.660 (Obras Sociales) | 19 |

**Qué decir.** «La LCT es la más modificada, con 105 normas: por eso la elegimos para reconstruir el texto vigente. Fijate que aparecen las anclas del corpus y también normas que no elegimos nosotros, como la 24.241, que el grafo descubre solo.» (`id_norma < 9000000` deja afuera el digesto.)

### 2.6 El mismo artículo, dos lecturas: reglas contra LLM

**Cuántas veces pasa:**
```cypher
MATCH (n:Norma)-[:CONTIENE]->(o:Articulo)-[r1]->(d1), (o)-[r2]->(d2)
WHERE r1.fuente = 'reglas_v2' AND r2.fuente = 'llm' AND type(r1) = 'CITA' AND type(r2) <> 'CITA'
  AND d1.id_norma = d2.id_norma
RETURN type(r2) AS segun_el_llm, count(DISTINCT o) AS articulos ORDER BY articulos DESC
```

| el LLM dice | artículos donde las reglas dicen CITA |
|---|---|
| REGLAMENTA | 124 |
| MODIFICA | 61 |
| SUSTITUYE | 34 |
| DEROGA | 25 |
| INCORPORA | 10 |

**Ejemplos:**
```cypher
MATCH (n:Norma)-[:CONTIENE]->(o:Articulo)-[r1]->(d1), (o)-[r2]->(d2)
WHERE r1.fuente = 'reglas_v2' AND r2.fuente = 'llm' AND type(r1) = 'CITA' AND type(r2) = 'SUSTITUYE'
  AND d1.id_norma = d2.id_norma
MATCH (dn:Norma {id_norma: d2.id_norma})
RETURN n.nombre AS norma, o.numero AS articulo, dn.nombre AS destino, type(r1) AS reglas, type(r2) AS llm,
       r2.verbo AS verbo_llm, left(r2.fragmento, 170) AS evidencia
LIMIT 6
```

Ejemplo real: **Ley 21.824, encabezado** → LCT: las reglas dicen CITA y el LLM dice SUSTITUYE, con «Sustitúyese el artículo 177 del régimen de contrato de trabajo, según texto ordenado por el Decreto N° 390/76…». Otro: **Ley 24.347, art. 1** → Ley 24.241: «Modifícanse los artículos 3º, inciso 5; 21, 24, 34, 40 y 97 de la ley 24.241…».

**Qué decir.**
- «Esto es la diferencia entre leer la superficie y leer la oración. La regla decide el tipo por el verbo y la zona, y acá no le alcanzó: en el primer caso, el verbo está en el sumario del encabezado; en el segundo, en plural y con una lista de artículos.»
- «Es el resultado de la tabla de tipos hecho visible: el LLM sube la macro-F1 de 0,672 a 0,883.»
- Matiz honesto: esta cuenta muestra **dónde difieren**, no quién acierta. Para saber quién acierta medimos el tipo sobre 78 casos revisados a mano. En la sección 2.3 hay dos casos al revés: las reglas ven una acción y el LLM, con razón, una cita.

### 2.7 La evidencia de una arista (trazabilidad)

```cypher
MATCH (n:Norma {tipo: 'Decreto', numero: '70', anio: 2023})-[:CONTIENE]->(o)-[r]->(d:Articulo {id_norma: 25552})
WHERE r.fuente = 'llm'
RETURN o.numero AS art_dnu, type(r) AS que_hizo, d.numero AS art_lct, r.verbo AS verbo, r.metodo AS metodo,
       r.inicio AS desde, r.fin AS hasta, left(r.fragmento, 150) AS evidencia
ORDER BY toInteger(split(d.numero, ' ')[0]) LIMIT 8
```

| art. DNU | qué hizo | art. LCT | verbo | método | desde–hasta | evidencia |
|---|---|---|---|---|---|---|
| 65 | SUSTITUYE | 2 | Sustitúyese | llm | 55935–55960 | «ARTÍCULO 65.- Sustitúyese el artículo 2° de la Ley N° 20.744 (t.o. 1976)…» |
| 66 | SUSTITUYE | 9 | Sustitúyese | llm | 57230–57255 | «ARTÍCULO 66.- Sustitúyese el artículo 9°…» |
| 60 | CITA | 29 | — | llm | 53624–53637 | «…En virtud de lo establecido en los artículos 29 y 30 de la L…» |

**Qué decir.**
- «La consigna pide que cada arista conserve norma origen, destino, tipo, fragmento, ubicación y método. Acá está todo: artículo 65 del DNU, sustituye el artículo 2 de la LCT, el verbo, el método que la produjo, y los offsets exactos en el texto limpio (55.935 a 55.960).»
- «La fila del art. 60 muestra la diferencia entre acción y cita: el artículo 60 del DNU nombra los artículos 29 y 30 de la LCT, pero lo que hace es incorporar un artículo a otra ley (la 24.013). El grafo lo registra como CITA, no como cambio.»
- «Con los offsets se puede abrir el texto y resaltar la cita: las respuestas se justifican con el texto de la norma.»

---

## 3. Consultas para lucirse (si hay tiempo o preguntan)

### 3.1 ¿En qué décadas se reformó más la LCT?

```cypher
MATCH (n:Norma)-[:CONTIENE]->(:Articulo)-[r]->(d)
WHERE r.fuente = 'llm' AND type(r) IN ['SUSTITUYE','INCORPORA','DEROGA','MODIFICA'] AND d.id_norma = 25552
RETURN (n.anio / 10) * 10 AS decada, count(DISTINCT n) AS normas, count(*) AS cambios
ORDER BY decada
```

| década | normas | cambios |
|---|---|---|
| 1970 | 4 | 5 |
| 1980 | 5 | 7 |
| 1990 | 10 | 26 |
| 2000 | 9 | 29 |
| 2010 | 15 | 21 |
| **2020** | 8 | **106** |

**Qué decir.** «En los años 2020 hubo pocas normas pero muchísimos cambios: el DNU 70/2023, la Ley 27.742 y la Ley 27.802 reescriben la LCT en bloque. Es análisis temporal sobre el grafo, uno de los usos que la consigna propone para el final.»

### 3.2 Reforma sobre reforma: quién modifica a las modificatorias de la LCT

```cypher
MATCH (m1:Norma)-[:CONTIENE]->(:Articulo)-[r1]->(d1)
WHERE r1.fuente = 'hibrido' AND type(r1) IN ['SUSTITUYE','INCORPORA','DEROGA','MODIFICA'] AND d1.id_norma = 25552
WITH DISTINCT m1
MATCH (m2:Norma)-[:CONTIENE]->(:Articulo)-[r2]->(d2)
WHERE r2.fuente = 'hibrido' AND type(r2) IN ['SUSTITUYE','INCORPORA','DEROGA','MODIFICA']
  AND d2.id_norma = m1.id_norma AND m2 <> m1
RETURN DISTINCT m2.nombre AS norma, m2.fecha AS fecha, type(r2) AS que_hizo, m1.nombre AS a_la_modificatoria
ORDER BY fecha DESC LIMIT 12
```

Resultado: en 2026, los Decretos 1228, 612, 408, 407 y 242 ya modifican a la Ley 27.802, y el Decreto 1203 al Decreto 214. **Qué decir:** «La reforma de marzo de 2026 ya tiene modificaciones encima: son dos saltos en el grafo. Por eso el texto vigente no se puede leer de una sola norma.»

### 3.3 ¿Cuántos parsers coinciden en cada vínculo?

```cypher
MATCH (m:Norma)-[:CONTIENE]->(:Articulo)-[r]->(d)
WHERE type(r) <> 'CITA' AND m.id_norma < 9000000 AND NOT r.fuente STARTS WITH 'unnoba'
WITH m, d.id_norma AS destino, collect(DISTINCT r.fuente) AS fuentes
WHERE destino <> m.id_norma
RETURN size(fuentes) AS cuantos_parsers, count(*) AS pares
ORDER BY cuantos_parsers DESC
```

| parsers que lo encuentran (de 7) | pares |
|---|---|
| 7 | 202 |
| 6 | 67 |
| 5 | 68 |
| 4 | 322 |
| 3 | 126 |
| 2 | 87 |
| 1 | 70 |

**Qué decir.** «Hay 202 vínculos en los que coinciden los siete métodos: son el núcleo seguro, las sustituciones con verbo explícito. En el otro extremo, 70 los ve un solo método: ahí están las dudas, como las citas del VISTO. Esto es lo que aprovecha el híbrido por intersección: quedarse con lo que dos métodos distintos confirman.»
Nota: se cuentan aristas que no son CITA. En los grafos de los clasificadores, un par rechazado queda todo como CITA, así que también cuenta como «no lo ve».

### 3.4 ¿Qué normas derogaron partes de la Ley de Empleo?

```cypher
MATCH (n:Norma)-[:CONTIENE]->(:Articulo)-[r:DEROGA]->(d)
WHERE r.fuente = 'llm' AND d.id_norma = 412
RETURN DISTINCT n.nombre AS norma, n.fecha AS fecha, coalesce(d.numero, 'toda la ley') AS que_derogo
ORDER BY fecha
```

Resultado: la Ley 25.013 (1998) derogó los arts. 18, 31, 28 a 40 y 43 a 65; la Ley 26.598 (2010) el 141; el DNU 70/2023 y la Ley 27.742 los arts. 8 a 17 y 120. **Qué decir:** «El DNU 70/2023 y la Ley 27.742 derogan lo mismo: los arts. 8 a 17 de la Ley de Empleo, las indemnizaciones por empleo no registrado. El grafo muestra que dos normas distintas hicieron la misma derogación.»

### 3.5 ¿Qué decretos reglamentan la Ley de Riesgos del Trabajo?

```cypher
MATCH (n:Norma {tipo: 'Decreto'})-[:CONTIENE]->(:Articulo)-[r:REGLAMENTA]->(d)
WHERE r.fuente = 'llm' AND d.id_norma = 27971
RETURN n.nombre AS decreto, n.fecha AS fecha, count(*) AS articulos
ORDER BY fecha
```

Resultado: ocho decretos entre 1996 y 2001, con los Decretos 170/96 (23 artículos) y 334/96 (24) a la cabeza. **Qué decir:** «La reglamentación de una ley se reparte en varios decretos; el grafo los junta.»

### 3.6 Los casos dudosos del random forest

```cypher
MATCH (m:Norma)-[:CONTIENE]->(:Articulo)-[r]->(d)
WHERE r.fuente = 'random_forest' AND r.confianza <> ''
WITH m, d.id_norma AS destino, max(toFloat(r.confianza)) AS prob,
     max(CASE WHEN type(r) <> 'CITA' THEN 1 ELSE 0 END) AS acepta
MATCH (dn:Norma {id_norma: destino})
RETURN m.nombre AS origen, dn.nombre AS destino, prob, CASE acepta WHEN 1 THEN 'sí' ELSE 'no' END AS acepta
ORDER BY abs(prob - 0.45) LIMIT 8
```

Resultado: pares con probabilidad 0,45, justo en el umbral (por ejemplo, Decreto 847 → Ley 24.557 aceptado; Ley 24.901 → Ley 24.241 rechazado). **Qué decir:** «Los clasificadores también están en el grafo, y cada arista guarda la probabilidad del modelo. Así se puede ver dónde dudó. Se puede llevar a la zona gris del híbrido, o a una revisión humana.» (Como la probabilidad se guarda con dos decimales, los que quedan exactamente en 0,45 a veces se aceptan y a veces no: el umbral se aplica sobre el valor sin redondear.)

### 3.7 Búsqueda por texto completo

```cypher
CALL db.index.fulltext.queryNodes('articulo_texto', 'indemnización despido') YIELD node, score
MATCH (n:Norma)-[:CONTIENE]->(node)
RETURN n.nombre AS norma, node.numero AS articulo, round(score, 2) AS puntaje, left(node.texto, 120) AS texto
ORDER BY puntaje DESC LIMIT 8
```

Resultado: Ley 26.844 art. 41 (indemnización especial por maternidad), Ley 26.727 art. 22, Ley 25.013 art. 9, el art. 245 bis que incorporan el DNU 70/2023 y la Ley 27.742, la Ley 27.802 art. 95… **Qué decir:** «Además de la estructura, el grafo tiene el texto de cada artículo con un índice de texto completo: es la base para el text-to-Cypher o una búsqueda semántica, que quedan para el final.»

### 3.8 El digesto de la UNNOBA en el mismo grafo

```cypher
MATCH (m:Norma)-[:CONTIENE]->(:Articulo)-[r]->(d)
WHERE r.fuente = 'unnoba_hibrido' AND type(r) <> 'CITA'
MATCH (n:Norma {id_norma: d.id_norma}) WHERE n <> m
RETURN n.nombre AS norma, left(n.titulo, 60) AS titulo, count(DISTINCT m) AS documentos_que_la_cambian
ORDER BY documentos_que_la_cambian DESC LIMIT 6
```

Resultado: la Ley 25.871 (7 documentos), la Resolución MIN 1523/1990 y la Resolución HCS 531/2012 (5 cada una), la Resolución REC 1122/2008 (4)… **Qué decir:** «El mismo modelo de grafo y el mismo código sirvieron para el digesto de la universidad: solo cambió el adaptador. Se ven las resoluciones del Consejo Superior que más cambiaron.»

---

## 4. Cómo explicar lo que muestra el grafo (resultados)

1. **El grafo es trazable.** Cada arista tiene artículo de origen, destino, tipo, verbo, método, offsets y fragmento: lo que pide la consigna. La demo 2.7 lo muestra.
2. **El grafo es fiel a lo que se cargó.** La ida y vuelta es idéntica en las siete fuentes, y el F1 leído desde Neo4j es igual al de los archivos (reglas v2: 0,828).
3. **El grafo responde preguntas que una tabla de pares no responde:** qué artículo cambió (2.2), la historia de un artículo (2.3), cadenas de reformas (2.4, 3.2), análisis temporal (3.1).
4. **El grafo alcanza para reconstruir el texto vigente.** Con estas mismas relaciones se armó la LCT consolidada: el 95,9 % de los artículos coincide con InfoLEG. Los errores vienen de lo que el grafo no tiene (la Ley 24.522 no quedó vinculada), no de la consolidación.
5. **El grafo permite comparar métodos.** Con siete fuentes sobre los mismos nodos, se ve dónde coinciden (202 vínculos con los 7) y dónde difieren (2.6, 3.3). Es un instrumento de análisis, no solo un resultado.
6. **Límites que conviene decir:** el grafo tiene lo que los parsers extrajeron, con sus errores (F1 ~0,83 contra InfoLEG); trabaja en mundo cerrado (solo vincula normas del corpus); y no tiene vigencias, suspensiones judiciales ni vetos.

---

## 5. Preguntas en vivo que pueden pedirte (y cómo resolverlas rápido)

| Si te piden… | Cambiá en la consulta… |
|---|---|
| Otra ley en vez de la LCT | `id_norma: 25552` por el id de la ley. Para buscar el id: `MATCH (n:Norma) WHERE n.nombre = 'Ley 24013' RETURN n.id_norma` |
| Otro artículo | `numero: '245'` por el número, como texto (por ejemplo `'92 bis'`) |
| Otro parser | `r.fuente = 'llm'` por `'reglas_v2'`, `'hibrido'`, `'random_forest'`, etc. |
| Solo un tipo | `type(r) = 'DEROGA'` o `[r:DEROGA]` |
| Lo que hizo una norma (y no lo que le hicieron) | Empezá desde ella: `MATCH (:Norma {nombre: 'Ley 27802'})-[:CONTIENE]->(a)-[r]->(d) WHERE r.fuente = 'llm' AND type(r) <> 'CITA' RETURN type(r), d.id_norma, count(*)` |
| Ver el texto completo de un artículo | `MATCH (a:Articulo {id_norma: 25552, numero: '245'}) RETURN a.texto` |
| Ver todo lo que sale de un artículo, por parser | `MATCH (o:Articulo {id: '395521#71'})-[r]->(d) RETURN r.fuente, type(r), d.id, r.fragmento` |

**Nombres:** las normas se llaman `'Ley 27802'` o `'Decreto 70'`, sin puntos ni año. Si hay varios decretos con el mismo número, filtrá además por `anio`. Las del digesto tienen `id_norma` de 9.000.000 en adelante.

**ids útiles:** LCT 25552 · t.o. de la LCT (Decreto 390/76) 229909 · Ley 24.013 412 · Ley 24.557 27971 · Ley 23.551 20993 · Ley 27.802 423680 · Ley 27.742 401266 · Ley 14.250 46379.
