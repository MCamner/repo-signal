"""Fast repository inspection report.

`inspect` is intentionally smaller than `doctor`.
It answers: what is this repo, what is present, what looks weak,
and what should the next useful commit probably be?
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from repo_signal.core.models import Repository
from repo_signal.publish_checklist import build_publish_checklist


CORE_FILES = [
    ("README.md", "README"),
    ("LICENSE", "License"),
    (".gitignore", "Git ignore rules"),
    ("CHANGELOG.md", "Changelog"),
    ("VERSION", "Version file"),
    ("docs", "Docs folder"),
    ("docs/index.html", "GitHub Pages landing"),
    ("docs/screenshots", "Screenshots/output gallery"),
    ("examples", "Examples folder"),
    ("tests", "Tests folder"),
]


def _as_path(path: str | Path | None) -> Path:
    if path is None:
        return Path.cwd()
    return Path(path).expanduser().resolve()


def _get(obj: Any, name: str, default: Any = None) -> Any:
    return getattr(obj, name, default)


def _format_mapping(value: Any, limit: int = 6) -> str:
    if not value:
        return "none detected"

    if isinstance(value, dict):
        items = sorted(value.items(), key=lambda item: str(item[0]).lower())
        rendered = [f"{key} ({count})" for key, count in items[:limit]]
    else:
        rendered = [str(item) for item in list(value)[:limit]]

    extra = ""
    try:
        if len(value) > limit:
            extra = f", +{len(value) - limit} more"
    except TypeError:
        extra = ""

    return ", ".join(rendered) + extra


def _format_list(value: Any, limit: int = 7) -> str:
    if not value:
        return "none detected"

    items: list[str] = []
    for item in list(value)[:limit]:
        if isinstance(item, tuple) and item:
            if len(item) > 1:
                items.append(f"{item[0]} ({item[1]})")
            else:
                items.append(str(item[0]))
        else:
            items.append(str(item))

    extra = ""
    try:
        if len(value) > limit:
            extra = f", +{len(value) - limit} more"
    except TypeError:
        extra = ""

    return ", ".join(items) + extra


def _top_directories(repo_model: Any) -> Any:
    counts = _get(repo_model, "top_directory_counts", {})
    if counts:
        return counts
    return _get(repo_model, "top_directories", [])


def _status_for_path(repo: Path, rel_path: str) -> str:
    return "OK" if (repo / rel_path).exists() else "MISSING"


def _git_summary(repo_model: Any) -> str:
    git = _get(repo_model, "git")
    if git is None:
        return "unknown"

    is_repo = bool(_get(git, "is_repo", False))
    if not is_repo:
        return "not a git repo"

    branch = _get(git, "branch", "") or "unknown branch"
    status_lines = (
        _get(git, "status_lines", None)
        or _get(git, "status", None)
        or _get(git, "changes", None)
        or []
    )

    try:
        change_count = len(status_lines)
    except TypeError:
        change_count = 0

    if change_count:
        return f"git repo, branch {branch}, {change_count} working tree change(s)"

    return f"git repo, branch {branch}, clean"


def _publish_summary(repo: Path) -> tuple[str, str, int | None, int | None]:
    try:
        result = build_publish_checklist(str(repo))
    except Exception as exc:
        return f"unavailable ({exc})", "run publish-checklist manually", None, None

    score = result.get("score")
    total = result.get("total")
    raw_status = str(result.get("status", "unknown")).lower()
    status = {"pass": "OK", "warn": "WARN"}.get(raw_status, raw_status.upper())
    recommended = str(result.get("recommended_next_action", "") or "").strip()

    if score is None or total is None:
        return status, recommended, None, None

    return f"{score}/{total} {status}", recommended, int(score), int(total)


def _possible_issues(
    repo_path: Path,
    repo_model: Any,
    publish_next: str,
    score: int | None,
    total: int | None,
) -> list[str]:
    issues: list[str] = []

    for rel_path, label in CORE_FILES:
        if not (repo_path / rel_path).exists():
            issues.append(f"[WARN] Missing {label}: {rel_path}")

    entrypoints = _get(repo_model, "entrypoints", [])
    if not entrypoints:
        issues.append("[WARN] No clear entrypoints detected")

    detected_tooling = _get(repo_model, "detected_tooling", [])
    if not detected_tooling:
        issues.append("[INFO] No packaging/tooling signal detected")

    if score is not None and total is not None and score < total:
        detail = f": {publish_next}" if publish_next else ""
        issues.append(f"[WARN] Publish checklist is not perfect ({score}/{total}){detail}")

    return issues


def _recommended_next_commit(issues: list[str], publish_next: str) -> str:
    publish_ready = publish_next.lower().startswith("repo looks publish-ready")
    if publish_next and not publish_next.lower().startswith("none") and not publish_ready:
        clean = publish_next
        if clean.lower().startswith("fix:"):
            clean = clean[4:].strip()
        if clean.endswith(")") and "(" in clean:
            hint = clean.rsplit("(", 1)[1][:-1].strip()
            if hint:
                clean = hint
        return clean[:1].upper() + clean[1:]

    if issues:
        first = issues[0]
        for prefix in ("[WARN] ", "[INFO] ", "[HIGH] ", "[MED] ", "[LOW] "):
            first = first.replace(prefix, "")
        return first

    return "Keep docs, examples, and command reference synced with the CLI"


def inspect_repo(path: str | Path | None = None) -> str:
    repo_path = _as_path(path)

    lines: list[str] = []
    lines.append("REPO INSPECTION")
    lines.append("===============")
    lines.append("")

    if not repo_path.exists():
        lines.append(f"Path: {repo_path}")
        lines.append("Status: MISSING")
        lines.append("")
        lines.append("Recommended next commit:")
        lines.append("Choose an existing repository path")
        return "\n".join(lines)

    repo = Repository.load(repo_path)
    publish_summary, publish_next, score, total = _publish_summary(repo_path)
    issues = _possible_issues(repo_path, repo, publish_next, score, total)

    project_type = _get(repo, "project_type", "") or "unknown"
    file_count = _get(repo, "repo_size_files", None)
    if file_count is None:
        try:
            file_count = len(_get(repo, "files", []))
        except TypeError:
            file_count = "unknown"

    lines.append(f"Repo: {repo_path.name}")
    lines.append(f"Path: {repo_path}")
    lines.append(f"Type: {project_type}")
    lines.append(f"Files: {file_count}")
    lines.append(f"Git: {_git_summary(repo)}")
    lines.append(f"Public readiness: {publish_summary}")
    lines.append("")

    lines.append("Detected")
    lines.append("--------")
    lines.append(f"Languages: {_format_mapping(_get(repo, 'languages', {}))}")
    lines.append(f"Entry points: {_format_list(_get(repo, 'entrypoints', []))}")
    lines.append(f"Tooling: {_format_list(_get(repo, 'detected_tooling', []))}")
    lines.append(f"Top directories: {_format_mapping(_top_directories(repo))}")
    lines.append("")

    lines.append("Core files")
    lines.append("----------")
    for rel_path, label in CORE_FILES:
        lines.append(f"- [{_status_for_path(repo_path, rel_path)}] {label}: {rel_path}")
    lines.append("")

    lines.append("Possible issues")
    lines.append("---------------")
    if issues:
        lines.extend(f"- {issue}" for issue in issues[:12])
        if len(issues) > 12:
            lines.append(f"- [INFO] Additional issues hidden: {len(issues) - 12}")
    else:
        lines.append("- [OK] No obvious front-door issue detected")
    lines.append("")

    lines.append("Recommended next commit")
    lines.append("-----------------------")
    lines.append(_recommended_next_commit(issues, publish_next))
    lines.append("")

    lines.append("Useful next commands")
    lines.append("--------------------")
    lines.append("repo-signal doctor")
    lines.append("repo-signal publish-checklist . --fail-under 16")
    lines.append('repo-signal repoaware --mode review --format markdown "what should I inspect first"')

    return "\n".join(lines)


__all__ = ["inspect_repo"]
