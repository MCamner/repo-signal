#!/usr/bin/env bash
# mqobsidian_export.sh — export one repo review into an mqobsidian vault.
#
# The vault comes from MQ_OBSIDIAN_DIR. Nothing here hard-codes a home
# directory or a machine-local path: the same script runs unchanged on any
# machine, and in CI against a throwaway vault.
#
#   MQ_OBSIDIAN_DIR=/tmp/vault ./mqobsidian_export.sh /path/to/repo
#
# Ownership, which this script respects and does not cross:
#   repo-signal produces signals. mqobsidian stores them. mq-agent owns
#   scoring, promotion and workflow orchestration. A review is a fresh
#   observation of a repo, not a promoted memory.
#
# Exit codes:
#   0  review written; its path is printed on stdout
#   1  repo-signal missing, or the vault is not configured
#   2  repo-signal refused: vault absent, unwritable, review already present,
#      or the source schema was not inspect.v1
set -euo pipefail

REPO="${1:-.}"

if ! command -v repo-signal >/dev/null 2>&1; then
  echo "repo-signal not found — run: pipx install repo-signal" >&2
  exit 1
fi

# Resolve the vault explicitly rather than letting the default ~/mqobsidian
# apply: a script that silently writes into someone's real notes is worse than
# one that stops and says what it needs.
if [[ -z "${MQ_OBSIDIAN_DIR:-}" ]]; then
  echo "MQ_OBSIDIAN_DIR is not set — point it at an mqobsidian vault" >&2
  exit 1
fi

if [[ ! -d "$MQ_OBSIDIAN_DIR" ]]; then
  echo "MQ_OBSIDIAN_DIR is not a directory: $MQ_OBSIDIAN_DIR" >&2
  exit 1
fi

# repo-signal reports vault faults as a readable message and exit 2 — no
# traceback — so the message is worth forwarding verbatim.
if ! output=$(repo-signal review-export "$REPO" --vault "$MQ_OBSIDIAN_DIR" 2>&1); then
  echo "review-export failed: $output" >&2
  exit 2
fi

# The review is written; confirm it declares both schemas before treating it as
# a contract artifact. An older repo-signal would write a different shape.
review="$output"
if [[ ! -f "$review" ]]; then
  echo "review-export reported a path that does not exist: $review" >&2
  exit 2
fi

if ! grep -q '^schema: repo-review.v1$' "$review"; then
  echo "Unexpected review schema in: $review — upgrade repo-signal" >&2
  exit 2
fi

if ! grep -q '^source_schema: inspect.v1$' "$review"; then
  echo "Review lost its inspect.v1 provenance: $review" >&2
  exit 2
fi

echo "$review"
