#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

run_cli() {
  python3 -m repo_signal.cli "$@"
}

mkdir -p \
  examples/analyze \
  examples/inspect \
  examples/doctor \
  examples/repoaware \
  examples/demo

echo "Generating analyze example..."
run_cli analyze . > examples/analyze/analyze.txt

echo "Generating inspect examples..."
run_cli inspect . > examples/inspect/inspect.txt
run_cli inspect --json . > examples/inspect/inspect.v1.json
python3 -m json.tool examples/inspect/inspect.v1.json >/tmp/repo-signal-inspect-json-check.json

echo "Generating doctor text example..."
run_cli doctor > examples/doctor/doctor.txt

echo "Generating doctor JSON example..."
if run_cli doctor --json > examples/doctor/doctor.v1.json.tmp 2>/tmp/repo-signal-doctor-json.err; then
  mv examples/doctor/doctor.v1.json.tmp examples/doctor/doctor.v1.json
elif run_cli doctor --format json > examples/doctor/doctor.v1.json.tmp 2>/tmp/repo-signal-doctor-json.err; then
  mv examples/doctor/doctor.v1.json.tmp examples/doctor/doctor.v1.json
else
  rm -f examples/doctor/doctor.v1.json.tmp
  echo "WARN: Could not regenerate doctor.v1.json. Existing file was left unchanged." >&2
  cat /tmp/repo-signal-doctor-json.err >&2 || true
fi

if [[ -f examples/doctor/doctor.v1.json ]]; then
  python3 -m json.tool examples/doctor/doctor.v1.json >/tmp/repo-signal-doctor-json-check.json
fi

echo "Generating RepoAware review example..."
if run_cli repoaware --mode review --format markdown "what should I inspect first" > examples/repoaware/review.md.tmp 2>/tmp/repo-signal-repoaware.err; then
  mv examples/repoaware/review.md.tmp examples/repoaware/review.md
else
  rm -f examples/repoaware/review.md.tmp
  echo "WARN: Could not regenerate RepoAware review. Existing file was left unchanged." >&2
  cat /tmp/repo-signal-repoaware.err >&2 || true
fi

echo "Generating demo bundle..."
if run_cli demo --generate . --output examples/demo --force; then
  echo "Demo bundle generated."
else
  echo "WARN: demo generation failed. Existing demo files were left unchanged." >&2
fi

echo "Validating generated examples..."
scripts/check-generated-examples.sh

echo "Generated examples updated."
