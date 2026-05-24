"""Tests for mq ecosystem integration patterns."""
import importlib.util
import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
INTEGRATIONS = REPO_ROOT / "examples" / "integrations"


def _load_consumer():
    spec = importlib.util.spec_from_file_location(
        "mq_agent_consumer", INTEGRATIONS / "mq_agent_consumer.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestInspectSafeScript:
    def test_script_exists_and_is_executable(self):
        script = INTEGRATIONS / "inspect_safe.sh"
        assert script.exists()
        assert script.stat().st_mode & 0o111

    def test_runs_and_returns_inspect_v1(self):
        result = subprocess.run(
            ["bash", str(INTEGRATIONS / "inspect_safe.sh"), str(REPO_ROOT)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["schema"] == "inspect.v1"

    def test_output_is_valid_json(self):
        result = subprocess.run(
            ["bash", str(INTEGRATIONS / "inspect_safe.sh"), str(REPO_ROOT)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, dict)


class TestReadinessGateScript:
    def test_script_exists_and_is_executable(self):
        script = INTEGRATIONS / "readiness_gate.sh"
        assert script.exists()
        assert script.stat().st_mode & 0o111

    def test_passes_with_low_threshold(self):
        result = subprocess.run(
            ["bash", str(INTEGRATIONS / "readiness_gate.sh"), str(REPO_ROOT), "1"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "PASS" in result.stdout

    def test_fails_with_impossibly_high_threshold(self):
        result = subprocess.run(
            ["bash", str(INTEGRATIONS / "readiness_gate.sh"), str(REPO_ROOT), "999"],
            capture_output=True, text=True,
        )
        assert result.returncode != 0


class TestMqAgentConsumer:
    def test_inspect_returns_dict(self):
        mod = _load_consumer()
        result = mod.inspect(REPO_ROOT)
        assert result is not None
        assert result["schema"] == "inspect.v1"

    def test_inspect_returns_none_for_missing_repo_signal(self):
        mod = _load_consumer()
        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = mod.inspect(REPO_ROOT)
        assert result is None

    def test_doctor_returns_dict(self):
        mod = _load_consumer()
        result = mod.doctor(REPO_ROOT)
        assert result is not None
        assert result["schema"] == "doctor.v1"

    def test_repo_summary_returns_string(self):
        mod = _load_consumer()
        summary = mod.repo_summary(REPO_ROOT)
        assert isinstance(summary, str)
        assert "repo-signal" in summary
        assert "score=" in summary
