# The repo-signal → mqobsidian boundary

repo-signal writes into an mqobsidian vault through exactly two paths. This
page states who owns what on either side of that line, and what each path does
when something goes wrong.

Contract details live in
[REVIEW_EXPORT_SCHEMA.md](REVIEW_EXPORT_SCHEMA.md) and
[MEMORY_OBSERVATION_SCHEMA.md](MEMORY_OBSERVATION_SCHEMA.md). This page is
about ownership and failure, not field lists.

---

## Ownership

| Component | Owns |
|---|---|
| **repo-signal** | Producing signals. It renders one review, or appends one observation, and stops. |
| **mqobsidian** | Storing them. It owns the vault layout and every durable note in it. |
| **mq-agent** | Scoring, promotion and workflow orchestration. |

Three consequences follow, and they are the reason the boundary is worth
writing down:

- **An observation is a proposal, not a memory.** repo-signal emits a
  `proposed_memory_key`. It never writes a `score`, a `promoted` flag or a
  resolved memory key — deciding what becomes durable memory is mq-agent's job,
  and a producer that scored its own output would be grading its own homework.
- **repo-signal only ever appends or creates.** It writes a review file that
  did not exist, or appends a line to the observation surface. It does not
  edit, reorder or delete anything already in the vault. A human's notes and a
  promoted memory are equally untouchable.
- **repo-signal never mutates a remote vault.** No commit, no push, no sync.
  What lands in git is the vault owner's decision.

## The two paths

| | Review export | Observation append |
|---|---|---|
| Command | `repo-signal review-export` | the `inspect` path, env-gated |
| Gate | explicit command | `REPO_SIGNAL_EMIT_MEMORY=1` |
| Writes | `reviews/<date>-repo-signal-<repo>.md` | `memory/observations/repo-signal.observations.jsonl` |
| Schema | `repo-review.v1`, preserving `source_schema: inspect.v1` | `memory-observation.v1` |
| On failure | reports and exits 2 | silently emits nothing |

The difference in failure behavior is deliberate. `review-export` is something
a person asked for, so it must say why it could not do it. Observation
emission is a side effect of `inspect`, so a broken vault must not change what
`inspect` reports or what it exits with.

## Resolving the vault

Both paths resolve the vault the same way:

1. the `--vault` argument, for `review-export` only
2. `MQ_OBSIDIAN_DIR`
3. `~/mqobsidian`

Neither path invents a path beyond that. If nothing resolves to an existing
directory, `review-export` fails loudly and the emitter stays silent —
guessing would mean writing someone's repository signals somewhere nobody
asked for.

The default is a real vault on a developer machine. Anything automated should
set `MQ_OBSIDIAN_DIR` explicitly rather than inherit it; that is what
[`examples/integrations/mqobsidian_export.sh`](../examples/integrations/mqobsidian_export.sh)
does, and why the test suite redirects both `MQ_OBSIDIAN_DIR` and `HOME`.

## Failure behavior

### Review export

Every fault below prints a single readable line and exits `2`. None of them
prints a traceback, and none leaves a partial file behind.

| Condition | Message | Exit |
|---|---|---|
| Vault directory does not exist | `mqobsidian vault not found: <path>` | 2 |
| Vault is not writable | `[Errno 13] Permission denied: <path>` | 2 |
| Review already exists | `review already exists: <path> (use --force to replace it)` | 2 |
| Source is not `inspect.v1` | `expected inspect.v1, got <schema>` | 2 |
| Repository does not exist | `cannot export a review for a missing repository` | 2 |

`PermissionError` is neither `FileNotFoundError` nor `FileExistsError`. It
escaped the CLI's handler until v1.6.0 and printed a stack trace at the one
moment a readable message matters most — writing into a vault that belongs to
someone else's setup.

### Observation append

| Condition | Behavior |
|---|---|
| `REPO_SIGNAL_EMIT_MEMORY` unset or not `1` | No emission. Nothing is written. |
| No vault resolves | Returns `None`. Nothing is written. |
| Repo missing, or no real issue surfaced | Returns `None` — evidence-bearing records only, never a placeholder. |
| Surface is unwritable, or any other I/O fault | Swallowed. `inspect` behaves exactly as if emission were off. |

The last row is the failure-isolation guarantee: `maybe_emit_memory` never
raises. A vault problem is not allowed to change `inspect`'s output or its
exit code.

## Verifying the boundary

`tests/test_mqobsidian_boundary.py` drives both paths end to end against a
temporary vault and asserts the ownership rules above — including that a run
creates *only* the expected file and leaves pre-existing notes byte-identical.

Those tests redirect `HOME` as well as `MQ_OBSIDIAN_DIR`, so a test that
forgot the environment variable cannot fall through to `~/mqobsidian` and
append to a real vault.
