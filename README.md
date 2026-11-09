# grafo-legal

TP Integrador de Sistemas Inteligentes (UNNOBA, Ingeniería en Informática), Problemática III.

El TP extrae automáticamente las relaciones entre normas (modifica, sustituye, deroga, reglamenta…) a partir del texto de InfoLEG. Las evalúa contra las relaciones estructuradas que publica InfoLEG, que funcionan como gold standard, y arma un grafo trazable en Neo4j que se consulta en lenguaje natural (text-to-Cypher). Se comparan tres parsers: reglas (regex/AST), LLM puro e híbrido. La transferencia al digesto de la UNNOBA queda para la etapa de maduración.

## Estado

| Etapa | Estado |
|---|---|
| Corpus único: 340 normas, 775 pares (583 dev, 192 test) | congelado, snapshot InfoLEG 06/11/2026 (`data/corpus/SNAPSHOT.md`) |
| Textos InfoLEG (306 HTML) | descargados y verificados por SHA-256 |
| Dataset: 8.066 segmentos y 1.091 pares candidatos | `data/dataset/`, ficha en `docs/dataset.md` |
| Parser 1: reglas v1 | evaluado; falta la iteración v2 sobre el dev del corpus único |
| Parser 2: LLM puro / Parser 3: híbrido | pendiente |
| Grafo Neo4j + text-to-Cypher | pendiente |

El estado completo está en [`docs/ESTADO.md`](docs/ESTADO.md).

## Resultados del parser de reglas v1 sobre el corpus único

| Configuración | P dev | R dev | F1 dev | P test | R test | F1 test | F1 test sin pares del v1 |
|---|---|---|---|---|---|---|---|
| A. todas las menciones | 0,589 | 0,810 | 0,682 | 0,638 | 0,964 | 0,768 | 0,553 |
| B. solo articulado | 0,642 | 0,652 | 0,647 | 0,719 | 0,854 | 0,781 | 0,551 |
| **C. articulado + temporal** | 0,653 | 0,650 | 0,652 | **0,732** | **0,854** | **0,788** | **0,563** |
| D. C + verbo en el artículo | 0,708 | 0,482 | 0,574 | 0,735 | 0,651 | 0,691 | 0,543 |
| E. C + verbo en la oración | 0,792 | 0,360 | 0,495 | 0,856 | 0,526 | 0,652 | 0,509 |

Las reglas se diseñaron sobre el corpus v1, que es un subconjunto de este, y no se tocaron. El detalle está en [`results/reglas/RESULTADOS.md`](results/reglas/RESULTADOS.md).

## Estructura

```
data/
  corpus/               corpus único y gold, congelados (ver SNAPSHOT.md)
  dataset/              articulos.csv y pares_candidatos.csv (ver docs/dataset.md)
  textos/infoleg/       HTML de InfoLEG en UTF-8 + manifiesto con URL, fecha y SHA-256
  raw/                  zips del portal de datos (cache local, fuera de git)
  verificacion/         corpus regenerado para comparar con el congelado (fuera de git)
src/grafo_legal/
  fuentes/infoleg.py    adaptador: HTML -> texto -> artículos con zona
  catalogo.py           normalización de menciones a id_norma (mundo cerrado)
  extractores/          menciones (regex + alias) y reglas de relación
  evaluacion.py         P/R/F1 a nivel de par
  archivos.py           escritura atómica de salidas
scripts/                01 corpus · 02 textos · 03 extraer · 04 evaluar · 05 cobertura · 06 muestra Ley 14.250 · 07 dataset
results/reglas/         evidencias, métricas y errores del parser de reglas
docs/                   estado, decisiones, ficha del dataset, revisión manual y copia de los documentos del Drive
tools/                  utilidades (conversión de Google Docs a Markdown)
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

## Reglas del protocolo

- El gold nunca es entrada de un extractor. Solo lo leen `04_evaluar.py`, `05_cobertura_textual.py` y `07_armar_dataset.py` (para la etiqueta `en_gold`, nunca para los atributos).
- Las reglas se iteran solo sobre dev. Test se evalúa una vez por versión congelada del parser.
- Cada arista extraída lleva su evidencia: artículo, offsets, fragmento, método y reglas cumplidas.

## Documentación del TP

Toda la documentación está en dos lugares: la carpeta de Google Drive del TP y este repositorio (bitácora, B32). El estado general está en [`docs/ESTADO.md`](docs/ESTADO.md).

| Documento | Versión editable | Copia |
|---|---|---|
| Bitácora (decisiones, dificultades y hallazgos) | Drive: «00 - Bitácora del TP» | [`docs/drive/00_bitacora.md`](docs/drive/00_bitacora.md) |
| Obtención y construcción del corpus | Drive: «01 - …» | [`docs/drive/01_obtencion_corpus.md`](docs/drive/01_obtencion_corpus.md) |
| Profundidad del grafo y transferencia | Drive: «02 - …» | [`docs/drive/02_profundidad_y_transferencia.md`](docs/drive/02_profundidad_y_transferencia.md) |
| Pipeline, decisiones, resultados y revisión manual | este repo (README, `docs/decisiones.md`, `results/`, `docs/revision_manual/`) | Drive: «03 - Pipeline oficial, parser de reglas y revisión manual» |
| Estado del TP | este repo: [`docs/ESTADO.md`](docs/ESTADO.md) | Drive: «04 - Estado del TP» |
| Roadmap | [artefacto de Claude](https://claude.ai/artifact/Aai3uXH2hrR92fLDmYpvfM) | [`docs/drive/roadmap.md`](docs/drive/roadmap.md) y Drive: «05 - Roadmap del TP (copia)» |

Las copias de los documentos del Drive se regeneran con `tools/gdoc_a_md.py` a partir del JSON de la API de Google Docs.

## Fuentes

- Base de Datos Legislativos InfoLEG, Portal de Datos Abiertos de la Justicia Argentina: http://datos.jus.gob.ar/dataset/base-de-datos-legislativos-infoleg (publicada bajo la Resolución MJ 986/2016).
- Textos normativos: https://servicios.infoleg.gob.ar
