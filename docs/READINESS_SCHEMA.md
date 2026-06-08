# readiness.v1 — Release Readiness Export Schema

`readiness.v1` is the release/readiness export contract for `repo-signal`.

It combines version alignment, metadata freshness, publish-checklist quality,
and a deterministic release gate block into a single JSON output intended for
mq-agent and mq-mcp consumers.

---

## Command

```bash
repo-signal readiness [path] [--format text|markdown|json]
repo-signal readiness . --json
repo-signal readiness . --format markdown
```

---

## Schema fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `schema` | string | Always `"readiness.v1"` |
| `repo` | string | Repository name (directory basename) |
| `path` | string | Absolute path to the repository root |
| `generated_at` | string | ISO 8601 UTC timestamp |
| `version` | object | Version alignment signals |
| `metadata` | object | Metadata freshness signals |
| `quality` | object | Publish-checklist and test quality signals |
| `release_gate` | object | Deterministic ready/blocked state |

### `version`

| Field | Type | Description |
| ----- | ---- | ----------- |
| `current` | string | Resolved current version (from VERSION file first) |
| `aligned` | bool | True if all non-empty sources agree |
| `sources.VERSION` | string | Value from VERSION file |
| `sources.pyproject` | string | Value from `pyproject.toml` |
| `sources.init` | string | Value from `repo_signal/__init__.py` |

### `metadata`

| Field | Type | Description |
| ----- | ---- | ----------- |
| `changelog_has_current` | bool | True if CHANGELOG contains `[{current version}]` |
| `readme_has_version` | bool | True if README contains the current version string |
| `roadmap_next_target` | string | Next planned version from ROADMAP (e.g. `"v1.5.0"`) or `""` |

### `quality`

| Field | Type | Description |
| ----- | ---- | ----------- |
| `publish_checklist_score` | int | Raw score from `publish-checklist` |
| `publish_checklist_total` | int | Maximum possible score |
| `publish_checklist_pass` | bool | True if score ≥ 16 |
| `test_files_present` | bool | True if any `tests/test_*.py` files exist |
| `test_file_count` | int | Number of `test_*.py` files in `tests/` |

### `release_gate`

| Field | Type | Description |
| ----- | ---- | ----------- |
| `ready` | bool | True if no blockers |
| `blocked` | bool | True if any blockers |
| `blockers` | list[str] | Human-readable list of blocking conditions |

Blocker conditions:

- Version sources disagree (VERSION ≠ pyproject ≠ init)
- CHANGELOG does not contain an entry for the current version
- Publish checklist score is below threshold (16)

---

## mq-agent integration

```python
import subprocess, json

result = subprocess.run(
    ["repo-signal", "readiness", ".", "--json"],
    capture_output=True, text=True, check=True
)
data = json.loads(result.stdout)
assert data["schema"] == "readiness.v1"

gate = data["release_gate"]
if gate["blocked"]:
    print("Release blocked:")
    for b in gate["blockers"]:
        print(f"  - {b}")
else:
    print(f"Ready to release {data['version']['current']}")
```

---

## mq-mcp integration pattern

mq-mcp Release Gate v2 can consume `readiness.v1` directly:

```text
repo-signal readiness . --json
  ↓
readiness.v1
  ↓
mq-mcp release-gate run --repo . --profile v2
```

The `release_gate.ready` field is the primary signal. `release_gate.blockers`
provides the reason list for operator display.

---

## Example output

See `examples/readiness/` for generated fixture outputs.
