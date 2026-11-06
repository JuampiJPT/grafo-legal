# Estado del TP al 06/11/2026

TP Integrador de Sistemas Inteligentes (UNNOBA), Problemática III: extracción de relaciones entre normas de InfoLEG y grafo trazable en Neo4j.

## En una línea

Están cerrados los datos (corpus v1 congelado y v2 ampliado, con sus textos) y el primer parser (reglas), que da F1 0,716 en dev y 0,844 en test. Sigue el parser LLM. El grafo y el text-to-Cypher todavía no se empezaron.

## Avance por fase del roadmap

| Fase | Estado | Qué hay |
|---|---|---|
| F0 · Alcance y estado del arte | Parcial | Alcance y relación «modifica o complementa» fijados (B01, B02). Faltan las fichas de lectura y el borrador de Introducción y Trabajos relacionados. |
| F1 · Corpus y gold | **Cerrada** | v1 congelado: 183 normas, 402 pares, 168 textos. v2: 340 normas, 775 pares, 306 textos. Scripts que reproducen todo y verificación del v1 con datos nuevos. |
| F2 · Segmentación, detección y normalización | **Cerrada para InfoLEG** | Segmentación por zonas (encabezado, articulado, anexo), detector de menciones con listas y nombres, catálogo cerrado. Cobertura textual medida y revisada a mano (30/30 correctas). |
| F3 · Parser de reglas y evaluación | **Cerrada** (falta revisar falsos positivos) | 5 configuraciones evaluadas. La final (articulado + filtro temporal) da P 0,692 / R 0,742 / F1 0,716 en dev y P 0,784 / R 0,913 / F1 0,844 en test, evaluado una sola vez. |
| F4 · Parser LLM puro | No empezada | |
| F5 · Parser híbrido | No empezada | |
| F6 · Grafo en Neo4j | No empezada | |
| F7 · Text-to-Cypher | No empezada | |
| F8 · Errores, informe y defensa | No empezada | La bitácora (B01 a B32) y los documentos 01 y 02 ya alimentan las secciones de Datos, Metodología y Limitaciones. |

## Hallazgos que van al informe

1. **El gold de InfoLEG mide un vínculo amplio, no solo modificaciones.** De 21 pares con mención explícita, 7 son modificaciones, 4 reglamentaciones, 1 texto ordenado y 9 remisiones (B27). Por eso exigir un verbo modificatorio baja el F1 de 0,716 a 0,556.
2. **Hay un techo de recall textual.** El 13 % de los pares del v1 no menciona a la norma destino y 9 pares no tienen texto: ningún parser que lea el texto puede recuperarlos (B12, B26).
3. **El test del v1 está concentrado.** El 54 % de sus pares sale de tres normas (Ley 27.802, DNU 70/2023 y Ley 27.742); en el v2 baja al 36 % (B24, B29). Explica que test dé mejor que dev.
4. **La Ley 14.250 está bien excluida.** 0 de 30 de sus «modificatorias» la modifican: son homologaciones de convenios (B30).
5. **El gold tiene ruido.** Aparecen circulares del BCRA y decretos secretos como modificatorias de leyes laborales (B30).

## Pendientes

**Del equipo:**

- Validar las dos revisiones manuales que hizo Claude (`docs/revision_manual/`) y que un segundo anotador repita parte, para el kappa.
- Consultar con la cátedra: supervisión distante, si se evalúa también la modificación estricta y la clasificación fina (B02, B14, B27).
- Elegir cómo obtener la muestra del digesto UNNOBA (B19, B22).

**Técnicos, en este orden:**

1. Revisar a mano 30 falsos positivos del parser de reglas (B28).
2. Parser LLM puro (F4), con salida estructurada y evidencia verificada contra el texto.
3. Parser híbrido (F5) y tabla comparativa de los tres sobre el v1 y el v2.
4. Grafo en Neo4j con evidencia y gold separado (F6), y luego text-to-Cypher (F7).
5. Muestra independiente del gold para medir el sesgo de selección (B15), si da el tiempo.

## Dónde está cada cosa

| Qué | Drive (carpeta TP INTEGRADOR) | Repositorio (github.com/JuampiJPT/grafo-legal) |
|---|---|---|
| Bitácora | 00 - Bitácora del TP (versión editable) | `docs/drive/00_bitacora.md` |
| Obtención del corpus | 01 - Obtención y construcción del corpus | `docs/drive/01_obtencion_corpus.md` |
| Profundidad y transferencia | 02 - Profundidad del grafo y transferencia de los parsers | `docs/drive/02_profundidad_y_transferencia.md` |
| Pipeline, parser de reglas y revisión manual | 03 - Pipeline oficial, parser de reglas y revisión manual | `README.md`, `docs/decisiones.md`, `results/reglas_v1/RESULTADOS.md`, `docs/revision_manual/` |
| Estado | 04 - Estado del TP | `docs/ESTADO.md` |
| Roadmap | 05 - Roadmap del TP (copia; la versión editable es el artefacto de Claude) | `docs/drive/roadmap.md` |
| Datos, textos y código | Solo los del v1 (01_obtencion_datos, 02_textos_normas) | Todo |

Regla (B32): todo documento nuevo se guarda en los dos lugares, y toda decisión, dificultad o hallazgo se registra en la bitácora del Drive.
