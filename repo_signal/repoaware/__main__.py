import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional

from repo_signal.repoaware.context_builder import (
    DEFAULT_FORMAT,
    DEFAULT_MODE,
    VALID_FORMATS,
    VALID_MODES,
    build_context,
)


def copy_to_clipboard(text: str) -> bool:
    try:
        subprocess.run(["pbcopy"], input=text, text=True, check=True)
        return True
    except Exception:
        return False


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="repoaware",
        description="Build high-signal repo context for AI-assisted code questions.",
    )
    parser.add_argument(
        "--mode",
        choices=sorted(VALID_MODES),
        default=DEFAULT_MODE,
        help="Context mode.",
    )
    parser.add_argument(
        "--format",
        choices=sorted(VALID_FORMATS),
        default=DEFAULT_FORMAT,
        help="Output format.",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy output to clipboard with pbcopy when available.",
    )
    parser.add_argument("question", nargs="+", help="Question to build repo context for.")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> None:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    question = " ".join(args.question)
    context = build_context(
        repo_path=Path.cwd(),
        question=question,
        mode=args.mode,
        output_format=args.format,
    )

    if args.copy:
        copied = copy_to_clipboard(context)
        if not copied:
            print("[repoaware] clipboard copy failed; printing output instead.", file=sys.stderr)

    print(context)


if __name__ == "__main__":
    main()
