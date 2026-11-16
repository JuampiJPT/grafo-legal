# Estado del TP al 16/11/2026

TP Integrador de Sistemas Inteligentes (UNNOBA), Problemática III: extracción de relaciones entre normas de InfoLEG y grafo trazable en Neo4j.

## En una línea

Hay un solo corpus congelado (340 normas, 775 relaciones) con sus 306 textos y el parser de reglas v2 congelado: F1 0,828 en test. La evaluación ya cubre lo que pide la consigna:

- **Subtareas por separado.** La detección encuentra el 99,6 % de los destinos nombrados y la exactitud de vinculación estimada es 99,1 %; casi todas las pérdidas están en la decisión de la regla. Cada falso negativo y falso positivo tiene su causa concreta y su evidencia (`results/errores_explicados/`, B51).
- **Taxonomía de errores** con las categorías de la consigna.
- **Modelo con contexto textual.** Solo da 0,783; en un híbrido con las reglas da 0,839, sin diferencia significativa con las reglas.
- **Tipos.** Matriz de confusión y macro-F1 ponderada de 0,672 sobre 78 casos.
- **Tabla final** con intervalos de confianza.

El parser LLM está implementado, con verificación de la cita y caché reproducible, y va a un grafo aparte. Falta correrlo con la clave de la API y escribir el artículo.

## Avance por fase del roadmap

| Fase | Estado | Qué hay |
|---|---|---|
| F0 · Alcance y estado del arte | Parcial | Alcance y relación «modifica o complementa» fijados (B01, B02). Faltan las fichas de lectura y el borrador de Introducción y Trabajos relacionados. |
| F1 · Corpus y gold | **Cerrada** | Corpus único congelado: 340 normas, 775 pares (583 dev, 192 test), 306 textos (B33). Scripts que lo reproducen byte a byte. |
| F2 · Segmentación, detección y normalización | **Cerrada para InfoLEG** | Segmentación por zonas, detector de menciones con listas y nombres, catálogo cerrado. Revisión manual de 30 casos de cobertura: 30 correctos. Dataset de segmentos y candidatos (B34). |
| F3 · Parser de reglas y evaluación | **Cerrada** | Reglas v2 diseñadas sobre dev y congeladas: F1 0,733 en dev y 0,828 en test (B36). Revisión de 30 falsos positivos. Clasificador de referencia: F1 0,823 en test (B37). |
| F4 · Parser LLM puro | **Implementado, falta correrlo** | `extractores/llm.py` y scripts 14 y 15 (`docs/parser_llm.md`). Modelo `claude-sonnet-5-5`, unos USD 8 para todo el corpus. Falta la clave de la API (B48). |
| F5 · Parser híbrido | **En curso** | Híbrido reglas + modelo contextual: F1 0,839 en test (B46). El híbrido reglas + LLM se evalúa con el script 15 cuando se corra el LLM. |
| F6 · Grafo en Neo4j | **En curso** | Modelo genérico con relaciones tipadas, armado desde la salida estándar (B41, B42). Evaluación leyendo el grafo: ida y vuelta idéntica y F1 0,828 contra InfoLEG en test (B43). Falta correr la evaluación sobre el Neo4j del equipo. |
| F7 · Text-to-Cypher | No empezada | Hay cinco consultas de ejemplo con su pregunta en lenguaje natural (`docs/grafo.md`). |
| F8 · Errores, informe y defensa | **En curso** | Evaluación por subtareas y taxonomía de errores (B45), tipos sobre 78 casos (B47), tabla final con intervalos de confianza (B49), comparación con el gold (`docs/comparacion_con_el_gold.md`) y guía del código para la presentación (`docs/guia_codigo.md`, B50). La bitácora (B01 a B51) y los documentos 01 a 03, 06 y 07 alimentan el artículo. Falta escribir el artículo LNCS. |

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

10. **Casi todas las pérdidas están en la decisión de la regla.** En test, de los 24 pares del gold que se pierden, 16 los descarta la regla, 7 no nombran a su destino en el texto y 1 no se normaliza. Los que descarta la regla son decretos que nombran la norma sin verbo o solo en el CONSIDERANDO (B45, B51).
11. **El mundo cerrado tiene un costo acotado.** El 48 % de las menciones nombra normas reales fuera del corpus. De las vinculadas, el 4,1 % son decretos sin año que solo se resuelven porque el corpus tiene uno con ese número; la fecha del texto permite verificar 117 y 31 resultan ser otro decreto. Fuera del corpus, la regla F acierta contra la base completa de InfoLEG el 62 % de las veces en test (B45).
12. **Leer el contexto, solo, no alcanza; combinado con las reglas, ayuda en la zona gris.** El modelo TF-IDF da 0,761 a 0,783 en test, significativamente peor que las reglas. Usado solo donde las reglas dudan, sube el recall de 0,875 a 0,906 y el F1 a 0,839. La mejora no es significativa con 192 pares (B46, B49).
13. **El error de tipo dominante es una cita tomada como acción** (21 de 25 errores en 78 casos). La macro-F1 ponderada es 0,672 y la exactitud 0,754 (B47).
14. **El año escrito como fecha es el principal error de normalización.** «Decreto N° 467 del 14 de abril de 1988»: el detector no lee el año de la fecha. Por eso quedan ambiguas 360 de 580 menciones, se vinculan mal 31 y se pierden 10 pares del gold (B51).
15. **InfoLEG registra vínculos que el texto no nombra.** De los 80 pares del gold sin mención: 36 son normas que complementan a la destino sin citarla, 9 son decretos de texto ordenado («t.o. 1976» vincula al Decreto 390/76), 16 son derogaciones genéricas o de modificatorias, y 2 parecen errores del gold (B51).

## Pendientes

**Del equipo:**

- Validar las cuatro revisiones manuales que hizo Claude (`docs/revision_manual/`) y que un segundo anotador repita parte, para el kappa.
- Subir los commits al repositorio (`git push`): desde la sesión de Claude no hay acceso de escritura a GitHub.
- Consultar con la cátedra: supervisión distante, si se evalúa también la modificación estricta y la clasificación fina (B02, B14, B27).
- Elegir cómo obtener la muestra del digesto UNNOBA (B19, B22).
- Crear `.anthropic_key` con la clave de la API para correr el parser LLM (B48).
- Decidir si el grafo lleva embeddings (B38).

**Técnicos, en este orden:**

1. Correr el parser LLM (script 14), evaluarlo (15 y 16), armar su grafo en `data/grafo_llm/` y cargarlo en Neo4j sin `--borrar`. Actualizar la tabla final (17).
2. Correr `bash cargar_y_evaluar_grafo.sh` sobre el Neo4j del equipo y probar las consultas de `docs/grafo.md` (F6).
3. Figuras del artículo: embudo de pérdidas, matriz de confusión de tipos, tabla de métodos con intervalos y diagrama del pipeline.
4. Artículo LNCS y guion de la defensa.
5. Para trabajo futuro: text-to-Cypher (F7), mejoras del tipado sobre otra muestra de dev y el digesto UNNOBA cambiando solo el adaptador (E3).

## Dónde está cada cosa

| Qué | Drive (carpeta TP INTEGRADOR) | Repositorio (github.com/JuampiJPT/grafo-legal) |
|---|---|---|
| Bitácora | 00 - Bitácora del TP (versión editable) | `docs/drive/00_bitacora.md` |
| Obtención del corpus | 01 - Obtención y construcción del corpus | `docs/drive/01_obtencion_corpus.md` |
| Profundidad y transferencia | 02 - Profundidad del grafo y transferencia de los parsers | `docs/drive/02_profundidad_y_transferencia.md` |
| Pipeline, corpus, dataset, parsers, salida estándar, grafo, evaluación y revisión manual | 03 - Pipeline oficial, corpus, dataset y parser de reglas | `README.md`, `data/corpus/SNAPSHOT.md`, `docs/dataset.md`, `docs/decisiones.md`, `docs/salida_estandar.md`, `docs/grafo.md`, `results/*/RESULTADOS.md`, `docs/revision_manual/` |
| Estado | 04 - Estado del TP | `docs/ESTADO.md` |
| Parser y grafo paso a paso | 06 - Parser y grafo: arquitectura y construcción paso a paso | `docs/arquitectura_parser_y_grafo.md` |
| Evaluación completa, parser LLM y guía del código | 07 - Evaluación completa, parser LLM y guía del código | `docs/comparacion_con_el_gold.md`, `docs/parser_llm.md`, `docs/guia_codigo.md`, `results/subtareas/`, `results/modelo_contextual/`, `results/tipos/`, `results/comparacion/` |
| Roadmap | 05 - Roadmap del TP (copia; la versión editable es el artefacto de Claude) | `docs/drive/roadmap.md` |
| Datos, textos, dataset, grafo y código | Solo los del corpus v1 histórico | Todo |

Regla (B32): todo documento nuevo se guarda en los dos lugares, y toda decisión, dificultad o hallazgo se registra en la bitácora del Drive.
