from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Union


@dataclass
class GitContext:
    branch: str = ""
    status: str = ""
    is_repo: bool = False

    @property
    def status_lines(self) -> List[str]:
        return self.status.splitlines() if self.status else []

    @property
    def changed_files(self) -> int:
        return len(self.status_lines)


@dataclass
class FileNode:
    path: str
    extension: str
    size: int
    keywords: List[str] = field(default_factory=list)


@dataclass
class Signal:
    file_path: str
    score: int
    reasons: List[str] = field(default_factory=list)


@dataclass
class Edge:
    source: str
    target: str
    relation: str


@dataclass
class RepositoryGraph:
    edges: List[Edge] = field(default_factory=list)

    def outgoing(self, file_path: str) -> List[Edge]:
        return [edge for edge in self.edges if edge.source == file_path]

    def incoming(self, file_path: str) -> List[Edge]:
        return [edge for edge in self.edges if edge.target == file_path]


@dataclass
class Repository:
    name: str
    path: Path

    files: List[FileNode] = field(default_factory=list)
    top_directories: List[str] = field(default_factory=list)
    top_directory_counts: Dict[str, int] = field(default_factory=dict)
    languages: Dict[str, int] = field(default_factory=dict)
    entrypoints: List[str] = field(default_factory=list)
    signals: List[Signal] = field(default_factory=list)
    graph: RepositoryGraph = field(default_factory=RepositoryGraph)
    git: GitContext = field(default_factory=GitContext)

    project_type: str = "General repository"
    detected_tooling: List[str] = field(default_factory=list)
    focus_areas: List[str] = field(default_factory=list)
    size_bytes: int = 0

    @property
    def repo_size_files(self) -> int:
        return len(self.files)

    @property
    def repo_size_mb(self) -> float:
        return self.size_bytes / 1024 / 1024

    @classmethod
    def load(cls, path: Union[str, Path] = ".") -> "Repository":
        from repo_signal.core.scanner import scan_repository

        return scan_repository(path)
