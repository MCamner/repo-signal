from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from repo_signal.publish_checklist import build_publish_checklist


@dataclass
class PortfolioRepo:
    name: str
    path: Path
    fail_under: int = 14


@dataclass
class PortfolioResult:
    name: str
    path: str
    score: int
    total: int
    fail_under: int
    status: str
    next_action: str


def load_portfolio_config(config_path: str = "repo-signal.yml") -> list[PortfolioRepo]:
    path = Path(config_path).expanduser().resolve()

    if not path.exists():
        return [PortfolioRepo(name=Path.cwd().name, path=Path.cwd())]

    text = path.read_text(encoding="utf-8")
    repos: list[PortfolioRepo] = []
    current: dict[str, str] = {}
    in_repos = False

    for raw in text.splitlines():
        stripped = raw.strip()

        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("- "):
            if current:
                repos.append(_make_repo(current))
            current = {}
            in_repos = True
            item = stripped[2:].strip()
            if ":" in item:
                k, v = item.split(":", 1)
                current[k.strip()] = v.strip().strip("\"'")
            continue

        if in_repos and ":" in stripped:
            k, v = stripped.split(":", 1)
            current[k.strip()] = v.strip().strip("\"'")

    if current:
        repos.append(_make_repo(current))

    return repos or [PortfolioRepo(name=Path.cwd().name, path=Path.cwd())]


def _make_repo(item: dict[str, str]) -> PortfolioRepo:
    name = item.get("name", "unknown")
    raw_path = item.get("path", ".")
    try:
        fail_under = int(item.get("fail_under", "14"))
    except ValueError:
        fail_under = 14
    return PortfolioRepo(name=name, path=Path(raw_path).expanduser().resolve(), fail_under=fail_under)


def _check_repo(repo: PortfolioRepo) -> PortfolioResult:
    if not repo.path.exists():
        return PortfolioResult(
            name=repo.name,
            path=str(repo.path),
            score=0,
            total=16,
            fail_under=repo.fail_under,
            status="MISSING",
            next_action="Repository path does not exist.",
        )

    result = build_publish_checklist(str(repo.path))
    score = int(result["score"])
    total = int(result["total"])
    next_action = str(result.get("recommended_next_action") or "No action found.")
    status = "OK" if score >= repo.fail_under else "WARN"

    return PortfolioResult(
        name=repo.name,
        path=str(repo.path),
        score=score,
        total=total,
        fail_under=repo.fail_under,
        status=status,
        next_action=next_action,
    )


def _weakest(results: list[PortfolioResult]) -> PortfolioResult:
    return min(results, key=lambda r: r.score / r.total if r.total else 0)


def _render_text(results: list[PortfolioResult]) -> str:
    width = max(len(r.name) for r in results)
    rows = ["PORTFOLIO CHECK", "===============", ""]
    for r in results:
        rows.append(
            f"{r.name:<{width}}  {r.score:>2}/{r.total:<2}  {r.status:<7}  fail-under={r.fail_under}"
        )
    weakest = _weakest(results)
    rows += ["", "Next action", "-----------", f"{weakest.name}: {weakest.next_action}"]
    return "\n".join(rows)


def _render_markdown(results: list[PortfolioResult]) -> str:
    rows = [
        "# Portfolio Check",
        "",
        "| Repo | Score | Status | Fail-under | Next action |",
        "|---|---:|---|---:|---|",
    ]
    for r in results:
        rows.append(
            f"| {r.name} | {r.score}/{r.total} | {r.status} | {r.fail_under} | {r.next_action} |"
        )
    weakest = _weakest(results)
    rows += ["", "## Next action", "", f"Improve **{weakest.name}**: {weakest.next_action}"]
    return "\n".join(rows)


def _render_json(results: list[PortfolioResult]) -> str:
    weakest = _weakest(results)
    data = {
        "object": "portfolio_check",
        "repos": [
            {
                "name": r.name,
                "path": r.path,
                "score": r.score,
                "total": r.total,
                "fail_under": r.fail_under,
                "status": r.status,
                "next_action": r.next_action,
            }
            for r in results
        ],
        "next_action": {"repo": weakest.name, "action": weakest.next_action},
    }
    return json.dumps(data, indent=2)


def check_portfolio(
    config_path: str = "repo-signal.yml",
    output_format: str = "text",
) -> str:
    repos = load_portfolio_config(config_path)
    results = [_check_repo(r) for r in repos]

    if output_format == "json":
        return _render_json(results)
    if output_format == "markdown":
        return _render_markdown(results)
    if output_format != "text":
        raise ValueError(f"Unsupported format: {output_format}")
    return _render_text(results)
