# Texto consolidado de la LCT armado desde el grafo

**Qué es.** El texto vigente de la Ley de Contrato de Trabajo (Ley 20.744, t.o. 1976), armado solo con lo que tiene el grafo:
- las relaciones de Neo4j;
- el texto de los artículos que las sostienen.

Las modificaciones se aplican en orden cronológico y cada artículo guarda su historia. Después se comparó contra el texto actualizado oficial de InfoLEG. Bitácora B60 y B61.

**Archivos.**
- Scripts:
  - `scripts/23_consultar_consolidado.py`: consultas Cypher.
  - `scripts/24_consolidar.py`: consolidación.
  - `scripts/firma_texto.py`: comparación.
- Resultado: `results/consolidado/lct_consolidada.md`, el texto con trazabilidad, y `lct_consolidada.json`.
- Detalle: `operaciones.csv` (cada operación aplicada), `no_aplicadas.csv` (lo que quedó afuera y por qué) y `evaluacion/` (`por_articulo.csv`, `eventos.csv`, `metricas.json`).
- Evaluación: `scripts/25_evaluar_consolidado.py`.

## 1. Qué ley: la de más profundidad en el grafo

`23_consultar_consolidado.py --ranking` calcula tres medidas para cada norma, sobre las aristas que no son CITA:
- **modificatorias:** cuántas normas distintas actúan sobre ella;
- **artículos afectados:** cuántos de sus artículos reciben alguna;
- **profundidad:** el largo de la cadena más larga que llega a ella. Por ejemplo, una ley la modifica, un decreto modifica esa ley, y así.

```cypher
MATCH (m:Norma)-[:CONTIENE]->(:Articulo)-[r]->(d)
WHERE r.fuente = $fuente AND type(r) <> 'CITA' AND m.id_norma < 9000000
OPTIONAL MATCH (t:Norma)-[:CONTIENE]->(d)
WITH m, r, d, coalesce(t, d) AS n
WHERE n:Norma AND n <> m
RETURN m.id_norma AS origen, n.id_norma AS destino, n.nombre AS nombre, type(r) AS tipo,
       CASE WHEN d:Articulo THEN d.numero ELSE '' END AS articulo
```

La LCT queda primera con las cuatro fuentes. Con la fuente del híbrido tiene 105 normas modificatorias, 107 artículos afectados y una profundidad de 16. La siguen la Ley 24.013 (81 normas, profundidad 14) y la Ley 24.241 (62, 10). El ranking completo está en `results/consolidado/ranking_profundidad.csv`.

## 2. El manifiesto, sacado de Neo4j

`23_consultar_consolidado.py --manifiesto 25552 229909` trae dos cosas:
- los artículos de la ley y de su texto ordenado, con su texto;
- todas las relaciones que llegan a ellos desde artículos de otras normas, con el texto del artículo de origen y qué parsers las encontraron.

```cypher
MATCH (n:Norma) WHERE n.id_norma IN $ids
MATCH (m:Norma)-[:CONTIENE]->(o:Articulo)-[r]->(d)
WHERE type(r) <> 'CITA' AND r.fuente IN $fuentes AND (d = n OR (n)-[:CONTIENE]->(d))
RETURN m.id_norma, m.nombre, m.fecha, o.id, o.numero, o.texto, type(r), r.fuente, r.verbo,
       CASE WHEN d:Articulo THEN d.numero ELSE '' END AS articulo_destino
ORDER BY m.fecha
```

Resultado: 943 relaciones de 107 normas, sumando las cuatro fuentes (reglas v2, reglas v3, LLM e híbrido).

**La trampa del texto base.** El texto de la Ley 20.744 que hay en el corpus es el original de 1974. Desde 1976, todas las modificaciones citan los artículos con la numeración del texto ordenado del Decreto 390/76. Por ejemplo, la indemnización por despido es el art. 245 del t.o. Por eso el texto base es el anexo del Decreto 390/76, que está en el corpus (id 229909), partido en sus 277 artículos.

## 3. Cómo se consolida

1. **Eventos.** Cada artículo de otra norma, posterior al t.o., que según el grafo SUSTITUYE, INCORPORA, DEROGA o MODIFICA la LCT.
   - Son 235 artículos de 100 normas.
   - REGLAMENTA y CITA no cambian el texto y quedan afuera.
   - El texto de cada evento sale del corpus, junto con los segmentos que lo siguen: a veces el texto nuevo («por el siguiente: "Artículo 245…"») quedó partido en otro segmento.
2. **Extracción.** El LLM lee cada artículo modificatorio, con las pistas del grafo (tipo y artículo destino según cada parser). Devuelve las operaciones sobre la LCT: artículo, operación y el texto nuevo literal.
   - **Verificación:** el texto nuevo tiene que estar tal cual en la norma modificatoria. Si no está, la operación no se aplica.
   - **Resultado:** 73 de los 235 artículos no hacen ningún cambio textual a la LCT. Son los «complementa» del híbrido: decretos que aplican la ley o normas que la mencionan para otra cosa. Los otros 162 dan 172 operaciones (120 SUSTITUYE, 23 MODIFICA_PARCIAL, 16 INCORPORA y 13 DEROGA), de las que 168 se verifican.
3. **Aplicación**, en orden cronológico por artículo:
   - **Sin LLM:** SUSTITUYE e INCORPORA ponen el texto nuevo verificado, y DEROGA marca el artículo como derogado.
   - **Con LLM:** en MODIFICA_PARCIAL (un inciso, un párrafo, una frase), el LLM reescribe el artículo. Se acepta solo si al menos el 90 % de los 4-gramas del resultado está en el texto anterior o en la norma modificatoria.
   - **No se aplicaron 8 operaciones**, cada una con su motivo:
     - 4 SUSTITUYE cuyo texto no apareció literal;
     - 3 cambios parciales que la norma no transcribe;
     - 1 cambio parcial idéntico al vigente.
4. **Trazabilidad.** Cada artículo lleva su historia: qué norma y qué artículo lo cambió, la fecha, la operación y qué parsers vieron la relación.

**Resultado:** 293 artículos.
- 89 tienen al menos un cambio después del t.o.;
- 16 son incorporados (29 bis, 92 bis, 92 ter, 103 bis…);
- 13 están derogados.

**Costo:** 258 pedidos al LLM, unos USD 2,4, guardados en la cache.

## 4. Qué tan fiel es: comparación con el texto actualizado de InfoLEG

**Referencia.** El texto actualizado de la LCT en InfoLEG (`texact.htm`), guardado el 20/11/2026 en `data/textos/infoleg/html/25552_texact.html`. Ya incluye la Ley 27.802 de marzo de 2026. Se usa solo para medir, nunca como entrada.

**Cómo se comparó** (`scripts/25_evaluar_consolidado.py`):
1. Los dos textos se parten por artículo.
2. Se sacan las notas editoriales de InfoLEG, como «(Artículo sustituido por art. … B.O. …)» o «(Nota Infoleg: …)».
3. Se normaliza: Unicode, minúsculas, sin puntuación y sin el rótulo «Art. N».
4. Se compara la secuencia de palabras con difflib.

Antes de tener el archivo, la misma comparación se había hecho con firmas (hash y MinHash) calculadas en el navegador (`scripts/firma_texto.py`, `evaluacion/distintos_infoleg.csv`). Llegó a las mismas conclusiones, con umbrales más gruesos.

**Resultados** (293 artículos en cada lado, el mismo conjunto de números):

| Resultado | Artículos | % |
|---|---|---|
| Idénticos después de normalizar | 207 | 70,6 |
| Casi idénticos (similitud ≥ 0,95) | 61 | 20,8 |
| Derogados en los dos | 13 | 4,4 |
| Diferencias menores (0,80 a 0,95) | 7 | 2,4 |
| Diferencia sustantiva (< 0,80) | 2 | 0,7 |
| Derogado en InfoLEG y vigente en el consolidado | 3 | 1,0 |

**Lectura.**
- **Lo que coincide.** 281 de 293 artículos (95,9 %) son idénticos, casi idénticos o están derogados en los dos.
- **Los casi idénticos** que nadie modificó son variantes de redacción del t.o. entre la publicación del Decreto 390/76 y el texto actualizado: «prohíbe»/«prohibe», «motivo»/«motivos», «sueldo o salario»/«sueldo».
- **Los artículos que cambian:** son 103 en alguno de los dos lados, y 94 coinciden (91 %). Eso incluye las cadenas largas y las sustituciones y derogaciones de la Ley 27.802.
- **Eventos.** De los 107 cambios que registran las notas de InfoLEG (artículo y norma), el consolidado aplicó 99 (92,5 %). La precisión de eventos (0,62) no se puede leer como error: las notas de InfoLEG solo guardan la última versión de cada parte, no la historia completa.

**De los 12 artículos que no coinciden, 6 son errores reales:**

| Art. | Qué pasó | Causa |
|---|---|---|
| 264, 265, 266 | InfoLEG los da por derogados por la Ley 24.522 (Concursos, 1995, art. 293); el consolidado los deja vigentes. El 266 tiene aplicada la sustitución anterior, de la Ley 23.472 | La relación no está en el grafo: ningún parser vinculó la Ley 24.522 con la LCT. Es un error de recall del parser, no de la consolidación |
| 251 | Sustituido por la Ley 24.522, art. 294; el consolidado tiene el texto de 1976 | La misma causa |
| 2 | Falta la última sustitución, de la Ley 27.802, art. 1 | El texto que extrajo el LLM no pasó la verificación literal y la operación se descartó. La verificación cuida la precisión a costa del recall |
| 147 | El consolidado tiene un tercer párrafo de más | El Decreto 27/2018 lo sustituyó y la Ley 27.444 derogó ese artículo del decreto. InfoLEG anota que «no se revive el texto». El método no modela la derogación de una norma modificatoria |

**Los otros 6 son diferencias de forma, no de contenido:**
- **98, 233 y 231:** InfoLEG conserva el epígrafe del artículo («Comportamiento de las partes…», «Comienzo del plazo…», «Plazos») y la norma modificatoria no lo transcribe. En el 231, el cambio parcial de la Ley 27.802 al inciso b) quedó bien aplicado.
- **17, 38 y 107:** ni InfoLEG ni el consolidado los modificaron. Son variantes de redacción del t.o. («prohíbe»/«prohibe», «motivo»/«motivos»).

## 5. Qué tan verídico es, y sus límites

- **Fuerte en las sustituciones completas.** Las sustituciones de artículos enteros, que son la mayoría (120 de 172), salen literales de la norma modificatoria y coinciden con InfoLEG. Las cadenas largas también se reconstruyen bien: el art. 245 pasa por las Leyes 23.697, 24.013 y 25.877, el DNU 70/2023 y la Ley 27.802; el art. 92 bis tiene seis versiones.
- **El techo es el recall del grafo.** Lo que el grafo no tiene no se aplica: es el caso de la Ley 24.522. La consolidación no agrega errores propios donde el grafo está completo, pero tampoco puede inventar relaciones que faltan.
- **Los cambios parciales son el punto débil.** Incisos, párrafos y montos: hay 23, 3 no se pudieron aplicar y 1 quedó distinto. Son los casos donde hace falta el LLM y la verificación es más débil (cobertura de 4-gramas, no igualdad literal).
- **No sabe nada fuera del texto de las normas.**
  - **Derogaciones de normas modificatorias:** el art. 147 muestra que no se modelan.
  - **Vigencias diferidas:** el método usa la fecha de publicación, no la fecha en que la norma empieza a regir.
  - **Suspensiones judiciales y declaraciones de inconstitucionalidad:** por ejemplo, el capítulo laboral del DNU 70/2023 fue suspendido judicialmente. El consolidado aplica todo lo que el texto de la norma dice.
  - **Vetos y observaciones parciales.**
- **No sirve como texto oficial.** Sirve para mostrar que el grafo tiene suficiente información para reconstruir el texto vigente, y para medir cuánto se pierde en cada paso: recall del parser, verificación y aplicación parcial.
