#!/bin/bash
set -euo pipefail
root_dir="$(dirname "${BASH_SOURCE[0]}")"

export UV_PROJECT_ENVIRONMENT=.venv

exec "$root_dir/.venv/bin/python" "$root_dir/import.py"
