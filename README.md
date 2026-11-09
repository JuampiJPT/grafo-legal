# grafo-legal

TP Integrador de Sistemas Inteligentes (UNNOBA, Ingeniería en Informática), Problemática III.

El TP extrae automáticamente las relaciones entre normas (modifica, sustituye, deroga, reglamenta…) a partir del texto de InfoLEG. Las evalúa contra las relaciones estructuradas que publica InfoLEG, que funcionan como gold standard, y arma un grafo trazable en Neo4j que se consulta en lenguaje natural (text-to-Cypher). Se comparan tres parsers: reglas (regex/AST), LLM puro e híbrido. La transferencia al digesto de la UNNOBA queda para la etapa de maduración.

## Estado

| Etapa | Estado |
|---|---|
| Corpus único: 340 normas, 775 pares (583 dev, 192 test) | congelado, snapshot InfoLEG 06/11/2026 (`data/corpus/SNAPSHOT.md`) |
| Textos InfoLEG (306 HTML) | descargados y verificados por SHA-256 |
| Dataset: 8.066 segmentos y 1.091 pares candidatos | `data/dataset/`, ficha en `docs/dataset.md` |
| Parser 1: reglas | v2 congelado y evaluado (F1 test 0,828); v1 se conserva para comparar |
| Clasificador de referencia (scikit-learn) | evaluado (F1 test 0,823) |
| Grafo Neo4j | archivos armados y verificados (`data/grafo/`, `docs/grafo.md`); falta la primera carga en Neo4j |
| Parser 2: LLM puro / Parser 3: híbrido / text-to-Cypher | pendiente |

El estado completo está en [`docs/ESTADO.md`](docs/ESTADO.md).

## Resultados

| Parser | P test | R test | F1 dev | F1 test | F1 test sin pares del v1 |
|---|---|---|---|---|---|
| Reglas v1, configuración C | 0,732 | 0,854 | 0,652 | 0,788 | 0,563 |
| **Reglas v2, configuración F** | **0,785** | **0,875** | **0,733** | **0,828** | **0,671** |
| Clasificador (random forest) | 0,799 | 0,849 | 0,728 (CV) | 0,823 | 0,683 |

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
  extractores/          menciones (regex + alias) y reglas de relación (reglas.py v1, reglas_v2.py)
  evaluacion.py         P/R/F1 a nivel de par
  archivos.py           escritura atómica de salidas
scripts/                01 corpus · 02 textos · 03 extraer · 04 evaluar · 05 cobertura · 06 muestra Ley 14.250
                        · 07 dataset · 08 clasificador · 09 grafo
results/reglas/         reglas v1: evidencias, métricas y errores
results/reglas_v2/      reglas v2: evidencias, métricas y errores
results/clasificador/   clasificador: métricas, predicciones e importancia de atributos
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

Para cargar el grafo en un Neo4j 5 local:

```bash
export NEO4J_PASSWORD=...
python scripts/09_armar_grafo.py --uri bolt://localhost:7687 --user neo4j --borrar
```

## Reglas del protocolo

- El gold nunca es entrada de un extractor. Solo lo leen `04_evaluar.py`, `05_cobertura_textual.py`, `07_armar_dataset.py` (para la etiqueta `en_gold`, nunca para los atributos), `08_clasificador.py` (para medir) y `09_armar_grafo.py` (para la relación `RELACION_INFOLEG`, separada de lo extraído).
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
| Roadmap | [artefacto de Claude](https://claude.ai/artifact/Aai3uXH2hrR92fLDmYpvfM) | [`docs/drive/roadmap.md`](docs/drive/roadmap.md) y Drive: «05 - Roadmap del TP (copia)» |

Las copias de los documentos del Drive se regeneran con `tools/gdoc_a_md.py` a partir del JSON de la API de Google Docs; `tools/md_a_gdoc.py` hace el camino inverso.

## Fuentes

- Base de Datos Legislativos InfoLEG, Portal de Datos Abiertos de la Justicia Argentina: http://datos.jus.gob.ar/dataset/base-de-datos-legislativos-infoleg (publicada bajo la Resolución MJ 986/2016).
- Textos normativos: https://servicios.infoleg.gob.ar
