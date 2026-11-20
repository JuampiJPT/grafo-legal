# Estado del TP al 20/11/2026

TP Integrador de Sistemas Inteligentes (UNNOBA), Problemática III: extracción de relaciones entre normas de InfoLEG y grafo trazable en Neo4j.

## En una línea

Hay un solo corpus congelado (340 normas, 775 relaciones) con sus 306 textos y el parser de reglas v2 congelado: F1 0,828 en test. La evaluación ya cubre lo que pide la consigna:

- **Subtareas por separado.** La detección encuentra el 99,6 % de los destinos nombrados y la exactitud de vinculación estimada es 99,1 %; casi todas las pérdidas están en la decisión de la regla. Cada falso negativo y falso positivo tiene su causa concreta y su evidencia (`results/errores_explicados/`, B51).
- **Taxonomía de errores** con las categorías de la consigna.
- **Modelo con contexto textual.** Solo da 0,783; en un híbrido con las reglas da 0,839, sin diferencia significativa con las reglas.
- **Tipos.** Matriz de confusión y macro-F1 ponderada de 0,672 sobre 78 casos.
- **Tabla final** con intervalos de confianza.
- **Reglas v3** (experimento, B52). Corrigen la normalización: lee el año escrito como fecha y ya no se pierde ningún par del gold ahí. En test empatan con la v2 (0,826 contra 0,828). Todos los fallos están explicados en `docs/analisis_de_fallos.md`, y el pipeline en `docs/como_se_detecta_una_relacion.md`.

El parser LLM está implementado, con verificación de la cita y caché reproducible, y va a un grafo aparte. Ya corrió sobre todo el corpus (USD 14). F1 0,841 en test; el híbrido por intersección da 0,838 y es la única mejora significativa sobre las reglas. Tipo de relación: macro-F1 0,883, contra 0,672 de las reglas (B54). Falta escribir el artículo.

## Avance por fase del roadmap

| Fase | Estado | Qué hay |
|---|---|---|
| F0 · Alcance y estado del arte | Parcial | Alcance y relación «modifica o complementa» fijados (B01, B02). Faltan las fichas de lectura y el borrador de Introducción y Trabajos relacionados. |
| F1 · Corpus y gold | **Cerrada** | Corpus único congelado: 340 normas, 775 pares (583 dev, 192 test), 306 textos (B33). Scripts que lo reproducen byte a byte. |
| F2 · Segmentación, detección y normalización | **Cerrada para InfoLEG** | Segmentación por zonas, detector de menciones con listas y nombres, catálogo cerrado. Revisión manual de 30 casos de cobertura: 30 correctos. Dataset de segmentos y candidatos (B34). |
| F3 · Parser de reglas y evaluación | **Cerrada** | Reglas v2 diseñadas sobre dev y congeladas: F1 0,733 en dev y 0,828 en test (B36). Revisión de 30 falsos positivos. Clasificador de referencia: F1 0,823 en test (B37). Reglas v3 como experimento: dev 0,750, test 0,826 (B52). |
| F4 · Parser LLM puro | **Cerrada** | `extractores/llm.py` y scripts 14 y 15 (`docs/parser_llm.md`). `claude-sonnet-5-5`, USD 14. F1 0,841 en test, R 0,938, alucinación del 0,1 %, tipo con macro-F1 0,883. Grafo en `data/grafo_llm/` (B54). |
| F5 · Parser híbrido | **En curso** | Híbrido reglas + modelo contextual: F1 0,839 en test (B46). Híbrido reglas ∩ LLM: F1 0,838, la única mejora significativa sobre las reglas (B54). **Parser híbrido en cascada** (`docs/parser_hibrido.md`): F1 0,758 en dev y 0,829 en test (B55). |
| F6 · Grafo en Neo4j | **Cerrada** | Modelo genérico con relaciones tipadas, armado desde la salida estándar (B41, B42). Evaluación leyendo el grafo: ida y vuelta idéntica y F1 0,828 contra InfoLEG en test (B43). Evaluada también sobre el Neo4j del equipo, con las cuatro fuentes: ida y vuelta idéntica (B60). Texto consolidado de la LCT armado desde el grafo: coincide con InfoLEG en el 92 % de los artículos que cambian (B61). |
| F7 · Text-to-Cypher | No empezada | Hay cinco consultas de ejemplo con su pregunta en lenguaje natural (`docs/grafo.md`). |
| F8 · Errores, informe y defensa | **En curso** | Evaluación por subtareas y taxonomía de errores (B45), tipos sobre 78 casos (B47), tabla final con intervalos de confianza (B49), comparación con el gold (`docs/comparacion_con_el_gold.md`) y guía del código para la presentación (`docs/guia_codigo.md`, B50). Análisis de fallos y explicación del pipeline (B52). La bitácora (B01 a B53) y los documentos 01 a 03 y 06 a 08 alimentan el artículo. Falta escribir el artículo LNCS. |

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
16. **Corregir la normalización no mueve el F1 de test.** La v3 lee el año escrito como fecha: las vinculaciones erróneas verificables pasan de 31 a 0 y la normalización deja de perder pares. Aun así empata en test (0,826 contra 0,828), porque gana 3 pares del gold y pierde 2 por una regresión del filtro de procedencia. Lo que limita es la decisión de la regla: el 80 % de los falsos positivos de test son citas del VISTO y remisiones desde leyes (B52).
17. **El LLM lee mejor la oración, pero no resuelve el VISTO.** Recupera 12 de los 24 pares de test que pierden las reglas: decretos sin verbo en la oración, el CONSIDERANDO y nombres propios. Mejora mucho el tipo de relación: macro-F1 de 0,672 a 0,883. Los falsos positivos del VISTO siguen ahí, y el híbrido por intersección es la única mejora significativa en F1: +1,0 puntos, intervalo de +0,2 a +2,5 (B54).
18. **El híbrido en cascada es el mejor en dev, pero empata en test.** Las reglas filtran y el LLM decide solo la zona gris: F1 0,758 en dev (el mejor del trabajo) y 0,829 en test, con recall 0,911 y a un cuarto del costo del LLM puro. Sobre los pares que la regla no sabe decidir, el LLM agrega y saca con confianza. El VISTO sigue siendo el límite (B55).
19. **PI4: el pipeline se transfiere al digesto de la UNNOBA si el adaptador lleva el vocabulario.** Se probó con 70 documentos anotados, cambiando solo el adaptador. El híbrido en cascada da F1 0,958 y las reglas 0,917; la diferencia no es significativa. Con el prompt de InfoLEG, el LLM ignora las resoluciones y cae a 0,405; con tres frases nuevas en el prompt sube a 0,864. El léxico de verbos de InfoLEG no tiene «Ratificar» ni «Dejar sin efecto». El gold es de Claude y está revisado (revisión 2): las remisiones que definen a quién alcanza la resolución son APLICA. Falta un segundo anotador (B57, B58).

20. **El grafo alcanza para reconstruir el texto vigente.** La LCT consolidada desde Neo4j coincide con el texto actualizado de InfoLEG en 242 de 293 artículos (82,6 %, idénticos o casi). Sobre los 102 artículos que cambian en alguno de los dos lados, coincide en el 92 %. Los errores vienen del recall del grafo (Ley 24.522), de la verificación literal y de la derogación de normas modificatorias (B61).
## Pendientes

**Del equipo:**

- Validar las cuatro revisiones manuales que hizo Claude (`docs/revision_manual/`) y que un segundo anotador repita parte, para el kappa.
- Subir los commits al repositorio (`git push`): desde la sesión de Claude no hay acceso de escritura a GitHub.
- Consultar con la cátedra: supervisión distante, si se evalúa también la modificación estricta y la clasificación fina (B02, B14, B27).
- Segundo anotador sobre una parte del gold de la PI4, para el kappa (B58).
- Decidir si el grafo lleva embeddings (B38).

**Técnicos, en este orden:**

1. Cargar los grafos de la v3 y del LLM en Neo4j sin `--borrar` y comparar las fuentes con consultas (B54).
2. Probar las consultas de `docs/grafo.md` en el Neo4j Browser (la evaluación sobre Neo4j ya está, B60).
3. Figuras del artículo: embudo de pérdidas, matriz de confusión de tipos, tabla de métodos con intervalos y diagrama del pipeline.
4. Artículo LNCS y guion de la defensa.
5. Para trabajo futuro: text-to-Cypher (F7), mejoras del tipado sobre otra muestra de dev (E3). La transferencia al digesto UNNOBA ya está hecha (PI4, B57).

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
| Análisis de fallos y cómo se detecta una relación | 08 - Análisis de fallos y cómo se detecta una relación | `docs/analisis_de_fallos.md`, `docs/como_se_detecta_una_relacion.md`, `results/reglas_v3/RESULTADOS.md`, `results/subtareas_v3/`, `results/errores_explicados_v3/` |
| Parser híbrido en cascada | 09 - Parser híbrido en cascada | `docs/parser_hibrido.md`, `results/hibrido/` |
| Texto consolidado (LCT) | 11 - Texto consolidado LCT | `docs/consolidado_lct.md`, `results/consolidado/` |
| PI4 · Digesto UNNOBA | 10 - PI4 digesto UNNOBA | `docs/pi4_digesto_unnoba.md`, `results/pi4_unnoba/`, grafos en `data/grafo_unnoba_{reglas,llm,hibrido}/` |
| Roadmap | 05 - Roadmap del TP (copia; la versión editable es el artefacto de Claude) | `docs/drive/roadmap.md` |
| Datos, textos, dataset, grafo y código | Solo los del corpus v1 histórico | Todo |

Regla (B32): todo documento nuevo se guarda en los dos lugares, y toda decisión, dificultad o hallazgo se registra en la bitácora del Drive.
