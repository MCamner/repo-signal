import argparse
from pathlib import Path
import sys
from typing import Optional

from repo_signal.ai.prompts.repo_question import build_repo_question_prompt
from repo_signal.ai.providers.base import ProviderConfigurationError
from repo_signal.ai.providers.openai_provider import OpenAIProvider
from repo_signal.repoaware.context_builder import build_context


def build_ask_prompt(repo_path: Path, question: str, mode: str = "explain") -> str:
    context = build_context(
        repo_path=repo_path,
        question=question,
        mode=mode,
        output_format="markdown",
    )
    return build_repo_question_prompt(context=context, question=question)


def ask_repo(
    repo_path: Path,
    question: str,
    mode: str = "explain",
    provider_name: str = "openai",
    dry_run: bool = False,
) -> str:
    prompt = build_ask_prompt(repo_path=repo_path, question=question, mode=mode)

    if dry_run:
        return prompt

    if provider_name != "openai":
        raise ProviderConfigurationError(f"Unknown provider: {provider_name}")

    provider = OpenAIProvider()
    return provider.generate(prompt)


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

