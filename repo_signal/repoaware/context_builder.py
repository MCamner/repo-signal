from pathlib import Path
import subprocess
from typing import Optional, Union

from repo_signal.repoaware.ranking import (
    extract_keywords as ranking_extract_keywords,
    rank_relevant_files as ranking_rank_relevant_files,
    read_relevant_snippet,
    should_skip,
)


DEFAULT_MODE = "explain"
DEFAULT_FORMAT = "xml"
VALID_MODES = {"debug", "architect", "explain", "review"}
VALID_FORMATS = {"xml", "markdown", "claude"}

MODE_INSTRUCTIONS = {
    "debug": [
        "Focus on errors, routing, stack flow, and recently modified files.",
        "Prefer concrete execution paths over broad architecture commentary.",
        "Call out likely failure points and the files to inspect first.",
    ],
    "architect": [
        "Focus on structure, modularity, coupling, boundaries, and roadmap implications.",
        "Explain how the relevant files fit together.",
        "Prefer system-level tradeoffs over line-by-line debugging.",
    ],
    "explain": [
        "Focus on a clear explanation of how the requested behavior works.",
        "Use the selected files as grounding and avoid unsupported guesses.",
        "Prefer concise walkthroughs and name the most important files first.",
    ],
    "review": [
        "Focus on risks, maintainability, shell pitfalls, edge cases, and test gaps.",
        "Prioritize findings by severity and reference files directly.",
        "Avoid cosmetic suggestions unless they affect readability or correctness.",
    ],
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
    return ranking_extract_keywords(question)


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

        return "".join(lines[:160]).rstrip()
    except Exception:
        return "[unable to read file]"


def validate_mode(mode: str) -> str:
    if mode not in VALID_MODES:
        raise ValueError(f"Unknown mode: {mode}")
    return mode


def validate_format(output_format: str) -> str:
    if output_format not in VALID_FORMATS:
        raise ValueError(f"Unknown format: {output_format}")
    return output_format


def build_context_data(repo_path: Union[str, Path], question: str, mode: str = DEFAULT_MODE) -> dict:
    repo = Path(repo_path).expanduser().resolve()
    mode = validate_mode(mode)

    keywords = ranking_extract_keywords(question)
    files = ranking_rank_relevant_files(repo, keywords, mode)
    branch, status = build_git_context(repo)
    tree = build_repo_tree(repo)

    return {
        "repo": repo,
        "mode": mode,
        "instructions": MODE_INSTRUCTIONS[mode],
        "question": question,
        "keywords": keywords,
        "branch": branch,
        "status": status,
        "tree": tree,
        "files": files,
    }


def format_xml(data: dict) -> str:
    repo = data["repo"]

    output = []

    output.append("<repoaware>")

    output.append("<repo>")
    output.append(f"name: {repo.name}")
    output.append(f"path: {repo}")
    output.append("</repo>\n")

    output.append("<mode>")
    output.append(data["mode"])
    output.append("</mode>\n")

    output.append("<instructions>")
    for instruction in data["instructions"]:
        output.append(f"- {instruction}")
    output.append("</instructions>\n")

    output.append("<git>")
    output.append(f"branch: {data['branch']}")
    output.append("status:")
    output.append(data["status"])
    output.append("</git>\n")

    output.append("<question>")
    output.append(data["question"])
    output.append("</question>\n")

    output.append("<keywords>")
    output.append(", ".join(data["keywords"]) if data["keywords"] else "none")
    output.append("</keywords>\n")

    output.append("<tree>")
    output.append(data["tree"])
    output.append("</tree>\n")

    output.append("<relevant_files>")

    if data["files"]:
        for file_info in data["files"]:
            output.append(f"- {file_info['path']} (score: {file_info['score']})")
    else:
        output.append("No matches found.")

    output.append("</relevant_files>\n")

    for file_info in data["files"]:
        file_path = file_info["path"]
        full_path = repo / file_path

        output.append(f'<file path="{file_path}">')
        output.append("<summary>")
        output.append(file_info["summary"])
        output.append("</summary>")
        output.append("<score>")
        output.append(str(file_info["score"]))
        output.append("</score>")
        output.append("<reasons>")
        for reason in file_info["reasons"]:
            output.append(f"- {reason}")
        output.append("</reasons>")
        output.append("<signals>")
        for signal, value in file_info.get("signals", {}).items():
            output.append(f"- {signal}: {value}")
        output.append("</signals>")
        output.append("<snippet>")
        output.append(read_relevant_snippet(full_path, data["keywords"]))
        output.append("</snippet>")
        output.append("</file>\n")

    output.append("</repoaware>")

    return "\n".join(output)


def format_markdown(data: dict) -> str:
    repo = data["repo"]
    lines = []

    lines.append("# RepoAware Context")
    lines.append("")
    lines.append(f"- Repo: `{repo.name}`")
    lines.append(f"- Path: `{repo}`")
    lines.append(f"- Mode: `{data['mode']}`")
    lines.append(f"- Branch: `{data['branch']}`")
    lines.append(f"- Question: {data['question']}")
    lines.append(f"- Keywords: `{', '.join(data['keywords']) if data['keywords'] else 'none'}`")
    lines.append("")
    lines.append("## Instructions")
    lines.append("")
    for instruction in data["instructions"]:
        lines.append(f"- {instruction}")
    lines.append("")
    lines.append("## Git Status")
    lines.append("")
    lines.append("```text")
    lines.append(data["status"])
    lines.append("```")
    lines.append("")
    lines.append("## Repo Tree")
    lines.append("")
    lines.append("```text")
    lines.append(data["tree"])
    lines.append("```")
    lines.append("")
    lines.append("## Relevant Files")
    lines.append("")

    if data["files"]:
        for file_info in data["files"]:
            lines.append(f"- `{file_info['path']}` score `{file_info['score']}` - {file_info['summary']}")
    else:
        lines.append("- No matches found.")

    for file_info in data["files"]:
        full_path = repo / file_info["path"]
        lines.append("")
        lines.append(f"## {file_info['path']}")
        lines.append("")
        lines.append(f"Summary: {file_info['summary']}")
        lines.append("")
        lines.append("Reasons:")
        for reason in file_info["reasons"]:
            lines.append(f"- {reason}")
        if file_info.get("signals"):
            lines.append("")
            lines.append("Signals:")
            for signal, value in file_info["signals"].items():
                lines.append(f"- {signal}: `{value}`")
        lines.append("")
        lines.append("```text")
        lines.append(read_relevant_snippet(full_path, data["keywords"]))
        lines.append("```")

    return "\n".join(lines)


def format_claude(data: dict) -> str:
    lines = []
    lines.append("<context>")
    lines.append(format_xml(data))
    lines.append("</context>")
    lines.append("")
    lines.append("<task>")
    lines.append("Answer the user question using only the repo context above where possible.")
    lines.append("Start with the highest-signal files and be explicit about uncertainty.")
    lines.append("</task>")
    return "\n".join(lines)


def build_context(
    repo_path: Union[str, Path],
    question: str,
    mode: str = DEFAULT_MODE,
    output_format: str = DEFAULT_FORMAT,
) -> str:
    output_format = validate_format(output_format)
    data = build_context_data(repo_path, question, mode)

    if output_format == "markdown":
        return format_markdown(data)
    if output_format == "claude":
        return format_claude(data)

    return format_xml(data)
    "should",
