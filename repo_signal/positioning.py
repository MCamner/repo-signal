import json
from pathlib import Path
import re
from typing import Any

from repo_signal.core.models import Repository
from repo_signal.core.scanner import scan_repository


VALID_FORMATS = {"text", "json"}


STOP_WORDS = {
    "and",
    "for",
    "from",
    "into",
    "the",
    "this",
    "that",
    "with",
    "your",
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(errors="ignore")
    except OSError:
        return ""


def first_useful_readme_line(text: str) -> str:
    for line in text.splitlines():
        clean = line.strip()
        if not clean:
            continue
        if clean.startswith(("#", "[!", "![", "---")):
            continue
        if clean.startswith("`") and clean.endswith("`"):
            continue
        if len(re.findall(r"\b[\w'-]+\b", clean)) >= 5:
            return clean
    return ""


def heading_names(text: str) -> list[str]:
    return [match.group(1).strip() for match in re.finditer(r"^##+\s+(.+?)\s*$", text, flags=re.MULTILINE)]


def top_keywords(text: str, limit: int = 8) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9-]{2,}", text.lower())
    counts: dict[str, int] = {}
    for word in words:
        if word in STOP_WORDS:
            continue
        counts[word] = counts.get(word, 0) + 1
    return [word for word, _count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]]


def has_any(text: str, needles: list[str]) -> bool:
    lowered = text.lower()
    return any(needle in lowered for needle in needles)


def infer_audience(repo: Repository, readme_text: str) -> str:
    text = readme_text.lower()

    if has_any(text, ["developer", "cli", "repository", "repo", "github", "automation"]):
        return "Developers who need a fast, local view of repository readiness and AI context."
    if has_any(text, ["portfolio", "publish", "showcase"]):
        return "Builders preparing a project for public sharing or portfolio review."
    if "api" in text or "sdk" in text:
        return "Developers integrating with an API or reusable library."
    if "dashboard" in text or "web" in repo.project_type.lower():
        return "Users evaluating or operating a web-facing project."

    return "People evaluating what the repository does and whether it is ready to use."


def infer_problem(repo: Repository, readme_text: str) -> str:
    text = readme_text.lower()

    if has_any(text, ["publish", "readiness", "roadmap", "checklist"]):
        return "It reduces the friction of understanding whether a repo is clear, documented, and ready to publish."
    if has_any(text, ["ai", "context", "assistant", "semantic"]):
        return "It turns repository structure into useful context for AI-assisted development."
    if has_any(text, ["automation", "cli", "terminal"]):
        return "It packages repeatable local workflow checks behind a predictable command surface."

    return "It helps a reader quickly understand the repo's purpose, state, and next step."


def strongest_angle(repo: Repository, readme_text: str) -> str:
    if has_any(readme_text, ["ai", "context", "assistant"]) and has_any(readme_text, ["publish", "readiness"]):
        return "Lead with repo intelligence for AI-assisted publish readiness."
    if has_any(readme_text, ["cli", "terminal", "automation"]):
        return "Lead with a practical local CLI workflow and show the first useful command."
    if repo.entrypoints:
        return f"Lead with the primary command or entrypoint: `{repo.entrypoints[0]}`."
    return "Lead with the clearest user problem before listing implementation details."


def unclear_items(readme_text: str, headings: list[str]) -> list[str]:
    items = []
    lowered_headings = " ".join(headings).lower()
    lowered_readme = readme_text.lower()

    if not has_any(lowered_readme, ["who", "for developers", "for teams", "for people"]):
        items.append("The target audience could be stated more directly.")
    if "install" not in lowered_headings and "installation" not in lowered_headings:
        items.append("Install path is not obvious from the section structure.")
    if not has_any(lowered_readme, ["example", "demo", "screenshot"]):
        items.append("The README could show a concrete example or output.")
    if not has_any(lowered_readme, ["why", "problem", "helps"]):
        items.append("The core problem statement could be sharper.")

    return items[:5] or ["Positioning is reasonably clear; polish the one-sentence promise next."]


def one_sentence(repo: Repository, readme_pitch: str, problem: str) -> str:
    if readme_pitch:
        clean = readme_pitch.rstrip(".")
        if len(clean) <= 160:
            return clean + "."

    return f"{repo.name} helps {problem[0].lower() + problem[1:]}"


def build_positioning_report(repo_path: str = ".") -> dict[str, Any]:
    repo = scan_repository(repo_path)
    readme_path = repo.path / "README.md"
    readme_text = read_text(readme_path)
    pitch = first_useful_readme_line(readme_text)
    headings = heading_names(readme_text)
    audience = infer_audience(repo, readme_text)
    problem = infer_problem(repo, readme_text)

    return {
        "schema": "positioning.v1",
        "repo": repo.name,
        "path": str(repo.path),
        "project_type": repo.project_type,
        "what_is_this": pitch or f"{repo.name} is a {repo.project_type.lower()}.",
        "who_is_it_for": audience,
        "problem_it_solves": problem,
        "strongest_readme_angle": strongest_angle(repo, readme_text),
        "what_is_unclear": unclear_items(readme_text, headings),
        "one_sentence": one_sentence(repo, pitch, problem),
        "evidence": {
            "readme_exists": readme_path.exists(),
            "readme_headings": headings[:12],
            "top_keywords": top_keywords(readme_text),
            "languages": repo.languages,
            "entrypoints": repo.entrypoints,
            "tooling": repo.detected_tooling,
        },
    }


def format_positioning_text(report: dict[str, Any]) -> str:
    lines = [
        "# Positioning Report",
        "",
        f"Repo: `{report['repo']}`",
        f"Project type: `{report['project_type']}`",
        "",
        "## What is this project?",
        "",
        report["what_is_this"],
        "",
        "## Who is it for?",
        "",
        report["who_is_it_for"],
        "",
        "## What problem does it solve?",
        "",
        report["problem_it_solves"],
        "",
        "## Strongest README angle",
        "",
        report["strongest_readme_angle"],
        "",
        "## What is unclear?",
        "",
    ]

    lines.extend(f"- {item}" for item in report["what_is_unclear"])
    lines.extend(
        [
            "",
            "## One-sentence positioning",
            "",
            report["one_sentence"],
            "",
            "## Evidence",
            "",
            f"- README exists: `{str(report['evidence']['readme_exists']).lower()}`",
            f"- Top keywords: `{', '.join(report['evidence']['top_keywords']) or 'none'}`",
            f"- Entry points: `{', '.join(report['evidence']['entrypoints']) or 'none'}`",
            f"- Tooling: `{', '.join(report['evidence']['tooling']) or 'none'}`",
        ]
    )

    return "\n".join(lines)


def format_positioning_report(report: dict[str, Any], output_format: str = "text") -> str:
    if output_format not in VALID_FORMATS:
        raise ValueError("Unsupported positioning format. Use: text or json.")
    if output_format == "json":
        return json.dumps(report, indent=2, ensure_ascii=False)
    return format_positioning_text(report)
