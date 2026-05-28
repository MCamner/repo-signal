"""Build callgraph.v1 — imports and cross-file relationships."""
from __future__ import annotations

import datetime
from collections import defaultdict
from pathlib import Path
from typing import Any

from repo_signal.core.scanner import scan_repository
from repo_signal.graph.graph_builder import build_repository_graph

SCHEMA = "callgraph.v1"

HUB_MIN_IMPORTERS = 3


def build_callgraph(repo_path: str | Path = ".") -> dict[str, Any]:
    root = Path(repo_path).resolve()
    repo = scan_repository(root)
    graph = build_repository_graph(repo)

    # Build imports and importers maps
    imports: dict[str, list[str]] = defaultdict(list)
    importers: dict[str, list[str]] = defaultdict(list)

    for edge in graph.edges:
        imports[edge.source].append(edge.target)
        importers[edge.target].append(edge.source)

    # Hub files: imported by many others
    hub_files = sorted(
        [f for f, imp in importers.items() if len(imp) >= HUB_MIN_IMPORTERS],
        key=lambda f: -len(importers[f]),
    )

    edges_out = [
        {"source": e.source, "target": e.target, "relation": e.relation}
        for e in graph.edges
    ]

    return {
        "schema": SCHEMA,
        "repo_name": repo.name,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "edge_count": len(graph.edges),
        "hub_files": hub_files,
        "imports": {k: sorted(v) for k, v in sorted(imports.items())},
        "importers": {k: sorted(v) for k, v in sorted(importers.items())},
        "edges": edges_out,
    }
