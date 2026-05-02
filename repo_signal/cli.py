from pathlib import Path
import re
import sys


CHECKS = [
    ("README.md", "README exists"),
    ("LICENSE", "License exists"),
    (".gitignore", ".gitignore exists"),
    ("docs", "docs folder exists"),
]


README_SECTIONS = [
    ("why", ["why this exists", "why"]),
    ("quick_start", ["quick start", "getting started", "installation", "usage"]),
    ("features", ["features", "current features"]),
    ("commands", ["commands", "planned commands", "cli"]),
    ("example", ["example", "example output"]),
    ("structure", ["structure", "project structure", "suggested repo structure"]),
    ("roadmap", ["roadmap"]),
    ("license", ["license"]),
]


def exists(path: Path, target: str) -> bool:
    return (path / target).exists()


def read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(errors="ignore")


def scan_repo(repo: Path) -> str:
    lines = []
    lines.append("# Repo Signal Report")
    lines.append("")
    lines.append(f"Repo: `{repo.name}`")
    lines.append("")

    lines.append("## Checks")
    lines.append("")

    for target, label in CHECKS:
        status = "OK" if exists(repo, target) else "MISSING"
        lines.append(f"- [{status}] {label}: `{target}`")

    ds_store = list(repo.rglob(".DS_Store"))

    lines.append("")
    lines.append("## Hygiene")
    lines.append("")

    if ds_store:
        lines.append(f"- [WARN] Found `.DS_Store` files: {len(ds_store)}")
        for item in ds_store[:10]:
            lines.append(f"  - `{item.relative_to(repo)}`")
    else:
        lines.append("- [OK] No `.DS_Store` files found")

    lines.append("")
    lines.append("## Suggested next actions")
    lines.append("")
    lines.append("1. Improve README clarity")
    lines.append("2. Add or verify GitHub Pages docs")
    lines.append("3. Remove tracked system files")
    lines.append("4. Add project screenshots")
    lines.append("5. Create or update Wiki pages")

    return "\n".join(lines)


def has_heading(text_lower: str, candidates: list[str]) -> bool:
    for candidate in candidates:
        pattern = rf"^#+\s+{re.escape(candidate)}\s*$"
        if re.search(pattern, text_lower, flags=re.MULTILINE):
            return True
    return False


def analyze_readme(repo: Path) -> str:
    readme = repo / "README.md"

    lines = []
    lines.append("# README Signal Report")
    lines.append("")
    lines.append(f"Repo: `{repo.name}`")
    lines.append("")

    if not readme.exists():
        lines.append("## Status")
        lines.append("")
        lines.append("- [HIGH] README.md is missing")
        lines.append("")
        lines.append("## Suggested next actions")
        lines.append("")
        lines.append("1. Create README.md")
        lines.append("2. Add project summary")
        lines.append("3. Add quick start")
        lines.append("4. Add project structure")
        lines.append("5. Add license")
        return "\n".join(lines)

    text = read_text_safe(readme)
    text_lower = text.lower()
    line_count = len(text.splitlines())
    word_count = len(re.findall(r"\b\w+\b", text))
    heading_count = len(re.findall(r"^#+\s+", text, flags=re.MULTILINE))
    code_block_count = text.count("```") // 2
    link_count = len(re.findall(r"https?://", text))
    table_count = text.count("|---")

    missing = []
    present = []

    for key, candidates in README_SECTIONS:
        if has_heading(text_lower, candidates):
            present.append(key)
        else:
            missing.append(key)

    score = 10

    if word_count < 150:
        score -= 3
    elif word_count < 350:
        score -= 1

    if heading_count < 4:
        score -= 2

    if "quick_start" in missing:
        score -= 2

    if "license" in missing:
        score -= 1

    if "roadmap" in missing:
        score -= 1

    if code_block_count == 0:
        score -= 1

    score = max(0, min(10, score))

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- README score: `{score}/10`")
    lines.append(f"- Lines: `{line_count}`")
    lines.append(f"- Words: `{word_count}`")
    lines.append(f"- Headings: `{heading_count}`")
    lines.append(f"- Code blocks: `{code_block_count}`")
    lines.append(f"- Links: `{link_count}`")
    lines.append(f"- Tables: `{table_count}`")
    lines.append("")

    lines.append("## Section check")
    lines.append("")

    for key, _ in README_SECTIONS:
        status = "OK" if key in present else "MISSING"
        label = key.replace("_", " ")
        lines.append(f"- [{status}] {label}")

    lines.append("")

    lines.append("## Findings")
    lines.append("")

    if score >= 8:
        lines.append("- [OK] README is strong enough for a public repo.")
    elif score >= 6:
        lines.append("- [MED] README is usable but needs polish.")
    else:
        lines.append("- [HIGH] README needs clearer structure before the repo is easy to understand.")

    if word_count < 150:
        lines.append("- [HIGH] README is very short.")
    elif word_count < 350:
        lines.append("- [MED] README could explain the project more clearly.")

    if code_block_count == 0:
        lines.append("- [MED] README has no command examples.")

    if link_count == 0:
        lines.append("- [LOW] README has no external or live demo links.")

    if table_count == 0:
        lines.append("- [LOW] README has no tables. A small feature/status table may improve scanning.")

    if missing:
        lines.append(f"- [MED] Missing sections: `{', '.join(missing)}`")

    lines.append("")

    lines.append("## Suggested next actions")
    lines.append("")

    action_number = 1

    if "quick_start" in missing:
        lines.append(f"{action_number}. Add a Quick Start section")
        action_number += 1

    if "example" in missing:
        lines.append(f"{action_number}. Add an example output section")
        action_number += 1

    if "structure" in missing:
        lines.append(f"{action_number}. Add a project structure section")
        action_number += 1

    if "roadmap" in missing:
        lines.append(f"{action_number}. Add a roadmap")
        action_number += 1

    if "license" in missing:
        lines.append(f"{action_number}. Add or link to license information")
        action_number += 1

    if action_number == 1:
        lines.append("1. Add screenshots or a demo GIF")
        lines.append("2. Add a short positioning sentence near the top")
        lines.append("3. Keep README synced with actual CLI commands")

    return "\n".join(lines)


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else "scan"
    repo = Path.cwd()

    if command == "scan":
        print(scan_repo(repo))
        return

    if command == "readme":
        print(analyze_readme(repo))
        return

    print(f"Unknown command: {command}")
    print("Available commands: scan, readme")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
