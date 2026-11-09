#!/usr/bin/env bash
# Corre el pipeline oficial completo en tu maquina.
#   bash correr_pipeline.sh
# Con los zips ya guardados en data/raw y los 306 textos en el repo, no hace ningun pedido a la red.
set -euo pipefail
cd "$(dirname "$0")"

python3 -m venv .venv
. .venv/bin/activate
pip install -q -r requirements.txt

echo "== 1/7 Verificacion del corpus: se regenera con los zips de data/raw y se compara con data/corpus"
python scripts/01_obtener_corpus.py --out data/verificacion/corpus_regenerado
for f in corpus_normas.csv gold_relaciones.csv; do
  if cmp -s "data/corpus/$f" "data/verificacion/corpus_regenerado/$f"; then
    echo "   $f identico al congelado"
  else
    echo "   ATENCION: $f difiere del congelado (otro snapshot de InfoLEG en data/raw)"
  fi
done

echo "== 2/7 Textos de InfoLEG (solo pide los que faltan en disco)"
python scripts/02_descargar_textos.py --corpus data/corpus/corpus_normas.csv

echo "== 3/7 Muestra de la Ley 14.250"
python scripts/06_muestra_ley14250.py

echo "== 4/7 Cobertura textual del gold (descriptiva, incluye test: ver B16)"
python scripts/05_cobertura_textual.py --corpus data/corpus

echo "== 5/7 Parser de reglas"
python scripts/03_extraer_reglas.py --corpus data/corpus --out results/reglas

echo "== 6/7 Evaluacion (incluye test: solo para la version congelada de las reglas)"
python scripts/04_evaluar.py --corpus data/corpus --res results/reglas --config-final C_articulado_temporal --incluir-test

echo "== 7/7 Dataset (articulos y pares candidatos)"
python scripts/07_armar_dataset.py --corpus data/corpus --res results/reglas --out data/dataset

echo "Listo. Revisa con: git status"
