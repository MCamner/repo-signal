---
name: symbolic-intelligence-exporter
description: Use when adding or changing repo-signal symbolic exports such as symbol_index.json, callgraph.json, repo_summary.json, risk_map.json, semantic packs, or schemas consumed by mq-mcp and mq-agent.
---

# Symbolic Intelligence Exporter

Use this skill when repo-signal produces structured repository intelligence for other mq tools.

## Boundary

repo-signal owns preprocessing, indexing, static repository signals, JSON contracts, semantic pack generation and release/publish intelligence.

It must not generate review findings, make architecture decisions, or become a cognition runtime.

## Expected Exports

- `symbol_index.json` — public symbols, files, ownership hints
- `callgraph.json` — imports and cross-file relationships
- `repo_summary.json` — compact repository context
- `risk_map.json` — structural risk signals, not AI findings

## Change Workflow

1. Define or update a versioned schema.
2. Keep terminal output human-readable and JSON output machine-readable.
3. Add generated examples for new export contracts.
4. Add tests that validate shape and no-mutation behavior.
5. Document safe downstream consumption for mq-mcp and mq-agent.

## Safety Rules

- No repository mutation.
- No AI-generated review text in symbolic exports.
- No secrets or `.env` values in generated packs.
- Downstream consumers should read schema versions, not terminal text.

## Verification

```bash
python3 -m pytest -q
repo-signal inspect --json . | python3 -m json.tool
repo-signal doctor
./release.sh --dry-run
```

Use the repo's actual release/check script if the dry-run flag is not available.
