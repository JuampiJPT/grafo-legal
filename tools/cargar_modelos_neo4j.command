#!/bin/bash
# Doble clic desde el Finder: levanta el contenedor de Neo4j del TP si está frenado y carga los
# grafos de los clasificadores (B73). Deja la salida en .carga_modelos_log.txt.
cd "$(dirname "$0")/.."
docker start neo4j-grafo-legal >/dev/null 2>&1 && sleep 8
bash scripts/34_cargar_modelos_neo4j.sh 2>&1 | tee .carga_modelos_log.txt
echo "EXIT=${PIPESTATUS[0]}" >> .carga_modelos_log.txt
