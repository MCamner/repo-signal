"""Tests for repo-signal semantic-upload safety and dry-run behavior."""
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


class TestDryRun:
    def test_dry_run_exits_zero_without_vector_store(self):
        env = {**os.environ, "OPENAI_VECTOR_STORE_ID": ""}
        result = subprocess.run(
            [sys.executable, "-m", "repo_signal.cli", "semantic-upload", "--dry-run"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 0

    def test_dry_run_output_contains_repo_name(self):
        result = subprocess.run(
            [sys.executable, "-m", "repo_signal.cli", "semantic-upload", "--dry-run"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "repo-signal" in result.stdout

    def test_dry_run_shows_symbols_count(self):
        result = subprocess.run(
            [sys.executable, "-m", "repo_signal.cli", "semantic-upload", "--dry-run"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Symbols:" in result.stdout

    def test_dry_run_shows_bytes(self):
        result = subprocess.run(
            [sys.executable, "-m", "repo_signal.cli", "semantic-upload", "--dry-run"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Bytes:" in result.stdout

    def test_dry_run_status_is_dry_run(self):
        result = subprocess.run(
            [sys.executable, "-m", "repo_signal.cli", "semantic-upload", "--dry-run"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "dry_run" in result.stdout


class TestMissingVectorStore:
    def test_upload_without_vector_store_exits_nonzero(self):
        env = {k: v for k, v in os.environ.items() if k != "OPENAI_VECTOR_STORE_ID"}
        env["OPENAI_API_KEY"] = "sk-test"
        result = subprocess.run(
            [sys.executable, "-m", "repo_signal.cli", "semantic-upload"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode != 0

    def test_upload_without_vector_store_prints_error(self):
        env = {k: v for k, v in os.environ.items() if k != "OPENAI_VECTOR_STORE_ID"}
        env["OPENAI_API_KEY"] = "sk-test"
        result = subprocess.run(
            [sys.executable, "-m", "repo_signal.cli", "semantic-upload"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            env=env,
        )
        assert "vector store" in result.stderr.lower() or "OPENAI_VECTOR_STORE_ID" in result.stderr

    def test_upload_function_raises_on_missing_store(self):
        from repo_signal.vectorstore.openai_store import resolve_vector_store_id
        from repo_signal.ai.providers.base import ProviderConfigurationError
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ProviderConfigurationError):
                resolve_vector_store_id(None)


class TestNoSecretGuarantee:
    def test_memory_document_contains_symbols_not_raw_source(self):
        from repo_signal.vectorstore.openai_store import build_openai_memory_document
        from repo_signal.core.scanner import scan_repository
        repo = scan_repository(REPO_ROOT)
        doc = build_openai_memory_document(repo, include_tests=False)
        assert "OPENAI_API_KEY" not in doc
        assert "sk-" not in doc
        assert len(doc) > 100

    def test_memory_document_is_markdown(self):
        from repo_signal.vectorstore.openai_store import build_openai_memory_document
        from repo_signal.core.scanner import scan_repository
        repo = scan_repository(REPO_ROOT)
        doc = build_openai_memory_document(repo, include_tests=False)
        assert "#" in doc


class TestMqAgentIntegration:
    def test_mq_agent_memory_status_reports_correctly(self):
        env = {**os.environ, "OPENAI_VECTOR_STORE_ID": ""}
        result = subprocess.run(
            ["mq-agent", "memory", "status", str(REPO_ROOT)],
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 0
        assert "missing-vector-store" in result.stdout

    def test_mq_agent_memory_build_dry_run(self):
        result = subprocess.run(
            ["mq-agent", "memory", "build", str(REPO_ROOT)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "dry-run" in result.stdout.lower() or "Would run" in result.stdout
