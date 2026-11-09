#!/usr/bin/env bash
# Arma el grafo desde la salida estandar, lo carga en el Neo4j del TP y lo evalua leyendolo de vuelta.
#   bash cargar_y_evaluar_grafo.sh
# Requiere el contenedor neo4j-grafo-legal corriendo (docs/grafo.md) y la clave en .neo4j_password.
set -euo pipefail
cd "$(dirname "$0")"
URI="${NEO4J_URI:-bolt://localhost:7688}"
export NEO4J_PASSWORD="${NEO4J_PASSWORD:-$(cat .neo4j_password)}"

echo "== 1/3 Relaciones tipadas (salida estandar del parser de reglas v2)"
python scripts/09_relaciones.py > /dev/null
echo "== 2/3 Grafo: armado y carga en $URI"
python scripts/10_armar_grafo.py --uri "$URI" --borrar
echo "== 3/3 Evaluacion del grafo leido desde Neo4j"
python scripts/11_evaluar_grafo.py --uri "$URI"
