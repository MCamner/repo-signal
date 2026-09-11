"""The single declaration of the repo-signal command surface.

Top-level `--help`, the unknown-command fallback list and subcommand `--help`
are all generated from `COMMANDS` here. `tests/test_command_registry.py`
additionally holds the dispatch chain in `cli.main()` and `docs/COMMANDS.md` to
the same list, so a command cannot be added in one place and forgotten in
another.
"""
from __future__ import annotations

from dataclasses import dataclass, field

TAGLINE = (
    "AI-assisted repo analysis for turning rough prototypes into clear, "
    "documented, publishable GitHub projects."
)

WIKI_EXPORT_HELP = """repo-signal wiki export

Generate wiki pages describing the target repository.

Usage:
  repo-signal wiki export [path] [--output path]

Options:
  -h, --help       Show this message
  --output PATH    Where to write the pages, relative to the target repo
                   (default: docs/wiki-export)

Pages are built from the target repo's own files: README.md, VERSION,
CHANGELOG.md, ROADMAP.md, docs/architecture.md, docs/COMMANDS.md, and skills/.
A page whose source is missing says so rather than inventing content.

Files are written locally and never pushed. Review them before copying into a
GitHub Wiki; see docs/PUBLISH-FLOW.md.
"""


@dataclass(frozen=True)
class Command:
    """One top-level command.

    `usage` lines are written without the `repo-signal ` prefix and must begin
    with the command name; the first word after the name, when it is not an
    option, is treated as a subcommand.

    `detailed` maps a subcommand to a full help text that replaces the generic
    one, for subcommands whose options deserve their own screen.
    """

    name: str
    summary: str
    usage: tuple[str, ...]
    examples: tuple[str, ...] = ()
    detailed: dict[str, str] = field(default_factory=dict)

    @property
    def subcommands(self) -> set[str]:
        subs = set()
        for line in self.usage:
            parts = line.split()
            if len(parts) > 1 and not parts[1].startswith(("-", "[", "<", '"')):
                subs.add(parts[1])
        return subs


COMMANDS: tuple[Command, ...] = (
    Command(
        name="actions",
        summary="Create a GitHub Actions publish-checklist workflow",
        usage=("actions init [path] [--fail-under score] [--force]",),
        examples=("actions init",),
    ),
    Command(
        name="analyze",
        summary="Summarize repo type, stack, health, structure, tooling, and focus areas",
        usage=("analyze [path]",),
        examples=("analyze",),
    ),
    Command(
        name="ask",
        summary="Ask an AI provider using ranked RepoAware context",
        usage=('ask [--mode mode] "question"',),
        examples=('ask --dry-run "how does routing work"',),
    ),
    Command(
        name="brief",
        summary="Compact daily health summary — publish signals, risks, and suggestions",
        usage=("brief [path] [--format text|json] [--json]",),
        examples=("brief .", "brief . --json"),
    ),
    Command(
        name="demo",
        summary="Print or generate a short repo-signal demo flow",
        usage=("demo [--generate] [path] [--output path] [--force]",),
        examples=("demo", "demo --generate"),
    ),
    Command(
        name="doctor",
        summary="Diagnose repo health, release maturity, docs quality, AI readiness, and skills",
        usage=("doctor [path] [--format markdown|json] [--json]",),
        examples=("doctor",),
    ),
    Command(
        name="inspect",
        summary="Show fast repo status, detected signals, issues, next commit, or inspect.v1 JSON",
        usage=("inspect [path] [--json|--format text|json]",),
        examples=("inspect",),
    ),
    Command(
        name="readiness",
        summary="Release readiness export — version alignment, freshness, and release gate",
        usage=("readiness [path] [--format text|json] [--json]",),
        examples=("readiness .", "readiness . --json"),
    ),
    Command(
        name="review-export",
        summary="Export a fresh inspect.v1 result to mqobsidian as repo-review.v1",
        usage=("review-export [path] [--vault PATH] [--force]",),
        examples=("review-export .",),
    ),
    Command(
        name="positioning",
        summary="Analyze README/project positioning and produce a positioning report",
        usage=("positioning [path] [--json|--format text|json]",),
        examples=("positioning .", "positioning . --json"),
    ),
    Command(
        name="scan",
        summary="Scan repo structure and basic project signals",
        usage=("scan",),
        examples=("scan",),
    ),
    Command(
        name="skill",
        summary="Create repo-local Codex skills",
        usage=("skill new <name> [--description text]",),
        examples=("skill new repo-aware",),
    ),
    Command(
        name="readme",
        summary="Analyze README clarity and missing sections",
        usage=("readme",),
        examples=("readme",),
    ),
    Command(
        name="readme-score",
        summary="Score README quality with a 100-point checklist",
        usage=("readme-score [path]",),
        examples=("readme-score .",),
    ),
    Command(
        name="publish-checklist",
        summary="Check public-facing docs, demo, release, and GitHub Pages signals",
        usage=(
            "publish-checklist [path] [--format text|markdown|json] "
            "[--fail-under score] [--fix-plan]",
        ),
        examples=(
            "publish-checklist .",
            "publish-checklist . --format json",
            "publish-checklist . --fail-under 14",
        ),
    ),
    Command(
        name="portfolio",
        summary="Check publish readiness across the repos in a repo-signal.yml portfolio",
        usage=("portfolio check [--config path] [--format text|markdown|json]",),
        examples=("portfolio check", "portfolio check --format markdown"),
    ),
    Command(
        name="repoaware",
        summary="Build high-signal repo context for AI-assisted code questions",
        usage=('repoaware [--mode mode] [--format format] "question"',),
        examples=('repoaware --mode debug "how does routing work"',),
    ),
    Command(
        name="semantic",
        summary="Search smart symbol chunks for semantic repository recall",
        usage=('semantic [--limit n] [--use-chroma] "query"',),
        examples=('semantic "routing system"',),
    ),
    Command(
        name="semantic-upload",
        summary="Upload symbol memory to a scoped OpenAI vector store",
        usage=("semantic-upload [--dry-run] [--vector-store-id id]",),
        examples=("semantic-upload --dry-run",),
    ),
    Command(
        name="export-codex",
        summary="Export repo-local skills into Codex skill storage",
        usage=("export-codex [--local] <skill>",),
        examples=("export-codex repo-product-auditor",),
    ),
    Command(
        name="export",
        summary="Generate symbolic intelligence packs (symbol_index, callgraph, repo_summary, risk_map)",
        usage=(
            "export [path] [--output DIR] "
            "[--all | --symbol-index | --callgraph | --repo-summary | --risk-map]",
        ),
        examples=("export . --all",),
    ),
    Command(
        name="hygiene",
        summary="Check junk files, .gitignore, large files, and Git status",
        usage=("hygiene",),
        examples=("hygiene",),
    ),
    Command(
        name="wiki",
        summary="Generate suggested GitHub Wiki structure, Home draft, or plan",
        usage=(
            "wiki [path]",
            "wiki plan [path]",
            "wiki export [path] [--output path]",
        ),
        examples=("wiki", "wiki plan .", "wiki export . --output docs/wiki-export"),
        detailed={"export": WIKI_EXPORT_HELP},
    ),
    Command(
        name="report",
        summary="Unified report — inspect + publish-checklist in text, markdown or JSON",
        usage=("report [path] [--format text|markdown|json]",),
        examples=("report .",),
    ),
    Command(
        name="suggest",
        summary="Safe patch suggestions — what to improve, no mutations",
        usage=("suggest [path] [--format text|markdown|json]",),
        examples=(
            "suggest .",
            "suggest . --format markdown",
            "suggest . --format json",
        ),
    ),
    Command(
        name="roadmap",
        summary="Generate a practical roadmap based on repo state",
        usage=("roadmap",),
        examples=("roadmap",),
    ),
)

COMMAND_INDEX: dict[str, Command] = {command.name: command for command in COMMANDS}

_SUMMARY_COLUMN = 13


def command_names() -> set[str]:
    return set(COMMAND_INDEX)


def _summary_block() -> list[str]:
    lines = []
    for command in COMMANDS:
        if len(command.name) + 3 <= _SUMMARY_COLUMN:
            lines.append(f"  {command.name.ljust(_SUMMARY_COLUMN - 3)} {command.summary}")
        else:
            lines.append(f"  {command.name}")
            lines.append(f"{' ' * _SUMMARY_COLUMN}{command.summary}")
    return lines


def build_help_text() -> str:
    """Render the top-level `--help` screen from the registry."""
    usage = [f"  repo-signal {line}" for command in COMMANDS for line in command.usage]
    usage.append("  repo-signal --help")
    usage.append("  repo-signal --version")

    examples = [
        f"  repo-signal {example}"
        for command in COMMANDS
        for example in command.examples
    ]

    return "\n".join(
        [
            "repo-signal",
            "",
            TAGLINE,
            "",
            "Usage:",
            *usage,
            "",
            "Commands:",
            *_summary_block(),
            "",
            "Examples:",
            *examples,
            "",
            "Run from any repository root.",
        ]
    )


def build_command_help(name: str, args: list[str] | None = None) -> str:
    """Render the `<command> --help` screen.

    When `args` names a subcommand that declares its own detailed help, that
    text is returned instead of the generic screen.
    """
    command = COMMAND_INDEX[name]

    if args:
        for arg in args:
            if arg in command.detailed:
                return command.detailed[arg]

    lines = [f"repo-signal {command.name}", "", command.summary, "", "Usage:"]
    lines += [f"  repo-signal {line}" for line in command.usage]
    lines += ["", "Options:", "  -h, --help   Show this message"]
    if command.examples:
        lines += ["", "Examples:"]
        lines += [f"  repo-signal {example}" for example in command.examples]
    return "\n".join(lines)


def fallback_command_list() -> str:
    """The comma-separated list printed after an unknown command."""
    names = [command.name for command in COMMANDS]
    return ", ".join([*names, "--help", "--version"])


def wants_help(args: list[str]) -> bool:
    return any(arg in {"-h", "--help"} for arg in args)
