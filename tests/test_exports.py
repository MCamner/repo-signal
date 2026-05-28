"""Tests for v1.1.0 symbolic intelligence export contracts."""
from __future__ import annotations

import json
from pathlib import Path

import pytest


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def minimal_repo(tmp_path: Path) -> Path:
    """A minimal Python repo with all key structural files."""
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


@pytest.fixture()
def no_docs_repo(tmp_path: Path) -> Path:
    """A repo missing README, CHANGELOG, and tests."""
    (tmp_path / "VERSION").write_text("0.0.1")
    pkg = tmp_path / "mylib"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    return tmp_path


# ── symbol_index.v1 ───────────────────────────────────────────────────────────

def test_symbol_index_schema(minimal_repo: Path):
    from repo_signal.exports.symbol_index import build_symbol_index
    result = build_symbol_index(minimal_repo)
    assert result["schema"] == "symbol_index.v1"


def test_symbol_index_required_fields(minimal_repo: Path):
    from repo_signal.exports.symbol_index import build_symbol_index
    result = build_symbol_index(minimal_repo)
    for field in ("repo_name", "generated_at", "file_count", "symbol_count", "files", "symbols"):
        assert field in result, f"Missing field: {field}"


def test_symbol_index_finds_public_symbols(minimal_repo: Path):
    from repo_signal.exports.symbol_index import build_symbol_index
    result = build_symbol_index(minimal_repo)
    all_names = [s["name"] for s in result["symbols"]]
    assert "Engine" in all_names
    assert "run" in all_names
    assert "helper" in all_names


def test_symbol_index_marks_private(minimal_repo: Path):
    from repo_signal.exports.symbol_index import build_symbol_index
    result = build_symbol_index(minimal_repo)
    private = [s for s in result["symbols"] if s["name"] == "_private"]
    assert private, "Expected _private to be extracted"
    assert private[0]["is_public"] is False


def test_symbol_index_is_json_serializable(minimal_repo: Path):
    from repo_signal.exports.symbol_index import build_symbol_index
    result = build_symbol_index(minimal_repo)
    payload = json.dumps(result)
    parsed = json.loads(payload)
    assert parsed["schema"] == "symbol_index.v1"


# ── callgraph.v1 ─────────────────────────────────────────────────────────────

def test_callgraph_schema(minimal_repo: Path):
    from repo_signal.exports.callgraph import build_callgraph
    result = build_callgraph(minimal_repo)
    assert result["schema"] == "callgraph.v1"


def test_callgraph_required_fields(minimal_repo: Path):
    from repo_signal.exports.callgraph import build_callgraph
    result = build_callgraph(minimal_repo)
    for field in ("repo_name", "generated_at", "edge_count", "hub_files", "imports", "importers", "edges"):
        assert field in result, f"Missing field: {field}"


def test_callgraph_detects_import(minimal_repo: Path):
    from repo_signal.exports.callgraph import build_callgraph
    result = build_callgraph(minimal_repo)
    # core.py imports utils.py
    edges = result["edges"]
    sources = [e["source"] for e in edges]
    assert any("core" in s for s in sources), f"Expected import edge from core, got: {sources}"


def test_callgraph_edge_fields(minimal_repo: Path):
    from repo_signal.exports.callgraph import build_callgraph
    result = build_callgraph(minimal_repo)
    for edge in result["edges"]:
        assert "source" in edge
        assert "target" in edge
        assert "relation" in edge


def test_callgraph_edge_count_matches(minimal_repo: Path):
    from repo_signal.exports.callgraph import build_callgraph
    result = build_callgraph(minimal_repo)
    assert result["edge_count"] == len(result["edges"])


def test_callgraph_is_json_serializable(minimal_repo: Path):
    from repo_signal.exports.callgraph import build_callgraph
    result = build_callgraph(minimal_repo)
    json.dumps(result)


# ── repo_summary.v1 ──────────────────────────────────────────────────────────

def test_repo_summary_schema(minimal_repo: Path):
    from repo_signal.exports.repo_summary import build_repo_summary
    result = build_repo_summary(minimal_repo)
    assert result["schema"] == "repo_summary.v1"


def test_repo_summary_required_fields(minimal_repo: Path):
    from repo_signal.exports.repo_summary import build_repo_summary
    result = build_repo_summary(minimal_repo)
    for field in (
        "repo_name", "generated_at", "version", "description",
        "project_type", "languages", "file_count", "test_summary",
        "key_files", "entrypoints", "stable_contracts", "top_symbols",
    ):
        assert field in result, f"Missing field: {field}"


def test_repo_summary_version(minimal_repo: Path):
    from repo_signal.exports.repo_summary import build_repo_summary
    result = build_repo_summary(minimal_repo)
    assert result["version"] == "0.1.0"


def test_repo_summary_description_nonempty(minimal_repo: Path):
    from repo_signal.exports.repo_summary import build_repo_summary
    result = build_repo_summary(minimal_repo)
    assert result["description"]


def test_repo_summary_key_files_has_readme(minimal_repo: Path):
    from repo_signal.exports.repo_summary import build_repo_summary
    result = build_repo_summary(minimal_repo)
    assert "README.md" in result["key_files"]


def test_repo_summary_top_symbols_nonempty(minimal_repo: Path):
    from repo_signal.exports.repo_summary import build_repo_summary
    result = build_repo_summary(minimal_repo)
    assert len(result["top_symbols"]) > 0


def test_repo_summary_is_json_serializable(minimal_repo: Path):
    from repo_signal.exports.repo_summary import build_repo_summary
    result = build_repo_summary(minimal_repo)
    json.dumps(result)


# ── risk_map.v1 ───────────────────────────────────────────────────────────────

def test_risk_map_schema(minimal_repo: Path):
    from repo_signal.exports.risk_map import build_risk_map
    result = build_risk_map(minimal_repo)
    assert result["schema"] == "risk_map.v1"


def test_risk_map_required_fields(minimal_repo: Path):
    from repo_signal.exports.risk_map import build_risk_map
    result = build_risk_map(minimal_repo)
    for field in ("repo_name", "generated_at", "risk_count", "risks"):
        assert field in result, f"Missing field: {field}"


def test_risk_map_count_matches(minimal_repo: Path):
    from repo_signal.exports.risk_map import build_risk_map
    result = build_risk_map(minimal_repo)
    assert result["risk_count"] == len(result["risks"])


def test_risk_map_risk_fields(minimal_repo: Path):
    from repo_signal.exports.risk_map import build_risk_map
    result = build_risk_map(minimal_repo)
    for risk in result["risks"]:
        assert "id" in risk
        assert "level" in risk
        assert "kind" in risk
        assert "file" in risk
        assert "detail" in risk
        assert risk["level"] in {"low", "medium", "high"}


def test_risk_map_no_docs_repo_high_risk(no_docs_repo: Path):
    from repo_signal.exports.risk_map import build_risk_map
    result = build_risk_map(no_docs_repo)
    levels = {r["level"] for r in result["risks"]}
    assert "high" in levels, "Expected high-level risks in repo with no README/tests"


def test_risk_map_ids_unique(minimal_repo: Path):
    from repo_signal.exports.risk_map import build_risk_map
    result = build_risk_map(minimal_repo)
    ids = [r["id"] for r in result["risks"]]
    assert len(ids) == len(set(ids))


def test_risk_map_is_json_serializable(minimal_repo: Path):
    from repo_signal.exports.risk_map import build_risk_map
    result = build_risk_map(minimal_repo)
    json.dumps(result)


# ── export_packs orchestrator ─────────────────────────────────────────────────

def test_export_packs_writes_all_four(minimal_repo: Path, tmp_path: Path):
    from repo_signal.export_packs import export_packs
    out = tmp_path / "exports"
    result = export_packs(minimal_repo, output_dir=out)
    assert len(result["written"]) == 4
    assert (out / "symbol_index.json").exists()
    assert (out / "callgraph.json").exists()
    assert (out / "repo_summary.json").exists()
    assert (out / "risk_map.json").exists()


def test_export_packs_json_valid(minimal_repo: Path, tmp_path: Path):
    from repo_signal.export_packs import export_packs
    out = tmp_path / "exports"
    export_packs(minimal_repo, output_dir=out)
    for filename in ("symbol_index.json", "callgraph.json", "repo_summary.json", "risk_map.json"):
        data = json.loads((out / filename).read_text())
        assert "schema" in data


def test_export_packs_selective(minimal_repo: Path, tmp_path: Path):
    from repo_signal.export_packs import export_packs
    out = tmp_path / "exports"
    result = export_packs(minimal_repo, output_dir=out, packs=["symbol_index", "callgraph"])
    assert len(result["written"]) == 2
    assert (out / "symbol_index.json").exists()
    assert (out / "callgraph.json").exists()
    assert not (out / "repo_summary.json").exists()


def test_export_packs_result_schema(minimal_repo: Path, tmp_path: Path):
    from repo_signal.export_packs import export_packs
    result = export_packs(minimal_repo, output_dir=tmp_path / "e")
    assert result["schema"] == "export-packs.v1"
    assert result["repo"] == minimal_repo.name


# ── CLI smoke test ────────────────────────────────────────────────────────────

def test_cli_export_runs(minimal_repo: Path, tmp_path: Path):
    import subprocess, sys
    out = tmp_path / "exports"
    proc = subprocess.run(
        [sys.executable, "-m", "repo_signal.cli", "export", str(minimal_repo), "--output", str(out)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert "4 pack(s) written" in proc.stdout


def test_cli_export_json_format(minimal_repo: Path, tmp_path: Path):
    import subprocess, sys
    out = tmp_path / "exports"
    proc = subprocess.run(
        [sys.executable, "-m", "repo_signal.cli", "export", str(minimal_repo),
         "--output", str(out), "--format", "json"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["schema"] == "export-packs.v1"
