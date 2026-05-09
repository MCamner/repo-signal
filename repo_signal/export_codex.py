import argparse
from pathlib import Path
import sys
from typing import List, Optional

from repo_signal.codex.exporter import SkillExportError, available_skills, export_codex_skill


def format_result(result) -> str:
    lines = []
    lines.append("# Codex Skill Export")
    lines.append("")
    lines.append(f"Installed skill: `{result.name}`")
    lines.append(f"Source: `{result.source}`")
    lines.append(f"Location: `{result.target}`")
    lines.append(f"Files copied: `{result.files}`")
    return "\n".join(lines)


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="repo-signal export-codex",
        description="Export repo-local skills into Codex skill storage.",
    )
    parser.add_argument("skill", nargs="?", help="Skill name from skills/<name>.")
    parser.add_argument("--local", action="store_true", help="Install to .codex/skills in this repo.")
    parser.add_argument(
        "--target-root",
        type=Path,
        default=None,
        help="Override target skill root. Defaults to ~/.codex/skills.",
    )
    parser.add_argument("--list", action="store_true", help="List exportable skills.")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    repo_root = Path.cwd()

    if args.list:
        for name in available_skills(repo_root):
            print(name)
        return

    if not args.skill:
        print("repo-signal export-codex: skill name required", file=sys.stderr)
        raise SystemExit(2)

    try:
        result = export_codex_skill(
            args.skill,
            repo_root=repo_root,
            target_root=args.target_root,
            local=args.local,
        )
    except SkillExportError as exc:
        print(f"repo-signal export-codex: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    print(format_result(result))


if __name__ == "__main__":
    main()
