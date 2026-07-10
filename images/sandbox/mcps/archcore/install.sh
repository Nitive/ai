#!/bin/bash
set -euo pipefail

export MISE_DATA_DIR="/opt/mise"
export MISE_CONFIG_DIR="/opt/mise"
export MISE_CACHE_DIR="/opt/mise/cache"

mise trust
mise install
