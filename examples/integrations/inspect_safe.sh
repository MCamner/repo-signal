#!/usr/bin/env bash
# inspect_safe.sh — safe repo-signal inspect.v1 consumption pattern.
# Exits 1 if repo-signal is missing, fails, or returns unknown schema.
set -euo pipefail

REPO="${1:-.}"

if ! command -v repo-signal >/dev/null 2>&1; then
  echo "repo-signal not found — run: pipx install repo-signal" >&2
  exit 1
fi

output=$(repo-signal inspect --json "$REPO" 2>/dev/null) || {
  echo "repo-signal inspect failed for: $REPO" >&2
  exit 1
}

schema=$(echo "$output" | python3 -c "import json,sys; print(json.load(sys.stdin).get('schema','unknown'))")
if [[ "$schema" != "inspect.v1" ]]; then
  echo "Unknown schema: $schema — upgrade repo-signal" >&2
  exit 1
fi

echo "$output"
