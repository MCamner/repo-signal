"""Tests for repo_signal.suggest — build_suggestions and format_suggestions.

Critical invariant: build_suggestions never writes to disk.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from repo_signal.suggest import VALID_FORMATS, build_suggestions, format_suggestions


# ── helpers ──────────────────────────────────────────────────────────────────

MOCK_INSPECT = {
    "schema": "inspect.v1",
    "repo": {"name": "testrepo"},
    "git": {"branch": "main", "clean": True, "summary": "clean"},
    "public_readiness": {"available": True, "score": 10, "total": 16, "status": "warn"},
    "detected": {"languages": {}, "entrypoints": [], "tooling": [], "top_directories": {}},
    "core_files": [
        {"path": "README.md", "label": "README", "exists": True, "status": "ok"},
        {"path": "LICENSE", "label": "License", "exists": False, "status": "missing"},
        {"path": "CHANGELOG.md", "label": "Changelog", "exists": False, "status": "missing"},
    ],
    "issues": [{"level": "warn", "message": "No CONTRIBUTING.md", "raw": ""}],
    "recommended_next_commit": "Add CONTRIBUTING.md",
    "useful_next_commands": [],
}

MOCK_CHECKLIST_PASS = {
    "repo": "testrepo",
    "score": 16,
    "total": 16,
    "status": "pass",
    "groups": [],
    "checks": [],
    "recommended_next_action": "",
}

MOCK_CHECKLIST_WARN = {
    "repo": "testrepo",
    "score": 12,
    "total": 16,
    "status": "warn",
    "groups": [
        {
            "name": "Front door",
            "checks": [
                {"name": "README exists", "status": "ok", "hint": ""},
                {"name": "README has quick start", "status": "warn", "hint": "add quick start section"},
                {"name": "README mentions demo", "status": "warn", "hint": "add demo reference"},
            ],
        },
        {
            "name": "Public quality",
            "checks": [
                {"name": "LICENSE exists", "status": "warn", "hint": "add LICENSE"},
                {"name": "CHANGELOG exists", "status": "ok", "hint": ""},
            ],
        },
    ],
    "checks": [],
    "recommended_next_action": "Add LICENSE",
}


# ── no-mutation guarantee ────────────────────────────────────────────────────

def test_build_suggestions_does_not_write_files(tmp_path: Path) -> None:
    """Core invariant: build_suggestions must never create or modify files."""
    (tmp_path / "README.md").write_text("# Test\n")

    snapshot_before = {p: p.stat().st_mtime for p in tmp_path.rglob("*") if p.is_file()}

    with patch("repo_signal.suggest.inspect_repo_data", return_value=MOCK_INSPECT):
        with patch("repo_signal.suggest.build_publish_checklist", return_value=MOCK_CHECKLIST_WARN):
            build_suggestions(tmp_path)

    snapshot_after = {p: p.stat().st_mtime for p in tmp_path.rglob("*") if p.is_file()}

    assert snapshot_before == snapshot_after, "build_suggestions must not write any files"


def test_build_suggestions_does_not_create_new_files(tmp_path: Path) -> None:
    files_before = set(tmp_path.rglob("*"))

    with patch("repo_signal.suggest.inspect_repo_data", return_value=MOCK_INSPECT):
        with patch("repo_signal.suggest.build_publish_checklist", return_value=MOCK_CHECKLIST_WARN):
            build_suggestions(tmp_path)

    files_after = set(tmp_path.rglob("*"))
    assert files_before == files_after, "build_suggestions must not create any files"


# ── schema ───────────────────────────────────────────────────────────────────

def test_build_suggestions_schema_field() -> None:
    with patch("repo_signal.suggest.inspect_repo_data", return_value=MOCK_INSPECT):
        with patch("repo_signal.suggest.build_publish_checklist", return_value=MOCK_CHECKLIST_PASS):
            result = build_suggestions(".")
    assert result["schema"] == "suggest.v1"


def test_build_suggestions_required_fields() -> None:
    with patch("repo_signal.suggest.inspect_repo_data", return_value=MOCK_INSPECT):
        with patch("repo_signal.suggest.build_publish_checklist", return_value=MOCK_CHECKLIST_WARN):
            result = build_suggestions(".")

    for field in ("schema", "repo", "path", "total", "by_risk", "by_group", "suggestions"):
        assert field in result, f"Missing field: {field}"


def test_build_suggestions_by_risk_keys() -> None:
    with patch("repo_signal.suggest.inspect_repo_data", return_value=MOCK_INSPECT):
        with patch("repo_signal.suggest.build_publish_checklist", return_value=MOCK_CHECKLIST_PASS):
            result = build_suggestions(".")
    assert set(result["by_risk"].keys()) == {"low", "medium", "high"}


def test_suggestion_fields() -> None:
    with patch("repo_signal.suggest.inspect_repo_data", return_value=MOCK_INSPECT):
        with patch("repo_signal.suggest.build_publish_checklist", return_value=MOCK_CHECKLIST_WARN):
            result = build_suggestions(".")

    for s in result["suggestions"]:
        for field in ("id", "title", "description", "risk", "commit_group", "diff_preview", "command_hint"):
            assert field in s, f"Suggestion missing field: {field}"


def test_suggestion_risk_values() -> None:
    with patch("repo_signal.suggest.inspect_repo_data", return_value=MOCK_INSPECT):
        with patch("repo_signal.suggest.build_publish_checklist", return_value=MOCK_CHECKLIST_WARN):
            result = build_suggestions(".")

    for s in result["suggestions"]:
        assert s["risk"] in ("low", "medium", "high"), f"Invalid risk: {s['risk']}"


def test_total_matches_suggestions_count() -> None:
    with patch("repo_signal.suggest.inspect_repo_data", return_value=MOCK_INSPECT):
        with patch("repo_signal.suggest.build_publish_checklist", return_value=MOCK_CHECKLIST_WARN):
            result = build_suggestions(".")
    assert result["total"] == len(result["suggestions"])


def test_by_risk_sums_to_total() -> None:
    with patch("repo_signal.suggest.inspect_repo_data", return_value=MOCK_INSPECT):
        with patch("repo_signal.suggest.build_publish_checklist", return_value=MOCK_CHECKLIST_WARN):
            result = build_suggestions(".")
    assert sum(result["by_risk"].values()) == result["total"]


# ── no suggestions case ──────────────────────────────────────────────────────

def test_no_suggestions_when_all_pass() -> None:
    clean_inspect = {**MOCK_INSPECT, "core_files": [], "issues": []}
    with patch("repo_signal.suggest.inspect_repo_data", return_value=clean_inspect):
        with patch("repo_signal.suggest.build_publish_checklist", return_value=MOCK_CHECKLIST_PASS):
            result = build_suggestions(".")
    assert result["total"] == 0
    assert result["suggestions"] == []


# ── format: json ─────────────────────────────────────────────────────────────

def test_format_json_is_valid_json() -> None:
    with patch("repo_signal.suggest.inspect_repo_data", return_value=MOCK_INSPECT):
        with patch("repo_signal.suggest.build_publish_checklist", return_value=MOCK_CHECKLIST_WARN):
            data = build_suggestions(".")
    output = format_suggestions(data, output_format="json")
    parsed = json.loads(output)
    assert parsed["schema"] == "suggest.v1"


def test_format_json_schema_field_present() -> None:
    with patch("repo_signal.suggest.inspect_repo_data", return_value=MOCK_INSPECT):
        with patch("repo_signal.suggest.build_publish_checklist", return_value=MOCK_CHECKLIST_PASS):
            data = build_suggestions(".")
    output = format_suggestions(data, output_format="json")
    assert '"schema": "suggest.v1"' in output


# ── format: text ──────────────────────────────────────────────────────────────

def test_format_text_contains_repo_name() -> None:
    with patch("repo_signal.suggest.inspect_repo_data", return_value=MOCK_INSPECT):
        with patch("repo_signal.suggest.build_publish_checklist", return_value=MOCK_CHECKLIST_WARN):
            data = build_suggestions(".")
    output = format_suggestions(data, output_format="text")
    assert "testrepo" in output


def test_format_text_no_suggestions_message() -> None:
    clean_inspect = {**MOCK_INSPECT, "core_files": [], "issues": []}
    with patch("repo_signal.suggest.inspect_repo_data", return_value=clean_inspect):
        with patch("repo_signal.suggest.build_publish_checklist", return_value=MOCK_CHECKLIST_PASS):
            data = build_suggestions(".")
    output = format_suggestions(data, output_format="text")
    assert "No suggestions" in output


# ── format: markdown ─────────────────────────────────────────────────────────

def test_format_markdown_has_heading() -> None:
    with patch("repo_signal.suggest.inspect_repo_data", return_value=MOCK_INSPECT):
        with patch("repo_signal.suggest.build_publish_checklist", return_value=MOCK_CHECKLIST_WARN):
            data = build_suggestions(".")
    output = format_suggestions(data, output_format="markdown")
    assert output.startswith("# repo-signal suggest")


def test_format_markdown_no_suggestions_message() -> None:
    clean_inspect = {**MOCK_INSPECT, "core_files": [], "issues": []}
    with patch("repo_signal.suggest.inspect_repo_data", return_value=clean_inspect):
        with patch("repo_signal.suggest.build_publish_checklist", return_value=MOCK_CHECKLIST_PASS):
            data = build_suggestions(".")
    output = format_suggestions(data, output_format="markdown")
    assert "No suggestions" in output


# ── invalid format ────────────────────────────────────────────────────────────

def test_format_invalid_raises() -> None:
    with patch("repo_signal.suggest.inspect_repo_data", return_value=MOCK_INSPECT):
        with patch("repo_signal.suggest.build_publish_checklist", return_value=MOCK_CHECKLIST_PASS):
            data = build_suggestions(".")
    with pytest.raises(ValueError, match="Unknown format"):
        format_suggestions(data, output_format="xml")


def test_valid_formats_set() -> None:
    assert VALID_FORMATS == {"text", "markdown", "json"}


# ── CLI smoke tests ───────────────────────────────────────────────────────────

def test_cli_suggest_exits_zero(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Test\n")
    result = subprocess.run(
        [sys.executable, "-m", "repo_signal.cli", "suggest", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_cli_suggest_json_exits_zero(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Test\n")
    result = subprocess.run(
        [sys.executable, "-m", "repo_signal.cli", "suggest", str(tmp_path), "--format", "json"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    parsed = json.loads(result.stdout)
    assert parsed["schema"] == "suggest.v1"


def test_cli_suggest_markdown_exits_zero(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Test\n")
    result = subprocess.run(
        [sys.executable, "-m", "repo_signal.cli", "suggest", str(tmp_path), "--format", "markdown"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "# repo-signal suggest" in result.stdout


def test_cli_suggest_invalid_format_exits_nonzero(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "repo_signal.cli", "suggest", str(tmp_path), "--format", "xml"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0


def test_cli_suggest_does_not_create_files(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Test\n")
    files_before = set(tmp_path.rglob("*"))
    subprocess.run(
        [sys.executable, "-m", "repo_signal.cli", "suggest", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    files_after = set(tmp_path.rglob("*"))
    assert files_before == files_after, "CLI suggest must not create files"
