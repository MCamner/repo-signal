#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

PYTHON_BIN="${PYTHON_BIN:-python3}"

command -v "$PYTHON_BIN" >/dev/null 2>&1 || fail "python3 not found"

[[ -f docs/PACKAGING.md ]] || fail "docs/PACKAGING.md missing"
[[ -f docs/TESTPYPI.md ]] || fail "docs/TESTPYPI.md missing"
[[ -x scripts/check-packaging.sh ]] || fail "scripts/check-packaging.sh missing or not executable"
[[ -x scripts/check-generated-examples.sh ]] || fail "scripts/check-generated-examples.sh missing or not executable"

echo "Running base packaging readiness check..."
scripts/check-packaging.sh

echo "Running generated examples check..."
scripts/check-generated-examples.sh

echo "Checking README and docs signals..."

grep -q "Packaging" README.md || fail "README.md should link to Packaging docs"
grep -q "TestPyPI" docs/TESTPYPI.md || fail "docs/TESTPYPI.md should mention TestPyPI"
grep -q "inspect.v1" docs/TESTPYPI.md || fail "docs/TESTPYPI.md should mention inspect.v1"
grep -q "pipx install repo-signal" docs/PACKAGING.md || fail "docs/PACKAGING.md should mention future pipx target"

echo "Checking build and twine validation..."

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

BUILD_VENV="$TMPDIR/build-venv"
DIST_DIR="$TMPDIR/dist"

"$PYTHON_BIN" -m venv "$BUILD_VENV"
"$BUILD_VENV/bin/python" -m pip install --upgrade pip >/dev/null
"$BUILD_VENV/bin/python" -m pip install build twine >/dev/null

"$BUILD_VENV/bin/python" -m build --outdir "$DIST_DIR"
"$BUILD_VENV/bin/python" -m twine check "$DIST_DIR"/*

echo "Checking distribution contents..."

WHEEL="$(find "$DIST_DIR" -maxdepth 1 -name '*.whl' | head -n 1)"
SDIST="$(find "$DIST_DIR" -maxdepth 1 -name '*.tar.gz' | head -n 1)"

[[ -n "$WHEEL" ]] || fail "wheel missing"
[[ -n "$SDIST" ]] || fail "sdist missing"

echo "Wheel: $(basename "$WHEEL")"
echo "Sdist: $(basename "$SDIST")"

echo "TestPyPI readiness check passed."
echo "No package was uploaded."
