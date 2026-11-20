# grafo-legal

TP Integrador de Sistemas Inteligentes (UNNOBA, Ingeniería en Informática), Problemática III.

El TP extrae automáticamente las relaciones entre normas (modifica, sustituye, deroga, reglamenta…) a partir del texto de InfoLEG. Las evalúa contra las relaciones estructuradas que publica InfoLEG, que funcionan como gold standard, y arma un grafo trazable en Neo4j que se consulta en lenguaje natural (text-to-Cypher). Se comparan tres parsers: reglas (regex/AST), LLM puro e híbrido. La transferencia al digesto de la UNNOBA (PI4) se probó cambiando solo el adaptador: con 70 documentos anotados, el híbrido da F1 0,958 y las reglas 0,917 (`docs/pi4_digesto_unnoba.md`).

## Estado

| Etapa | Estado |
|---|---|
| Corpus único: 340 normas, 775 pares (583 dev, 192 test) | congelado, snapshot InfoLEG 06/11/2026 (`data/corpus/SNAPSHOT.md`) |
| Textos InfoLEG (306 HTML) | descargados y verificados por SHA-256 |
| Dataset: 8.066 segmentos y 1.091 pares candidatos | `data/dataset/`, ficha en `docs/dataset.md` |
| Parser 1: reglas | v2 congelado y evaluado (F1 test 0,828); v1 se conserva para comparar |
| Clasificador de referencia (scikit-learn) | evaluado (F1 test 0,823) |
| Salida estándar de relaciones tipadas | 3.277 relaciones del parser de reglas v2 (`docs/salida_estandar.md`) |
| Grafo Neo4j | se arma solo desde la salida estándar (`docs/grafo.md`); ida y vuelta idéntica, F1 0,828 contra InfoLEG en test (`results/evaluacion_grafo/`) |
| Evaluación por subtareas (detección, normalización, extracción) y taxonomía de errores | `results/subtareas/` |
| Explicación de cada error (causa y evidencia, caso por caso) | `results/errores_explicados/` |
| Modelo con contexto textual (TF-IDF) e híbrido reglas + modelo | evaluado: híbrido F1 test 0,839 (`results/modelo_contextual/`) |
| Tipo de relación: matriz de confusión y macro-F1 (78 casos) | macro-F1 0,672, exactitud 0,754 (`results/tipos/`) |
| Parser 2: LLM | implementado con caché reproducible (`docs/parser_llm.md`); falta correrlo con la clave de la API |
| Text-to-Cypher | pendiente |

El parser apunta a cualquier documento normativo: lo único que depende de la fuente es el adaptador que pasa el documento a texto.

El estado completo está en [`docs/ESTADO.md`](docs/ESTADO.md). Cómo funciona el parser y cómo está armado el grafo, contado paso a paso, está en [`docs/arquitectura_parser_y_grafo.md`](docs/arquitectura_parser_y_grafo.md).

## Resultados

| Parser | P test | R test | F1 dev | F1 test | F1 test sin pares del v1 |
|---|---|---|---|---|---|
| Reglas v1, configuración C | 0,732 | 0,854 | 0,652 | 0,788 | 0,563 |
| **Reglas v2, configuración F** | **0,785** | **0,875** | **0,733** | **0,828** | **0,671** |
| Reglas v3, configuración F3 (experimento) | 0,779 | 0,880 | 0,750 | 0,826 | 0,671 |
| **Parser LLM (Sonnet 5.5), regla F** | 0,763 | **0,938** | 0,741 | **0,841** | |
| **Parser híbrido en cascada** | 0,761 | 0,911 | **0,758** | 0,829 | |
| Híbrido reglas ∩ LLM | **0,804** | 0,875 | 0,735 | 0,838 | |
| Clasificador (random forest) | 0,799 | 0,849 | 0,728 (CV) | 0,823 | 0,683 |
| Modelo contextual (TF-IDF + superficie) | 0,760 | 0,807 | 0,751 (CV) | 0,783 | |
| **Híbrido reglas + modelo contextual** | 0,780 | 0,906 | 0,749 (CV) | **0,839** | |

Ninguna diferencia con las reglas v2 es significativa, salvo las de los modelos contextuales solos, que son peores: el intervalo del 95 % de la diferencia del híbrido va de −2,2 a +4,0 puntos (`results/comparacion/`). Cómo se compara con el gold: [`docs/comparacion_con_el_gold.md`](docs/comparacion_con_el_gold.md). Recorrido del código para la presentación: [`docs/guia_codigo.md`](docs/guia_codigo.md).

Parser híbrido en cascada (las reglas filtran y el LLM decide la zona gris): [`docs/parser_hibrido.md`](docs/parser_hibrido.md). Parser LLM: [`results/evaluacion_llm/RESULTADOS.md`](results/evaluacion_llm/RESULTADOS.md). El híbrido por intersección es la única mejora significativa sobre las reglas (+1,0 puntos, IC de +0,2 a +2,5), y el LLM sube la macro-F1 del tipo de 0,672 a 0,883. La v3 corrige la normalización: lee el año escrito como fecha, y la normalización ya no pierde pares. En test empata con la v2 ([`results/reglas_v3/RESULTADOS.md`](results/reglas_v3/RESULTADOS.md)). Cómo se detecta una relación, paso por paso: [`docs/como_se_detecta_una_relacion.md`](docs/como_se_detecta_una_relacion.md). Por qué falla cada error: [`docs/analisis_de_fallos.md`](docs/analisis_de_fallos.md).

Cada versión se diseñó solo sobre dev, y su test se evaluó una vez. El detalle está en [`results/reglas_v2/RESULTADOS.md`](results/reglas_v2/RESULTADOS.md), [`results/reglas/RESULTADOS.md`](results/reglas/RESULTADOS.md) y [`results/clasificador/RESULTADOS.md`](results/clasificador/RESULTADOS.md).

## Estructura

```
data/
  corpus/               corpus único y gold, congelados (ver SNAPSHOT.md)
  dataset/              articulos.csv y pares_candidatos.csv (ver docs/dataset.md)
  grafo/                nodos y relaciones para Neo4j (ver docs/grafo.md)
  textos/infoleg/       HTML de InfoLEG en UTF-8 + manifiesto con URL, fecha y SHA-256
  raw/                  zips del portal de datos (cache local, fuera de git)
  verificacion/         corpus regenerado para comparar con el congelado (fuera de git)
src/grafo_legal/
  fuentes/infoleg.py    adaptador: HTML -> texto -> artículos con zona
  catalogo.py           normalización de menciones a id_norma (mundo cerrado)
  extractores/          menciones (regex + alias), reglas de relación (reglas.py v1, reglas_v2.py, reglas_v3.py), parser híbrido (hibrido.py), tipado (relaciones.py) y parser LLM (llm.py)
  salida.py             formato de la salida estándar de los parsers
  grafo.py              modelo del grafo: construcción, carga en Neo4j y lectura de vuelta
  evaluacion.py         P/R/F1 a nivel de par
  archivos.py           escritura atómica de salidas
scripts/                01 corpus · 02 textos · 03 extraer · 04 evaluar · 05 cobertura · 06 muestra Ley 14.250
                        · 07 dataset · 08 clasificador · 09 relaciones · 10 grafo · 11 evaluar grafo
                        · 12 subtareas · 13 modelo contextual e híbrido · 14 parser LLM · 15 evaluar LLM
                        · 16 tipos · 17 tabla final con intervalos de confianza · 18 explicación de cada error
results/reglas/         reglas v1: evidencias, métricas y errores
results/reglas_v2/      reglas v2: evidencias, métricas y errores
results/clasificador/   clasificador: métricas, predicciones e importancia de atributos
results/relaciones/     salida estándar: relaciones tipadas de cada parser
results/evaluacion_grafo/  ida y vuelta del grafo y comparación con InfoLEG
results/subtareas/      detección, normalización y extracción por separado; taxonomía de errores
results/errores_explicados/ la causa y la evidencia de cada falso negativo y falso positivo
results/modelo_contextual/ modelo TF-IDF e híbrido reglas + modelo
results/tipos/          matriz de confusión y macro-F1 del tipo de relación
results/comparacion/    todos los métodos en test, con intervalos de confianza
results/relaciones_llm/ salida del parser LLM y caché de sus respuestas (cuando se corre)
docs/                   estado, decisiones, ficha del dataset, revisión manual y copia de los documentos del Drive
tools/                  utilidades (conversión entre Google Docs y Markdown)
tests/                  tests sin red (pytest)
```

## Cómo reproducir

Requiere Python 3.10 o superior. Con los zips en `data/raw` y los textos en el repo, no hace ningún pedido a la red:

```bash
bash correr_pipeline.sh
pytest -q
```

Si falta `data/raw`, el paso 1 descarga los zips del portal de datos. Con un snapshot distinto, el corpus regenerado no va a coincidir con el congelado, y el script lo avisa.

Para usar el dataset:

```python
import pandas as pd
art = pd.read_csv("data/dataset/articulos.csv")
pares = pd.read_csv("data/dataset/pares_candidatos.csv")
dev = pares[pares.split == "dev"]   # se entrena y ajusta solo con dev
```

Para cargar el grafo en el Neo4j del TP y evaluarlo (contenedor y clave en `docs/grafo.md`):

```bash
bash cargar_y_evaluar_grafo.sh
```

## Reglas del protocolo

- El gold nunca es entrada de un extractor. Solo lo leen `04_evaluar.py`, `05_cobertura_textual.py`, `07_armar_dataset.py` (para la etiqueta `en_gold`, nunca para los atributos), `08_clasificador.py` y `13_modelo_contextual.py` (para entrenar con dev), y `11`, `12`, `15`, `16` y `17` (para medir). El grafo y el parser LLM no lo leen.
- Las reglas se iteran solo sobre dev. Test se evalúa una vez por versión congelada del parser.
- Cada arista extraída lleva su evidencia: artículo, offsets, fragmento, método y reglas cumplidas.

## Documentación del TP

Toda la documentación está en dos lugares: la carpeta de Google Drive del TP y este repositorio (bitácora, B32). El estado general está en [`docs/ESTADO.md`](docs/ESTADO.md).

| Documento | Versión editable | Copia |
|---|---|---|
| Bitácora (decisiones, dificultades y hallazgos) | Drive: «00 - Bitácora del TP» | [`docs/drive/00_bitacora.md`](docs/drive/00_bitacora.md) |
| Obtención y construcción del corpus | Drive: «01 - …» | [`docs/drive/01_obtencion_corpus.md`](docs/drive/01_obtencion_corpus.md) |
| Profundidad del grafo y transferencia | Drive: «02 - …» | [`docs/drive/02_profundidad_y_transferencia.md`](docs/drive/02_profundidad_y_transferencia.md) |
| Pipeline, corpus, dataset, decisiones, resultados, grafo y revisión manual | este repo (README, `data/corpus/SNAPSHOT.md`, `docs/dataset.md`, `docs/decisiones.md`, `results/`, `docs/grafo.md`, `docs/revision_manual/`) | Drive: «03 - Pipeline oficial, corpus, dataset y parser de reglas» |
| Estado del TP | este repo: [`docs/ESTADO.md`](docs/ESTADO.md) | Drive: «04 - Estado del TP» |
| Parser y grafo: arquitectura y construcción paso a paso | este repo: [`docs/arquitectura_parser_y_grafo.md`](docs/arquitectura_parser_y_grafo.md) | Drive: «06 - Parser y grafo: arquitectura y construcción paso a paso» |
| Evaluación completa, parser LLM y guía del código | este repo: `docs/comparacion_con_el_gold.md`, `docs/parser_llm.md`, `docs/guia_codigo.md` | Drive: «07 - Evaluación completa, parser LLM y guía del código» |
| Análisis de fallos y cómo se detecta una relación | este repo: [`docs/analisis_de_fallos.md`](docs/analisis_de_fallos.md), [`docs/como_se_detecta_una_relacion.md`](docs/como_se_detecta_una_relacion.md) | Drive: «08 - Análisis de fallos y cómo se detecta una relación» |
| Roadmap | [artefacto de Claude](https://claude.ai/artifact/Aai3uXH2hrR92fLDmYpvfM) | [`docs/drive/roadmap.md`](docs/drive/roadmap.md) y Drive: «05 - Roadmap del TP (copia)» |

Las copias de los documentos del Drive se regeneran con `tools/gdoc_a_md.py` a partir del JSON de la API de Google Docs; `tools/md_a_gdoc.py` hace el camino inverso.

## Fuentes

- Base de Datos Legislativos InfoLEG, Portal de Datos Abiertos de la Justicia Argentina: http://datos.jus.gob.ar/dataset/base-de-datos-legislativos-infoleg (publicada bajo la Resolución MJ 986/2016).
- Textos normativos: https://servicios.infoleg.gob.ar
