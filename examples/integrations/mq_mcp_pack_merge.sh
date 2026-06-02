#!/usr/bin/env bash
# mq_mcp_pack_merge.sh — smoke test for repo-signal → mq-mcp pack merge pipeline
#
# Verifies that repo-signal export produces packs mq-mcp can consume.
# Run from any git repository root.
#
# Usage:
#   bash examples/integrations/mq_mcp_pack_merge.sh [repo-path]
#
# Exit codes:
#   0 — all four packs written and schema-valid
#   1 — one or more packs missing or schema mismatch

set -euo pipefail

REPO="${1:-.}"
EXPORTS_DIR="$REPO/.repo-signal/exports"

ok()   { printf '[OK]  %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; FAILED=1; }
FAILED=0

echo "repo-signal → mq-mcp pack merge smoke"
echo "repo: $REPO"
echo "---"

# Step 1: generate exports
if ! repo-signal export "$REPO" >/dev/null 2>&1; then
  echo "ERROR: repo-signal export failed"
  exit 1
fi

# Step 2: verify all four packs exist and carry the right schema field
declare -A SCHEMAS=(
  ["callgraph.json"]="callgraph.v1"
  ["symbol_index.json"]="symbol_index.v1"
  ["repo_summary.json"]="repo_summary.v1"
  ["risk_map.json"]="risk_map.v1"
)

for fname in "${!SCHEMAS[@]}"; do
  expected="${SCHEMAS[$fname]}"
  fpath="$EXPORTS_DIR/$fname"

  if [[ ! -f "$fpath" ]]; then
    fail "$fname: not found"
    continue
  fi

  actual="$(python3 -c "import json; d=json.load(open('$fpath')); print(d.get('schema',''))" 2>/dev/null || echo '')"
  if [[ "$actual" == "$expected" ]]; then
    ok "$fname  [$actual]"
  else
    fail "$fname: expected schema=$expected  got=$actual"
  fi
done

echo "---"

# Step 3: verify fields mq-mcp reads per pack
python3 - "$EXPORTS_DIR" <<'PYCHECK'
import json, sys
from pathlib import Path

out = Path(sys.argv[1])
ok = True

cg = json.loads((out / "callgraph.json").read_text())
for edge in cg.get("edges", []):
    if "source" not in edge or "target" not in edge:
        print(f"[FAIL] callgraph edge missing source/target: {edge}")
        ok = False
        break
else:
    print(f"[OK]  callgraph edges — {len(cg['edges'])} edges, fields verified")

sym = json.loads((out / "symbol_index.json").read_text())
for s in sym.get("symbols", []):
    if "name" not in s or "file_path" not in s:
        print(f"[FAIL] symbol missing name/file_path: {s}")
        ok = False
        break
else:
    print(f"[OK]  symbol_index symbols — {len(sym['symbols'])} symbols, fields verified")

risk = json.loads((out / "risk_map.json").read_text())
if isinstance(risk.get("risks", []), list):
    print(f"[OK]  risk_map risks — {len(risk['risks'])} risks")
else:
    print("[FAIL] risk_map.risks is not a list")
    ok = False

summary = json.loads((out / "repo_summary.json").read_text())
if summary.get("schema") == "repo_summary.v1":
    print("[OK]  repo_summary — schema verified")
else:
    print("[FAIL] repo_summary schema mismatch")
    ok = False

sys.exit(0 if ok else 1)
PYCHECK

PY_STATUS=$?

echo "---"
if [[ "$FAILED" -eq 0 && "$PY_STATUS" -eq 0 ]]; then
  echo "PASS — all packs written and mq-mcp consumer fields verified"
  exit 0
else
  echo "FAIL — one or more checks failed"
  exit 1
fi
