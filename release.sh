#!/usr/bin/env bash
#
# release.sh — repo-signal release workflow
#
# Usage:
#   ./release.sh             # run all checks, no publish
#   ./release.sh --publish   # run checks, tag, push, create GitHub release
#
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PUBLISH=0
for arg in "$@"; do
  [[ "$arg" == "--publish" || "$arg" == "--github-release" ]] && PUBLISH=1
done

if [[ -z "${PYTHON_BIN:-}" ]]; then
  if [[ -x ".venv/bin/python" ]]; then
    PYTHON_BIN=".venv/bin/python"
  else
    PYTHON_BIN="python3"
  fi
fi

PASS=0
FAIL=0

ok()   { echo "  [OK]   $*"; (( PASS++ )) || true; }
warn() { echo "  [WARN] $*"; }
fail() { echo "  [FAIL] $*" >&2; (( FAIL++ )) || true; }

section() {
  echo
  echo "$*"
  printf '%0.s-' $(seq 1 ${#1})
  echo
}

# ── Version sync ─────────────────────────────────────────────────────────────

section "Version"

VERSION_FILE="$(cat VERSION 2>/dev/null | tr -d '[:space:]')"
PYPROJECT_VERSION="$("$PYTHON_BIN" -c "
import re, sys
t = open('pyproject.toml').read()
m = re.search(r'^version\s*=\s*\"([^\"]+)\"', t, re.MULTILINE)
print(m.group(1) if m else '')
")"
INIT_VERSION="$("$PYTHON_BIN" -c "from repo_signal import __version__; print(__version__)")"

echo "  VERSION:              $VERSION_FILE"
echo "  pyproject.toml:       $PYPROJECT_VERSION"
echo "  repo_signal.__version__: $INIT_VERSION"

if [[ "$VERSION_FILE" == "$PYPROJECT_VERSION" && "$VERSION_FILE" == "$INIT_VERSION" ]]; then
  ok "All three version sources agree: $VERSION_FILE"
else
  fail "Version mismatch — update VERSION, pyproject.toml, and repo_signal/__init__.py"
fi

# The contract carries the version the rest of the MQ stack reads. release.sh
# validated VERSION/pyproject/__version__ but not this, so a release could tag
# with the contract behind — v1.4.1 shipped VERSION=1.4.1, contract=1.4.0, and
# the drift failed the stack contract gate in mq-agent's CI instead of here.
CONTRACT_VERSION="$("$PYTHON_BIN" -c "
import json
try:
    print(json.load(open('.mq/repo-contract.json'))['version'])
except Exception:
    print('')
")"
echo "  .mq/repo-contract.json:  $CONTRACT_VERSION"
if [[ "$VERSION_FILE" == "$CONTRACT_VERSION" ]]; then
  ok ".mq/repo-contract.json matches VERSION: $VERSION_FILE"
else
  fail ".mq/repo-contract.json version '$CONTRACT_VERSION' != VERSION '$VERSION_FILE' — bump it before releasing"
fi

# ── CHANGELOG ────────────────────────────────────────────────────────────────

section "CHANGELOG"

if grep -qF "## [$VERSION_FILE]" CHANGELOG.md; then
  ok "CHANGELOG.md has entry for $VERSION_FILE"
else
  fail "CHANGELOG.md is missing section for $VERSION_FILE"
fi

# ── Git state ─────────────────────────────────────────────────────────────────

section "Git state"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  DIRTY="$(git status --short)"
  if [[ -z "$DIRTY" ]]; then
    ok "Working tree is clean"
  else
    fail "Working tree has uncommitted changes — commit or stash before release"
    git status --short | sed 's/^/    /'
  fi

  BRANCH="$(git rev-parse --abbrev-ref HEAD)"
  if [[ "$BRANCH" == "main" ]]; then
    ok "On branch main"
  else
    warn "On branch $BRANCH (expected main)"
  fi

  if git tag | grep -qF "v$VERSION_FILE"; then
    fail "Tag v$VERSION_FILE already exists"
  else
    ok "Tag v$VERSION_FILE does not yet exist"
  fi
else
  fail "Not a Git repository"
fi

# ── Tests ────────────────────────────────────────────────────────────────────

section "Tests"

if "$PYTHON_BIN" -m pytest -q 2>&1 | tee /tmp/repo-signal-release-pytest.txt | tail -1 | grep -qE "passed"; then
  PASSED="$(grep -E "passed" /tmp/repo-signal-release-pytest.txt | tail -1)"
  ok "Tests: $PASSED"
else
  fail "Tests failed"
  cat /tmp/repo-signal-release-pytest.txt
fi

# ── Packaging readiness ──────────────────────────────────────────────────────

section "Packaging readiness"

if PYTHON_BIN="$PYTHON_BIN" scripts/check-packaging.sh > /tmp/repo-signal-release-packaging.txt 2>&1; then
  ok "Packaging check passed"
else
  fail "Packaging check failed"
  cat /tmp/repo-signal-release-packaging.txt
fi

# ── Generated examples ───────────────────────────────────────────────────────

section "Generated examples"

if scripts/check-generated-examples.sh > /tmp/repo-signal-release-examples.txt 2>&1; then
  ok "Generated examples check passed"
else
  fail "Generated examples check failed"
  cat /tmp/repo-signal-release-examples.txt
fi

# ── inspect --json schema ────────────────────────────────────────────────────

section "inspect --json schema"

SCHEMA="$("$PYTHON_BIN" -m repo_signal.cli inspect --json . | "$PYTHON_BIN" -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('schema', ''))
")"

if [[ "$SCHEMA" == "inspect.v1" ]]; then
  ok "inspect --json returns schema: inspect.v1"
else
  fail "inspect --json returned unexpected schema: '$SCHEMA'"
fi

# ── doctor --json schema ─────────────────────────────────────────────────────

section "doctor --json schema"

DOCTOR_SCHEMA="$("$PYTHON_BIN" -m repo_signal.cli doctor --json . | "$PYTHON_BIN" -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('schema', ''))
")"

if [[ "$DOCTOR_SCHEMA" == "doctor.v1" ]]; then
  ok "doctor --json returns schema: doctor.v1"
else
  fail "doctor --json returned unexpected schema: '$DOCTOR_SCHEMA'"
fi

# ── report --format json schema ───────────────────────────────────────────────

section "report --format json schema"

REPORT_SCHEMA="$("$PYTHON_BIN" -m repo_signal.cli report . --format json | "$PYTHON_BIN" -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('schema', ''))
")"

if [[ "$REPORT_SCHEMA" == "report.v1" ]]; then
  ok "report --format json returns schema: report.v1"
else
  fail "report --format json returned unexpected schema: '$REPORT_SCHEMA'"
fi

# ── suggest --format json schema ──────────────────────────────────────────────

section "suggest --format json schema"

SUGGEST_SCHEMA="$("$PYTHON_BIN" -m repo_signal.cli suggest . --format json | "$PYTHON_BIN" -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('schema', ''))
")"

if [[ "$SUGGEST_SCHEMA" == "suggest.v1" ]]; then
  ok "suggest --format json returns schema: suggest.v1"
else
  fail "suggest --format json returned unexpected schema: '$SUGGEST_SCHEMA'"
fi

# ── Publish checklist ────────────────────────────────────────────────────────

section "Publish checklist"

SCORE="$("$PYTHON_BIN" -m repo_signal.cli publish-checklist . 2>&1 | grep -E "Score:" | head -1 | grep -oE "[0-9]+/[0-9]+")"
if "$PYTHON_BIN" -m repo_signal.cli publish-checklist . --fail-under 16 > /tmp/repo-signal-release-checklist.txt 2>&1; then
  ok "Publish checklist: ${SCORE:-passed}"
else
  fail "Publish checklist below threshold"
  tail -5 /tmp/repo-signal-release-checklist.txt
fi

# ── README score ─────────────────────────────────────────────────────────────

section "README score"

"$PYTHON_BIN" -m repo_signal.cli readme-score . 2>&1 | tail -3

# ── Wiki Command-Reference ───────────────────────────────────────────────────

section "Wiki Command-Reference"

if "$PYTHON_BIN" tools/generate_wiki_command_ref.py > /tmp/repo-signal-wiki.txt 2>&1; then
  WIKI_TMP="$(mktemp -d)"
  if git clone --quiet git@github.com:MCamner/repo-signal.wiki.git "$WIKI_TMP" 2>/dev/null; then
    GENERATED="$HOME/repo-signal.wiki/Command-Reference.md"
    [[ -f "$GENERATED" ]] || GENERATED="$WIKI_TMP/Command-Reference.md"
    cp "$GENERATED" "$WIKI_TMP/Command-Reference.md" 2>/dev/null || true
    cd "$WIKI_TMP"
    git add Command-Reference.md
    if git diff --cached --quiet; then
      ok "Wiki Command-Reference unchanged"
    elif [[ "$PUBLISH" == "1" ]]; then
      git commit -m "Update Command-Reference for v${VERSION_FILE}"
      git push --quiet
      ok "Wiki Command-Reference pushed"
    else
      warn "Wiki Command-Reference has changes — will be pushed on --publish"
    fi
    cd "$ROOT_DIR"
    rm -rf "$WIKI_TMP"
  else
    warn "Could not clone wiki repo — skipping"
    rm -rf "$WIKI_TMP"
  fi
else
  warn "Wiki generator failed — skipping"
fi

# ── Summary ───────────────────────────────────────────────────────────────────

echo
echo "================================================"
echo "RELEASE CHECK SUMMARY"
echo "================================================"
echo "  Version:  $VERSION_FILE"
echo "  Passed:   $PASS"
echo "  Failed:   $FAIL"
echo "================================================"

if [[ "$FAIL" -gt 0 ]]; then
  echo
  echo "Release blocked — fix the failures above before publishing."
  exit 1
fi

echo
echo "All checks passed."

# ── Publish ───────────────────────────────────────────────────────────────────

if [[ "$PUBLISH" == "0" ]]; then
  echo
  echo "Dry run complete. To tag and publish:"
  echo "  ./release.sh --publish"
  exit 0
fi

echo
echo "Publishing v${VERSION_FILE}..."

git tag -m "v${VERSION_FILE}" "v${VERSION_FILE}"
git push
git push origin "v${VERSION_FILE}"

NOTES="$("$PYTHON_BIN" - "$VERSION_FILE" <<'PY'
import re, sys
from pathlib import Path

version = sys.argv[1]
text = Path("CHANGELOG.md").read_text(encoding="utf-8")
pattern = rf"## \[{re.escape(version)}\][^\n]*\n(.*?)(?=\n## \[|\Z)"
m = re.search(pattern, text, re.DOTALL)
if m:
    print(m.group(1).strip())
else:
    print(f"Release {version}")
PY
)"

gh release create "v${VERSION_FILE}" \
  --title "v${VERSION_FILE}" \
  --notes "$NOTES"

echo
echo "Released: https://github.com/MCamner/repo-signal/releases/tag/v${VERSION_FILE}"
