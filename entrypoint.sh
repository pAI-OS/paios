#!/bin/bash
set -e

if [ -d "paios/.venv/" ]; then
    . paios/.venv/bin/activate

else
    echo "Error: el entorno virtual no se encontró en 'paois/.venv'"
    exit 1
fi

python -m paios
