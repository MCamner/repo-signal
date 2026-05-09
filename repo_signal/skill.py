import argparse
from pathlib import Path
import sys
from typing import List, Optional

from repo_signal.codex.exporter import SkillExportError, create_codex_skill


def format_create_result(result) -> str:
    lines = []
    lines.append("# Codex Skill Created")
    lines.append("")
    lines.append(f"Skill: `{result.name}`")
    lines.append(f"Location: `{result.path}`")
    lines.append(f"File: `{result.path / 'SKILL.md'}`")
    lines.append("")
    lines.append("Next:")
    lines.append(f"1. Edit `skills/{result.name}/SKILL.md`")
    lines.append(f"2. Export with `repo-signal export-codex {result.name}`")
    return "\n".join(lines)


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="repo-signal skill",
        description="Create repo-local Codex skills.",
    )
    subparsers = parser.add_subparsers(dest="command")

    new_parser = subparsers.add_parser("new", help="Create skills/<name>/SKILL.md.")
    new_parser.add_argument("name", help="Skill name, for example repo-aware.")
    new_parser.add_argument(
        "--description",
        default=None,
        help="Skill trigger description for SKILL.md frontmatter.",
    )

    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    if args.command != "new":
        print("repo-signal skill: expected command `new`", file=sys.stderr)
        raise SystemExit(2)

    try:
        result = create_codex_skill(
            args.name,
            repo_root=Path.cwd(),
            description=args.description,
        )
    except SkillExportError as exc:
        print(f"repo-signal skill: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    print(format_create_result(result))


if __name__ == "__main__":
    main()
