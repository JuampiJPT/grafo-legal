#!/usr/bin/env bash
# Corre el pipeline oficial completo desde cero en tu maquina (necesita internet).
#   bash correr_pipeline.sh
# Tarda unos minutos: baja ~3 zips del portal de datos y los textos nuevos de InfoLEG (1 s por pedido).
set -euo pipefail
cd "$(dirname "$0")"

python3 -m venv .venv
. .venv/bin/activate
pip install -q -r requirements.txt

echo "== 1/6 Corpus v2 (laboral ampliado) desde el snapshot actual de InfoLEG"
python scripts/01_obtener_corpus.py --version v2 --out data/corpus_v2

echo "== 2/6 Verificacion: corpus v1 con el snapshot actual (no toca data/corpus_v1, que esta congelado)"
python scripts/01_obtener_corpus.py --version v1 --out data/verificacion/corpus_v1_snapshot_actual

echo "== 3/6 Textos de InfoLEG para el corpus v2 (los 168 de v1 ya estan y no se re-descargan)"
python scripts/02_descargar_textos.py --corpus data/corpus_v2/corpus_normas.csv

echo "== 4/6 Muestra de la Ley 14.250"
python scripts/06_muestra_ley14250.py

echo "== 5/6 Parser de reglas + evaluacion sobre corpus v1 (congelado)"
python scripts/05_cobertura_textual.py --corpus data/corpus_v1
python scripts/03_extraer_reglas.py --corpus data/corpus_v1 --out results/reglas_v1
python scripts/04_evaluar.py --corpus data/corpus_v1 --res results/reglas_v1 --config-final C_articulado_temporal --incluir-test

echo "== 6/6 Cobertura textual del corpus v2 (solo dev; el test de v2 no se mira hasta congelar el parser)"
python scripts/05_cobertura_textual.py --corpus data/corpus_v2

echo "Listo. Revisa con: git status"
