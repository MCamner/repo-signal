from repo_signal.core.models import RepoSummary
from repo_signal.core.scanner import scan_repository


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def format_list(items: list[str], empty: str = "none detected") -> list[str]:
    if not items:
        return [f"- {empty}"]
    return [f"- {item}" for item in items]


def format_analyze_report(summary: RepoSummary) -> str:
    lines = []

    lines.append("# Repo Signal Analyze Report")
    lines.append("")
    lines.append(f"Repo: `{summary.path.name}`")
    lines.append(f"Path: `{summary.path}`")
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Project type: `{summary.project_type}`")
    lines.append(f"- Files scanned: `{summary.repo_size_files}`")
    lines.append(f"- Approx size: `{summary.repo_size_mb:.2f} MB`")
    lines.append(f"- Git repo: `{yes_no(summary.git.is_repo)}`")
    if summary.git.is_repo:
        lines.append(f"- Git branch: `{summary.git.branch or 'unknown'}`")
        lines.append(f"- Working tree changes: `{summary.git.changed_files}`")
    lines.append("")

    lines.append("## Languages")
    lines.append("")
    if summary.languages:
        for language, count in summary.languages:
            lines.append(f"- {language}: `{count}` files")
    else:
        lines.append("- none detected")
    lines.append("")

    lines.append("## Key Entry Points")
    lines.append("")
    lines.extend(format_list(summary.key_entrypoints))
    lines.append("")

    lines.append("## Top Directories")
    lines.append("")
    if summary.top_directories:
        for directory, count in summary.top_directories:
            lines.append(f"- `{directory}`: `{count}` files")
    else:
        lines.append("- none detected")
    lines.append("")

    lines.append("## Detected Tooling")
    lines.append("")
    lines.extend(format_list(summary.detected_tooling))
    lines.append("")

    lines.append("## Git Health")
    lines.append("")
    if not summary.git.is_repo:
        lines.append("- [WARN] Not a Git repository")
    elif summary.git.changed_files:
        lines.append(f"- [MED] Working tree has changes: `{summary.git.changed_files}`")
        for status_line in summary.git.status_lines[:10]:
            lines.append(f"  - `{status_line}`")
    else:
        lines.append("- [OK] Working tree clean")
    lines.append("")

    lines.append("## Suggested Focus Areas")
    lines.append("")
    for index, focus in enumerate(summary.focus_areas, start=1):
        lines.append(f"{index}. {focus}")

    return "\n".join(lines)


def analyze_repo(repo_path: str) -> str:
    return format_analyze_report(scan_repository(repo_path))

