from pathlib import Path
import re
import shutil
import subprocess
from typing import Optional


MAX_RANKED_FILES = 5
MAX_SNIPPET_LINES = 120
SNIPPET_CONTEXT_LINES = 18

WEIGHTS = {
    "filename_exact": 10,
    "filename_contains": 7,
    "path_contains_keyword": 6,
    "keyword_frequency": 4,
    "git_modified": 8,
    "recent_commit": 5,
    "path_priority": 7,
    "shell_entrypoint": 8,
    "symbol_match": 9,
    "file_size_penalty": -3,
    "docs_penalty": -2,
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
    "build",
    "dist",
    "node_modules",
    "venv",
}

SKIP_NAMES = {
    ".DS_Store",
}

TOPIC_PATH_PRIORITIES = {
    "routing": {
        "dispatch",
        "launcher",
        "launchers",
        "command-mode",
        "menu",
        "menus",
        "route",
        "router",
    },
    "dispatch": {
        "dispatch",
        "launcher",
        "command-mode",
        "menu",
        "menus",
        "route",
        "router",
    },
    "release": {
        ".github",
        "action",
        "actions",
        "changelog",
        "release",
        "version",
    },
    "doctor": {
        "doctor",
        "health",
        "menu",
        "menus",
        "release-check",
    },
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


def should_skip(path: Path) -> bool:
    return any(
        part in SKIP_DIRS
        or part in SKIP_NAMES
        or part.endswith(".egg-info")
        for part in path.parts
    )


def to_repo_relative(repo_path: Path, path_text: str) -> str:
    repo_path = repo_path.resolve()
    path = Path(path_text)
    if not path.is_absolute():
        path = repo_path / path

    try:
        return path.resolve().relative_to(repo_path).as_posix()
    except ValueError:
        return path_text


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def discover_all_files(repo_path: Path) -> list[str]:
    files = []

    for path in repo_path.rglob("*"):
        try:
            relative = path.relative_to(repo_path)
        except ValueError:
            continue

        if should_skip(relative) or not path.is_file():
            continue

        files.append(relative.as_posix())

    return sorted(files)


def find_candidate_files(repo_path: Path, keywords: list[str]) -> set[str]:
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
            for file_path in discover_all_files(repo_path):
                if keyword in read_text(repo_path / file_path).lower():
                    matches.add(file_path)

    return matches


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


def recently_committed_files(repo_path: Path, limit: int = 40) -> set[str]:
    output = run(
        ["git", "log", "--name-only", "--pretty=format:", f"-n{limit}"],
        cwd=repo_path,
    )
    return {line.strip() for line in output.splitlines() if line.strip()}


def topic_priority_terms(keywords: list[str]) -> set[str]:
    terms = set()
    for keyword in keywords:
        terms.update(TOPIC_PATH_PRIORITIES.get(keyword, set()))
    return terms


def count_keyword_hits(text_lower: str, keywords: list[str]) -> dict[str, int]:
    hits = {}
    for keyword in keywords:
        count = len(re.findall(rf"\b{re.escape(keyword)}\b", text_lower))
        if count:
            hits[keyword] = count
    return hits


def has_symbol_match(text_lower: str, keywords: list[str]) -> list[str]:
    matches = []
    for keyword in keywords:
        pattern = rf"^\s*(def|class|function)\s+[\w-]*{re.escape(keyword)}[\w-]*"
        shell_pattern = rf"^\s*[\w-]*{re.escape(keyword)}[\w-]*\s*\(\)\s*\{{"
        if re.search(pattern, text_lower, flags=re.MULTILINE) or re.search(shell_pattern, text_lower, flags=re.MULTILINE):
            matches.append(keyword)
    return matches


def is_docs_path(path_lower: str) -> bool:
    return (
        path_lower.endswith(".md")
        or path_lower.startswith("docs/")
        or "/docs/" in path_lower
        or "readme" in path_lower
    )


def is_shell_entrypoint(file_path: str, text: str) -> bool:
    path_lower = file_path.lower()
    if not path_lower.endswith((".sh", ".bash", ".zsh")):
        return False
    return text.startswith("#!") or "/bin/" in path_lower or "launcher" in path_lower


def score_file(
    repo_path: Path,
    file_path: str,
    keywords: list[str],
    modified: set[str],
    recent: set[str],
    mode: str,
) -> dict:
    full_path = repo_path / file_path
    text = read_text(full_path)
    text_lower = text.lower()
    path_lower = file_path.lower()
    name_lower = full_path.name.lower()
    priority_terms = topic_priority_terms(keywords)

    score = 0
    reasons = []
    signals = {}

    exact_filename_hits = [
        keyword for keyword in keywords
        if name_lower == keyword or name_lower.startswith(f"{keyword}.")
    ]
    if exact_filename_hits:
        value = WEIGHTS["filename_exact"] * len(exact_filename_hits)
        score += value
        signals["filename_exact"] = value
        reasons.append(f"filename exact match: {', '.join(exact_filename_hits)}")

    filename_hits = [keyword for keyword in keywords if keyword in name_lower and keyword not in exact_filename_hits]
    if filename_hits:
        value = WEIGHTS["filename_contains"] * len(filename_hits)
        score += value
        signals["filename_contains"] = value
        reasons.append(f"filename contains: {', '.join(filename_hits)}")

    path_keyword_hits = [keyword for keyword in keywords if keyword in path_lower]
    if path_keyword_hits:
        value = WEIGHTS["path_contains_keyword"] * len(path_keyword_hits)
        score += value
        signals["path_contains_keyword"] = value
        reasons.append(f"path contains keyword: {', '.join(path_keyword_hits)}")

    keyword_hits = count_keyword_hits(text_lower, keywords)
    if keyword_hits:
        value = min(sum(keyword_hits.values()) * WEIGHTS["keyword_frequency"], 24)
        score += value
        signals["keyword_frequency"] = value
        top_hits = sorted(keyword_hits.items(), key=lambda item: item[1], reverse=True)[:4]
        reasons.append(
            "keyword frequency: "
            + ", ".join(f"{keyword}={count}" for keyword, count in top_hits)
        )

    symbols = has_symbol_match(text_lower, keywords)
    if symbols:
        value = WEIGHTS["symbol_match"]
        score += value
        signals["symbol_match"] = value
        reasons.append(f"symbol match: {', '.join(symbols)}")

    path_priority_hits = sorted(term for term in priority_terms if term in path_lower)
    if path_priority_hits:
        value = WEIGHTS["path_priority"]
        score += value
        signals["path_priority"] = value
        reasons.append(f"path priority: {', '.join(path_priority_hits[:4])}")

    if file_path in modified and mode in {"debug", "review"}:
        value = WEIGHTS["git_modified"]
        score += value
        signals["git_modified"] = value
        reasons.append("git modified")

    if file_path in recent:
        value = WEIGHTS["recent_commit"]
        score += value
        signals["recent_commit"] = value
        reasons.append("recent commit")

    if is_shell_entrypoint(file_path, text):
        value = WEIGHTS["shell_entrypoint"]
        score += value
        signals["shell_entrypoint"] = value
        reasons.append("shell entrypoint")

    try:
        line_count = len(text.splitlines())
    except MemoryError:
        line_count = MAX_SNIPPET_LINES + 1

    if line_count > 500:
        value = WEIGHTS["file_size_penalty"]
        score += value
        signals["file_size_penalty"] = value
        reasons.append("large file penalty")

    if is_docs_path(path_lower) and not any(keyword in {"readme", "docs", "documentation"} for keyword in keywords):
        value = WEIGHTS["docs_penalty"]
        score += value
        signals["docs_penalty"] = value
        reasons.append("docs penalty")

    if "test" in path_lower and mode not in {"review", "debug"}:
        score -= 4
        signals["test_penalty"] = -4
        reasons.append("test file penalty")

    return {
        "path": file_path,
        "score": score,
        "reasons": reasons,
        "signals": signals,
        "summary": summarize_file(file_path, keywords, reasons),
    }


def rank_relevant_files(repo_path: Path, keywords: list[str], mode: str = "explain") -> list[dict]:
    repo_path = repo_path.resolve()
    modified = modified_files(repo_path)
    recent = recently_committed_files(repo_path)
    candidates = set(find_candidate_files(repo_path, keywords))

    priority_terms = topic_priority_terms(keywords)
    if priority_terms:
        for file_path in discover_all_files(repo_path):
            path_lower = file_path.lower()
            if any(term in path_lower for term in priority_terms):
                candidates.add(file_path)

    if mode in {"debug", "review"}:
        candidates.update(path for path in modified if (repo_path / path).exists())

    ranked = [
        score_file(repo_path, file_path, keywords, modified, recent, mode)
        for file_path in candidates
        if not should_skip(Path(file_path))
    ]
    ranked = [item for item in ranked if item["score"] > 0]

    return sorted(ranked, key=lambda item: (-item["score"], item["path"]))[:MAX_RANKED_FILES]


def summarize_file(file_path: str, keywords: list[str], reasons: list[str]) -> str:
    path_lower = file_path.lower()
    keyword_text = ", ".join(keywords[:4]) if keywords else "the question"

    if "test" in path_lower:
        role = "Test coverage or expected behavior"
    elif "release" in path_lower or "changelog" in path_lower:
        role = "Release or versioning workflow"
    elif "doctor" in path_lower or "health" in path_lower:
        role = "Diagnostics or health-check workflow"
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
    elif path_lower.endswith(".ps1"):
        role = "PowerShell workflow"
    elif "readme" in path_lower or path_lower.endswith(".md"):
        role = "Documentation and project explanation"
    else:
        role = "Relevant repository file"

    reason_text = "; ".join(reasons[:3]) if reasons else f"matches {keyword_text}"
    return f"{role}. Selected because {reason_text}."


def line_score(line: str, keywords: list[str]) -> int:
    line_lower = line.lower()
    score = 0
    for keyword in keywords:
        if keyword in line_lower:
            score += 4
    if re.match(r"^\s*(def|class|function)\s+", line_lower):
        score += 3
    if re.match(r"^\s*[\w-]+\s*\(\)\s*\{", line_lower):
        score += 3
    if "case " in line_lower or " if " in f" {line_lower} " or "elif " in line_lower:
        score += 1
    return score


def merge_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not ranges:
        return []

    merged = []
    for start, end in sorted(ranges):
        if not merged or start > merged[-1][1] + 1:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)

    return [(start, end) for start, end in merged]


def read_relevant_snippet(path: Path, keywords: list[str], max_lines: int = MAX_SNIPPET_LINES) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return "[unable to read file]"

    if not lines:
        return ""

    scored = [
        (index, line_score(line, keywords))
        for index, line in enumerate(lines)
    ]
    best = [index for index, score in sorted(scored, key=lambda item: item[1], reverse=True) if score > 0][:4]

    if not best:
        return "\n".join(lines[:max_lines]).rstrip()

    ranges = []
    for index in best:
        start = max(0, index - SNIPPET_CONTEXT_LINES)
        end = min(len(lines), index + SNIPPET_CONTEXT_LINES + 1)
        ranges.append((start, end))

    output = []
    used = 0
    for start, end in merge_ranges(ranges):
        block = lines[start:end]
        remaining = max_lines - used
        if remaining <= 0:
            break
        block = block[:remaining]
        output.append(f"# lines {start + 1}-{start + len(block)}")
        output.extend(block)
        used += len(block)
        if used >= max_lines:
            break

    return "\n...\n".join(output).rstrip()
