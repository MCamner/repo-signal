#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

if [[ -z "${PYTHON_BIN:-}" ]]; then
  for candidate in python3.12 python3.11 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
      PYTHON_BIN="$candidate"
      break
    fi
  done
fi

[[ -n "${PYTHON_BIN:-}" ]] || fail "Python 3.11 or newer not found"
command -v "$PYTHON_BIN" >/dev/null 2>&1 || fail "$PYTHON_BIN not found"

if ! "$PYTHON_BIN" -c 'import sys; raise SystemExit(sys.version_info < (3, 11))'; then
  fail "$PYTHON_BIN must be Python 3.11 or newer"
fi

[[ -f pyproject.toml ]] || fail "pyproject.toml missing"
[[ -f VERSION ]] || fail "VERSION missing"
[[ -f README.md ]] || fail "README.md missing"
[[ -f LICENSE ]] || fail "LICENSE missing"

echo "Checking packaging metadata..."

"$PYTHON_BIN" - <<'PY'
from __future__ import annotations

import sys
import tomllib
from pathlib import Path

root = Path.cwd()
pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
version_file = (root / "VERSION").read_text(encoding="utf-8").strip()

project = pyproject.get("project", {})
errors: list[str] = []

name = project.get("name")
version = project.get("version")
description = project.get("description")
requires_python = project.get("requires-python")
scripts = project.get("scripts", {})

if name != "repo-signal":
    errors.append(f"project.name should be 'repo-signal', got {name!r}")

if not version:
    errors.append("project.version missing")

if version and version != version_file:
    errors.append(f"VERSION mismatch: VERSION={version_file!r}, pyproject={version!r}")

if not description:
    errors.append("project.description missing")

if not requires_python:
    errors.append("project.requires-python missing")

if scripts.get("repo-signal") != "repo_signal.cli:main":
    errors.append("project.scripts.repo-signal should be 'repo_signal.cli:main'")

if not project.get("readme"):
    errors.append("project.readme missing")

if not project.get("license"):
    errors.append("project.license missing")

if not project.get("authors"):
    errors.append("project.authors missing")

if errors:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    raise SystemExit(1)

print(f"Metadata OK: {name} {version}")
PY

echo "Creating isolated build environment..."

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

BUILD_VENV="$TMPDIR/build-venv"
INSTALL_VENV="$TMPDIR/install-venv"
DIST_DIR="$TMPDIR/dist"

"$PYTHON_BIN" -m venv "$BUILD_VENV"
"$BUILD_VENV/bin/python" -m pip install --upgrade pip >/dev/null
"$BUILD_VENV/bin/python" -m pip install build >/dev/null

echo "Building sdist and wheel..."
"$BUILD_VENV/bin/python" -m build --outdir "$DIST_DIR"

WHEEL="$(find "$DIST_DIR" -maxdepth 1 -name '*.whl' | head -n 1)"
SDIST="$(find "$DIST_DIR" -maxdepth 1 -name '*.tar.gz' | head -n 1)"

[[ -n "$WHEEL" ]] || fail "wheel was not built"
[[ -n "$SDIST" ]] || fail "sdist was not built"

echo "Built wheel: $(basename "$WHEEL")"
echo "Built sdist: $(basename "$SDIST")"

echo "Installing wheel into clean virtual environment..."

"$PYTHON_BIN" -m venv "$INSTALL_VENV"
"$INSTALL_VENV/bin/python" -m pip install --upgrade pip >/dev/null
"$INSTALL_VENV/bin/python" -m pip install "$WHEEL" >/dev/null

CLI="$INSTALL_VENV/bin/repo-signal"
[[ -x "$CLI" ]] || fail "repo-signal console script was not installed"

echo "Running installed CLI smoke tests..."

"$CLI" --help >/dev/null
"$CLI" inspect "$ROOT" >/dev/null
"$CLI" inspect --json "$ROOT" > "$TMPDIR/inspect.v1.json"
"$CLI" doctor >/dev/null
"$CLI" publish-checklist "$ROOT" >/dev/null

"$INSTALL_VENV/bin/python" - "$TMPDIR/inspect.v1.json" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
schema = payload.get("schema")

if schema != "inspect.v1":
    raise SystemExit(f"Expected inspect.v1 schema, got {schema!r}")

print("inspect.v1 schema OK")
PY

echo "Packaging check passed."
