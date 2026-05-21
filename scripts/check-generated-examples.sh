#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

STRICT=0
if [[ "${1:-}" == "--strict" ]]; then
  STRICT=1
fi

run_cli() {
  python3 -m repo_signal.cli "$@"
}

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

check_file() {
  local file="$1"
  [[ -s "$file" ]] || fail "Missing or empty generated example: $file"
}

check_contains() {
  local file="$1"
  local pattern="$2"
  grep -qE "$pattern" "$file" || fail "Expected pattern '$pattern' in $file"
}

check_json_schema() {
  local file="$1"
  local expected_schema="$2"

  python3 - "$file" "$expected_schema" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
expected = sys.argv[2]

try:
    payload = json.loads(path.read_text(encoding="utf-8"))
except Exception as exc:
    raise SystemExit(f"{path}: invalid JSON: {exc}")

# Support both field naming conventions: "schema" (inspect.v1) and "schema_version" (doctor.v1)
actual = payload.get("schema") or payload.get("schema_version")
if actual != expected:
    raise SystemExit(f"{path}: expected schema {expected!r}, got {actual!r}")
PY
}

echo "Checking generated example files..."

required_files=(
  "examples/analyze/analyze.txt"
  "examples/inspect/inspect.txt"
  "examples/inspect/inspect.v1.json"
  "examples/doctor/doctor.txt"
  "examples/doctor/doctor.v1.json"
  "examples/repoaware/review.md"
  "docs/INSPECT_SCHEMA.md"
  "docs/DOCTOR_SCHEMA.md"
  "docs/INTEGRATIONS.md"
  "ROADMAP.md"
)

for file in "${required_files[@]}"; do
  check_file "$file"
done

echo "Checking generated example structure..."

check_contains "examples/inspect/inspect.txt" "REPO INSPECTION"
check_contains "examples/inspect/inspect.txt" "Recommended next commit"
check_contains "examples/analyze/analyze.txt" "repo-signal|Repository|REPO|ANALY"
check_contains "examples/doctor/doctor.txt" "doctor|Doctor|DOCTOR|readiness|Readiness"
check_contains "examples/repoaware/review.md" "repo|Repo|Repository|review|Review"

check_json_schema "examples/inspect/inspect.v1.json" "inspect.v1"
check_json_schema "examples/doctor/doctor.v1.json" "doctor.v1"

echo "Checking docs links..."

check_contains "README.md" "examples/inspect/inspect.v1.json"
check_contains "README.md" "docs/INSPECT_SCHEMA.md"
check_contains "README.md" "ROADMAP.md"
check_contains "README.md" "docs/INTEGRATIONS.md"
check_contains "ROADMAP.md" "Release readiness checklist"
check_contains "ROADMAP.md" "inspect.v1"

echo "Checking current CLI output..."

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

run_cli inspect . > "$tmpdir/inspect.txt"
run_cli inspect --json . > "$tmpdir/inspect.v1.json"
run_cli analyze . > "$tmpdir/analyze.txt"
run_cli doctor > "$tmpdir/doctor.txt"

check_contains "$tmpdir/inspect.txt" "REPO INSPECTION"
check_contains "$tmpdir/inspect.txt" "Recommended next commit"
check_json_schema "$tmpdir/inspect.v1.json" "inspect.v1"
check_contains "$tmpdir/analyze.txt" "repo-signal|Repository|REPO|ANALY"
check_contains "$tmpdir/doctor.txt" "doctor|Doctor|DOCTOR|readiness|Readiness"

if [[ "$STRICT" == "1" ]]; then
  echo "Running strict example comparison..."

  diff -u examples/inspect/inspect.txt "$tmpdir/inspect.txt"
  diff -u examples/inspect/inspect.v1.json "$tmpdir/inspect.v1.json"

  echo "Strict comparison passed."
else
  echo "Structural generated example check passed."
  echo "Tip: run scripts/check-generated-examples.sh --strict after regenerating examples on a clean tree."
fi
