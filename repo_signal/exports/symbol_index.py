"""Build symbol_index.v1 — public symbols, files, and ownership hints."""
from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

from repo_signal.core.scanner import scan_repository
from repo_signal.symbols.symbol_extractor import extract_symbols

SCHEMA = "symbol_index.v1"


def _is_public(name: str) -> bool:
    return not name.startswith("_")


def build_symbol_index(repo_path: str | Path = ".") -> dict[str, Any]:
    root = Path(repo_path).resolve()
    repo = scan_repository(root)

    # Per-file public symbol counts
    file_symbol_map: dict[str, list[dict[str, Any]]] = {}
    all_symbols: list[dict[str, Any]] = []

    for file in repo.files:
        if file.extension not in {".py", ".sh", ".bash", ".zsh", ".ps1"}:
            continue
        raw = extract_symbols(root / file.path, repo_path=root)
        for sym in raw:
            public = _is_public(sym.name)
            entry = {
                "name": sym.name,
                "kind": sym.kind,
                "file_path": sym.file_path,
                "line": sym.line,
                "is_public": public,
            }
            all_symbols.append(entry)
            file_symbol_map.setdefault(file.path, []).append(entry)

    files_out = []
    for file in repo.files:
        syms = file_symbol_map.get(file.path, [])
        public_names = [s["name"] for s in syms if s["is_public"]]
        files_out.append({
            "path": file.path,
            "extension": file.extension,
            "symbol_count": len(syms),
            "public_symbols": public_names,
        })

    return {
        "schema": SCHEMA,
        "repo_name": repo.name,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "file_count": len(repo.files),
        "symbol_count": len(all_symbols),
        "files": files_out,
        "symbols": all_symbols,
    }
