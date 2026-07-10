#!/bin/bash
set -euo pipefail

project_dir="${PROJECT_DIR:-$PWD}"

root_dir="$(dirname "${BASH_SOURCE[0]}")"
cd "$root_dir"

exec archcore mcp --project "$project_dir"
