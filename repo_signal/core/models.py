from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class GitHealth:
    is_repo: bool
    branch: str = ""
    changed_files: int = 0
    status_lines: list[str] = field(default_factory=list)


@dataclass
class RepoSummary:
    path: Path
    project_type: str
    languages: list[tuple[str, int]]
    key_entrypoints: list[str]
    git: GitHealth
    repo_size_files: int
    repo_size_mb: float
    top_directories: list[tuple[str, int]]
    detected_tooling: list[str]
    focus_areas: list[str]

