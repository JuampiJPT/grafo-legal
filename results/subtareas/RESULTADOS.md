# Evaluación por subtareas: detección, normalización y extracción

`scripts/12_evaluar_subtareas.py` mide por separado los tres eslabones del parser de reglas v2, como pide la consigna, y clasifica los errores con las categorías de la consigna (bitácora B45). El gold se usa solo para medir.

## Cómo se mide cada subtarea

| Subtarea | Pregunta | Referencia |
|---|---|---|
| Detección | ¿El detector encontró la mención a la norma destino? | Una búsqueda laxa, independiente del detector: el número de la norma destino («20.744» o «20744») como número suelto, sus nombres propios del gazetteer o nombres que el gazetteer no tiene («Ley de Ministerios», «L.C.T.»). Si aparece y el detector no lo vio, es un fallo de detección. Para la precisión, una muestra de 60 menciones revisada a mano (`docs/revision_manual/revision_deteccion_60.csv`). |
| Normalización | ¿La mención se vinculó a la norma correcta? | Cada mención se resuelve contra el catálogo del corpus (el que usa el parser) y contra el catálogo completo de InfoLEG: 106.466 leyes, decretos y decretos-leyes. Si el texto escribe el año como fecha después de la mención («Decreto 84 del 23 de enero de 2014»), ese año confirma o contradice la vinculación. |
| Extracción | Con la mención detectada y normalizada, ¿la regla decide bien si hay relación? | El gold, sobre los pares candidatos: así se aísla la decisión de las reglas de los pasos anteriores. |

## 1. Detección

| | dev | test |
|---|---|---|
| Pares del gold con texto | 548 | 192 |
| … cuyo destino aparece en el texto (búsqueda laxa) | 475 | 185 |
| … y el detector lo encontró | 473 | 185 |
| **Recall de detección** | **0,996** | **1,000** |

Cuando el número de la norma destino está en el texto, el detector siempre lo encuentra. Los 2 fallos de dev son nombres que el gazetteer no tiene: «Ley de Ministerios» y «L.C.T.». Los pares que no nombran la norma destino en ninguna forma (73 en dev, 7 en test) no se pueden recuperar leyendo el texto; por qué los registra InfoLEG está en `results/errores_explicados/RESULTADOS.md`.

**Precisión de detección:** de 60 menciones al azar, 58 son citas inequívocas a una norma. Las otras 2 son nombres de tributos tomados como alias de la ley («Impuesto al Valor Agregado», «impuesto a las ganancias»): en «Exención del Impuesto a las Ganancias» el texto habla del tributo, no cita la ley. Precisión: 0,97. La revisión es de Claude y está pendiente de validación humana.

## 2. Normalización

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

## 3. Extracción

| | P | R | F1 |
|---|---|---|---|
| dev, de punta a punta (contra todo el gold) | 0,750 | 0,717 | 0,733 |
| dev, condicional a los candidatos | 0,750 | 0,886 | 0,812 |
| test, de punta a punta | 0,785 | 0,875 | 0,828 |
| test, condicional a los candidatos | 0,785 | 0,908 | **0,842** |

La regla F, sola, recupera el 91 % de los pares de test que ya pasaron detección y normalización. La diferencia entre las dos filas es el techo que ponen los pasos anteriores.

## Embudo: dónde se pierde cada par del gold

| Paso | dev | test |
|---|---|---|
| 1. Pares del gold | 583 | 192 |
| 2. Con texto en InfoLEG | 548 | 192 |
| 3. Con mención explícita del destino en el texto | 475 | 185 |
| 4. Detectados | 473 | 185 |
| 5. Normalizados a la norma correcta | 464 | 184 |
| 6. Extraídos por la regla F | 418 | 168 |

En test se pierden 24 pares: 7 no tienen mención en el texto (paso 3), 1 no se normaliza porque el año del decreto está escrito como fecha (paso 5) y 16 los descarta la regla (paso 6). En dev, la detección pierde 2 y la normalización 9.

## Taxonomía de errores (categorías de la consigna)

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

## Archivos

- `metricas.json`: todas las cifras de este documento.
- `menciones.csv`: las 8.915 menciones, con su estado de normalización y la cantidad de candidatas en InfoLEG.
- `errores.csv`: cada falso negativo y falso positivo de la configuración F con su categoría.
- `deteccion_fallos.csv`: pares en los que el número aparece y el detector no lo vio (vacío).
