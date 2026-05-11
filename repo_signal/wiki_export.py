from pathlib import Path


WIKI_EXPORT_PAGES = {
    "Home.md": """# Home

## Purpose

This wiki explains what the repository does, how to use it, how it is
structured, and what should happen next.

## Start Here

- Getting Started
- Command Reference
- Architecture
- Roadmap
- Release Flow
- Skills
- Troubleshooting
""",
    "Getting-Started.md": """# Getting Started

## Basic Flow

```bash
repo-signal analyze .
repo-signal doctor .
repo-signal publish-checklist .
```

## Common Next Step

Run a publish checklist before polishing or releasing a repository.
""",
    "Command-Reference.md": """# Command Reference

## Core Commands

```bash
repo-signal analyze .
repo-signal doctor .
repo-signal publish-checklist .
repo-signal publish-checklist . --format markdown
repo-signal publish-checklist . --format json
repo-signal wiki plan .
repo-signal wiki export . --output docs/wiki-export
```
""",
    "Architecture.md": """# Architecture

## Current Architecture

repo-signal is a local-first repository intelligence tool.

Core areas:

- scanning
- README scoring
- publish checklist
- RepoAware context generation
- wiki planning/export
- release readiness
""",
    "Roadmap.md": """# Roadmap

## Current Focus

Phase 3 - Wiki Generator.

## Next Milestones

- wiki plan
- wiki export
- generated wiki page review
- safe manual publish flow
""",
    "Release-Flow.md": """# Release Flow

## Recommended Release Check

```bash
git status --short
python3 -m pytest -q
repo-signal publish-checklist .
repo-signal publish-checklist . --format json
```

## Release Notes

Keep release notes short, public-facing, and focused on user-visible change.
""",
    "Skills.md": """# Skills

## Local Skills

- repo-product-auditor
- terminal-ui-polisher
- release-readiness
- repo-aware

## Platform Skills

Track uploaded Platform skill IDs in:

```text
skills/platform-skills.md
```
""",
    "Troubleshooting.md": """# Troubleshooting

## Common Checks

```bash
repo-signal --help
python3 -m pytest -q
git status --short
repo-signal publish-checklist .
```

## If Output Looks Wrong

Check README formatting, local paths, missing docs folders, and generated
examples.
""",
}


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

    for filename, content in WIKI_EXPORT_PAGES.items():
        path = output / filename
        path.write_text(content.rstrip() + "\n", encoding="utf-8")
        written.append(path)

    lines = [
        "WIKI EXPORT",
        "===========",
        f"Repo: {repo.name}",
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
