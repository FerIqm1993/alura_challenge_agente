#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8501}"

cd "$(dirname "$0")/.."
source .venv/bin/activate

streamlit run app.py --server.address=0.0.0.0 --server.port="$PORT"
