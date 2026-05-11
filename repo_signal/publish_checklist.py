import json
from pathlib import Path


VALID_FORMATS = {"text", "markdown", "json"}


def has_any(path: Path, names: list[str]) -> bool:
    return any((path / name).exists() for name in names)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(errors="ignore")
    except OSError:
        return ""


def readme_has_any(readme_text: str, terms: list[str]) -> bool:
    text = readme_text.lower()
    return any(term in text for term in terms)


def format_check(label: str, passed: bool, hint: str = "") -> str:
    mark = "OK" if passed else "WARN"
    line = f"- [{mark}] {label}"
    if hint and not passed:
        line += f": {hint}"
    return line


def build_publish_checklist(repo_path: str = ".") -> dict:
    root = Path(repo_path).resolve()
    if not root.exists():
        return {
            "repo": root.name,
            "path": str(root),
            "score": 0,
            "total": 0,
            "status": "warn",
            "groups": [
                {
                    "name": "Status",
                    "checks": [
                        {
                            "group": "Status",
                            "name": f"Path does not exist: {root}",
                            "status": "warn",
                            "hint": "choose an existing repository path",
                        }
                    ],
                }
            ],
            "checks": [
                {
                    "group": "Status",
                    "name": f"Path does not exist: {root}",
                    "status": "warn",
                    "hint": "choose an existing repository path",
                }
            ],
            "recommended_next_action": "Fix: choose an existing repository path",
        }

    readme = root / "README.md"
    readme_text = read_text(readme)

    docs = root / "docs"
    issue_templates = root / ".github" / "ISSUE_TEMPLATE"

    raw_groups = [
        (
            "Front door",
            [
                ("README exists", readme.exists(), "add README.md"),
                (
                    "README has quick start",
                    readme_has_any(
                        readme_text,
                        ["quick start", "getting started", "installation", "usage"],
                    ),
                    "add a Quick Start section",
                ),
                (
                    "README links to GitHub Pages",
                    readme_has_any(readme_text, ["github.io", "pages", "live demo"]),
                    "link the live GitHub Pages site",
                ),
                (
                    "README mentions demo",
                    readme_has_any(readme_text, ["demo", "example output", "gallery"]),
                    "add demo or example output",
                ),
                (
                    "README mentions screenshots or gallery",
                    readme_has_any(readme_text, ["screenshot", "gallery"]),
                    "add screenshots or a gallery",
                ),
            ],
        ),
        (
            "Public quality",
            [
                (
                    "LICENSE exists",
                    has_any(root, ["LICENSE", "LICENSE.md"]),
                    "add a license",
                ),
                (
                    "CHANGELOG exists",
                    has_any(root, ["CHANGELOG.md", "HISTORY.md"]),
                    "add CHANGELOG.md",
                ),
                ("VERSION exists", (root / "VERSION").exists(), "add a VERSION file"),
                (".gitignore exists", (root / ".gitignore").exists(), "add .gitignore"),
                (
                    "README mentions roadmap",
                    readme_has_any(readme_text, ["roadmap"]),
                    "link or add a roadmap",
                ),
                (
                    "README mentions safe sharing/security",
                    readme_has_any(readme_text, ["safe", "security"]),
                    "add a safe sharing or security note",
                ),
                (
                    "issue templates exist",
                    issue_templates.exists(),
                    "add .github/ISSUE_TEMPLATE/",
                ),
                (
                    "roadmap file exists",
                    has_any(root, ["ROADMAP.md"])
                    or has_any(docs, ["ROADMAP.md", "roadmap.md"]),
                    "add ROADMAP.md or docs/ROADMAP.md",
                ),
            ],
        ),
        (
            "GitHub Pages",
            [
                ("docs folder exists", docs.exists(), "add docs/"),
                (
                    "GitHub Pages landing exists",
                    (docs / "index.html").exists(),
                    "add docs/index.html",
                ),
                (
                    "docs screenshots folder exists",
                    (docs / "screenshots").exists(),
                    "add docs/screenshots/",
                ),
            ],
        ),
    ]

    groups = []
    checks = []

    for group_name, group_checks in raw_groups:
        formatted_checks = []
        for label, passed, hint in group_checks:
            check = {
                "group": group_name,
                "name": label,
                "status": "ok" if passed else "warn",
                "hint": "" if passed else hint,
            }
            formatted_checks.append(check)
            checks.append(check)
        groups.append({"name": group_name, "checks": formatted_checks})

    score = sum(1 for check in checks if check["status"] == "ok")
    total = len(checks)

    missing = [check for check in checks if check["status"] != "ok"]
    if missing:
        first_missing = missing[0]
        recommended_next_action = f"Fix: {first_missing['name']} ({first_missing['hint']})"
        status = "warn"
    else:
        recommended_next_action = "Repo looks publish-ready from the static checklist."
        status = "pass"

    return {
        "repo": root.name,
        "path": str(root),
        "score": score,
        "total": total,
        "status": status,
        "groups": groups,
        "checks": checks,
        "recommended_next_action": recommended_next_action,
    }


def format_publish_checklist_text(result: dict) -> str:
    lines = [
        "PUBLISH CHECKLIST",
        "=================",
        f"Repo: {result['repo']}",
        f"Score: {result['score']}/{result['total']}",
        "",
    ]

    for group in result["groups"]:
        title = group["name"]
        lines.append(title)
        lines.append("-" * len(title))
        for check in group["checks"]:
            lines.append(
                format_check(
                    check["name"],
                    check["status"] == "ok",
                    check["hint"],
                )
            )
        lines.append("")

    lines.append("Recommended next action")
    lines.append("-----------------------")
    lines.append(result["recommended_next_action"])

    return "\n".join(lines)


def format_publish_checklist_markdown(result: dict) -> str:
    lines = [
        f"# Publish Checklist: {result['repo']}",
        "",
        f"Score: {result['score']}/{result['total']}",
        "",
        f"Status: `{result['status']}`",
        "",
    ]

    for group in result["groups"]:
        lines.append(f"## {group['name']}")
        lines.append("")
        for check in group["checks"]:
            marker = "x" if check["status"] == "ok" else " "
            line = f"- [{marker}] {check['name']}"
            if check["hint"]:
                line += f" - {check['hint']}"
            lines.append(line)
        lines.append("")

    lines.append("## Recommended Next Action")
    lines.append("")
    lines.append(result["recommended_next_action"])

    return "\n".join(lines)


def format_publish_checklist_json(result: dict) -> str:
    output = {
        key: result[key]
        for key in [
            "repo",
            "score",
            "total",
            "status",
            "checks",
            "recommended_next_action",
        ]
    }
    return json.dumps(output, indent=2)


def format_publish_checklist(result: dict, output_format: str = "text") -> str:
    if output_format == "text":
        return format_publish_checklist_text(result)

    if output_format == "markdown":
        return format_publish_checklist_markdown(result)

    if output_format == "json":
        return format_publish_checklist_json(result)

    formats = ", ".join(sorted(VALID_FORMATS))
    raise ValueError(
        f"Unsupported publish checklist format: {output_format}. Use one of: {formats}"
    )


def check_publish_readiness(repo_path: str = ".", output_format: str = "text") -> str:
    return format_publish_checklist(
        build_publish_checklist(repo_path),
        output_format=output_format,
    )
