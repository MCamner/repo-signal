"""Tests for readiness.v1 — release/readiness export compatibility."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from repo_signal.readiness import (
    SCHEMA,
    _metadata_freshness,
    _release_gate,
    _version_alignment,
    build_readiness,
    format_readiness,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def aligned_repo(tmp_path: Path) -> Path:
    (tmp_path / "VERSION").write_text("1.4.0\n")
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "1.4.0"\n')
    rs = tmp_path / "repo_signal"
    rs.mkdir()
    (rs / "__init__.py").write_text('__version__ = "1.4.0"\n')
    (tmp_path / "CHANGELOG.md").write_text("## [1.4.0] - 2026-06-08\n### Added\n- readiness.v1\n")
    (tmp_path / "README.md").write_text("# repo-signal\n\nVersion 1.4.0 is out.\n")
    (tmp_path / "ROADMAP.md").write_text("Current main target:\nv1.5.0 — next planned release\n")
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_smoke.py").write_text("def test_ok(): pass\n")
    return tmp_path


@pytest.fixture()
def misaligned_repo(tmp_path: Path) -> Path:
    (tmp_path / "VERSION").write_text("1.4.0\n")
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "1.3.0"\n')
    rs = tmp_path / "repo_signal"
    rs.mkdir()
    (rs / "__init__.py").write_text('__version__ = "1.4.0"\n')
    (tmp_path / "CHANGELOG.md").write_text("## [1.3.0] - 2026-06-03\n")
    (tmp_path / "README.md").write_text("# repo-signal\n")
    return tmp_path


# ---------------------------------------------------------------------------
# Schema shape
# ---------------------------------------------------------------------------


def test_schema_field(aligned_repo: Path) -> None:
    data = build_readiness(aligned_repo)
    assert data["schema"] == SCHEMA


def test_top_level_fields(aligned_repo: Path) -> None:
    data = build_readiness(aligned_repo)
    for key in ("schema", "repo", "path", "generated_at", "version", "metadata", "quality", "release_gate"):
        assert key in data, f"missing field: {key}"


def test_version_block_fields(aligned_repo: Path) -> None:
    data = build_readiness(aligned_repo)
    ver = data["version"]
    assert "current" in ver
    assert "aligned" in ver
    assert "sources" in ver
    assert set(ver["sources"].keys()) == {"VERSION", "pyproject", "init"}


def test_metadata_block_fields(aligned_repo: Path) -> None:
    data = build_readiness(aligned_repo)
    meta = data["metadata"]
    assert "changelog_has_current" in meta
    assert "readme_has_version" in meta
    assert "roadmap_next_target" in meta


def test_quality_block_fields(aligned_repo: Path) -> None:
    data = build_readiness(aligned_repo)
    qual = data["quality"]
    for key in ("publish_checklist_score", "publish_checklist_total", "publish_checklist_pass",
                "test_files_present", "test_file_count"):
        assert key in qual, f"missing quality field: {key}"


def test_release_gate_fields(aligned_repo: Path) -> None:
    data = build_readiness(aligned_repo)
    gate = data["release_gate"]
    assert "ready" in gate
    assert "blocked" in gate
    assert "blockers" in gate
    assert isinstance(gate["blockers"], list)


# ---------------------------------------------------------------------------
# Version alignment
# ---------------------------------------------------------------------------


def test_version_aligned_when_all_match(tmp_path: Path) -> None:
    (tmp_path / "VERSION").write_text("1.4.0\n")
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "1.4.0"\n')
    rs = tmp_path / "repo_signal"
    rs.mkdir()
    (rs / "__init__.py").write_text('__version__ = "1.4.0"\n')
    result = _version_alignment(tmp_path)
    assert result["aligned"] is True
    assert result["current"] == "1.4.0"


def test_version_misaligned_when_pyproject_differs(tmp_path: Path) -> None:
    (tmp_path / "VERSION").write_text("1.4.0\n")
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "1.3.0"\n')
    rs = tmp_path / "repo_signal"
    rs.mkdir()
    (rs / "__init__.py").write_text('__version__ = "1.4.0"\n')
    result = _version_alignment(tmp_path)
    assert result["aligned"] is False


def test_version_missing_files(tmp_path: Path) -> None:
    result = _version_alignment(tmp_path)
    assert result["current"] == ""
    assert result["aligned"] is False


# ---------------------------------------------------------------------------
# Metadata freshness
# ---------------------------------------------------------------------------


def test_changelog_has_current_version(tmp_path: Path) -> None:
    (tmp_path / "CHANGELOG.md").write_text("## [1.4.0] - 2026-06-08\n")
    (tmp_path / "README.md").write_text("")
    (tmp_path / "ROADMAP.md").write_text("")
    result = _metadata_freshness(tmp_path, "1.4.0")
    assert result["changelog_has_current"] is True


def test_changelog_missing_current_version(tmp_path: Path) -> None:
    (tmp_path / "CHANGELOG.md").write_text("## [1.3.0] - 2026-06-03\n")
    (tmp_path / "README.md").write_text("")
    (tmp_path / "ROADMAP.md").write_text("")
    result = _metadata_freshness(tmp_path, "1.4.0")
    assert result["changelog_has_current"] is False


def test_readme_has_version_string(tmp_path: Path) -> None:
    (tmp_path / "CHANGELOG.md").write_text("")
    (tmp_path / "README.md").write_text("# repo-signal v1.4.0\n")
    (tmp_path / "ROADMAP.md").write_text("")
    result = _metadata_freshness(tmp_path, "1.4.0")
    assert result["readme_has_version"] is True


def test_roadmap_next_target_extracted(tmp_path: Path) -> None:
    (tmp_path / "CHANGELOG.md").write_text("")
    (tmp_path / "README.md").write_text("")
    (tmp_path / "ROADMAP.md").write_text("Current main target:\nv1.5.0 — next planned release\n")
    result = _metadata_freshness(tmp_path, "1.4.0")
    assert result["roadmap_next_target"] == "v1.5.0"


def test_roadmap_next_target_empty_when_none(tmp_path: Path) -> None:
    (tmp_path / "CHANGELOG.md").write_text("")
    (tmp_path / "README.md").write_text("")
    (tmp_path / "ROADMAP.md").write_text("# Roadmap\n\nNo targets listed.\n")
    result = _metadata_freshness(tmp_path, "1.4.0")
    assert result["roadmap_next_target"] == ""


# ---------------------------------------------------------------------------
# Release gate
# ---------------------------------------------------------------------------


def test_release_gate_ready_when_no_blockers() -> None:
    ver = {"aligned": True, "current": "1.4.0", "sources": {"VERSION": "1.4.0", "pyproject": "1.4.0", "init": "1.4.0"}}
    meta = {"changelog_has_current": True, "readme_has_version": True, "roadmap_next_target": "v1.5.0"}
    qual = {"publish_checklist_score": 18, "publish_checklist_total": 20, "publish_checklist_pass": True, "test_files_present": True, "test_file_count": 5}
    gate = _release_gate(ver, meta, qual)
    assert gate["ready"] is True
    assert gate["blocked"] is False
    assert gate["blockers"] == []


def test_release_gate_blocked_on_version_mismatch() -> None:
    ver = {"aligned": False, "current": "1.4.0", "sources": {"VERSION": "1.4.0", "pyproject": "1.3.0", "init": "1.4.0"}}
    meta = {"changelog_has_current": True, "readme_has_version": True, "roadmap_next_target": ""}
    qual = {"publish_checklist_score": 18, "publish_checklist_total": 20, "publish_checklist_pass": True, "test_files_present": True, "test_file_count": 5}
    gate = _release_gate(ver, meta, qual)
    assert gate["blocked"] is True
    assert any("version mismatch" in b for b in gate["blockers"])


def test_release_gate_blocked_on_missing_changelog() -> None:
    ver = {"aligned": True, "current": "1.4.0", "sources": {"VERSION": "1.4.0", "pyproject": "1.4.0", "init": "1.4.0"}}
    meta = {"changelog_has_current": False, "readme_has_version": True, "roadmap_next_target": ""}
    qual = {"publish_checklist_score": 18, "publish_checklist_total": 20, "publish_checklist_pass": True, "test_files_present": True, "test_file_count": 5}
    gate = _release_gate(ver, meta, qual)
    assert gate["blocked"] is True
    assert any("CHANGELOG" in b for b in gate["blockers"])


def test_release_gate_blocked_on_low_checklist() -> None:
    ver = {"aligned": True, "current": "1.4.0", "sources": {"VERSION": "1.4.0", "pyproject": "1.4.0", "init": "1.4.0"}}
    meta = {"changelog_has_current": True, "readme_has_version": True, "roadmap_next_target": ""}
    qual = {"publish_checklist_score": 10, "publish_checklist_total": 20, "publish_checklist_pass": False, "test_files_present": True, "test_file_count": 5}
    gate = _release_gate(ver, meta, qual)
    assert gate["blocked"] is True
    assert any("publish checklist" in b for b in gate["blockers"])


def test_release_gate_multiple_blockers() -> None:
    ver = {"aligned": False, "current": "1.4.0", "sources": {"VERSION": "1.4.0", "pyproject": "1.3.0", "init": "1.4.0"}}
    meta = {"changelog_has_current": False, "readme_has_version": False, "roadmap_next_target": ""}
    qual = {"publish_checklist_score": 8, "publish_checklist_total": 20, "publish_checklist_pass": False, "test_files_present": False, "test_file_count": 0}
    gate = _release_gate(ver, meta, qual)
    assert len(gate["blockers"]) >= 3


# ---------------------------------------------------------------------------
# Output formats
# ---------------------------------------------------------------------------


def test_json_format_parses(aligned_repo: Path) -> None:
    data = build_readiness(aligned_repo)
    output = format_readiness(data, "json")
    parsed = json.loads(output)
    assert parsed["schema"] == SCHEMA


def test_text_format_contains_status(aligned_repo: Path) -> None:
    data = build_readiness(aligned_repo)
    output = format_readiness(data, "text")
    assert "readiness.v1" in output
    assert data["repo"] in output


def test_markdown_format_contains_heading(aligned_repo: Path) -> None:
    data = build_readiness(aligned_repo)
    output = format_readiness(data, "markdown")
    assert f"# Readiness — {data['repo']}" in output
    assert "readiness.v1" in output


def test_text_format_shows_blocked(misaligned_repo: Path) -> None:
    data = build_readiness(misaligned_repo)
    output = format_readiness(data, "text")
    assert "BLOCKED" in output


# ---------------------------------------------------------------------------
# Test files present check
# ---------------------------------------------------------------------------


def test_test_file_count_correct(aligned_repo: Path) -> None:
    data = build_readiness(aligned_repo)
    assert data["quality"]["test_file_count"] == 1
    assert data["quality"]["test_files_present"] is True


def test_no_test_files(tmp_path: Path) -> None:
    (tmp_path / "VERSION").write_text("1.4.0\n")
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "1.4.0"\n')
    rs = tmp_path / "repo_signal"
    rs.mkdir()
    (rs / "__init__.py").write_text('__version__ = "1.4.0"\n')
    (tmp_path / "CHANGELOG.md").write_text("")
    (tmp_path / "README.md").write_text("")
    data = build_readiness(tmp_path)
    assert data["quality"]["test_files_present"] is False
    assert data["quality"]["test_file_count"] == 0
