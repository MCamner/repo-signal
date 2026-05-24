"""Tests for repo_signal.report — build_report and format_report."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from repo_signal.report import VALID_FORMATS, build_report, format_report


# ── helpers ─────────────────────────────────────────────────────────────────

MOCK_INSPECT = {
    "schema": "inspect.v1",
    "repo": {"name": "testrepo"},
    "git": {"branch": "main", "clean": True, "summary": "clean"},
    "public_readiness": {
        "available": True,
        "score": 14,
        "total": 16,
        "status": "pass",
        "recommended_next_action": "Add contributing guide",
    },
    "detected": {"languages": {"Python": 10, "Markdown": 3}, "entrypoints": [], "tooling": [], "top_directories": {}},
    "core_files": [{"path": "README.md", "label": "README", "exists": True, "status": "ok"}],
    "issues": [{"level": "warn", "message": "No CONTRIBUTING.md", "raw": ""}],
    "recommended_next_commit": "Add CONTRIBUTING.md",
    "useful_next_commands": ["repo-signal doctor"],
}

MOCK_CHECKLIST = {
    "repo": "testrepo",
    "score": 14,
    "total": 16,
    "status": "pass",
    "groups": [],
}


def _patched_build_report(tmp_path: Path) -> dict:
    with patch("repo_signal.report.inspect_repo_data", return_value=MOCK_INSPECT), \
         patch("repo_signal.report.build_publish_checklist", return_value=MOCK_CHECKLIST):
        return build_report(tmp_path)


# ── build_report ─────────────────────────────────────────────────────────────

def test_build_report_schema(tmp_path):
    data = _patched_build_report(tmp_path)
    assert data["schema"] == "report.v1"


def test_build_report_fields(tmp_path):
    data = _patched_build_report(tmp_path)
    assert data["repo"] == "testrepo"
    assert data["publish_score"] == 14
    assert data["publish_total"] == 16
    assert data["publish_status"] == "pass"
    assert data["git"]["branch"] == "main"
    assert data["git"]["clean"] is True
    assert "Python" in data["languages"]


def test_build_report_issues(tmp_path):
    data = _patched_build_report(tmp_path)
    assert "No CONTRIBUTING.md" in data["issues"]


def test_build_report_next_commit(tmp_path):
    data = _patched_build_report(tmp_path)
    assert data["recommended_next_commit"] == "Add CONTRIBUTING.md"


def test_build_report_useful_commands(tmp_path):
    data = _patched_build_report(tmp_path)
    assert "repo-signal doctor" in data["useful_next_commands"]


# ── format_report ─────────────────────────────────────────────────────────────

def _sample_data(tmp_path: Path) -> dict:
    return _patched_build_report(tmp_path)


def test_format_text_contains_repo(tmp_path):
    out = format_report(_sample_data(tmp_path), "text")
    assert "testrepo" in out
    assert "14/16" in out
    assert "main" in out


def test_format_text_contains_issues(tmp_path):
    out = format_report(_sample_data(tmp_path), "text")
    assert "No CONTRIBUTING.md" in out


def test_format_markdown_has_heading(tmp_path):
    out = format_report(_sample_data(tmp_path), "markdown")
    assert out.startswith("# repo-signal report")
    assert "**Branch:**" in out
    assert "16" in out  # total


def test_format_markdown_core_files_no_raw_dict(tmp_path):
    out = format_report(_sample_data(tmp_path), "markdown")
    assert "README.md" in out
    assert "{'path'" not in out


def test_format_json_valid(tmp_path):
    out = format_report(_sample_data(tmp_path), "json")
    parsed = json.loads(out)
    assert parsed["schema"] == "report.v1"
    assert parsed["publish_score"] == 14


def test_format_json_and_text_equal_data(tmp_path):
    data = _sample_data(tmp_path)
    parsed = json.loads(format_report(data, "json"))
    assert parsed["repo"] == data["repo"]
    assert parsed["publish_score"] == data["publish_score"]


def test_format_unknown_raises(tmp_path):
    with pytest.raises(ValueError, match="Unknown format"):
        format_report(_sample_data(tmp_path), "html")


def test_valid_formats_set():
    assert VALID_FORMATS == {"text", "markdown", "json"}


# ── CLI smoke ────────────────────────────────────────────────────────────────

def test_cli_report_text():
    result = subprocess.run(
        [sys.executable, "-m", "repo_signal.cli", "report", "."],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "repo-signal report" in result.stdout


def test_cli_report_json():
    result = subprocess.run(
        [sys.executable, "-m", "repo_signal.cli", "report", ".", "--json"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["schema"] == "report.v1"
    assert "publish_score" in data


def test_cli_report_markdown():
    result = subprocess.run(
        [sys.executable, "-m", "repo_signal.cli", "report", ".", "--format", "markdown"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert result.stdout.startswith("# repo-signal report")


def test_cli_report_invalid_format():
    result = subprocess.run(
        [sys.executable, "-m", "repo_signal.cli", "report", ".", "--format", "xml"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
