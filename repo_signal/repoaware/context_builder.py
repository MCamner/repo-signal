from pathlib import Path
import re
import shutil
import subprocess
from typing import Optional, Union


MAX_FILES = 10
MAX_SNIPPET_LINES = 160
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

PATH_BOOST_TERMS = {
    "dispatch",
    "launcher",
    "launchers",
    "menu",
    "menus",
    "route",
    "router",
    "routing",
}

COMMON_WORDS = {
    "a",
    "an",
    "and",
    "does",
    "first",
    "how",
    "i",
    "in",
    "is",
    "it",
    "of",
    "should",
    "the",
    "this",
    "to",
    "what",
    "work",
    "works",
}

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
    keywords = [word for word in words if len(word) > 1 and word not in COMMON_WORDS]
    return list(dict.fromkeys(keywords))


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


def find_candidate_files(repo_path: Path, keywords: list[str]) -> list[str]:
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

    return sorted(matches)


def modified_files(repo_path: Path) -> set[str]:
    output = run(["git", "status", "--short"], cwd=repo_path)
    files = set()

    for line in output.splitlines():
        path = line[3:].strip()
        if not path:
            continue
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        files.add(path)

    return files


def read_text_for_scoring(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def score_file(repo_path: Path, file_path: str, keywords: list[str], modified: set[str], mode: str) -> dict:
    full_path = repo_path / file_path
    text = read_text_for_scoring(full_path)
    text_lower = text.lower()
    path_lower = file_path.lower()
    name_lower = full_path.name.lower()

    score = 0
    reasons = []

    filename_hits = [keyword for keyword in keywords if keyword in name_lower]
    if filename_hits:
        boost = 5 * len(filename_hits)
        score += boost
        reasons.append(f"filename match: {', '.join(filename_hits)}")

    path_hits = sorted(term for term in PATH_BOOST_TERMS if term in path_lower)
    if path_hits:
        score += 4
        reasons.append(f"path signal: {', '.join(path_hits[:3])}")

    keyword_hits = {}
    for keyword in keywords:
        count = len(re.findall(rf"\b{re.escape(keyword)}\b", text_lower))
        if count:
            keyword_hits[keyword] = count

    if keyword_hits:
        boost = min(sum(keyword_hits.values()) * 3, 18)
        score += boost
        top_hits = sorted(keyword_hits.items(), key=lambda item: item[1], reverse=True)[:4]
        reasons.append(
            "keyword hits: "
            + ", ".join(f"{keyword}={count}" for keyword, count in top_hits)
        )

    exact_symbols = [
        keyword for keyword in keywords
        if re.search(rf"^\s*(def|class|function)\s+.*{re.escape(keyword)}", text_lower, flags=re.MULTILINE)
    ]
    if exact_symbols:
        score += 7
        reasons.append(f"symbol match: {', '.join(exact_symbols)}")

    if file_path in modified and mode in {"debug", "review"}:
        score += 5
        reasons.append("modified file")

    if "test" in path_lower and mode != "review":
        score -= 4

    return {
        "path": file_path,
        "score": score,
        "reasons": reasons,
        "summary": summarize_file(file_path, keywords, reasons),
    }


def rank_relevant_files(repo_path: Path, keywords: list[str], mode: str = DEFAULT_MODE) -> list[dict]:
    modified = modified_files(repo_path)
    candidates = set(find_candidate_files(repo_path, keywords))
    if mode in {"debug", "review"}:
        candidates.update(path for path in modified if (repo_path / path).exists())

    ranked = [
        score_file(repo_path, file_path, keywords, modified, mode)
        for file_path in candidates
        if not should_skip(Path(file_path))
    ]
    ranked = [item for item in ranked if item["score"] > 0]

    return sorted(ranked, key=lambda item: (-item["score"], item["path"]))[:MAX_FILES]


def summarize_file(file_path: str, keywords: list[str], reasons: list[str]) -> str:
    path_lower = file_path.lower()
    keyword_text = ", ".join(keywords[:4]) if keywords else "the question"

    if "test" in path_lower:
        role = "Test coverage or expected behavior"
    elif "readme" in path_lower or path_lower.endswith(".md"):
        role = "Documentation and project explanation"
    elif "launcher" in path_lower or "launch" in path_lower:
        role = "Launcher or command entry point"
    elif "menu" in path_lower:
        role = "Menu or dispatch surface"
    elif "route" in path_lower or "dispatch" in path_lower:
        role = "Routing or dispatch logic"
    elif path_lower.endswith(".py"):
        role = "Python implementation"
    elif path_lower.endswith((".sh", ".zsh", ".bash")):
        role = "Shell workflow"
    else:
        role = "Relevant repository file"

    reason_text = "; ".join(reasons[:3]) if reasons else f"matches {keyword_text}"
    return f"{role}. Selected because {reason_text}."


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

    keywords = extract_keywords(question)
    files = rank_relevant_files(repo, keywords, mode)
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
        output.append("<snippet>")
        output.append(read_file_snippet(full_path))
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
        lines.append("")
        lines.append("```text")
        lines.append(read_file_snippet(full_path))
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
