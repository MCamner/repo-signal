# suggest.v1 — JSON Schema Reference

`repo-signal suggest [path] --format json` emits a single JSON object with schema version `suggest.v1`.

**Safety guarantee:** `repo-signal suggest` never writes to the repository. It produces read-only output only.

## Top-level shape

```json
{
  "schema": "suggest.v1",
  "repo": "my-project",
  "path": "/abs/path/to/repo",
  "total": 3,
  "by_risk": {
    "low": 2,
    "medium": 1,
    "high": 0
  },
  "by_group": {
    "docs": 1,
    "release": 1,
    "hygiene": 1
  },
  "suggestions": [ ... ]
}
```

## Field reference

| Field | Type | Description |
|---|---|---|
| `schema` | string | Always `"suggest.v1"` — use to verify schema version before parsing |
| `repo` | string | Repository name |
| `path` | string | Absolute path to the repository root |
| `total` | integer | Total number of suggestions |
| `by_risk` | object | Count per risk level: `low`, `medium`, `high` |
| `by_group` | object | Count per commit group — see groups below |
| `suggestions` | array | List of suggestion objects — see below |

### Commit groups

| Group | Covers |
|---|---|
| `docs` | README, Quick Start, screenshots, demos, ROADMAP, contributing, wiki |
| `hygiene` | LICENSE, `.gitignore`, junk cleanup |
| `release` | CHANGELOG, VERSION, pyproject.toml, release scripts |
| `testing` | tests, test coverage |
| `ci` | GitHub Actions, workflow files |
| `pages` | GitHub Pages, docs/ landing |
| `examples` | examples/ directory and generated examples |

### Suggestion item

| Field | Type | Description |
|---|---|---|
| `id` | string | Stable slug identifier for the suggestion |
| `title` | string | One-line description of the suggestion |
| `hint` | string | Expanded explanation from the publish checklist |
| `risk` | string | `"low"`, `"medium"`, or `"high"` |
| `commit_group` | string | Suggested commit grouping |
| `diff_preview` | string | Illustrative diff — not a real patch, for human review |
| `command_hint` | string | Shell command or comment to help apply the suggestion |

## Risk levels

| Level | Meaning |
|---|---|
| `low` | Adding missing files, documentation, or sections |
| `medium` | Renaming, restructuring, or modifying existing files |
| `high` | Removing tracked files, force operations, breaking changes |

## Schema version check

```python
import json, subprocess

out = subprocess.check_output(["repo-signal", "suggest", ".", "--format", "json"])
data = json.loads(out)

if data.get("schema") != "suggest.v1":
    raise RuntimeError(f"Unexpected schema: {data.get('schema')}")

for s in data["suggestions"]:
    print(s["risk"], s["commit_group"], s["title"])
```

## No-mutation guarantee

`repo-signal suggest` is read-only. It will never:

- Create files
- Edit files
- Delete files
- Run `git commit` or `git push`
- Apply patches or diffs

The `diff_preview` and `command_hint` fields are for human review only.

## Example output (repo with suggestions)

```json
{
  "schema": "suggest.v1",
  "repo": "my-project",
  "path": "/Users/me/my-project",
  "total": 2,
  "by_risk": { "low": 2, "medium": 0, "high": 0 },
  "by_group": { "docs": 1, "hygiene": 1 },
  "suggestions": [
    {
      "id": "add-readme",
      "title": "Add a README.md",
      "hint": "Missing README.md — add a project overview and quick start",
      "risk": "low",
      "commit_group": "docs",
      "diff_preview": "--- /dev/null\n+++ README.md\n@@ -0,0 +1 @@\n+# my-project",
      "command_hint": "touch README.md"
    },
    {
      "id": "add-gitignore",
      "title": "Add a .gitignore",
      "hint": "Missing .gitignore — add one to exclude build artifacts",
      "risk": "low",
      "commit_group": "hygiene",
      "diff_preview": "--- /dev/null\n+++ .gitignore\n@@ -0,0 +1 @@\n+# .gitignore",
      "command_hint": "touch .gitignore"
    }
  ]
}
```

## Example output (complete repo)

```json
{
  "schema": "suggest.v1",
  "repo": "repo-signal",
  "path": "/Users/me/repo-signal",
  "total": 0,
  "by_risk": { "low": 0, "medium": 0, "high": 0 },
  "by_group": {},
  "suggestions": []
}
```

See `examples/suggest/suggest.v1.json` for a full generated example.

## See Also

- [REPORT_SCHEMA.md](REPORT_SCHEMA.md) — report.v1 schema reference
- [INSPECT_SCHEMA.md](INSPECT_SCHEMA.md) — inspect.v1 schema reference
- [DOCTOR_SCHEMA.md](DOCTOR_SCHEMA.md) — doctor.v1 schema reference
- [INTEGRATIONS.md](INTEGRATIONS.md) — safe consumption patterns
