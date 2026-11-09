# Evaluación del grafo normativo

`scripts/11_evaluar_grafo.py` lee las relaciones desde el grafo y las evalúa (bitácora B43). Estos resultados son de la copia en memoria, armada con el mismo código que la carga en Neo4j. `cargar_y_evaluar_grafo.sh` corre la misma evaluación sobre el Neo4j del equipo. La fuente es el parser de reglas v2, y la fecha es el 09/11/2026.

## 1. Ida y vuelta: el grafo devuelve lo que se cargó

| | Relaciones |
|---|---|
| Cargadas desde la salida estándar | 3.277 |
| Devueltas al recorrer el grafo | 3.277 |
| Faltan en el grafo | 0 |
| Sobran en el grafo | 0 |

Son idénticas. La carga no pierde, no duplica ni cambia ninguna relación, incluido el artículo destino.

## 2. Comparación con InfoLEG

Las relaciones del grafo se proyectan a pares de normas con la misma regla F de las reglas v2. Un par es un vínculo si tiene alguna relación que cumpla una de estas condiciones:

- sale del VISTO;
- sale del articulado, con número, y no es una `CITA` o la norma origen no es un decreto.

| Split | Proyección | P | R | F1 |
|---|---|---|---|---|
| dev | vínculos del grafo | 0,750 | 0,717 | 0,733 |
| dev | cualquier relación | 0,616 | 0,804 | 0,697 |
| test | vínculos del grafo | 0,785 | 0,875 | **0,828** |
| test | cualquier relación | 0,669 | 0,958 | 0,788 |
| test | vínculos, sin los pares del v1 | 0,549 | 0,862 | 0,671 |

Los vínculos leídos del grafo dan exactamente las métricas de las reglas v2 (`results/reglas_v2/RESULTADOS.md`). Es otra comprobación de que el grafo representa fielmente la salida del parser. Contar cualquier relación sube el recall, pero baja la precisión, porque muchas citas no son vínculos para InfoLEG.

## 3. Qué tan seguido coincide cada tipo con InfoLEG

Para cada tipo: pares de normas que tienen al menos una relación de ese tipo, y qué proporción de ellos está en InfoLEG.

| Tipo | Pares dev | En InfoLEG | Pares test | En InfoLEG |
|---|---|---|---|---|
| `SUSTITUYE` | 73 | 94,5 % | 41 | 100 % |
| `DEROGA` | 38 | 89,5 % | 37 | 100 % |
| `INCORPORA` | 73 | 76,7 % | 28 | 85,7 % |
| `REGLAMENTA` | 26 | 80,8 % | 12 | 66,7 % |
| `MODIFICA` | 78 | 80,8 % | 25 | 80,0 % |
| `CITA` | 696 | 61,9 % | 241 | 65,1 % |

Las relaciones que cambian el texto (`SUSTITUYE`, `DEROGA`) casi siempre están en InfoLEG. Las citas coinciden en dos de cada tres casos, porque InfoLEG registra también muchas remisiones (B27). De los 185 falsos positivos (dev y test), 160 son pares que solo tienen relaciones `CITA` (`discrepancias.csv`).

## 4. Por norma semilla (dev y test)

| Norma destino | Modificatorias en InfoLEG | En el grafo | Coinciden | Recall | Precisión |
|---|---|---|---|---|---|
| Ley 20.744 (LCT) | 130 | 104 | 94 | 0,723 | 0,904 |
| Ley 24.013 | 105 | 79 | 70 | 0,667 | 0,886 |
| Ley 24.557 | 67 | 62 | 58 | 0,866 | 0,935 |
| Ley 23.551 | 24 | 22 | 18 | 0,750 | 0,818 |
| Ley 14.250 | 12 | 21 | 10 | 0,833 | 0,476 |
| Ley 27.802 | 7 | 8 | 7 | 1,000 | 0,875 |
| Ley 27.742 | 1 | 4 | 1 | 1,000 | 0,250 |

La precisión es baja en la Ley 14.250, porque se la cita mucho en normas que no la modifican (convenios colectivos), y en la Ley 27.742, que tiene una sola modificatoria registrada.

## 5. Lo que InfoLEG no puede evaluar: el tipo

InfoLEG no dice si una norma sustituye, deroga o cita, así que el tipo se evaluó a mano sobre 36 relaciones, 6 por tipo (`docs/revision_manual/revision_tipos_36.csv`). La revisión es una primera pasada de Claude, pendiente de validación humana.

| | Correctos |
|---|---|
| Tipo | 24 de 36 (67 %) |
| Artículo destino | 30 de 36 (83 %) |

Por tipo, son correctos 5 de 6 en `SUSTITUYE`, `INCORPORA` y `DEROGA`, 4 de 6 en `REGLAMENTA` y `CITA`, y solo 1 de 6 en `MODIFICA`. Los errores y su causa están en `docs/salida_estandar.md`.
