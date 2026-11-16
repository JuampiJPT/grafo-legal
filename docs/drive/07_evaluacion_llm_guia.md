# 07 - Evaluación completa, parser LLM y guía del código

*Copia de documentos del repositorio (github.com/JuampiJPT/grafo-legal), 16/11/2026. Bitácora B45 a B51. Las versiones de referencia están en el repositorio, en las rutas indicadas en cada sección.*

## Cómo se compara el parser con el gold de InfoLEG

Este documento es la base de la sección «Diseño experimental» del artículo.

### 1. Qué es el gold

InfoLEG publica dos bases complementarias: la de normas modificatorias y la de normas modificadas. Cada fila dice que una norma A «modifica o complementa» a una norma B. El gold del TP son los pares de esa base con origen y destino entre las 340 normas del corpus: **775 pares** (`data/corpus/gold_relaciones.csv`, snapshot del 06/11/2026).

Tres cosas a tener en cuenta:

- **El vínculo es amplio.** En una revisión de 21 pares con mención explícita, 7 son modificaciones, 4 reglamentaciones, 1 texto ordenado y 9 remisiones (B27). Por eso el gold no se compara contra «modifica» en sentido estricto.
- **Es a nivel de norma.** No dice qué artículo ni qué tipo de relación.
- **Tiene ruido.** En 3 de 30 falsos positivos revisados, el texto sí modifica a la norma y InfoLEG no lo registra (B36).

**El gold nunca es entrada del parser.** Lo leen solo los scripts de evaluación: 04, 05, 11, 12, 13 (para entrenar en dev), 15, 16 y 17.

### 2. Split temporal

- **dev:** la norma modificatoria es del 31/12/2019 o anterior (583 pares);
- **test:** la norma modificatoria es posterior (192 pares).

Las reglas, los umbrales de los modelos y la proyección del LLM se eligieron mirando solo dev. Test se evaluó una vez por versión congelada, con fecha y huella SHA-256 del código registradas. El split temporal mide además si el método aguanta el paso del tiempo: test tiene la Ley 27.802, el DNU 70/2023 y sus reglamentaciones.

### 3. Unidad de comparación: el par de normas

El parser produce relaciones tipadas por artículo («el art. 70 del Decreto 70/2023 SUSTITUYE el art. 80 de la Ley 20.744»). Para compararlas con InfoLEG se proyectan a pares (origen, destino).

- **Reglas.** El par está predicho si alguna de sus menciones pasa la regla F: está en el VISTO, o en el articulado con número cuando el origen es una ley o la oración tiene un verbo modificatorio. En todas se exige que la mención no sea una cita de procedencia y que el destino no sea posterior al origen.
- **LLM.** Se prueban cuatro proyecciones y se elige una en dev (`docs/parser_llm.md`).
- **Grafo.** La misma regla F se aplica sobre las aristas leídas del grafo (script 11), y da exactamente las mismas métricas que sobre los archivos del parser.

### 4. Métricas

Sobre pares, contra **todo** el gold del split:

- **precisión:** de los pares que predice el parser, cuántos están en el gold;
- **recall:** de los pares del gold, cuántos recupera;
- **F1:** media armónica de las dos.

Un par del gold que el parser no puede ver, porque no tiene texto o no tiene mención, cuenta como falso negativo. Así todos los métodos se comparan sobre la misma base. Además se reportan:

- el recall sobre el gold con texto;
- el F1 sobre los pares que no se usaron cuando se diseñaron las reglas (`sin_pares_de_v1`), que mide la generalización.

### 5. Evaluación por subtareas

`results/subtareas/RESULTADOS.md` mide cada eslabón por separado:

| Subtarea | Métrica | Resultado |
|---|---|---|
| Detección | Recall contra una búsqueda laxa del número o el nombre de la norma destino; precisión en una muestra de 60 | 0,996 en dev y 1,000 en test; 0,97 |
| Normalización | Proporción de menciones no resueltas; exactitud de vinculación contra el catálogo completo de InfoLEG y la fecha escrita en el texto | 55,6 % no resueltas (48,0 % son normas fuera del corpus); exactitud estimada 99,1 % |
| Extracción | P, R y F1 de punta a punta y condicional a los candidatos | test 0,828 de punta a punta; 0,842 condicional |

Además están el embudo (dónde se pierde cada par del gold) y la taxonomía de errores con las categorías de la consigna. Cada error tiene su causa concreta y su evidencia en `results/errores_explicados/RESULTADOS.md`.

### 6. Techo de recall

En test, 7 de los 192 pares (4 %) no tienen ninguna mención de la norma destino en el texto de la modificatoria. En dev son 75 de 583 (13 %), más 35 sin texto. Ningún método que lea el texto puede recuperarlos. El techo es un recall de 0,964 en test y 0,811 en dev.

### 7. El tipo de relación

InfoLEG no registra el tipo, así que se evalúa contra una revisión manual de 78 relaciones, 13 por tipo predicho. Se reportan la matriz de confusión, la macro-F1 ponderada a la población y la exactitud del artículo destino (`results/tipos/RESULTADOS.md`). La revisión es una primera pasada de Claude y está pendiente de validación humana y de un segundo anotador para el kappa.

### 8. Comparación entre métodos e incertidumbre

`scripts/17_comparar_metodos.py` arma la tabla final en test con intervalos de confianza del 95 %, por bootstrap pareado sobre normas origen (2.000 réplicas). Se remuestrean normas y no pares, porque los pares de una misma norma no son independientes. Si el intervalo de la diferencia con las reglas contiene al 0, la diferencia no es significativa.

| Método | P | R | F1 | IC 95 % F1 | Diferencia con las reglas [IC 95 %] |
|---|---|---|---|---|---|
| Híbrido reglas + modelo contextual (texto + superficie) | 0,780 | 0,906 | 0,839 | 0,794 – 0,878 | +0,011 [−0,022; +0,040] |
| Reglas v2, regla F | 0,785 | 0,875 | 0,828 | 0,783 – 0,875 | — |
| Clasificador de superficie | 0,799 | 0,849 | 0,823 | 0,781 – 0,861 | −0,004 [−0,035; +0,025] |
| Híbrido reglas + modelo contextual (solo texto) | 0,716 | 0,932 | 0,810 | 0,752 – 0,851 | −0,018 [−0,076; +0,023] |
| Modelo contextual (texto + superficie) | 0,760 | 0,807 | 0,783 | 0,735 – 0,827 | −0,045 [−0,086; −0,007] |
| Modelo contextual (solo texto) | 0,697 | 0,839 | 0,761 | 0,689 – 0,810 | −0,066 [−0,136; −0,015] |

El parser LLM y sus híbridos se agregan a esta tabla cuando se corran (bitácora B48).

*Fuente: `docs/comparacion_con_el_gold.md`.*

## Evaluación por subtareas: detección, normalización y extracción

`scripts/12_evaluar_subtareas.py` mide por separado los tres eslabones del parser de reglas v2, como pide la consigna, y clasifica los errores con las categorías de la consigna (bitácora B45). El gold se usa solo para medir.

### Cómo se mide cada subtarea

| Subtarea | Pregunta | Referencia |
|---|---|---|
| Detección | ¿El detector encontró la mención a la norma destino? | Una búsqueda laxa, independiente del detector: el número de la norma destino («20.744» o «20744») como número suelto, sus nombres propios del gazetteer o nombres que el gazetteer no tiene («Ley de Ministerios», «L.C.T.»). Si aparece y el detector no lo vio, es un fallo de detección. Para la precisión, una muestra de 60 menciones revisada a mano (`docs/revision_manual/revision_deteccion_60.csv`). |
| Normalización | ¿La mención se vinculó a la norma correcta? | Cada mención se resuelve contra el catálogo del corpus (el que usa el parser) y contra el catálogo completo de InfoLEG: 106.466 leyes, decretos y decretos-leyes. Si el texto escribe el año como fecha después de la mención («Decreto 84 del 23 de enero de 2014»), ese año confirma o contradice la vinculación. |
| Extracción | Con la mención detectada y normalizada, ¿la regla decide bien si hay relación? | El gold, sobre los pares candidatos: así se aísla la decisión de las reglas de los pasos anteriores. |

### 1. Detección

| | dev | test |
|---|---|---|
| Pares del gold con texto | 548 | 192 |
| … cuyo destino aparece en el texto (búsqueda laxa) | 475 | 185 |
| … y el detector lo encontró | 473 | 185 |
| **Recall de detección** | **0,996** | **1,000** |

Cuando el número de la norma destino está en el texto, el detector siempre lo encuentra. Los 2 fallos de dev son nombres que el gazetteer no tiene: «Ley de Ministerios» y «L.C.T.». Los pares que no nombran la norma destino en ninguna forma (73 en dev, 7 en test) no se pueden recuperar leyendo el texto; por qué los registra InfoLEG está en `results/errores_explicados/RESULTADOS.md`.

**Precisión de detección:** de 60 menciones al azar, 58 son citas inequívocas a una norma. Las otras 2 son nombres de tributos tomados como alias de la ley («Impuesto al Valor Agregado», «impuesto a las ganancias»): en «Exención del Impuesto a las Ganancias» el texto habla del tributo, no cita la ley. Precisión: 0,97. La revisión es de Claude y está pendiente de validación humana.

### 2. Normalización

8.062 menciones por número en las 306 normas con texto (más 853 por nombre propio, que por construcción apuntan a una norma del corpus).

| Estado | Total | % | dev | test |
|---|---|---|---|---|
| Resuelta sin ambigüedad (una sola candidata en InfoLEG, o una sola anterior a la norma que cita) | 3.430 | 42,5 % | 2.381 | 1.049 |
| Resuelta solo por el mundo cerrado (varias candidatas en InfoLEG, una en el corpus) | 147 | 1,8 % | 112 | 35 |
| Fuera del corpus (existe en InfoLEG, no en el corpus) | 3.868 | 48,0 % | 2.802 | 1.066 |
| Ambigua (varias candidatas en InfoLEG, ninguna en el corpus: un decreto citado sin año) | 580 | 7,2 % | 476 | 104 |
| No encontrada en ningún catálogo (OCR, normas provinciales) | 37 | 0,5 % | 37 | 0 |

- **Proporción de referencias no resueltas:** 55,6 % (dev 57,1 %, test 51,9 %). Casi todas son normas que existen pero están fuera del corpus (48,0 %). Es un efecto del tamaño del corpus, no un error del normalizador.
- **Exactitud de vinculación:** el 95,9 % de las menciones vinculadas es inequívoco también contra todo InfoLEG. El 4,1 % restante (147) son decretos citados sin «/año» que el parser vincula porque el corpus tiene uno solo con ese número. En 117 de ellos el texto escribe el año como fecha y se puede verificar: 86 están bien y **31 son otro decreto con el mismo número**. Con eso, la exactitud estimada es **99,1 %** (dev 99,0 %, test 99,4 %), y quedan 30 vinculaciones sin verificar.
- **Por qué quedan ambiguas 580 menciones:** son decretos sin «/año» con varias candidatas en InfoLEG. En 360 el año está escrito como fecha («del 20 de noviembre de 1974»): el detector no lo lee. Es la mejora con más efecto sobre la normalización.
- **Por qué no se encuentran 37:** casi todos son decretos de 1930 a 1980 que InfoLEG no tiene catalogados.

### 3. Extracción

| | P | R | F1 |
|---|---|---|---|
| dev, de punta a punta (contra todo el gold) | 0,750 | 0,717 | 0,733 |
| dev, condicional a los candidatos | 0,750 | 0,886 | 0,812 |
| test, de punta a punta | 0,785 | 0,875 | 0,828 |
| test, condicional a los candidatos | 0,785 | 0,908 | **0,842** |

La regla F, sola, recupera el 91 % de los pares de test que ya pasaron detección y normalización. La diferencia entre las dos filas es el techo que ponen los pasos anteriores.

### Embudo: dónde se pierde cada par del gold

| Paso | dev | test |
|---|---|---|
| 1. Pares del gold | 583 | 192 |
| 2. Con texto en InfoLEG | 548 | 192 |
| 3. Con mención explícita del destino en el texto | 475 | 185 |
| 4. Detectados | 473 | 185 |
| 5. Normalizados a la norma correcta | 464 | 184 |
| 6. Extraídos por la regla F | 418 | 168 |

En test se pierden 24 pares: 7 no tienen mención en el texto (paso 3), 1 no se normaliza porque el año del decreto está escrito como fecha (paso 5) y 16 los descarta la regla (paso 6). En dev, la detección pierde 2 y la normalización 9.

### Taxonomía de errores (categorías de la consigna)

| Categoría | Qué es | dev | test |
|---|---|---|---|
| **Falsos negativos** | | | |
| Norma no detectada | El destino aparece en el texto y el detector no lo vio | 2 | 0 |
| Norma mal normalizada | Se detectó el número pero no se vinculó (año escrito como fecha) | 9 | 1 |
| Relación descartada por la regla | Detectada y normalizada, la regla F dijo que no | 46 | 16 |
| Sin mención explícita | El texto no nombra la norma destino | 73 | 7 |
| Sin texto (fuera de alcance) | InfoLEG no publica el texto de la modificatoria | 35 | 0 |
| **Falsos positivos** | | | |
| Relación inexistente | La norma se cita, pero InfoLEG no registra el vínculo | 129 | 42 |
| Norma mal normalizada | Se vinculó a otro decreto con el mismo número (la fecha del texto lo contradice) | 8 | 1 |
| Referencia ambigua | Decreto sin año que la fecha no confirma, o solo un nombre propio | 2 | 3 |
| Relación invertida | El gold tiene el par al revés | 0 | 0 |
| **Otras** | | | |
| Destino ausente del corpus | Pares que la regla F extraería si el destino estuviera en el catálogo | 886 | 203 |
| Tipo incorrecto | Ver `results/tipos/RESULTADOS.md` | 25 de 78 en la muestra | |

- **Cada error tiene su causa concreta y su evidencia** en `results/errores_explicados/` (B51).
- **No hay relaciones invertidas.** La restricción temporal (una norma no puede modificar a otra posterior) las elimina.
- **Los destinos fuera del corpus no son ruido.** Contra la base complementaria completa de InfoLEG, el 54 % de esos pares en dev y el 62 % en test son vínculos registrados. El parser generaliza fuera del corpus con una precisión unos 20 puntos menor que dentro. La diferencia se explica porque normas de alcance amplio, como la Ley 23.697 de Emergencia Económica, citan muchas leyes que no modifican.

### Archivos

- `metricas.json`: todas las cifras de este documento.
- `menciones.csv`: las 8.915 menciones, con su estado de normalización y la cantidad de candidatas en InfoLEG.
- `errores.csv`: cada falso negativo y falso positivo de la configuración F con su categoría.
- `deteccion_fallos.csv`: pares en los que el número aparece y el detector no lo vio (vacío).

*Fuente: `results/subtareas/RESULTADOS.md`.*

## Por qué falla cada error del parser

`scripts/18_explicar_errores.py` le asigna a cada falso negativo y a cada falso positivo del parser de reglas v2 (configuración F) una **causa concreta**, una **explicación** y la **evidencia** del texto que la muestra (bitácora B51). La lista completa, caso por caso, está en `errores_explicados.csv`: 304 errores de dev y 70 de test.

### Cómo se asignó la causa

- **Falsos negativos que descarta la regla:** automáticamente, mirando dónde están las menciones del par y si la oración tiene verbo. Es la misma información que usó la regla para decidir, así que la causa es exacta.
- **Falsos negativos sin mención explícita:** no hay mención que mirar, así que hubo que leer el texto.
  - Una parte se asigna con reglas: el destino es un decreto de texto ordenado, InfoLEG no publica el texto completo, o la norma destino modificaba a una ley que el origen deroga.
  - El resto (57 pares) se revisó a mano. La revisión es de Claude y está pendiente de validación humana.
- **Falsos positivos:** automáticamente, según por qué pasó la regla (cita en el VISTO, remisión desde una ley, verbo que no actúa sobre el destino, alias). Hay 8 casos corregidos a mano.
- **Errores de normalización:** se detectan leyendo la fecha que sigue a la mención. «Decreto N° 84 del 23 de enero de 2014» dice el año aunque no esté escrito «84/14».

### Falsos negativos: relaciones de InfoLEG que el parser no encontró

| Eslabón | Causa | dev | test | Qué pasó |
|---|---|---|---|---|
| Fuera de alcance | Sin texto | 35 | 0 | InfoLEG no publica el texto de la modificatoria. |
| Detección | Nombre no reconocido | 2 | 0 | Se nombra con un nombre que no está en el gazetteer: «Ley de Ministerios» (Ley 24.013 → Ley 22.520) y «L.C.T.» (Decreto 328/88 → LCT). |
| Normalización | Año escrito como fecha | 9 | 1 | «Decreto N° 467 del 14 de abril de 1988»: el detector no lee el año de la fecha y en el corpus hay tres decretos 467, así que la mención queda sin resolver. |
| Extracción | CONSIDERANDO y decreto sin verbo | 10 | 6 | Ejemplo: el Decreto 266/20 nombra el Decreto 590/97 en el CONSIDERANDO y en el articulado («creado mediante el Decreto N° 590/97»), sin verbo. |
| Extracción | Decreto, articulado sin verbo | 10 | 4 | «en los términos del apartado 2 … del artículo 6º de la Ley Nº 24.557» (Decreto 875/20). La regla F lo trata como remisión. |
| Extracción | Solo en el CONSIDERANDO | 6 | 3 | «la emergencia pública en materia sanitaria establecida por la Ley N° 27.541» (Decreto 367/20). |
| Extracción | Solo por nombre propio | 14 | 2 | La Ley 27.802 modifica «la Ley de Impuesto a las Ganancias, texto ordenado en 2019» sin dar el número, y la regla exige número en el articulado. |
| Extracción | Solo cita de procedencia | 2 | 1 | «Ley 18.345 (t.o. por Decreto Nº 106/98)»: la regla descarta a propósito estas citas, e InfoLEG sí vincula el decreto del texto ordenado. |
| Extracción | Solo en anexos o notas | 4 | 0 | Las menciones están en un anexo o en una nota de InfoLEG. |
| Sin mención | Texto ordenado implícito | 4 | 5 | La Ley 27.802 cita la «Ley de Impuesto al Valor Agregado (t.o. en 1997)», e InfoLEG registra el vínculo con el Decreto 280/97, que aprobó ese texto ordenado y el texto no nombra. |
| Sin mención | Complementa sin citar | 36 | 0 | Regula la misma materia sin nombrar la norma. Ejemplo: la Ley 23.691 da licencia paga para trámites, e InfoLEG la registra como complementaria de la LCT. |
| Sin mención | Modificatorias de la ley citada | 8 | 0 | La LCT de 1974 deroga la Ley 11.317, e InfoLEG registra el vínculo también con las normas que habían modificado a esa ley. |
| Sin mención | Derogación genérica | 8 | 0 | «toda otra disposición legal o reglamentaria que se oponga» (LCT de 1974). |
| Sin mención | Texto incompleto en InfoLEG | 7 | 0 | «El texto completo original … no se encuentra en nuestra base», o el decreto «se publica sin el anexo I». |
| Sin mención | Referencia conceptual | 5 | 0 | «el convenio colectivo de la actividad» (Ley 14.250), «asociaciones sindicales con personería gremial» (Ley 23.551). |
| Sin mención | Organismo en lugar de norma | 3 | 0 | Nombra la ANSES y no el Decreto 2741/91 que la creó. |
| Sin mención | Posible error del gold | 2 | 0 | El Decreto 12/99 designa un ministro interino de Relaciones Exteriores e InfoLEG lo vincula con la Ley de Asociaciones Sindicales; el Decreto 415/01 designa subsecretarios de Economía y aparece vinculado a la Ley de Riesgos del Trabajo. |
| Sin mención | No verificable | 0 | 2 | El DNU 70/2023 no nombra la Ley 23.789 (telegrama gratuito) ni la 18.345 (procedimiento laboral), y no se encontró un vínculo indirecto. |

### Falsos positivos: pares que el parser propuso y InfoLEG no registra

| Eslabón | Causa | dev | test | Qué pasó |
|---|---|---|---|---|
| Extracción | Cita en el VISTO | 48 | 24 | La norma está en la lista de fundamentos del VISTO. Ejemplo: el Decreto 39/21 enumera «las Leyes Nros. 24.241, 24.557, 26.122, 26.773, 27.348 y 27.541», y solo modifica a una. La regla acepta todo el VISTO porque el 80 % de esos pares está en InfoLEG. |
| Extracción | Remisión desde una ley | 66 | 14 | «quedará exenta del pago del impuesto a las ganancias establecido en la ley 20.628» (Ley 27.555). Una ley nombra la norma en su articulado sin modificarla. |
| Extracción | Verbo que no actúa | 6 | 3 | Hay un verbo en la oración, pero es nominal o actúa sobre otra norma: «… Ley N° 24.557 y sus modificaciones», «Reglamentación» de otra ley. |
| Extracción | Procedencia no filtrada | 4 | 1 | «creado por la ley 25.565 y ampliado y modificado por ley 27.637» (Ley 27.742). El filtro de procedencia solo cubre «t.o.» y «sustituido por el artículo N del». |
| Normalización | Otro decreto con el mismo número | 8 | 1 | «Decreto 267 del 29 de diciembre de 2015» (DNU 70/2023), vinculado al único Decreto 267 del corpus, que es de 2006: es otro decreto. |
| Normalización | Decreto sin año, mundo cerrado | 1 | 2 | Decreto citado sin año, que en InfoLEG tiene varias candidatas. |
| Detección | Alias de otra ley | 1 | 0 | «Ley de Convenciones Colectivas de Trabajo de la Administración Pública Nacional Nº 24.185» empieza igual que el nombre de la Ley 14.250. |
| Detección | Error en el texto fuente | 0 | 1 | El Decreto 841/22 dice «Ley de Impuesto a las Ganancias N° 20.744», que es el número de la LCT. |
| Gold | Posible omisión del gold | 5 | 0 | El texto modifica a la norma e InfoLEG no lo registra. Ejemplo: la Ley 24.347, «Modificación de la Ley Nº 24.241», incorpora un texto a esa ley. |

### Detección: los 2 errores de la muestra de 60

Las dos menciones dudosas son nombres de tributos que el gazetteer toma como alias de su ley: «Impuesto al Valor Agregado» y «impuesto a las ganancias». En «Exención del Impuesto a las Ganancias» el texto habla del tributo, no cita la ley. El mismo problema aparece en los falsos negativos («solo por nombre propio») y en el tipado (B47), donde «Agregado» se lee como verbo.

### Normalización: por qué no se resuelve una mención

| Estado | Menciones | Por qué |
|---|---|---|
| Fuera del corpus | 3.868 | Son normas reales de InfoLEG que no están entre las 340 del corpus (mundo cerrado). No es un error. |
| Ambigua | 580 | Decreto citado sin «/año», con varias candidatas en InfoLEG. **En 360 el año está escrito como fecha** («del 20 de noviembre de 1974»); leyéndolo, se resolverían. |
| Resuelta solo por mundo cerrado | 147 | El corpus tiene un solo decreto con ese número y se vincula a ese. En 117 el año de la fecha permite verificarlo: **86 bien y 31 mal** (otro decreto con el mismo número). Los otros 30 no se pueden verificar. |
| No encontrada | 37 | No está en ningún catálogo. Casi todos son decretos de 1930 a 1980 que InfoLEG no tiene catalogados (por ejemplo el Decreto 20.268/46), y algunos tienen el año cambiado. |

Con la verificación por fecha, la **exactitud de vinculación estimada es 99,1 %**: de las 3.547 vinculaciones que se pueden verificar, 31 son erróneas. Antes se reportaba 95,9 %, contando como dudosas todas las de mundo cerrado.

### Qué cambia respecto de B45

Explicar cada error caso por caso corrigió la clasificación de B45:

- **La detección pierde 2 pares en dev.** Son nombres que el gazetteer no tiene. El recall de detección pasa de 1,000 a 0,996 en dev; en test sigue en 1,000.
- **La normalización pierde 9 pares en dev y 1 en test** por no leer el año escrito como fecha. Antes contaban como descartados por la regla.
- **9 falsos positivos son vinculaciones erróneas**, no relaciones inexistentes: el decreto citado es otro con el mismo número.

El parser congelado no cambia. Leer el año de la fecha es la mejora con más efecto sobre la normalización: resuelve 360 menciones ambiguas y corrige 31 vinculaciones. Queda como v3, para diseñar sobre dev y medir aparte.

*Fuente: `results/errores_explicados/RESULTADOS.md`.*

## Modelo con contexto textual e híbrido reglas + modelo

`scripts/13_modelo_contextual.py` implementa el método basado en modelos «a partir del contexto textual» que pide la consigna, y una primera aproximación al híbrido de la PI2 (bitácora B46).

### Qué lee el modelo

Por cada par candidato (norma origen → norma destino) se juntan los fragmentos de todas sus menciones: 150 caracteres a cada lado, los que el parser ya guarda como evidencia. En cada fragmento:

- la mención del destino se reemplaza por la palabra `DESTINO`;
- los dígitos se reemplazan por `#`, para que el modelo aprenda el contexto y no los números de normas;
- adelante va la parte del documento donde está la mención (`PARTE_visto`, `PARTE_articulado`…).

Ejemplo: «Sustitúyese el artículo 80 de la Ley N° 20.744 por» queda como `PARTE_articulado Sustitúyese el artículo ## de la DESTINO por`.

Sobre eso se calcula un TF-IDF de unigramas y bigramas de palabras y se entrena una regresión logística. Hay dos variantes: solo el texto (`contexto`), y el texto más los atributos de superficie del clasificador de 08 (`contexto+superficie`).

### Híbrido

Con las mismas evidencias que usa la regla F, los candidatos se separan en tres grupos:

| Grupo | Criterio | Candidatos dev | En el gold |
|---|---|---|---|
| Seguro sí | Mención en el VISTO, o en el articulado con verbo en la oración | 407 | 82 % |
| Seguro no | Ninguna mención cuenta: solo notas, anexos, procedencia o destino posterior | 64 | 9 % |
| Zona gris | El resto: articulado sin verbo, solo CONSIDERANDO, solo alias | 330 | 40 % |

Las reglas deciden los grupos seguros y el modelo decide la zona gris, donde las reglas aciertan menos.

### Protocolo

El mismo de 08:

- **Selección en dev.** Validación cruzada de 5 particiones, agrupada por norma origen. Se eligen C (de 0,3 a 100) y el umbral (de 0,20 a 0,80).
- **Modelo final.** Se entrena con todo dev y test se evalúa una sola vez, el 16/11/2026, con el script congelado (SHA-256 `d7734e9d…`). Después solo se agregó al script que guarde la probabilidad de cada variante en `predicciones.csv`. Se volvió a correr y `comparacion.csv` dio idéntico.
- **Métricas.** Contra todo el gold del split.

### Resultados

| Método | dev (CV) P | R | F1 | test P | R | F1 |
|---|---|---|---|---|---|---|
| Reglas v2, configuración F | 0,750 | 0,717 | 0,733 | 0,785 | 0,875 | 0,828 |
| Clasificador de superficie (08, random forest) | 0,766 | 0,695 | 0,728 | 0,799 | 0,849 | 0,823 |
| Modelo contextual, solo texto (C=10, umbral 0,40) | 0,705 | 0,746 | 0,725 | 0,697 | 0,839 | 0,761 |
| Modelo contextual, texto + superficie (C=30, umbral 0,20) | 0,746 | 0,756 | 0,751 | 0,760 | 0,807 | 0,783 |
| Híbrido: reglas + modelo de solo texto en la zona gris | 0,714 | 0,770 | 0,741 | 0,716 | 0,932 | 0,810 |
| **Híbrido: reglas + modelo texto + superficie en la zona gris** | 0,736 | 0,763 | 0,749 | 0,780 | 0,906 | **0,839** |

### Lectura

1. **El modelo con contexto, solo, no supera a las reglas.** En dev empata y en test cae a 0,761 con solo texto y a 0,783 con atributos. Con 801 pares de entrenamiento, un TF-IDF aprende rasgos del dominio que no transfieren de un período al siguiente: test son las normas de 2020 en adelante.
2. **El híbrido da el mejor F1 de test (0,839),** un punto más que las reglas, con más recall (0,906 contra 0,875) y precisión parecida. La mejora sale de la zona gris: el modelo recupera relaciones que las reglas descartaban, como decretos que remiten a una ley en el articulado sin verbo. Con 192 pares de test, un punto no es una diferencia significativa. El intervalo del 95 % de la diferencia con las reglas va de −2,2 a +4,0 puntos (bootstrap por norma origen, `results/comparacion/`, bitácora B49). En cambio, el modelo de solo texto es significativamente peor que las reglas: entre −13,6 y −1,5 puntos.
3. **Lo que pesa en el modelo** (`terminos.csv`). A favor de que haya relación: `parte_articulado articulo`, `la destino`, `siguiente` (de «por el siguiente»), `el articulo`, `parte_visto`. En contra: `alcance`, `especial`, `caso`, `contrato de`, `por ley`. Son señales de técnica legislativa («sustitúyese el artículo # de la DESTINO por el siguiente») frente a remisiones de contenido.

### Archivos

- `metricas.json`: hiperparámetros elegidos, CV y test de cada variante, grupos.
- `predicciones.csv`: probabilidad por candidato (en dev, la de la validación cruzada).
- `comparacion.csv`: la tabla de arriba.
- `terminos.csv`: los 30 n-gramas con más peso a favor y en contra.

*Fuente: `results/modelo_contextual/RESULTADOS.md`.*

## Tipo de relación: matriz de confusión y macro-F1

`scripts/16_evaluar_tipos.py` evalúa el tipo de relación (`SUSTITUYE`, `INCORPORA`, `DEROGA`, `REGLAMENTA`, `MODIFICA`, `CITA`) y el artículo destino contra la revisión manual (bitácora B47). InfoLEG no registra el tipo, así que esta es la única medida posible.

### Muestra

La muestra tiene 78 relaciones del parser de reglas v2 (`docs/revision_manual/revision_tipos_78.csv`), 13 por cada tipo predicho:

- los 36 casos revisados en B43;
- 42 nuevos, sorteados con la semilla 20261116.

La revisión es de Claude y está pendiente de validación humana. Que un segundo anotador repita una parte da el kappa.

Como la muestra está estratificada por el tipo predicho, cada caso representa a una cantidad distinta de relaciones: uno de `CITA` representa a 179 (2.332 / 13) y uno de `REGLAMENTA` a 4,5 (58 / 13). Por eso se reportan dos cosas:

- la matriz de confusión de la muestra, en conteos;
- las métricas de la población, con cada caso ponderado por la inversa de su probabilidad de muestreo.

### Matriz de confusión de las reglas v2 (filas: predicho; columnas: correcto)

| predicho \ correcto | CITA | DEROGA | INCORPORA | MODIFICA | REGLAMENTA | SUSTITUYE |
|---|---|---|---|---|---|---|
| **CITA** | **10** | 1 | 0 | 2 | 0 | 0 |
| **DEROGA** | 2 | **11** | 0 | 0 | 0 | 0 |
| **INCORPORA** | 5 | 0 | **8** | 0 | 0 | 0 |
| **MODIFICA** | 8 | 0 | 0 | **4** | 0 | 1 |
| **REGLAMENTA** | 5 | 0 | 0 | 0 | **8** | 0 |
| **SUSTITUYE** | 1 | 0 | 0 | 0 | 0 | **12** |

### Métricas

| Tipo | P (muestra) | P (población) | R (población) | F1 (población) |
|---|---|---|---|---|
| SUSTITUYE | 0,923 | 0,923 | 0,962 | 0,942 |
| INCORPORA | 0,615 | 0,615 | 1,000 | 0,762 |
| DEROGA | 0,846 | 0,846 | 0,422 | 0,563 |
| REGLAMENTA | 0,615 | 0,615 | 1,000 | 0,762 |
| MODIFICA | 0,308 | 0,308 | 0,131 | 0,184 |
| CITA | 0,769 | 0,769 | 0,876 | 0,819 |
| **Macro-F1** | 0,700 (muestra) | | | **0,672** |
| **Exactitud** | 0,679 (muestra) | | | **0,754** |

- **Artículo destino correcto:** 67 de 78 casos (0,859).
- **El recall ponderado de `DEROGA` (0,42) tiene mucha varianza.** Sale de un solo caso predicho como `CITA` que era una derogación, y ese caso pesa como 179 relaciones. Con 13 casos por estrato, los recall poblacionales son orientativos.

### Errores típicos

1. **La mayoría de los errores son citas tomadas como acción** (21 de 25; otros 3 son acciones tomadas como cita y 1 es una sustitución tipada como `MODIFICA`). El verbo que decide el tipo está en la oración, pero no actúa sobre la norma mencionada. Ejemplos:
   - «Impuesto al Valor **Agregado**»: se lee como el verbo de `INCORPORA` (4 casos);
   - «**texto ordenado** en 1997» dentro de una remisión se lee como `MODIFICA`;
   - «la Ley 25.877 y su **reglamentación**» se lee como `REGLAMENTA`.
2. **El encabezado se tipa entero como `CITA`.** El sumario de una ley («Modifícase el artículo 12 de la Ley Nº 20.744») es una modificación.
3. **Artículo destino:** en «Apruébase la reglamentación de la Ley …» y «Apruébase el texto ordenado …», se toma como destino el número del artículo de la propia norma origen («Artículo 1°»). En «Incorpóranse los artículos 13 bis y 13 ter a la ley», no se extrae el artículo.

Estos errores están documentados y no se corrigen sobre esta muestra: corregirlos mirando los casos que después se usan para medir inflaría el resultado. Quedan como mejoras del tipado, para diseñar sobre otra muestra de dev. Si existe la salida del parser LLM, el script la evalúa sobre los mismos 78 casos (bitácora B48).

*Fuente: `results/tipos/RESULTADOS.md`.*

## Parser LLM

El parser LLM (`src/grafo_legal/extractores/llm.py`) cumple el mismo contrato que el parser de reglas: recibe los segmentos del adaptador y devuelve relaciones en la salida estándar (`docs/salida_estandar.md`). Lo único que cambia es quién lee el texto. En las reglas son expresiones regulares; acá es un modelo de lenguaje grande. Así los dos parsers se comparan con la misma evaluación y alimentan el mismo modelo de grafo (bitácora B48).

### Cómo funciona

```
segmentos del adaptador ──► 1 prefiltro ──► 2 lotes ──► 3 LLM (JSON) ──► 4 verificación de la cita
                                                                              │
                         salida estándar (fuente = llm) ◄── 5 normalización ◄─┘
                                       (mismo catálogo que las reglas)
```

1. **Prefiltro, sin LLM.** Solo se mandan los segmentos del encabezado y del articulado que contienen alguna palabra que pueda introducir una norma: ley, decreto, DNU, código, régimen o estatuto. Un artículo que no nombra ninguna norma no puede tener una relación con otra. Las notas de InfoLEG y los anexos no se mandan, igual que en las reglas.
2. **Lotes.** Los segmentos de una norma se agrupan en lotes de hasta 12.000 caracteres. Cada uno lleva su identificador (`[S12] Artículo 11`) para que el LLM diga de qué artículo sale cada relación. Un artículo más largo se parte en pedazos, y cada pedazo recuerda su desplazamiento.
3. **Prompt.** El modelo recibe la definición de los seis tipos, con ejemplos de técnica legislativa argentina, y devuelve un JSON con una entrada por relación:
   - segmento;
   - cita textual exacta;
   - tipo, número y año de la norma destino;
   - artículo destino;
   - tipo de relación;
   - verbo.

   Se usa temperatura 0. El prompt está en `llm.SISTEMA` y su versión en `llm.VERSION_PROMPT`.
4. **Verificación de la cita (anti-alucinación).** La cita que devuelve el LLM se busca en el texto del segmento. Si aparece, se guardan sus offsets en el texto limpio de la norma, y la relación queda trazable a su evidencia igual que en las reglas. Si no aparece, la relación se descarta y se cuenta: la tasa de citas que no están en el texto es una medida de alucinación.
5. **Normalización.** El tipo, el número y el año que da el LLM se resuelven contra el mismo catálogo que usan las reglas (`catalogo.py`, mundo cerrado). Así la comparación entre parsers mide solo la lectura del texto, no la normalización.
6. **Caché.** Cada respuesta se guarda en `results/relaciones_llm/cache/`, con nombre igual a la huella SHA-256 del pedido (modelo, versión del prompt, prompt y texto). La caché va en el repositorio. Volver a correr no llama a la API y da exactamente lo mismo, así que el experimento es reproducible sin la clave y sin costo.

El LLM nunca ve el gold de InfoLEG. El gold lo lee solo `scripts/15_evaluar_llm.py`.

### Modelo y costo

| | Valor |
|---|---|
| Modelo por defecto | `claude-sonnet-5-5` (se cambia con `--modelo`) |
| Normas | 306 |
| Lotes (pedidos a la API) | 590 |
| Entrada estimada | ~1,8 millones de tokens (`--estimar`) |
| Costo estimado con Sonnet 5.5 ($2 / $10 por millón de tokens de entrada / salida) | unos USD 8 |
| Costo estimado con Haiku 5.5 ($0,10 / $0,50) | menos de USD 0,50 |

### Cómo se corre

```bash
cd "/Users/jptmac/Documents/grafo legal"
echo "TU_API_KEY" > .anthropic_key          # está en .gitignore: no se sube nunca
export ANTHROPIC_API_KEY=$(cat .anthropic_key)
python scripts/14_parser_llm.py --estimar   # cuenta lotes y tokens, no llama a la API
python scripts/14_parser_llm.py --limite 5  # piloto con 5 normas
python scripts/14_parser_llm.py             # todo el corpus
python scripts/15_evaluar_llm.py            # contra InfoLEG, mismo protocolo que las reglas
python scripts/16_evaluar_tipos.py          # tipos, sobre los 78 casos revisados
python scripts/10_armar_grafo.py --relaciones results/relaciones_llm/relaciones_llm.csv --out data/grafo_llm
```

### Evaluación

- **Contra InfoLEG (`15_evaluar_llm.py`).** Las relaciones del LLM se proyectan a pares de normas y se comparan con el gold, igual que las reglas. Se prueban cuatro proyecciones y se elige una en dev:
  - cualquier relación que no sea `CITA`;
  - lo anterior más cualquier mención del VISTO;
  - la regla F aplicada a las relaciones del LLM;
  - todas las relaciones.

  En todas se aplica la misma restricción temporal de las reglas. Con la proyección elegida se arman dos híbridos con las reglas: la unión (más recall) y la intersección (más precisión).
- **Tipos (`16_evaluar_tipos.py`).** Sobre los mismos 78 casos revisados a mano que las reglas.
- **Tabla final (`17_comparar_metodos.py`).** Todos los métodos sobre el mismo test, con intervalos de confianza por bootstrap.

### Grafo del LLM

El grafo del LLM no reemplaza al de las reglas. Sus CSV van a `data/grafo_llm/`; los de las reglas siguen en `data/grafo/`.

En Neo4j, las aristas se identifican por tipo y por `fuente`. Cargar el LLM **sin** `--borrar` agrega sus aristas (`fuente = 'llm'`) a los mismos nodos `Norma` y `Articulo`, sin tocar las de `reglas_v2`:

```bash
export NEO4J_PASSWORD=$(cat .neo4j_password)
python scripts/10_armar_grafo.py --relaciones results/relaciones_llm/relaciones_llm.csv \
    --out data/grafo_llm --uri bolt://localhost:7688      # SIN --borrar
python scripts/11_evaluar_grafo.py --relaciones results/relaciones_llm/relaciones_llm.csv \
    --fuente llm --out results/evaluacion_grafo_llm --uri bolt://localhost:7688
```

Así, en la demo se pueden comparar las dos lecturas del mismo artículo:

```cypher
MATCH (o:Articulo)-[r]->(d) WHERE o.id = '395521#71'
RETURN r.fuente, type(r), d.id, r.fragmento
```

*Fuente: `docs/parser_llm.md`.*

## Guía de lectura del código (para la presentación)

Este documento recorre el código en el orden en que viaja un documento: del HTML de InfoLEG hasta la arista del grafo y su evaluación. Cada paso dice qué archivo y qué función abrir, y qué mostrar. Todos los módulos tienen comentarios que explican cada expresión regular y cada decisión. El ejemplo de punta a punta es el artículo 70 del Decreto 70/2023, que sustituye el artículo 80 de la LCT (Ley 20.744).

### Mapa

```
                      ┌──────────── específico de la fuente ────────────┐
HTML de InfoLEG ──► fuentes/infoleg.py  html_a_texto() ──► segmentar()
                      └──────────────────────────────────────────────────┘
                                       │ texto limpio + segmentos (encabezado, artículos, anexo, notas)
             ┌─────────────────────────┴─────────────────────────┐
     PARSER DE REGLAS                                       PARSER LLM
  extractores/menciones.py  detectar(), detectar_alias()  extractores/llm.py  seleccionar(), lotes()
  catalogo.py               Catalogo.resolver()           ClienteLLM.pedir()  (API + caché)
  extractores/reglas_v2.py  extraer(), CONFIGS["F_…"]     a_relaciones()      (verifica la cita,
  extractores/relaciones.py desde_evidencias()                                 normaliza con catalogo.py)
             └─────────────────────────┬─────────────────────────┘
                                       │ salida estándar (salida.py): una fila por relación tipada
                                       ▼
                      grafo.py  construir() ──► cargar_neo4j()  /  a_networkx()
                                       │
                                       ▼
              evaluación: 04 (pares), 11 (grafo), 12 (subtareas), 13 (modelo), 15 (LLM), 16 (tipos), 17 (tabla final)
```

### Paso a paso

#### 1. Del HTML al texto limpio

- **Archivo y función:** `src/grafo_legal/fuentes/infoleg.py`, `html_a_texto()`.
- **Qué hace:**
  - borra scripts, estilos y comentarios;
  - convierte las etiquetas de bloque (`<p>`, `<br>`, `<tr>`) en saltos de línea;
  - decodifica las entidades (`&aacute;` → «á»);
  - normaliza los espacios.
- **Por qué importa:** todos los offsets (`inicio`, `fin`) que guardan las evidencias, las relaciones y el grafo se cuentan sobre este texto. Es lo que permite volver de una arista al fragmento exacto.
- **Para mostrar:** es el único archivo que depende de InfoLEG. Para el digesto de la UNNOBA se escribe otro adaptador que devuelva la misma lista de `Articulo`.

#### 2. Segmentación

- **Archivo y función:** `infoleg.py`, `segmentar()`.
- **Qué hace:** corta el texto en zonas.
  - El **encabezado** es todo lo anterior al primer artículo: título, VISTO y CONSIDERANDO.
  - Cada **artículo** del articulado va desde su marca («ARTÍCULO 70.-», «Art. 2º —») hasta la siguiente. Lo detecta la expresión regular `_ART`, explicada pieza por pieza en el código.
  - El **anexo** empieza en el primer renglón «ANEXO» posterior al articulado.
  - Las **notas** de InfoLEG empiezan en «Nota Infoleg:» o «Antecedentes:».
- **Por qué importa:** la zona es la señal más fuerte de las reglas. Un par citado en el VISTO está en InfoLEG el 80 % de las veces; uno citado solo en el CONSIDERANDO, el 24 %.

#### 3. Detección de menciones

- **Archivo y funciones:** `src/grafo_legal/extractores/menciones.py`, `detectar()` y `detectar_alias()`.
- **Qué hace:**
  - `detectar()` arma el patrón TIPO + NOMBRE opcional + «N°» opcional + LISTA de números. Reconoce, por ejemplo:
    - «Decreto de Necesidad y Urgencia N° 70/23»;
    - «Ley de Contrato de Trabajo Nº 20.744»;
    - «Leyes Nros. 24.013, 24.465 y 24.467», que da tres menciones.
  - `detectar_alias()` encuentra nombres propios sin número («Ley de Contrato de Trabajo»), con un gazetteer.
- **Resultado medido** (`results/subtareas`): cuando el número de la norma destino está en el texto, el detector lo encuentra siempre. Pierde 2 pares de dev por nombres que el gazetteer no tiene («Ley de Ministerios», «L.C.T.»). La precisión es 0,97 en una muestra de 60: los 2 errores son nombres de tributos tomados como alias.

#### 4. Normalización

- **Archivo y función:** `src/grafo_legal/catalogo.py`, `Catalogo.resolver()`.
- **Qué hace:** de («decreto», «1694», 2006) a un `id_norma`. Las leyes tienen número único. Los decretos se renumeran cada año, así que el año desempata: si falta y hay más de un candidato, no se resuelve.
- **Mundo cerrado:** el catálogo es el corpus. Una mención que no resuelve se conserva como evidencia, pero no genera arista.
- **Resultado medido:**
  - el 48 % de las menciones nombra normas reales fuera del corpus;
  - de las que se resuelven, el 95,9 % es inequívoco también contra todo InfoLEG, y la exactitud estimada es 99,1 %;
      - el error principal: el año del decreto escrito como fecha («Decreto N° 467 del 14 de abril de 1988») no se lee, así que la mención queda ambigua o se vincula a otro decreto con el mismo número.

#### 5. Reglas: de mención a evidencia y de evidencia a par

- **Archivo:** `src/grafo_legal/extractores/reglas_v2.py`.
- **`extraer()`:** produce una evidencia por mención resuelta, con lo que la regla necesita para decidir:
  - parte del documento (visto, considerando o articulado);
  - verbo en la oración (expresión regular `VERBOS` de `reglas.py`);
  - restricción temporal (el destino no puede ser posterior al origen);
  - si es una cita de procedencia («t.o. por Decreto 390/76»).
- **`CONFIGS["F_visto_o_articulado_con_verbo_o_ley"]`:** la decisión. Hay vínculo si la mención está en el VISTO, o en el articulado con número cuando el origen es una ley o la oración tiene verbo.
- **Ejemplo:** en «ARTÍCULO 70.- Sustitúyese el artículo 80 de la Ley N° 20.744», la mención es «Ley N° 20.744» (ley 20744 → `id` 25552), está en el articulado, el verbo de la oración es «Sustitúyese» y la ley es de 1974, anterior al decreto. Pasa la regla F.

#### 6. Relaciones tipadas: la salida estándar

- **Archivos:** `src/grafo_legal/extractores/relaciones.py` (`desde_evidencias()`) y `src/grafo_legal/salida.py`.
- **Qué hace `desde_evidencias()`, por cada evidencia:**
  - asigna el segmento que la contiene (`merge_asof`), que es el `id_articulo_origen`;
  - tipa con `tipo_por_verbo()`: «Sustitúyese» → `SUSTITUYE`; sin verbo o en el encabezado → `CITA`;
  - busca el artículo destino con `articulos_destino()`, en el «artículo N de la» que precede a la mención;
  - agrupa las menciones con la misma clave.
- **El contrato:** `salida.py` define las columnas y la clave `(fuente, id_articulo_origen, tipo, id_norma_destino, articulo_destino)`. Cualquier parser que escriba esta tabla entra al grafo sin cambiar nada más.
- **Ejemplo:** `reglas_v2, 395521#71, SUSTITUYE, 25552, "80", verbo "Sustitúyese", fragmento "ARTÍCULO 70.- Sustitúyese el artículo 80 de la Ley N° 20.744…"`.

#### 7. Parser LLM

- **Archivo:** `src/grafo_legal/extractores/llm.py`; se explica entero en `docs/parser_llm.md`.
- **Para mostrar:**
  - `SISTEMA`, el prompt con la definición de los seis tipos;
  - `a_relaciones()`, que verifica que la cita que devuelve el LLM esté en el texto (si no está, se descarta) y la normaliza con el mismo `Catalogo.resolver()`;
  - la caché, que hace el experimento reproducible sin clave.

#### 8. El grafo

- **Archivo y función:** `src/grafo_legal/grafo.py`, `construir()`.
- **Nodos:** `Norma`, uno por norma del corpus, y `Articulo`, uno por segmento, con id `id_norma#orden`.
- **Aristas:** `CONTIENE` de cada norma a sus artículos, más las relaciones tipadas.
- **Destino de cada relación:**
  - si la relación dice el artículo destino, va al nodo de ese artículo;
  - si no, va a la norma entera;
  - si el artículo destino no tiene texto, se crea un nodo «stub» sin texto.
- **Carga:** `cargar_neo4j()` carga con `MERGE`, así que cargar dos veces no duplica. Cada arista lleva su `fuente`, y por eso el grafo del LLM se agrega sin pisar el de las reglas.
- **Ejemplo:** `(Decreto 70 art. 70)-[:SUSTITUYE {fragmento…}]->(Ley 20.744 art. 80)`.

#### 9. Evaluación

| Script | Qué mide |
|---|---|
| `04_evaluar.py` | P, R y F1 por par contra InfoLEG, por configuración y por split |
| `11_evaluar_grafo.py` | Ida y vuelta (el grafo devuelve lo cargado) y comparación con InfoLEG leyendo el grafo |
| `12_evaluar_subtareas.py` | Detección, normalización y extracción por separado; embudo; taxonomía de errores |
| `13_modelo_contextual.py` | Modelo con contexto textual (TF-IDF) e híbrido reglas + modelo |
| `15_evaluar_llm.py` | Parser LLM contra InfoLEG e híbridos reglas + LLM |
| `16_evaluar_tipos.py` | Tipo de relación: matriz de confusión y macro-F1 sobre 78 casos revisados |
| `17_comparar_metodos.py` | Tabla final de todos los métodos en test, con intervalos de confianza por bootstrap |

Cómo se compara con el gold: `docs/comparacion_con_el_gold.md`.

*Fuente: `docs/guia_codigo.md`.*
