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

echo "== 9/10 Relaciones tipadas (salida estandar) y grafo (CSV; para cargar en Neo4j: cargar_y_evaluar_grafo.sh)"
python scripts/09_relaciones.py
python scripts/10_armar_grafo.py

echo "== 10/10 Evaluacion del grafo (copia en memoria)"
python scripts/11_evaluar_grafo.py

echo "== Evaluacion por subtareas, modelo contextual e hibrido, tipos y tabla final"
python scripts/12_evaluar_subtareas.py
python scripts/18_explicar_errores.py
# reglas v3 (experimento, B52): salidas aparte, no pisan las de v2
python scripts/03_extraer_reglas.py --parser v3 --corpus data/corpus --out results/reglas_v3
python scripts/04_evaluar.py --parser v3 --corpus data/corpus --res results/reglas_v3 --config-final F3_alias_con_verbo --incluir-test
python scripts/19_ablacion_v3.py
python scripts/09_relaciones.py --parser v3
python scripts/10_armar_grafo.py --relaciones results/relaciones/relaciones_reglas_v3.csv --out data/grafo_v3
python scripts/12_evaluar_subtareas.py --parser v3
python scripts/18_explicar_errores.py --parser v3
python scripts/13_modelo_contextual.py --incluir-test
if [ -f results/relaciones_llm/relaciones_llm.csv ]; then
  # sin clave usa solo la cache de results/relaciones_llm/cache (reproducible y sin costo)
  python scripts/14_parser_llm.py
  python scripts/15_evaluar_llm.py
  python scripts/10_armar_grafo.py --relaciones results/relaciones_llm/relaciones_llm.csv --out data/grafo_llm
fi
python scripts/20_parser_hibrido.py --incluir-test   # parser hibrido en cascada (usa la cache sin clave)
python scripts/10_armar_grafo.py --relaciones results/hibrido/relaciones_hibrido.csv --out data/grafo_hibrido
python scripts/16_evaluar_tipos.py
python scripts/17_comparar_metodos.py

# PI4: digesto UNNOBA (necesita el texto local de la muestra, que no va a git; usa la cache del LLM)
if [ -f data/textos/unnoba/muestra_pi4_textos.jsonl ]; then
  python scripts/21_pi4_unnoba.py
  python scripts/22_grafo_unnoba.py     # con --uri bolt://localhost:7688 los carga en Neo4j sin borrar nada
fi

echo "== Tests"
pytest -q

echo "Listo. Revisa con: git status"
