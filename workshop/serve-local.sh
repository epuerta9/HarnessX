#!/usr/bin/env bash
# Start a keyless local inference backend for the workshop lab.
#
# Preferred path: Ollama (clean UX). Fallback: standalone llama.cpp llama-server
# on the model blobs (use when Ollama is broken/unavailable).
#
# Usage:
#   ./workshop/serve-local.sh ollama          # start Ollama (unsets LLAMA_API_KEY)
#   ./workshop/serve-local.sh llama <blob> <port>   # standalone llama-server
set -euo pipefail

# llama.cpp reads LLAMA_API_KEY as a mandatory server key — strip it so local
# calls don't 401. See workshop/README.md § Troubleshooting.
unset LLAMA_API_KEY LLAMA_ARG_API_KEY || true

MODE="${1:-ollama}"

case "$MODE" in
  ollama)
    echo "Starting Ollama with LLAMA_API_KEY unset..."
    # If the GUI app is already running with a bad env, stop it first:
    #   killall Ollama 2>/dev/null; launchctl unsetenv LLAMA_API_KEY
    exec ollama serve
    ;;
  llama)
    BLOB="${2:?path to GGUF blob required}"
    PORT="${3:-8088}"
    echo "Starting keyless llama-server on :$PORT for $BLOB"
    exec llama-server -m "$BLOB" --host 127.0.0.1 --port "$PORT" \
      -c 8192 --chat-template chatml -ngl 99
    ;;
  *)
    echo "unknown mode: $MODE (use 'ollama' or 'llama')" >&2; exit 1
    ;;
esac
