# Doctor JSON Output

`repo-signal doctor` supports machine-readable output for dashboards, launchers, CI helpers, and local AI assistants.

## Usage

```bash
repo-signal doctor --json
repo-signal doctor . --format json
repo-signal doctor ~/some-repo --format json
```

## Why this exists

Markdown is good for humans. JSON is better for:

- `mqlaunch`
- `mq-hal`
- Bridget (via `hal_repo_report`)
- dashboards
- CI gates
- local scripts
- repo memory pipelines

## Example shape

```json
{
  "schema_version": "doctor.v1",
  "repo": {
    "name": "repo-signal",
    "path": "/Users/mansys/repo-signal",
    "project_type": "Python CLI / repo intelligence toolkit"
  },
  "summary": {
    "files_scanned": 100,
    "languages": { "Python": 80, "Markdown": 20 },
    "git_repo": true,
    "git_branch": "main",
    "working_tree_changes": 0
  },
  "scores": {
    "repo_health":      { "score": 90, "max_score": 100, "status": "strong", "evidence": [] },
    "release_maturity": { "score": 85, "max_score": 100, "status": "strong", "evidence": [] },
    "docs_quality":     { "score": 80, "max_score": 100, "status": "strong", "evidence": [] },
    "ai_readiness":     { "score": 90, "max_score": 100, "status": "strong", "evidence": [] }
  },
  "key_signals": {
    "entrypoints": ["bin/repo-signal"],
    "tooling": ["uv", "pytest"],
    "symbols": 42,
    "repo_graph_edges": 18
  },
  "readme": {
    "path": "/Users/mansys/repo-signal/README.md",
    "exists": true,
    "missing_checks": [],
    "present_checks": ["why", "quick_start", "features"]
  },
  "suggested_skills": ["repo-aware"],
  "suggested_priorities": [],
  "repoaware_context": {
    "summary": "Short AI-readable repo summary.",
    "prioritize": []
  }
}
```

## Schema version

Current schema version: `doctor.v1`

Bump `schema_version` if the JSON structure changes in a breaking way.
