from pathlib import Path
import fnmatch
import re
import subprocess
import sys

from repo_signal import __version__
from repo_signal.actions_init import init_actions_workflow
from repo_signal.portfolio_check import check_portfolio
from repo_signal.analyze import analyze_repo
from repo_signal.ask import main as ask_main
from repo_signal.doctor import doctor_repo
from repo_signal.export_codex import main as export_codex_main
from repo_signal.inspect import inspect_repo
from repo_signal.positioning import build_positioning_report, format_positioning_report
from repo_signal.publish_checklist import (
    VALID_FORMATS,
    build_publish_checklist,
    format_fix_plan,
    format_publish_checklist,
)
from repo_signal.repoaware.__main__ import main as repoaware_main
from repo_signal.readme_score import format_readme_score, score_readme
from repo_signal.semantic import main as semantic_main
from repo_signal.semantic_upload import main as semantic_upload_main
from repo_signal.skill import main as skill_main
from repo_signal.wiki_export import export_wiki_pages
from repo_signal.report import build_report, format_report
from repo_signal.suggest import VALID_FORMATS as SUGGEST_FORMATS, build_suggestions, format_suggestions
from repo_signal.export_packs import main as export_packs_main


HELP_TEXT = """repo-signal

AI-assisted repo analysis for turning rough prototypes into clear, documented, publishable GitHub projects.

Usage:
  repo-signal actions init [path] [--fail-under score] [--force]
  repo-signal analyze [path]
  repo-signal ask [--mode mode] "question"
  repo-signal demo [--generate] [path] [--output path] [--force]
  repo-signal doctor [path] [--format markdown|json] [--json]
  repo-signal inspect [path] [--json|--format text|json]
  repo-signal positioning [path] [--json|--format text|json]
  repo-signal scan
  repo-signal skill new <name> [--description text]
  repo-signal readme
  repo-signal readme-score [path]
  repo-signal publish-checklist [path] [--format text|markdown|json] [--fail-under score] [--fix-plan]
  repo-signal repoaware [--mode mode] [--format format] "question"
  repo-signal semantic [--limit n] [--use-chroma] "query"
  repo-signal semantic-upload [--dry-run] [--vector-store-id id]
  repo-signal export-codex [--local] <skill>
  repo-signal hygiene
  repo-signal wiki [path]
  repo-signal wiki plan [path]
  repo-signal wiki export [path] [--output path]
  repo-signal export [path] [--output DIR] [--all | --symbol-index | --callgraph | --repo-summary | --risk-map]
  repo-signal report [path] [--format text|markdown|json]
  repo-signal suggest [path] [--format text|markdown|json]
  repo-signal roadmap
  repo-signal --help
  repo-signal --version

Commands:
  actions init
             Create a GitHub Actions publish-checklist workflow
  analyze   Summarize repo type, stack, health, structure, tooling, and focus areas
  ask       Ask an AI provider using ranked RepoAware context
  demo      Print or generate a short repo-signal demo flow
  doctor    Diagnose repo health, release maturity, docs quality, AI readiness, and skills
  inspect   Show fast repo status, detected signals, issues, next commit, or inspect.v1 JSON
  positioning
             Analyze README/project positioning and produce a positioning report
  scan       Scan repo structure and basic project signals
  skill      Create repo-local Codex skills
  readme     Analyze README clarity and missing sections
  readme-score
             Score README quality with a 100-point checklist
  publish-checklist
             Check public-facing docs, demo, release, and GitHub Pages signals
  repoaware  Build high-signal repo context for AI-assisted code questions
  semantic   Search smart symbol chunks for semantic repository recall
  semantic-upload
             Upload symbol memory to a scoped OpenAI vector store
  export-codex
             Export repo-local skills into Codex skill storage
  export     Generate symbolic intelligence packs (symbol_index, callgraph, repo_summary, risk_map)
  hygiene    Check junk files, .gitignore, large files, and Git status
  report     Unified report — inspect + publish-checklist in text, markdown or JSON
  suggest    Safe patch suggestions — what to improve, no mutations
  wiki       Generate suggested GitHub Wiki structure, Home draft, or plan
  roadmap    Generate a practical roadmap based on repo state

Examples:
  repo-signal actions init
  repo-signal analyze
  repo-signal inspect
  repo-signal positioning .
  repo-signal positioning . --json
  repo-signal doctor
  repo-signal demo
  repo-signal demo --generate
  repo-signal ask --dry-run "how does routing work"
  repo-signal scan
  repo-signal skill new repo-aware
  repo-signal readme
  repo-signal readme-score .
  repo-signal publish-checklist .
  repo-signal publish-checklist . --format json
  repo-signal publish-checklist . --fail-under 14
  repo-signal repoaware --mode debug "how does routing work"
  repo-signal semantic "routing system"
  repo-signal semantic-upload --dry-run
  repo-signal export-codex repo-product-auditor
  repo-signal hygiene
  repo-signal wiki
  repo-signal wiki plan .
  repo-signal wiki export . --output docs/wiki-export
  repo-signal suggest .
  repo-signal suggest . --format markdown
  repo-signal suggest . --format json
  repo-signal roadmap

Run from any repository root.
"""


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


HYGIENE_IGNORE_RULES = [
    ".DS_Store",
    "__pycache__/",
    "*.pyc",
    ".venv/",
    ".env",
    "node_modules/",
]


JUNK_NAMES = {
    ".DS_Store",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    ".venv",
    "venv",
}


JUNK_PATTERNS = [
    "*.pyc",
    "*.pyo",
    "*.swp",
    "*.tmp",
    "*.log",
]


SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
}


LARGE_FILE_LIMIT_MB = 5


WIKI_TARGET_PAGES = [
    "Home.md",
    "Getting-Started.md",
    "Command-Reference.md",
    "Architecture.md",
    "Roadmap.md",
    "Release-Flow.md",
    "Skills.md",
    "Troubleshooting.md",
]


def exists(path: Path, target: str) -> bool:
    return (path / target).exists()


def read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(errors="ignore")


def run_git(repo: Path, args: list[str]) -> tuple[int, str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        return result.returncode, result.stdout.strip()
    except FileNotFoundError:
        return 1, ""


def is_git_repo(repo: Path) -> bool:
    code, output = run_git(repo, ["rev-parse", "--is-inside-work-tree"])
    return code == 0 and output == "true"


def git_tracked_files(repo: Path) -> set[str]:
    if not is_git_repo(repo):
        return set()

    code, output = run_git(repo, ["ls-files"])
    if code != 0 or not output:
        return set()

    return set(output.splitlines())


def git_status(repo: Path) -> list[str]:
    if not is_git_repo(repo):
        return []

    code, output = run_git(repo, ["status", "--porcelain"])
    if code != 0 or not output:
        return []

    return output.splitlines()


def read_gitignore(repo: Path) -> str:
    path = repo / ".gitignore"
    if not path.exists():
        return ""

    return read_text_safe(path)


def gitignore_has_rule(gitignore_text: str, rule: str) -> bool:
    lines = [line.strip() for line in gitignore_text.splitlines()]
    return rule in lines


def iter_files(repo: Path):
    for path in repo.rglob("*"):
        try:
            rel_parts = path.relative_to(repo).parts
        except ValueError:
            continue

        if any(part in SKIP_DIRS for part in rel_parts):
            continue

        yield path


def find_junk(repo: Path) -> list[Path]:
    found = []

    for path in iter_files(repo):
        name = path.name

        if name in JUNK_NAMES:
            found.append(path)
            continue

        if any(fnmatch.fnmatch(name, pattern) for pattern in JUNK_PATTERNS):
            found.append(path)

    return sorted(found)


def find_large_files(repo: Path, limit_mb: int = LARGE_FILE_LIMIT_MB) -> list[tuple[Path, float]]:
    found = []
    limit_bytes = limit_mb * 1024 * 1024

    for path in iter_files(repo):
        if not path.is_file():
            continue

        try:
            size = path.stat().st_size
        except OSError:
            continue

        if size >= limit_bytes:
            found.append((path, size / 1024 / 1024))

    return sorted(found, key=lambda item: item[1], reverse=True)


def parse_publish_checklist_args(args: list[str]) -> tuple[Path, str, int | None, bool]:
    repo = Path.cwd()
    output_format = "text"
    fail_under = None
    fix_plan = False
    index = 0

    while index < len(args):
        arg = args[index]

        if arg == "--format":
            if index + 1 >= len(args):
                print("Missing value for --format")
                raise SystemExit(2)
            output_format = args[index + 1]
            index += 2
            continue

        if arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
            index += 1
            continue

        if arg == "--fail-under":
            if index + 1 >= len(args):
                print("Missing value for --fail-under")
                raise SystemExit(2)
            try:
                fail_under = int(args[index + 1])
            except ValueError:
                print(f"Invalid publish-checklist --fail-under value: {args[index + 1]}")
                raise SystemExit(2)
            index += 2
            continue

        if arg.startswith("--fail-under="):
            raw_value = arg.split("=", 1)[1]
            try:
                fail_under = int(raw_value)
            except ValueError:
                print(f"Invalid publish-checklist --fail-under value: {raw_value}")
                raise SystemExit(2)
            index += 1
            continue

        if arg == "--fix-plan":
            fix_plan = True
            index += 1
            continue

        if arg.startswith("-"):
            print(f"Unknown publish-checklist option: {arg}")
            raise SystemExit(2)

        repo = Path(arg).resolve()
        index += 1

    if output_format not in VALID_FORMATS:
        formats = ", ".join(sorted(VALID_FORMATS))
        print(f"Unknown publish-checklist format: {output_format}")
        print(f"Available formats: {formats}")
        raise SystemExit(2)

    return repo, output_format, fail_under, fix_plan


def parse_positioning_args(args: list[str]) -> tuple[Path, str]:
    repo = Path.cwd()
    output_format = "text"
    path_seen = False

    index = 0
    while index < len(args):
        arg = args[index]

        if arg in {"--json"}:
            output_format = "json"
            index += 1
            continue

        if arg == "--format":
            if index + 1 >= len(args):
                print("Missing value for --format")
                raise SystemExit(2)
            output_format = args[index + 1]
            index += 2
            continue

        if arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
            index += 1
            continue

        if arg.startswith("-"):
            print(f"Unknown positioning option: {arg}")
            raise SystemExit(2)

        if path_seen:
            print(f"Unexpected positioning argument: {arg}")
            raise SystemExit(2)

        repo = Path(arg).expanduser().resolve()
        path_seen = True
        index += 1

    if output_format not in {"text", "json"}:
        print("Available formats: text, json")
        raise SystemExit(2)

    return repo, output_format


def parse_actions_init_args(args: list[str]) -> tuple[Path, int, bool]:
    if not args or args[0] != "init":
        print("Usage: repo-signal actions init [path] [--fail-under score] [--force]")
        raise SystemExit(2)

    repo = Path.cwd()
    fail_under = 14
    force = False
    rest = args[1:]

    if rest and not rest[0].startswith("-"):
        repo = Path(rest[0]).resolve()
        rest = rest[1:]

    index = 0
    while index < len(rest):
        arg = rest[index]

        if arg == "--force":
            force = True
            index += 1
            continue

        if arg == "--fail-under":
            if index + 1 >= len(rest):
                print("Missing value for --fail-under")
                raise SystemExit(2)
            try:
                fail_under = int(rest[index + 1])
            except ValueError:
                print(f"Invalid actions init --fail-under value: {rest[index + 1]}")
                raise SystemExit(2)
            index += 2
            continue

        if arg.startswith("--fail-under="):
            raw_value = arg.split("=", 1)[1]
            try:
                fail_under = int(raw_value)
            except ValueError:
                print(f"Invalid actions init --fail-under value: {raw_value}")
                raise SystemExit(2)
            index += 1
            continue

        print(f"Unknown actions init option: {arg}")
        raise SystemExit(2)

    return repo, fail_under, force


def parse_wiki_args(args: list[str]) -> tuple[str, Path, str]:
    if not args:
        return "draft", Path.cwd(), ""

    if args[0] == "plan":
        repo = Path(args[1]).resolve() if len(args) > 1 else Path.cwd()
        return "plan", repo, ""

    if args[0] == "export":
        repo = Path.cwd()
        output = "docs/wiki-export"
        rest = args[1:]

        if rest and not rest[0].startswith("-"):
            repo = Path(rest[0]).resolve()
            rest = rest[1:]

        index = 0
        while index < len(rest):
            arg = rest[index]

            if arg == "--output":
                if index + 1 >= len(rest):
                    print("Missing value for --output")
                    raise SystemExit(2)
                output = rest[index + 1]
                index += 2
                continue

            if arg.startswith("--output="):
                output = arg.split("=", 1)[1]
                index += 1
                continue

            print(f"Unknown wiki export option: {arg}")
            raise SystemExit(2)

        return "export", repo, output

    repo = Path(args[0]).resolve()
    return "draft", repo, ""


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


def analyze_hygiene(repo: Path) -> str:
    lines = []
    lines.append("# Hygiene Signal Report")
    lines.append("")
    lines.append(f"Repo: `{repo.name}`")
    lines.append("")

    git_repo = is_git_repo(repo)
    tracked = git_tracked_files(repo)
    status_lines = git_status(repo)
    gitignore_text = read_gitignore(repo)

    junk = find_junk(repo)
    large_files = find_large_files(repo)

    tracked_junk = [
        item for item in tracked
        if item.endswith(".DS_Store")
        or "__pycache__" in item
        or item.endswith(".pyc")
        or item.startswith(".venv/")
        or item.startswith("node_modules/")
    ]

    missing_ignore_rules = [
        rule for rule in HYGIENE_IGNORE_RULES
        if not gitignore_has_rule(gitignore_text, rule)
    ]

    issue_count = 0

    lines.append("## Summary")
    lines.append("")

    if git_repo:
        lines.append("- [OK] Git repository detected")
    else:
        lines.append("- [WARN] This folder is not a Git repository")
        issue_count += 1

    if gitignore_text:
        lines.append("- [OK] `.gitignore` exists")
    else:
        lines.append("- [HIGH] `.gitignore` is missing")
        issue_count += 1

    if not junk:
        lines.append("- [OK] No obvious junk files found")
    else:
        lines.append(f"- [WARN] Obvious junk files/folders found: `{len(junk)}`")
        issue_count += 1

    if not tracked_junk:
        lines.append("- [OK] No tracked junk files detected")
    else:
        lines.append(f"- [HIGH] Tracked junk files detected: `{len(tracked_junk)}`")
        issue_count += 1

    if not large_files:
        lines.append(f"- [OK] No files over `{LARGE_FILE_LIMIT_MB} MB` found")
    else:
        lines.append(f"- [WARN] Large files found: `{len(large_files)}`")
        issue_count += 1

    if not status_lines:
        lines.append("- [OK] Working tree appears clean")
    else:
        lines.append(f"- [MED] Working tree has changes: `{len(status_lines)}`")
        issue_count += 1

    lines.append("")
    lines.append("## .gitignore check")
    lines.append("")

    if not missing_ignore_rules:
        lines.append("- [OK] Common ignore rules are present")
    else:
        for rule in missing_ignore_rules:
            lines.append(f"- [MISSING] `{rule}`")

    lines.append("")
    lines.append("## Junk files")
    lines.append("")

    if not junk:
        lines.append("- [OK] No junk files found")
    else:
        for item in junk[:30]:
            lines.append(f"- [WARN] `{item.relative_to(repo)}`")
        if len(junk) > 30:
            lines.append(f"- [INFO] Additional junk entries hidden: `{len(junk) - 30}`")

    lines.append("")
    lines.append("## Tracked junk")
    lines.append("")

    if not tracked_junk:
        lines.append("- [OK] No tracked junk files")
    else:
        for junk_name in tracked_junk[:30]:
            lines.append(f"- [HIGH] `{junk_name}`")
        if len(tracked_junk) > 30:
            lines.append(f"- [INFO] Additional tracked junk entries hidden: `{len(tracked_junk) - 30}`")

    lines.append("")
    lines.append("## Large files")
    lines.append("")

    if not large_files:
        lines.append(f"- [OK] No files over `{LARGE_FILE_LIMIT_MB} MB`")
    else:
        for path, size_mb in large_files[:20]:
            lines.append(f"- [WARN] `{path.relative_to(repo)}` — `{size_mb:.1f} MB`")
        if len(large_files) > 20:
            lines.append(f"- [INFO] Additional large files hidden: `{len(large_files) - 20}`")

    lines.append("")
    lines.append("## Git status")
    lines.append("")

    if not git_repo:
        lines.append("- [WARN] Not a Git repository")
    elif not status_lines:
        lines.append("- [OK] Working tree clean")
    else:
        for line in status_lines[:30]:
            lines.append(f"- `{line}`")
        if len(status_lines) > 30:
            lines.append(f"- [INFO] Additional status lines hidden: `{len(status_lines) - 30}`")

    lines.append("")
    lines.append("## Suggested next actions")
    lines.append("")

    actions = []

    if not gitignore_text:
        actions.append("Create `.gitignore` with common local/system ignores")

    if missing_ignore_rules:
        actions.append("Add missing `.gitignore` rules")

    if tracked_junk:
        actions.append("Remove tracked junk files with `git rm --cached`")

    if junk:
        actions.append("Delete local junk files if they are not needed")

    if large_files:
        actions.append("Review large files and move heavy assets out of the repo if needed")

    if status_lines:
        actions.append("Review uncommitted changes with `git status --short`")

    if not actions:
        actions.append("No immediate hygiene action needed")

    for index, action in enumerate(actions, start=1):
        lines.append(f"{index}. {action}")

    lines.append("")
    lines.append("## Safe cleanup examples")
    lines.append("")
    lines.append("```bash")
    lines.append("# Remove tracked .DS_Store files but keep local files")
    lines.append('find . -name ".DS_Store" -print -exec git rm --cached {} \\;')
    lines.append("")
    lines.append("# Add common ignore rules")
    lines.append('grep -qxF ".DS_Store" .gitignore || echo ".DS_Store" >> .gitignore')
    lines.append('grep -qxF "__pycache__/" .gitignore || echo "__pycache__/" >> .gitignore')
    lines.append('grep -qxF "*.pyc" .gitignore || echo "*.pyc" >> .gitignore')
    lines.append('grep -qxF ".venv/" .gitignore || echo ".venv/" >> .gitignore')
    lines.append("```")

    return "\n".join(lines)



def repo_has_any(repo: Path, paths: list[str]) -> bool:
    return any((repo / path).exists() for path in paths)


def readme_title_and_summary(repo: Path) -> tuple[str, str]:
    readme = repo / "README.md"

    if not readme.exists():
        return repo.name, "No README summary found."

    text = read_text_safe(readme)
    title = repo.name
    summary = "No README summary found."

    for line in text.splitlines():
        clean = line.strip()
        if clean.startswith("# "):
            title = clean.removeprefix("# ").strip()
            break

    for line in text.splitlines():
        clean = line.strip()
        if not clean:
            continue
        if clean.startswith("#"):
            continue
        if clean.startswith("!"):
            continue
        if clean.startswith("[!"):
            continue
        if len(clean) > 20:
            summary = clean
            break

    return title, summary


def detect_repo_track(repo: Path) -> str:
    if repo_has_any(repo, ["repo_signal", "pyproject.toml"]) and repo_has_any(repo, ["bin/repo-signal"]):
        return "Python CLI / repo intelligence"

    if repo_has_any(repo, ["docs/index.html"]) and repo_has_any(repo, ["helper", "helpers"]):
        return "GitHub Pages dashboard with local helper agents"

    if repo_has_any(repo, ["docs/index.html"]):
        return "GitHub Pages / static web project"

    if repo_has_any(repo, ["bin", "tools", "scripts"]):
        return "Command-line tools / automation"

    if repo_has_any(repo, ["package.json"]):
        return "JavaScript / web application"

    if repo_has_any(repo, ["requirements.txt"]):
        return "Python project"

    return "General repository"


def recommended_wiki_pages(repo: Path) -> list[tuple[str, str]]:
    pages = [
        ("Home", "Project overview, purpose, key links, and current status"),
        ("Usage", "How to run, test, and operate the project"),
        ("Roadmap", "Near-term improvements and long-term direction"),
    ]

    if repo_has_any(repo, ["docs/index.html", "docs"]):
        pages.append(("GitHub Pages", "Live site structure, routing, deployment, and demo notes"))

    if repo_has_any(repo, ["bin", "tools", "scripts"]):
        pages.append(("Command Surface", "CLI commands, local workflows, and script entry points"))

    if repo_has_any(repo, ["repo_signal", "src", "helper", "helpers"]):
        pages.append(("Architecture", "Internal structure, modules, data flow, and design decisions"))

    if repo_has_any(repo, ["README.md"]):
        pages.append(("Documentation Model", "README, examples, wiki, and public positioning strategy"))

    pages.append(("Maintenance", "Cleanup, release, repo hygiene, and contribution notes"))

    return pages


def generate_home_draft(repo: Path) -> str:
    title, summary = readme_title_and_summary(repo)
    track = detect_repo_track(repo)

    lines = []
    lines.append(f"# {title} Wiki")
    lines.append("")
    lines.append(summary)
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(f"`{repo.name}` is part of a broader system of small, practical tools that make technical work clearer, more structured, and easier to repeat.")
    lines.append("")
    lines.append("This wiki explains:")
    lines.append("")
    lines.append("- what the project does")
    lines.append("- why it exists")
    lines.append("- how it is structured")
    lines.append("- how to run it")
    lines.append("- what should be improved next")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Project track")
    lines.append("")
    lines.append(f"```text\n{track}\n```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Main pages")
    lines.append("")

    for page, purpose in recommended_wiki_pages(repo):
        lines.append(f"| {page} | {purpose} |")

    lines.insert(lines.index("## Main pages") + 2, "| Page | Purpose |")
    lines.insert(lines.index("## Main pages") + 3, "|---|---|")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Current status")
    lines.append("")
    lines.append("```text")
    lines.append("early working system")
    lines.append("local-first")
    lines.append("documentation-driven")
    lines.append("safe to iterate")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## North star")
    lines.append("")
    lines.append("```text")
    lines.append("turn unclear project state into clear next actions")
    lines.append("```")

    return "\n".join(lines)


def generate_wiki_plan(repo: Path) -> str:
    title, summary = readme_title_and_summary(repo)
    track = detect_repo_track(repo)
    pages = recommended_wiki_pages(repo)

    lines = []
    lines.append("# Wiki Signal Report")
    lines.append("")
    lines.append(f"Repo: `{repo.name}`")
    lines.append(f"Detected track: `{track}`")
    lines.append("")
    lines.append("## README signal")
    lines.append("")
    lines.append(f"- Title: `{title}`")
    lines.append(f"- Summary: {summary}")
    lines.append("")
    lines.append("## Recommended wiki pages")
    lines.append("")
    lines.append("| Page | Purpose |")
    lines.append("|---|---|")

    for page, purpose in pages:
        lines.append(f"| {page} | {purpose} |")

    lines.append("")
    lines.append("## Suggested creation order")
    lines.append("")

    for index, (page, _) in enumerate(pages, start=1):
        lines.append(f"{index}. {page}")

    lines.append("")
    lines.append("## Wiki Home draft")
    lines.append("")
    lines.append("Copy this into the GitHub Wiki Home page:")
    lines.append("")
    lines.append("```markdown")
    lines.append(generate_home_draft(repo))
    lines.append("```")
    lines.append("")
    lines.append("## Suggested edit message")
    lines.append("")
    lines.append("```text")
    lines.append("Create wiki home page")
    lines.append("```")

    return "\n".join(lines)


def wiki_page_locations(repo: Path) -> list[Path]:
    return [
        repo / "docs" / "wiki-export",
        Path.home() / f"{repo.name}.wiki",
    ]


def existing_wiki_pages(repo: Path) -> set[str]:
    found = set()

    for location in wiki_page_locations(repo):
        if not location.exists():
            continue

        for page in location.glob("*.md"):
            found.add(page.name)

    return found


def generate_wiki_plan_report(repo: Path) -> str:
    track = detect_repo_track(repo)
    existing = existing_wiki_pages(repo)
    missing = [page for page in WIKI_TARGET_PAGES if page not in existing]

    if missing:
        next_action = f"Create or refresh: {missing[0]}"
    else:
        next_action = "Create or refresh: Command-Reference.md"

    lines = [
        "WIKI PLAN",
        "=========",
        f"Repo: {repo.name}",
        f"Detected project type: {track}",
        "",
        "Recommended pages",
        "-----------------",
    ]

    for page in WIKI_TARGET_PAGES:
        lines.append(f"- {page}")

    lines.extend(["", "Existing pages", "--------------"])

    if existing:
        for page in sorted(existing):
            lines.append(f"- {page}")
    else:
        lines.append("- none detected")

    lines.extend(["", "Missing pages", "-------------"])

    if missing:
        for page in missing:
            lines.append(f"- {page}")
    else:
        lines.append("- none")

    lines.extend(["", "Next action", "-----------", next_action])

    return "\n".join(lines)


def roadmap_has(repo: Path, target: str) -> bool:
    return (repo / target).exists()


def roadmap_readme_has(repo: Path, phrase: str) -> bool:
    readme = repo / "README.md"

    if not readme.exists():
        return False

    return phrase.lower() in read_text_safe(readme).lower()


def roadmap_detect_track(repo: Path) -> str:
    try:
        return detect_repo_track(repo)
    except NameError:
        pass

    if roadmap_has(repo, "docs/index.html"):
        return "GitHub Pages / static web project"

    if roadmap_has(repo, "bin") or roadmap_has(repo, "tools") or roadmap_has(repo, "scripts"):
        return "Command-line tools / automation"

    if roadmap_has(repo, "repo_signal"):
        return "Python CLI"

    if roadmap_has(repo, "package.json"):
        return "JavaScript / web application"

    if roadmap_has(repo, "requirements.txt") or roadmap_has(repo, "pyproject.toml"):
        return "Python project"

    return "General repository"


def generate_roadmap_plan(repo: Path) -> str:
    track = roadmap_detect_track(repo)

    has_readme = roadmap_has(repo, "README.md")
    has_license = roadmap_has(repo, "LICENSE")
    has_gitignore = roadmap_has(repo, ".gitignore")
    has_docs = roadmap_has(repo, "docs")
    has_docs_index = roadmap_has(repo, "docs/index.html")
    has_examples = roadmap_has(repo, "examples")
    has_bin = roadmap_has(repo, "bin")
    has_cli_package = roadmap_has(repo, "repo_signal")
    has_tests = roadmap_has(repo, "tests")
    has_pyproject = roadmap_has(repo, "pyproject.toml")
    has_requirements = roadmap_has(repo, "requirements.txt")
    has_roadmap_text = roadmap_readme_has(repo, "roadmap")

    status_lines = git_status(repo) if is_git_repo(repo) else []

    lines = []
    lines.append("# Roadmap Signal Report")
    lines.append("")
    lines.append(f"Repo: `{repo.name}`")
    lines.append(f"Detected track: `{track}`")
    lines.append("")

    lines.append("## Current signals")
    lines.append("")
    lines.append(f"- README: `{'yes' if has_readme else 'no'}`")
    lines.append(f"- LICENSE: `{'yes' if has_license else 'no'}`")
    lines.append(f"- .gitignore: `{'yes' if has_gitignore else 'no'}`")
    lines.append(f"- docs/: `{'yes' if has_docs else 'no'}`")
    lines.append(f"- docs/index.html: `{'yes' if has_docs_index else 'no'}`")
    lines.append(f"- examples/: `{'yes' if has_examples else 'no'}`")
    lines.append(f"- bin/: `{'yes' if has_bin else 'no'}`")
    lines.append(f"- Python package folder: `{'yes' if has_cli_package else 'no'}`")
    lines.append(f"- tests/: `{'yes' if has_tests else 'no'}`")
    lines.append(f"- pyproject.toml: `{'yes' if has_pyproject else 'no'}`")
    lines.append(f"- requirements.txt: `{'yes' if has_requirements else 'no'}`")
    lines.append(f"- README roadmap: `{'yes' if has_roadmap_text else 'no'}`")
    lines.append(f"- Working tree changes: `{len(status_lines)}`")
    lines.append("")

    lines.append("## Immediate next actions")
    lines.append("")

    actions = []

    if status_lines:
        actions.append("Review and commit or discard current working tree changes")

    if not has_license:
        actions.append("Add a LICENSE file")

    if not has_gitignore:
        actions.append("Add a .gitignore with common local/system ignores")

    if not has_docs_index:
        actions.append("Add a docs/index.html landing page or clarify that no live demo is needed")

    if not has_examples:
        actions.append("Add example reports or example usage output")

    if not has_tests:
        actions.append("Add a small tests/ folder for core scanner behavior")

    if not has_pyproject and has_cli_package:
        actions.append("Add pyproject.toml so the CLI can be installed cleanly")

    if not has_roadmap_text:
        actions.append("Add a Roadmap section to README.md")

    if not actions:
        actions.append("No urgent foundation gaps detected; move to feature depth")

    for index, action in enumerate(actions, start=1):
        lines.append(f"{index}. {action}")

    lines.append("")
    lines.append("## Suggested roadmap")
    lines.append("")

    lines.append("### Phase 1 — Stabilize the foundation")
    lines.append("")
    lines.append("- keep CLI commands working from any directory")
    lines.append("- keep README, LICENSE, docs, and examples in sync")
    lines.append("- verify GitHub Pages deployment")
    lines.append("- make output predictable and copy-paste friendly")
    lines.append("")

    lines.append("### Phase 2 — Improve analysis depth")
    lines.append("")
    lines.append("- improve project type detection")
    lines.append("- detect GitHub Pages structure more accurately")
    lines.append("- detect missing screenshots or preview assets")
    lines.append("- detect broken obvious local links")
    lines.append("- detect stale planned commands in README")
    lines.append("")

    lines.append("### Phase 3 — Add installable CLI packaging")
    lines.append("")
    lines.append("- add `pyproject.toml`")
    lines.append("- expose `repo-signal` as a console script")
    lines.append("- support `pipx install .`")
    lines.append("- add version output")
    lines.append("- add basic tests")
    lines.append("")

    lines.append("### Phase 4 — Safe patch mode")
    lines.append("")
    lines.append("- generate safe cleanup commands")
    lines.append("- generate README section patches")
    lines.append("- generate docs/README.md")
    lines.append("- generate wiki drafts")
    lines.append("- never modify files without explicit confirmation")
    lines.append("")

    lines.append("### Phase 5 — AI-assisted handoff")
    lines.append("")
    lines.append("- export structured prompts for deeper analysis")
    lines.append("- generate positioning drafts")
    lines.append("- generate release notes")
    lines.append("- generate GitHub Wiki pages")
    lines.append("- generate LinkedIn/GitHub launch posts")
    lines.append("")

    lines.append("## Recommended next commit")
    lines.append("")

    if has_cli_package and not has_pyproject:
        lines.append("```text")
        lines.append("Add installable CLI packaging")
        lines.append("```")
    elif not has_tests:
        lines.append("```text")
        lines.append("Add tests for repo-signal commands")
        lines.append("```")
    elif not has_examples:
        lines.append("```text")
        lines.append("Add real repo-signal example reports")
        lines.append("```")
    else:
        lines.append("```text")
        lines.append("Improve repo-signal analysis depth")
        lines.append("```")

    lines.append("")
    lines.append("## North star")
    lines.append("")
    lines.append("```text")
    lines.append("turn unclear project state into clear next actions")
    lines.append("```")

    return "\n".join(lines)

def parse_doctor_args(args: list[str]) -> tuple[Path, str]:
    repo = Path.cwd()
    output_format = "markdown"
    index = 0

    while index < len(args):
        arg = args[index]

        if arg == "--json":
            output_format = "json"
            index += 1
            continue

        if arg == "--format":
            if index + 1 >= len(args):
                print("Missing value for --format")
                raise SystemExit(2)
            output_format = args[index + 1]
            index += 2
            continue

        if arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
            index += 1
            continue

        if arg.startswith("-"):
            print(f"Unknown doctor option: {arg}")
            raise SystemExit(2)

        repo = Path(arg).resolve()
        index += 1

    if output_format == "text":
        output_format = "markdown"

    if output_format not in {"markdown", "json"}:
        print(f"Unknown doctor format: {output_format}")
        print("Available formats: markdown, json")
        raise SystemExit(2)

    return repo, output_format


def demo_text() -> str:
    return """# repo-signal demo

Run these commands from a repository root:

```bash
repo-signal analyze
repo-signal inspect
repo-signal doctor
repo-signal doctor --json
repo-signal publish-checklist .
repo-signal repoaware --mode review --format markdown "what should I inspect first"
```

Useful follow-up docs:

- docs/COMMANDS.md
- docs/DOCTOR_SCHEMA.md
- docs/screenshots/README.md
- examples/doctor/doctor.v1.json

Generate local demo reports:

```bash
repo-signal demo --generate
repo-signal demo --generate . --output examples/demo --force
```
"""


def parse_inspect_args(args: list[str]) -> tuple[Path, str]:
    repo = Path.cwd()
    output_format = "text"
    index = 0

    while index < len(args):
        arg = args[index]

        if arg == "--json":
            output_format = "json"
            index += 1
            continue

        if arg == "--format":
            if index + 1 >= len(args):
                print("Missing value for --format")
                raise SystemExit(2)
            output_format = args[index + 1]
            index += 2
            continue

        if arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
            index += 1
            continue

        if arg.startswith("-"):
            print(f"Unknown inspect option: {arg}")
            raise SystemExit(2)

        repo = Path(arg).resolve()
        index += 1

    if output_format not in {"text", "json"}:
        print(f"Unknown inspect format: {output_format}")
        print("Available formats: text, json")
        raise SystemExit(2)

    return repo, output_format


def parse_demo_args(args: list[str]) -> tuple[bool, Path, Path, bool]:
    generate = False
    repo = Path.cwd()
    output = Path("examples/demo")
    force = False
    index = 0

    while index < len(args):
        arg = args[index]

        if arg == "--generate":
            generate = True
            index += 1
            continue

        if arg == "--force":
            force = True
            index += 1
            continue

        if arg == "--output":
            if index + 1 >= len(args):
                print("Missing value for --output")
                raise SystemExit(2)
            output = Path(args[index + 1])
            index += 2
            continue

        if arg.startswith("--output="):
            output = Path(arg.split("=", 1)[1])
            index += 1
            continue

        if arg.startswith("-"):
            print(f"Unknown demo option: {arg}")
            raise SystemExit(2)

        repo = Path(arg).resolve()
        index += 1

    return generate, repo, output, force


def write_demo_file(path: Path, content: str, force: bool) -> bool:
    if path.exists() and not force:
        return False

    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    return True


def generate_demo_reports(repo: Path, output: Path, force: bool = False) -> str:
    output.mkdir(parents=True, exist_ok=True)

    publish_result = build_publish_checklist(str(repo))
    files = {
        "analyze.txt": analyze_repo(str(repo)),
        "inspect.txt": inspect_repo(repo),
        "inspect.v1.json": inspect_repo(repo, output_format="json"),
        "doctor.txt": doctor_repo(repo),
        "doctor.v1.json": doctor_repo(repo, output_format="json"),
        "publish-checklist.txt": format_publish_checklist(publish_result),
        "README.md": f"""# repo-signal Demo Reports

Generated from `{repo}`.

Files:

- `analyze.txt`
- `inspect.txt`
- `inspect.v1.json`
- `doctor.txt`
- `doctor.v1.json`
- `publish-checklist.txt`

Regenerate:

```bash
repo-signal demo --generate {repo} --output {output} --force
```
""",
    }

    written = []
    skipped = []
    for name, content in files.items():
        path = output / name
        if write_demo_file(path, content, force):
            written.append(name)
        else:
            skipped.append(name)

    lines = []
    lines.append("# repo-signal demo generated")
    lines.append("")
    lines.append(f"Repo: `{repo}`")
    lines.append(f"Output: `{output.resolve()}`")
    lines.append("")
    if written:
        lines.append("Written:")
        for name in written:
            lines.append(f"- `{output / name}`")
    if skipped:
        lines.append("")
        lines.append("Skipped existing files:")
        for name in skipped:
            lines.append(f"- `{output / name}`")
        lines.append("")
        lines.append("Run with `--force` to overwrite existing demo reports.")

    return "\n".join(lines)


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else "scan"

    if command in {"--help", "-h", "help"}:
        print(HELP_TEXT)
        return

    if command in {"--version", "-v", "version"}:
        print(f"repo-signal {__version__}")
        return

    if command == "demo":
        generate, demo_repo, output, force = parse_demo_args(sys.argv[2:])
        if generate:
            print(generate_demo_reports(demo_repo, output, force=force))
        else:
            print(demo_text())
        return

    if command == "repoaware":
        repoaware_main(sys.argv[2:])
        return

    if command == "ask":
        ask_main(sys.argv[2:])
        return

    if command == "semantic":
        semantic_main(sys.argv[2:])
        return

    if command == "semantic-upload":
        semantic_upload_main(sys.argv[2:])
        return

    if command == "export-codex":
        export_codex_main(sys.argv[2:])
        return

    if command == "export":
        export_packs_main(sys.argv[2:])
        return

    if command == "skill":
        skill_main(sys.argv[2:])
        return

    if command == "actions":
        repo, fail_under, force = parse_actions_init_args(sys.argv[2:])
        print(init_actions_workflow(str(repo), fail_under=fail_under, force=force))
        return

    if command == "portfolio":
        args = sys.argv[2:]
        if not args or args[0] != "check":
            print("Usage: repo-signal portfolio check [--config path] [--format text|markdown|json]")
            raise SystemExit(2)
        config = "repo-signal.yml"
        output_format = "text"
        i = 1
        while i < len(args):
            if args[i] == "--config" and i + 1 < len(args):
                config = args[i + 1]
                i += 2
            elif args[i].startswith("--config="):
                config = args[i].split("=", 1)[1]
                i += 1
            elif args[i] == "--format" and i + 1 < len(args):
                output_format = args[i + 1]
                i += 2
            elif args[i].startswith("--format="):
                output_format = args[i].split("=", 1)[1]
                i += 1
            else:
                print(f"Unknown portfolio option: {args[i]}")
                raise SystemExit(2)
        try:
            print(check_portfolio(config, output_format=output_format))
        except ValueError as e:
            print(e)
            raise SystemExit(2)
        return

    if command == "publish-checklist":
        repo, output_format, score_threshold, fix_plan = parse_publish_checklist_args(sys.argv[2:])
        result = build_publish_checklist(str(repo))
        if fix_plan:
            print(format_fix_plan(result))
        else:
            print(format_publish_checklist(result, output_format=output_format))
        if score_threshold is not None and result["score"] < score_threshold:
            raise SystemExit(1)
        return

    if command == "positioning":
        repo, output_format = parse_positioning_args(sys.argv[2:])
        result = build_positioning_report(str(repo))
        print(format_positioning_report(result, output_format=output_format))
        return

    if command == "wiki":
        wiki_command, repo, wiki_output = parse_wiki_args(sys.argv[2:])
        if wiki_command == "plan":
            print(generate_wiki_plan_report(repo))
        elif wiki_command == "export":
            print(export_wiki_pages(str(repo), wiki_output))
        else:
            print(generate_wiki_plan(repo))
        return

    if command == "inspect":
        inspect_path, inspect_format = parse_inspect_args(sys.argv[2:])
        print(inspect_repo(inspect_path, output_format=inspect_format))
        return

    repo = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else Path.cwd()

    if command == "scan":
        print(scan_repo(repo))
        return

    if command == "analyze":
        print(analyze_repo(str(repo)))
        return

    if command == "doctor":
        doctor_path, doctor_format = parse_doctor_args(sys.argv[2:])
        print(doctor_repo(doctor_path, output_format=doctor_format))
        return

    if command == "readme":
        print(analyze_readme(repo))
        return

    if command == "readme-score":
        print(format_readme_score(score_readme(str(repo))))
        return

    if command == "hygiene":
        print(analyze_hygiene(repo))
        return

    if command == "suggest":
        args = sys.argv[2:]
        suggest_path = "."
        suggest_format = "text"
        i = 0
        while i < len(args):
            if args[i] == "--format" and i + 1 < len(args):
                suggest_format = args[i + 1]
                i += 2
            elif args[i].startswith("--format="):
                suggest_format = args[i].split("=", 1)[1]
                i += 1
            elif args[i] == "--json":
                suggest_format = "json"
                i += 1
            elif not args[i].startswith("--"):
                suggest_path = args[i]
                i += 1
            else:
                print(f"Unknown suggest option: {args[i]}")
                raise SystemExit(2)
        if suggest_format not in SUGGEST_FORMATS:
            print(f"Unknown suggest format: {suggest_format}")
            print(f"Available formats: {', '.join(sorted(SUGGEST_FORMATS))}")
            raise SystemExit(2)
        try:
            data = build_suggestions(suggest_path)
            print(format_suggestions(data, output_format=suggest_format))
        except ValueError as exc:
            print(exc)
            raise SystemExit(2)
        return

    if command == "roadmap":
        print(generate_roadmap_plan(repo))
        return

    if command == "report":
        args = sys.argv[2:]
        report_path = "."
        report_format = "text"
        i = 0
        while i < len(args):
            if args[i] == "--format" and i + 1 < len(args):
                report_format = args[i + 1]
                i += 2
            elif args[i].startswith("--format="):
                report_format = args[i].split("=", 1)[1]
                i += 1
            elif args[i] == "--json":
                report_format = "json"
                i += 1
            elif not args[i].startswith("--"):
                report_path = args[i]
                i += 1
            else:
                print(f"Unknown report option: {args[i]}")
                raise SystemExit(2)
        try:
            data = build_report(report_path)
            print(format_report(data, output_format=report_format))
        except ValueError as exc:
            print(exc)
            raise SystemExit(2)
        return

    if command == "brief":
        from repo_signal.brief import build_brief, format_brief
        args = sys.argv[2:]
        brief_path = "."
        brief_format = "text"
        i = 0
        while i < len(args):
            if args[i] == "--format" and i + 1 < len(args):
                brief_format = args[i + 1]
                i += 2
            elif args[i].startswith("--format="):
                brief_format = args[i].split("=", 1)[1]
                i += 1
            elif args[i] == "--json":
                brief_format = "json"
                i += 1
            elif not args[i].startswith("--"):
                brief_path = args[i]
                i += 1
            else:
                print(f"Unknown brief option: {args[i]}")
                raise SystemExit(2)
        data = build_brief(brief_path)
        print(format_brief(data, output_format=brief_format))
        return

    if command == "readiness":
        from repo_signal.readiness import build_readiness, format_readiness
        args = sys.argv[2:]
        readiness_path = "."
        readiness_format = "text"
        i = 0
        while i < len(args):
            if args[i] == "--format" and i + 1 < len(args):
                readiness_format = args[i + 1]
                i += 2
            elif args[i].startswith("--format="):
                readiness_format = args[i].split("=", 1)[1]
                i += 1
            elif args[i] == "--json":
                readiness_format = "json"
                i += 1
            elif not args[i].startswith("--"):
                readiness_path = args[i]
                i += 1
            else:
                print(f"Unknown readiness option: {args[i]}")
                raise SystemExit(2)
        data = build_readiness(readiness_path)
        print(format_readiness(data, output_format=readiness_format))
        return

    print(f"Unknown command: {command}")
    print("Available commands: actions, analyze, ask, brief, demo, doctor, inspect, positioning, readiness, scan, skill, readme, readme-score, publish-checklist, repoaware, semantic, semantic-upload, export-codex, hygiene, suggest, wiki, roadmap, --help, --version")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
