# repo-signal → mq-mcp pack merge integration

repo-signal v1.1.0 introduced four symbolic intelligence export packs.
mq-mcp v1.10.0+ consumes these packs to enrich its callgraph data before
running architecture, review, and risk workflows.

This document describes the full integration path and how to verify it.

---

## Integration flow

```text
repo-signal export .
  ↓
.repo-signal/exports/
  ├── callgraph.json      (callgraph.v1)
  ├── symbol_index.json   (symbol_index.v1)
  ├── repo_summary.json   (repo_summary.v1)
  └── risk_map.json       (risk_map.v1)
  ↓
mq-mcp: callgraph_builder._try_merge_repo_signal_packs()
  ↓
enriched callgraph passed to review, architecture, and risk tools
```

mq-mcp reads the packs automatically when the exports directory is present.
No configuration is required.

---

## Step 1 — generate packs

Run from the repository you want mq-mcp to review:

```bash
repo-signal export .
```

Output:

```
repo-signal export — repo-signal
output: .repo-signal/exports

  wrote  .repo-signal/exports/symbol_index.json  [symbol_index.v1]
  wrote  .repo-signal/exports/callgraph.json  [callgraph.v1]
  wrote  .repo-signal/exports/repo_summary.json  [repo_summary.v1]
  wrote  .repo-signal/exports/risk_map.json  [risk_map.v1]

4 pack(s) written.
```

You can regenerate at any time. mq-mcp reads the files on each invocation.

---

## Step 2 — mq-mcp reads the packs

When mq-mcp runs `callgraph_builder.build()`, it calls
`_try_merge_repo_signal_packs()` after its own graph analysis.

The merge is additive and non-destructive:

| Pack | What mq-mcp does with it |
| ---- | ------------------------ |
| `callgraph.v1` | Merges edges into internal `imports`/`importers` maps; refreshes `hub_files` |
| `symbol_index.v1` | Adds symbols to per-file `symbols` map |
| `repo_summary.v1` | Stored as `data["repo_signal_summary"]` for prompt injection |
| `risk_map.v1` | Stored as `data["repo_signal_risks"]` for risk-aware reviews |

The merge result is reported in the callgraph summary:

```
callgraph_builder: 121 Python files  96 import edges
  Hub files (3): __init__.py, core.py, scanner.py
  repo-signal packs merged: callgraph.v1, symbol_index.v1, repo_summary.v1, risk_map.v1
```

---

## Step 3 — verify

Run the smoke script to verify the full pipeline:

```bash
bash examples/integrations/mq_mcp_pack_merge.sh [repo-path]
```

Expected output:

```
repo-signal → mq-mcp pack merge smoke
repo: .
---
[OK]  callgraph.json  [callgraph.v1]
[OK]  symbol_index.json  [symbol_index.v1]
[OK]  repo_summary.json  [repo_summary.v1]
[OK]  risk_map.json  [risk_map.v1]
---
[OK]  callgraph edges — N edges, fields verified
[OK]  symbol_index symbols — N symbols, fields verified
[OK]  risk_map risks — N risks
[OK]  repo_summary — schema verified
---
PASS — all packs written and mq-mcp consumer fields verified
```

---

## Schema field contract

The fields mq-mcp reads per pack:

### callgraph.v1

```json
{
  "schema": "callgraph.v1",
  "edges": [
    { "source": "pkg/core.py", "target": "pkg/utils.py", "relation": "import" }
  ],
  "hub_files": ["pkg/utils.py"]
}
```

mq-mcp reads: `edge["source"]`, `edge["target"]`

### symbol_index.v1

```json
{
  "schema": "symbol_index.v1",
  "symbols": [
    { "name": "Engine", "kind": "class", "file_path": "pkg/core.py", "line": 3, "is_public": true }
  ]
}
```

mq-mcp reads: `sym["name"]`, `sym["file_path"]`

### repo_summary.v1

```json
{
  "schema": "repo_summary.v1",
  "repo_name": "my-repo",
  "description": "...",
  "project_type": "Python project"
}
```

mq-mcp stores the whole pack as `data["repo_signal_summary"]`.

### risk_map.v1

```json
{
  "schema": "risk_map.v1",
  "risks": [
    { "id": "RSK-001", "level": "medium", "kind": "large_file", "file": "tests/test_cli.py" }
  ]
}
```

mq-mcp stores `pack["risks"]` as `data["repo_signal_risks"]`.

---

## Graceful degradation

If `.repo-signal/exports/` does not exist, mq-mcp continues without enrichment
and reports:

```
repo-signal packs: not found (run `repo-signal export` to generate)
```

If the directory exists but contains no valid v1 schemas:

```
repo-signal packs: exports directory present but no valid v1 schemas found
```

No errors are raised. The callgraph is still built from mq-mcp's own analysis.

---

## Keeping packs current

The packs are static snapshots. Regenerate after significant changes:

```bash
repo-signal export .
```

For CI integration, add to your pre-review step:

```bash
repo-signal export . && mq-mcp review ...
```
