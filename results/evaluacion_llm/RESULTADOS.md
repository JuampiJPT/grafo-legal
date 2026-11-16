# Parser LLM: resultados

Corrida del 16/11/2026 con `claude-sonnet-5-5` y el prompt `v1-2026-11-16`. Se procesaron las 306 normas con texto en 590 lotes:

- unos 2,68 millones de tokens de entrada y 0,89 millones de salida;
- alrededor de USD 14, más unos USD 0,30 del piloto;
- ninguna respuesta se cortó por longitud.

Las 590 respuestas están en `results/relaciones_llm/cache/`. Con esa caché, volver a correr da exactamente lo mismo, sin clave y sin costo.

## Lo que devolvió el modelo

| | |
|---|---|
| Menciones devueltas | 7.688 |
| … con una cita que no está en el texto (alucinación) | **8 (0,1 %)** |
| … a normas fuera del corpus o sin número | 4.318 |
| … aceptadas | 3.360 |
| Relaciones después de deduplicar | 3.247 (1.014 pares de normas) |

## Detección de relaciones contra InfoLEG

El LLM devuelve también citas que no son modificaciones. Para comparar con el gold se probaron cuatro proyecciones en dev, y se eligió **la regla F aplicada a lo que extrae el LLM**: cuentan las menciones del VISTO y las del articulado; en un decreto, solo si el LLM les asignó un tipo distinto de CITA.

| Método | P test | R test | F1 dev | F1 test | Diferencia con reglas v2 (IC 95 %) |
|---|---|---|---|---|---|
| Reglas v2, F | 0,785 | 0,875 | 0,733 | 0,828 | — |
| **LLM, regla F** | 0,763 | **0,938** | 0,741 | **0,841** | +1,3 [−1,9; +4,0] |
| Híbrido: intersección reglas y LLM | **0,804** | 0,875 | 0,735 | 0,838 | **+1,0 [+0,2; +2,5]** |
| Híbrido: unión | 0,747 | 0,938 | 0,739 | 0,831 | +0,4 [−2,7; +3,0] |
| LLM, todas sus relaciones | — | — | 0,709 | 0,796 | — |

- **El LLM sube el recall** de 0,875 a 0,938, con 12 relaciones más en test, y no pierde ninguna de las que encontraban las reglas.
- **La intersección es la única mejora significativa.** Una relación cuenta si la extraen las reglas y también el LLM. Así se descartan 5 falsos positivos de las reglas sin perder ninguna relación del gold.

## Qué errores de las reglas corrige (test)

| Causa del error de la regla v2 | Pares | Los recupera el LLM |
|---|---|---|
| CONSIDERANDO y decreto sin verbo | 6 | 3 |
| Decreto, articulado sin verbo | 4 | 2 |
| Solo en el CONSIDERANDO | 3 | 3 |
| Solo por nombre propio | 2 | 2 |
| Año escrito como fecha | 1 | 1 |
| Solo cita de procedencia | 1 | 1 |
| Texto ordenado implícito | 5 | 0 |
| No verificable | 2 | 0 |

- **Lo que el LLM recupera** son casos que piden leer la oración: un verbo que está en otra parte del artículo, una norma nombrada por su nombre o una referencia como «la citada ley».
- **Lo que no recupera** son relaciones que el texto no contiene: 7 de los 12 que quedan.
- **Falsos positivos:** el LLM comparte con las reglas los 24 del VISTO y las 14 remisiones desde leyes, porque la proyección elegida acepta igual el VISTO, y agrega 15 propios. Separar en el VISTO la norma que se modifica de la que solo se cita sigue sin resolverse.

## Tipo de relación (los mismos 78 casos revisados a mano)

| | Macro-F1 ponderada | Exactitud ponderada |
|---|---|---|
| Reglas v2 | 0,672 | 0,754 |
| Reglas v3 (optimista) | 0,703 | 0,755 |
| **LLM** | **0,883** | **0,849** |

Es la mejora más grande del trabajo. A diferencia de la v3, el LLM no se ajustó con esta muestra, así que la medida no está sesgada a su favor. El LLM distingue una cita de una acción y entiende las nominalizaciones («la modificación de …»), que es el error principal de las reglas (B47).

## Grafo

Está en `data/grafo_llm/`, separado de los grafos de reglas, que no cambian.

- **Contenido:** 3.247 relaciones, 1.951 de ellas a un artículo concreto.
- **Ida y vuelta:** idéntica (`results/evaluacion_grafo_llm/`).
- **Neo4j:** se carga sin `--borrar`, con `fuente = 'llm'`.

## Reproducir

```bash
python scripts/14_parser_llm.py --hilos 8   # sin clave usa solo la cache
python scripts/15_evaluar_llm.py
python scripts/16_evaluar_tipos.py
python scripts/17_comparar_metodos.py
python scripts/10_armar_grafo.py --relaciones results/relaciones_llm/relaciones_llm.csv --out data/grafo_llm
```
