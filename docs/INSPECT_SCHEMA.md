# Inspect JSON Schema

Schema version: `inspect.v1`

`repo-signal inspect --json` returns a stable integration contract for tools that
should not parse terminal text.

Intended consumers:

- `mqlaunch`
- `mq-hal`
- `mq-mcp`
- Bridget
- CI helpers
- repo dashboards

## Usage

```bash
repo-signal inspect --json
repo-signal inspect ~/some-repo --json
repo-signal inspect --format json
```

## Top-level fields

| Field                     | Type   | Meaning                                                           |
| ------------------------- | ------ | ----------------------------------------------------------------- |
| `schema`                  | string | Contract version. Currently `inspect.v1`.                         |
| `repo`                    | object | Repository identity and basic size/type signals.                  |
| `git`                     | object | Git repo status, branch, cleanliness, and summary.                |
| `public_readiness`        | object | Publish-checklist summary, score, total, status, and next action. |
| `detected`                | object | Languages, entrypoints, tooling, and top directories.             |
| `core_files`              | array  | Presence of expected public-facing files/folders.                 |
| `issues`                  | array  | Normalized issue records with `level`, `message`, `raw`.         |
| `recommended_next_commit` | string | Human-readable next commit suggestion.                            |
| `useful_next_commands`    | array  | Follow-up commands for deeper checks.                             |

## Compatibility rule

Consumers must check:

```text
schema == "inspect.v1"
```

If a future schema is introduced, consumers should fail safely instead of
guessing field meanings.

## Example

```json
{
  "schema": "inspect.v1",
  "repo": {
    "name": "repo-signal",
    "path": "/Users/example/repo-signal",
    "exists": true,
    "type": "python",
    "files": 120
  },
  "git": {
    "is_repo": true,
    "branch": "main",
    "change_count": 0,
    "clean": true,
    "summary": "git repo, branch main, clean"
  },
  "public_readiness": {
    "available": true,
    "summary": "16/16 OK",
    "status": "ok",
    "score": 16,
    "total": 16,
    "recommended_next_action": "Repo looks publish-ready",
    "error": null
  },
  "detected": {
    "languages": { "Python": 42 },
    "entrypoints": ["repo_signal/cli.py"],
    "tooling": ["pyproject.toml"],
    "top_directories": { "repo_signal": 30, "tests": 10 }
  },
  "core_files": [
    { "path": "README.md", "label": "README", "exists": true, "status": "ok" }
  ],
  "issues": [],
  "recommended_next_commit": "Keep docs, examples, and command reference synced with the CLI",
  "useful_next_commands": [
    "repo-signal doctor",
    "repo-signal publish-checklist . --fail-under 16"
  ]
}
```
