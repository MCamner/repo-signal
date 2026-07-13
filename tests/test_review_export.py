"""Tests for explicit repo-review.v1 export into mqobsidian."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from repo_signal.review_export import build_repo_review, export_repo_review


REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def sample_inspect() -> dict:
    return {
        "schema": "inspect.v1",
        "repo": {"name": "demo-repo", "path": "/private/demo", "exists": True},
        "git": {"branch": "main", "clean": True},
        "public_readiness": {"summary": "14/16 WARN", "status": "warn"},
        "issues": [
            {"level": "warn", "message": "Missing tests", "raw": "[WARN] Missing tests"},
        ],
        "recommended_next_commit": "Add focused tests",
    }


def test_build_repo_review_preserves_schema_provenance(sample_inspect: dict):
    content = build_repo_review(sample_inspect, created_at="2026-07-13T12:00:00Z")

    assert "schema: repo-review.v1" in content
    assert "source_schema: inspect.v1" in content
    assert "repo: demo-repo" in content
    assert "created_at: 2026-07-13T12:00:00Z" in content
    assert "- [WARN] Missing tests" in content
    assert "Add focused tests" in content
    assert "/private/demo" not in content


def test_export_repo_review_writes_only_under_reviews(sample_inspect: dict, tmp_path: Path):
    path = export_repo_review(
        sample_inspect,
        vault=tmp_path,
        created_at="2026-07-13T12:00:00Z",
    )

    assert path == tmp_path / "reviews" / "2026-07-13-repo-signal-demo-repo.md"
    assert path.is_file()


def test_export_repo_review_refuses_overwrite_without_force(sample_inspect: dict, tmp_path: Path):
    export_repo_review(sample_inspect, vault=tmp_path, created_at="2026-07-13T12:00:00Z")

    with pytest.raises(FileExistsError):
        export_repo_review(sample_inspect, vault=tmp_path, created_at="2026-07-13T13:00:00Z")


def test_cli_review_export_writes_mqobsidian_review(tmp_path: Path):
    vault = tmp_path / "vault"
    vault.mkdir()
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "repo_signal.cli",
            "review-export",
            str(REPO_ROOT),
            "--vault",
            str(vault),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    written_files = list((vault / "reviews").glob("*-repo-signal-repo-signal.md"))
    assert len(written_files) == 1
    written = written_files[0]
    assert written.is_file()
    assert str(written) in result.stdout


def test_cli_review_export_reports_missing_vault_without_traceback(tmp_path: Path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "repo_signal.cli",
            "review-export",
            str(REPO_ROOT),
            "--vault",
            str(tmp_path / "missing"),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "mqobsidian vault not found" in result.stdout
    assert "Traceback" not in result.stderr
