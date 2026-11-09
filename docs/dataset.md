# Ficha del dataset

Generado por `scripts/07_armar_dataset.py` a partir del corpus único (`data/corpus`, snapshot de InfoLEG del 06/11/2026) y de las menciones que detecta el parser de reglas (`results/reglas/evidencias.csv`). Se regenera en segundos y sin red.

## Archivos

| Archivo | Unidad (una fila por…) | Filas | Para qué |
|---|---|---|---|
| `data/dataset/articulos.csv` | segmento de una norma: encabezado, artículo, anexo o notas | 8.066 (306 normas) | Entrada de los parsers LLM e híbrido; análisis del texto |
| `data/dataset/pares_candidatos.csv` | par norma origen → norma destino propuesto por el detector de menciones | 1.091 (801 dev, 290 test) | Clasificador con scikit-learn; elección de ejemplos few-shot; análisis de errores |
| `data/dataset/resumen.json` | | | Conteos y descripción de columnas |

### articulos.csv

Columnas: `id_norma`, `norma`, `tipo_norma`, `fecha`, `split`, `orden`, `zona`, `articulo`, `inicio`, `fin`, `n_chars`, `largo_norma` y `texto`.

| Zona | Segmentos |
|---|---|
| articulado | 7.667 |
| encabezado | 303 |
| notas | 54 |
| anexo | 42 |

`inicio` y `fin` son offsets sobre el texto limpio de la norma, el mismo que usan las evidencias del parser. Así cualquier arista se puede rastrear hasta su fragmento. La mediana es de 424 caracteres por artículo.

### pares_candidatos.csv

La etiqueta es `en_gold`: vale 1 si el par está en el gold de InfoLEG.

| Grupo | Atributos |
|---|---|
| Menciones | `n_menciones`, `n_menc_articulado`, `n_menc_encabezado`, `n_menc_anexo`, `n_menc_notas`, `n_articulos`, `frac_articulos` |
| Verbos | `verbo_en_articulo`, `verbo_en_oracion`. Se cuentan en cualquier segmento que contenga la mención, incluido el encabezado |
| Forma de la cita | `solo_alias` (el destino solo se nombra, sin número) |
| Tiempo | `temporal_ok`, `dif_anios` |
| Posición | `pos_primera_mencion`, `largo_texto` |
| Categóricos | `tipo_origen`, `tipo_destino`, `destino_es_semilla` |

La descripción de cada columna está en `resumen.json`.

| | Dev | Test |
|---|---|---|
| Candidatos | 801 | 290 |
| Positivos | 472 | 185 |
| Proporción de positivos | 58,9 % | 63,8 % |
| Cobertura de los candidatos sobre el gold | 81,0 % | 96,4 % |

La cobertura es el techo de recall de cualquier clasificador que parta de estos candidatos. El resto del gold no tiene una mención detectable en el texto (bitácora B26).

## Reglas de uso

1. **Ningún atributo se calcula con el gold.** Tampoco se usan los conteos `modificada_por_total` y `modifica_a_total` de InfoLEG, porque salen de las mismas relaciones y filtrarían la respuesta.
2. **Se entrena y se ajusta solo con `split == "dev"`.** La etiqueta de test está en el archivo solo para la evaluación final, que se hace una vez (B16).
3. **Las etiquetas son supervisión distante.** Vienen de InfoLEG, que mezcla modificaciones con remisiones (B27). Un positivo significa «InfoLEG registró el vínculo», no necesariamente «lo modifica». Queda como consulta a la cátedra (B14).
4. **Los candidatos dependen del detector de reglas.** Si el detector mejora, hay que regenerar el dataset y versionar los resultados.

## Formato y librerías

Los datos son CSV, que se leen con `pandas.read_csv`. No se usa `.npy`: es un formato para arreglos numéricos sin nombres de columnas, y acá la mitad del contenido es texto o categorías. Para scikit-learn, la matriz se arma en memoria:

```python
import pandas as pd
p = pd.read_csv("data/dataset/pares_candidatos.csv")
dev = p[p.split == "dev"]
X = pd.get_dummies(dev.drop(columns=["id_norma_origen", "id_norma_destino", "split", "en_gold"]))
y = dev.en_gold.to_numpy()
```

Se probó Parquet, que guarda los tipos de columna, pero exige `pyarrow` y no se pudo instalar en el entorno de trabajo. Si el equipo lo prefiere, es un cambio de una línea.
