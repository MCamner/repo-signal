from dataclasses import dataclass
from pathlib import Path
import os
import subprocess
import tempfile
from typing import List, Optional

from repo_signal.ai.providers.base import ProviderConfigurationError
from repo_signal.ai.providers.openai_provider import load_dotenv_if_available
from repo_signal.core.models import Repository
from repo_signal.vectorstore.chunks import build_symbol_chunks


VECTOR_STORE_ENV = "OPENAI_VECTOR_STORE_ID"


@dataclass
class OpenAIUploadResult:
    repo_name: str
    vector_store_id: str
    filename: str
    symbols: int
    bytes_written: int
    status: str
    file_id: str = ""


def load_shell_env_if_available(name: str) -> None:
    if os.getenv(name):
        return

    try:
        result = subprocess.run(
            ["zsh", "-lic", f"print -r -- ${{{name}:-}}"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except Exception:
        return

    value = result.stdout.strip()
    if value:
        os.environ[name] = value


def resolve_vector_store_id(vector_store_id: Optional[str] = None) -> str:
    load_dotenv_if_available()
    load_shell_env_if_available(VECTOR_STORE_ENV)

    resolved = vector_store_id or os.getenv(VECTOR_STORE_ENV, "")
    if not resolved:
        raise ProviderConfigurationError(
            "OpenAI vector store id is missing. Pass --vector-store-id or set OPENAI_VECTOR_STORE_ID."
        )
    return resolved


def openai_client():
    load_dotenv_if_available()
    load_shell_env_if_available("OPENAI_API_KEY")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ProviderConfigurationError(
            "OPENAI_API_KEY is not available. Export it before uploading to OpenAI."
        )

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ProviderConfigurationError(
            "The OpenAI Python package is not installed. Install the optional AI dependencies first."
        ) from exc

    return OpenAI(api_key=api_key)


def build_openai_memory_document(repo: Repository, include_tests: bool = False) -> str:
    chunks = build_symbol_chunks(repo, include_tests=include_tests)
    lines: List[str] = []

    lines.append(f"# {repo.name} Repository Semantic Memory")
    lines.append("")
    lines.append("memory_type: repository_symbols")
    lines.append(f"repo: {repo.name}")
    lines.append("scope: symbol summaries, entrypoints, structural relationships")
    lines.append("")

    lines.append("## Entry Points")
    lines.append("")
    if repo.entrypoints:
        for entrypoint in repo.entrypoints:
            lines.append(f"- {entrypoint}")
    else:
        lines.append("- none detected")
    lines.append("")

    lines.append("## Symbol Summaries")
    lines.append("")
    for chunk in chunks:
        lines.append(f"### {chunk.symbol}")
        lines.append(f"- kind: {chunk.kind}")
        lines.append(f"- file: {chunk.file_path}:{chunk.line}")
        lines.append(f"- language: {chunk.language}")
        lines.append(f"- summary: {chunk.summary}")
        lines.append("")

    lines.append("## Structural Relationships")
    lines.append("")
    if repo.graph.edges:
        for edge in repo.graph.edges:
            lines.append(f"- {edge.source} -> {edge.target} ({edge.relation})")
    else:
        lines.append("- none detected")
    lines.append("")

    return "\n".join(lines)


def upload_repository_memory(
    repo_path: Path,
    vector_store_id: Optional[str] = None,
    include_tests: bool = False,
    dry_run: bool = False,
) -> OpenAIUploadResult:
    repo = Repository.load(repo_path)
    resolved_store_id = resolve_vector_store_id(vector_store_id)
    document = build_openai_memory_document(repo, include_tests=include_tests)
    encoded = document.encode("utf-8")
    filename = f"{repo.name}-symbol-memory.md"

    if dry_run:
        return OpenAIUploadResult(
            repo_name=repo.name,
            vector_store_id=resolved_store_id,
            filename=filename,
            symbols=len(build_symbol_chunks(repo, include_tests=include_tests)),
            bytes_written=len(encoded),
            status="dry_run",
        )

    client = openai_client()

    with tempfile.NamedTemporaryFile("wb", suffix=".md", delete=True) as file:
        file.write(encoded)
        file.flush()
        file.seek(0)
        result = client.vector_stores.files.upload_and_poll(
            vector_store_id=resolved_store_id,
            file=(filename, file, "text/markdown"),
            attributes={
                "repo": repo.name,
                "memory_type": "symbols",
                "source": "repo-signal",
            },
        )

    return OpenAIUploadResult(
        repo_name=repo.name,
        vector_store_id=resolved_store_id,
        filename=filename,
        symbols=len(build_symbol_chunks(repo, include_tests=include_tests)),
        bytes_written=len(encoded),
        status=getattr(result, "status", "unknown"),
        file_id=getattr(result, "id", ""),
    )

