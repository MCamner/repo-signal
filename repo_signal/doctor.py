import json
from pathlib import Path
from typing import Any

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


def build_doctor_result_from_repo(repo: Repository, readme_result: dict[str, Any]) -> dict[str, Any]:
    docs_score = int(readme_result["score"])
    health_score, health_evidence = score_repo_health(repo)
    release_score, release_evidence = score_release_maturity(repo)
    ai_score, ai_evidence = score_ai_readiness(repo, docs_score)
    skills = suggested_skills(repo, docs_score, release_score)
    priorities = suggested_priorities(repo, docs_score, health_score, release_score, ai_score)

    return {
        "schema_version": "doctor.v1",
        "repo": {
            "name": repo.name,
            "path": str(repo.path),
            "project_type": repo.project_type,
        },
        "summary": {
            "files_scanned": repo.repo_size_files,
            "languages": repo.languages,
            "git_repo": repo.git.is_repo,
            "git_branch": repo.git.branch,
            "working_tree_changes": repo.git.changed_files,
        },
        "scores": {
            "repo_health": {
                "score": health_score,
                "max_score": 100,
                "status": status_label(health_score),
                "evidence": health_evidence,
            },
            "release_maturity": {
                "score": release_score,
                "max_score": 100,
                "status": status_label(release_score),
                "evidence": release_evidence,
            },
            "docs_quality": {
                "score": docs_score,
                "max_score": int(readme_result.get("max_score", 100)),
                "status": status_label(docs_score),
                "evidence": ["README score checklist"],
            },
            "ai_readiness": {
                "score": ai_score,
                "max_score": 100,
                "status": status_label(ai_score),
                "evidence": ai_evidence,
            },
        },
        "key_signals": {
            "entrypoints": repo.entrypoints[:5],
            "tooling": repo.detected_tooling,
            "symbols": len(repo.symbols),
            "repo_graph_edges": len(repo.graph.edges),
        },
        "readme": {
            "path": str(readme_result.get("path", "")),
            "exists": bool(readme_result.get("exists", False)),
            "missing_checks": readme_result.get("missing", []),
            "present_checks": readme_result.get("present", []),
        },
        "suggested_skills": skills,
        "suggested_priorities": priorities,
        "repoaware_context": {
            "summary": (
                f"This repo is a {repo.project_type}. "
                f"Repo health is {status_label(health_score)} ({health_score}/100). "
                f"Release maturity is {status_label(release_score)} ({release_score}/100). "
                f"Docs quality is {status_label(docs_score)} ({docs_score}/100). "
                f"AI readiness is {status_label(ai_score)} ({ai_score}/100)."
            ),
            "prioritize": priorities[:3],
        },
    }


def build_doctor_result(repo_path: str | Path = ".") -> dict[str, Any]:
    repo = scan_repository(repo_path)
    readme_result = score_readme(str(repo.path))
    return build_doctor_result_from_repo(repo, readme_result)


def format_doctor_report_from_result(result: dict[str, Any]) -> str:
    scores = result["scores"]
    summary = result["summary"]
    key_signals = result["key_signals"]
    readme = result["readme"]

    health = scores["repo_health"]
    release = scores["release_maturity"]
    docs = scores["docs_quality"]
    ai = scores["ai_readiness"]

    lines: list[str] = []
    lines.append("# Repo Signal Doctor Report")
    lines.append("")
    lines.append(f"Repo: `{result['repo']['name']}`")
    lines.append(f"Path: `{result['repo']['path']}`")
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Project type: `{result['repo']['project_type']}`")
    lines.append(f"- Files scanned: `{summary['files_scanned']}`")
    lines.append(
        f"- Languages: `{', '.join(summary['languages'].keys()) if summary['languages'] else 'none detected'}`"
    )
    lines.append(f"- Git repo: `{yes_no(summary['git_repo'])}`")
    lines.append(f"- Working tree changes: `{summary['working_tree_changes']}`")
    lines.append("")

    lines.append("## Scores")
    lines.append("")
    lines.append("| Area | Score | Status | Evidence |")
    lines.append("|---|---:|---|---|")
    lines.append(f"| Repo health | {health['score']}/100 | {health['status']} | {format_evidence(health['evidence'])} |")
    lines.append(f"| Release maturity | {release['score']}/100 | {release['status']} | {format_evidence(release['evidence'])} |")
    lines.append(f"| Docs quality | {docs['score']}/100 | {docs['status']} | README score checklist |")
    lines.append(f"| AI readiness | {ai['score']}/100 | {ai['status']} | {format_evidence(ai['evidence'])} |")
    lines.append("")

    lines.append("## Key Signals")
    lines.append("")
    lines.append(
        f"- Entry points: `{', '.join(key_signals['entrypoints']) if key_signals['entrypoints'] else 'none detected'}`"
    )
    lines.append(
        f"- Tooling: `{', '.join(key_signals['tooling']) if key_signals['tooling'] else 'none detected'}`"
    )
    lines.append(f"- Symbols: `{key_signals['symbols']}`")
    lines.append(f"- Repo graph edges: `{key_signals['repo_graph_edges']}`")
    lines.append(
        f"- README missing checks: `{', '.join(readme['missing_checks']) if readme['missing_checks'] else 'none'}`"
    )
    lines.append("")

    lines.append("## Suggested Skills")
    lines.append("")
    for skill in result["suggested_skills"]:
        lines.append(f"- `{skill}`")
    lines.append("")

    lines.append("## Suggested Priorities")
    lines.append("")
    for index, priority in enumerate(result["suggested_priorities"], start=1):
        lines.append(f"{index}. {priority}")
    lines.append("")

    lines.append("## RepoAware Context")
    lines.append("")
    lines.append("```text")
    lines.append(result["repoaware_context"]["summary"])
    lines.append("Prioritize:")
    for index, priority in enumerate(result["repoaware_context"]["prioritize"], start=1):
        lines.append(f"{index}. {priority}")
    lines.append("```")

    return "\n".join(lines)


def format_doctor_report(repo: Repository, readme_result: dict[str, Any]) -> str:
    return format_doctor_report_from_result(build_doctor_result_from_repo(repo, readme_result))


def format_doctor_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True)


def doctor_repo(repo_path: str | Path = ".", output_format: str = "markdown") -> str:
    normalized = output_format.lower()
    if normalized == "text":
        normalized = "markdown"
    if normalized not in {"markdown", "json"}:
        raise ValueError(f"Unknown doctor format: {output_format}")

    result = build_doctor_result(repo_path)

    if normalized == "json":
        return format_doctor_json(result)

    return format_doctor_report_from_result(result)
