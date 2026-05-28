"""Fast repository inspection report.

`inspect` is intentionally smaller than `doctor`.

Text mode answers:
- what is this repo?
- what is present?
- what looks weak?
- what should the next useful commit probably be?

JSON mode provides the `inspect.v1` integration contract for mqlaunch,
mq-hal, mq-mcp, Bridget, and other tools that should not parse terminal text.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from repo_signal.core.models import Repository
from repo_signal.publish_checklist import build_publish_checklist


INSPECT_SCHEMA = "inspect.v1"

CORE_FILES = [
    ("README.md", "README", "required"),
    ("LICENSE", "License", "required"),
    (".gitignore", "Git ignore rules", "required"),
    ("CHANGELOG.md", "Changelog", "required"),
    ("VERSION", "Version file", "required"),
    ("docs", "Docs folder", "required"),
    ("docs/index.html", "GitHub Pages landing", "required"),
    ("docs/screenshots", "Screenshots/output gallery", "optional"),
    ("examples", "Examples folder", "optional"),
    ("tests", "Tests folder", "required"),
]

USEFUL_NEXT_COMMANDS = [
    "repo-signal doctor",
    "repo-signal publish-checklist . --fail-under 16",
    'repo-signal repoaware --mode review --format markdown "what should I inspect first"',
]


def _as_path(path: str | Path | None) -> Path:
    if path is None:
        return Path.cwd()
    return Path(path).expanduser().resolve()


def _get(obj: Any, name: str, default: Any = None) -> Any:
    return getattr(obj, name, default)


def _json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, set):
        return sorted(_json_safe(item) for item in value)
    return value


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


def _core_file_records(repo: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for rel_path, label, importance in CORE_FILES:
        exists = (repo / rel_path).exists()
        records.append(
            {
                "path": rel_path,
                "label": label,
                "importance": importance,
                "exists": exists,
                "status": "ok" if exists else "missing",
            }
        )
    return records


def _status_for_path(repo: Path, rel_path: str) -> str:
    return "OK" if (repo / rel_path).exists() else "MISSING"


def _git_details(repo_model: Any) -> dict[str, Any]:
    git = _get(repo_model, "git")
    if git is None:
        return {
            "is_repo": None,
            "branch": None,
            "change_count": None,
            "clean": None,
            "summary": "unknown",
        }

    is_repo = bool(_get(git, "is_repo", False))
    if not is_repo:
        return {
            "is_repo": False,
            "branch": None,
            "change_count": None,
            "clean": None,
            "summary": "not a git repo",
        }

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

    clean = change_count == 0
    if clean:
        summary = f"git repo, branch {branch}, clean"
    else:
        summary = f"git repo, branch {branch}, {change_count} working tree change(s)"

    return {
        "is_repo": True,
        "branch": branch,
        "change_count": change_count,
        "clean": clean,
        "summary": summary,
    }


def _git_summary(repo_model: Any) -> str:
    return str(_git_details(repo_model)["summary"])


def _publish_details(repo: Path) -> dict[str, Any]:
    try:
        result = build_publish_checklist(str(repo))
    except Exception as exc:
        return {
            "available": False,
            "summary": f"unavailable ({exc})",
            "status": "unavailable",
            "score": None,
            "total": None,
            "recommended_next_action": "run publish-checklist manually",
            "error": str(exc),
        }

    score = result.get("score")
    total = result.get("total")
    raw_status = str(result.get("status", "unknown")).lower()
    status = {"pass": "ok", "warn": "warn"}.get(raw_status, raw_status)
    recommended = str(result.get("recommended_next_action", "") or "").strip()

    if score is None or total is None:
        summary = status.upper()
    else:
        summary = f"{score}/{total} {status.upper()}"

    return {
        "available": True,
        "summary": summary,
        "status": status,
        "score": score,
        "total": total,
        "recommended_next_action": recommended,
        "error": None,
    }


def _publish_summary(repo: Path) -> tuple[str, str, int | None, int | None]:
    details = _publish_details(repo)
    return (
        str(details["summary"]),
        str(details["recommended_next_action"] or ""),
        details["score"],
        details["total"],
    )


def _possible_issues(
    repo_path: Path,
    repo_model: Any,
    publish_next: str,
    score: int | None,
    total: int | None,
) -> list[str]:
    issues: list[str] = []

    for rel_path, label, importance in CORE_FILES:
        if not (repo_path / rel_path).exists():
            if importance == "optional":
                issues.append(f"[OPTIONAL] Missing {label}: {rel_path}")
            else:
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


def _issue_records(issues: list[str]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for issue in issues:
        level = "info"
        message = issue

        for marker, normalized in (
            ("[HIGH]", "high"),
            ("[MED]", "medium"),
            ("[LOW]", "low"),
            ("[WARN]", "warn"),
            ("[OPTIONAL]", "optional"),
            ("[INFO]", "info"),
            ("[OK]", "ok"),
        ):
            if issue.startswith(marker):
                level = normalized
                message = issue.replace(marker, "", 1).strip()
                break

        records.append({"level": level, "message": message, "raw": issue})

    return records


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

    actionable = [issue for issue in issues if not issue.startswith("[OPTIONAL]")]

    if actionable:
        first = actionable[0]
        for prefix in ("[WARN] ", "[INFO] ", "[HIGH] ", "[MED] ", "[LOW] "):
            first = first.replace(prefix, "")
        return first

    if publish_ready:
        return "None — repo is publish-ready. Optional polish only."

    return "Keep docs, examples, and command reference synced with the CLI"


def inspect_repo_data(path: str | Path | None = None) -> dict[str, Any]:
    """Return the inspect.v1 integration contract."""

    repo_path = _as_path(path)

    if not repo_path.exists():
        return {
            "schema": INSPECT_SCHEMA,
            "repo": {
                "name": repo_path.name,
                "path": str(repo_path),
                "exists": False,
                "type": None,
                "files": None,
            },
            "git": {
                "is_repo": None,
                "branch": None,
                "change_count": None,
                "clean": None,
                "summary": "unknown",
            },
            "public_readiness": {
                "available": False,
                "summary": "unavailable",
                "status": "unavailable",
                "score": None,
                "total": None,
                "recommended_next_action": "choose an existing repository path",
                "error": "path does not exist",
            },
            "detected": {
                "languages": {},
                "entrypoints": [],
                "tooling": [],
                "top_directories": {},
            },
            "core_files": [],
            "issues": [
                {
                    "level": "warn",
                    "message": "Path does not exist",
                    "raw": "[WARN] Path does not exist",
                }
            ],
            "recommended_next_commit": "Choose an existing repository path",
            "useful_next_commands": [],
        }

    repo = Repository.load(repo_path)
    publish = _publish_details(repo_path)
    publish_next = str(publish.get("recommended_next_action") or "")
    score = publish.get("score")
    total = publish.get("total")
    issues = _possible_issues(repo_path, repo, publish_next, score, total)
    recommended_next_commit = _recommended_next_commit(issues, publish_next)

    file_count = _get(repo, "repo_size_files", None)
    if file_count is None:
        try:
            file_count = len(_get(repo, "files", []))
        except TypeError:
            file_count = None

    return {
        "schema": INSPECT_SCHEMA,
        "repo": {
            "name": repo_path.name,
            "path": str(repo_path),
            "exists": True,
            "type": _get(repo, "project_type", "") or "unknown",
            "files": file_count,
        },
        "git": _git_details(repo),
        "public_readiness": publish,
        "detected": {
            "languages": _json_safe(_get(repo, "languages", {})),
            "entrypoints": _json_safe(_get(repo, "entrypoints", [])),
            "tooling": _json_safe(_get(repo, "detected_tooling", [])),
            "top_directories": _json_safe(_top_directories(repo)),
        },
        "core_files": _core_file_records(repo_path),
        "issues": _issue_records(issues),
        "recommended_next_commit": recommended_next_commit,
        "useful_next_commands": USEFUL_NEXT_COMMANDS,
    }


def inspect_repo(path: str | Path | None = None, output_format: str = "text") -> str:
    data = inspect_repo_data(path)

    if output_format == "json":
        return json.dumps(data, indent=2, sort_keys=True)

    if output_format != "text":
        raise ValueError(f"Unknown inspect output format: {output_format}")

    lines: list[str] = []
    lines.append("REPO INSPECTION")
    lines.append("===============")
    lines.append("")

    repo = data["repo"]

    if not repo["exists"]:
        lines.append(f"Path: {repo['path']}")
        lines.append("Status: MISSING")
        lines.append("")
        lines.append("Recommended next commit:")
        lines.append(data["recommended_next_commit"])
        return "\n".join(lines)

    detected = data["detected"]
    publish = data["public_readiness"]

    lines.append(f"Repo: {repo['name']}")
    lines.append(f"Path: {repo['path']}")
    lines.append(f"Type: {repo['type']}")
    lines.append(f"Files: {repo['files']}")
    lines.append(f"Git: {data['git']['summary']}")
    lines.append(f"Public readiness: {publish['summary']}")
    lines.append("")

    lines.append("Detected")
    lines.append("--------")
    lines.append(f"Languages: {_format_mapping(detected['languages'])}")
    lines.append(f"Entry points: {_format_list(detected['entrypoints'])}")
    lines.append(f"Tooling: {_format_list(detected['tooling'])}")
    lines.append(f"Top directories: {_format_mapping(detected['top_directories'])}")
    lines.append("")

    lines.append("Core files")
    lines.append("----------")
    for record in data["core_files"]:
        status = "OK" if record["exists"] else "MISSING"
        lines.append(f"- [{status}] {record['label']}: {record['path']}")
    lines.append("")

    lines.append("Possible issues")
    lines.append("---------------")
    issues = data["issues"]
    if issues:
        for issue in issues[:12]:
            lines.append(f"- {issue['raw']}")
        if len(issues) > 12:
            lines.append(f"- [INFO] Additional issues hidden: {len(issues) - 12}")
    else:
        lines.append("- [OK] No obvious front-door issue detected")
    lines.append("")

    lines.append("Recommended next commit")
    lines.append("-----------------------")
    lines.append(data["recommended_next_commit"])
    lines.append("")

    lines.append("Useful next commands")
    lines.append("--------------------")
    for command in data["useful_next_commands"]:
        lines.append(command)

    return "\n".join(lines)


__all__ = ["INSPECT_SCHEMA", "inspect_repo", "inspect_repo_data"]
