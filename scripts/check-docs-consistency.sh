#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="$(cat "$ROOT/VERSION")"
ERRORS=0

fail() { echo "FAIL: $1" >&2; ERRORS=$((ERRORS + 1)); }
ok()   { echo "OK:   $1"; }

echo "=== docs consistency check v${VERSION} ==="

# Version sync
TOML_VER="$(grep '^version' "$ROOT/pyproject.toml" | head -1 | sed 's/.*"\(.*\)".*/\1/')"
if [[ "$TOML_VER" == "$VERSION" ]]; then
  ok "pyproject.toml version matches VERSION ($VERSION)"
else
  fail "pyproject.toml version '$TOML_VER' != VERSION '$VERSION'"
fi

INIT_VER="$(python3 -c "from repo_signal import __version__; print(__version__)" 2>/dev/null || echo "")"
if [[ "$INIT_VER" == "$VERSION" ]]; then
  ok "repo_signal.__version__ matches VERSION ($VERSION)"
else
  fail "repo_signal.__version__ '$INIT_VER' != VERSION '$VERSION'"
fi

# Repo contract — the version surface the rest of the stack reads. Ungated, a
# stale value here fails mq-agent's stack contract gate rather than this repo's
# own checks, so the drift surfaces late and in someone else's CI.
if [[ ! -f "$ROOT/.mq/repo-contract.json" ]]; then
  fail ".mq/repo-contract.json is missing"
else
  CONTRACT_VER="$(python3 -c "import json; print(json.load(open('$ROOT/.mq/repo-contract.json')).get('version',''))" 2>/dev/null || echo "")"
  if [[ "$CONTRACT_VER" == "$VERSION" ]]; then
    ok ".mq/repo-contract.json version matches VERSION ($VERSION)"
  else
    fail ".mq/repo-contract.json version '$CONTRACT_VER' != VERSION '$VERSION'"
  fi
fi

# CHANGELOG
if grep -q "\[$VERSION\]" "$ROOT/CHANGELOG.md"; then
  ok "CHANGELOG.md contains [$VERSION]"
else
  fail "CHANGELOG.md missing [$VERSION] entry"
fi

# README release badge
if grep -q "v/release/MCamner/repo-signal" "$ROOT/README.md"; then
  ok "README.md has GitHub release badge"
else
  fail "README.md missing GitHub release badge"
fi

# README version status section
if grep -q "## v${VERSION} status" "$ROOT/README.md"; then
  ok "README.md has ## v${VERSION} status section"
else
  fail "README.md missing ## v${VERSION} status section"
fi

# Source readability guards
for spec in \
  "README.md:100" \
  "CHANGELOG.md:30" \
  "pyproject.toml:40" \
  "scripts/check-docs-consistency.sh:30" \
  "scripts/check-packaging.sh:20" \
  "release.sh:50"; do
  file="${spec%%:*}"
  min_lines="${spec##*:}"
  line_count="$(wc -l < "$ROOT/$file" | tr -d ' ')"
  if [[ "$line_count" -ge "$min_lines" ]]; then
    ok "$file has readable line structure ($line_count lines)"
  else
    fail "$file appears too short ($line_count lines, expected at least $min_lines)"
  fi
done

echo ""
if [[ "$ERRORS" -eq 0 ]]; then
  echo "=== All consistency checks passed ==="
else
  echo "=== $ERRORS check(s) failed ===" >&2
  exit 1
fi
