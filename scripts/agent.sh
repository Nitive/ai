#!/bin/bash
set -euo pipefail
root_dir="$(dirname "$(dirname "${BASH_SOURCE[0]}")")"

exec uv run "$root_dir/main.py" "$@"
