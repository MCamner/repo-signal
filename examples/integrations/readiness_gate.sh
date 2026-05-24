#!/usr/bin/env bash
# readiness_gate.sh — CI publish-readiness gate using repo-signal.
# Usage: ./readiness_gate.sh [path] [min-score]
set -euo pipefail

REPO="${1:-.}"
MIN_SCORE="${2:-14}"

if ! command -v repo-signal >/dev/null 2>&1; then
  echo "repo-signal not found — run: pipx install repo-signal" >&2
  exit 1
fi

output=$(repo-signal inspect --json "$REPO" 2>/dev/null) || {
  echo "repo-signal inspect failed" >&2
  exit 1
}

score=$(echo "$output" | python3 -c "
import json, sys
d = json.load(sys.stdin)
if d.get('schema') != 'inspect.v1':
    sys.exit(1)
pr = d.get('public_readiness', {})
print(pr.get('score', 0))
")

echo "Readiness score: $score (minimum: $MIN_SCORE)"

if [[ "$score" -lt "$MIN_SCORE" ]]; then
  echo "FAIL: score below threshold" >&2
  exit 1
fi

echo "PASS"
