"""readiness.v1 — release/readiness export for mq-agent and mq-mcp consumers.

Combines version alignment, metadata freshness, publish-checklist quality, and
a deterministic release_gate block into a single JSON contract.
"""
from __future__ import annotations

import datetime
import json
import re
from pathlib import Path
from typing import Any

SCHEMA = "readiness.v1"
PUBLISH_CHECKLIST_PASS_THRESHOLD = 16


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _version_alignment(root: Path) -> dict[str, Any]:
    version_file = _read(root / "VERSION").strip()
    pyproject = _read(root / "pyproject.toml")
    init = _read(root / "repo_signal" / "__init__.py")

    pyproject_match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', pyproject, re.MULTILINE)
    pyproject_ver = pyproject_match.group(1) if pyproject_match else ""

    init_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init)
    init_ver = init_match.group(1) if init_match else ""

    current = version_file or pyproject_ver or init_ver
    sources = {"VERSION": version_file, "pyproject": pyproject_ver, "init": init_ver}
    non_empty = [v for v in sources.values() if v]
    aligned = len(set(non_empty)) == 1 if non_empty else False

    return {"current": current, "aligned": aligned, "sources": sources}


def _metadata_freshness(root: Path, version: str) -> dict[str, Any]:
    changelog = _read(root / "CHANGELOG.md")
    readme = _read(root / "README.md")
    roadmap = _read(root / "ROADMAP.md")

    changelog_has_current = bool(version and re.search(
        rf"\[{re.escape(version)}\]", changelog
    ))

    readme_has_version = bool(version and version in readme)

    roadmap_next: str = ""
    for line in roadmap.splitlines():
        m = re.search(r"v(\d+\.\d+\.\d+)", line)
        if m and ("planned" in line.lower() or "next" in line.lower() or "target" in line.lower()):
            roadmap_next = f"v{m.group(1)}"
            break

    return {
        "changelog_has_current": changelog_has_current,
        "readme_has_version": readme_has_version,
        "roadmap_next_target": roadmap_next,
    }


def _quality_signals(root: Path) -> dict[str, Any]:
    from repo_signal.publish_checklist import build_publish_checklist

    checklist = build_publish_checklist(str(root))
    score = checklist.get("score", 0)
    total = checklist.get("total", 0)
    tests_dir = root / "tests"
    test_files = list(tests_dir.glob("test_*.py")) if tests_dir.is_dir() else []

    return {
        "publish_checklist_score": score,
        "publish_checklist_total": total,
        "publish_checklist_pass": score >= PUBLISH_CHECKLIST_PASS_THRESHOLD,
        "test_files_present": len(test_files) > 0,
        "test_file_count": len(test_files),
    }


def _release_gate(version_data: dict, metadata: dict, quality: dict) -> dict[str, Any]:
    blockers: list[str] = []

    if not version_data["aligned"]:
        sources = version_data["sources"]
        mismatch = {k: v for k, v in sources.items() if v}
        if len(set(mismatch.values())) > 1:
            blockers.append(f"version mismatch: {mismatch}")

    if not metadata["changelog_has_current"]:
        ver = version_data.get("current", "?")
        blockers.append(f"CHANGELOG missing entry for {ver}")

    if not quality["publish_checklist_pass"]:
        score = quality["publish_checklist_score"]
        total = quality["publish_checklist_total"]
        blockers.append(
            f"publish checklist below threshold: {score}/{total} "
            f"(need {PUBLISH_CHECKLIST_PASS_THRESHOLD})"
        )

    return {
        "ready": len(blockers) == 0,
        "blocked": len(blockers) > 0,
        "blockers": blockers,
    }


def build_readiness(repo_path: str | Path = ".") -> dict[str, Any]:
    root = Path(repo_path).resolve()
    version_data = _version_alignment(root)
    metadata = _metadata_freshness(root, version_data["current"])
    quality = _quality_signals(root)
    gate = _release_gate(version_data, metadata, quality)

    return {
        "schema": SCHEMA,
        "repo": root.name,
        "path": str(root),
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "version": version_data,
        "metadata": metadata,
        "quality": quality,
        "release_gate": gate,
    }


def format_readiness(data: dict[str, Any], output_format: str = "text") -> str:
    if output_format == "json":
        return json.dumps(data, indent=2)

    repo = data["repo"]
    ver = data["version"]
    meta = data["metadata"]
    qual = data["quality"]
    gate = data["release_gate"]

    if output_format == "markdown":
        status = "READY" if gate["ready"] else "BLOCKED"
        lines = [
            f"# Readiness — {repo}",
            "",
            f"**Status:** {status}  ",
            f"**Version:** {ver['current']} (aligned: {ver['aligned']})",
            "",
            "## Version sources",
            "",
        ]
        for src, val in ver["sources"].items():
            mark = "OK" if val == ver["current"] else "MISMATCH"
            lines.append(f"- `{src}`: {val or '(missing)'}  [{mark}]")
        lines += [
            "",
            "## Metadata",
            "",
            f"- Changelog has current version: {meta['changelog_has_current']}",
            f"- README has version string: {meta['readme_has_version']}",
            f"- Roadmap next target: {meta['roadmap_next_target'] or '(none found)'}",
            "",
            "## Quality",
            "",
            f"- Publish checklist: {qual['publish_checklist_score']}/{qual['publish_checklist_total']} "
            f"(pass: {qual['publish_checklist_pass']})",
            f"- Test files: {qual['test_file_count']}",
            "",
        ]
        if gate["blockers"]:
            lines += ["## Blockers", ""]
            for b in gate["blockers"]:
                lines.append(f"- {b}")
            lines.append("")
        lines.append("*readiness.v1 — repo-signal*")
        return "\n".join(lines)

    # text (default)
    W = 56
    sep = "─" * W
    status = "READY" if gate["ready"] else "BLOCKED"
    lines = [
        "",
        f"  Readiness — {repo}",
        f"  {sep}",
        f"  Status      {status}",
        f"  Version     {ver['current']}  (aligned: {ver['aligned']})",
    ]
    for src, val in ver["sources"].items():
        mark = "ok" if val == ver["current"] else "MISMATCH"
        lines.append(f"    {src:<12}{val or '(missing)'}  [{mark}]")
    lines += [
        f"  {sep}",
        f"  Changelog   current={'yes' if meta['changelog_has_current'] else 'NO'}",
        f"  README ver  {'yes' if meta['readme_has_version'] else 'no'}",
        f"  Roadmap     {meta['roadmap_next_target'] or '(none)'}",
        f"  {sep}",
        f"  Checklist   {qual['publish_checklist_score']}/{qual['publish_checklist_total']}"
        f"  ({'pass' if qual['publish_checklist_pass'] else 'FAIL'})",
        f"  Test files  {qual['test_file_count']}",
        f"  {sep}",
    ]
    if gate["blockers"]:
        lines.append("  Blockers")
        for b in gate["blockers"]:
            lines.append(f"    - {b[:52]}")
    lines += [f"  {sep}", "  readiness.v1", ""]
    return "\n".join(lines)
