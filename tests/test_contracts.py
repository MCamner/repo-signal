"""Schema contract tests for inspect.v1 and doctor.v1."""
import json
from pathlib import Path

import pytest

from repo_signal.doctor import doctor_repo
from repo_signal.inspect import inspect_repo

REPO_ROOT = Path(__file__).resolve().parents[1]


def _inspect() -> dict:
    return json.loads(inspect_repo(REPO_ROOT, output_format="json"))


def _doctor() -> dict:
    return json.loads(doctor_repo(REPO_ROOT, output_format="json"))


# ── inspect.v1 ─────────────────────────────────────────────────────────────

class TestInspectV1:
    def test_schema_field_is_inspect_v1(self):
        assert _inspect()["schema"] == "inspect.v1"

    def test_required_top_level_keys(self):
        result = _inspect()
        for key in ["schema", "repo", "core_files", "detected", "issues"]:
            assert key in result, f"Missing key: {key}"

    def test_repo_section_has_name_and_path(self):
        result = _inspect()
        assert "name" in result["repo"]
        assert "path" in result["repo"]

    def test_core_files_is_list(self):
        assert isinstance(_inspect()["core_files"], list)

    def test_core_file_items_have_label_and_exists(self):
        for item in _inspect()["core_files"]:
            assert "label" in item
            assert "exists" in item

    def test_json_roundtrip(self):
        raw = inspect_repo(REPO_ROOT, output_format="json")
        assert json.loads(raw)["schema"] == "inspect.v1"


# ── doctor.v1 ──────────────────────────────────────────────────────────────

class TestDoctorV1:
    def test_schema_field_is_doctor_v1(self):
        assert _doctor()["schema"] == "doctor.v1"

    def test_required_top_level_keys(self):
        result = _doctor()
        for key in ["schema", "repo", "scores", "summary"]:
            assert key in result, f"Missing key: {key}"

    def test_repo_section_has_name_and_path(self):
        result = _doctor()
        assert "name" in result["repo"]
        assert "path" in result["repo"]

    def test_scores_section_present(self):
        assert isinstance(_doctor()["scores"], dict)

    def test_json_roundtrip(self):
        raw = doctor_repo(REPO_ROOT, output_format="json")
        assert json.loads(raw)["schema"] == "doctor.v1"


# ── safe consumption pattern ───────────────────────────────────────────────

class TestSafeConsumption:
    def test_inspect_schema_check_pattern(self):
        result = _inspect()
        schema = result.get("schema", "unknown")
        assert schema == "inspect.v1", f"Unknown schema: {schema}"

    def test_doctor_schema_check_pattern(self):
        result = _doctor()
        schema = result.get("schema", "unknown")
        assert schema == "doctor.v1", f"Unknown schema: {schema}"

    def test_unknown_schema_is_detectable(self):
        fake = {"schema": "future.v99", "data": {}}
        assert fake.get("schema", "unknown") not in ("inspect.v1", "doctor.v1")
