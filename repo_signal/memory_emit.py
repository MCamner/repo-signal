"""Spak 2 — minimal real `memory-observation.v1` emitter (Phase 12).

Single purpose: make multi-producer memory data REAL by letting repo-signal emit
ONE genuine `memory-observation.v1` record during an actual `inspect` run.

HARD SCOPE — do NOT extend this module:
- maps ONE real signal (the top `inspect` issue) -> one `memory-observation.v1`
- writes to the REAL, local-only, gitignored observation surface in the
  mqobsidian vault (`memory/observations/repo-signal.observations.jsonl`)
- an observation is a *proposal*, not a memory.

EXPLICITLY OUT OF SCOPE (lives elsewhere, deferred — see mqobsidian ADR-008/009):
- no scoring, no promotion/demotion, no DD-001 logic, no `evaluate_memory`
- no merge engine, no new status vocabulary, no contract change
- no synthetic bootstrap: only a real inspect run may emit, and a run with no
  real issue emits nothing.

Emission is opt-in (`REPO_SIGNAL_EMIT_MEMORY=1`) and NEVER raises into the
caller: a failed emission must not change any other repo-signal behaviour.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PRODUCER = "repo-signal"
SCHEMA = "memory-observation.v1"

# The observation's own confidence field (required by the contract). This is the
# producer's stated certainty in the *signal*, NOT a memory score — no promotion
# logic reads it here.
_LEVEL_CONFIDENCE = {"fail": 0.8, "error": 0.75, "warn": 0.6, "info": 0.5}
_LEVEL_RANK = {"fail": 3, "error": 2, "warn": 1, "info": 0}


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:48] or "issue"


def vault_dir() -> Path | None:
    """Resolve the mqobsidian vault: env first, then a home-relative default.

    Returns None (rather than guessing an absolute path) if nothing is found, so
    the emitter stays silent instead of writing somewhere wrong.
    """
    env = os.environ.get("MQ_OBSIDIAN_DIR")
    if env and Path(env).is_dir():
        return Path(env)
    default = Path.home() / "mqobsidian"
    return default if default.is_dir() else None


def surface_path(vault: Path) -> Path:
    return vault / "memory" / "observations" / "repo-signal.observations.jsonl"


def _top_issue(issues: list[dict[str, Any]]) -> dict[str, Any] | None:
    real = [i for i in issues if (i.get("message") or "").strip()]
    if not real:
        return None
    return max(real, key=lambda i: _LEVEL_RANK.get(i.get("level", "info"), 0))


def observation_from_inspect(data: dict[str, Any]) -> dict[str, Any] | None:
    """Map ONE real inspect result -> one memory-observation.v1, or None.

    Returns None when there is no real signal worth emitting (repo missing, or no
    issue surfaced). Evidence-bearing only — never a placeholder.
    """
    repo = data.get("repo") or {}
    if not repo.get("exists"):
        return None
    issue = _top_issue(data.get("issues") or [])
    if issue is None:
        return None

    name = repo.get("name") or Path(str(repo.get("path", "repo"))).name
    level = issue.get("level", "info")
    message = (issue.get("message") or "").strip()
    raw = (issue.get("raw") or message).strip()
    next_commit = (data.get("recommended_next_commit") or "").strip()
    ts = datetime.now(timezone.utc)
    ts_compact = ts.strftime("%Y%m%d%H%M%S")

    record: dict[str, Any] = {
        "schema": SCHEMA,
        "id": f"obs_rs_{_slug(name)}_{ts_compact}_{_slug(message)}",
        "timestamp": ts.isoformat().replace("+00:00", "Z"),
        "producer": PRODUCER,
        "repository": str(name),
        "workflow": "repo-inspect",
        "title": message,
        "summary": f"repo-signal inspect of {name} flagged a real issue.",
        "observation": next_commit or message,
        "category": "review",
        "confidence": _LEVEL_CONFIDENCE.get(level, 0.5),
        "evidence": [
            {
                "source": "repo-signal inspect.v1",
                "reference": str(repo.get("path", name)),
                "excerpt": raw,
            }
        ],
        "tags": ["repo-signal", "inspect", level],
        "proposed_memory_key": _slug(message),
    }

    branch = (data.get("git") or {}).get("branch")
    if isinstance(branch, str) and branch:
        record["metadata"] = {"branch": branch}

    session = os.environ.get("REPO_SIGNAL_SESSION")
    if session:
        record["session_id"] = session

    return record


def emit_from_inspect(
    data: dict[str, Any], *, surface: Path | None = None
) -> Path | None:
    """Build one observation from a real inspect result and append it.

    Returns the surface path written, or None if nothing was emitted. Raises only
    on a genuine I/O fault — callers in the live path must wrap (see
    `maybe_emit_memory`).
    """
    record = observation_from_inspect(data)
    if record is None:
        return None
    if surface is None:
        vault = vault_dir()
        if vault is None:
            return None
        surface = surface_path(vault)
    surface.parent.mkdir(parents=True, exist_ok=True)
    with surface.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return surface


def maybe_emit_memory(data: dict[str, Any]) -> Path | None:
    """Env-gated, failure-isolated hook for the live inspect path.

    No-op unless `REPO_SIGNAL_EMIT_MEMORY=1`. Never raises: a failed emission must
    not change any other repo-signal behaviour.
    """
    if os.environ.get("REPO_SIGNAL_EMIT_MEMORY") != "1":
        return None
    try:
        return emit_from_inspect(data)
    except Exception:  # noqa: BLE001 — emission must never break inspect
        return None
