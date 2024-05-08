#!/bin/sh
# setup_environment.sh
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r backend/requirements.txt
cd frontend
npm install
npm run build
cd ..
