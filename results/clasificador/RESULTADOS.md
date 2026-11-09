# Clasificador sobre los pares candidatos: resultados

`scripts/08_clasificador.py` entrena un clasificador sobre `data/dataset/pares_candidatos.csv`. El clasificador decide si un par (norma origen → norma destino) propuesto por el detector de menciones es una relación de InfoLEG. Sirve como punto de comparación estadístico para los parsers de reglas, LLM e híbrido (bitácora B37).

## Protocolo

- **Selección.** Validación cruzada de 5 particiones sobre dev, agrupada por norma origen: los pares de una misma norma no quedan repartidos entre entrenamiento y validación. Se probaron tres modelos y, para cada uno, umbrales de 0,20 a 0,80.
- **Modelo final.** El elegido se entrena con todo dev. Test se evaluó una vez, el 09/11/2026.
- **Métricas.** Se miden contra todo el gold del split. Un par del gold que no es candidato cuenta como falso negativo, igual que en las reglas.

## Validación cruzada en dev

| Modelo | Umbral | P | R | F1 | F1 con umbral 0,5 |
|---|---|---|---|---|---|
| Regresión logística | 0,35 | 0,709 | 0,727 | 0,718 | 0,692 |
| **Random forest** | **0,45** | **0,766** | **0,695** | **0,728** | 0,703 |
| Gradient boosting | 0,20 | 0,692 | 0,727 | 0,709 | 0,690 |

## Test

| | P | R | F1 | F1 sin pares del v1 |
|---|---|---|---|---|
| Random forest, umbral 0,45 | 0,799 | 0,849 | 0,823 | 0,683 |
| Reglas v2, configuración F | 0,785 | 0,875 | 0,828 | 0,671 |
| Reglas v1, configuración C | 0,732 | 0,854 | 0,788 | 0,563 |

## Lectura

1. **El clasificador empata con las reglas v2.** En test, la diferencia de F1 es de medio punto, y con 192 pares no es distinguible. Con los mismos atributos de superficie (dónde está la mención, cuántas veces aparece, si hay un verbo), un modelo entrenado no encuentra mucho más que las reglas escritas a mano.
2. **Los atributos que más pesan** son la posición de la primera mención, la fracción de artículos que mencionan al destino, el largo del texto, la diferencia de años y la cantidad de menciones (`importancia.csv`). Varios describen la norma más que la mención, así que pueden no transferirse a otro dominio. Esto se mide en E2 y E3.
3. **El techo es el detector.** Los candidatos cubren el 81 % del gold de dev y el 96 % del de test, y el clasificador no puede recuperar un par que no es candidato.

En `predicciones.csv`, la probabilidad de dev es la de la validación cruzada y la de test es la del modelo final. Así las aristas del clasificador en el grafo no tienen la precisión inflada en dev.
