from dataclasses import dataclass
from pathlib import Path
import re
from typing import Dict, List

from repo_signal.core.models import Repository, Symbol
from repo_signal.symbols.summarizer import summarize_symbol


MAX_SYMBOL_SNIPPET_LINES = 36


@dataclass
class SymbolChunk:
    id: str
    symbol: str
    file_path: str
    kind: str
    language: str
    line: int
    summary: str
    text: str

    @property
    def metadata(self) -> Dict[str, object]:
        return {
            "symbol": self.symbol,
            "file": self.file_path,
            "kind": self.kind,
            "language": self.language,
            "line": self.line,
        }


def language_for_symbol(symbol: Symbol) -> str:
    if symbol.kind == "shell_function":
        return "shell"
    if symbol.file_path.endswith(".py"):
        return "python"
    return "unknown"


def chunk_id(symbol: Symbol) -> str:
    safe_symbol = re.sub(r"[^a-zA-Z0-9_.-]+", "-", symbol.name)
    safe_file = re.sub(r"[^a-zA-Z0-9_.-]+", "-", symbol.file_path)
    return f"{safe_file}:{safe_symbol}:{symbol.line}"


def read_symbol_snippet(repo: Repository, symbol: Symbol, max_lines: int = MAX_SYMBOL_SNIPPET_LINES) -> str:
    path = repo.path / symbol.file_path
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return ""

    if not lines:
        return ""

    start = max(0, symbol.line - 1)
    end = min(len(lines), start + max_lines)
    return "\n".join(lines[start:end]).rstrip()


def build_symbol_chunk(repo: Repository, symbol: Symbol) -> SymbolChunk:
    summary = summarize_symbol(symbol)
    snippet = read_symbol_snippet(repo, symbol)
    language = language_for_symbol(symbol)
    text = "\n".join(
        [
            f"symbol: {symbol.name}",
            f"kind: {symbol.kind}",
            f"language: {language}",
            f"file: {symbol.file_path}:{symbol.line}",
            f"summary: {summary}",
            "snippet:",
            snippet,
        ]
    ).strip()

    return SymbolChunk(
        id=chunk_id(symbol),
        symbol=symbol.name,
        file_path=symbol.file_path,
        kind=symbol.kind,
        language=language,
        line=symbol.line,
        summary=summary,
        text=text,
    )


def build_symbol_chunks(repo: Repository, include_tests: bool = False) -> List[SymbolChunk]:
    chunks = []

    for symbol in repo.symbols:
        if not include_tests and (
            symbol.file_path.startswith("tests/")
            or "/tests/" in symbol.file_path
            or symbol.name.startswith("test_")
        ):
            continue
        chunks.append(build_symbol_chunk(repo, symbol))

    return chunks
