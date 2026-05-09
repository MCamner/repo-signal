from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import List, Optional


class SkillExportError(RuntimeError):
    """Raised when a Codex skill cannot be exported."""


@dataclass
class SkillExportResult:
    name: str
    source: Path
    target: Path
    files: int


def repo_root_from_path(path: Optional[Path] = None) -> Path:
    return (path or Path.cwd()).expanduser().resolve()


def skills_root(repo_root: Path) -> Path:
    return repo_root / "skills"


def available_skills(repo_root: Path) -> List[str]:
    root = skills_root(repo_root)
    if not root.exists():
        return []

    names = []
    for path in root.iterdir():
        if path.is_dir() and (path / "SKILL.md").exists():
            names.append(path.name)

    return sorted(names)


def validate_skill_name(name: str) -> str:
    if not name or "/" in name or "\\" in name or name in {".", ".."}:
        raise SkillExportError(f"Invalid skill name: {name}")
    return name


def resolve_source(repo_root: Path, name: str) -> Path:
    name = validate_skill_name(name)
    source = skills_root(repo_root) / name

    if not (source / "SKILL.md").exists():
        names = ", ".join(available_skills(repo_root)) or "none"
        raise SkillExportError(f"Unknown skill: {name}. Available skills: {names}")

    return source


def default_target_root(repo_root: Path, local: bool = False) -> Path:
    if local:
        return repo_root / ".codex" / "skills"
    return Path.home() / ".codex" / "skills"


def count_files(path: Path) -> int:
    return sum(1 for item in path.rglob("*") if item.is_file())


def export_codex_skill(
    name: str,
    repo_root: Optional[Path] = None,
    target_root: Optional[Path] = None,
    local: bool = False,
) -> SkillExportResult:
    root = repo_root_from_path(repo_root)
    source = resolve_source(root, name)
    destination_root = (target_root.expanduser().resolve() if target_root else default_target_root(root, local=local))
    target = destination_root / validate_skill_name(name)

    try:
        destination_root.mkdir(parents=True, exist_ok=True)
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)
    except OSError as exc:
        raise SkillExportError(f"Could not export skill to {target}: {exc}") from exc

    return SkillExportResult(
        name=name,
        source=source,
        target=target,
        files=count_files(target),
    )
