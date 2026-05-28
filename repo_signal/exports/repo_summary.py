"""Build repo_summary.v1 — compact repository context for AI consumers."""
from __future__ import annotations

import datetime
import re
from pathlib import Path
from typing import Any

from repo_signal.core.scanner import scan_repository
from repo_signal.symbols.symbol_extractor import extract_symbols

SCHEMA = "repo_summary.v1"


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _version(root: Path) -> str:
    for candidate in ["VERSION", "version.txt"]:
        p = root / candidate
        if p.exists():
            return p.read_text().strip()
    # Try pyproject.toml
    pp = root / "pyproject.toml"
    if pp.exists():
        m = re.search(r'version\s*=\s*["\']([^"\']+)["\']', pp.read_text())
        if m:
            return m.group(1)
    return ""


def _description(root: Path) -> str:
    readme = root / "README.md"
    if not readme.exists():
        return ""
    lines = readme.read_text(encoding="utf-8", errors="ignore").splitlines()
    # Skip headings and blank lines to find first non-trivial sentence
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("!"):
            return stripped[:200]
    return ""


def _test_summary(root: Path) -> str:
    test_dir = root / "tests"
    if not test_dir.is_dir():
        return "no test directory"
    test_files = list(test_dir.glob("test_*.py"))
    return f"{len(test_files)} test files"


def _stable_contracts(root: Path) -> list[str]:
    """Detect declared stable JSON schema contracts from docs/ directory."""
    docs = root / "docs"
    if not docs.is_dir():
        return []
    contracts = []
    for doc in sorted(docs.glob("*_SCHEMA.md")):
        schema_name = doc.stem.lower().replace("_schema", "")
        # Convert INSPECT_SCHEMA → inspect.v1 heuristic
        m = re.search(r"schema[:\s]+[`\"]?([a-z_]+\.v\d+)[`\"]?", doc.read_text(encoding="utf-8", errors="ignore"), re.IGNORECASE)
        if m:
            contracts.append(m.group(1))
        else:
            contracts.append(schema_name)
    return contracts


def _top_public_symbols(root: Path, repo: Any, max_symbols: int = 20) -> list[str]:
    seen: set[str] = set()
    result = []
    for file in repo.files:
        if file.extension != ".py":
            continue
        for sym in extract_symbols(root / file.path, repo_path=root):
            if not sym.name.startswith("_") and sym.name not in seen:
                seen.add(sym.name)
                result.append(sym.name)
            if len(result) >= max_symbols:
                return result
    return result


def build_repo_summary(repo_path: str | Path = ".") -> dict[str, Any]:
    root = Path(repo_path).resolve()
    repo = scan_repository(root)

    return {
        "schema": SCHEMA,
        "repo_name": repo.name,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "version": _version(root),
        "description": _description(root),
        "project_type": repo.project_type,
        "languages": repo.languages,
        "file_count": len(repo.files),
        "test_summary": _test_summary(root),
        "key_files": [f.path for f in repo.files if f.path in {
            "README.md", "CHANGELOG.md", "ROADMAP.md", "VERSION",
            "pyproject.toml", "package.json", "Cargo.toml", "go.mod",
        }],
        "entrypoints": repo.entrypoints,
        "stable_contracts": _stable_contracts(root),
        "top_symbols": _top_public_symbols(root, repo),
    }
