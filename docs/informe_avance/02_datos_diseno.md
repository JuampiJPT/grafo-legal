# 3. Datos y diseño experimental

## 3.1 Fuente y características de los datos

**Fuente.** La Base InfoLEG de Normativa Nacional y sus dos bases complementarias, de normas modificadas y de normas modificatorias. Las publica el Portal de Datos Abiertos de la Justicia Argentina con licencia CC BY 4.0 [1]. Se descargaron el 06/11/2026:

| Base | Filas |
|---|---|
| Normativa nacional | 430.834 |
| Normas modificatorias | 380.481 |
| Normas modificadas | 385.118 |

Los SHA-256 de los tres CSV están en `data/corpus/SNAPSHOT.md`. Los textos de las normas se bajaron del sitio de InfoLEG (306 HTML) y se guardaron con su URL, fecha y SHA-256 (`data/textos/infoleg/`).

**Corpus.** Es único y está congelado (B33, D11), dentro del dominio laboral:

- **Anclas.** Cinco leyes que se expanden un salto: 20.744 (LCT), 27.802 (modernización laboral), 24.013 (empleo), 24.557 (riesgos del trabajo) y 23.551 (asociaciones sindicales). Dos nodos no se expanden: la Ley 14.250 (convenciones colectivas), porque arrastraría cientos de normas de otro dominio (B07, B30), y la Ley 27.742.
- **Tipos de norma.** Ley, decreto y decreto-ley.
- **Tamaño.** 340 normas, 306 con texto en InfoLEG. Las 34 sin texto no tienen enlace al texto en InfoLEG; todas menos una son de 1997 o anteriores.
- **Gold.** 775 pares dirigidos (norma origen, norma destino) de las bases complementarias, restringidos a normas del corpus.

**Qué mide el gold.** InfoLEG registra un vínculo amplio. En una muestra de 21 pares con mención explícita en el texto (B27):

| Clase de vínculo | Pares |
|---|---|
| Modificaciones | 7 |
| Remisiones | 9 |
| Reglamentaciones | 4 |
| Texto ordenado | 1 |

Por eso se evalúa la relación general «modifica o complementa» (D6).

**Partición temporal.** El corte es el 31/12/2019, según la fecha de la norma modificatoria (B09):

| Conjunto | Pares | Modificatorias |
|---|---|---|
| Desarrollo (dev) | 583 | hasta 2019 |
| Prueba (test) | 192 | desde 2020 (43 normas de origen) |

La partición simula aplicar el sistema a normas nuevas, y la recomienda la consigna. El corpus anterior (v1, 183 normas y 402 pares) está contenido en el actual con el mismo split. `pares_evaluados_en_v1.csv` marca los pares que ya se habían mirado, para informar también el desempeño sobre pares nunca vistos.

**Techo textual.** No todo el gold se puede encontrar leyendo el texto de la modificatoria. El destino aparece nombrado en el 81 % de los pares de dev y en el 96 % de los de test. El resto son normas sin texto, vínculos que el texto no nombra (complementa sin citar, texto ordenado implícito, derogación genérica) o errores del gold (B26, B51).

**Dataset derivado.** Con pandas se armaron dos tablas (B34, D12, `docs/dataset.md`):

- `articulos.csv`: 8.066 segmentos;
- `pares_candidatos.csv`: 1.091 pares candidatos, con sus atributos y su etiqueta.

**Corpus de transferencia (PI4).** El digesto de la UNNOBA tiene 912 documentos distintos en PDF. Se bajaron a mano porque el robots.txt prohíbe el acceso automático (B56). Se sorteó una muestra estratificada de 70 con una semilla fija:

- 7 ordenanzas;
- 48 documentos de temas de reglamentos;
- 15 al azar.

Claude la anotó en tres clases (MOD, APLICA y CITA), en dos revisiones (B57, B58). Son 109 pares, de los que 61 forman el vínculo MOD ∪ APLICA.

## 3.2 Preprocesamiento

El adaptador de la fuente (`fuentes/infoleg.py`) pasa el HTML a texto limpio: saca etiquetas, notas al pie y espacios repetidos. Después lo segmenta en **zonas**:

- **encabezado**, con el VISTO y el CONSIDERANDO;
- **articulado**, partido en artículos;
- **anexos**;
- **notas de InfoLEG**.

Cada segmento conserva sus offsets en el texto limpio, que es lo que después permite que cada arista apunte a su evidencia exacta.

Para el digesto, el adaptador `fuentes/unnoba.py` hace lo mismo sobre el texto que sale de `pdftotext`, y aplica OCR (tesseract) a los 38 documentos escaneados de la muestra. Une las líneas de maquetación y reconoce las fórmulas propias del digesto: «RESUELVE:», «ORDENA:», «Regístrese…».

## 3.3 Método de referencia: reglas

El parser de reglas tiene tres etapas, que se evalúan por separado:

1. **Detección** (`extractores/menciones.py`). Dos detectores:
   - Expresiones regulares para las menciones por número: «Ley N° 24.557», «Decreto 1694/06», «leyes 23.551 y 25.674», «DNU 70/2023».
   - Un gazetteer de nombres propios: «Ley de Contrato de Trabajo», «L.C.T.», «Ley de Ministerios».
2. **Normalización** (`catalogo.py`). Cada mención (tipo, número, año) se busca en el catálogo de las 430.834 normas, y queda en uno de cuatro estados:
   - **resuelta**, si hay una sola norma posible;
   - **ambigua**, si falta el año y hay varias. Se resuelve por mundo cerrado solo si una única candidata está en el corpus;
   - **fuera del corpus**;
   - **no encontrada**.
3. **Decisión de la relación.** Una regla sobre la zona, el verbo y el tipo de norma de origen decide si la mención es un vínculo. El tipo de relación sale del verbo de la oración (`relaciones.py`).

Hay tres versiones de la regla:

- **v1** (configuración C): solo menciones del articulado, no posteriores al origen.
- **v2** (configuración F): es la **referencia del trabajo**. Acepta el par si hay una mención no posterior al origen y que no sea una cita de procedencia («t.o. por Decreto 390/76»), siempre que esté en el VISTO, o en el articulado cuando el origen es una ley o la oración tiene un verbo modificatorio (D13).
- **v3** (experimento, D25): corrige la normalización, porque lee el año escrito como fecha («Decreto 467 del 14 de abril de 1988»).

## 3.4 Soluciones evaluadas

| Enfoque | Descripción | Bitácora |
|---|---|---|
| Clasificador de superficie | Random forest sobre 22 atributos de cada par candidato: menciones por zona, verbo en el artículo o en la oración, tipos de norma, diferencia de años, mención solo por nombre propio, entre otros. Validación cruzada agrupada por norma de origen en dev | B37, D14 |
| Modelo contextual | TF-IDF de la ventana de texto de cada mención, solo y con los atributos de superficie | B46, D20 |
| Parser LLM | `claude-sonnet-5-5` lee los artículos que nombran normas y devuelve, en JSON, la cita textual, la norma destino, el artículo destino, el tipo y el verbo. Si la cita no está literal en el texto, la relación se descarta (anti-alucinación). Las respuestas se guardan en una caché por huella del pedido | B48, D22 |
| Híbrido reglas + modelo contextual | El modelo decide solo donde las reglas dudan | B46 |
| Híbridos reglas ∩ LLM y reglas ∪ LLM | Combinan las dos salidas: intersección o unión | B54, D26 |
| Híbrido en cascada | Las reglas generan candidatos y los dividen en tres zonas (descarte, seguro y gris). El LLM juzga solo los seguros (para el tipo) y los grises (para la decisión), con umbrales de 0,15 y 0,5 sobre la opinión previa de la regla | B55, D27 |

## 3.5 Métricas

- **Extracción.** Precisión, recall y F1 a nivel de par dirigido (origen, destino), contra el gold de InfoLEG.
- **Detección.** Proporción de pares del gold cuyo destino se detecta en el texto.
- **Normalización.** Exactitud de vinculación (verificable contra la fecha del texto, y estimada) y proporción de menciones no resueltas, separando las que están fuera del corpus.
- **Tipo de relación.** Matriz de confusión, F1 por tipo y macro-F1 sobre 78 casos revisados a mano, 13 por tipo. Como la muestra está estratificada, se informa también la macro-F1 ponderada por la frecuencia de cada tipo en la población (D21).
- **Incertidumbre.** Intervalos de confianza del 95 % por bootstrap pareado, remuestreando las normas de origen de test (43 normas, 2.000 réplicas, semilla fija) [16]. Una diferencia es significativa si su intervalo no contiene el cero (D23).
- **Grafo.** Ida y vuelta (lo que se lee de Neo4j tiene que ser igual a lo que se cargó) y F1 contra InfoLEG leyendo desde el grafo (D18).
- **Consolidado.** Similitud por artículo (difflib sobre texto normalizado) con el texto actualizado de InfoLEG.

## 3.6 Procedimiento de evaluación

1. **El gold nunca es entrada de un extractor.** Solo lo leen los scripts de evaluación y, para entrenar, los modelos supervisados sobre dev. El parser LLM y el grafo no lo leen.
2. **Todo se diseña sobre dev.** Reglas, prompts, umbrales y proyecciones se ajustan sobre dev. Cada versión congelada se evalúa en test **una sola vez** (B16, D7). La v3 y el híbrido en cascada, que se diseñaron después de ver los errores de test de la v2, se informan como experimentos.
3. **Todos los métodos se miden sobre los mismos 192 pares de test**, con la misma proyección a pares y la misma restricción temporal (`17_comparar_metodos.py`).
4. **Cada error se explica caso por caso.** Cada falso positivo y falso negativo de test se clasifica con una causa y su evidencia (`18_explicar_errores.py`, D24), con las categorías de error de la consigna.
5. **Reproducibilidad.** Todo está en scripts numerados (`correr_pipeline.sh`). Las respuestas del LLM se guardan en caché, y el corpus se verifica byte a byte (sección 5).
