"""Export a fresh repo-signal inspection as mqobsidian repo-review.v1."""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "repo-review.v1"
SOURCE_SCHEMA = "inspect.v1"


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "repo"


def _scalar(value: Any) -> str:
    return str(value or "").replace("\r", " ").replace("\n", " ").strip()


def resolve_vault(path: str | Path | None = None) -> Path:
    """Resolve an existing mqobsidian vault without guessing private paths."""
    candidate = Path(path).expanduser() if path is not None else None
    if candidate is None:
        configured = os.environ.get("MQ_OBSIDIAN_DIR")
        candidate = Path(configured).expanduser() if configured else Path.home() / "mqobsidian"
    candidate = candidate.resolve()
    if not candidate.is_dir():
        raise FileNotFoundError(f"mqobsidian vault not found: {candidate}")
    return candidate


def build_repo_review(data: dict[str, Any], *, created_at: str | None = None) -> str:
    """Map inspect.v1 data to compact, public-safe repo-review.v1 Markdown."""
    if data.get("schema") != SOURCE_SCHEMA:
        raise ValueError(f"expected {SOURCE_SCHEMA}, got {data.get('schema', 'missing')}")
    repo = data.get("repo") or {}
    if not repo.get("exists"):
        raise ValueError("cannot export a review for a missing repository")

    name = _scalar(repo.get("name")) or "repo"
    timestamp = created_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    issues = data.get("issues") or []
    findings = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        message = _scalar(issue.get("message"))
        if not message:
            continue
        level = _scalar(issue.get("level")).upper() or "INFO"
        findings.append(f"[{level}] {message}")

    readiness = _scalar((data.get("public_readiness") or {}).get("summary"))
    summary = f"repo-signal inspect found {len(findings)} finding(s)"
    if readiness:
        summary += f"; public readiness {readiness}"
    recommendation = _scalar(data.get("recommended_next_commit")) or "No next action reported."
    finding_lines = "\n".join(f"- {finding}" for finding in findings) or "- No findings."

    return f"""---
schema: {SCHEMA}
repo: {name}
created_at: {timestamp}
summary: {summary}
source: repo-signal
source_schema: {SOURCE_SCHEMA}
---

# Repo Review: {name}

## Findings

{finding_lines}

## Recommendation

{recommendation}
"""


def export_repo_review(
    data: dict[str, Any],
    *,
    vault: str | Path,
    force: bool = False,
    created_at: str | None = None,
) -> Path:
    """Write one review below the vault's reviews directory."""
    vault_path = resolve_vault(vault)
    content = build_repo_review(data, created_at=created_at)
    repo_name = _slug(_scalar((data.get("repo") or {}).get("name")))
    timestamp = created_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    date = timestamp[:10]
    output = vault_path / "reviews" / f"{date}-repo-signal-{repo_name}.md"
    if output.exists() and not force:
        raise FileExistsError(f"review already exists: {output} (use --force to replace it)")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    return output
