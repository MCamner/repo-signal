# repo-review.v1 — Review Export Schema

`repo-review.v1` is the Markdown export contract produced by
`repo-signal review-export`. It converts a fresh `inspect.v1` result into a
compact review note below an existing mqobsidian vault.

## Command

```bash
repo-signal review-export [path] [--vault PATH] [--force]
```

The source repository defaults to the current directory. Vault resolution uses
`--vault` first, then `MQ_OBSIDIAN_DIR`, then `~/mqobsidian`. The resolved vault
must already exist.

## Output path

```text
<vault>/reviews/<YYYY-MM-DD>-repo-signal-<repo-slug>.md
```

The repository slug is lowercase, replaces non-alphanumeric runs with `-`, and
falls back to `repo` when empty. The exporter creates `reviews/` when needed.

An existing file is never replaced by default. Pass `--force` explicitly to
replace the file for the same date and repository slug.

## Frontmatter fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `schema` | string | Always `repo-review.v1` |
| `repo` | string | Repository name from the source inspection |
| `created_at` | string | ISO 8601 UTC timestamp |
| `summary` | string | Finding count and optional public-readiness summary |
| `source` | string | Always `repo-signal` |
| `source_schema` | string | Always `inspect.v1` |

Consumers must verify both `schema` and `source_schema` before processing the
note. Inputs with another schema or a missing repository are rejected.

## Markdown body

The body contains two stable sections:

- `Findings`: one list item per non-empty `inspect.v1` issue, formatted as
  `[LEVEL] message`; otherwise `No findings.`
- `Recommendation`: `recommended_next_commit`, or `No next action reported.`

Example:

```markdown
---
schema: repo-review.v1
repo: demo-repo
created_at: 2026-08-22T12:00:00Z
summary: repo-signal inspect found 1 finding(s); public readiness 14/16 WARN
source: repo-signal
source_schema: inspect.v1
---

# Repo Review: demo-repo

## Findings

- [WARN] Missing tests

## Recommendation

Add focused tests
```

## Provenance and safety boundary

The export copies only the repository name, issue level/message,
public-readiness summary, and recommended next commit from `inspect.v1`. It does
not include the source repository's absolute `repo.path`, git metadata, or raw
issue field.

Scalar values have newlines removed before rendering. Dedicated rejection or
redaction of secret-like values and machine-local paths inside copied message
text is not part of the current contract; do not publish a generated review
without checking its contents.

repo-signal produces this proposal but does not score, promote, or otherwise
manage durable mqobsidian memory.

## Failure behavior

The command exits without writing a review when:

- the vault does not exist;
- the source schema is not `inspect.v1`;
- the inspected repository does not exist; or
- the destination exists and `--force` was not supplied.

## See also

- [Inspect Schema](INSPECT_SCHEMA.md) — source `inspect.v1` contract
- [Command Reference](COMMANDS.md) — `review-export` usage
- [Integrations](INTEGRATIONS.md) — MQ consumer boundaries
