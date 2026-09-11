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
        # The dry-run header names the repo it scanned, and that name is the
        # checkout directory's. Deriving it from the path this test ran against
        # keeps the assertion about the output rather than about where the
        # checkout happens to live.
        assert REPO_ROOT.name in result.stdout

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
    """Missing-vector-store behavior must depend on test input only.

    These tests must not see a vector store id from the developer's .env or
    login shell, so they clear the process env and disable discovery.
    """

    @staticmethod
    def _isolated_env():
        """Process env with an API key but no vector store id."""
        env = patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"})
        env.start()
        os.environ.pop("OPENAI_VECTOR_STORE_ID", None)
        return env

    def test_cli_without_vector_store_exits_nonzero(self):
        from repo_signal.semantic_upload import main as semantic_upload_main

        env = self._isolated_env()
        try:
            with patch(
                "repo_signal.vectorstore.openai_store.load_dotenv_if_available",
                lambda: None,
            ):
                with pytest.raises(SystemExit) as excinfo:
                    semantic_upload_main([])
            assert excinfo.value.code != 0
        finally:
            env.stop()

    def test_cli_without_vector_store_prints_error(self, capsys):
        from repo_signal.semantic_upload import main as semantic_upload_main

        env = self._isolated_env()
        try:
            with patch(
                "repo_signal.vectorstore.openai_store.load_dotenv_if_available",
                lambda: None,
            ):
                with pytest.raises(SystemExit):
                    semantic_upload_main([])
            stderr = capsys.readouterr().err
        finally:
            env.stop()
        assert "vector store" in stderr.lower() or "OPENAI_VECTOR_STORE_ID" in stderr

    def test_upload_function_raises_on_missing_store(self):
        from repo_signal.vectorstore.openai_store import resolve_vector_store_id
        from repo_signal.ai.providers.base import ProviderConfigurationError

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ProviderConfigurationError):
                resolve_vector_store_id(None, discover=False)

    def test_discover_false_ignores_dotenv(self):
        """discover=False must not read .env, even when it holds an id."""
        from repo_signal.vectorstore import openai_store
        from repo_signal.ai.providers.base import ProviderConfigurationError

        def poisoned_dotenv():
            os.environ["OPENAI_VECTOR_STORE_ID"] = "vs_from_dotenv"

        with patch.dict(os.environ, {}, clear=True):
            with patch.object(openai_store, "load_dotenv_if_available", poisoned_dotenv):
                with pytest.raises(ProviderConfigurationError):
                    openai_store.resolve_vector_store_id(None, discover=False)

    def test_resolution_does_not_spawn_a_login_shell(self):
        """Vector store resolution must never shell out to the user's shell."""
        from repo_signal.vectorstore import openai_store

        from repo_signal.ai.providers.base import ProviderConfigurationError

        with patch.dict(os.environ, {}, clear=True):
            with patch.object(openai_store, "load_dotenv_if_available", lambda: None):
                with patch("subprocess.run") as run:
                    with pytest.raises(ProviderConfigurationError):
                        openai_store.resolve_vector_store_id(None)
        run.assert_not_called()


class TestNoShellDiscovery:
    """Configuration must be explicit and process-scoped.

    repo-signal never interrogates the user's login or interactive shell to
    manufacture configuration or credentials: it is slow, can hang, and hides
    runtime behavior in machine-local dotfiles.
    """

    def test_openai_client_does_not_spawn_a_shell(self):
        from repo_signal.vectorstore import openai_store
        from repo_signal.ai.providers.base import ProviderConfigurationError

        with patch.dict(os.environ, {}, clear=True):
            with patch.object(openai_store, "load_dotenv_if_available", lambda: None):
                with patch("subprocess.run") as run:
                    with pytest.raises(ProviderConfigurationError):
                        openai_store.openai_client()
        run.assert_not_called()

    def test_openai_client_discover_false_ignores_dotenv(self):
        from repo_signal.vectorstore import openai_store
        from repo_signal.ai.providers.base import ProviderConfigurationError

        def poisoned_dotenv():
            os.environ["OPENAI_API_KEY"] = "sk-from-dotenv"

        with patch.dict(os.environ, {}, clear=True):
            with patch.object(openai_store, "load_dotenv_if_available", poisoned_dotenv):
                with pytest.raises(ProviderConfigurationError):
                    openai_store.openai_client(discover=False)

    def test_openai_provider_does_not_spawn_a_shell(self):
        from repo_signal.ai.providers import openai_provider
        from repo_signal.ai.providers.base import ProviderConfigurationError

        with patch.dict(os.environ, {}, clear=True):
            with patch.object(openai_provider, "load_dotenv_if_available", lambda: None):
                with patch("subprocess.run") as run:
                    with pytest.raises(ProviderConfigurationError):
                        openai_provider.OpenAIProvider()
        run.assert_not_called()

    def test_openai_provider_discover_false_ignores_dotenv(self):
        from repo_signal.ai.providers import openai_provider
        from repo_signal.ai.providers.base import ProviderConfigurationError

        def poisoned_dotenv():
            os.environ["OPENAI_API_KEY"] = "sk-from-dotenv"

        with patch.dict(os.environ, {}, clear=True):
            with patch.object(openai_provider, "load_dotenv_if_available", poisoned_dotenv):
                with pytest.raises(ProviderConfigurationError):
                    openai_provider.OpenAIProvider(discover=False)

    def test_shell_discovery_helpers_are_gone(self):
        """The two near-duplicate zsh helpers must not come back."""
        from repo_signal.vectorstore import openai_store
        from repo_signal.ai.providers import openai_provider

        assert not hasattr(openai_store, "load_shell_env_if_available")
        assert not hasattr(openai_provider, "load_shell_openai_key_if_available")


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


import shutil

@pytest.mark.skipif(
    shutil.which("mq-agent") is None,
    reason="mq-agent not installed in this environment",
)
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
