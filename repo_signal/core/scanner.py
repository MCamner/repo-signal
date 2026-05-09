from collections import Counter
from pathlib import Path
import re
import subprocess
from typing import Union

from repo_signal.core.models import FileNode, GitContext, Repository
from repo_signal.symbols.symbol_extractor import extract_symbols


IGNORE_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "venv",
}

LANGUAGE_MAP = {
    ".py": "Python",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".html": "HTML",
    ".css": "CSS",
    ".md": "Markdown",
    ".json": "JSON",
    ".toml": "TOML",
    ".yaml": "YAML",
    ".yml": "YAML",
}

TOOLING_FILES = {
    "pyproject.toml": "Python packaging",
    "requirements.txt": "Python requirements",
    "package.json": "Node package",
    "Dockerfile": "Docker",
    "docker-compose.yml": "Docker Compose",
    "Makefile": "Make",
    ".github/workflows": "GitHub Actions",
    "docs/index.html": "GitHub Pages docs",
    "README.md": "README",
    "LICENSE": "License",
}

ENTRYPOINT_NAME_KEYWORDS = {
    "app",
    "cli",
    "launch",
    "main",
    "run",
}

ENTRYPOINT_NAMES = {
    "__main__.py",
    "app.py",
    "cli.py",
    "main.py",
    "manage.py",
    "server.py",
}


def run(cmd: list[str], cwd: Union[Path, None] = None) -> str:
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def should_ignore(path: Path) -> bool:
    return any(part in IGNORE_DIRS or part.endswith(".egg-info") for part in path.parts)


def extract_keywords(path: Path) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9_-]+", path.stem.lower())
    return list(dict.fromkeys(word for word in words if len(word) > 1))


def build_git_context(repo_path: Path) -> GitContext:
    inside = run(["git", "rev-parse", "--is-inside-work-tree"], cwd=repo_path)
    is_repo = inside == "true"

    if not is_repo:
        return GitContext()

    return GitContext(
        branch=run(["git", "branch", "--show-current"], cwd=repo_path),
        status=run(["git", "status", "--short"], cwd=repo_path),
        is_repo=True,
    )


def detect_project_type(repo: Repository) -> str:
    path = repo.path

    if (path / "pyproject.toml").exists() and (path / "repo_signal").exists():
        return "Python CLI / repo intelligence toolkit"
    if (path / "pyproject.toml").exists():
        return "Python project"
    if (path / "package.json").exists() and (path / "docs" / "index.html").exists():
        return "JavaScript / static web project"
    if (path / "package.json").exists():
        return "JavaScript / Node project"
    if (path / "docs" / "index.html").exists():
        return "GitHub Pages / static web project"
    if (path / "bin").exists() or (path / "tools").exists() or (path / "scripts").exists():
        return "Command-line tools / automation"
    return "General repository"


def detect_tooling(repo_path: Path) -> list[str]:
    found = []

    for target, label in TOOLING_FILES.items():
        if (repo_path / target).exists():
            found.append(label)

    return found


def is_entrypoint(relative: Path, full_path: Path) -> bool:
    path_text = relative.as_posix()
    name_lower = relative.name.lower()

    if path_text.startswith("tests/") or "/tests/" in path_text:
        return False

    if relative.name in ENTRYPOINT_NAMES:
        return True
    if path_text.startswith(("bin/", "scripts/", "tools/")):
        return True
    if any(keyword in name_lower for keyword in ENTRYPOINT_NAME_KEYWORDS):
        return True
    if full_path.suffix.lower() in {".sh", ".bash", ".zsh"}:
        try:
            first_line = full_path.read_text(encoding="utf-8", errors="ignore").splitlines()[0]
        except (IndexError, OSError):
            first_line = ""
        return first_line.startswith("#!")

    return False


def suggest_focus_areas(repo: Repository) -> list[str]:
    focus = []

    if not (repo.path / "README.md").exists():
        focus.append("Create README.md with purpose, install, usage, and examples")
    if not (repo.path / "LICENSE").exists():
        focus.append("Add a LICENSE file")
    if not (repo.path / ".gitignore").exists():
        focus.append("Add .gitignore for local and build artifacts")
    if not (repo.path / "tests").exists():
        focus.append("Add focused tests for the main command surface")
    if not repo.entrypoints:
        focus.append("Document or add a clear executable entrypoint")
    if repo.git.changed_files:
        focus.append("Review current working tree changes before release or demo")
    if "GitHub Pages docs" not in repo.detected_tooling:
        focus.append("Add or clarify whether a public docs/demo page is needed")

    if not focus:
        focus.append("Foundation looks healthy; improve analysis depth next")

    return focus[:6]


def scan_repository(path: Union[str, Path] = ".") -> Repository:
    repo_path = Path(path).expanduser().resolve()
    repo = Repository(
        name=repo_path.name,
        path=repo_path,
        git=build_git_context(repo_path),
    )

    language_counter = Counter()
    top_directory_counter = Counter()

    for full_path in repo_path.rglob("*"):
        if not full_path.is_file():
            continue

        try:
            relative = full_path.relative_to(repo_path)
        except ValueError:
            continue

        if should_ignore(relative):
            continue

        try:
            size = full_path.stat().st_size
        except OSError:
            size = 0

        extension = full_path.suffix.lower()
        language = LANGUAGE_MAP.get(extension)
        if language:
            language_counter[language] += 1

        top_directory = relative.parts[0] if len(relative.parts) > 1 else "."
        top_directory_counter[top_directory] += 1

        relative_path = relative.as_posix()
        repo.files.append(
            FileNode(
                path=relative_path,
                extension=extension,
                size=size,
                keywords=extract_keywords(relative),
            )
        )
        repo.size_bytes += size

        if is_entrypoint(relative, full_path):
            repo.entrypoints.append(relative_path)

        repo.symbols.extend(extract_symbols(full_path, repo_path=repo_path))

    repo.languages = dict(language_counter.most_common())
    repo.top_directory_counts = dict(top_directory_counter.most_common())
    repo.top_directories = list(repo.top_directory_counts.keys())
    repo.entrypoints = sorted(dict.fromkeys(repo.entrypoints))[:10]
    repo.detected_tooling = detect_tooling(repo_path)
    repo.project_type = detect_project_type(repo)
    repo.focus_areas = suggest_focus_areas(repo)

    from repo_signal.graph.graph_builder import build_repository_graph

    repo.graph = build_repository_graph(repo)

    return repo
