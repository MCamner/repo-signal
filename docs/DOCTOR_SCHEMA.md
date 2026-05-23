# Doctor JSON Schema

Schema version: `doctor.v1`

`repo-signal doctor --json` emits a machine-readable readiness report for dashboards, CI helpers, local scripts, and AI-assisted repository workflows.

## Usage

```bash
repo-signal doctor --json
repo-signal doctor . --format json
repo-signal doctor ~/some-repo --format json
```

## Example

```json
{
  "schema": "doctor.v1",
  "schema_version": "doctor.v1",
  "repo": {
    "name": "repo-signal",
    "path": "/Users/mansys/repo-signal",
    "project_type": "Python CLI / repo intelligence toolkit"
  },
  "summary": {
    "files_scanned": 124,
    "languages": {
      "Python": 52,
      "Markdown": 43
    },
    "git_repo": true,
    "git_branch": "main",
    "working_tree_changes": 0
  },
  "scores": {
    "repo_health": {
      "score": 90,
      "max_score": 100,
      "status": "strong",
      "evidence": ["README exists", "LICENSE exists"]
    }
  },
  "suggested_skills": ["repo-aware"],
  "suggested_priorities": ["Use this repo as a baseline and improve deeper semantic analysis next"]
}
```

## Top-Level Fields

| Field | Type | Meaning |
| --- | --- | --- |
| `schema` | string | Schema identifier. Always `"doctor.v1"`. Check this field before parsing. |
| `schema_version` | string | Legacy alias for `schema`. Same value. |
| `repo` | object | Repository identity and project classification. |
| `summary` | object | Scan summary, language counts, and Git state. |
| `scores` | object | Readiness scores grouped by area. |
| `key_signals` | object | Entry points, tooling, symbol count, and graph edge count. |
| `readme` | object | README presence and checklist status. |
| `suggested_skills` | array | Suggested Codex skills for follow-up work. |
| `suggested_priorities` | array | Highest-signal next actions. |
| `repoaware_context` | object | Compact AI-readable summary and priorities. |

## `repo`

| Field | Type | Meaning |
| --- | --- | --- |
| `name` | string | Repository directory name. |
| `path` | string | Absolute local repository path. |
| `project_type` | string | Best-effort project type classification. |

## `summary`

| Field | Type | Meaning |
| --- | --- | --- |
| `files_scanned` | number | Number of scanned files. |
| `languages` | object | Language name to file count. |
| `git_repo` | boolean | Whether the path is inside a Git repository. |
| `git_branch` | string or null | Current Git branch when available. |
| `working_tree_changes` | number | Count of Git working tree changes. |

## `scores`

`scores` contains four named score objects:

- `repo_health`
- `release_maturity`
- `docs_quality`
- `ai_readiness`

Each score object has this shape:

| Field | Type | Meaning |
| --- | --- | --- |
| `score` | number | Current score. |
| `max_score` | number | Maximum possible score. |
| `status` | string | Human-readable status: `strong`, `usable`, `thin`, or `weak`. |
| `evidence` | array | Short evidence strings used to justify the score. |

## `key_signals`

| Field | Type | Meaning |
| --- | --- | --- |
| `entrypoints` | array | Important runnable or operational files. |
| `tooling` | array | Detected project tooling and public repo signals. |
| `symbols` | number | Extracted symbol count. |
| `repo_graph_edges` | number | Repository graph edge count. |

## `readme`

| Field | Type | Meaning |
| --- | --- | --- |
| `path` | string | README path when detected. |
| `exists` | boolean | Whether README exists. |
| `missing_checks` | array | README quality checks that are missing. |
| `present_checks` | array | README quality checks that are present. |

## Compatibility Contract

`doctor.v1` is stable enough for local scripts and CI helpers.

Breaking changes should bump `schema_version`. Additive fields may appear without a version bump.

For a fuller narrative description, see [DOCTOR_JSON.md](DOCTOR_JSON.md).
