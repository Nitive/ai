#!/bin/bash
set -euo pipefail

mise use -g github:archcore-ai/cli@$(cat /opt/mcps/archcore/version.txt) >&2

project_dir="${PROJECT_DIR:-$PWD}"

exec mise exec -- archcore mcp --project "$project_dir"
