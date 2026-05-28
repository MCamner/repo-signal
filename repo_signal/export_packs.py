"""Export all symbolic intelligence packs for mq ecosystem consumers."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from repo_signal.exports.callgraph import build_callgraph
from repo_signal.exports.repo_summary import build_repo_summary
from repo_signal.exports.risk_map import build_risk_map
from repo_signal.exports.symbol_index import build_symbol_index

DEFAULT_OUTPUT_DIR = ".repo-signal/exports"

_PACKS = {
    "symbol_index": ("symbol_index.json", build_symbol_index),
    "callgraph": ("callgraph.json", build_callgraph),
    "repo_summary": ("repo_summary.json", build_repo_summary),
    "risk_map": ("risk_map.json", build_risk_map),
}


def export_packs(
    repo_path: str | Path = ".",
    output_dir: str | Path | None = None,
    packs: list[str] | None = None,
) -> dict[str, Any]:
    """
    Generate symbolic intelligence packs and write them to disk.

    Args:
        repo_path: Repository root.
        output_dir: Output directory (default: .repo-signal/exports/).
        packs: List of pack names to generate. None = all four.

    Returns:
        dict with schema, written files, and per-pack results.
    """
    root = Path(repo_path).resolve()
    out_dir = Path(output_dir) if output_dir else root / DEFAULT_OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    selected = set(packs) if packs else set(_PACKS.keys())
    written: list[str] = []
    results: dict[str, Any] = {}

    for pack_name, (filename, builder) in _PACKS.items():
        if pack_name not in selected:
            continue
        data = builder(root)
        dest = out_dir / filename
        dest.write_text(json.dumps(data, indent=2), encoding="utf-8")
        written.append(str(dest.relative_to(root) if dest.is_relative_to(root) else dest))
        results[pack_name] = {"schema": data.get("schema"), "file": filename}

    return {
        "schema": "export-packs.v1",
        "repo": root.name,
        "output_dir": str(out_dir.relative_to(root) if out_dir.is_relative_to(root) else out_dir),
        "written": written,
        "packs": results,
    }


def format_export_result(result: dict[str, Any], output_format: str = "text") -> str:
    if output_format == "json":
        return json.dumps(result, indent=2)

    lines = [f"repo-signal export — {result['repo']}"]
    lines.append(f"output: {result['output_dir']}")
    lines.append("")
    for path in result["written"]:
        schema = next(
            (v["schema"] for v in result["packs"].values() if path.endswith(v["file"])),
            "?",
        )
        lines.append(f"  wrote  {path}  [{schema}]")
    lines.append("")
    lines.append(f"{len(result['written'])} pack(s) written.")
    return "\n".join(lines)


def _parse_args(args: list[str]) -> tuple[Path, Path, list[str] | None, str]:
    repo = Path(".")
    output_dir = Path(DEFAULT_OUTPUT_DIR)
    packs: list[str] | None = None
    output_format = "text"

    i = 0
    positional = 0
    while i < len(args):
        arg = args[i]
        if arg in {"--all"}:
            packs = None
            i += 1
        elif arg in {"--symbol-index"}:
            packs = (packs or []) + ["symbol_index"]
            i += 1
        elif arg in {"--callgraph"}:
            packs = (packs or []) + ["callgraph"]
            i += 1
        elif arg in {"--repo-summary"}:
            packs = (packs or []) + ["repo_summary"]
            i += 1
        elif arg in {"--risk-map"}:
            packs = (packs or []) + ["risk_map"]
            i += 1
        elif arg in {"--output", "-o"} and i + 1 < len(args):
            output_dir = Path(args[i + 1])
            i += 2
        elif arg.startswith("--output="):
            output_dir = Path(arg.split("=", 1)[1])
            i += 1
        elif arg in {"--format"} and i + 1 < len(args):
            output_format = args[i + 1]
            i += 2
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
            i += 1
        elif not arg.startswith("-") and positional == 0:
            repo = Path(arg)
            positional += 1
            i += 1
        else:
            print(f"Unknown option: {arg}", file=sys.stderr)
            raise SystemExit(2)

    return repo, output_dir, packs, output_format


def main(args: list[str]) -> None:
    if not args or args[0] in {"--help", "-h"}:
        print(
            "Usage: repo-signal export [path] [--output DIR] "
            "[--all | --symbol-index | --callgraph | --repo-summary | --risk-map] "
            "[--format text|json]"
        )
        return

    repo, output_dir, packs, output_format = _parse_args(args)
    result = export_packs(repo, output_dir=output_dir, packs=packs)
    print(format_export_result(result, output_format=output_format))
