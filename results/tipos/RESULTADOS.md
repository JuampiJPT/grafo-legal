# Tipo de relación: matriz de confusión y macro-F1

`scripts/16_evaluar_tipos.py` evalúa el tipo de relación (`SUSTITUYE`, `INCORPORA`, `DEROGA`, `REGLAMENTA`, `MODIFICA`, `CITA`) y el artículo destino contra la revisión manual (bitácora B47). InfoLEG no registra el tipo, así que esta es la única medida posible.

## Muestra

La muestra tiene 78 relaciones del parser de reglas v2 (`docs/revision_manual/revision_tipos_78.csv`), 13 por cada tipo predicho:

- los 36 casos revisados en B43;
- 42 nuevos, sorteados con la semilla 20261116.

La revisión es de Claude y está pendiente de validación humana. Que un segundo anotador repita una parte da el kappa.

Como la muestra está estratificada por el tipo predicho, cada caso representa a una cantidad distinta de relaciones: uno de `CITA` representa a 179 (2.332 / 13) y uno de `REGLAMENTA` a 4,5 (58 / 13). Por eso se reportan dos cosas:

- la matriz de confusión de la muestra, en conteos;
- las métricas de la población, con cada caso ponderado por la inversa de su probabilidad de muestreo.

## Matriz de confusión de las reglas v2 (filas: predicho; columnas: correcto)

| predicho \ correcto | CITA | DEROGA | INCORPORA | MODIFICA | REGLAMENTA | SUSTITUYE |
|---|---|---|---|---|---|---|
| **CITA** | **10** | 1 | 0 | 2 | 0 | 0 |
| **DEROGA** | 2 | **11** | 0 | 0 | 0 | 0 |
| **INCORPORA** | 5 | 0 | **8** | 0 | 0 | 0 |
| **MODIFICA** | 8 | 0 | 0 | **4** | 0 | 1 |
| **REGLAMENTA** | 5 | 0 | 0 | 0 | **8** | 0 |
| **SUSTITUYE** | 1 | 0 | 0 | 0 | 0 | **12** |

## Métricas

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

## Errores típicos

1. **La mayoría de los errores son citas tomadas como acción** (21 de 25; otros 3 son acciones tomadas como cita y 1 es una sustitución tipada como `MODIFICA`). El verbo que decide el tipo está en la oración, pero no actúa sobre la norma mencionada. Ejemplos:
   - «Impuesto al Valor **Agregado**»: se lee como el verbo de `INCORPORA` (4 casos);
   - «**texto ordenado** en 1997» dentro de una remisión se lee como `MODIFICA`;
   - «la Ley 25.877 y su **reglamentación**» se lee como `REGLAMENTA`.
2. **El encabezado se tipa entero como `CITA`.** El sumario de una ley («Modifícase el artículo 12 de la Ley Nº 20.744») es una modificación.
3. **Artículo destino:** en «Apruébase la reglamentación de la Ley …» y «Apruébase el texto ordenado …», se toma como destino el número del artículo de la propia norma origen («Artículo 1°»). En «Incorpóranse los artículos 13 bis y 13 ter a la ley», no se extrae el artículo.

Estos errores están documentados y no se corrigen sobre esta muestra: corregirlos mirando los casos que después se usan para medir inflaría el resultado. Quedan como mejoras del tipado, para diseñar sobre otra muestra de dev. Si existe la salida del parser LLM, el script la evalúa sobre los mismos 78 casos (bitácora B48).
