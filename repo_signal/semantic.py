import argparse
from pathlib import Path
import sys
from typing import List, Optional

from repo_signal.core.models import Repository
from repo_signal.vectorstore.chroma_store import ChromaUnavailableError, build_default_store, tokenize
from repo_signal.vectorstore.chunks import SymbolChunk, build_symbol_chunks


def lexical_score(query: str, chunk: SymbolChunk) -> int:
    query_tokens = set(tokenize(query))
    text_tokens = tokenize(chunk.text)
    score = 0

    for token in query_tokens:
        score += text_tokens.count(token) * 3
        if token in chunk.symbol.lower():
            score += 8
        if token in chunk.file_path.lower():
            score += 4

    if chunk.kind in {"function", "shell_function"}:
        score += 1

    return score


def lexical_search(chunks: List[SymbolChunk], query: str, limit: int = 5) -> List[dict]:
    ranked = []

    for chunk in chunks:
        score = lexical_score(query, chunk)
        if score <= 0:
            continue
        ranked.append({"chunk": chunk, "score": score})

    return sorted(ranked, key=lambda item: (-item["score"], item["chunk"].file_path, item["chunk"].line))[:limit]


def format_lexical_results(repo: Repository, query: str, matches: List[dict]) -> str:
    lines = []
    lines.append("# Semantic Signal Report")
    lines.append("")
    lines.append(f"Repo: `{repo.name}`")
    lines.append(f"Query: {query}")
    lines.append(f"Symbols indexed: `{len(repo.symbols)}`")
    lines.append("Mode: `symbol chunks / lexical fallback`")
    lines.append("")
    lines.append("## Matches")
    lines.append("")

    if not matches:
        lines.append("- No symbol chunks matched.")
        return "\n".join(lines)

    for item in matches:
        chunk = item["chunk"]
        lines.append(f"- `{chunk.symbol}` ({chunk.kind}) score `{item['score']}`")
        lines.append(f"  - file: `{chunk.file_path}:{chunk.line}`")
        lines.append(f"  - language: `{chunk.language}`")
        lines.append(f"  - summary: {chunk.summary}")

    return "\n".join(lines)


def format_chroma_results(repo: Repository, query: str, matches: List[dict], store_path: Path) -> str:
    lines = []
    lines.append("# Semantic Signal Report")
    lines.append("")
    lines.append(f"Repo: `{repo.name}`")
    lines.append(f"Query: {query}")
    lines.append(f"Symbols indexed: `{len(repo.symbols)}`")
    lines.append("Mode: `chroma symbol chunks`")
    lines.append(f"Store: `{store_path}`")
    lines.append("Collection: `symbols`")
    lines.append("")
    lines.append("## Matches")
    lines.append("")

    if not matches:
        lines.append("- No symbol chunks matched.")
        return "\n".join(lines)

    for match in matches:
        metadata = match["metadata"]
        lines.append(f"- `{metadata.get('symbol')}` ({metadata.get('kind')}) distance `{match['distance']:.4f}`")
        lines.append(f"  - file: `{metadata.get('file')}:{metadata.get('line')}`")
        lines.append(f"  - language: `{metadata.get('language')}`")

    return "\n".join(lines)


def semantic_repo(
    repo_path: Path,
    query: str,
    limit: int = 5,
    use_chroma: bool = False,
    include_tests: bool = False,
    store_path: Optional[Path] = None,
) -> str:
    repo = Repository.load(repo_path)
    chunks = build_symbol_chunks(repo, include_tests=include_tests)

    if use_chroma:
        store = build_default_store(repo.path, store_path=store_path)
        store.reset()
        store.upsert_chunks(chunks)
        return format_chroma_results(repo, query, store.query(query, limit=limit), store.path)

    return format_lexical_results(repo, query, lexical_search(chunks, query, limit=limit))


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="repo-signal semantic",
        description="Search smart symbol chunks for semantic repository recall.",
    )
    parser.add_argument("query", nargs="+", help="Semantic query.")
    parser.add_argument("--limit", type=int, default=5, help="Maximum matches to print.")
    parser.add_argument("--use-chroma", action="store_true", help="Use local Chroma store instead of lexical fallback.")
    parser.add_argument("--include-tests", action="store_true", help="Include test symbols in semantic memory.")
    parser.add_argument(
        "--store-path",
        type=Path,
        default=None,
        help="Override Chroma store path. Defaults to ~/.repo-signal/vectorstores/<repo>.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    query = " ".join(args.query)

    try:
        print(
            semantic_repo(
                repo_path=Path.cwd(),
                query=query,
                limit=args.limit,
                use_chroma=args.use_chroma,
                include_tests=args.include_tests,
                store_path=args.store_path,
            )
        )
    except ChromaUnavailableError as exc:
        print(f"repo-signal semantic: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
