#!/bin/bash
set -euo pipefail
root_dir="$(dirname "${BASH_SOURCE[0]}")"

export UV_PROJECT_ENVIRONMENT=.venv

"$root_dir/.venv/bin/jcodemunch-mcp"
