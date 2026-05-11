from pathlib import Path


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


def check_publish_readiness(repo_path: str = ".") -> str:
    root = Path(repo_path).resolve()
    if not root.exists():
        return "\n".join(
            [
                "PUBLISH CHECKLIST",
                "=================",
                f"Repo: {root.name}",
                "Score: 0/0",
                "",
                "Status",
                "------",
                f"- [WARN] Path does not exist: {root}",
                "",
                "Recommended next action",
                "-----------------------",
                "Fix: choose an existing repository path",
            ]
        )

    readme = root / "README.md"
    readme_text = read_text(readme)

    docs = root / "docs"
    issue_templates = root / ".github" / "ISSUE_TEMPLATE"

    groups = [
        (
            "Front door",
            [
                ("README exists", readme.exists(), "add README.md"),
                (
                    "README has quick start",
                    readme_has_any(readme_text, ["quick start", "getting started", "installation", "usage"]),
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
                ("LICENSE exists", has_any(root, ["LICENSE", "LICENSE.md"]), "add a license"),
                ("CHANGELOG exists", has_any(root, ["CHANGELOG.md", "HISTORY.md"]), "add CHANGELOG.md"),
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
                ("issue templates exist", issue_templates.exists(), "add .github/ISSUE_TEMPLATE/"),
                (
                    "roadmap file exists",
                    has_any(root, ["ROADMAP.md"]) or has_any(docs, ["ROADMAP.md", "roadmap.md"]),
                    "add ROADMAP.md or docs/ROADMAP.md",
                ),
            ],
        ),
        (
            "GitHub Pages",
            [
                ("docs folder exists", docs.exists(), "add docs/"),
                ("GitHub Pages landing exists", (docs / "index.html").exists(), "add docs/index.html"),
                ("docs screenshots folder exists", (docs / "screenshots").exists(), "add docs/screenshots/"),
            ],
        ),
    ]

    checks = [
        (label, passed, hint)
        for _, group_checks in groups
        for label, passed, hint in group_checks
    ]
    score = sum(1 for _, passed, _ in checks if passed)
    total = len(checks)

    lines = [
        "PUBLISH CHECKLIST",
        "=================",
        f"Repo: {root.name}",
        f"Score: {score}/{total}",
        "",
    ]

    for title, group_checks in groups:
        lines.append(title)
        lines.append("-" * len(title))
        for label, passed, hint in group_checks:
            lines.append(format_check(label, passed, hint))
        lines.append("")

    lines.append("Recommended next action")
    lines.append("-----------------------")

    missing = [(label, hint) for label, passed, hint in checks if not passed]
    if missing:
        label, hint = missing[0]
        lines.append(f"Fix: {label} ({hint})")
    else:
        lines.append("Repo looks publish-ready from the static checklist.")

    return "\n".join(lines)
