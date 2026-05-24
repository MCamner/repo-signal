"""Unified repo-signal report — combines inspect, publish-checklist and hygiene."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from repo_signal.inspect import inspect_repo_data
from repo_signal.publish_checklist import build_publish_checklist

VALID_FORMATS = {"text", "markdown", "json"}


def build_report(repo_path: str | Path = ".") -> dict[str, Any]:
    """Collect inspect.v1, publish-checklist and basic hygiene into one dict."""
    root = Path(repo_path).resolve()
    inspect = inspect_repo_data(root)
    checklist = build_publish_checklist(str(root))

    core_files = inspect.get("core_files", [])
    issues = inspect.get("issues", [])
    languages = inspect.get("detected", {}).get("languages", {})
    git = inspect.get("git", {})
    readiness = inspect.get("public_readiness", {})

    return {
        "schema": "report.v1",
        "repo": inspect.get("repo", {}).get("name", root.name),
        "path": str(root),
        "git": {
            "branch": git.get("branch"),
            "clean": git.get("clean"),
            "summary": git.get("summary"),
        },
        "languages": languages,
        "publish_score": checklist.get("score", 0),
        "publish_total": checklist.get("total", 0),
        "publish_status": checklist.get("status", "warn"),
        "core_files": core_files,
        "issues": [i.get("message", "") for i in issues],
        "recommended_next_action": readiness.get("recommended_next_action", ""),
        "recommended_next_commit": inspect.get("recommended_next_commit", ""),
        "useful_next_commands": inspect.get("useful_next_commands", []),
    }


def format_report(data: dict[str, Any], output_format: str = "text") -> str:
    if output_format not in VALID_FORMATS:
        raise ValueError(f"Unknown format: {output_format!r}. Choose from: {', '.join(sorted(VALID_FORMATS))}")

    if output_format == "json":
        return json.dumps(data, indent=2)

    repo = data["repo"]
    branch = data["git"].get("branch") or "unknown"
    clean = "clean" if data["git"].get("clean") else "dirty"
    score = data["publish_score"]
    total = data["publish_total"]
    status = data["publish_status"].upper()
    langs = ", ".join(data["languages"]) if data["languages"] else "unknown"
    issues = data["issues"]
    next_action = data["recommended_next_action"]
    next_commit = data["recommended_next_commit"]
    next_cmds = data["useful_next_commands"]
    core = data["core_files"]

    if output_format == "markdown":
        lines = [
            f"# repo-signal report — {repo}",
            "",
            f"**Branch:** {branch}  ",
            f"**Working tree:** {clean}  ",
            f"**Languages:** {langs}  ",
            "",
            f"## Publish readiness",
            "",
            f"Score: **{score}/{total}** ({status})",
            "",
        ]
        if next_action:
            lines += [f"Recommended next action: {next_action}", ""]
        if core:
            lines += ["## Core files", ""]
            for f in core:
                label = f["path"] if isinstance(f, dict) else str(f)
                lines.append(f"- `{label}`")
            lines.append("")
        if issues:
            lines += ["## Issues", ""]
            for i in issues:
                lines.append(f"- {i}")
            lines.append("")
        if next_commit:
            lines += [f"## Recommended next commit", "", next_commit, ""]
        if next_cmds:
            lines += ["## Useful next commands", ""]
            for cmd in next_cmds:
                lines.append(f"- `{cmd}`")
            lines.append("")
        return "\n".join(lines).rstrip()

    # text
    lines = [
        f"repo-signal report — {repo}",
        f"  branch : {branch}",
        f"  tree   : {clean}",
        f"  langs  : {langs}",
        f"  score  : {score}/{total} ({status})",
    ]
    if next_action:
        lines.append(f"  next   : {next_action}")
    if issues:
        lines.append("")
        lines.append("issues:")
        for i in issues:
            lines.append(f"  - {i}")
    if next_commit:
        lines.append("")
        lines.append(f"recommended commit: {next_commit}")
    if next_cmds:
        lines.append("")
        lines.append("useful commands:")
        for cmd in next_cmds:
            lines.append(f"  {cmd}")
    return "\n".join(lines)
