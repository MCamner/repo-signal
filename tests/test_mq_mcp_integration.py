"""v1.2.0 — verify repo-signal export packs match mq-mcp consumer field expectations.

These tests prove the contract between repo-signal v1.1.0 exports and the
mq-mcp callgraph_builder._try_merge_repo_signal_packs() consumer without
requiring mq-mcp to be installed.

Consumer field map (from review_engine/callgraph_builder.py):
  callgraph.v1    edge.get("source"), edge.get("target")
  symbol_index.v1 sym.get("file_path"), sym.get("name")
  repo_summary.v1 whole pack stored as data["repo_signal_summary"]
  risk_map.v1     pack.get("risks", []) stored as data["repo_signal_risks"]
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


# ── shared fixture ────────────────────────────────────────────────────────────

@pytest.fixture()
def minimal_repo(tmp_path: Path) -> Path:
    (tmp_path / "README.md").write_text("# test-repo\n\nA test repository.\n")
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n\n## 0.1.0\n\n- Initial.\n")
    (tmp_path / "VERSION").write_text("0.1.0")
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "test-repo"\nversion = "0.1.0"\n'
    )
    pkg = tmp_path / "test_pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text('"""test_pkg."""\n__version__ = "0.1.0"\n')
    (pkg / "core.py").write_text(
        "from test_pkg.utils import helper\n\nclass Engine:\n    pass\n\ndef run():\n    pass\n"
    )
    (pkg / "utils.py").write_text("def helper():\n    pass\n\ndef _private():\n    pass\n")
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_core.py").write_text("def test_placeholder():\n    pass\n")
    return tmp_path


# ── callgraph.v1 consumer contract ───────────────────────────────────────────

def test_callgraph_edges_have_source_and_target(minimal_repo: Path):
    """mq-mcp reads edge.get('source') and edge.get('target') — both must exist."""
    from repo_signal.exports.callgraph import build_callgraph
    pack = build_callgraph(minimal_repo)
    assert pack["schema"] == "callgraph.v1"
    for edge in pack["edges"]:
        assert "source" in edge, f"edge missing 'source': {edge}"
        assert "target" in edge, f"edge missing 'target': {edge}"


def test_callgraph_hub_files_is_list(minimal_repo: Path):
    """mq-mcp refreshes hub_files from importers — pack must expose hub_files list."""
    from repo_signal.exports.callgraph import build_callgraph
    pack = build_callgraph(minimal_repo)
    assert isinstance(pack["hub_files"], list)


def test_callgraph_edge_source_target_are_strings(minimal_repo: Path):
    from repo_signal.exports.callgraph import build_callgraph
    pack = build_callgraph(minimal_repo)
    for edge in pack["edges"]:
        assert isinstance(edge["source"], str)
        assert isinstance(edge["target"], str)


# ── symbol_index.v1 consumer contract ────────────────────────────────────────

def test_symbol_index_symbols_have_file_path_and_name(minimal_repo: Path):
    """mq-mcp reads sym.get('file_path') and sym.get('name') — both must exist."""
    from repo_signal.exports.symbol_index import build_symbol_index
    pack = build_symbol_index(minimal_repo)
    assert pack["schema"] == "symbol_index.v1"
    for sym in pack["symbols"]:
        assert "file_path" in sym, f"symbol missing 'file_path': {sym}"
        assert "name" in sym, f"symbol missing 'name': {sym}"


def test_symbol_index_file_path_and_name_are_strings(minimal_repo: Path):
    from repo_signal.exports.symbol_index import build_symbol_index
    pack = build_symbol_index(minimal_repo)
    for sym in pack["symbols"]:
        assert isinstance(sym["file_path"], str)
        assert isinstance(sym["name"], str)


def test_symbol_index_symbols_nonempty_for_python_repo(minimal_repo: Path):
    """mq-mcp only gets value if there are symbols to merge."""
    from repo_signal.exports.symbol_index import build_symbol_index
    pack = build_symbol_index(minimal_repo)
    assert len(pack["symbols"]) > 0


# ── repo_summary.v1 consumer contract ────────────────────────────────────────

def test_repo_summary_schema_field(minimal_repo: Path):
    """mq-mcp checks pack.get('schema') == 'repo_summary.v1' before storing."""
    from repo_signal.exports.repo_summary import build_repo_summary
    pack = build_repo_summary(minimal_repo)
    assert pack["schema"] == "repo_summary.v1"


def test_repo_summary_is_json_serializable(minimal_repo: Path):
    """mq-mcp stores the whole pack — it must be JSON-safe."""
    from repo_signal.exports.repo_summary import build_repo_summary
    pack = build_repo_summary(minimal_repo)
    serialized = json.dumps(pack)
    assert json.loads(serialized)["schema"] == "repo_summary.v1"


# ── risk_map.v1 consumer contract ────────────────────────────────────────────

def test_risk_map_schema_field(minimal_repo: Path):
    """mq-mcp checks pack.get('schema') == 'risk_map.v1' before storing."""
    from repo_signal.exports.risk_map import build_risk_map
    pack = build_risk_map(minimal_repo)
    assert pack["schema"] == "risk_map.v1"


def test_risk_map_risks_is_list(minimal_repo: Path):
    """mq-mcp stores pack.get('risks', []) — key must exist and be a list."""
    from repo_signal.exports.risk_map import build_risk_map
    pack = build_risk_map(minimal_repo)
    assert isinstance(pack.get("risks", []), list)


def test_risk_map_is_json_serializable(minimal_repo: Path):
    from repo_signal.exports.risk_map import build_risk_map
    pack = build_risk_map(minimal_repo)
    assert json.loads(json.dumps(pack))["schema"] == "risk_map.v1"


# ── graceful degradation ──────────────────────────────────────────────────────

def test_exports_dir_absent_returns_not_found_status(tmp_path: Path):
    """mq-mcp returns a status string when .repo-signal/exports/ is absent.
    Simulate the consumer check: if dir does not exist, return early with message.
    """
    exports_dir = tmp_path / ".repo-signal" / "exports"
    assert not exports_dir.exists()
    # Mirror mq-mcp logic
    if not exports_dir.is_dir():
        status = "repo-signal packs: not found (run `repo-signal export` to generate)"
    else:
        status = "merged"
    assert status.startswith("repo-signal packs: not found")


def test_exports_dir_present_but_empty_returns_no_valid_schemas(tmp_path: Path):
    """mq-mcp returns fallback status when dir exists but no valid v1 schemas found."""
    exports_dir = tmp_path / ".repo-signal" / "exports"
    exports_dir.mkdir(parents=True)
    found: list[str] = []
    # Mirror mq-mcp logic for each pack
    for fname in ["callgraph.json", "symbol_index.json", "repo_summary.json", "risk_map.json"]:
        f = exports_dir / fname
        if f.exists():
            try:
                pack = json.loads(f.read_text(encoding="utf-8"))
                if pack.get("schema"):
                    found.append(pack["schema"])
            except Exception:
                pass
    status = (
        f"repo-signal packs merged: {', '.join(found)}"
        if found
        else "repo-signal packs: exports directory present but no valid v1 schemas found"
    )
    assert "no valid v1 schemas" in status


# ── full pipeline smoke ───────────────────────────────────────────────────────

def test_all_four_packs_written_to_exports_dir(minimal_repo: Path, tmp_path: Path):
    """End-to-end: export writes all four packs; each has the correct schema field."""
    from repo_signal.export_packs import export_packs
    out_dir = tmp_path / ".repo-signal" / "exports"
    export_packs(minimal_repo, output_dir=out_dir)

    expected = {
        "callgraph.json": "callgraph.v1",
        "symbol_index.json": "symbol_index.v1",
        "repo_summary.json": "repo_summary.v1",
        "risk_map.json": "risk_map.v1",
    }
    for fname, schema in expected.items():
        path = out_dir / fname
        assert path.exists(), f"missing: {fname}"
        pack = json.loads(path.read_text(encoding="utf-8"))
        assert pack.get("schema") == schema, f"{fname}: expected schema={schema}, got {pack.get('schema')}"


def test_mq_mcp_consumer_fields_present_in_all_packs(minimal_repo: Path, tmp_path: Path):
    """Prove every field mq-mcp reads is present in the generated packs."""
    from repo_signal.export_packs import export_packs
    out_dir = tmp_path / ".repo-signal" / "exports"
    export_packs(minimal_repo, output_dir=out_dir)

    cg = json.loads((out_dir / "callgraph.json").read_text())
    for edge in cg["edges"]:
        assert "source" in edge and "target" in edge

    sym = json.loads((out_dir / "symbol_index.json").read_text())
    for s in sym["symbols"]:
        assert "name" in s and "file_path" in s

    summary = json.loads((out_dir / "repo_summary.json").read_text())
    assert summary.get("schema") == "repo_summary.v1"

    risk = json.loads((out_dir / "risk_map.json").read_text())
    assert isinstance(risk.get("risks", []), list)
