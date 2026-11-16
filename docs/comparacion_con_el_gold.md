# Cómo se compara el parser con el gold de InfoLEG

Este documento es la base de la sección «Diseño experimental» del artículo.

## 1. Qué es el gold

InfoLEG publica dos bases complementarias: la de normas modificatorias y la de normas modificadas. Cada fila dice que una norma A «modifica o complementa» a una norma B. El gold del TP son los pares de esa base con origen y destino entre las 340 normas del corpus: **775 pares** (`data/corpus/gold_relaciones.csv`, snapshot del 06/11/2026).

Tres cosas a tener en cuenta:

- **El vínculo es amplio.** En una revisión de 21 pares con mención explícita, 7 son modificaciones, 4 reglamentaciones, 1 texto ordenado y 9 remisiones (B27). Por eso el gold no se compara contra «modifica» en sentido estricto.
- **Es a nivel de norma.** No dice qué artículo ni qué tipo de relación.
- **Tiene ruido.** En 3 de 30 falsos positivos revisados, el texto sí modifica a la norma y InfoLEG no lo registra (B36).

**El gold nunca es entrada del parser.** Lo leen solo los scripts de evaluación: 04, 05, 11, 12, 13 (para entrenar en dev), 15, 16 y 17.

## 2. Split temporal

- **dev:** la norma modificatoria es del 31/12/2019 o anterior (583 pares);
- **test:** la norma modificatoria es posterior (192 pares).

Las reglas, los umbrales de los modelos y la proyección del LLM se eligieron mirando solo dev. Test se evaluó una vez por versión congelada, con fecha y huella SHA-256 del código registradas. El split temporal mide además si el método aguanta el paso del tiempo: test tiene la Ley 27.802, el DNU 70/2023 y sus reglamentaciones.

## 3. Unidad de comparación: el par de normas

El parser produce relaciones tipadas por artículo («el art. 70 del Decreto 70/2023 SUSTITUYE el art. 80 de la Ley 20.744»). Para compararlas con InfoLEG se proyectan a pares (origen, destino).

- **Reglas.** El par está predicho si alguna de sus menciones pasa la regla F: está en el VISTO, o en el articulado con número cuando el origen es una ley o la oración tiene un verbo modificatorio. En todas se exige que la mención no sea una cita de procedencia y que el destino no sea posterior al origen.
- **LLM.** Se prueban cuatro proyecciones y se elige una en dev (`docs/parser_llm.md`).
- **Grafo.** La misma regla F se aplica sobre las aristas leídas del grafo (script 11), y da exactamente las mismas métricas que sobre los archivos del parser.

## 4. Métricas

Sobre pares, contra **todo** el gold del split:

- **precisión:** de los pares que predice el parser, cuántos están en el gold;
- **recall:** de los pares del gold, cuántos recupera;
- **F1:** media armónica de las dos.

Un par del gold que el parser no puede ver, porque no tiene texto o no tiene mención, cuenta como falso negativo. Así todos los métodos se comparan sobre la misma base. Además se reportan:

- el recall sobre el gold con texto;
- el F1 sobre los pares que no se usaron cuando se diseñaron las reglas (`sin_pares_de_v1`), que mide la generalización.

## 5. Evaluación por subtareas

`results/subtareas/RESULTADOS.md` mide cada eslabón por separado:

| Subtarea | Métrica | Resultado |
|---|---|---|
| Detección | Recall contra una búsqueda laxa del número de la norma destino; precisión en una muestra de 60 | 1,00 (dev y test); 0,97 |
| Normalización | Proporción de menciones no resueltas; exactitud de vinculación contra el catálogo completo de InfoLEG | 55,6 % no resueltas (48,0 % son normas fuera del corpus); 95,9 % inequívocas |
| Extracción | P, R y F1 de punta a punta y condicional a los candidatos | test 0,828 de punta a punta; 0,842 condicional |

Además están el embudo (dónde se pierde cada par del gold) y la taxonomía de errores con las categorías de la consigna.

## 6. Techo de recall

En test, 7 de los 192 pares (4 %) no tienen ninguna mención de la norma destino en el texto de la modificatoria. En dev son 75 de 583 (13 %), más 35 sin texto. Ningún método que lea el texto puede recuperarlos. El techo es un recall de 0,964 en test y 0,811 en dev.

## 7. El tipo de relación

InfoLEG no registra el tipo, así que se evalúa contra una revisión manual de 78 relaciones, 13 por tipo predicho. Se reportan la matriz de confusión, la macro-F1 ponderada a la población y la exactitud del artículo destino (`results/tipos/RESULTADOS.md`). La revisión es una primera pasada de Claude y está pendiente de validación humana y de un segundo anotador para el kappa.

## 8. Comparación entre métodos e incertidumbre

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
