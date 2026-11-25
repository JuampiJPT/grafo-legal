# Resultados de las consultas de la demo (B76)

Corridas sobre `bolt://localhost:7688` el 2026-11-25 22:40 UTC con `scripts/35_demo_consultas.py`.

## panorama_nodos: ¿Qué hay en la base?

```cypher
MATCH (n) WHERE n:Norma OR n:Articulo RETURN labels(n)[0] AS etiqueta, count(*) AS cantidad
```

| etiqueta | cantidad |
|---|---|
| Articulo | 8545 |
| Norma | 444 |

## panorama_fuentes: ¿Cuántas aristas aportó cada parser?

```cypher
MATCH (:Articulo)-[r]->() WHERE type(r) <> 'CONTIENE'
RETURN r.fuente AS fuente, count(*) AS aristas,
       sum(CASE WHEN type(r) <> 'CITA' THEN 1 ELSE 0 END) AS no_cita
ORDER BY fuente
```

| fuente | aristas | no_cita |
|---|---|---|
| hibrido | 3147 | 1356 |
| hibrido_tfidf | 3273 | 1427 |
| llm | 3247 | 1022 |
| random_forest | 3283 | 1327 |
| reglas_v2 | 3277 | 945 |
| reglas_v3 | 3149 | 848 |
| tfidf | 3280 | 1384 |
| unnoba_hibrido | 150 | 62 |
| unnoba_llm | 156 | 23 |
| unnoba_reglas_v3 | 150 | 13 |

## ley27802_resumen: ¿Qué le hizo la Ley 27.802 a la LCT? (fuente llm)

```cypher
MATCH (:Norma {nombre: 'Ley 27802'})-[:CONTIENE]->(a)-[r]->(d:Articulo {id_norma: 25552})
WHERE r.fuente = 'llm' AND type(r) <> 'CITA'
RETURN type(r) AS que_hizo, count(DISTINCT d) AS articulos_de_la_lct
ORDER BY articulos_de_la_lct DESC
```

| que_hizo | articulos_de_la_lct |
|---|---|
| SUSTITUYE | 52 |
| DEROGA | 9 |
| INCORPORA | 3 |

## ley27802_detalle: ¿Qué artículos de la LCT sustituyó la Ley 27.802, y con qué texto?

```cypher
MATCH (:Norma {nombre: 'Ley 27802'})-[:CONTIENE]->(a)-[r:SUSTITUYE]->(d:Articulo {id_norma: 25552})
WHERE r.fuente = 'llm'
RETURN a.numero AS art_27802, d.numero AS art_lct, left(r.fragmento, 160) AS evidencia
ORDER BY toInteger(split(d.numero, ' ')[0]) LIMIT 12
```

| art_27802 | art_lct | evidencia |
|---|---|---|
| 1 | 2 | Artículo 1°- Sustitúyese el artículo 2° de la Ley de Contrato de Trabajo N° 20.744 (t.o. 1976) y sus modificaciones, por el siguiente: |
| 2 | 4 | Artículo 2°- Sustitúyese el artículo 4° de la Ley de Contrato de Trabajo N° 20.744 (t.o. 1976) y sus modificaciones, por el siguiente: |
| 3 | 9 | Artículo 3°- Sustitúyese el artículo 9° de la Ley de Contrato de Trabajo N° 20.744 (t.o. 1976) y sus modificaciones, por el siguiente: |
| 4 | 11 | Artículo 4°- Sustitúyese el artículo 11 de la Ley de Contrato de Trabajo N° 20.744 (t.o. 1976) y sus modificaciones, por el siguiente: |
| 6 | 12 | Artículo 6°- Sustitúyese el artículo 12 de la Ley de Contrato de Trabajo N° 20.744 (t.o. 1976) y sus modificaciones, por el siguiente: |
| 7 | 15 | Artículo 7°- Sustitúyese el artículo 15 de la Ley de Contrato de Trabajo N° 20.744 (t.o. 1976) y sus modificaciones, por el siguiente: |
| 8 | 16 | Artículo 8°- Sustitúyese el artículo 16 de la Ley de Contrato de Trabajo N° 20.744 (t.o. 1976) y sus modificaciones, por el siguiente: |
| 9 | 18 | Artículo 9°- Sustitúyese el artículo 18 de la Ley de Contrato de Trabajo N° 20.744 (t.o. 1976) y sus modificaciones, por el siguiente: |
| 10 | 20 | Artículo 10.- Sustitúyese el artículo 20 de la Ley de Contrato de Trabajo N° 20.744 (t.o. 1976) y sus modificaciones, por el siguiente: |
| 11 | 21 | Artículo 11.- Sustitúyese el artículo 21 de la Ley de Contrato de Trabajo N° 20.744 (t.o. 1976) y sus modificaciones, por el siguiente: |
| 12 | 22 | Artículo 12.- Sustitúyese el artículo 22 de la Ley de Contrato de Trabajo N° 20.744 (t.o. 1976) y sus modificaciones, por el siguiente: |
| 13 | 23 | Artículo 13.- Sustitúyese el artículo 23 de la Ley de Contrato de Trabajo N° 20.744 (t.o. 1976) y sus modificaciones, por el siguiente: |

## historia_245: Historia del artículo 245 de la LCT (indemnización por despido)

```cypher
MATCH (n:Norma)-[:CONTIENE]->(o)-[r]->(:Articulo {id_norma: 25552, numero: '245'})
WHERE type(r) <> 'CITA'
RETURN n.nombre AS norma, n.fecha AS fecha, type(r) AS que_hizo, collect(DISTINCT r.fuente) AS fuentes
ORDER BY fecha
```

| norma | fecha | que_hizo | fuentes |
|---|---|---|---|
| Ley 23697 | 1989-09-25 | SUSTITUYE | ['hibrido_tfidf', 'tfidf', 'random_forest', 'hibrido', 'reglas_v2', 'reglas_v3', 'llm'] |
| Ley 24013 | 1991-12-17 | SUSTITUYE | ['reglas_v2', 'hibrido_tfidf', 'tfidf', 'random_forest', 'hibrido', 'reglas_v3', 'llm'] |
| Ley 25323 | 2000-10-11 | MODIFICA | ['reglas_v2', 'hibrido_tfidf', 'tfidf', 'random_forest', 'hibrido', 'reglas_v3'] |
| Ley 25877 | 2004-03-19 | SUSTITUYE | ['hibrido_tfidf', 'tfidf', 'random_forest', 'hibrido', 'reglas_v2', 'reglas_v3', 'llm'] |
| Decreto 70 | 2023-12-21 | SUSTITUYE | ['hibrido_tfidf', 'tfidf', 'random_forest', 'hibrido', 'reglas_v2', 'reglas_v3', 'llm'] |
| Ley 27742 | 2024-07-08 | SUSTITUYE | ['hibrido_tfidf', 'tfidf', 'random_forest', 'hibrido', 'reglas_v2', 'reglas_v3'] |
| Ley 27802 | 2026-03-06 | SUSTITUYE | ['hibrido_tfidf', 'tfidf', 'random_forest', 'hibrido', 'reglas_v2', 'reglas_v3', 'llm'] |

## lct_por_decada: ¿En qué décadas se reformó más la LCT? (fuente llm)

```cypher
MATCH (n:Norma)-[:CONTIENE]->(:Articulo)-[r]->(d)
WHERE r.fuente = 'llm' AND type(r) IN ['SUSTITUYE','INCORPORA','DEROGA','MODIFICA'] AND d.id_norma = 25552
RETURN (n.anio / 10) * 10 AS decada, count(DISTINCT n) AS normas, count(*) AS cambios
ORDER BY decada
```

| decada | normas | cambios |
|---|---|---|
| 1970 | 4 | 5 |
| 1980 | 5 | 7 |
| 1990 | 10 | 26 |
| 2000 | 9 | 29 |
| 2010 | 15 | 21 |
| 2020 | 8 | 106 |

## deroga_24013: ¿Qué normas derogaron algo de la Ley de Empleo 24.013? (fuente llm)

```cypher
MATCH (n:Norma)-[:CONTIENE]->(:Articulo)-[r:DEROGA]->(d)
WHERE r.fuente = 'llm' AND d.id_norma = 412
RETURN DISTINCT n.nombre AS norma, n.fecha AS fecha, coalesce(d.numero, 'toda la ley') AS que_derogo
ORDER BY fecha
```

| norma | fecha | que_derogo |
|---|---|---|
| Ley 25013 | 1998-09-24 | 18 |
| Ley 25013 | 1998-09-24 | 31 |
| Ley 25013 | 1998-09-24 | 28 a 40 |
| Ley 25013 | 1998-09-24 | 43 a 65 |
| Ley 26598 | 2010-07-06 | 141 |
| Decreto 70 | 2023-12-21 | 8 a 17 |
| Decreto 70 | 2023-12-21 | 120 |
| Ley 27742 | 2024-07-08 | 8 a 17 |
| Ley 27742 | 2024-07-08 | 120 |

## reglamenta_lrt: ¿Qué decretos reglamentan la Ley de Riesgos del Trabajo 24.557? (fuente llm)

```cypher
MATCH (n:Norma {tipo: 'Decreto'})-[:CONTIENE]->(:Articulo)-[r:REGLAMENTA]->(d)
WHERE r.fuente = 'llm' AND d.id_norma = 27971
RETURN n.nombre AS decreto, n.fecha AS fecha, count(*) AS articulos
ORDER BY fecha
```

| decreto | fecha | articulos |
|---|---|---|
| Decreto 170 | 1996-02-26 | 23 |
| Decreto 334 | 1996-04-08 | 24 |
| Decreto 333 | 1996-04-09 | 2 |
| Decreto 719 | 1996-07-29 | 1 |
| Decreto 491 | 1997-06-04 | 3 |
| Decreto 559 | 1997-06-24 | 2 |
| Decreto 962 | 1997-09-24 | 1 |
| Decreto 410 | 2001-04-17 | 8 |

## ranking: ¿Cuáles son las normas más modificadas? (fuente hibrido)

```cypher
MATCH (m:Norma)-[:CONTIENE]->(:Articulo)-[r]->(d)
WHERE r.fuente = 'hibrido' AND type(r) IN ['SUSTITUYE','INCORPORA','DEROGA','MODIFICA','REGLAMENTA'] AND m.id_norma < 9000000
MATCH (n:Norma {id_norma: d.id_norma}) WHERE n <> m
RETURN n.nombre AS norma, left(n.titulo, 60) AS titulo, count(DISTINCT m) AS normas_que_la_modifican
ORDER BY normas_que_la_modifican DESC LIMIT 10
```

| norma | titulo | normas_que_la_modifican |
|---|---|---|
| Ley 20744 | REGIMEN | 105 |
| Ley 24013 | PROTECCION DEL TRABAJO | 81 |
| Ley 24241 | CREACION | 62 |
| Ley 24557 | REGIMEN LEGAL | 61 |
| Ley 23551 | REGIMEN | 20 |
| Ley 14250 | TRABAJO | 20 |
| Ley 23660 | NUEVO REGIMEN - APROBACION | 19 |
| Ley 26727 | REGIMEN DE TRABAJO AGRARIO - APROBACION | 13 |
| Ley 20628 | REGIMEN LEGAL | 13 |
| Ley 24467 | MARCO REGULATORIO | 12 |

## dos_saltos: Reforma sobre reforma: normas que modifican a una modificatoria de la LCT (fuente hibrido)

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

| norma | fecha | que_hizo | a_la_modificatoria |
|---|---|---|---|
| Decreto 1228 | 2026-10-20 | MODIFICA | Ley 27802 |
| Decreto 1203 | 2026-10-19 | MODIFICA | Decreto 214 |
| Decreto 612 | 2026-07-20 | MODIFICA | Ley 27802 |
| Decreto 408 | 2026-06-01 | MODIFICA | Ley 27802 |
| Decreto 409 | 2026-06-01 | MODIFICA | Ley 24013 |
| Decreto 407 | 2026-06-01 | MODIFICA | Ley 27802 |
| Decreto 409 | 2026-06-01 | MODIFICA | Ley 24557 |
| Decreto 407 | 2026-06-01 | SUSTITUYE | Ley 26727 |
| Decreto 407 | 2026-06-01 | MODIFICA | Ley 26727 |
| Decreto 407 | 2026-06-01 | DEROGA | Ley 26727 |
| Decreto 242 | 2026-04-13 | INCORPORA | Ley 27802 |
| Decreto 242 | 2026-04-13 | MODIFICA | Ley 27802 |

## consenso: ¿Cuántos de los 7 parsers de InfoLEG encuentran cada vínculo?

```cypher
MATCH (m:Norma)-[:CONTIENE]->(:Articulo)-[r]->(d)
WHERE type(r) <> 'CITA' AND m.id_norma < 9000000 AND NOT r.fuente STARTS WITH 'unnoba'
WITH m, d.id_norma AS destino, collect(DISTINCT r.fuente) AS fuentes
WHERE destino <> m.id_norma
RETURN size(fuentes) AS cuantos_parsers, count(*) AS pares
ORDER BY cuantos_parsers DESC
```

| cuantos_parsers | pares |
|---|---|
| 7 | 202 |
| 6 | 67 |
| 5 | 68 |
| 4 | 322 |
| 3 | 126 |
| 2 | 87 |
| 1 | 70 |

## dos_lecturas_conteo: ¿En cuántos artículos las reglas ven una cita y el LLM una acción?

```cypher
MATCH (n:Norma)-[:CONTIENE]->(o:Articulo)-[r1]->(d1), (o)-[r2]->(d2)
WHERE r1.fuente = 'reglas_v2' AND r2.fuente = 'llm' AND type(r1) = 'CITA' AND type(r2) <> 'CITA'
  AND d1.id_norma = d2.id_norma
RETURN type(r2) AS segun_el_llm, count(DISTINCT o) AS articulos ORDER BY articulos DESC
```

| segun_el_llm | articulos |
|---|---|
| REGLAMENTA | 124 |
| MODIFICA | 61 |
| SUSTITUYE | 34 |
| DEROGA | 25 |
| INCORPORA | 10 |

## dos_lecturas: Ejemplos: mismo artículo, dos lecturas

```cypher
MATCH (n:Norma)-[:CONTIENE]->(o:Articulo)-[r1]->(d1), (o)-[r2]->(d2)
WHERE r1.fuente = 'reglas_v2' AND r2.fuente = 'llm' AND type(r1) = 'CITA' AND type(r2) = 'SUSTITUYE'
  AND d1.id_norma = d2.id_norma
MATCH (dn:Norma {id_norma: d2.id_norma})
RETURN n.nombre AS norma, o.numero AS articulo, dn.nombre AS destino, type(r1) AS reglas, type(r2) AS llm,
       r2.verbo AS verbo_llm, left(r2.fragmento, 170) AS evidencia
LIMIT 6
```

| norma | articulo | destino | reglas | llm | verbo_llm | evidencia |
|---|---|---|---|---|---|---|
| Ley 21824 | 0 | Ley 20744 | CITA | SUSTITUYE | Sustitúyese | CONTRATO DE TRABAJO LEY N° 21.824 Sustitúyese el artículo 177 del régimen de contrato de trabajo, según texto ordenado por el Decreto N° 390/76, relativo a la licencia po |
| Ley 22276 | 0 | Ley 20744 | CITA | SUSTITUYE | Sustitúyese | CONTRATOS DE TRABAJO LEY N° 22.276 Sustitúyese un artículo del Régimen de Contrato de Trabajo. Ley N° 20.744 (t.o. 1976) Buenos Aires, 25 de agosto de 1980 En uso de las  |
| Ley 24241 | 155 | Ley 20091 | CITA | SUSTITUYE | Sustitúyese | ejercicio económico anterior, que no podrá ser inferior al 0,5 por ciento del capital mínimo requerido. Sustitúyese el segundo y tercer párrafo del art. 86 de la ley 20.0 |
| Ley 24241 | 155 | Ley 20091 | CITA | SUSTITUYE | Sustitúyese | saneamiento, la autoridad de control establecerá sobre las inversiones, las medidas previstas en el art. 86 de esta ley. Sustitúyese el inc. c) del art. 58 de la ley 20.0 |
| Ley 24241 | 155 | Ley 20091 | CITA | SUSTITUYE | Sustituyese | mentarias, las sanciones previstas en la ley 20.091 con los procedimientos que ella establece. Sustituyese el primer párrafo de la segunda parte del art. 31 (indisponibil |
| Ley 24347 | 1 | Ley 24241 | CITA | SUSTITUYE | Modifícanse | ARTICULO 1º — Modifícanse los artículos 3º, inciso 5; 21, 24, 34, 40 y 97 de la ley 24.241, los que quedarán redactados de la siguiente forma: Artículo 3º, Inciso 5: Las  |

## evidencia_dnu70: La evidencia completa de una arista: DNU 70/2023 sobre la LCT (fuente llm)

```cypher
MATCH (n:Norma {tipo: 'Decreto', numero: '70', anio: 2023})-[:CONTIENE]->(o)-[r]->(d:Articulo {id_norma: 25552})
WHERE r.fuente = 'llm'
RETURN o.numero AS art_dnu, type(r) AS que_hizo, d.numero AS art_lct, r.verbo AS verbo, r.metodo AS metodo,
       r.inicio AS desde, r.fin AS hasta, left(r.fragmento, 150) AS evidencia
ORDER BY toInteger(split(d.numero, ' ')[0]) LIMIT 8
```

| art_dnu | que_hizo | art_lct | verbo | metodo | desde | hasta | evidencia |
|---|---|---|---|---|---|---|---|
| 65 | SUSTITUYE | 2 | Sustitúyese | llm | 55935 | 55960 | ARTÍCULO 65.- Sustitúyese el artículo 2° de la Ley N° 20.744 (t.o. 1976) y sus modificatorias por el siguiente: “ARTÍCULO 2°.- Ámbito de Aplicación. L |
| 66 | SUSTITUYE | 9 | Sustitúyese | llm | 57230 | 57255 | ARTÍCULO 66.- Sustitúyese el artículo 9° de la Ley N° 20.744 (t.o. 1976) y sus modificatorias por el siguiente: “ARTÍCULO 9°.- El principio de la norm |
| 67 | SUSTITUYE | 12 | Sustitúyese | llm | 58291 | 58316 | ARTÍCULO 67.- Sustitúyese el artículo 12 de la Ley N° 20.744 (t.o. 1976) y sus modificatorias por el siguiente: “ARTÍCULO 12 - Protección de los traba |
| 68 | SUSTITUYE | 23 | Sustitúyese | llm | 59055 | 59080 | ARTÍCULO 68.- Sustitúyese el artículo 23 de la Ley N° 20.744 (t.o. 1976) y sus modificatorias por el siguiente: “ARTÍCULO 23.- Presunción de la existe |
| 69 | SUSTITUYE | 29 | Sustitúyese | llm | 59887 | 59912 | ARTÍCULO 69.- Sustitúyese el artículo 29 de la Ley N° 20.744 (t.o. 1976) y sus modificatorias por el siguiente: “ARTÍCULO 29.- Mediación. Intermediaci |
| 60 | CITA | 29 |  | llm | 53624 | 53637 | .- Incorpórase como artículo 7° bis de la Ley N° 24.013, el siguiente: “ARTÍCULO 7° bis - En virtud de lo establecido en los artículos 29 y 30 de la L |
| 60 | CITA | 30 |  | llm | 53624 | 53637 | .- Incorpórase como artículo 7° bis de la Ley N° 24.013, el siguiente: “ARTÍCULO 7° bis - En virtud de lo establecido en los artículos 29 y 30 de la L |
| 74 | CITA | 30 |  | llm | 65047 | 65078 | concepto de remuneraciones, indemnizaciones u otros derechos apreciables en dinero provenientes de la relación laboral. Conforme lo dispuesto en el ar |

## clasificador_dudoso: Los pares en que el random forest dudó (probabilidad cerca del umbral 0,45)

```cypher
MATCH (m:Norma)-[:CONTIENE]->(:Articulo)-[r]->(d)
WHERE r.fuente = 'random_forest' AND r.confianza <> ''
WITH m, d.id_norma AS destino, max(toFloat(r.confianza)) AS prob,
     max(CASE WHEN type(r) <> 'CITA' THEN 1 ELSE 0 END) AS acepta
MATCH (dn:Norma {id_norma: destino})
RETURN m.nombre AS origen, dn.nombre AS destino, prob, CASE acepta WHEN 1 THEN 'sí' ELSE 'no' END AS acepta
ORDER BY abs(prob - 0.45) LIMIT 8
```

| origen | destino | prob | acepta |
|---|---|---|---|
| Ley 24901 | Ley 24241 | 0.45 | no |
| Decreto 551 | Ley 27541 | 0.45 | sí |
| Decreto 737 | Ley 12713 | 0.45 | no |
| Decreto 724 | Ley 11672 | 0.45 | sí |
| Decreto 847 | Ley 24557 | 0.45 | sí |
| Decreto 1048 | Decreto 84 | 0.45 | sí |
| Ley 23769 | Ley 20744 | 0.45 | sí |
| Decreto 70 | Ley 26844 | 0.45 | no |

## texto_completo: Búsqueda por texto: artículos que hablan de indemnización por despido

```cypher
CALL db.index.fulltext.queryNodes('articulo_texto', 'indemnización despido') YIELD node, score
MATCH (n:Norma)-[:CONTIENE]->(node)
RETURN n.nombre AS norma, node.numero AS articulo, round(score, 2) AS puntaje, left(node.texto, 120) AS texto
ORDER BY puntaje DESC LIMIT 8
```

| norma | articulo | puntaje | texto |
|---|---|---|---|
| Ley 26844 | 41 | 6.09 | ARTICULO 41. — Indemnización especial. Maternidad. Matrimonio. Cuando el despido obedeciera a razones de maternidad o em |
| Ley 26727 | 22 | 5.99 | ARTICULO 22. — Trabajador permanente. Indemnización mínima por antigüedad o despido . El trabajador permanente en ningún |
| Ley 25013 | 9 | 5.99 | ARTICULO 9º- (Falta de pago en término de la indemnización por despido incausado). En caso de falta de pago en término y |
| Ley 27742 | 245 bis | 5.9 | Artículo 245 bis: Agravamiento indemnizatorio por despido motivado por un acto discriminatorio. Será considerado despido |
| Decreto 70 | 82 | 5.9 | ARTÍCULO 82.- Incorpórase como artículo 245 bis a la Ley N° 20.744 (t.o. 1976) y sus modificatorias, el siguiente:  “ART |
| Ley 26844 | 48 | 5.85 | ARTICULO 48. — Indemnización por antigüedad o despido. En los casos de despido dispuesto por el empleador sin causa, hab |
| Ley 27802 | 95 | 5.64 | Artículo 95: Despido antes del vencimiento del plazo. Indemnización. El despido injustificado dispuesto con antelación a |
| Ley 25877 | 4 | 5.55 | ARTICULO 4º — Sustitúyese el artículo 233 de la Ley de Contrato de Trabajo, Nº 20.744 (t.o. 1976) y sus modificatorias,  |

## unnoba_fuentes: Digesto UNNOBA: aristas por parser

```cypher
MATCH (:Articulo)-[r]->() WHERE r.fuente STARTS WITH 'unnoba'
RETURN r.fuente AS fuente, type(r) AS tipo, count(*) AS aristas ORDER BY fuente, aristas DESC
```

| fuente | tipo | aristas |
|---|---|---|
| unnoba_hibrido | CITA | 88 |
| unnoba_hibrido | MODIFICA | 56 |
| unnoba_hibrido | REGLAMENTA | 5 |
| unnoba_hibrido | INCORPORA | 1 |
| unnoba_llm | CITA | 133 |
| unnoba_llm | MODIFICA | 12 |
| unnoba_llm | SUSTITUYE | 6 |
| unnoba_llm | INCORPORA | 3 |
| unnoba_llm | REGLAMENTA | 1 |
| unnoba_llm | DEROGA | 1 |
| unnoba_reglas_v3 | CITA | 137 |
| unnoba_reglas_v3 | MODIFICA | 11 |
| unnoba_reglas_v3 | REGLAMENTA | 1 |
| unnoba_reglas_v3 | INCORPORA | 1 |

## unnoba_mas_modificadas: Digesto UNNOBA: las normas más modificadas (fuente unnoba_hibrido)

```cypher
MATCH (m:Norma)-[:CONTIENE]->(:Articulo)-[r]->(d)
WHERE r.fuente = 'unnoba_hibrido' AND type(r) <> 'CITA'
MATCH (n:Norma {id_norma: d.id_norma}) WHERE n <> m
RETURN n.nombre AS norma, left(n.titulo, 60) AS titulo, count(DISTINCT m) AS documentos_que_la_cambian
ORDER BY documentos_que_la_cambian DESC LIMIT 6
```

| norma | titulo | documentos_que_la_cambian |
|---|---|---|
| Ley 25871 | Ley 25871 | 7 |
| Resolución MIN 1523/1990 | Resolución MIN 1523/1990 | 5 |
| Resolución HCS 531/2012 | Resolución HCS 531/2012 | 5 |
| Resolución REC 1122/2008 | Resolución REC 1122/2008 | 4 |
| Resolución HCS 97/2008 | Resolución HCS Nº 097/08 | 3 |
| Ordenanza HCS 14/2009 | Ordenanza HCS 14/2009 | 3 |

## visual_27802: Para la vista de grafo: Ley 27.802 → artículos de la LCT (filas que dibuja)

```cypher
MATCH p = (:Norma {nombre: 'Ley 27802'})-[:CONTIENE]->(:Articulo)-[r:SUSTITUYE {fuente: 'llm'}]->(:Articulo)<-[:CONTIENE]-(:Norma {id_norma: 25552})
RETURN count(p) AS caminos
```

| caminos |
|---|
| 52 |

## cadena_lct: la cadena de modificaciones más larga que llega a la LCT (fuente hibrido)

14 saltos:

0. Decreto 551 (2022-08-30, id 370565)
1. Decreto 711 (2021-10-19, id 355459)
2. Decreto 493 (2021-08-06, id 352666)
3. Decreto 191 (2021-03-24, id 348194)
4. Ley 27541 (2019-12-23, id 333564)
5. Ley 27260 (2016-07-22, id 263691)
6. Ley 26940 (2014-06-02, id 230592)
7. Ley 26476 (2008-12-24, id 148719)
8. Ley 25877 (2004-03-19, id 93595)
9. Ley 25250 (2000-06-02, id 63208)
10. Ley 25013 (1998-09-24, id 53159)
11. Ley 24465 (1995-03-28, id 15931)
12. Ley 24013 (1991-12-17, id 412)
13. Ley 23697 (1989-09-25, id 15)
14. Ley 20744 (1974-09-27, id 25552)

Para dibujarla en el Browser (89 filas):

```cypher
WITH [370565, 355459, 352666, 348194, 333564, 263691, 230592, 148719, 93595, 63208, 53159, 15931, 412, 15, 25552] AS ids
MATCH p = (m:Norma)-[:CONTIENE]->(:Articulo)-[r]->(d)
WHERE m.id_norma IN ids AND d.id_norma IN ids AND d.id_norma <> m.id_norma
  AND r.fuente = 'hibrido' AND type(r) IN ['SUSTITUYE','INCORPORA','DEROGA','MODIFICA']
OPTIONAL MATCH (n:Norma)-[:CONTIENE]->(d)
RETURN p, n
```
