# Evaluación por subtareas: detección, normalización y extracción

`scripts/12_evaluar_subtareas.py` mide por separado los tres eslabones del parser de reglas v2, como pide la consigna, y clasifica los errores con las categorías de la consigna (bitácora B45). El gold se usa solo para medir.

## Cómo se mide cada subtarea

| Subtarea | Pregunta | Referencia |
|---|---|---|
| Detección | ¿El detector encontró la mención a la norma destino? | Una búsqueda laxa, independiente del detector: el número de la norma destino («20.744» o «20744») como número suelto, o uno de sus nombres propios. Si aparece y el detector no lo vio, es un fallo de detección. Para la precisión, una muestra de 60 menciones revisada a mano (`docs/revision_manual/revision_deteccion_60.csv`). |
| Normalización | ¿La mención se vinculó a la norma correcta? | Cada mención se resuelve contra el catálogo del corpus (el que usa el parser) y contra el catálogo completo de InfoLEG: 106.466 leyes, decretos y decretos-leyes. |
| Extracción | Con la mención detectada y normalizada, ¿la regla decide bien si hay relación? | El gold, sobre los pares candidatos: así se aísla la decisión de las reglas de los pasos anteriores. |

## 1. Detección

| | dev | test |
|---|---|---|
| Pares del gold con texto | 548 | 192 |
| … cuyo destino aparece en el texto (búsqueda laxa) | 473 | 185 |
| … y el detector lo encontró | 473 | 185 |
| **Recall de detección** | **1,000** | **1,000** |

Cuando el número de la norma destino está en el texto, el detector siempre lo encuentra. Los pares que se pierden (75 en dev, 7 en test) no nombran la norma destino en ninguna forma: son relaciones implícitas o hechas por otra norma intermedia, y ningún extractor que lea el texto puede recuperarlas.

**Precisión de detección:** de 60 menciones al azar, 58 son citas inequívocas a una norma. Las otras 2 son nombres de tributos tomados como alias de la ley («Impuesto al Valor Agregado», «impuesto a las ganancias»). Precisión: 0,97. La revisión es de Claude y está pendiente de validación humana.

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
- **Exactitud de vinculación verificable:** 95,9 % (dev 95,5 %, test 96,8 %). De las menciones que el parser vincula, esa proporción es inequívoca también contra todo InfoLEG. El 4,1 % restante son decretos citados sin año que el parser vincula porque el corpus tiene uno solo con ese número. Pueden estar bien o mal: es la cota de error de la decisión de mundo cerrado.

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
| 3. Con mención explícita del destino en el texto | 473 | 185 |
| 4. Detectados | 473 | 185 |
| 5. Normalizados a la norma correcta | 472 | 185 |
| 6. Extraídos por la regla F | 418 | 168 |

En test, de los 24 pares perdidos, 7 no tienen mención en el texto (paso 3) y 17 los descarta la regla (paso 6). La detección y la normalización no pierden ninguno.

## Taxonomía de errores (categorías de la consigna)

| Categoría | Qué es | dev | test |
|---|---|---|---|
| **Falsos negativos** | | | |
| Norma no detectada | El destino aparece en el texto y el detector no lo vio | 0 | 0 |
| Norma mal normalizada | Se detectó el número pero se vinculó a otra norma o a ninguna | 1 | 0 |
| Relación descartada por la regla | Detectada y normalizada, la regla F dijo que no | 54 | 17 |
| Sin mención explícita | El texto no nombra la norma destino | 75 | 7 |
| Sin texto (fuera de alcance) | InfoLEG no publica el texto de la modificatoria | 35 | 0 |
| **Falsos positivos** | | | |
| Relación inexistente | La norma se cita, pero InfoLEG no registra el vínculo | 119 | 38 |
| Referencia ambigua | Decreto sin año resuelto por mundo cerrado, o solo un nombre propio («impuesto a las ganancias») | 20 | 8 |
| Relación invertida | El gold tiene el par al revés | 0 | 0 |
| **Otras** | | | |
| Destino ausente del corpus | Pares que la regla F extraería si el destino estuviera en el catálogo | 886 | 203 |
| Tipo incorrecto | Ver `results/tipos/RESULTADOS.md` | 25 de 78 en la muestra | |

- **No hay relaciones invertidas.** La restricción temporal (una norma no puede modificar a otra posterior) las elimina.
- **Los destinos fuera del corpus no son ruido.** Contra la base complementaria completa de InfoLEG, el 54 % de esos pares en dev y el 62 % en test son vínculos registrados. El parser generaliza fuera del corpus con una precisión unos 20 puntos menor que dentro. La diferencia se explica porque normas de alcance amplio, como la Ley 23.697 de Emergencia Económica, citan muchas leyes que no modifican.

## Archivos

- `metricas.json`: todas las cifras de este documento.
- `menciones.csv`: las 8.915 menciones, con su estado de normalización y la cantidad de candidatas en InfoLEG.
- `errores.csv`: cada falso negativo y falso positivo de la configuración F con su categoría.
- `deteccion_fallos.csv`: pares en los que el número aparece y el detector no lo vio (vacío).
