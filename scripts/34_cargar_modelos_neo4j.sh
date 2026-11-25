#!/usr/bin/env bash
# Carga en el Neo4j del TP los grafos de los clasificadores (random_forest, tfidf, hibrido_tfidf;
# scripts/33, B73) y los evalúa leyéndolos de vuelta. Sin --borrar: la carga es MERGE por fuente,
# así que conviven con reglas_v2, reglas_v3, llm, hibrido y unnoba_*.
# Requiere el contenedor neo4j-grafo-legal corriendo y .neo4j_password.
set -euo pipefail
cd "$(dirname "$0")/.."
URI="${NEO4J_URI:-bolt://localhost:7688}"
export NEO4J_PASSWORD="${NEO4J_PASSWORD:-$(cat .neo4j_password)}"
python3 scripts/33_grafo_modelos.py
for f in random_forest tfidf hibrido_tfidf; do
  rel="results/relaciones_modelos/relaciones_$f.csv"
  echo "===== $f"
  python3 scripts/10_armar_grafo.py --relaciones "$rel" --out "data/grafo_$f" --uri "$URI" | tail -1
  python3 scripts/11_evaluar_grafo.py --uri "$URI" --relaciones "$rel" --fuente "$f" --proyeccion no_cita \
      --out "results/evaluacion_grafo_neo4j/$f" | tail -12
done
