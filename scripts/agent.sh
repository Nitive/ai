#!/bin/bash

set -euo pipefail

prefix="$(echo ${PWD#/} | tr '/' '-')"

case "${1:-}" in
  agy)
    args="agy --dangerously-skip-permissions"
    ;;
  gemini)
    args="gemini --yolo --no-sandbox --allowed-mcp-server-names=context7 --skip-trust"
    ;;
  codex)
    args="codex --sandbox danger-full-access --ask-for-approval on-request"
    ;;
  caveman)
    args="caveman --caveman-mode full"
    ;;
  *)
    args=${@:-bash}
    ;;
esac

docker run --runtime=runsc --rm -it \
  -v "$prefix-home:$HOME" \
  -v "$HOME/.codex:$HOME/.codex" \
  -v "$HOME/.gemini:$HOME/.gemini" \
  -v "$HOME/.antigravity:$HOME/.antigravity" \
  -v "$HOME/.cave:$HOME/.cave" \
  -v "$HOME/.agents:$HOME/.agents:ro" \
  -v "$HOME/.agents/skills:$HOME/.codex/skills:ro" \
  -v "$HOME/.agents/skills:$HOME/.gemini/skills:ro" \
  -v "$PWD:$PWD" \
  -w "$PWD" \
  -e "TERM=xterm-kitty" \
  --add-host=host.docker.internal:host-gateway \
  local/sandbox:latest bash -c "echo Starting...; mise trust ~ &> /dev/null; mise trust &> /dev/null; $args"
