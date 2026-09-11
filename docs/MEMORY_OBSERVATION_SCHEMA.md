# memory-observation.v1 — Observation Emission Schema

`memory-observation.v1` is the JSONL contract repo-signal appends when a real
`inspect` run surfaces a real issue. It carries one observation per line.

**An observation is a proposal, not a memory.** Emitting one asserts that
repo-signal saw a signal worth considering. It does not assert that the signal
is true, durable, important, or that anything should be remembered. Nothing in
repo-signal scores, ranks, promotes, demotes, or merges observations, and this
contract must not grow a field that implies it does.

## Ownership boundary

```text
repo-signal   produces signals        (this contract)
mqobsidian    stores them             (durable memory surface)
mq-agent      scores, promotes,       (decisions about memory)
              orchestrates workflow
```

Each side owns one thing. repo-signal never decides what is remembered;
mqobsidian never decides what is true; mq-agent never re-derives the signal.
A consumer that finds itself needing a promotion field in this schema is
reaching across the boundary — that logic belongs in mq-agent (see mqobsidian
ADR-008/009).

## Emission is opt-in

```bash
REPO_SIGNAL_EMIT_MEMORY=1 repo-signal inspect .
```

Emission is a no-op unless `REPO_SIGNAL_EMIT_MEMORY` is exactly `1`. Values like
`true`, `yes`, or `0` do not enable it.

Emission never raises into `inspect`. A failed write, an unreadable vault, or a
malformed record leaves `inspect` behaving exactly as it would have. A run that
surfaces no real issue emits nothing rather than a placeholder — there is no
synthetic bootstrap.

## Output surface

```text
<vault>/memory/observations/repo-signal.observations.jsonl
```

Vault resolution uses `MQ_OBSIDIAN_DIR` first, then `~/mqobsidian`. When neither
exists the emitter stays silent rather than guessing a path. Records are
appended; existing lines are never rewritten.

## Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `schema` | string | Always `memory-observation.v1` |
| `id` | string | `obs_rs_<repo>_<UTC timestamp>_<issue slug>` |
| `timestamp` | string | ISO 8601 UTC, `Z`-suffixed |
| `producer` | string | Always `repo-signal` |
| `repository` | string | Repository name — a logical identity, never a path |
| `workflow` | string | Always `repo-inspect` |
| `title` | string | The issue message, verbatim |
| `summary` | string | One sentence naming the repo and that a real issue was flagged |
| `observation` | string | The recommended next commit, or the message when absent |
| `category` | string | Always `review` |
| `confidence` | number | Producer certainty in the **signal**: `fail` 0.8, `error` 0.75, `warn` 0.6, `info` 0.5 |
| `evidence` | array | One entry: `source`, `reference`, `excerpt` |
| `tags` | array | `["repo-signal", "inspect", <level>]` |
| `proposed_memory_key` | string | Slug a consumer *may* key on; repo-signal does not use it |
| `metadata.branch` | string | Present only when the inspect result carried a git branch |
| `session_id` | string | Present only when `REPO_SIGNAL_SESSION` is set |

`confidence` is the producer's certainty in the signal. It is **not** a memory
score, and no promotion logic in repo-signal reads it.

The highest-severity issue wins when an inspect run surfaces several. Ranking is
`fail` > `error` > `warn` > `info`.

## Reference contract

> `evidence.reference` MUST NOT contain absolute machine-local filesystem paths.
> Repository identities and repository-relative paths are permitted.

```text
reference = stable logical identity
not        machine-local physical location
```

A reference identifies the evidence, not the machine the evidence happened to be
produced on. `/Users/mansys/repo-signal` carries no traceability that
`repo-signal` does not, while making the record machine-specific and worse to
move, compare, or share between runtime environments.

Permitted:

```text
repo-signal
mq-mcp
repo_signal/memory_emit.py
docs/ROADMAP.md
```

Rejected and redacted:

```text
/Users/mansys/repo-signal
/home/user/repo-signal
C:\Users\foo\repo-signal
\\fileserver\share\repo-signal
~/repo-signal
```

The rule is a shape invariant over POSIX absolute paths, Windows drive paths,
UNC shares, and `~` expansions — deliberately not a patch for the one platform
where the leak was first found. A path inside the repository is rewritten
repo-relative; the repository root itself, and anything outside it, becomes the
repository name.

Enforced by `repo_signal/redaction.py`, covered by `tests/test_redaction.py` and
`tests/test_memory_emit.py`, and checked at release time by the
`mqobsidian export contracts` section of `release.sh`. The same invariant
governs `repo-review.v1` (see [Review export schema](REVIEW_EXPORT_SCHEMA.md)),
which satisfies it by construction and is guarded by tests.

## Example

```json
{
  "schema": "memory-observation.v1",
  "id": "obs_rs_repo-signal_20260101000000_changelog-md-is-missing",
  "timestamp": "2026-01-01T00:00:00Z",
  "producer": "repo-signal",
  "repository": "repo-signal",
  "workflow": "repo-inspect",
  "title": "CHANGELOG.md is missing",
  "summary": "repo-signal inspect of repo-signal flagged a real issue.",
  "observation": "docs: add CHANGELOG.md",
  "category": "review",
  "confidence": 0.8,
  "evidence": [
    {
      "source": "repo-signal inspect.v1",
      "reference": "repo-signal",
      "excerpt": "CHANGELOG.md is missing"
    }
  ],
  "tags": ["repo-signal", "inspect", "fail"],
  "proposed_memory_key": "changelog-md-is-missing",
  "metadata": { "branch": "main" }
}
```

## Consuming safely

Verify `schema` before processing a line. Reject unknown schema versions rather
than guessing at field meaning. Treat every record as a proposal awaiting a
decision that repo-signal does not make.

## See also

- [Review export schema](REVIEW_EXPORT_SCHEMA.md) — the `repo-review.v1` contract
- [Export schemas](EXPORT_SCHEMAS.md) — the symbolic intelligence packs
