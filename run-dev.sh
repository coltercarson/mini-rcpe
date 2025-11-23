#!/usr/bin/env bash
set -euo pipefail

# Convenience script to launch the FastAPI dev server with auto-reload.
# Requires dependencies from requirements.txt to be installed in the active environment.

# Load environment variables from .env if present so local dev matches Docker compose configuration.
if [[ -f .env ]]; then
	# shellcheck disable=SC1091
	set -o allexport
	source .env
	set +o allexport
fi

HOST_VALUE="${HOST:-${APP_HOST:-0.0.0.0}}"
PORT_VALUE="${PORT:-${APP_PORT:-8000}}"

python -m uvicorn app.main:app --reload --host "$HOST_VALUE" --port "$PORT_VALUE"
