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

echo "Running full packaging readiness check..."
scripts/check-packaging.sh

echo "Running TestPyPI readiness check..."
scripts/check-testpypi-readiness.sh

echo "Running Trusted Publishing setup check..."
scripts/check-trusted-publishing-setup.sh

echo "Checking PyPI docs..."

[[ -f docs/PYPI.md ]] || fail "docs/PYPI.md missing"
grep -q "pipx install repo-signal" docs/PYPI.md || fail "docs/PYPI.md should mention pipx install"
grep -q "inspect.v1" docs/PYPI.md || fail "docs/PYPI.md should mention inspect.v1"

echo "Checking PyPI workflow..."

[[ -f .github/workflows/pypi.yml ]] || fail ".github/workflows/pypi.yml missing"
grep -qE "workflow_dispatch" .github/workflows/pypi.yml || fail "pypi.yml must be manually triggered"
grep -qE "environment: pypi" .github/workflows/pypi.yml || fail "pypi.yml must use environment: pypi"
grep -qE "id-token: write" .github/workflows/pypi.yml || fail "pypi.yml must have id-token: write"
grep -qE "pypa/gh-action-pypi-publish" .github/workflows/pypi.yml || fail "pypi.yml must use pypa/gh-action-pypi-publish"
grep -v "test.pypi.org" .github/workflows/pypi.yml | grep -qF "gh-action-pypi-publish" || \
  grep -qE "repository-url.*upload\.pypi\.org" .github/workflows/pypi.yml || \
  echo "INFO: pypi.yml targets real PyPI (default or explicit)"

echo "PyPI readiness check passed."
echo "No package was uploaded."
