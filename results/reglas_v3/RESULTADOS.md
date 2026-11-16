# Reglas v3: resultados

`src/grafo_legal/extractores/reglas_v3.py` corrige los fallos que encontró el análisis caso por caso de la v2 (bitácora B51 y B52). Se diseñó solo mirando dev; después se congeló y test se evaluó una vez, el 16/11/2026. Las huellas SHA-256 de lo congelado son:

- `reglas_v3.py`: `519c7586…`
- `menciones.py`: `62e79044…`
- `relaciones.py`: `d8297ce9…`

La v2 sigue congelada y reproducible: los cambios de la v3 se activan con parámetros que la v2 no usa, y las salidas de la v2 dieron idénticas byte a byte.

## Qué cambia y qué fallo corrige

| # | Cambio | Fallo que corrige | Eslabón |
|---|---|---|---|
| 1 | El detector lee el año escrito como fecha: «Decreto N° 1694 del 22 de noviembre de 2006», «… de fecha 23 de enero de 2014», «… 658 y 659, ambos del 24 de junio de 1996», «… del 13/03/2001». | Decretos sin «/año» que quedaban sin resolver o se vinculaban a otro decreto con el mismo número. | Normalización |
| 2 | Gazetteer: se agregan «Ley de Ministerios» y «L.C.T.»; se sacan los nombres de tributos sueltos («impuesto a las ganancias», «impuesto al valor agregado»), y quedan las formas con «Ley». | Normas nombradas sin número que no se detectaban; tributos tomados como citas a su ley. | Detección |
| 3 | «Agregado» precedido de «Valor» no es un verbo. | «Impuesto al Valor Agregado» leído como verbo de incorporación. | Extracción y tipo |
| 4 | Procedencia extendida: «modificado por el Decreto», «reemplazado por el artículo N de la ley», «ampliado y modificado por ley». | Citas que indican de dónde viene un texto, contadas como relación. | Extracción |
| 5 | Regla F3: en el articulado, una norma nombrada sin número también cuenta si la oración tiene un verbo modificatorio. | «Modifícase la Ley de Impuesto a las Ganancias», sin número, que la regla F descartaba. | Extracción |
| 6 | El número del propio artículo origen («Artículo 1° — Apruébase la reglamentación de la Ley …») ya no se toma como artículo destino. | Artículo destino equivocado. | Tipado |

## Ablación sobre dev (`ablacion_dev.csv`, script 19)

| Variante | P | R | F1 |
|---|---|---|---|
| v2 (ningún cambio) | 0,750 | 0,717 | 0,733 |
| v2 + año escrito como fecha | 0,764 | 0,732 | 0,748 |
| v2 + gazetteer | 0,747 | 0,715 | 0,731 |
| v2 + «Valor Agregado» | 0,750 | 0,717 | 0,733 |
| v2 + procedencia | 0,754 | 0,715 | 0,734 |
| v2 + alias con verbo | 0,734 | 0,726 | 0,730 |
| **v3 completa** | **0,761** | **0,739** | **0,750** |
| v3 sin año escrito como fecha | 0,748 | 0,724 | 0,736 |
| v3 sin gazetteer | 0,759 | 0,739 | 0,749 |
| v3 sin procedencia | 0,758 | 0,741 | 0,749 |
| v3 sin «Valor Agregado» | 0,760 | 0,739 | 0,750 |
| v3 sin alias con verbo | 0,764 | 0,727 | 0,745 |

- **El año escrito como fecha es el cambio que más aporta** (+1,5 puntos solo).
- **El alias con verbo solo funciona junto con el gazetteer.** Sobre la v2 baja el F1, porque los nombres de tributos sueltos siguen ahí y generan falsos positivos. Con el gazetteer limpio, suma medio punto.

## Test (evaluado una vez)

| | P | R | F1 | F1 sin pares del v1 |
|---|---|---|---|---|
| Reglas v2, F | 0,785 | 0,875 | 0,828 | 0,671 |
| **Reglas v3, F3** | 0,779 | 0,880 | **0,826** | 0,671 |

Diferencia con la v2: −0,1 puntos, intervalo del 95 % entre −1,9 y +1,3 (bootstrap por norma origen, `results/comparacion/`). **En test, la v3 no mejora a la v2.** Las dos versiones difieren en 9 pares:

- **Gana 3 relaciones del gold:**
  - Decreto 342/24 → Decreto 467/88, por el año escrito como fecha;
  - Ley 27.802 → Ley de IVA y Ley de Ganancias, por el alias con verbo.
- **Elimina 1 falso positivo:** DNU 70/2023 → Decreto 267, que era otro decreto con el mismo número.
- **Agrega 3 falsos positivos:** Ley 27.742 → IVA y Decreto 242 → IVA y Ganancias. Son leyes nombradas con un verbo en la oración que no actúa sobre ellas.
- **Pierde 2 relaciones del gold:** Ley 27.742 y Ley 27.802 → Ley 24.674. El filtro de procedencia nuevo toma «Ley de Impuestos Internos, texto sustituido por la ley 24.674» como procedencia, y ahí «sustituido por» nombra la ley que se está modificando. Es una regresión del cambio 4. En dev no apareció porque esa forma no está en dev.

## Por subtareas (`results/subtareas_v3/`)

| | v2 | v3 |
|---|---|---|
| Menciones ambiguas (decreto sin año, varias candidatas) | 580 | 251 |
| Resueltas solo por mundo cerrado | 147 | 31 |
| … de ellas, otro decreto con el mismo número | 31 | 0 |
| Exactitud de vinculación estimada | 99,1 % | 100 % de las verificables |
| Pares del gold perdidos en la normalización (dev / test) | 9 / 1 | 0 / 0 |
| Falsos positivos por mala normalización (dev / test) | 8 / 1 | 0 / 0 |

**La normalización quedó resuelta:** ningún par del gold se pierde ahí y ninguna vinculación verificable es errónea. Lo que queda es la decisión de la regla: las citas del VISTO y las remisiones que InfoLEG no registra.

## Tipo de relación (`results/tipos/`)

Sobre los mismos 78 casos revisados:

| | v2 | v3 |
|---|---|---|
| Macro-F1 ponderada | 0,672 | 0,703 |
| Exactitud ponderada | 0,754 | 0,755 |

La medida de la v3 es **optimista**: las correcciones 3 y 6 salieron de errores vistos en esta misma muestra. Para medirlas sin sesgo hace falta una muestra nueva.

## Problemas conocidos de la v3, para una v4 diseñada sobre dev

- «texto sustituido por la ley N» no es procedencia: hay que sacarlo del filtro.
- La entrada «l.c.t.» del gazetteer no se encuentra, porque el punto final impide el límite de palabra: hay que escribirla «l.c.t».
- Sacar «impuesto a las ganancias» del gazetteer hizo perder una relación de dev (Ley 25.561 → Ley 20.628).
- «Inclúyense» no está en la lista de verbos, así que «Inclúyense como incisos … de la Ley de Ministerios» no cuenta como modificación.

## Grafo de la v3

Está en `data/grafo_v3/` y no reemplaza al de la v2 (`data/grafo/`). Tiene 3.149 relaciones; la ida y vuelta es idéntica (`results/evaluacion_grafo_v3/`). En Neo4j se carga sin `--borrar`, con `fuente = 'reglas_v3'`.
