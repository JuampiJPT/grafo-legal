# Estado del TP al 09/11/2026

TP Integrador de Sistemas Inteligentes (UNNOBA), Problemática III: extracción de relaciones entre normas de InfoLEG y grafo trazable en Neo4j.

## En una línea

Hay un solo corpus congelado (340 normas, 775 relaciones) con sus 306 textos, y un dataset listo para usar: 8.066 segmentos de texto y 1.091 pares candidatos etiquetados. El parser de reglas v1 da F1 0,652 en dev y 0,788 en test, pero cae a alrededor de 0,5 en los pares que no se usaron para diseñarlo. Sigue la iteración v2 de reglas y después el parser LLM.

## Avance por fase del roadmap

| Fase | Estado | Qué hay |
|---|---|---|
| F0 · Alcance y estado del arte | Parcial | Alcance y relación «modifica o complementa» fijados (B01, B02). Faltan las fichas de lectura y el borrador de Introducción y Trabajos relacionados. |
| F1 · Corpus y gold | **Cerrada** | Corpus único congelado: 340 normas, 775 pares (583 dev, 192 test), 306 textos (B33). Scripts que lo reproducen byte a byte. |
| F2 · Segmentación, detección y normalización | **Cerrada para InfoLEG** | Segmentación por zonas, detector de menciones con listas y nombres, catálogo cerrado. Revisión manual de 30 casos de cobertura: 30 correctos. Dataset de segmentos y candidatos (B34). |
| F3 · Parser de reglas y evaluación | **En curso** | Las reglas v1 dan F1 0,652 en dev y 0,788 en test sobre el corpus único, y 0,514 y 0,563 sobre los pares nuevos. Falta la iteración v2 sobre dev y la revisión de falsos positivos. |
| F4 · Parser LLM puro | No empezada | Su entrada ya existe: `data/dataset/articulos.csv`. |
| F5 · Parser híbrido | No empezada | Los candidatos ya existen: `data/dataset/pares_candidatos.csv`. |
| F6 · Grafo en Neo4j | No empezada | |
| F7 · Text-to-Cypher | No empezada | |
| F8 · Errores, informe y defensa | No empezada | La bitácora (B01 a B35) y los documentos 01 a 03 alimentan las secciones de Datos, Metodología y Limitaciones. |

## Hallazgos que van al informe

1. **El gold de InfoLEG mide un vínculo amplio, no solo modificaciones.** De 21 pares con mención explícita, 7 son modificaciones, 4 reglamentaciones, 1 texto ordenado y 9 remisiones (B27).
2. **Hay un techo de recall textual.** El 81 % del gold de dev y el 96 % del de test aparece como candidato. El resto no tiene una mención detectable o no tiene texto (B26, B34).
3. **Las reglas diseñadas sobre una parte del corpus no generalizan bien al resto.** Pierden 14 puntos de F1 en dev y 22 en test cuando se miden solo sobre pares nuevos. Los falsos positivos vienen de citas de paso (Ganancias, IVA) y de la LCT citada «t.o. por Decreto 390/76», que cuenta el decreto como otra mención (B35).
4. **Restringir al articulado pierde vínculos reales.** En los pares nuevos, 72 de los 73 que filtra la regla de zona tienen la mención solo en el VISTO o el CONSIDERANDO, o en un anexo (B35).
5. **La Ley 14.250 está bien excluida y el gold tiene ruido** (B30).

## Pendientes

**Del equipo:**

- Validar las dos revisiones manuales que hizo Claude (`docs/revision_manual/`) y que un segundo anotador repita parte, para el kappa.
- Consultar con la cátedra: supervisión distante, si se evalúa también la modificación estricta y la clasificación fina (B02, B14, B27).
- Elegir cómo obtener la muestra del digesto UNNOBA (B19, B22).

**Técnicos, en este orden:**

1. Reglas v2 sobre el dev del corpus único: tratar el «t.o. por Decreto 390/76» como parte de la cita a la LCT, revisar la regla de zona y revisar 30 falsos positivos.
2. Clasificador con scikit-learn sobre `pares_candidatos.csv`, entrenado solo con dev, como punto de comparación de los parsers.
3. Parser LLM puro (F4) sobre `articulos.csv`, con salida estructurada y evidencia verificada contra el texto.
4. Parser híbrido (F5) y tabla comparativa de los tres sobre el mismo test.
5. Grafo en Neo4j con evidencia y gold separado (F6), y luego text-to-Cypher (F7).

## Dónde está cada cosa

| Qué | Drive (carpeta TP INTEGRADOR) | Repositorio (github.com/JuampiJPT/grafo-legal) |
|---|---|---|
| Bitácora | 00 - Bitácora del TP (versión editable) | `docs/drive/00_bitacora.md` |
| Obtención del corpus | 01 - Obtención y construcción del corpus | `docs/drive/01_obtencion_corpus.md` |
| Profundidad y transferencia | 02 - Profundidad del grafo y transferencia de los parsers | `docs/drive/02_profundidad_y_transferencia.md` |
| Pipeline, corpus, dataset, parser de reglas y revisión manual | 03 - Pipeline oficial, corpus, dataset y parser de reglas | `README.md`, `data/corpus/SNAPSHOT.md`, `docs/dataset.md`, `docs/decisiones.md`, `results/reglas/RESULTADOS.md`, `docs/revision_manual/` |
| Estado | 04 - Estado del TP | `docs/ESTADO.md` |
| Roadmap | 05 - Roadmap del TP (copia; la versión editable es el artefacto de Claude) | `docs/drive/roadmap.md` |
| Datos, textos, dataset y código | Solo los del corpus v1 histórico | Todo |

Regla (B32): todo documento nuevo se guarda en los dos lugares, y toda decisión, dificultad o hallazgo se registra en la bitácora del Drive.
