#!/usr/bin/env bash
# Corre el pipeline oficial completo en tu maquina.
#   bash correr_pipeline.sh
# Con los zips ya guardados en data/raw y los 306 textos en el repo, no hace ningun pedido a la red.
set -euo pipefail
cd "$(dirname "$0")"

python3 -m venv .venv
. .venv/bin/activate
pip install -q -r requirements.txt

echo "== 1/10 Verificacion del corpus: se regenera con los zips de data/raw y se compara con data/corpus"
python scripts/01_obtener_corpus.py --out data/verificacion/corpus_regenerado
for f in corpus_normas.csv gold_relaciones.csv; do
  if cmp -s "data/corpus/$f" "data/verificacion/corpus_regenerado/$f"; then
    echo "   $f identico al congelado"
  else
    echo "   ATENCION: $f difiere del congelado (otro snapshot de InfoLEG en data/raw)"
  fi
done

echo "== 2/10 Textos de InfoLEG (solo pide los que faltan en disco)"
python scripts/02_descargar_textos.py --corpus data/corpus/corpus_normas.csv

echo "== 3/10 Muestra de la Ley 14.250"
python scripts/06_muestra_ley14250.py

echo "== 4/10 Cobertura textual del gold (descriptiva, incluye test: ver B16)"
python scripts/05_cobertura_textual.py --corpus data/corpus

echo "== 5/10 Parser de reglas: v1 y v2 (las dos congeladas)"
python scripts/03_extraer_reglas.py --corpus data/corpus --out results/reglas
python scripts/03_extraer_reglas.py --parser v2 --corpus data/corpus --out results/reglas_v2

echo "== 6/10 Evaluacion (incluye test: solo versiones congeladas)"
python scripts/04_evaluar.py --corpus data/corpus --res results/reglas --config-final C_articulado_temporal --incluir-test
python scripts/04_evaluar.py --parser v2 --corpus data/corpus --res results/reglas_v2 --config-final F_visto_o_articulado_con_verbo_o_ley --incluir-test

echo "== 7/10 Dataset (articulos y pares candidatos)"
python scripts/07_armar_dataset.py --corpus data/corpus --res results/reglas_v2 --out data/dataset

echo "== 8/10 Clasificador de referencia (CV agrupada en dev; test una vez)"
python scripts/08_clasificador.py --incluir-test

echo "== 9/10 Grafo para Neo4j (solo arma los CSV; para cargar ver docs/grafo.md)"
python scripts/09_armar_grafo.py

echo "== 10/10 Tests"
pytest -q

echo "Listo. Revisa con: git status"
