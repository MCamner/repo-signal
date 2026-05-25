# report.v1 — JSON Schema Reference

`repo-signal report [path] --format json` emits a single JSON object with schema version `report.v1`.

## Top-level shape

```json
{
  "schema": "report.v1",
  "repo": "repo-signal",
  "path": "/abs/path/to/repo",
  "git": { ... },
  "languages": { ... },
  "publish_score": 16,
  "publish_total": 16,
  "publish_status": "pass",
  "core_files": [ ... ],
  "issues": [ ... ],
  "recommended_next_action": "...",
  "recommended_next_commit": "...",
  "useful_next_commands": [ ... ]
}
```

## Field reference

| Field | Type | Description |
|---|---|---|
| `schema` | string | Always `"report.v1"` — use to verify schema version before parsing |
| `repo` | string | Repository name (directory name or detected project name) |
| `path` | string | Absolute path to the repository root |
| `git` | object | Git state — see below |
| `languages` | object | Map of detected language → file count |
| `publish_score` | integer | Publish checklist score (items passing) |
| `publish_total` | integer | Publish checklist total items |
| `publish_status` | string | `"pass"`, `"warn"`, or `"fail"` |
| `core_files` | array | List of expected core files with status — see below |
| `issues` | array | List of issue message strings |
| `recommended_next_action` | string | High-level recommendation for what to do next |
| `recommended_next_commit` | string | Suggested next commit message |
| `useful_next_commands` | array | List of commands to run next |

### `git` object

| Field | Type | Description |
|---|---|---|
| `branch` | string or null | Current branch name |
| `clean` | boolean | Whether the working tree is clean |
| `summary` | string | Human-readable git state summary |

### `core_files` item

| Field | Type | Description |
|---|---|---|
| `path` | string | Relative path from repo root |
| `label` | string | Human-readable file label |
| `exists` | boolean | Whether the file or directory exists |
| `status` | string | `"ok"` or `"missing"` |

## Schema version check

Always check `schema` before parsing to detect breaking changes:

```python
import json, subprocess

out = subprocess.check_output(["repo-signal", "report", ".", "--format", "json"])
data = json.loads(out)

if data.get("schema") != "report.v1":
    raise RuntimeError(f"Unexpected schema: {data.get('schema')}")
```

## Example output

```json
{
  "schema": "report.v1",
  "repo": "repo-signal",
  "path": "/Users/me/repo-signal",
  "git": {
    "branch": "main",
    "clean": true,
    "summary": "git repo, branch main, clean"
  },
  "languages": {
    "Markdown": 66,
    "Python": 63,
    "Shell": 10
  },
  "publish_score": 16,
  "publish_total": 16,
  "publish_status": "pass",
  "core_files": [
    { "path": "README.md", "label": "README", "exists": true, "status": "ok" }
  ],
  "issues": [],
  "recommended_next_action": "Repo looks publish-ready from the static checklist.",
  "recommended_next_commit": "Keep docs, examples, and command reference synced with the CLI",
  "useful_next_commands": [
    "repo-signal doctor",
    "repo-signal publish-checklist . --fail-under 16"
  ]
}
```

See `examples/report/report.v1.json` for a full generated example.

## See Also

- [SUGGEST_SCHEMA.md](SUGGEST_SCHEMA.md) — suggest.v1 schema reference
- [INSPECT_SCHEMA.md](INSPECT_SCHEMA.md) — inspect.v1 schema reference
- [DOCTOR_SCHEMA.md](DOCTOR_SCHEMA.md) — doctor.v1 schema reference
- [INTEGRATIONS.md](INTEGRATIONS.md) — safe consumption patterns
