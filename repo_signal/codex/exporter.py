from dataclasses import dataclass
from pathlib import Path
import re
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


@dataclass
class SkillCreateResult:
    name: str
    path: Path


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
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", name):
        raise SkillExportError(
            "Invalid skill name: use lowercase letters, numbers, hyphens, or underscores"
        )
    return name


def default_skill_description(name: str) -> str:
    label = name.replace("-", " ").replace("_", " ")
    return f"Use when working on {label} tasks that need a repeatable Codex workflow."


def skill_template(name: str, description: str) -> str:
    title = " ".join(part.capitalize() for part in name.replace("_", "-").split("-"))

    return f"""---
name: {name}
description: {description}
---

# {title}

Use this skill when the user asks for work that should follow the `{name}` workflow.

## When to use

Use this skill when:

- the task matches this workflow
- repeatable steps matter
- repo-specific context should guide the answer

## Workflow

1. Inspect the relevant files before acting.
2. Identify the user's goal and the repo constraints.
3. Make the smallest useful change or recommendation.
4. Verify important behavior with a lightweight check when possible.
5. Report what changed, what was verified, and what remains uncertain.

## Output style

Be concise, practical, and grounded in the files or evidence available.

Do not invent repo details. If something cannot be confirmed, say so briefly and continue with the best grounded next step.
"""


def create_codex_skill(
    name: str,
    repo_root: Optional[Path] = None,
    description: Optional[str] = None,
) -> SkillCreateResult:
    root = repo_root_from_path(repo_root)
    skill_name = validate_skill_name(name)
    target = skills_root(root) / skill_name

    if target.exists():
        raise SkillExportError(f"Skill already exists: {skill_name}")

    try:
        target.mkdir(parents=True)
        skill_description = description or default_skill_description(skill_name)
        (target / "SKILL.md").write_text(
            skill_template(skill_name, skill_description),
            encoding="utf-8",
        )
    except OSError as exc:
        raise SkillExportError(f"Could not create skill at {target}: {exc}") from exc

    return SkillCreateResult(name=skill_name, path=target)


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
