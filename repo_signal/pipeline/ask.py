from pathlib import Path
from typing import Optional

from repo_signal.ai.providers.base import BaseProvider, ProviderConfigurationError
from repo_signal.ai.providers.openai_provider import OpenAIProvider
from repo_signal.core.models import Repository
from repo_signal.pipeline.context import build_focused_context, rank_files
from repo_signal.pipeline.prompts import build_ask_prompt
from repo_signal.pipeline.response import AskPipelineResult


def get_provider(provider_name: str) -> BaseProvider:
    if provider_name == "openai":
        return OpenAIProvider()
    raise ProviderConfigurationError(f"Unknown provider: {provider_name}")


def run_ask_pipeline(
    repo_path: Path,
    question: str,
    mode: str = "explain",
    provider_name: str = "openai",
    dry_run: bool = False,
    provider: Optional[BaseProvider] = None,
) -> AskPipelineResult:
    repo = Repository.load(repo_path)
    signals = rank_files(repo, question, mode=mode)
    context = build_focused_context(repo, question, signals, mode=mode)
    prompt = build_ask_prompt(
        question=question,
        context=context,
        mode=mode,
        referenced_files=[signal.file_path for signal in signals],
    )

    answer = ""
    if not dry_run:
        selected_provider = provider or get_provider(provider_name)
        answer = selected_provider.generate(prompt)

    return AskPipelineResult(
        repo=repo,
        question=question,
        mode=mode,
        context=context,
        prompt=prompt,
        signals=signals,
        answer=answer,
    )

