"""`memory-observation.v1` emission: schema, gating, isolation, redaction.

An observation is a *proposal*, not promoted memory. repo-signal produces it;
mqobsidian stores it; mq-agent owns scoring and promotion. Nothing here may
score, promote, or write outside the observation surface.
"""
from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from repo_signal.memory_emit import (
    PRODUCER,
    SCHEMA,
    emit_from_inspect,
    maybe_emit_memory,
    observation_from_inspect,
    surface_path,
    vault_dir,
)
from repo_signal.redaction import is_machine_local_path

REQUIRED_FIELDS = {
    "schema",
    "id",
    "timestamp",
    "producer",
    "repository",
    "workflow",
    "title",
    "summary",
    "observation",
    "category",
    "confidence",
    "evidence",
    "tags",
    "proposed_memory_key",
}


def inspect_data(**overrides):
    data = {
        "schema": "inspect.v1",
        "repo": {
            "exists": True,
            "name": "repo-signal",
            "path": "/Users/mansys/repo-signal",
        },
        "issues": [
            {"level": "warn", "message": "README has no install section"},
            {"level": "fail", "message": "CHANGELOG is missing", "raw": "no CHANGELOG.md"},
            {"level": "info", "message": "consider adding a demo"},
        ],
        "recommended_next_commit": "docs: add CHANGELOG",
        "git": {"branch": "main"},
    }
    data.update(overrides)
    return data


class TestObservationSchema(unittest.TestCase):
    def test_record_carries_every_required_field(self):
        record = observation_from_inspect(inspect_data())
        self.assertIsNotNone(record)
        self.assertEqual(REQUIRED_FIELDS - set(record), set())

    def test_schema_and_producer_are_the_contract_values(self):
        record = observation_from_inspect(inspect_data())
        self.assertEqual(record["schema"], "memory-observation.v1")
        self.assertEqual(record["schema"], SCHEMA)
        self.assertEqual(record["producer"], PRODUCER)

    def test_the_most_severe_issue_wins(self):
        record = observation_from_inspect(inspect_data())
        self.assertEqual(record["title"], "CHANGELOG is missing")
        self.assertEqual(record["confidence"], 0.8)

    def test_record_is_json_serializable(self):
        record = observation_from_inspect(inspect_data())
        self.assertEqual(json.loads(json.dumps(record))["schema"], SCHEMA)

    def test_record_carries_no_scoring_or_promotion_fields(self):
        """An observation is a proposal; scoring and promotion live elsewhere."""
        record = observation_from_inspect(inspect_data())
        for forbidden in ("score", "status", "promoted", "memory_key", "decision"):
            with self.subTest(field=forbidden):
                self.assertNotIn(forbidden, record)


class TestNoIssueBehavior(unittest.TestCase):
    def test_no_issues_emits_nothing(self):
        self.assertIsNone(observation_from_inspect(inspect_data(issues=[])))

    def test_blank_messages_emit_nothing(self):
        data = inspect_data(issues=[{"level": "warn", "message": "   "}])
        self.assertIsNone(observation_from_inspect(data))

    def test_missing_repo_emits_nothing(self):
        data = inspect_data(repo={"exists": False, "name": "gone"})
        self.assertIsNone(observation_from_inspect(data))

    def test_nothing_is_written_when_there_is_nothing_to_say(self):
        with TemporaryDirectory() as tmp:
            surface = Path(tmp) / "memory" / "observations" / "repo-signal.observations.jsonl"
            self.assertIsNone(
                emit_from_inspect(inspect_data(issues=[]), surface=surface)
            )
            self.assertFalse(surface.exists())


class TestRedaction(unittest.TestCase):
    def test_evidence_reference_is_not_machine_local(self):
        record = observation_from_inspect(inspect_data())
        reference = record["evidence"][0]["reference"]
        self.assertFalse(
            is_machine_local_path(reference),
            f"evidence.reference leaked a machine-local path: {reference!r}",
        )
        self.assertEqual(reference, "repo-signal")

    def test_reference_stays_logical_across_platforms(self):
        for path in (
            "/Users/mansys/repo-signal",
            "/home/runner/work/repo-signal/repo-signal",
            "C:\\Users\\foo\\repo-signal",
            "\\\\fileserver\\share\\repo-signal",
        ):
            with self.subTest(path=path):
                data = inspect_data(
                    repo={"exists": True, "name": "repo-signal", "path": path}
                )
                reference = observation_from_inspect(data)["evidence"][0]["reference"]
                self.assertFalse(is_machine_local_path(reference))

    def test_no_field_of_the_record_contains_a_machine_local_path(self):
        record = observation_from_inspect(inspect_data())

        def walk(value, trail="record"):
            if isinstance(value, dict):
                for key, item in value.items():
                    walk(item, f"{trail}.{key}")
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    walk(item, f"{trail}[{index}]")
            elif is_machine_local_path(value):
                self.fail(f"{trail} leaked a machine-local path: {value!r}")

        walk(record)


class TestOptInGating(unittest.TestCase):
    def test_no_emission_without_the_env_flag(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(maybe_emit_memory(inspect_data()))

    def test_no_emission_when_the_flag_is_not_exactly_one(self):
        for value in ("0", "true", "yes", ""):
            with self.subTest(value=value):
                with mock.patch.dict(
                    os.environ, {"REPO_SIGNAL_EMIT_MEMORY": value}, clear=True
                ):
                    self.assertIsNone(maybe_emit_memory(inspect_data()))

    def test_emission_happens_when_opted_in(self):
        with TemporaryDirectory() as tmp:
            vault = Path(tmp)
            (vault / "memory").mkdir()
            with mock.patch.dict(
                os.environ,
                {"REPO_SIGNAL_EMIT_MEMORY": "1", "MQ_OBSIDIAN_DIR": str(vault)},
                clear=True,
            ):
                written = maybe_emit_memory(inspect_data())
            self.assertIsNotNone(written)
            self.assertEqual(written, surface_path(vault))
            lines = written.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            self.assertEqual(json.loads(lines[0])["schema"], SCHEMA)


class TestFailureIsolation(unittest.TestCase):
    def test_a_write_fault_never_raises_into_the_caller(self):
        with mock.patch.dict(os.environ, {"REPO_SIGNAL_EMIT_MEMORY": "1"}, clear=True):
            with mock.patch(
                "repo_signal.memory_emit.emit_from_inspect",
                side_effect=OSError("disk full"),
            ):
                self.assertIsNone(maybe_emit_memory(inspect_data()))

    def test_a_malformed_record_never_raises_into_the_caller(self):
        with mock.patch.dict(os.environ, {"REPO_SIGNAL_EMIT_MEMORY": "1"}, clear=True):
            with mock.patch(
                "repo_signal.memory_emit.observation_from_inspect",
                side_effect=KeyError("repo"),
            ):
                self.assertIsNone(maybe_emit_memory(inspect_data()))

    def test_a_missing_vault_is_silent_rather_than_a_guess(self):
        with TemporaryDirectory() as tmp:
            absent = Path(tmp) / "no-such-vault"
            with mock.patch.dict(
                os.environ,
                {"REPO_SIGNAL_EMIT_MEMORY": "1", "MQ_OBSIDIAN_DIR": str(absent)},
                clear=True,
            ):
                with mock.patch("repo_signal.memory_emit.Path.home", return_value=Path(tmp)):
                    self.assertIsNone(maybe_emit_memory(inspect_data()))
            self.assertFalse(absent.exists())

    def test_appending_preserves_earlier_observations(self):
        with TemporaryDirectory() as tmp:
            surface = Path(tmp) / "observations.jsonl"
            emit_from_inspect(inspect_data(), surface=surface)
            emit_from_inspect(inspect_data(), surface=surface)
            lines = surface.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 2)
            for line in lines:
                self.assertEqual(json.loads(line)["schema"], SCHEMA)


class TestVaultResolution(unittest.TestCase):
    def test_env_var_wins_when_it_points_at_a_real_directory(self):
        with TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {"MQ_OBSIDIAN_DIR": tmp}, clear=True):
                self.assertEqual(vault_dir(), Path(tmp))

    def test_no_vault_resolves_to_none_rather_than_a_guessed_path(self):
        with TemporaryDirectory() as tmp:
            with mock.patch.dict(
                os.environ, {"MQ_OBSIDIAN_DIR": str(Path(tmp) / "absent")}, clear=True
            ):
                with mock.patch("repo_signal.memory_emit.Path.home", return_value=Path(tmp)):
                    self.assertIsNone(vault_dir())


if __name__ == "__main__":
    unittest.main()
