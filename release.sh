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

text = Path("pyproject.toml").read_text(encoding="utf-8")
match = re.search(r'^version\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
print(match.group(1) if match else "missing pyproject.toml version")
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
