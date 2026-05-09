from pathlib import Path

from repo_signal.core.models import Repository
from repo_signal.core.scanner import scan_repository
from repo_signal.readme_score import score_readme


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def status_label(score: int) -> str:
    if score >= 80:
        return "strong"
    if score >= 60:
        return "usable"
    if score >= 40:
        return "thin"
    return "weak"


def score_release_maturity(repo: Repository) -> tuple[int, list[str]]:
    path = repo.path
    score = 0
    evidence = []

    if repo.git.is_repo:
        score += 20
        evidence.append("Git repository detected")
    if (path / "tests").exists():
        score += 20
        evidence.append("tests/ exists")
    if (path / ".github" / "workflows").exists():
        score += 20
        evidence.append("GitHub Actions workflows detected")
    if (path / "pyproject.toml").exists() or (path / "package.json").exists():
        score += 15
        evidence.append("installable project metadata detected")
    if (path / "LICENSE").exists():
        score += 10
        evidence.append("LICENSE exists")
    if any(path.joinpath(target).exists() for target in ["CHANGELOG.md", "RELEASE.md", "docs"]):
        score += 10
        evidence.append("release/docs support detected")
    if repo.git.is_repo and not repo.git.changed_files:
        score += 5
        evidence.append("working tree clean")

    if not evidence:
        evidence.append("no release signals detected")

    return min(score, 100), evidence


def score_repo_health(repo: Repository) -> tuple[int, list[str]]:
    path = repo.path
    score = 0
    evidence = []

    if (path / "README.md").exists():
        score += 15
        evidence.append("README exists")
    if (path / "LICENSE").exists():
        score += 10
        evidence.append("LICENSE exists")
    if (path / ".gitignore").exists():
        score += 10
        evidence.append(".gitignore exists")
    if repo.entrypoints:
        score += 15
        evidence.append("clear entrypoints detected")
    if repo.detected_tooling:
        score += 15
        evidence.append("tooling detected")
    if repo.git.is_repo:
        score += 10
        evidence.append("Git repository detected")
    if repo.git.is_repo and not repo.git.changed_files:
        score += 10
        evidence.append("working tree clean")
    if repo.repo_size_files > 0:
        score += 5
        evidence.append("files scanned successfully")
    if repo.graph.edges:
        score += 10
        evidence.append("repository graph edges detected")

    if not evidence:
        evidence.append("no health signals detected")

    return min(score, 100), evidence


def score_ai_readiness(repo: Repository, docs_score: int) -> tuple[int, list[str]]:
    path = repo.path
    score = 0
    evidence = []

    if docs_score >= 70:
        score += 25
        evidence.append("README has strong AI-readable structure")
    elif docs_score >= 40:
        score += 15
        evidence.append("README has some useful structure")
    if repo.entrypoints:
        score += 20
        evidence.append("entrypoints can anchor AI context")
    if repo.symbols:
        score += 15
        evidence.append("symbols extracted")
    if repo.graph.edges:
        score += 15
        evidence.append("repo graph available")
    if (path / "docs").exists() or (path / "examples").exists():
        score += 10
        evidence.append("docs/examples available")
    if (path / "skills").exists():
        score += 10
        evidence.append("repo-local skills available")
    if repo.detected_tooling:
        score += 5
        evidence.append("tooling helps classify workflow")

    if not evidence:
        evidence.append("no AI readiness signals detected")

    return min(score, 100), evidence


def suggested_skills(repo: Repository, docs_score: int, release_score: int) -> list[str]:
    skills = ["repo-aware"]

    if docs_score < 80:
        skills.append("repo-product-auditor")
    if repo.entrypoints or "Shell" in repo.languages:
        skills.append("terminal-ui-polisher")
    if release_score < 70:
        skills.append("release-readiness")
    if repo.graph.edges or repo.symbols:
        skills.append("architecture-map")

    return list(dict.fromkeys(skills))


def suggested_priorities(
    repo: Repository,
    docs_score: int,
    health_score: int,
    release_score: int,
    ai_score: int,
) -> list[str]:
    priorities = []

    if docs_score < 70:
        priorities.append("Improve README structure, examples, and contribution guidance")
    if health_score < 70:
        priorities.append("Close foundation gaps in repo structure, tooling, or Git hygiene")
    if release_score < 70:
        priorities.append("Add or verify tests, CI, and release notes before public release")
    if ai_score < 70:
        priorities.append("Add docs/examples that make entrypoints and workflows easier for AI to inspect")
    if repo.git.changed_files:
        priorities.append("Review current working tree changes before using the report as a baseline")
    if not priorities:
        priorities.append("Use this repo as a baseline and improve deeper semantic analysis next")

    return priorities[:5]


def format_evidence(items: list[str]) -> str:
    return "; ".join(items[:4])


def format_doctor_report(repo: Repository, readme_result: dict) -> str:
    docs_score = int(readme_result["score"])
    health_score, health_evidence = score_repo_health(repo)
    release_score, release_evidence = score_release_maturity(repo)
    ai_score, ai_evidence = score_ai_readiness(repo, docs_score)
    skills = suggested_skills(repo, docs_score, release_score)
    priorities = suggested_priorities(repo, docs_score, health_score, release_score, ai_score)

    lines = []
    lines.append("# Repo Signal Doctor Report")
    lines.append("")
    lines.append(f"Repo: `{repo.name}`")
    lines.append(f"Path: `{repo.path}`")
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Project type: `{repo.project_type}`")
    lines.append(f"- Files scanned: `{repo.repo_size_files}`")
    lines.append(f"- Languages: `{', '.join(repo.languages.keys()) if repo.languages else 'none detected'}`")
    lines.append(f"- Git repo: `{yes_no(repo.git.is_repo)}`")
    lines.append(f"- Working tree changes: `{repo.git.changed_files}`")
    lines.append("")

    lines.append("## Scores")
    lines.append("")
    lines.append("| Area | Score | Status | Evidence |")
    lines.append("|---|---:|---|---|")
    lines.append(f"| Repo health | {health_score}/100 | {status_label(health_score)} | {format_evidence(health_evidence)} |")
    lines.append(f"| Release maturity | {release_score}/100 | {status_label(release_score)} | {format_evidence(release_evidence)} |")
    lines.append(f"| Docs quality | {docs_score}/100 | {status_label(docs_score)} | README score checklist |")
    lines.append(f"| AI readiness | {ai_score}/100 | {status_label(ai_score)} | {format_evidence(ai_evidence)} |")
    lines.append("")

    lines.append("## Key Signals")
    lines.append("")
    lines.append(f"- Entry points: `{', '.join(repo.entrypoints[:5]) if repo.entrypoints else 'none detected'}`")
    lines.append(f"- Tooling: `{', '.join(repo.detected_tooling) if repo.detected_tooling else 'none detected'}`")
    lines.append(f"- Symbols: `{len(repo.symbols)}`")
    lines.append(f"- Repo graph edges: `{len(repo.graph.edges)}`")
    lines.append(f"- README missing checks: `{', '.join(readme_result['missing']) if readme_result['missing'] else 'none'}`")
    lines.append("")

    lines.append("## Suggested Skills")
    lines.append("")
    for skill in skills:
        lines.append(f"- `{skill}`")
    lines.append("")

    lines.append("## Suggested Priorities")
    lines.append("")
    for index, priority in enumerate(priorities, start=1):
        lines.append(f"{index}. {priority}")
    lines.append("")

    lines.append("## RepoAware Context")
    lines.append("")
    lines.append("```text")
    lines.append(f"This repo is a {repo.project_type}.")
    lines.append(f"Repo health is {status_label(health_score)} ({health_score}/100).")
    lines.append(f"Release maturity is {status_label(release_score)} ({release_score}/100).")
    lines.append(f"Docs quality is {status_label(docs_score)} ({docs_score}/100).")
    lines.append(f"AI readiness is {status_label(ai_score)} ({ai_score}/100).")
    lines.append("Prioritize:")
    for index, priority in enumerate(priorities[:3], start=1):
        lines.append(f"{index}. {priority}")
    lines.append("```")

    return "\n".join(lines)


def doctor_repo(repo_path: str | Path = ".") -> str:
    repo = scan_repository(repo_path)
    readme_result = score_readme(str(repo.path))
    return format_doctor_report(repo, readme_result)
