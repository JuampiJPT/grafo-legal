# Conclusiones del TP y cómo se llegó a cada una

Este documento junta todas las conclusiones del TP, ordenadas por las preguntas de investigación del enunciado (PI1 a PI5). Para cada una dice:
- **qué se concluye**;
- **cómo se llegó**: el experimento, sobre qué datos y con qué control;
- **la evidencia**: los números, el archivo donde están y la entrada de la bitácora;
- **el límite**: hasta dónde vale.

Los hallazgos numerados de `docs/ESTADO.md` son la versión corta. Este documento cuenta el razonamiento detrás de cada uno. Bitácora B63.

## 0. Cómo se trabajó: las reglas que hacen creíbles los números

Las conclusiones dependen de cómo se midió. Se siguieron cinco reglas durante todo el TP:

1. **Un solo corpus congelado.** 340 normas del dominio laboral, con 775 pares del gold de InfoLEG (B33, D11). Se partió en el tiempo: dev son las modificatorias hasta 2019 (583 pares) y test, las de 2020 en adelante (192 pares) (B09). Así test se parece a usar el sistema sobre normas nuevas.
2. **El test no se usa para diseñar.** Las reglas, los prompts y los umbrales se ajustaron solo con dev, y cada versión congelada se midió en test una sola vez (B16, D7). Por eso la v3, que se hizo después, se informa como experimento y la v2 sigue siendo la referencia.
3. **El gold nunca entra a un extractor.** Solo lo leen los scripts que miden o que entrenan con dev. El grafo y el parser LLM no lo ven (README, «Reglas del protocolo»).
4. **Cada arista lleva su evidencia:** el artículo, los offsets, el fragmento, el método y las reglas que cumplió. Así cualquier par se puede revisar a mano (B41).
5. **Intervalos de confianza.** Las diferencias entre métodos se miden con bootstrap pareado (B49). «Mejor» quiere decir que el intervalo de la diferencia no toca el cero.

## 1. Antes de los parsers: qué mide el gold y cuál es el techo

### 1.1 El gold de InfoLEG mide un vínculo amplio, no solo modificaciones

- **Conclusión.** La relación que registra InfoLEG es «modifica o complementa». Incluye modificaciones, pero también reglamentaciones, textos ordenados y remisiones. Un extractor que busque solo modificaciones en sentido estricto va a perder recall contra este gold.
- **Cómo se llegó.** Se leyeron a mano los 21 pares de una muestra que tenían una mención explícita en el texto, y se clasificó qué hace cada uno.
- **Evidencia.** 7 modificaciones, 4 reglamentaciones, 1 texto ordenado y 9 remisiones (B27). Por eso se fijó evaluar el vínculo general (B02, D6).
- **Límite.** Es una muestra chica. La consulta a la cátedra sobre si se evalúa también la modificación estricta sigue abierta.

### 1.2 Hay un techo de recall que ningún parser textual puede pasar

- **Conclusión.** Una parte del gold no se puede encontrar leyendo el texto: la norma no nombra a la otra, o no tiene texto en InfoLEG.
- **Cómo se llegó.** Se buscó, para cada par del gold, si el texto de la modificatoria nombra a la destino, primero a mano y después con el detector de menciones (`05_cobertura_textual.py`). Después se explicó cada par sin mención (`18_explicar_errores.py`).
- **Evidencia.** El 81 % del gold de dev y el 96 % del de test aparecen como candidatos (B26, B34). De los 80 pares sin mención, 36 son normas que complementan a la otra sin citarla, 9 son textos ordenados («t.o. 1976» remite al Decreto 390/76), 16 son derogaciones genéricas o de modificatorias y 2 parecen errores del gold (B51).
- **Límite.** El techo vale para un extractor que lee el texto de la modificatoria. Inferir esos vínculos necesitaría otra fuente, como el texto de la norma destino o la fecha.

### 1.3 El gold tiene ruido

- **Conclusión.** Algunos falsos positivos son vínculos reales que InfoLEG no registra. El F1 contra InfoLEG subestima un poco la calidad real.
- **Cómo se llegó.** Se revisaron a mano 30 falsos positivos de dev de las reglas v2, y se tomó una muestra de la Ley 14.250, que se había dejado sin expandir.
- **Evidencia.** En 3 de los 30 falsos positivos el texto sí modifica a la norma y InfoLEG no lo registra (B36, `docs/revision_manual/revision_fp_dev_30.csv`). La muestra de la Ley 14.250 confirmó que estaba bien excluirla (B30).
- **Límite.** La revisión la hizo Claude. Falta que el equipo la valide y que un segundo anotador repita una parte, para el kappa.

## 2. PI1 · Qué efectividad alcanza cada enfoque

### 2.1 Las reglas a mano llegan a F1 0,828 en test

- **Conclusión.** Un parser de reglas transparente (mención en el VISTO o en el articulado, con verbo o desde una ley) alcanza F1 0,828 en test, con precisión 0,785 y recall 0,875.
- **Cómo se llegó.** La v1 se diseñó sobre el corpus anterior y daba 0,788 en test. Al ampliar el corpus se midió sobre los pares nuevos, que la v1 no había visto, y cayó (2.2). La v2 se diseñó sobre dev con lo aprendido y se congeló antes de mirar test (B36, D13).
- **Evidencia.** `results/reglas_v2/RESULTADOS.md`. Dev 0,733 y test 0,828.
- **Límite.** Es un dominio (laboral) y dos tipos de norma (leyes y decretos).

### 2.2 Las reglas diseñadas sobre una parte del corpus no generalizan bien al resto

- **Conclusión.** Medir sobre los mismos pares que se miraron al diseñar infla el resultado.
- **Cómo se llegó.** El corpus nuevo contiene al anterior, y `pares_evaluados_en_v1.csv` marca qué pares ya se habían usado. Se midió la v1 solo sobre los pares nuevos.
- **Evidencia.** La v1 pierde 14 puntos de F1 en dev y 22 en test sobre los pares nuevos (B35). La v2 también se informa sobre los pares que nunca se miraron: 0,671 en test.
- **Límite.** Los pares nuevos de test son 65, así que la cifra tiene un intervalo ancho.

### 2.3 El VISTO es una señal fuerte, y el CONSIDERANDO no

- **Conclusión.** Dónde está la mención importa más que casi cualquier otro atributo. Lo que se cita en el VISTO casi siempre está vinculado; lo que solo aparece en el CONSIDERANDO, casi nunca.
- **Cómo se llegó.** La v1 solo aceptaba el articulado. Al revisar qué filtraba, se vio que eran vínculos reales citados en el VISTO. Después se midió la tasa de pares del gold por zona en dev.
- **Evidencia.** Restringir al articulado deja afuera 73 pares nuevos, y 72 de ellos están en el VISTO, el CONSIDERANDO o un anexo (B35). En el VISTO, el 80 % de los pares están en el gold; solo en el CONSIDERANDO, el 24 %. Aceptar el VISTO es lo que más mejora la v2 (B36).
- **Límite.** La misma señal es la principal fuente de falsos positivos (3.1).

### 2.4 Un modelo entrenado con atributos de superficie empata con las reglas

- **Conclusión.** Con los atributos que usan las reglas (zona, verbo, tipo de norma, fecha), aprender en lugar de escribir las reglas no mejora nada. Lo que falta es información de la oración.
- **Cómo se llegó.** Se entrenó un random forest sobre el dataset de pares candidatos de dev, con validación cruzada agrupada por norma de origen, y se evaluó una vez en test (B37, D14).
- **Evidencia.** 0,823 en test contra 0,828 de las reglas (`results/clasificador/`).
- **Límite.** Solo se probó con atributos de superficie.

### 2.5 Leer el contexto, solo, no alcanza

- **Conclusión.** Un modelo que lee la oración con TF-IDF es peor que las reglas. Combinado con ellas ayuda en la zona gris, pero no de forma significativa.
- **Cómo se llegó.** Se entrenó un modelo TF-IDF con atributos de superficie. Se usó solo y también como desempate donde las reglas dudan (B46, D20).
- **Evidencia.** Solo, da 0,761 a 0,783 en test, y la diferencia es significativa. En el híbrido sube el recall de 0,875 a 0,906 y el F1 a 0,839, pero el intervalo de la diferencia va de −2,2 a +4,0 puntos (`results/modelo_contextual/`, `results/comparacion/`).

### 2.6 El parser LLM sube el recall y el tipado

- **Conclusión.** El LLM es el mejor en F1 y en tipo de relación, con alucinación casi nula gracias a la verificación de la cita. No resuelve el problema del VISTO.
- **Cómo se llegó.** Se diseñó un parser que manda los artículos al modelo (Sonnet 5.5), le pide las menciones con su tipo y verifica que cada cita esté literal en el texto. Las respuestas se guardan en una caché (B48, D22). Corrió sobre todo el corpus, por USD 14, y se evaluó con la misma regla de decisión que las reglas.
- **Evidencia.** F1 0,841 en test, recall 0,938 y alucinación del 0,1 %. Recupera 12 de los 24 pares que pierden las reglas: decretos sin verbo en la oración, el CONSIDERANDO y nombres propios (B54, `results/evaluacion_llm/`).
- **Límite.** La diferencia de F1 con las reglas no es significativa. Cuesta dinero y depende de la caché para ser reproducible.

### 2.7 Tabla final

| Parser | P test | R test | F1 dev | F1 test |
|---|---|---|---|---|
| Reglas v2 (referencia) | 0,785 | 0,875 | 0,733 | 0,828 |
| Reglas v3 (experimento) | 0,779 | 0,880 | 0,750 | 0,826 |
| Clasificador (random forest) | 0,799 | 0,849 | 0,728 (CV) | 0,823 |
| Modelo contextual (TF-IDF) | 0,760 | 0,807 | 0,751 (CV) | 0,783 |
| Híbrido reglas + modelo contextual | 0,780 | 0,906 | 0,749 (CV) | 0,839 |
| Parser LLM | 0,763 | 0,938 | 0,741 | 0,841 |
| Híbrido reglas ∩ LLM | 0,804 | 0,875 | 0,735 | 0,838 |
| Híbrido en cascada | 0,761 | 0,911 | 0,758 | 0,829 |

**Respuesta a la PI1.** Los tres enfoques están entre 0,78 y 0,84 de F1 en test. Las reglas bien diseñadas ya son competitivas, y el resto mejora sobre todo el recall y el tipo. El límite común no está en los métodos sino en dos cosas: el techo textual (1.2) y la ambigüedad de las citas del VISTO (3.1).

## 3. PI2 · ¿Un híbrido mejora sobre cada enfoque por separado?

### 3.1 La intersección de reglas y LLM es la única mejora significativa

- **Conclusión.** Aceptar un par solo si lo aceptan las reglas y el LLM sube la precisión sin perder recall. Es la única diferencia significativa del TP.
- **Cómo se llegó.** Se compararon por bootstrap pareado las combinaciones de reglas y LLM sobre los mismos 192 pares de test (B54, D26).
- **Evidencia.** F1 0,838, precisión 0,804. La diferencia con las reglas es de +1,0 puntos, con intervalo de +0,2 a +2,5 (`results/comparacion/`).
- **Límite.** La mejora es chica. Lo que la hace robusta es que el intervalo no toca el cero.

### 3.2 El híbrido en cascada es el mejor en dev y empata en test

- **Conclusión.** Usar las reglas para filtrar y el LLM solo para decidir la zona gris es lo mejor en dev y cuesta un cuarto del LLM puro. En test empata: las reglas ya resuelven bien los casos claros, y en la zona gris el LLM tampoco sabe qué hace InfoLEG con las citas del VISTO.
- **Cómo se llegó.** Se diseñó sobre dev una política con umbrales y se congeló antes de test (B55, D27, `docs/parser_hibrido.md`).
- **Evidencia.** F1 0,758 en dev, el mejor del trabajo, y 0,829 en test, con recall 0,911 (`results/hibrido/`).
- **Límite.** El VISTO sigue siendo el límite. El 80 % de los falsos positivos de test son citas del VISTO y remisiones desde leyes (B52).

**Respuesta a la PI2.** Sí, pero poco. El híbrido mejora de forma significativa solo cuando combina reglas y LLM por intersección (+1 punto). El híbrido en cascada es el más eficiente (mejor en dev, a un cuarto del costo) y en el digesto de la UNNOBA es el mejor de todos (5.1).

## 4. PI3 · Qué formulaciones producen más errores

La respuesta sale de explicar cada falso negativo y cada falso positivo de test, uno por uno, con su causa y su evidencia (`18_explicar_errores.py`, `results/errores_explicados/`, B51). También de medir cada subtarea por separado: detección, normalización y decisión (`12_evaluar_subtareas.py`, B45).

### 4.1 Casi todas las pérdidas están en la decisión, no en la detección

- **Evidencia.** La detección encuentra el 99,6 % de los destinos nombrados, y la vinculación al id correcto es del 99,1 %. De los 24 pares que se pierden en test, 16 los descarta la regla, 7 no nombran a su destino y 1 no se normaliza (B45, B51).
- **Conclusión.** Mejorar el detector no mueve el resultado. Lo que hay que mejorar es decidir si la mención es un vínculo.

### 4.2 Las formulaciones que más fallan

| Formulación | Error que produce | Evidencia |
|---|---|---|
| Cita en el VISTO de una norma que solo se menciona («Visto la Ley 20.744…») | Falso positivo: parece un vínculo y no está en InfoLEG | El 80 % de los FP de test (B52) |
| Remisión desde una ley a otra, de paso (Ganancias, IVA) | Falso positivo | B35 |
| «Ley 20.744 (t.o. por Decreto 390/76)» | El decreto cuenta como otra mención y da un falso positivo | B35 |
| Decreto que aplica la ley sin verbo en la oración, o solo en el CONSIDERANDO | Falso negativo: la regla lo descarta | 16 de 24 FN de test (B51) |
| «Decreto N° 467 del 14 de abril de 1988» (año escrito como fecha) | Error de normalización: el detector no lee el año | 360 de 580 menciones quedan ambiguas, 31 se vinculan mal y se pierden 10 pares (B51) |
| Decreto sin año que se resuelve por el número | Vinculación arriesgada: el 4,1 % de las vinculadas | B45 |
| Nominalización («la derogación del artículo 2°») y verbo que no actúa («deberá proponer la reglamentación») | Error de tipo: se toma como acción | Tipo correcto en `MODIFICA` en 1 de 6 casos (B43) |
| Cita tomada como acción | Error de tipo dominante: 21 de 25 errores en 78 casos | Macro-F1 0,672 (B47) |
| Vínculo sin mención (complementa, t.o., derogación genérica) | Imposible de encontrar en el texto | 80 pares (1.2) |

### 4.3 Corregir la normalización no mueve el F1

- **Conclusión.** Se arregló el error del año escrito como fecha, y el F1 de test no cambió. El cuello de botella está en la decisión.
- **Cómo se llegó.** La v3 corrige la normalización y se midió con ablación sobre dev (B52, D25).
- **Evidencia.** Las vinculaciones erróneas pasan de 31 a 0, y la normalización deja de perder pares. Test queda en 0,826 contra 0,828: gana 3 pares y pierde 2 por una regresión en el filtro de procedencia (`results/reglas_v3/`).

### 4.4 El tipo de relación por verbo es una heurística débil; el LLM tipa mucho mejor

- **Evidencia.** Con las reglas, macro-F1 de 0,672 y exactitud de 0,754 en 78 casos. Con el LLM, la macro-F1 sube a 0,883 (B47, B54).
- **Conclusión.** El tipo necesita leer la oración: si el verbo actúa, sobre qué parte y si es una cita. Es donde el LLM más aporta.

**Respuesta a la PI3.** Lo que más falla son las citas sin acción en el VISTO y las remisiones (falsos positivos). Le siguen los decretos que aplican una ley sin decirlo con un verbo (falsos negativos) y el año escrito como fecha (normalización, ya corregido en la v3). En el tipo, la cita leída como acción.

## 5. PI4 · Transferencia a otro cuerpo normativo

### 5.1 El pipeline se transfiere si el adaptador lleva el vocabulario de la fuente

- **Conclusión.** Cambiando solo el adaptador (texto, partes, menciones y claves), los tres parsers funcionan sobre el digesto de la UNNOBA. El híbrido es el mejor. La condición es que el vocabulario de la fuente (los tipos de norma y los verbos) sea parte del adaptador.
- **Cómo se llegó.**
  1. Se bajaron 912 documentos del digesto a mano, porque su robots.txt prohíbe automatizarlo (B56).
  2. Se sortearon 70 con una semilla fija, estratificados para que haya relaciones: ordenanzas, temas de reglamentos y 15 al azar.
  3. Claude anotó un gold de tres clases (MOD, APLICA y CITA). Se evaluó el vínculo, MOD ∪ APLICA, para que sea comparable con InfoLEG.
  4. Se escribió `fuentes/unnoba.py` y se corrieron las reglas, el LLM y el híbrido sin ajustar nada.
  5. Para medir el peso del vocabulario se probó una variante del prompt que cambia solo las frases que enumeran tipos de norma (B57, D28).
- **Evidencia** (`results/pi4_unnoba/`):

  | Método | F1 del vínculo |
  |---|---|
  | Reglas F (v2) = F3 (v3) | 0,917 |
  | LLM, prompt de InfoLEG | 0,405 |
  | LLM, prompt con el vocabulario | 0,864 |
  | Híbrido | **0,958** |

  - **El vocabulario.** El LLM con el prompt de InfoLEG ignora las resoluciones, porque el prompt solo habla de leyes y decretos. Con tres frases nuevas sube 46 puntos, la única diferencia significativa de la PI4.
  - **Los verbos.** El léxico de InfoLEG no tiene «Ratificar» ni «Dejar sin efecto» en infinitivo, y las reglas pierden la mitad del tipo MOD: F1 0,625 contra 0,788 del LLM con el vocabulario.
- **Límite.**
  - Son 70 documentos, y la diferencia entre el híbrido y las reglas no es significativa (el intervalo va de −0,002 a +0,101).
  - El gold lo anotó Claude y falta un segundo anotador.
  - 38 documentos son escaneos con OCR (ver `docs/reproducibilidad.md`).

### 5.2 Las remisiones que definen a quién alcanza la norma son vínculo

- **Conclusión.** En el digesto, el caso dudoso equivalente al VISTO de InfoLEG es la remisión del articulado («los alumnos comprendidos en la Res. 44/08»). Se decidió que es APLICA, es decir, vínculo.
- **Cómo se llegó.** Se releyeron los 108 pares en contexto. Se compararon con dos documentos en los que la relación era clara (docs 25 y 26), y se cambiaron las anotaciones inconsistentes, marcando cada cambio (B58, `docs/pi4_revision_gold.md`).
- **Evidencia.** 14 remisiones pasaron de CITA a APLICA. Los números con la revisión anterior se informan como sensibilidad.

**Respuesta a la PI4.** La transferencia es buena (F1 0,92 a 0,96) con modificaciones mínimas. Pero «mínimas» tiene que incluir el vocabulario de la fuente: sin él, el LLM se cae a 0,405. La arquitectura con el adaptador como único punto que depende de la fuente se sostuvo: no se tocó ni una regla, ni un umbral, ni el código de los extractores.

## 6. PI5 · Qué aporta el grafo con evidencia y procedencia

### 6.1 El grafo devuelve exactamente lo que se le cargó

- **Conclusión.** El grafo es una representación fiel de la salida de los parsers: no pierde ni agrega pares.
- **Cómo se llegó.** Se cargó en Neo4j la salida estándar de cada parser, se leyó de vuelta con Cypher y se comparó con la entrada. Primero con una copia en memoria (B43) y después con las cuatro fuentes en el Neo4j del equipo (B60).
- **Evidencia.** La ida y vuelta es idéntica en las cuatro fuentes, y el F1 leído desde el grafo es el mismo que el del parser: 0,828 en test con las reglas v2 (`results/evaluacion_grafo_neo4j/`).

### 6.2 La evidencia en el grafo explica dónde está el problema

- **Conclusión.** Tener el tipo y el fragmento en cada arista permite ver que las relaciones que cambian el texto casi siempre están en InfoLEG, y las citas no.
- **Evidencia.** Los pares con `SUSTITUYE` o `DEROGA` están en InfoLEG entre el 90 % y el 100 % de las veces; los que solo tienen citas, alrededor del 63 %. Esas citas explican 160 de los 185 falsos positivos (B43).
- **Por qué importa.** Una tabla de pares no deja ver esto. Con el grafo es una consulta.

### 6.3 El grafo alcanza para reconstruir el texto vigente de una ley

- **Conclusión.** Esta es la prueba más fuerte de la PI5. Con lo que tiene el grafo (qué artículo de qué norma actúa sobre qué artículo, y su texto) se puede armar el texto consolidado de la ley con más profundidad, la LCT, con la historia de cada artículo.
- **Cómo se llegó.**
  1. Se eligió la ley por profundidad en el grafo: 105 normas modificatorias y una cadena de 16 saltos (`23_consultar_consolidado.py --ranking`).
  2. Se sacó el manifiesto de Neo4j: 943 relaciones de 107 normas.
  3. Se aplicaron las modificaciones en orden cronológico. El LLM extrae la operación y el texto nuevo, y una verificación literal descarta lo que no está en la norma (`24_consolidar.py`).
  4. Se comparó artículo por artículo con el texto actualizado de InfoLEG, que se usa solo para medir (`25_evaluar_consolidado.py`, B61).
- **Evidencia.** Coincide en 281 de 293 artículos (95,9 %) y en 94 de los 103 que cambian (91 %). Las cadenas largas se reconstruyen bien: el art. 245 pasa por cinco normas y el 92 bis tiene seis versiones (`docs/consolidado_lct.md`).
- **Los 6 errores reales** tienen tres causas, y ninguna es de la consolidación:
  - recall del grafo: la Ley 24.522 no está vinculada (4 artículos);
  - la verificación literal descartó una sustitución (1);
  - el método no modela la derogación de una norma modificatoria (1).
- **Límite.** No sirve como texto oficial. No modela vigencias diferidas, suspensiones judiciales ni vetos.

### 6.4 El modelo del grafo sirve para cualquier fuente

- **Conclusión.** El mismo modelo de nodos y aristas, y el mismo código, cargan el digesto de la UNNOBA en la misma base que InfoLEG, sin choques.
- **Evidencia.** 104 normas del digesto, con ids desde 9.000.001 y su `fuente` propia. La base tiene 444 normas en total (B59).

**Respuesta a la PI5.** El grafo aporta tres cosas:
- **trazabilidad:** cada vínculo se puede justificar con su fragmento y su método;
- **análisis:** se puede preguntar por tipo, zona o parser, y ver dónde fallan;
- **reconstrucción:** el texto vigente de una ley con su historia, que una tabla de pares no da.

Lo que no se llegó a probar es la consulta en lenguaje natural (text-to-Cypher, F7). Hay cinco consultas de ejemplo con su pregunta en `docs/grafo.md`, pero no un sistema evaluado.

## 7. Conclusiones sobre el proceso

- **Congelar el corpus fue necesario.** El portal cambió los hashes en un mes (B17). Sin congelar, los números no se podrían repetir (`docs/reproducibilidad.md`).
- **Medir cada subtarea por separado cambió dónde se puso el esfuerzo.** La v3 mostró que mejorar la normalización no mueve el F1. Sin la evaluación por subtareas, el siguiente paso habría sido seguir puliendo el detector.
- **Explicar cada error encontró problemas del gold y del método** que el F1 solo no muestra: errores del gold, vínculos sin mención y el caso del t.o.
- **Un diagnóstico se tuvo que corregir.** El 401 de la API se atribuyó primero a la clave y era el proxy del entorno (B53). Quedó registrado como error, junto con la corrección.
- **El costo del LLM es acotado y se paga una vez.** USD 14 por todo el corpus y USD 2,4 por el consolidado. Con la caché, cada corrida siguiente es gratis e idéntica.

## 8. Lo que queda abierto

- **Validación humana.** Las revisiones manuales y el gold de la PI4 los hizo Claude. Falta que el equipo los valide y un segundo anotador para el kappa (B58).
- **Text-to-Cypher** (F7): no empezado.
- **Reglas v4:** los ajustes identificados en B52 y B57, diseñados sobre dev.
- **Consultas a la cátedra:** supervisión distante, modificación estricta y clasificación fina (B02, B14, B27).
- **El artículo LNCS y sus figuras:** el embudo de pérdidas, la matriz de confusión de tipos, la tabla de métodos con intervalos y el diagrama del pipeline.
