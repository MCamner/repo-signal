"""brief.v1 — compact daily health summary for a repository.

Combines publish_checklist, risk_map, and suggest into a single fast scan.
No external API keys required.
"""
from __future__ import annotations

import datetime
import json
import subprocess
from pathlib import Path
from typing import Any

SCHEMA = "brief.v1"

MAX_RISKS = 4
MAX_SUGGESTIONS = 4


def _git_last_commit(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%s"],
            capture_output=True, text=True, cwd=root, timeout=5,
        )
        msg = result.stdout.strip()
        return msg[:72] if msg else "—"
    except Exception:
        return "—"


def _health_label(score: int, total: int) -> str:
    if total == 0:
        return "unknown"
    pct = score / total
    if pct >= 0.9:
        return "good"
    if pct >= 0.7:
        return "fair"
    return "needs work"


def build_brief(repo_path: str | Path = ".") -> dict[str, Any]:
    from repo_signal.publish_checklist import build_publish_checklist
    from repo_signal.exports.risk_map import build_risk_map
    from repo_signal.suggest import build_suggestions

    root = Path(repo_path).resolve()

    checklist = build_publish_checklist(str(root))
    risk = build_risk_map(root)
    suggest = build_suggestions(root)

    score = checklist.get("score", 0)
    total = checklist.get("total", 0)

    risks = risk.get("risks", [])
    high_risks = [r for r in risks if r.get("level") == "high"]
    medium_risks = [r for r in risks if r.get("level") == "medium"]
    low_risks = [r for r in risks if r.get("level") == "low"]

    suggestions = suggest.get("suggestions", [])
    by_risk = suggest.get("by_risk", {})

    return {
        "schema": SCHEMA,
        "repo": root.name,
        "path": str(root),
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "last_commit": _git_last_commit(root),
        "health": {
            "score": score,
            "total": total,
            "label": _health_label(score, total),
        },
        "risks": {
            "high": len(high_risks),
            "medium": len(medium_risks),
            "low": len(low_risks),
            "total": len(risks),
            "top": risks[:MAX_RISKS],
        },
        "suggestions": {
            "total": len(suggestions),
            "by_risk": by_risk,
            "top": suggestions[:MAX_SUGGESTIONS],
        },
    }


def format_brief(data: dict[str, Any], output_format: str = "text") -> str:
    if output_format == "json":
        return json.dumps(data, indent=2)

    repo = data["repo"]
    health = data["health"]
    risks = data["risks"]
    suggs = data["suggestions"]
    last_commit = data.get("last_commit", "—")

    if output_format == "markdown":
        lines = [
            f"# Repo Brief — {repo}",
            "",
            f"| Field | Value |",
            f"| ----- | ----- |",
            f"| Health | {health['score']}/{health['total']} ({health['label']}) |",
            f"| Risks | {risks['high']} high · {risks['medium']} medium · {risks['low']} low |",
            f"| Suggestions | {suggs['total']} |",
            f"| Last commit | {last_commit} |",
            "",
        ]
        if risks["top"]:
            lines += ["## Top risks", ""]
            for r in risks["top"]:
                lines.append(f"- `[{r['level']}]` **{r['kind']}** {r.get('file', '')} — {r.get('detail', '')}")
            lines.append("")
        if suggs["top"]:
            lines += ["## Top suggestions", ""]
            for s in suggs["top"]:
                lines.append(f"- `[{s.get('risk','?')}]` **{s.get('group','')}** {s.get('title', '')}")
            lines.append("")
        lines.append(f"*brief.v1 — repo-signal*")
        return "\n".join(lines)

    # text (default)
    W = 56
    sep = "─" * W
    lines = [
        "",
        f"  Repo Brief — {repo}",
        f"  {sep}",
        f"  Health      {health['score']}/{health['total']}  ({health['label']})",
        f"  Risks       {risks['high']} high · {risks['medium']} medium · {risks['low']} low",
        f"  Suggestions {suggs['total']}",
        f"  Last commit {last_commit}",
        f"  {sep}",
    ]
    if risks["top"]:
        lines.append("  Risks")
        for r in risks["top"]:
            tag = f"[{r['level'][:3]}]"
            detail = r.get("detail", r.get("file", ""))[:42]
            lines.append(f"    {tag}  {r['kind']}  {detail}")
    if suggs["top"]:
        if risks["top"]:
            lines.append("")
        lines.append("  Suggestions")
        for s in suggs["top"]:
            tag = f"[{s.get('risk','?')[:3]}]"
            title = s.get("title", "")[:42]
            lines.append(f"    {tag}  {s.get('group','')}  {title}")
    lines += [f"  {sep}", "  brief.v1", ""]
    return "\n".join(lines)
