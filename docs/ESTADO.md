# Estado del TP al 09/11/2026

TP Integrador de Sistemas Inteligentes (UNNOBA), Problemática III: extracción de relaciones entre normas de InfoLEG y grafo trazable en Neo4j.

## En una línea

Hay un solo corpus congelado (340 normas, 775 relaciones) con sus 306 textos, un dataset de 8.066 segmentos y 1.091 pares candidatos, y el parser de reglas v2 congelado: F1 0,828 en test (v1 daba 0,788). Un clasificador con scikit-learn empata con las reglas (0,823). El grafo para Neo4j está armado y verificado, con lo de InfoLEG y lo extraído separados y cada arista rastreable hasta su artículo; falta cargarlo por primera vez en un Neo4j. Sigue el parser LLM.

## Avance por fase del roadmap

| Fase | Estado | Qué hay |
|---|---|---|
| F0 · Alcance y estado del arte | Parcial | Alcance y relación «modifica o complementa» fijados (B01, B02). Faltan las fichas de lectura y el borrador de Introducción y Trabajos relacionados. |
| F1 · Corpus y gold | **Cerrada** | Corpus único congelado: 340 normas, 775 pares (583 dev, 192 test), 306 textos (B33). Scripts que lo reproducen byte a byte. |
| F2 · Segmentación, detección y normalización | **Cerrada para InfoLEG** | Segmentación por zonas, detector de menciones con listas y nombres, catálogo cerrado. Revisión manual de 30 casos de cobertura: 30 correctos. Dataset de segmentos y candidatos (B34). |
| F3 · Parser de reglas y evaluación | **Cerrada** | Reglas v2 diseñadas sobre dev y congeladas: F1 0,733 en dev y 0,828 en test (B36). Revisión de 30 falsos positivos. Clasificador de referencia: F1 0,823 en test (B37). |
| F4 · Parser LLM puro | No empezada | Su entrada ya existe: `data/dataset/articulos.csv`. Hay que elegir el modelo y cómo se accede (API o local). |
| F5 · Parser híbrido | No empezada | Los candidatos ya existen: `data/dataset/pares_candidatos.csv`. |
| F6 · Grafo en Neo4j | **En curso** | Modelo, CSV y cargador listos y verificados (`docs/grafo.md`, B38). Falta la primera carga en un Neo4j del equipo. |
| F7 · Text-to-Cypher | No empezada | Hay cinco consultas de ejemplo con su pregunta en lenguaje natural (`docs/grafo.md`). |
| F8 · Errores, informe y defensa | No empezada | La bitácora (B01 a B39) y los documentos 01 a 03 alimentan las secciones de Datos, Metodología y Limitaciones. |

## Hallazgos que van al informe

1. **El gold de InfoLEG mide un vínculo amplio, no solo modificaciones.** De 21 pares con mención explícita, 7 son modificaciones, 4 reglamentaciones, 1 texto ordenado y 9 remisiones (B27).
2. **Hay un techo de recall textual.** El 81 % del gold de dev y el 96 % del de test aparece como candidato. El resto no tiene una mención detectable o no tiene texto (B26, B34).
3. **Las reglas diseñadas sobre una parte del corpus no generalizan bien al resto.** Pierden 14 puntos de F1 en dev y 22 en test cuando se miden solo sobre pares nuevos. Los falsos positivos vienen de citas de paso (Ganancias, IVA) y de la LCT citada «t.o. por Decreto 390/76», que cuenta el decreto como otra mención (B35).
4. **Restringir al articulado pierde vínculos reales.** En los pares nuevos, 72 de los 73 que filtra la regla de zona tienen la mención solo en el VISTO o el CONSIDERANDO, o en un anexo (B35).
5. **El VISTO es una señal fuerte y el CONSIDERANDO no.** Los pares citados en el VISTO están en el gold el 80 % de las veces; los citados solo en el CONSIDERANDO, el 24 %. Aceptar el VISTO es lo que más mejora las reglas v2 (B36).
6. **Las reglas a mano y un modelo entrenado llegan al mismo F1** (0,828 y 0,823 en test). Con atributos de superficie no hay mucho más para ganar. Lo que queda son remisiones que solo se distinguen de una modificación leyendo la oración (B36, B37).
7. **La Ley 14.250 está bien excluida y el gold tiene ruido** (B30). En 3 de 30 falsos positivos el texto modifica a la norma y InfoLEG no lo registra (B36).

## Pendientes

**Del equipo:**

- Validar las tres revisiones manuales que hizo Claude (`docs/revision_manual/`) y que un segundo anotador repita parte, para el kappa.
- Subir los commits al repositorio (`git push`): desde la sesión de Claude no hay acceso de escritura a GitHub.
- Consultar con la cátedra: supervisión distante, si se evalúa también la modificación estricta y la clasificación fina (B02, B14, B27).
- Elegir cómo obtener la muestra del digesto UNNOBA (B19, B22).
- Elegir el LLM para F4 y F5, y si el grafo lleva embeddings (B38).

**Técnicos, en este orden:**

1. Cargar el grafo en un Neo4j 5 del equipo y correr las consultas de `docs/grafo.md` (F6).
2. Parser LLM puro (F4) sobre `articulos.csv`, con salida estructurada y evidencia verificada contra el texto. Hay que decidir el modelo y el acceso.
3. Parser híbrido (F5): las reglas proponen candidatos y el LLM decide si es modificación o remisión. Tabla comparativa de los tres parsers y el clasificador sobre el mismo test.
4. Text-to-Cypher (F7), con las consultas de ejemplo como base. Decidir si se agregan embeddings a los artículos.

## Dónde está cada cosa

| Qué | Drive (carpeta TP INTEGRADOR) | Repositorio (github.com/JuampiJPT/grafo-legal) |
|---|---|---|
| Bitácora | 00 - Bitácora del TP (versión editable) | `docs/drive/00_bitacora.md` |
| Obtención del corpus | 01 - Obtención y construcción del corpus | `docs/drive/01_obtencion_corpus.md` |
| Profundidad y transferencia | 02 - Profundidad del grafo y transferencia de los parsers | `docs/drive/02_profundidad_y_transferencia.md` |
| Pipeline, corpus, dataset, parsers, clasificador, grafo y revisión manual | 03 - Pipeline oficial, corpus, dataset y parser de reglas | `README.md`, `data/corpus/SNAPSHOT.md`, `docs/dataset.md`, `docs/decisiones.md`, `results/*/RESULTADOS.md`, `docs/grafo.md`, `docs/revision_manual/` |
| Estado | 04 - Estado del TP | `docs/ESTADO.md` |
| Roadmap | 05 - Roadmap del TP (copia; la versión editable es el artefacto de Claude) | `docs/drive/roadmap.md` |
| Datos, textos, dataset, grafo y código | Solo los del corpus v1 histórico | Todo |

Regla (B32): todo documento nuevo se guarda en los dos lugares, y toda decisión, dificultad o hallazgo se registra en la bitácora del Drive.
