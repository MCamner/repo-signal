#!/usr/bin/env bash
set -euo pipefail

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

check_file() {
  [[ -f "$1" ]] || fail "Missing file: $1"
}

check_contains() {
  local file="$1"
  local pattern="$2"
  grep -qE "$pattern" "$file" || fail "Expected '$pattern' in $file"
}

echo "Checking Trusted Publishing setup docs and workflow..."

check_file "docs/TRUSTED_PUBLISHING.md"
check_file "docs/TESTPYPI.md"
check_file ".github/workflows/testpypi.yml"

check_contains "docs/TRUSTED_PUBLISHING.md" "MCamner"
check_contains "docs/TRUSTED_PUBLISHING.md" "repo-signal"
check_contains "docs/TRUSTED_PUBLISHING.md" "testpypi.yml"
check_contains "docs/TRUSTED_PUBLISHING.md" "Environment name"
check_contains "docs/TRUSTED_PUBLISHING.md" "testpypi"
check_contains "docs/TRUSTED_PUBLISHING.md" "inspect.v1"

check_contains ".github/workflows/testpypi.yml" "workflow_dispatch"
check_contains ".github/workflows/testpypi.yml" "id-token: write"
check_contains ".github/workflows/testpypi.yml" "environment: testpypi"
check_contains ".github/workflows/testpypi.yml" "pypa/gh-action-pypi-publish@release/v1"
check_contains ".github/workflows/testpypi.yml" "repository-url: https://test.pypi.org/legacy/"
check_contains ".github/workflows/testpypi.yml" "publish_to_testpypi"

echo "Trusted Publishing setup check passed."
echo "No package was uploaded."
