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
| `scores` | object | Static structural scores grouped by area; not execution evidence. |
| `verification` | object | Additive local receipt-validation summary; see below. |
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

## Verification evidence (additive)

```bash
repo-signal doctor . --verification --json
```

Without `--verification`, `verification.status` is `NOT_VERIFIED` and no
mq-agent process is started. With the flag, repo-signal invokes the installed
`mq-agent verify-changes <repo> --check-receipt --json` with a 30-second timeout.
It validates existing evidence only: no tests, receipt writes, cloud calls or
GitHub queries. mq-agent owns checksum and current-snapshot validation.

| Field | Meaning |
| --- | --- |
| `status` | `PASS`, `FAIL`, `STALE` or `NOT_VERIFIED`. |
| `code_status` | Producer code status, or null when unavailable/invalid. A code PASS can coexist with overall NOT_VERIFIED. |
| `reason` | Fixed reason code; no raw provider errors or paths. |
| `source` | Always `mq-agent`. |
| `scope` | Always `changed_files_against_HEAD`; not full-repository coverage. |
| `receipt_id`, `fingerprint` | Validated-producer references, or null. |
| `head`, `base` | Producer Git object IDs, or null. |
| `next_action` | Advisory text; never executed. |

`MISSING`, `NO_CHANGES`, `PLAN`, `ERROR`, `INCOMPLETE`, unavailable/older mq-agent,
invalid JSON, timeout, oversized output and inconsistent PASS responses all map
to `NOT_VERIFIED`. PASS requires a nonempty passing check set, no uncovered files
and no unverified runtime data. The adapter emits references and summary only;
raw check output, filenames and provider stderr are discarded.

The four numerical scores and existing `doctor.v1` fields remain compatible.
They measure structure, even at 100/100. Doctor still exits 0 when a report was
produced; automation must inspect `verification.status`, not its exit code or
structure score, to make a verification decision. This is local changed-file
evidence against HEAD, not a full-suite, CI, release approval or authenticity
attestation. Only invoke a trusted mq-agent installation from PATH.

Example verification object: [not requested](../examples/doctor/verification-not-requested.json).
