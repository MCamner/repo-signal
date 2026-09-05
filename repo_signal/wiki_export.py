"""Generate wiki pages that describe the target repository.

Every page is built from files found in the target repo. When a source is
missing the page says so; it never substitutes plausible text. That rule is the
point of this module: an exported page is copied into a public GitHub Wiki, so
an invented claim becomes a published claim.
"""

from pathlib import Path
import re
import subprocess


PAGE_ORDER = [
    "Home.md",
    "Getting-Started.md",
    "Command-Reference.md",
    "Architecture.md",
    "Roadmap.md",
    "Release-Flow.md",
    "Skills.md",
    "Troubleshooting.md",
]

QUICK_START_HEADINGS = ("quick start", "quickstart", "getting started", "install", "usage")
TROUBLESHOOTING_HEADINGS = ("troubleshooting", "common problems", "faq")

ARCHITECTURE_CANDIDATES = ("docs/architecture.md", "ARCHITECTURE.md", "docs/ARCHITECTURE.md")
COMMANDS_CANDIDATES = ("docs/COMMANDS.md", "docs/commands.md", "COMMANDS.md")
ROADMAP_CANDIDATES = ("ROADMAP.md", "docs/ROADMAP.md", "docs/roadmap.md")
TROUBLESHOOTING_CANDIDATES = ("docs/TROUBLESHOOTING.md", "TROUBLESHOOTING.md")
SKILL_GLOBS = ("skills/*.md", ".claude/skills/*/SKILL.md", ".claude/skills/*.md")

CHANGELOG_HEADING = re.compile(r"^##\s*\[?(\d+\.\d+\.\d+)\]?", re.MULTILINE)


def tracked_paths(repo: Path) -> set[str] | None:
    """Repo-relative paths git tracks, or None when this is not a git repo.

    Exported pages are copied into a public wiki, so a gitignored file must not
    become a published one. Repos routinely keep local-only material in
    otherwise ordinary directories (`skills/`, `docs/`), and reading it off the
    filesystem alone would leak it.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "ls-files"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return {line for line in result.stdout.splitlines() if line}


def read_text(repo: Path, rel: str, tracked: set[str] | None = None) -> str | None:
    if tracked is not None and rel not in tracked:
        return None
    path = repo / rel
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def first_existing(
    repo: Path, candidates: tuple[str, ...], tracked: set[str] | None = None
) -> tuple[str, str] | None:
    """Return (relative path, content) for the first candidate that exists."""
    for rel in candidates:
        text = read_text(repo, rel, tracked)
        if text is not None:
            return rel, text
    return None


def sections(markdown: str) -> list[tuple[str, str]]:
    """Split markdown into (heading, body) pairs on `##`-level headings."""
    found: list[tuple[str, str]] = []
    heading = ""
    body: list[str] = []
    for line in markdown.splitlines():
        if line.startswith("## "):
            if heading or body:
                found.append((heading, "\n".join(body).strip()))
            heading = line[3:].strip()
            body = []
        else:
            body.append(line)
    if heading or body:
        found.append((heading, "\n".join(body).strip()))
    return found


def section_matching(markdown: str, keywords: tuple[str, ...]) -> tuple[str, str] | None:
    for heading, body in sections(markdown):
        lowered = heading.lower()
        if any(keyword in lowered for keyword in keywords) and body:
            return heading, body
    return None


def project_name(repo: Path, tracked: set[str] | None = None) -> str:
    """The name the project calls itself, falling back to the directory name."""
    readme = read_text(repo, "README.md", tracked)
    if readme:
        for line in readme.splitlines():
            if line.startswith("# "):
                return line[2:].strip() or repo.name
    return repo.name


def project_summary(repo: Path, tracked: set[str] | None = None) -> str | None:
    """First non-empty prose line under the README title."""
    readme = read_text(repo, "README.md", tracked)
    if not readme:
        return None
    seen_title = False
    for line in readme.splitlines():
        stripped = line.strip()
        if not seen_title:
            seen_title = stripped.startswith("# ")
            continue
        if not stripped or stripped.startswith(("#", "!", "[!", "```", "---", "|")):
            continue
        return stripped
    return None


def missing(what: str, looked_for: tuple[str, ...] | str) -> str:
    looked = looked_for if isinstance(looked_for, str) else ", ".join(f"`{c}`" for c in looked_for)
    return f"No {what} found in this repository.\n\nLooked for: {looked}."


def page_home(repo: Path, tracked: set[str] | None) -> str:
    name = project_name(repo, tracked)
    lines = [f"# {name}", ""]

    summary = project_summary(repo, tracked)
    lines.append(summary if summary else "No project summary found in `README.md`.")

    version = read_text(repo, "VERSION", tracked)
    if version and version.strip():
        lines += ["", f"Current version: `{version.strip()}`"]

    lines += ["", "## Pages", ""]
    lines += [f"- {name[:-3].replace('-', ' ')}" for name in PAGE_ORDER[1:]]
    lines += [
        "",
        "## Source of truth",
        "",
        "This wiki is generated from the repository. When the two disagree, the",
        "repository is correct — regenerate rather than editing pages here.",
    ]
    return "\n".join(lines)


def page_getting_started(repo: Path, tracked: set[str] | None) -> str:
    readme = read_text(repo, "README.md", tracked)
    if readme:
        found = section_matching(readme, QUICK_START_HEADINGS)
        if found:
            heading, body = found
            return f"# Getting Started\n\n## {heading}\n\n{body}\n\nSource: `README.md`."
    return "# Getting Started\n\n" + missing(
        "quick start section", "a `## Quick start`, `## Getting started`, `## Install`, or `## Usage` heading in `README.md`"
    )


def page_command_reference(repo: Path, tracked: set[str] | None) -> str:
    found = first_existing(repo, COMMANDS_CANDIDATES, tracked)
    if found:
        rel, text = found
        body = "\n".join(text.splitlines()[1:]).strip() if text.startswith("# ") else text.strip()
        return f"# Command Reference\n\n{body}\n\nSource: `{rel}`."
    return "# Command Reference\n\n" + missing("command reference", COMMANDS_CANDIDATES)


def page_architecture(repo: Path, tracked: set[str] | None) -> str:
    found = first_existing(repo, ARCHITECTURE_CANDIDATES, tracked)
    if found:
        rel, text = found
        body = "\n".join(text.splitlines()[1:]).strip() if text.startswith("# ") else text.strip()
        return f"# Architecture\n\n{body}\n\nSource: `{rel}`."
    return "# Architecture\n\n" + missing("architecture document", ARCHITECTURE_CANDIDATES)


def page_roadmap(repo: Path, tracked: set[str] | None) -> str:
    found = first_existing(repo, ROADMAP_CANDIDATES, tracked)
    if found:
        rel, text = found
        body = "\n".join(text.splitlines()[1:]).strip() if text.startswith("# ") else text.strip()
        return f"# Roadmap\n\n{body}\n\nSource: `{rel}`."
    return "# Roadmap\n\n" + missing("roadmap", ROADMAP_CANDIDATES)


def page_release_flow(repo: Path, tracked: set[str] | None) -> str:
    lines = ["# Release Flow", ""]

    version = read_text(repo, "VERSION", tracked)
    changelog = read_text(repo, "CHANGELOG.md", tracked)

    if version and version.strip():
        lines.append(f"Declared version: `{version.strip()}` (`VERSION`).")
    else:
        lines.append("No `VERSION` file found.")

    if changelog:
        match = CHANGELOG_HEADING.search(changelog)
        if match:
            lines += ["", f"Latest release in `CHANGELOG.md`: `{match.group(1)}`."]
        else:
            lines += ["", "`CHANGELOG.md` exists but declares no versioned release heading."]
        if version and version.strip() and match and match.group(1) != version.strip():
            lines += [
                "",
                f"`VERSION` and `CHANGELOG.md` disagree: `{version.strip()}` vs `{match.group(1)}`.",
            ]
    else:
        lines += ["", "No `CHANGELOG.md` found."]

    return "\n".join(lines)


def page_skills(repo: Path, tracked: set[str] | None) -> str:
    names: list[str] = []
    for pattern in SKILL_GLOBS:
        for path in sorted(repo.glob(pattern)):
            if tracked is not None and str(path.relative_to(repo)) not in tracked:
                continue
            name = path.parent.name if path.name == "SKILL.md" else path.stem
            if name not in names:
                names.append(name)

    if not names:
        return "# Skills\n\n" + missing("skills", SKILL_GLOBS)

    listed = "\n".join(f"- {name}" for name in names)
    return f"# Skills\n\n{listed}"


def page_troubleshooting(repo: Path, tracked: set[str] | None) -> str:
    found = first_existing(repo, TROUBLESHOOTING_CANDIDATES, tracked)
    if found:
        rel, text = found
        body = "\n".join(text.splitlines()[1:]).strip() if text.startswith("# ") else text.strip()
        return f"# Troubleshooting\n\n{body}\n\nSource: `{rel}`."

    readme = read_text(repo, "README.md", tracked)
    if readme:
        section = section_matching(readme, TROUBLESHOOTING_HEADINGS)
        if section:
            heading, body = section
            return f"# Troubleshooting\n\n## {heading}\n\n{body}\n\nSource: `README.md`."

    return "# Troubleshooting\n\n" + missing("troubleshooting documentation", TROUBLESHOOTING_CANDIDATES)


PAGE_BUILDERS = {
    "Home.md": page_home,
    "Getting-Started.md": page_getting_started,
    "Command-Reference.md": page_command_reference,
    "Architecture.md": page_architecture,
    "Roadmap.md": page_roadmap,
    "Release-Flow.md": page_release_flow,
    "Skills.md": page_skills,
    "Troubleshooting.md": page_troubleshooting,
}


def build_wiki_pages(repo_path: str | Path = ".") -> dict[str, str]:
    """Build every wiki page from the target repository's own files."""
    repo = Path(repo_path).resolve()
    tracked = tracked_paths(repo)
    return {name: PAGE_BUILDERS[name](repo, tracked) for name in PAGE_ORDER}


def display_path(path: Path, repo: Path) -> str:
    if path.is_relative_to(repo):
        return str(path.relative_to(repo))
    return str(path)


def export_wiki_pages(
    repo_path: str = ".",
    output_path: str = "docs/wiki-export",
) -> str:
    repo = Path(repo_path).resolve()
    output = (repo / output_path).resolve()
    output.mkdir(parents=True, exist_ok=True)

    written = []

    for filename, content in build_wiki_pages(repo).items():
        path = output / filename
        path.write_text(content.rstrip() + "\n", encoding="utf-8")
        written.append(path)

    lines = [
        "WIKI EXPORT",
        "===========",
        f"Repo: {project_name(repo, tracked_paths(repo))}",
        f"Output: {display_path(output, repo)}",
        "",
        "Written files",
        "-------------",
    ]

    for path in written:
        lines.append(f"- {display_path(path, repo)}")

    lines.extend(
        [
            "",
            "Next action",
            "-----------",
            "Review generated files before copying them into the GitHub Wiki.",
        ]
    )

    return "\n".join(lines)
