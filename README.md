# grafo-legal

TP Integrador de Sistemas Inteligentes (UNNOBA, Ingeniería en Informática), Problemática III.

El TP extrae automáticamente las relaciones entre normas (modifica, sustituye, deroga, reglamenta…) a partir del texto de InfoLEG. Las evalúa contra las relaciones estructuradas que publica InfoLEG, que funcionan como gold standard, y arma un grafo trazable en Neo4j que se consulta en lenguaje natural (text-to-Cypher). Se comparan tres parsers: reglas (regex/AST), LLM puro e híbrido. La transferencia al digesto de la UNNOBA queda para la etapa de maduración.

## Estado

| Etapa | Estado |
|---|---|
| Corpus v1 y gold (183 normas, 402 pares) | congelado, snapshot InfoLEG 30/09/2026 |
| Textos InfoLEG del corpus v1 (168 HTML) | descargados y verificados por SHA-256 |
| Techo de recall textual | `data/corpus_v1/cobertura_textual_gold.csv` |
| Parser 1: reglas (regex/AST) | hecho, evaluado en dev y una vez en test |
| Corpus v2 laboral ampliado | script listo, falta correrlo con red (`correr_pipeline.sh`) |
| Parser 2: LLM puro / Parser 3: híbrido | pendiente |
| Grafo Neo4j + text-to-Cypher | pendiente |

## Resultados del parser de reglas (corpus v1)

Evaluación a nivel de par (norma origen → norma destino). La configuración final es C: menciones del articulado más el filtro temporal.

| Configuración | P dev | R dev | F1 dev | P test | R test | F1 test |
|---|---|---|---|---|---|---|
| A. todas las menciones | 0,625 | 0,811 | 0,706 | 0,732 | 0,945 | 0,825 |
| B. solo articulado | 0,674 | 0,746 | 0,708 | 0,778 | 0,913 | 0,841 |
| **C. articulado + temporal** | **0,692** | **0,742** | **0,716** | **0,784** | **0,913** | **0,844** |
| D. C + verbo en el artículo | 0,732 | 0,567 | 0,639 | 0,780 | 0,669 | 0,720 |
| E. C + verbo en la oración | 0,844 | 0,414 | 0,556 | 0,849 | 0,575 | 0,685 |

El detalle está en [`results/reglas_v1/RESULTADOS.md`](results/reglas_v1/RESULTADOS.md).

## Estructura

```
data/
  corpus_v1/            corpus y gold congelados (no se regeneran: ver SNAPSHOT.md)
  corpus_v2/            corpus laboral ampliado (lo genera correr_pipeline.sh)
  textos/infoleg/       HTML de InfoLEG en UTF-8 + manifiesto con URL, fecha y SHA-256
  raw/                  zips del portal de datos (cache local, fuera de git)
src/grafo_legal/
  fuentes/infoleg.py    adaptador: HTML -> texto -> artículos con zona
  catalogo.py           normalización de menciones a id_norma (mundo cerrado)
  extractores/          menciones (regex + alias) y reglas de relación
  evaluacion.py         P/R/F1 a nivel de par
scripts/                01 corpus · 02 textos · 03 extraer · 04 evaluar · 05 cobertura · 06 muestra Ley 14.250
results/reglas_v1/      evidencias, métricas y errores del parser de reglas
docs/                   decisiones, revisión manual
tests/                  tests sin red (pytest)
```

## Cómo reproducir

Requiere Python 3.10 o superior.

```bash
bash correr_pipeline.sh           # todo, con internet (portal de datos + InfoLEG)
```

Sin internet se puede reproducir la evaluación del corpus v1, porque los textos ya están en el repo:

```bash
pip install -r requirements.txt
python scripts/05_cobertura_textual.py --corpus data/corpus_v1
python scripts/03_extraer_reglas.py --corpus data/corpus_v1 --out results/reglas_v1
python scripts/04_evaluar.py --corpus data/corpus_v1 --res results/reglas_v1 --config-final C_articulado_temporal --incluir-test
pytest -q
```

## Reglas del protocolo

- El gold nunca es entrada de un extractor. Solo lo leen `04_evaluar.py` y `05_cobertura_textual.py`, que es un análisis del dataset.
- Las reglas se iteran solo sobre dev. Test se evalúa una vez por versión congelada del parser.
- Cada arista extraída lleva su evidencia: artículo, offsets, fragmento, método y reglas cumplidas.

## Documentación del TP

La bitácora, los informes por etapa y el roadmap están en la carpeta de Google Drive del TP. Las decisiones que afectan al código están resumidas en [`docs/decisiones.md`](docs/decisiones.md).

## Fuentes

- Base de Datos Legislativos InfoLEG, Portal de Datos Abiertos de la Justicia Argentina: http://datos.jus.gob.ar/dataset/base-de-datos-legislativos-infoleg (publicada bajo la Resolución MJ 986/2016).
- Textos normativos: https://servicios.infoleg.gob.ar
