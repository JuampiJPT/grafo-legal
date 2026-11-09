# Estado del TP al 09/11/2026

TP Integrador de Sistemas Inteligentes (UNNOBA), Problemática III: extracción de relaciones entre normas de InfoLEG y grafo trazable en Neo4j.

## En una línea

Hay un solo corpus congelado (340 normas, 775 relaciones) con sus 306 textos, un dataset de 8.066 segmentos y 1.091 pares candidatos, y el parser de reglas v2 congelado: F1 0,828 en test (v1 daba 0,788). Un clasificador con scikit-learn empata con las reglas (0,823). El parser produce una salida estándar de relaciones tipadas (sustituye, deroga, reglamenta, cita…), pensada para cualquier documento normativo, y el grafo se arma solo desde ella. Leído de vuelta, el grafo devuelve exactamente lo que se cargó, y contra InfoLEG da F1 0,828 en test. El tipo de relación es correcto en el 67 % de una muestra de 36. Sigue mejorar el tipado y el parser LLM.

## Avance por fase del roadmap

| Fase | Estado | Qué hay |
|---|---|---|
| F0 · Alcance y estado del arte | Parcial | Alcance y relación «modifica o complementa» fijados (B01, B02). Faltan las fichas de lectura y el borrador de Introducción y Trabajos relacionados. |
| F1 · Corpus y gold | **Cerrada** | Corpus único congelado: 340 normas, 775 pares (583 dev, 192 test), 306 textos (B33). Scripts que lo reproducen byte a byte. |
| F2 · Segmentación, detección y normalización | **Cerrada para InfoLEG** | Segmentación por zonas, detector de menciones con listas y nombres, catálogo cerrado. Revisión manual de 30 casos de cobertura: 30 correctos. Dataset de segmentos y candidatos (B34). |
| F3 · Parser de reglas y evaluación | **Cerrada** | Reglas v2 diseñadas sobre dev y congeladas: F1 0,733 en dev y 0,828 en test (B36). Revisión de 30 falsos positivos. Clasificador de referencia: F1 0,823 en test (B37). |
| F4 · Parser LLM puro | No empezada | Su entrada ya existe: `data/dataset/articulos.csv`. Hay que elegir el modelo y cómo se accede (API o local). |
| F5 · Parser híbrido | No empezada | Los candidatos ya existen: `data/dataset/pares_candidatos.csv`. |
| F6 · Grafo en Neo4j | **En curso** | Modelo genérico con relaciones tipadas, armado desde la salida estándar (B41, B42). Evaluación leyendo el grafo: ida y vuelta idéntica y F1 0,828 contra InfoLEG en test (B43). Falta correr la evaluación sobre el Neo4j del equipo. |
| F7 · Text-to-Cypher | No empezada | Hay cinco consultas de ejemplo con su pregunta en lenguaje natural (`docs/grafo.md`). |
| F8 · Errores, informe y defensa | No empezada | La bitácora (B01 a B43) y los documentos 01 a 03 alimentan las secciones de Datos, Metodología y Limitaciones. |

## Hallazgos que van al informe

1. **El gold de InfoLEG mide un vínculo amplio, no solo modificaciones.** De 21 pares con mención explícita, 7 son modificaciones, 4 reglamentaciones, 1 texto ordenado y 9 remisiones (B27).
2. **Hay un techo de recall textual.** El 81 % del gold de dev y el 96 % del de test aparece como candidato. El resto no tiene una mención detectable o no tiene texto (B26, B34).
3. **Las reglas diseñadas sobre una parte del corpus no generalizan bien al resto.** Pierden 14 puntos de F1 en dev y 22 en test cuando se miden solo sobre pares nuevos. Los falsos positivos vienen de citas de paso (Ganancias, IVA) y de la LCT citada «t.o. por Decreto 390/76», que cuenta el decreto como otra mención (B35).
4. **Restringir al articulado pierde vínculos reales.** En los pares nuevos, 72 de los 73 que filtra la regla de zona tienen la mención solo en el VISTO o el CONSIDERANDO, o en un anexo (B35).
5. **El VISTO es una señal fuerte y el CONSIDERANDO no.** Los pares citados en el VISTO están en el gold el 80 % de las veces; los citados solo en el CONSIDERANDO, el 24 %. Aceptar el VISTO es lo que más mejora las reglas v2 (B36).
6. **Las reglas a mano y un modelo entrenado llegan al mismo F1** (0,828 y 0,823 en test). Con atributos de superficie no hay mucho más para ganar. Lo que queda son remisiones que solo se distinguen de una modificación leyendo la oración (B36, B37).
7. **La Ley 14.250 está bien excluida y el gold tiene ruido** (B30). En 3 de 30 falsos positivos el texto modifica a la norma y InfoLEG no lo registra (B36).
8. **Las relaciones que cambian el texto casi siempre están en InfoLEG; las citas, no.** Los pares con una relación `SUSTITUYE` o `DEROGA` están en InfoLEG entre el 90 % y el 100 % de las veces. Los que solo tienen citas, alrededor del 63 %, y explican 160 de los 185 falsos positivos (B43).
9. **El tipo por verbo es una heurística débil para `MODIFICA`.** En la revisión manual el tipo es correcto en 24 de 36 casos, pero en `MODIFICA` solo en 1 de 6. Las nominalizaciones («la derogación del artículo 2°») y los verbos que no actúan («deberá proponer la reglamentación») se toman como acción (B43).

## Pendientes

**Del equipo:**

- Validar las cuatro revisiones manuales que hizo Claude (`docs/revision_manual/`) y que un segundo anotador repita parte, para el kappa.
- Subir los commits al repositorio (`git push`): desde la sesión de Claude no hay acceso de escritura a GitHub.
- Consultar con la cátedra: supervisión distante, si se evalúa también la modificación estricta y la clasificación fina (B02, B14, B27).
- Elegir cómo obtener la muestra del digesto UNNOBA (B19, B22).
- Elegir el LLM para F4 y F5, y si el grafo lleva embeddings (B38).

**Técnicos, en este orden:**

1. Correr `bash cargar_y_evaluar_grafo.sh` sobre el Neo4j del equipo y probar las consultas de `docs/grafo.md` (F6).
2. Mejorar el tipado de las reglas sobre dev: verbos que actúan frente a nominalizaciones, el «como artículo N a la Ley» de las incorporaciones y los artículos de una reglamentación. Ampliar la revisión de tipos para medirlo.
3. Parser LLM puro (F4) que escriba la misma salida estándar, y parser híbrido (F5). Tabla comparativa de los parsers sobre el mismo test y la misma evaluación del grafo.
4. Text-to-Cypher (F7), con las consultas de ejemplo como base.
5. Probar el parser sobre otra fuente (digesto UNNOBA, E3) cambiando solo el adaptador.

## Dónde está cada cosa

| Qué | Drive (carpeta TP INTEGRADOR) | Repositorio (github.com/JuampiJPT/grafo-legal) |
|---|---|---|
| Bitácora | 00 - Bitácora del TP (versión editable) | `docs/drive/00_bitacora.md` |
| Obtención del corpus | 01 - Obtención y construcción del corpus | `docs/drive/01_obtencion_corpus.md` |
| Profundidad y transferencia | 02 - Profundidad del grafo y transferencia de los parsers | `docs/drive/02_profundidad_y_transferencia.md` |
| Pipeline, corpus, dataset, parsers, salida estándar, grafo, evaluación y revisión manual | 03 - Pipeline oficial, corpus, dataset y parser de reglas | `README.md`, `data/corpus/SNAPSHOT.md`, `docs/dataset.md`, `docs/decisiones.md`, `docs/salida_estandar.md`, `docs/grafo.md`, `results/*/RESULTADOS.md`, `docs/revision_manual/` |
| Estado | 04 - Estado del TP | `docs/ESTADO.md` |
| Roadmap | 05 - Roadmap del TP (copia; la versión editable es el artefacto de Claude) | `docs/drive/roadmap.md` |
| Datos, textos, dataset, grafo y código | Solo los del corpus v1 histórico | Todo |

Regla (B32): todo documento nuevo se guarda en los dos lugares, y toda decisión, dificultad o hallazgo se registra en la bitácora del Drive.
