#!/bin/bash
# Hace git push desde la Mac con la clave SSH del usuario (B62).
# Lo usa Claude cuando su entorno no llega a GitHub: escribe este archivo, lo abre con doble clic
# desde el Finder (corre en Terminal) y lee .push_log.txt. También se puede abrir a mano.
cd "$(dirname "$0")/.."
git push 2>&1 | tee .push_log.txt
echo "EXIT=${PIPESTATUS[0]}" >> .push_log.txt
