"""Safe patch suggestion planning — suggest.v1.

Reads repo signals and produces structured, human-reviewable suggestions.
Never writes to the repository. No mutations.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from repo_signal.inspect import inspect_repo_data
from repo_signal.publish_checklist import build_publish_checklist

VALID_FORMATS = {"text", "markdown", "json"}

_COMMIT_GROUP_RULES: list[tuple[list[str], str]] = [
    (["readme", "quick start", "screenshot", "demo", "roadmap", "positioning", "contributing", "wiki"], "docs"),
    (["license", ".gitignore", "gitignore", "junk", "cleanup"], "hygiene"),
    (["changelog", "version", "release", "pyproject"], "release"),
    (["test", "tests"], "testing"),
    (["github action", "workflow", "ci"], "ci"),
    (["github pages", "docs/", "landing page", "screenshot"], "pages"),
    (["example", "examples"], "examples"),
]

_RISK_HIGH_KEYWORDS = ["remove tracked", "force", "drop", "delete", "breaking"]
_RISK_MED_KEYWORDS = ["restructure", "rename", "move", "migrate", "fix", "run", "git rm"]


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _infer_commit_group(text: str) -> str:
    lower = text.lower()
    for keywords, group in _COMMIT_GROUP_RULES:
        if any(kw in lower for kw in keywords):
            return group
    return "docs"


def _infer_risk(hint: str) -> str:
    lower = hint.lower()
    if any(kw in lower for kw in _RISK_HIGH_KEYWORDS):
        return "high"
    if any(kw in lower for kw in _RISK_MED_KEYWORDS):
        return "medium"
    return "low"


def _diff_preview_for_file(filename: str, sample_content: str = "") -> str:
    lines = [f"--- /dev/null", f"+++ {filename}", "@@ -0,0 +1 @@"]
    if sample_content:
        for line in sample_content.splitlines()[:4]:
            lines.append(f"+{line}")
    else:
        lines.append(f"+# {filename}")
    return "\n".join(lines)


def _diff_preview_for_section(filename: str, heading: str) -> str:
    return "\n".join([
        f"--- {filename}",
        f"+++ {filename}",
        "@@ ... @@",
        f"+## {heading}",
        "+",
        "+<!-- add content here -->",
    ])


def _command_hint_from_hint(hint: str, check_name: str) -> str:
    lower_hint = hint.lower()
    lower_name = check_name.lower()

    file_map = {
        "readme.md": "touch README.md",
        "license": "touch LICENSE",
        "changelog.md": "touch CHANGELOG.md",
        "version": "echo '0.1.0' > VERSION",
        ".gitignore": "touch .gitignore",
        "contributing.md": "touch CONTRIBUTING.md",
    }
    for target, cmd in file_map.items():
        if target in lower_hint or target in lower_name:
            return cmd

    if "section" in lower_hint or "add" in lower_hint:
        return f"# Edit the relevant file to add: {hint}"

    return f"# {hint}"


def _suggestions_from_checklist(checklist: dict) -> list[dict[str, Any]]:
    suggestions = []
    seen_ids: set[str] = set()

    for group in checklist.get("groups", []):
        for check in group.get("checks", []):
            if check["status"] == "ok":
                continue

            name = check["name"]
            hint = check.get("hint", name)
            sid = _slug(name)

            if sid in seen_ids:
                continue
            seen_ids.add(sid)

            commit_group = _infer_commit_group(name + " " + hint)
            risk = _infer_risk(hint)

            # Build diff_preview
            if "section" in hint.lower() or "add" in hint.lower() and "." not in hint:
                diff_preview = _diff_preview_for_section("README.md", hint.replace("add ", "").title())
            else:
                target_file = hint.replace("add ", "").strip()
                diff_preview = _diff_preview_for_file(target_file)

            suggestions.append({
                "id": sid,
                "title": name,
                "description": hint,
                "risk": risk,
                "commit_group": commit_group,
                "diff_preview": diff_preview,
                "command_hint": _command_hint_from_hint(hint, name),
            })

    return suggestions


def _suggestions_from_inspect(inspect: dict, existing_ids: set[str]) -> list[dict[str, Any]]:
    suggestions = []

    for file_info in inspect.get("core_files", []):
        if isinstance(file_info, dict) and file_info.get("status") != "ok":
            path_str = file_info.get("path", "")
            label = file_info.get("label", path_str)
            sid = _slug(f"add-{path_str}")

            if sid in existing_ids:
                continue
            existing_ids.add(sid)

            commit_group = _infer_commit_group(path_str + " " + label)
            suggestions.append({
                "id": sid,
                "title": f"Add {label}",
                "description": f"add {path_str}",
                "risk": "low",
                "commit_group": commit_group,
                "diff_preview": _diff_preview_for_file(path_str),
                "command_hint": _command_hint_from_hint(f"add {path_str}", f"add {label}"),
            })

    for issue in inspect.get("issues", []):
        msg = issue.get("message", "") if isinstance(issue, dict) else str(issue)
        if not msg:
            continue
        sid = _slug(msg[:60])
        if sid in existing_ids:
            continue
        existing_ids.add(sid)

        level = issue.get("level", "warn") if isinstance(issue, dict) else "warn"
        risk = "high" if level == "error" else "medium" if level == "warn" else "low"

        suggestions.append({
            "id": sid,
            "title": msg,
            "description": msg,
            "risk": risk,
            "commit_group": _infer_commit_group(msg),
            "diff_preview": "",
            "command_hint": f"# Review: {msg}",
        })

    return suggestions


def build_suggestions(repo_path: str | Path = ".") -> dict[str, Any]:
    """Collect patch suggestions from repo signals. Never writes to disk."""
    root = Path(repo_path).resolve()

    inspect = inspect_repo_data(root)
    checklist = build_publish_checklist(str(root))

    suggestions = _suggestions_from_checklist(checklist)
    seen_ids = {s["id"] for s in suggestions}
    suggestions += _suggestions_from_inspect(inspect, seen_ids)

    by_risk: dict[str, int] = {"low": 0, "medium": 0, "high": 0}
    by_group: dict[str, int] = {}
    for s in suggestions:
        by_risk[s["risk"]] = by_risk.get(s["risk"], 0) + 1
        by_group[s["commit_group"]] = by_group.get(s["commit_group"], 0) + 1

    return {
        "schema": "suggest.v1",
        "repo": inspect.get("repo", {}).get("name", root.name),
        "path": str(root),
        "total": len(suggestions),
        "by_risk": by_risk,
        "by_group": by_group,
        "suggestions": suggestions,
    }


def format_suggestions(data: dict[str, Any], output_format: str = "text") -> str:
    if output_format not in VALID_FORMATS:
        raise ValueError(f"Unknown format: {output_format!r}. Choose from: {', '.join(sorted(VALID_FORMATS))}")

    if output_format == "json":
        return json.dumps(data, indent=2)

    repo = data["repo"]
    total = data["total"]
    by_risk = data["by_risk"]
    suggestions = data["suggestions"]

    if not suggestions:
        if output_format == "markdown":
            return f"# repo-signal suggest — {repo}\n\nNo suggestions. Repository looks complete.\n"
        return f"repo-signal suggest — {repo}\n  No suggestions. Repository looks complete."

    if output_format == "markdown":
        lines = [
            f"# repo-signal suggest — {repo}",
            "",
            f"**{total} suggestion{'s' if total != 1 else ''}**  ",
            f"low: {by_risk['low']}  medium: {by_risk['medium']}  high: {by_risk['high']}",
            "",
        ]
        for i, s in enumerate(suggestions, 1):
            lines += [
                f"## {i}. {s['title']}",
                "",
                f"**Risk:** {s['risk']}  **Group:** {s['commit_group']}",
                "",
                s["description"],
                "",
            ]
            if s["diff_preview"]:
                lines += ["```diff", s["diff_preview"], "```", ""]
            if s["command_hint"]:
                lines += ["```bash", s["command_hint"], "```", ""]
        return "\n".join(lines).rstrip()

    # text
    lines = [
        f"repo-signal suggest — {repo}",
        f"  {total} suggestion{'s' if total != 1 else ''}  "
        f"(low: {by_risk['low']}  medium: {by_risk['medium']}  high: {by_risk['high']})",
        "",
    ]
    for i, s in enumerate(suggestions, 1):
        lines.append(f"  {i}. [{s['risk'].upper()}] {s['title']}")
        lines.append(f"     group: {s['commit_group']}")
        lines.append(f"     hint:  {s['command_hint']}")
        lines.append("")
    return "\n".join(lines).rstrip()
