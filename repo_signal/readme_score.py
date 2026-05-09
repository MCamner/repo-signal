from pathlib import Path
import re


README_SCORE_RULES = [
    ("title", "title"),
    ("short_pitch", "short pitch"),
    ("install", "install section"),
    ("usage", "usage section"),
    ("examples", "examples"),
    ("screenshots_demo", "screenshots/demo"),
    ("badges", "badges"),
    ("license", "license"),
    ("roadmap", "roadmap"),
    ("contributing", "contributing"),
]


HEADING_PATTERNS = {
    "install": [
        "install",
        "installation",
        "setup",
        "getting started",
        "quick start",
    ],
    "usage": [
        "usage",
        "quick start",
        "commands",
        "cli",
        "how to run",
    ],
    "examples": [
        "example",
        "examples",
        "example output",
        "demo",
    ],
    "screenshots_demo": [
        "screenshot",
        "screenshots",
        "demo",
        "preview",
        "gallery",
    ],
    "license": [
        "license",
    ],
    "roadmap": [
        "roadmap",
        "planned features",
        "planned",
        "next steps",
    ],
    "contributing": [
        "contributing",
        "contribute",
        "development",
    ],
}


def read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(errors="ignore")


def resolve_readme_path(path: str) -> Path:
    target = Path(path)

    if target.is_dir():
        return target / "README.md"

    return target


def has_heading(text: str, candidates: list[str]) -> bool:
    for candidate in candidates:
        pattern = rf"^#+\s+{re.escape(candidate)}\s*$"
        if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
            return True

    return False


def has_title(text: str) -> bool:
    return bool(re.search(r"^#\s+\S+", text, flags=re.MULTILINE))


def has_short_pitch(text: str) -> bool:
    for line in text.splitlines():
        clean = line.strip()

        if not clean:
            continue
        if clean.startswith("#"):
            continue
        if clean.startswith("---"):
            continue
        if clean.startswith("[!"):
            continue
        if clean.startswith("!["):
            continue
        if re.match(r"^\[!\[.+\]\(.+\)\]\(.+\)$", clean):
            continue

        words = re.findall(r"\b[\w'-]+\b", clean)
        if len(words) >= 5:
            return True

    return False


def has_badges(text: str) -> bool:
    return bool(re.search(r"\[!\[.+?\]\(.+?\)\]\(.+?\)", text)) or "shields.io" in text.lower()


def has_screenshot_or_demo(text: str) -> bool:
    if has_heading(text, HEADING_PATTERNS["screenshots_demo"]):
        return True

    return bool(
        re.search(r"!\[.+?\]\(.+?\.(png|jpe?g|gif|webp)\)", text, flags=re.IGNORECASE)
        or re.search(r"\.(mp4|mov|webm)\b", text, flags=re.IGNORECASE)
    )


def score_readme(path: str) -> dict:
    readme_path = resolve_readme_path(path)
    repo_path = readme_path.parent

    checks = {key: False for key, _ in README_SCORE_RULES}

    if not readme_path.exists():
        return {
            "path": str(readme_path),
            "exists": False,
            "score": 0,
            "max_score": 100,
            "checks": checks,
            "present": [],
            "missing": [key for key, _ in README_SCORE_RULES],
        }

    text = read_text_safe(readme_path)

    checks["title"] = has_title(text)
    checks["short_pitch"] = has_short_pitch(text)
    checks["install"] = has_heading(text, HEADING_PATTERNS["install"])
    checks["usage"] = has_heading(text, HEADING_PATTERNS["usage"])
    checks["examples"] = has_heading(text, HEADING_PATTERNS["examples"])
    checks["screenshots_demo"] = has_screenshot_or_demo(text)
    checks["badges"] = has_badges(text)
    checks["license"] = has_heading(text, HEADING_PATTERNS["license"]) or (repo_path / "LICENSE").exists()
    checks["roadmap"] = has_heading(text, HEADING_PATTERNS["roadmap"])
    checks["contributing"] = has_heading(text, HEADING_PATTERNS["contributing"]) or (repo_path / "CONTRIBUTING.md").exists()

    present = [key for key, value in checks.items() if value]
    missing = [key for key, value in checks.items() if not value]
    score = len(present) * 10

    return {
        "path": str(readme_path),
        "exists": True,
        "score": score,
        "max_score": 100,
        "checks": checks,
        "present": present,
        "missing": missing,
    }


def format_readme_score(result: dict) -> str:
    lines = []
    lines.append("# README Score Report")
    lines.append("")
    lines.append(f"README: `{result['path']}`")
    lines.append(f"README score: {result['score']}/{result['max_score']}")
    lines.append("")

    if not result["exists"]:
        lines.append("Missing: README.md")
        return "\n".join(lines)

    lines.append("## Checks")
    lines.append("")

    labels = dict(README_SCORE_RULES)
    for key, _ in README_SCORE_RULES:
        status = "OK" if result["checks"][key] else "MISSING"
        lines.append(f"- [{status}] {labels[key]}")

    lines.append("")

    if result["missing"]:
        missing = ", ".join(labels[key] for key in result["missing"])
        lines.append(f"Missing: {missing}")
    else:
        lines.append("Missing: none")

    return "\n".join(lines)
