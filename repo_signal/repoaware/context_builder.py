from pathlib import Path
import re
import shutil
import subprocess
from typing import Optional, Union


MAX_FILES = 10
MAX_SNIPPET_LINES = 160

SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    "node_modules",
    "venv",
}

SKIP_NAMES = {
    ".DS_Store",
}


def run(cmd: list[str], cwd: Optional[Path] = None) -> str:
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


def extract_keywords(question: str) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9_-]+", question.lower())
    return list(dict.fromkeys(words))


def to_repo_relative(repo_path: Path, path_text: str) -> str:
    path = Path(path_text)
    if not path.is_absolute():
        path = repo_path / path

    try:
        return path.resolve().relative_to(repo_path).as_posix()
    except ValueError:
        return path_text


def should_skip(path: Path) -> bool:
    return any(
        part in SKIP_DIRS
        or part in SKIP_NAMES
        or part.endswith(".egg-info")
        for part in path.parts
    )


def find_files_with_python(repo_path: Path, keyword: str) -> list[str]:
    matches = []

    for path in repo_path.rglob("*"):
        try:
            relative = path.relative_to(repo_path)
        except ValueError:
            continue

        if should_skip(relative) or not path.is_file():
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        if keyword in text.lower():
            matches.append(relative.as_posix())

    return matches


def find_relevant_files(repo_path: Path, keywords: list[str]) -> list[str]:
    matches = set()

    for keyword in keywords:
        if shutil.which("rg"):
            output = run(
                ["rg", "-l", "--glob", "!{.git,node_modules,.venv,venv,__pycache__,*.egg-info}/**", keyword, "."],
                cwd=repo_path,
            )

            for line in output.splitlines():
                clean = line.strip()
                if clean:
                    matches.add(to_repo_relative(repo_path, clean))
        else:
            matches.update(find_files_with_python(repo_path, keyword))

    return sorted(matches)[:MAX_FILES]


def build_repo_tree(repo_path: Path) -> str:
    output = run(
        ["find", ".", "-maxdepth", "2"],
        cwd=repo_path,
    )

    lines = []
    for line in output.splitlines():
        clean = line.strip()
        if not clean:
            continue
        if should_skip(Path(clean)):
            continue
        lines.append(clean)

    return "\n".join(lines[:80])


def build_git_context(repo_path: Path) -> tuple[str, str]:
    branch = run(
        ["git", "branch", "--show-current"],
        cwd=repo_path,
    )

    status = run(
        ["git", "status", "--short"],
        cwd=repo_path,
    )

    return branch, status


def read_file_snippet(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8") as file:
            lines = file.readlines()

        return "".join(lines[:MAX_SNIPPET_LINES]).rstrip()
    except Exception:
        return "[unable to read file]"


def build_context(repo_path: Union[str, Path], question: str) -> str:
    repo = Path(repo_path).expanduser().resolve()

    keywords = extract_keywords(question)
    files = find_relevant_files(repo, keywords)
    branch, status = build_git_context(repo)
    tree = build_repo_tree(repo)

    output = []

    output.append("<repo>")
    output.append(f"name: {repo.name}")
    output.append(f"path: {repo}")
    output.append("</repo>\n")

    output.append("<git>")
    output.append(f"branch: {branch}")
    output.append("status:")
    output.append(status)
    output.append("</git>\n")

    output.append("<question>")
    output.append(question)
    output.append("</question>\n")

    output.append("<tree>")
    output.append(tree)
    output.append("</tree>\n")

    output.append("<relevant_files>")

    if files:
        output.extend(files)
    else:
        output.append("No matches found.")

    output.append("</relevant_files>\n")

    for file_path in files:
        full_path = repo / file_path

        output.append(f'<file path="{file_path}">')
        output.append(read_file_snippet(full_path))
        output.append("</file>\n")

    return "\n".join(output)
