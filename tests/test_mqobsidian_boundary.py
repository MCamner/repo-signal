"""The repo-signal -> mqobsidian boundary, proven end to end against a temp vault.

Ownership, which these tests encode rather than assume:

- repo-signal **produces** signals. It writes a review or appends an
  observation and stops there.
- mqobsidian **stores** them. It owns the vault layout and the durable notes.
- mq-agent owns **scoring, promotion and workflow orchestration**. An
  observation is a proposal, not a memory; nothing here promotes anything.

Both export paths default to a real vault — `MQ_OBSIDIAN_DIR`, else
`~/mqobsidian` — which on a developer machine holds live notes. Every test
below therefore points the vault at `tmp_path` and asserts that the durable
default was not consulted, so running the suite can never append to a real
vault. See docs/MQOBSIDIAN_BOUNDARY.md.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from repo_signal.memory_emit import (
    emit_from_inspect,
    maybe_emit_memory,
    surface_path,
    vault_dir,
)
from repo_signal.redaction import is_machine_local_path
from repo_signal.review_export import build_repo_review, export_repo_review, resolve_vault

REPO_ROOT = Path(__file__).resolve().parents[1]

OBSERVATION_SURFACE = Path("memory/observations/repo-signal.observations.jsonl")


needs_unprivileged = pytest.mark.skipif(
    hasattr(os, "geteuid") and os.geteuid() == 0,
    reason="chmod does not restrict root, so an unwritable path cannot be simulated",
)


@pytest.fixture
def vault(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """An empty temporary vault that is also the only vault discovery can find.

    `HOME` is redirected as well: the default when `MQ_OBSIDIAN_DIR` is unset is
    `~/mqobsidian`, so a test that forgets the env var would otherwise reach a
    developer's real notes.
    """
    path = tmp_path / "vault"
    path.mkdir()
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("MQ_OBSIDIAN_DIR", str(path))
    monkeypatch.setenv("HOME", str(home))
    return path


@pytest.fixture
def inspect_data() -> dict:
    """One real inspect.v1 result, the input both export paths consume."""
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


def vault_files(vault: Path) -> set[str]:
    return {
        str(p.relative_to(vault)) for p in vault.rglob("*") if p.is_file()
    }


def front_matter(text: str) -> dict[str, str]:
    """Parse the review's YAML-ish front matter without a YAML dependency."""
    assert text.startswith("---\n")
    block = text.split("---\n", 2)[1]
    fields = {}
    for line in block.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


class TestReviewExportSmoke:
    """inspect -> review export -> schema read, against a temporary vault."""

    def test_round_trip_preserves_both_schemas(self, vault: Path, inspect_data: dict):
        written = export_repo_review(
            inspect_data, vault=vault, created_at="2026-07-13T12:00:00Z"
        )

        assert written.is_file()
        fields = front_matter(written.read_text(encoding="utf-8"))
        assert fields["schema"] == "repo-review.v1"
        assert fields["source_schema"] == "inspect.v1"
        assert fields["repo"] == "demo-repo"
        assert fields["created_at"] == "2026-07-13T12:00:00Z"

    def test_writes_exactly_one_file_and_only_under_reviews(
        self, vault: Path, inspect_data: dict
    ):
        export_repo_review(inspect_data, vault=vault, created_at="2026-07-13T12:00:00Z")

        assert vault_files(vault) == {"reviews/2026-07-13-repo-signal-demo-repo.md"}

    def test_export_leaves_existing_notes_alone(self, vault: Path, inspect_data: dict):
        note = vault / "notes" / "durable.md"
        note.parent.mkdir()
        note.write_text("hand-written\n", encoding="utf-8")

        export_repo_review(inspect_data, vault=vault, created_at="2026-07-13T12:00:00Z")

        assert note.read_text(encoding="utf-8") == "hand-written\n"

    def test_cli_round_trip_into_a_temporary_vault(self, vault: Path, tmp_path: Path):
        """The full CLI path: inspect a real checkout, read the review back."""
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
        written = [p for p in (vault / "reviews").glob("*.md")]
        assert len(written) == 1
        fields = front_matter(written[0].read_text(encoding="utf-8"))
        assert fields["schema"] == "repo-review.v1"
        assert fields["source_schema"] == "inspect.v1"
        assert fields["repo"] == REPO_ROOT.name


class TestObservationSmoke:
    """inspect -> observation append, without touching durable notes."""

    def test_append_creates_only_the_observation_surface(
        self, vault: Path, inspect_data: dict
    ):
        surface = emit_from_inspect(inspect_data)

        assert surface == surface_path(vault)
        assert vault_files(vault) == {str(OBSERVATION_SURFACE)}

    def test_appended_record_declares_the_observation_schema(
        self, vault: Path, inspect_data: dict
    ):
        surface = emit_from_inspect(inspect_data)

        lines = surface.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["schema"] == "memory-observation.v1"
        assert record["producer"] == "repo-signal"
        assert record["repository"] == "demo-repo"

    def test_observation_is_a_proposal_not_a_promoted_memory(
        self, vault: Path, inspect_data: dict
    ):
        """Scoring and promotion belong to mq-agent, so nothing here does either."""
        surface = emit_from_inspect(inspect_data)
        record = json.loads(surface.read_text(encoding="utf-8").strip())

        assert "proposed_memory_key" in record
        for owned_elsewhere in ("score", "promoted", "memory_key", "rank"):
            assert owned_elsewhere not in record

    def test_append_leaves_durable_notes_untouched(self, vault: Path, inspect_data: dict):
        note = vault / "memory" / "learn" / "repos" / "demo-repo.md"
        note.parent.mkdir(parents=True)
        note.write_text("promoted memory\n", encoding="utf-8")

        emit_from_inspect(inspect_data)

        assert note.read_text(encoding="utf-8") == "promoted memory\n"
        assert vault_files(vault) == {
            "memory/learn/repos/demo-repo.md",
            str(OBSERVATION_SURFACE),
        }

    def test_appending_twice_keeps_both_records(self, vault: Path, inspect_data: dict):
        emit_from_inspect(inspect_data)
        surface = emit_from_inspect(inspect_data)

        lines = surface.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        assert all(json.loads(line)["schema"] == "memory-observation.v1" for line in lines)

    def test_live_hook_is_opt_in(self, vault: Path, inspect_data: dict, monkeypatch):
        monkeypatch.delenv("REPO_SIGNAL_EMIT_MEMORY", raising=False)

        assert maybe_emit_memory(inspect_data) is None
        assert vault_files(vault) == set()

    def test_live_hook_writes_when_enabled(self, vault: Path, inspect_data: dict, monkeypatch):
        monkeypatch.setenv("REPO_SIGNAL_EMIT_MEMORY", "1")

        assert maybe_emit_memory(inspect_data) == surface_path(vault)
        assert vault_files(vault) == {str(OBSERVATION_SURFACE)}


class TestDurableVaultIsNeverReached:
    """The default vault is a real one; the suite must never resolve to it."""

    def test_discovery_resolves_to_the_temporary_vault(self, vault: Path):
        assert vault_dir() == vault

    def test_discovery_returns_none_when_no_vault_exists(self, tmp_path, monkeypatch):
        monkeypatch.setenv("MQ_OBSIDIAN_DIR", str(tmp_path / "absent"))
        monkeypatch.setenv("HOME", str(tmp_path / "home-without-a-vault"))

        assert vault_dir() is None

    def test_emission_is_silent_without_a_vault(self, tmp_path, monkeypatch, inspect_data):
        monkeypatch.setenv("MQ_OBSIDIAN_DIR", str(tmp_path / "absent"))
        monkeypatch.setenv("HOME", str(tmp_path / "home-without-a-vault"))

        assert emit_from_inspect(inspect_data) is None


class TestFailureBehavior:
    """Documented in docs/MQOBSIDIAN_BOUNDARY.md; asserted here."""

    def test_missing_vault_raises_a_named_error(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError, match="mqobsidian vault not found"):
            resolve_vault(tmp_path / "absent")

    def test_unknown_source_schema_is_refused(self, inspect_data: dict):
        inspect_data["schema"] = "inspect.v2"

        with pytest.raises(ValueError, match="expected inspect.v1"):
            build_repo_review(inspect_data)

    def test_missing_repository_is_refused(self, inspect_data: dict):
        inspect_data["repo"]["exists"] = False

        with pytest.raises(ValueError, match="missing repository"):
            build_repo_review(inspect_data)

    def test_overwrite_requires_force(self, vault: Path, inspect_data: dict):
        export_repo_review(inspect_data, vault=vault, created_at="2026-07-13T12:00:00Z")

        with pytest.raises(FileExistsError, match="use --force"):
            export_repo_review(inspect_data, vault=vault, created_at="2026-07-13T13:00:00Z")

    @needs_unprivileged
    def test_unwritable_output_raises_permission_error(self, vault: Path, inspect_data: dict):
        reviews = vault / "reviews"
        reviews.mkdir()
        reviews.chmod(0o500)
        try:
            with pytest.raises(PermissionError):
                export_repo_review(
                    inspect_data, vault=vault, created_at="2026-07-13T12:00:00Z"
                )
        finally:
            reviews.chmod(0o700)

    @pytest.mark.parametrize(
        "case,argv_vault,expected",
        [
            ("missing vault", "absent", "mqobsidian vault not found"),
            ("unwritable vault", "readonly", "Permission denied"),
        ],
    )
    @needs_unprivileged
    def test_cli_reports_io_failure_without_a_traceback(
        self, tmp_path: Path, case: str, argv_vault: str, expected: str
    ):
        """An I/O fault against someone else's vault must read, not dump a stack.

        `PermissionError` is neither `FileNotFoundError` nor `FileExistsError`,
        so an unwritable vault escaped the CLI's handler and printed a traceback.
        """
        target = tmp_path / argv_vault
        if argv_vault == "readonly":
            (target / "reviews").mkdir(parents=True)
            (target / "reviews").chmod(0o500)

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "repo_signal.cli",
                    "review-export",
                    str(REPO_ROOT),
                    "--vault",
                    str(target),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        finally:
            if argv_vault == "readonly":
                (target / "reviews").chmod(0o700)

        assert result.returncode == 2, result.stdout
        assert "Traceback" not in result.stderr
        assert expected in result.stdout

    def test_emission_failure_does_not_break_the_caller(self, vault: Path, inspect_data, monkeypatch):
        """A failed emission must not change any other repo-signal behaviour."""
        monkeypatch.setenv("REPO_SIGNAL_EMIT_MEMORY", "1")
        surface = surface_path(vault)
        surface.parent.mkdir(parents=True)
        # A directory where the surface file belongs: appending must fail.
        surface.mkdir()

        assert maybe_emit_memory(inspect_data) is None


class TestIntegrationExample:
    """`mqobsidian_export.sh` is the copyable version of this boundary.

    An example that only works on the machine it was written on teaches the
    wrong thing, so it is held to the same path invariant as the exports.
    """

    SCRIPT = REPO_ROOT / "examples" / "integrations" / "mqobsidian_export.sh"

    def test_script_exists_and_is_executable(self):
        assert self.SCRIPT.exists()
        assert self.SCRIPT.stat().st_mode & 0o111

    def test_script_uses_the_documented_environment_variable(self):
        assert "MQ_OBSIDIAN_DIR" in self.SCRIPT.read_text(encoding="utf-8")

    def test_script_contains_no_user_specific_absolute_path(self):
        """A home directory baked into an example teaches the wrong thing.

        Placeholders like `/path/to/repo` are fine — `is_machine_local_path`
        would flag them, but the invariant it guards is about the content of
        exported artifacts, not about prose in a usage comment. What must not
        appear is a path that only resolves on one person's machine.
        """
        content = self.SCRIPT.read_text(encoding="utf-8")

        assert str(Path.home()) not in content
        offenders = re.findall(r"(?:/Users/|/home/|[A-Za-z]:\\Users\\)\w+", content)
        assert offenders == [], offenders

    def test_the_invariant_helper_still_flags_a_real_home_path(self):
        """Guards the test above: the shape rule it relies on is still live."""
        assert is_machine_local_path(str(Path.home() / "mqobsidian"))
        assert not is_machine_local_path("MQ_OBSIDIAN_DIR")

    def test_script_requires_an_explicit_vault(self, tmp_path: Path):
        """Unset MQ_OBSIDIAN_DIR must stop the script, not fall back to ~."""
        env = {k: v for k, v in os.environ.items() if k != "MQ_OBSIDIAN_DIR"}
        result = subprocess.run(
            ["bash", str(self.SCRIPT), str(REPO_ROOT)],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )

        assert result.returncode == 1
        assert "MQ_OBSIDIAN_DIR is not set" in result.stderr

    def test_script_rejects_a_vault_that_is_not_a_directory(self, tmp_path: Path):
        result = subprocess.run(
            ["bash", str(self.SCRIPT), str(REPO_ROOT)],
            capture_output=True,
            text=True,
            env={**os.environ, "MQ_OBSIDIAN_DIR": str(tmp_path / "absent")},
            check=False,
        )

        assert result.returncode == 1
        assert "not a directory" in result.stderr
