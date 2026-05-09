from pathlib import Path
from typing import List

from repo_signal.core.models import Repository, Signal
from repo_signal.repoaware.ranking import (
    extract_keywords,
    rank_relevant_files,
    read_relevant_snippet,
    summarize_file,
)


def rank_files(repo: Repository, question: str, mode: str = "explain") -> List[Signal]:
    keywords = extract_keywords(question)
    ranked = rank_relevant_files(repo.path, keywords, mode=mode)
    repo.signals = [
        Signal(
            file_path=item["path"],
            score=int(item["score"]),
            reasons=list(item.get("reasons", [])),
        )
        for item in ranked
    ]
    return repo.signals


def _format_git_status(repo: Repository) -> str:
    if not repo.git.is_repo:
        return "not a git repository"
    return repo.git.status or "clean"


def _signal_summary(signal: Signal, keywords: List[str]) -> str:
    return summarize_file(signal.file_path, keywords, signal.reasons)


def build_focused_context(
    repo: Repository,
    question: str,
    signals: List[Signal],
    mode: str = "explain",
) -> str:
    keywords = extract_keywords(question)
    lines = []

    lines.append("# RepoAware Context")
    lines.append("")
    lines.append("## Repository")
    lines.append("")
    lines.append(f"- Name: `{repo.name}`")
    lines.append(f"- Path: `{repo.path}`")
    lines.append(f"- Project type: {repo.project_type}")
    lines.append(f"- Mode: `{mode}`")
    lines.append(f"- Files scanned: `{repo.repo_size_files}`")
    lines.append(f"- Languages: `{repo.languages if repo.languages else {}}`")
    lines.append(f"- Entry points: `{', '.join(repo.entrypoints[:8]) if repo.entrypoints else 'none detected'}`")
    lines.append(f"- Top directories: `{', '.join(repo.top_directories[:8]) if repo.top_directories else 'none detected'}`")
    lines.append(f"- Graph edges: `{len(repo.graph.edges)}`")
    lines.append("")
    lines.append("## Git")
    lines.append("")
    lines.append(f"- Branch: `{repo.git.branch or 'unknown'}`")
    lines.append(f"- Changed files: `{repo.git.changed_files}`")
    lines.append("")
    lines.append("```text")
    lines.append(_format_git_status(repo))
    lines.append("```")
    lines.append("")
    lines.append("## Question")
    lines.append("")
    lines.append(question)
    lines.append("")
    lines.append("## Ranked Files")
    lines.append("")

    if not signals:
        lines.append("- No ranked files found.")
    else:
        for signal in signals:
            summary = _signal_summary(signal, keywords)
            lines.append(f"- `{signal.file_path}` score `{signal.score}` - {summary}")

    graph_edges = []
    selected_files = {signal.file_path for signal in signals}
    for edge in repo.graph.edges:
        if edge.source in selected_files or edge.target in selected_files:
            graph_edges.append(edge)

    lines.append("")
    lines.append("## Structural Relations")
    lines.append("")
    if graph_edges:
        for edge in graph_edges[:20]:
            lines.append(f"- `{edge.source}` -> `{edge.target}` ({edge.relation})")
    else:
        lines.append("- No graph edges connected to selected files.")

    for signal in signals:
        full_path = repo.path / Path(signal.file_path)
        lines.append("")
        lines.append(f"## File: {signal.file_path}")
        lines.append("")
        lines.append(f"Score: `{signal.score}`")
        lines.append("")
        lines.append(f"Summary: {_signal_summary(signal, keywords)}")
        lines.append("")
        lines.append("Reasons:")
        if signal.reasons:
            for reason in signal.reasons:
                lines.append(f"- {reason}")
        else:
            lines.append("- Ranked from repository signals")
        lines.append("")
        lines.append("Snippet:")
        lines.append("")
        lines.append("```text")
        lines.append(read_relevant_snippet(full_path, keywords))
        lines.append("```")

    return "\n".join(lines)
