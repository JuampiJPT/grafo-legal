# Estructura del repositorio

Este documento explica cómo está organizado el repositorio [github.com/JuampiJPT/grafo-legal](https://github.com/JuampiJPT/grafo-legal). Para cada carpeta dice qué hay, qué script lo genera y si va a git. Bitácora B63.

## La idea general

El repositorio sigue el recorrido del dato, en cinco pasos:

```
fuente (InfoLEG / digesto)  ──►  data/            corpus, gold, textos, dataset, grafos
                                   │
código                         src/grafo_legal/   adaptadores, extractores, salida, grafo, evaluación
                                   │
pasos numerados                scripts/01…32      cada paso lee de data/ o results/ y escribe ahí
                                   │
resultados                     results/           métricas, errores, relaciones, consolidado
                                   │
explicación                    docs/              estado, decisiones, bitácora, análisis
```

Cuatro reglas lo ordenan:
1. **El código reutilizable va en `src/grafo_legal/`**, y los scripts solo lo arman en un orden. Así un parser nuevo, o una fuente nueva, no obliga a tocar los scripts de los demás.
2. **Lo único que depende de la fuente es el adaptador** (`src/grafo_legal/fuentes/`). La PI4 lo probó: el digesto de la UNNOBA corre con los mismos extractores que InfoLEG.
3. **Cada resultado tiene un script que lo genera**, y `correr_pipeline.sh` los corre en orden.
4. **Lo que tiene datos personales o es muy grande no va a git** (`.gitignore`). El detalle está en la tabla de la sección 7.

## 1. Raíz

| Archivo | Qué es |
|---|---|
| `README.md` | Presentación, resultados principales, cómo reproducir y dónde está cada documento |
| `correr_pipeline.sh` | Corre todo el pipeline en orden. Sin red y sin clave de la API: usa los textos y las cachés del repo |
| `cargar_y_evaluar_grafo.sh` | Script histórico: carga el grafo de las reglas v2 en Neo4j **con `--borrar`**. Para cargar todo sin borrar nada, usar `scripts/30_cargar_y_evaluar_neo4j.sh` |
| `requirements.txt` | Dependencias de Python: pandas, numpy, scikit-learn, scipy, networkx, neo4j, anthropic, requests y pytest |
| `.gitignore` | Lo que no se sube, cada línea con su motivo |
| `.anthropic_key`, `.neo4j_password` | Claves locales. **Nunca van a git** |

## 2. `src/grafo_legal/`: el código

```
src/grafo_legal/
  fuentes/
    infoleg.py       adaptador de InfoLEG: HTML -> texto -> artículos con su zona (VISTO, CONSIDERANDO, articulado, anexo)
    unnoba.py        adaptador del digesto: texto del PDF -> partes -> menciones -> claves TIPO-EMISOR-N-AÑO
  catalogo.py        normalización: de una mención («Ley 20.744», «Decreto 390/76») al id_norma (mundo cerrado)
  extractores/
    menciones.py     detector de menciones: regex, listas («Leyes 20.744 y 24.013»), alias («Ley de Contrato de Trabajo»)
    reglas.py        reglas v1 (configuraciones A a E)
    reglas_v2.py     reglas v2 (configuración F, la de referencia)
    reglas_v3.py     reglas v3 (F3, experimento: año escrito como fecha)
    relaciones.py    tipo de relación por el verbo (SUSTITUYE, DEROGA, INCORPORA, MODIFICA, REGLAMENTA, CITA)
    llm.py           parser LLM: lotes, prompt, verificación de la cita, caché por huella del pedido
    hibrido.py       parser híbrido en cascada: las reglas filtran y el LLM decide la zona gris
  salida.py          formato de la salida estándar: una fila por relación, con su evidencia
  grafo.py           modelo del grafo: construir, cargar en Neo4j (MERGE) y leer de vuelta
  evaluacion.py      precisión, recall y F1 a nivel de par
  archivos.py        escritura atómica (no deja archivos a medio escribir)
```

El recorrido completo del código para la presentación está en `docs/guia_codigo.md`, y la arquitectura paso a paso en `docs/arquitectura_parser_y_grafo.md`.

## 3. `scripts/`: los pasos numerados

Cada script es un paso. El número da el orden y, a la vez, la cronología del TP.

| Bloque | Scripts | Qué hace | Escribe en |
|---|---|---|---|
| Corpus y textos | 01, 02, 05, 06 | Arma el corpus desde las bases del portal, baja los textos, mide la cobertura textual del gold y saca la muestra de la Ley 14.250 | `data/corpus/`, `data/textos/infoleg/`, `docs/revision_manual/` |
| Reglas | 03, 04 | Extrae con las reglas (v1, v2, v3) y evalúa contra el gold | `results/reglas*/` |
| Dataset y clasificador | 07, 08 | Arma segmentos y pares candidatos, y entrena el clasificador de referencia | `data/dataset/`, `results/clasificador/` |
| Salida estándar y grafo | 09, 10, 11 | Relaciones tipadas, grafo en CSV y evaluación del grafo leído de vuelta | `results/relaciones/`, `data/grafo*/`, `results/evaluacion_grafo*/` |
| Evaluación fina | 12, 13, 16, 17, 18, 19 | Subtareas, modelo contextual, tipos, tabla final con intervalos, explicación de cada error y ablación de la v3 | `results/subtareas*/`, `modelo_contextual/`, `tipos/`, `comparacion/`, `errores_explicados*/`, `reglas_v3/` |
| Parser LLM e híbrido | 14, 15, 20 | Corre y evalúa el parser LLM y el híbrido en cascada | `results/relaciones_llm/`, `evaluacion_llm/`, `hibrido/` |
| PI4 · digesto | 26, 27, 28, 29, 21, 22 | Catálogo, copias, texto y OCR, muestra, evaluación y grafos del digesto | `data/corpus_unnoba/`, `data/textos/unnoba/`, `results/pi4_unnoba/`, `data/grafo_unnoba_*/` |
| Neo4j y consolidado | 30, 23, 24, 25 | Carga todos los grafos sin borrar, consulta el manifiesto, consolida la LCT y la compara con InfoLEG | `results/evaluacion_grafo_neo4j/`, `results/consolidado/` |
| Informe y diagnóstico | 31, 32 | Figuras del informe de avance y curva de aprendizaje de los modelos supervisados (B68) | `docs/informe_avance/figuras/`, `results/curva_aprendizaje/` |
| Demo del grafo | 35 | Corre las consultas de la demo sobre Neo4j y guarda los resultados (B76) | `results/demo/` |
| Grafo de los clasificadores | 33, 34 | Arma y carga en Neo4j los grafos del random forest, del TF-IDF y del híbrido reglas + TF-IDF (B73) | `results/relaciones_modelos/`, `data/grafo_random_forest/`, `data/grafo_tfidf/`, `data/grafo_hibrido_tfidf/` |
| Utilidades | `firma_texto.py`, `firma_texto_navegador.js` | Firmas de texto (hash y MinHash) para comparar sin el archivo completo | `results/consolidado/evaluacion/` |

Los números 21 y 22 son anteriores a 26–29 porque la evaluación de la PI4 se escribió primero. Los pasos previos de preparación del digesto se pasaron a scripts después (B62). En `correr_pipeline.sh` corren en el orden correcto.

## 4. `data/`: entradas y estructuras intermedias

| Carpeta | Qué hay | Lo genera | En git |
|---|---|---|---|
| `corpus/` | Corpus único congelado: 340 normas, 775 pares del gold, procedencia y SHA-256 (`SNAPSHOT.md`) | 01, una sola vez | Sí |
| `raw/` | Zips del portal de datos del 06/11/2026 | 01 | No (67 MB) |
| `verificacion/` | Corpus regenerado para comparar con el congelado | `correr_pipeline.sh` | No |
| `textos/infoleg/` | 306 HTML de InfoLEG, `manifiesto_textos.csv` (URL, fecha y SHA-256) y el texto actualizado de la LCT (`25552_texact.html`) | 02, y a mano el texact | Sí |
| `dataset/` | `articulos.csv` (8.066 segmentos) y `pares_candidatos.csv` (1.091 pares) | 07 | Sí |
| `grafo/`, `grafo_v3/`, `grafo_llm/`, `grafo_hibrido/` | Nodos y relaciones para Neo4j, uno por parser de InfoLEG | 10 | Sí |
| `corpus_unnoba/` | Catálogo del digesto (912), muestra de 70, gold de la PI4 y `textos.csv` (qué documento es escaneado) | 26, 28, 29, y el gold a mano | Sí |
| `textos/unnoba/` | PDF, texto extraído, OCR, JSONL de la muestra y la lectura para anotar | El equipo (descarga), 27, 28, 29 | **No** (nombres y DNI) |
| `grafo_unnoba_reglas/`, `_llm/`, `_hibrido/` | Grafos del digesto | 22 | `normas.csv`, `articulos.csv` y `resumen.json`, sí; `relaciones.csv`, no |

## 5. `results/`: lo que se mide

Cada carpeta tiene un `metricas.json`. Las principales tienen además un `RESULTADOS.md` que se lee solo.

| Carpeta | Qué contiene |
|---|---|
| `reglas/`, `reglas_v2/`, `reglas_v3/` | Evidencias de cada par, métricas por configuración y errores. La v3 suma la ablación |
| `clasificador/`, `modelo_contextual/` | El clasificador de referencia y el modelo TF-IDF, con el híbrido reglas + modelo |
| `relaciones/`, `relaciones_llm/`, `relaciones_llm_piloto/`, `hibrido/` | La salida estándar de cada parser. Las de los parsers con LLM incluyen la caché (`cache/`) |
| `evaluacion_grafo*/` | Ida y vuelta del grafo y comparación con InfoLEG, en memoria (una carpeta por parser) y leyendo desde Neo4j (`evaluacion_grafo_neo4j/`) |
| `subtareas/`, `subtareas_v3/` | Detección, normalización y extracción por separado, con la taxonomía de errores |
| `errores_explicados/`, `errores_explicados_v3/` | Causa y evidencia de cada falso negativo y falso positivo |
| `tipos/` | Matriz de confusión y macro-F1 del tipo de relación (78 casos) |
| `comparacion/` | Todos los métodos en test, con intervalos de confianza por bootstrap |
| `curva_aprendizaje/` | Curva de aprendizaje de los modelos supervisados (script 32, B68): F1 y precisión promedio según la cantidad de datos de dev |
| `relaciones_modelos/` | Salida estándar de los clasificadores (script 33, B73): una tabla por modelo y metricas.json |
| `evaluacion_llm/` | Evaluación del parser LLM y sus híbridos |
| `pi4_unnoba/` | Evaluación sobre el digesto. Sus cachés quedan fuera de git |
| `consolidado/` | La LCT consolidada (`lct_consolidada.md` y `.json`), las operaciones aplicadas y no aplicadas, el ranking de profundidad, el manifiesto de Neo4j y la evaluación contra InfoLEG |

## 6. `docs/`: la explicación

| Documento | Para qué leerlo |
|---|---|
| `ESTADO.md` | Dónde está el TP, los hallazgos numerados y los pendientes. **Empezar por acá** |
| `conclusiones.md` | Todas las conclusiones, cómo se llegó a cada una y con qué evidencia |
| `estructura_repositorio.md` | Este documento |
| `reproducibilidad.md` | Qué se repite exacto y qué no |
| `decisiones.md` | Las decisiones D1 a D28, con su motivo |
| `drive/00_bitacora.md` | La bitácora completa (B01 a B71): decisiones, dificultades, cuestionamientos y hallazgos con fecha |
| `drive/01_…`, `02_…`, `07_…`, `roadmap.md` | Copias de los documentos del Drive |
| `arquitectura_parser_y_grafo.md`, `como_se_detecta_una_relacion.md`, `guia_codigo.md` | Cómo funciona el código, paso a paso |
| `dataset.md`, `salida_estandar.md`, `grafo.md` | Fichas del dataset, de la salida de los parsers y del modelo del grafo (con consultas Cypher) |
| `parser_llm.md`, `parser_hibrido.md` | Los dos parsers que usan el LLM |
| `comparacion_con_el_gold.md`, `analisis_de_fallos.md` | Cómo se compara con InfoLEG y por qué falla cada error |
| `pi4_digesto_unnoba.md`, `pi4_revision_gold.md` | La transferencia al digesto y la revisión de su gold |
| `consolidado_lct.md` | El texto consolidado de la LCT desde el grafo y su evaluación |
| `revision_manual/` | Las revisiones manuales en CSV: cobertura, Ley 14.250, falsos positivos, tipos y menciones |
| `informe_avance/` | El informe de avance para la entrega de la cursada: fuentes por sección, `armar_informe.py` y el `.docx` (B64, B70) |
| `presentacion/` | La presentación en PowerPoint para el coloquio, con notas del orador, y el script que la genera (B71) |
| `video/` | El video explicativo con Fusi, su guion y la narración: material interno del equipo (B65 a B69, B71) |

## 7. `tools/` y `tests/`

- `tools/gdoc_a_md.py` y `tools/md_a_gdoc.py`: pasan los documentos entre Google Docs y Markdown, para mantener el Drive y el repo iguales.
- `tools/digesto_unnoba/`: los descargadores del digesto, que corren en la computadora del equipo. Tiene su propio `README.md`.
- `tests/test_pipeline.py` y `tests/test_unnoba.py`: tests sin red (`pytest -q`).

## 8. Qué no va a git, y por qué

| Qué | Motivo |
|---|---|
| `.anthropic_key`, `.neo4j_password` | Claves |
| `data/raw/`, `data/verificacion/` | Tamaño; se regeneran o se guardan aparte |
| `*.pdf` | Los enunciados de la cátedra y los PDF del digesto |
| `data/textos/unnoba/` (texto, OCR, JSONL, lectura para anotar, copias del catálogo) | Nombres y DNI |
| `results/pi4_unnoba/cache_*` | Las respuestas del LLM citan fragmentos con nombres |
| `data/grafo_unnoba_*/relaciones.csv` | Los fragmentos pueden traer nombres |
| `data/corpus_unnoba/posgrado_lista.csv` | Resúmenes con nombres |

## 9. Dónde vive cada cosa: repo y Drive

Toda la documentación está en los dos lugares (B32). Los documentos de razonamiento, como la bitácora, se escriben primero en el Drive y se copian a `docs/drive/`. Los técnicos, como `ESTADO.md` o los RESULTADOS, se escriben en el repo y se copian al Drive. La correspondencia completa está en la tabla «Dónde está cada cosa» de `docs/ESTADO.md`.

El repositorio se trabaja en la Mac del equipo (`~/Documents/grafo legal`). El entorno de Claude lo edita a través de la carpeta conectada, y no llega a GitHub por SSH. Los commits se hacen en la Mac, y el push desde la Mac, con la clave del equipo.
