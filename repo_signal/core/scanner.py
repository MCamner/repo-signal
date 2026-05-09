from collections import Counter
from pathlib import Path
import subprocess
from typing import Union

from repo_signal.core.models import GitHealth, RepoSummary


SKIP_DIRS = {
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

LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".jsx": "JavaScript",
    ".html": "HTML",
    ".css": "CSS",
    ".md": "Markdown",
    ".toml": "TOML",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".json": "JSON",
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

ENTRYPOINT_NAMES = {
    "cli.py",
    "__main__.py",
    "main.py",
    "app.py",
    "server.py",
    "manage.py",
}


def run_git(repo: Path, args: list[str]) -> tuple[int, str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        return result.returncode, result.stdout.strip()
    except FileNotFoundError:
        return 1, ""


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS or part.endswith(".egg-info") for part in path.parts)


def iter_repo_files(repo: Path):
    for path in repo.rglob("*"):
        try:
            relative = path.relative_to(repo)
        except ValueError:
            continue

        if should_skip(relative) or not path.is_file():
            continue

        yield relative, path


def scan_git_health(repo: Path) -> GitHealth:
    code, inside = run_git(repo, ["rev-parse", "--is-inside-work-tree"])
    if code != 0 or inside != "true":
        return GitHealth(is_repo=False)

    _, branch = run_git(repo, ["branch", "--show-current"])
    _, status = run_git(repo, ["status", "--short"])
    status_lines = status.splitlines() if status else []

    return GitHealth(
        is_repo=True,
        branch=branch,
        changed_files=len(status_lines),
        status_lines=status_lines,
    )


def detect_languages(files: list[tuple[Path, Path]]) -> list[tuple[str, int]]:
    counts = Counter()

    for relative, _ in files:
        language = LANGUAGE_EXTENSIONS.get(relative.suffix.lower())
        if language:
            counts[language] += 1

    return counts.most_common(6)


def detect_project_type(repo: Path) -> str:
    if (repo / "pyproject.toml").exists() and (repo / "repo_signal").exists():
        return "Python CLI / repo intelligence toolkit"
    if (repo / "pyproject.toml").exists():
        return "Python project"
    if (repo / "package.json").exists() and (repo / "docs" / "index.html").exists():
        return "JavaScript / static web project"
    if (repo / "package.json").exists():
        return "JavaScript / Node project"
    if (repo / "docs" / "index.html").exists():
        return "GitHub Pages / static web project"
    if (repo / "bin").exists() or (repo / "tools").exists() or (repo / "scripts").exists():
        return "Command-line tools / automation"
    return "General repository"


def detect_entrypoints(repo: Path, files: list[tuple[Path, Path]]) -> list[str]:
    found = []

    for relative, path in files:
        path_text = relative.as_posix()
        if relative.name in ENTRYPOINT_NAMES:
            found.append(path_text)
            continue
        if path_text.startswith(("bin/", "scripts/", "tools/")):
            found.append(path_text)
            continue
        if "launcher" in path_text.lower() or "command-mode" in path_text.lower():
            found.append(path_text)
            continue
        if path.suffix.lower() in {".sh", ".bash", ".zsh"}:
            try:
                first_line = path.read_text(encoding="utf-8", errors="ignore").splitlines()[0]
            except (IndexError, OSError):
                first_line = ""
            if first_line.startswith("#!"):
                found.append(path_text)

    return sorted(dict.fromkeys(found))[:10]


def detect_tooling(repo: Path) -> list[str]:
    found = []

    for target, label in TOOLING_FILES.items():
        if (repo / target).exists():
            found.append(label)

    return found


def top_directories(files: list[tuple[Path, Path]]) -> list[tuple[str, int]]:
    counts = Counter()

    for relative, _ in files:
        top = relative.parts[0] if len(relative.parts) > 1 else "."
        counts[top] += 1

    return counts.most_common(8)


def repo_size(files: list[tuple[Path, Path]]) -> tuple[int, float]:
    total_bytes = 0

    for _, path in files:
        try:
            total_bytes += path.stat().st_size
        except OSError:
            continue

    return len(files), total_bytes / 1024 / 1024


def suggest_focus_areas(repo: Path, summary: RepoSummary) -> list[str]:
    focus = []

    if not (repo / "README.md").exists():
        focus.append("Create README.md with purpose, install, usage, and examples")
    if not (repo / "LICENSE").exists():
        focus.append("Add a LICENSE file")
    if not (repo / ".gitignore").exists():
        focus.append("Add .gitignore for local and build artifacts")
    if not (repo / "tests").exists():
        focus.append("Add focused tests for the main command surface")
    if not summary.key_entrypoints:
        focus.append("Document or add a clear executable entrypoint")
    if summary.git.changed_files:
        focus.append("Review current working tree changes before release or demo")
    if "GitHub Pages docs" not in summary.detected_tooling:
        focus.append("Add or clarify whether a public docs/demo page is needed")

    if not focus:
        focus.append("Foundation looks healthy; improve analysis depth next")

    return focus[:6]


def scan_repository(repo_path: Union[Path, str]) -> RepoSummary:
    repo = Path(repo_path).expanduser().resolve()
    files = list(iter_repo_files(repo))
    git = scan_git_health(repo)
    file_count, size_mb = repo_size(files)

    partial = RepoSummary(
        path=repo,
        project_type=detect_project_type(repo),
        languages=detect_languages(files),
        key_entrypoints=detect_entrypoints(repo, files),
        git=git,
        repo_size_files=file_count,
        repo_size_mb=size_mb,
        top_directories=top_directories(files),
        detected_tooling=detect_tooling(repo),
        focus_areas=[],
    )
    partial.focus_areas = suggest_focus_areas(repo, partial)

    return partial
