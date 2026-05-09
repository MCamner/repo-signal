#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "RELEASE CHECK"
echo "============="
echo
echo "Repo: $ROOT_DIR"
echo

echo "Git status"
echo "----------"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git status --short
else
  echo "Not a Git repository"
fi
echo

echo "Version"
echo "-------"
python3 - <<'PY'
from pathlib import Path
import re
import sys

from repo_signal import __version__

version_file = Path("VERSION").read_text(encoding="utf-8").strip()

text = Path("pyproject.toml").read_text(encoding="utf-8")
match = re.search(r'^version\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
pyproject_version = match.group(1) if match else ""

print(f"VERSION: {version_file}")
print(f"pyproject.toml: {pyproject_version or 'missing'}")
print(f"repo_signal.__version__: {__version__}")

if not pyproject_version:
    print("ERROR: missing pyproject.toml version", file=sys.stderr)
    sys.exit(1)

if len({version_file, pyproject_version, __version__}) != 1:
    print("ERROR: version mismatch", file=sys.stderr)
    sys.exit(1)

changelog = Path("CHANGELOG.md")
if not changelog.exists():
    print("ERROR: CHANGELOG.md is missing", file=sys.stderr)
    sys.exit(1)

changelog_text = changelog.read_text(encoding="utf-8")
if f"## [{version_file}]" not in changelog_text:
    print(f"ERROR: CHANGELOG.md is missing section for {version_file}", file=sys.stderr)
    sys.exit(1)
PY
echo

echo "Tests"
echo "-----"
python3 -m unittest tests.test_cli
echo

echo "Doctor"
echo "------"
python3 -m repo_signal.cli doctor
echo

echo "README score"
echo "------------"
python3 -m repo_signal.cli readme-score .
echo

echo "Release check complete."
echo "This script does not publish, tag, or push."
