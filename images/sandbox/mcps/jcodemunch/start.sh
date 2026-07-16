#!/bin/bash
set -euo pipefail
root_dir="$(dirname "${BASH_SOURCE[0]}")"

export UV_PROJECT_ENVIRONMENT=.venv

mkdir -p ~/.code-index/
cat /opt/mcps/jcodemunch/config.jsonc > ~/.code-index/config.jsonc

"$root_dir/.venv/bin/jcodemunch-mcp"
