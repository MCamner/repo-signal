import argparse
from pathlib import Path
import sys
from typing import List, Optional

from repo_signal.ai.providers.base import ProviderConfigurationError
from repo_signal.vectorstore.openai_store import OpenAIUploadResult, upload_repository_memory


def format_upload_result(result: OpenAIUploadResult) -> str:
    lines = []
    lines.append("# OpenAI Vector Store Upload")
    lines.append("")
    lines.append(f"Repo: `{result.repo_name}`")
    lines.append(f"Vector store: `{result.vector_store_id}`")
    lines.append(f"File: `{result.filename}`")
    lines.append(f"Symbols: `{result.symbols}`")
    lines.append(f"Bytes: `{result.bytes_written}`")
    lines.append(f"Status: `{result.status}`")
    if result.file_id:
        lines.append(f"OpenAI file: `{result.file_id}`")
    return "\n".join(lines)


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="repo-signal semantic-upload",
        description="Upload high-signal repository symbol memory to an OpenAI vector store.",
    )
    parser.add_argument(
        "--vector-store-id",
        default=None,
        help="OpenAI vector store id. Defaults to OPENAI_VECTOR_STORE_ID.",
    )
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include test symbols in the uploaded memory document.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build the memory document and report size without uploading.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    try:
        result = upload_repository_memory(
            repo_path=Path.cwd(),
            vector_store_id=args.vector_store_id,
            include_tests=args.include_tests,
            dry_run=args.dry_run,
        )
    except ProviderConfigurationError as exc:
        print(f"repo-signal semantic-upload: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    print(format_upload_result(result))


if __name__ == "__main__":
    main()
