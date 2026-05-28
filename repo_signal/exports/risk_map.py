"""Build risk_map.v1 — structural risk signals, no AI findings."""
from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

from repo_signal.core.scanner import scan_repository
from repo_signal.graph.graph_builder import build_repository_graph

SCHEMA = "risk_map.v1"

LARGE_FILE_LINES = 400
HIGH_FAN_IN = 5


def _read_lines(path: Path) -> int:
    try:
        return path.read_text(encoding="utf-8", errors="ignore").count("\n")
    except OSError:
        return 0


def build_risk_map(repo_path: str | Path = ".") -> dict[str, Any]:
    root = Path(repo_path).resolve()
    repo = scan_repository(root)
    graph = build_repository_graph(repo)

    # Count importers per file
    importer_counts: dict[str, int] = {}
    for edge in graph.edges:
        importer_counts[edge.target] = importer_counts.get(edge.target, 0) + 1

    risks: list[dict[str, Any]] = []
    rsk_id = 1

    # Missing docs
    if not (root / "README.md").exists():
        risks.append({
            "id": f"RSK-{rsk_id:03d}",
            "level": "high",
            "kind": "missing_readme",
            "file": "README.md",
            "detail": "No README.md found — repository is undocumented.",
            "structural": True,
        })
        rsk_id += 1

    if not (root / "CHANGELOG.md").exists():
        risks.append({
            "id": f"RSK-{rsk_id:03d}",
            "level": "medium",
            "kind": "missing_changelog",
            "file": "CHANGELOG.md",
            "detail": "No CHANGELOG.md found — release history is undocumented.",
            "structural": True,
        })
        rsk_id += 1

    # No tests
    test_dir = root / "tests"
    if not test_dir.is_dir() or not list(test_dir.glob("test_*.py")):
        risks.append({
            "id": f"RSK-{rsk_id:03d}",
            "level": "high",
            "kind": "no_tests",
            "file": "tests/",
            "detail": "No test files found — changes cannot be automatically verified.",
            "structural": True,
        })
        rsk_id += 1

    # Large source files
    for file in repo.files:
        if file.extension not in {".py", ".js", ".ts", ".go", ".rs"}:
            continue
        lines = _read_lines(root / file.path)
        if lines > LARGE_FILE_LINES:
            risks.append({
                "id": f"RSK-{rsk_id:03d}",
                "level": "medium",
                "kind": "large_file",
                "file": file.path,
                "detail": f"{lines} lines — consider splitting into focused modules.",
                "structural": True,
            })
            rsk_id += 1

    # High fan-in files (change risk: many files depend on this one)
    for file_path, count in sorted(importer_counts.items(), key=lambda x: -x[1]):
        if count >= HIGH_FAN_IN:
            risks.append({
                "id": f"RSK-{rsk_id:03d}",
                "level": "medium",
                "kind": "high_fan_in",
                "file": file_path,
                "detail": f"Imported by {count} files — changes here have wide blast radius.",
                "structural": True,
            })
            rsk_id += 1

    return {
        "schema": SCHEMA,
        "repo_name": repo.name,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "risk_count": len(risks),
        "risks": risks,
    }
