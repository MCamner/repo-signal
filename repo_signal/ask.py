import argparse
from pathlib import Path
import sys
from typing import Optional

from repo_signal.ai.providers.base import ProviderConfigurationError
from repo_signal.pipeline.ask import run_ask_pipeline
from repo_signal.pipeline.response import format_pipeline_output


def build_ask_prompt(repo_path: Path, question: str, mode: str = "explain") -> str:
    result = run_ask_pipeline(
        repo_path=repo_path,
        question=question,
        mode=mode,
        dry_run=True,
    )
    return result.prompt


def ask_repo(
    repo_path: Path,
    question: str,
    mode: str = "explain",
    provider_name: str = "openai",
    dry_run: bool = False,
) -> str:
    result = run_ask_pipeline(
        repo_path=repo_path,
        question=question,
        mode=mode,
        provider_name=provider_name,
        dry_run=dry_run,
    )
    return format_pipeline_output(result, dry_run=dry_run)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="repo-signal ask",
        description="Ask an AI provider a repo-aware question using ranked context.",
    )
    parser.add_argument(
        "--mode",
        choices=["architect", "debug", "explain", "review"],
        default="explain",
        help="RepoAware context mode.",
    )
    parser.add_argument(
        "--provider",
        choices=["openai"],
        default="openai",
        help="AI provider.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the prompt instead of calling the provider.",
    )
    parser.add_argument("question", nargs="+", help="Question to answer.")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> None:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    question = " ".join(args.question)

    try:
        answer = ask_repo(
            repo_path=Path.cwd(),
            question=question,
            mode=args.mode,
            provider_name=args.provider,
            dry_run=args.dry_run,
        )
    except ProviderConfigurationError as exc:
        print(f"repo-signal ask: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    print(answer)


if __name__ == "__main__":
    main()
