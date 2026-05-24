# Semantic repository memory

`repo-signal semantic-upload` builds a compact symbol map of the repository
and uploads it to an OpenAI vector store.

No upload happens without an explicit vector store ID. Dry-run is always safe.

---

## Generation flow

```text
Repository.load(".")
  ↓
build_openai_memory_document()
  ↓
{repo-name}-symbol-memory.md  (symbols only, no raw source)
  ↓
OpenAI vector store  (only on explicit upload)
```

---

## Commands

```bash
# always safe — shows what would be uploaded
repo-signal semantic-upload --dry-run

# upload (requires OPENAI_VECTOR_STORE_ID)
repo-signal semantic-upload

# include test symbols
repo-signal semantic-upload --include-tests

# target a specific vector store
repo-signal semantic-upload --vector-store-id vs_abc123
```

---

## Environment

```bash
export OPENAI_VECTOR_STORE_ID="vs_..."
export OPENAI_API_KEY="sk-..."
```

If `OPENAI_VECTOR_STORE_ID` is missing and `--dry-run` is not set, the command
exits with code 2 and prints an error.

---

## Verified dry-run output

```text
$ repo-signal semantic-upload --dry-run

# OpenAI Vector Store Upload

Repo: `repo-signal`
Vector store: `(not set)`
File: `repo-signal-symbol-memory.md`
Symbols: `312`
Bytes: `63832`
Status: `dry_run`
```

---

## mq-agent integration

`mq-agent` wraps semantic-upload via `memory build` and `memory refresh`:

```bash
mq-agent memory status .        # check vector store and repo-signal
mq-agent memory doctor .        # diagnose environment
mq-agent memory build .         # dry-run (safe default)
mq-agent memory refresh . --approve  # upload when ready
```

```text
$ mq-agent memory status /path/to/repo
╭────────────────────────── Semantic Memory ───────────────────────────────╮
│ status:       missing-vector-store                                        │
│ vector store: (not set — export OPENAI_VECTOR_STORE_ID)                  │
│ repo-signal:  available                                                   │
│ repo:         /path/to/repo                                               │
╰──────────────────────────────────────────────────────────────────────────╯
```

---

## Safety rules

| Rule | Behavior |
|---|---|
| No upload by default | `--dry-run` is the safe default |
| Missing vector store | Exits code 2 with clear error |
| Missing API key | Exits code 2 with clear error |
| No raw source | Only symbols and metadata are included |
| No secrets | Memory document never contains env vars or credentials |

---

## No-secret guarantee

The memory document contains only:

- Function and class names
- Docstrings
- Module structure
- Import patterns

It never contains:

- Raw file contents
- Environment variables
- API keys or credentials
- `.env` file contents

---

## Failure states

### Missing vector store

```text
repo-signal semantic-upload: OpenAI vector store id is missing.
Pass --vector-store-id or set OPENAI_VECTOR_STORE_ID.
```

Fix:

```bash
export OPENAI_VECTOR_STORE_ID="vs_..."
```

### Missing API key

The OpenAI client raises a configuration error before any upload is attempted.

Fix:

```bash
export OPENAI_API_KEY="sk-..."
```
