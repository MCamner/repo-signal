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


class TestPublicSafety:
    """`repo-review.v1` is a public-safe artifact.

    The same invariant that governs `memory-observation.v1` evidence applies
    here: a machine-local path must never reach the exported document. This
    exporter satisfies it by construction — it projects only repo name,
    findings, readiness and recommendation — so these tests are the guard that
    keeps it that way.
    """

    def test_export_contains_no_machine_local_path(self, sample_inspect):
        from repo_signal.redaction import is_machine_local_path

        content = build_repo_review(sample_inspect, created_at="2026-09-10T00:00:00Z")
        for line in content.splitlines():
            for token in line.split():
                assert not is_machine_local_path(token), (
                    f"repo-review.v1 leaked a machine-local path: {token!r}"
                )

    def test_source_path_is_not_projected_into_the_document(self, sample_inspect):
        sample_inspect["repo"]["path"] = "/Users/someone/private/demo-repo"
        content = build_repo_review(sample_inspect, created_at="2026-09-10T00:00:00Z")
        assert "/Users/someone" not in content
        assert "demo-repo" in content

    def test_windows_source_path_is_not_projected(self, sample_inspect):
        sample_inspect["repo"]["path"] = "C:\\Users\\someone\\demo-repo"
        content = build_repo_review(sample_inspect, created_at="2026-09-10T00:00:00Z")
        assert "C:\\Users" not in content
