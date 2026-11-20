#!/usr/bin/env bash
# Carga TODOS los grafos en el Neo4j del TP y los evalúa leyéndolos de vuelta (B59, B60).
#   bash scripts/30_cargar_y_evaluar_neo4j.sh
# A diferencia de cargar_y_evaluar_grafo.sh, NO usa --borrar: la carga es MERGE por fuente, así que
# se puede repetir sin perder nada y conviven InfoLEG (reglas_v2, reglas_v3, llm, hibrido) y el
# digesto UNNOBA (unnoba_*). Requiere el contenedor neo4j-grafo-legal corriendo y .neo4j_password.
set -euo pipefail
cd "$(dirname "$0")/.."
URI="${NEO4J_URI:-bolt://localhost:7688}"
export NEO4J_PASSWORD="${NEO4J_PASSWORD:-$(cat .neo4j_password)}"
for par in "reglas_v2:results/relaciones/relaciones_reglas_v2.csv" \
           "reglas_v3:results/relaciones/relaciones_reglas_v3.csv" \
           "llm:results/relaciones_llm/relaciones_llm.csv" \
           "hibrido:results/hibrido/relaciones_hibrido.csv"; do
  f="${par%%:*}"; rel="${par#*:}"
  echo "===== $f"
  # los CSV del grafo van a una carpeta temporal: los de data/grafo* no se tocan
  python3 scripts/10_armar_grafo.py --relaciones "$rel" --out "/tmp/grafo_eval_$f" --uri "$URI" | tail -1
  python3 scripts/11_evaluar_grafo.py --uri "$URI" --relaciones "$rel" --fuente "$f" \
      --out "results/evaluacion_grafo_neo4j/$f" | tail -30
done
# digesto UNNOBA (necesita el texto local de la muestra)
if [ -f data/textos/unnoba/muestra_pi4_textos.jsonl ]; then
  echo "===== digesto UNNOBA"
  python3 scripts/22_grafo_unnoba.py --uri "$URI" | tail -5
fi
