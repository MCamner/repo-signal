from pathlib import Path
import re
from typing import List, Optional

from repo_signal.core.models import Symbol


PYTHON_CLASS_RE = re.compile(r"^\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(:]", re.MULTILINE)
PYTHON_FUNCTION_RE = re.compile(r"^\s*(?:async\s+)?def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", re.MULTILINE)
SHELL_FUNCTION_RE = re.compile(
    r"^\s*(?:function\s+)?([a-zA-Z_][a-zA-Z0-9_-]*)\s*(?:\(\))?\s*\{",
    re.MULTILINE,
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def line_number_at(content: str, position: int) -> int:
    return content.count("\n", 0, position) + 1


def extract_python_symbols(file_path: str, content: str) -> List[Symbol]:
    symbols = []

    for match in PYTHON_CLASS_RE.finditer(content):
        symbols.append(
            Symbol(
                name=match.group(1),
                kind="class",
                file_path=file_path,
                line=line_number_at(content, match.start()),
            )
        )

    for match in PYTHON_FUNCTION_RE.finditer(content):
        symbols.append(
            Symbol(
                name=match.group(1),
                kind="function",
                file_path=file_path,
                line=line_number_at(content, match.start()),
            )
        )

    return symbols


def extract_shell_symbols(file_path: str, content: str) -> List[Symbol]:
    symbols = []

    for match in SHELL_FUNCTION_RE.finditer(content):
        symbols.append(
            Symbol(
                name=match.group(1),
                kind="shell_function",
                file_path=file_path,
                line=line_number_at(content, match.start()),
            )
        )

    return symbols


def extract_symbols(path: Path, repo_path: Optional[Path] = None) -> List[Symbol]:
    content = read_text(path)
    if not content:
        return []

    if repo_path is not None:
        try:
            symbol_path = path.resolve().relative_to(repo_path.resolve()).as_posix()
        except ValueError:
            symbol_path = path.as_posix()
    else:
        symbol_path = path.as_posix()

    suffix = path.suffix.lower()
    if suffix == ".py":
        return extract_python_symbols(symbol_path, content)
    first_line = content.splitlines()[0] if content.splitlines() else ""
    if suffix in {".sh", ".bash", ".zsh"} or "bash" in first_line or "zsh" in first_line or " sh" in first_line:
        return extract_shell_symbols(symbol_path, content)

    return []
