from pathlib import Path
import re
from typing import Dict, Iterable, List, Optional, Set

from repo_signal.core.models import Edge, FileNode, Repository, RepositoryGraph


PYTHON_FROM_IMPORT_RE = re.compile(r"^\s*from\s+([a-zA-Z0-9_.]+)\s+import\s+", re.MULTILINE)
PYTHON_IMPORT_RE = re.compile(r"^\s*import\s+([a-zA-Z0-9_.,\t ]+)", re.MULTILINE)
SHELL_SOURCE_RE = re.compile(r"^\s*(?:source|\.)\s+['\"]?([^'\"\s;]+)", re.MULTILINE)
SHELL_EXEC_RE = re.compile(r"^\s*(?:bash|zsh|sh)\s+['\"]?([^'\"\s;]+)", re.MULTILINE)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def file_index(files: Iterable[FileNode]) -> Set[str]:
    return {file.path for file in files}


def module_index(files: Iterable[FileNode]) -> Dict[str, str]:
    modules = {}

    for file in files:
        if file.extension != ".py":
            continue

        path = Path(file.path)
        if path.name == "__init__.py":
            module = ".".join(path.parent.parts)
        else:
            module = ".".join(path.with_suffix("").parts)

        if module:
            modules[module] = file.path

    return modules


def resolve_python_module(module: str, modules: Dict[str, str]) -> Optional[str]:
    if module in modules:
        return modules[module]

    parts = module.split(".")
    while len(parts) > 1:
        parts.pop()
        candidate = ".".join(parts)
        if candidate in modules:
            return modules[candidate]

    return None


def clean_shell_target(raw_target: str) -> Optional[str]:
    target = raw_target.strip().strip("'\"")

    if not target or "$" in target or target.startswith(("-", "|")):
        return None

    return target


def resolve_repo_path(
    repo_path: Path,
    source_path: str,
    raw_target: str,
    known_files: Set[str],
) -> Optional[str]:
    target = clean_shell_target(raw_target)
    if not target:
        return None

    source_dir = Path(source_path).parent
    candidates = [
        source_dir / target,
        Path(target),
    ]

    for candidate in candidates:
        normalized = candidate.as_posix().removeprefix("./")
        if normalized in known_files:
            return normalized

        absolute = (repo_path / candidate).resolve()
        try:
            relative = absolute.relative_to(repo_path).as_posix()
        except ValueError:
            continue

        if relative in known_files:
            return relative

    return None


def python_import_edges(source: FileNode, text: str, modules: Dict[str, str]) -> List[Edge]:
    edges = []

    for match in PYTHON_FROM_IMPORT_RE.finditer(text):
        target = resolve_python_module(match.group(1), modules)
        if target and target != source.path:
            edges.append(Edge(source=source.path, target=target, relation="python_import"))

    for match in PYTHON_IMPORT_RE.finditer(text):
        imports = [item.strip().split(" as ", 1)[0] for item in match.group(1).split(",")]
        for imported in imports:
            target = resolve_python_module(imported, modules)
            if target and target != source.path:
                edges.append(Edge(source=source.path, target=target, relation="python_import"))

    return edges


def shell_edges(repo_path: Path, source: FileNode, text: str, known_files: Set[str]) -> List[Edge]:
    edges = []

    for match in SHELL_SOURCE_RE.finditer(text):
        target = resolve_repo_path(repo_path, source.path, match.group(1), known_files)
        if target and target != source.path:
            edges.append(Edge(source=source.path, target=target, relation="shell_source"))

    for match in SHELL_EXEC_RE.finditer(text):
        target = resolve_repo_path(repo_path, source.path, match.group(1), known_files)
        if target and target != source.path:
            edges.append(Edge(source=source.path, target=target, relation="shell_exec"))

    return edges


def dedupe_edges(edges: Iterable[Edge]) -> List[Edge]:
    seen = set()
    unique = []

    for edge in edges:
        key = (edge.source, edge.target, edge.relation)
        if key in seen:
            continue
        seen.add(key)
        unique.append(edge)

    return sorted(unique, key=lambda edge: (edge.source, edge.target, edge.relation))


def build_repository_graph(repo: Repository) -> RepositoryGraph:
    known_files = file_index(repo.files)
    modules = module_index(repo.files)
    edges = []

    for file in repo.files:
        if file.extension not in {".py", ".sh", ".bash", ".zsh"}:
            continue

        text = read_text(repo.path / file.path)
        if not text:
            continue

        if file.extension == ".py":
            edges.extend(python_import_edges(file, text, modules))
        else:
            edges.extend(shell_edges(repo.path, file, text, known_files))

    return RepositoryGraph(edges=dedupe_edges(edges))
