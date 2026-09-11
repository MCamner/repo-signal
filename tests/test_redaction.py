"""Contract: exported artifacts carry logical identity, not machine location.

`evidence.reference` and every other exported reference MUST NOT contain an
absolute machine-local filesystem path. Repository identities (`repo-signal`)
and repository-relative paths (`repo_signal/memory_emit.py`) are permitted.

The rule is expressed as an invariant over path *shape*, not as a patch for the
one platform this was found on. `/Users/...` was the observed leak; `/home/...`,
`C:\\Users\\...`, UNC shares and `~/...` are the same defect on another machine.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from repo_signal.redaction import is_machine_local_path, redact_reference

MACHINE_LOCAL = [
    "/Users/mansys/repo-signal",
    "/Users/mansys/repo-signal/repo_signal/memory_emit.py",
    "/home/user/repo-signal",
    "/home/runner/work/repo-signal/repo-signal",
    "/var/folders/xy/T/tmp1234/repo",
    "C:\\Users\\foo\\repo-signal",
    "C:/Users/foo/repo-signal",
    "D:\\projects\\repo-signal",
    "\\\\fileserver\\share\\repo-signal",
    "~/repo-signal",
    "~mansys/repo-signal",
]

LOGICAL = [
    "repo-signal",
    "mq-mcp",
    "repo_signal/memory_emit.py",
    "docs/ROADMAP.md",
    "./docs/ROADMAP.md",
    "tests/test_redaction.py",
    "repo-signal inspect.v1",
]


class TestPathShapeInvariant(unittest.TestCase):
    def test_machine_local_paths_are_rejected(self):
        for value in MACHINE_LOCAL:
            with self.subTest(value=value):
                self.assertTrue(
                    is_machine_local_path(value),
                    f"{value!r} is machine-local and must be rejected",
                )

    def test_logical_references_are_accepted(self):
        for value in LOGICAL:
            with self.subTest(value=value):
                self.assertFalse(
                    is_machine_local_path(value),
                    f"{value!r} is a logical identity and must be accepted",
                )

    def test_empty_and_non_string_values_are_not_paths(self):
        for value in ("", "   ", None, 42, [], {}):
            with self.subTest(value=value):
                self.assertFalse(is_machine_local_path(value))


class TestRedactReference(unittest.TestCase):
    def test_repo_root_becomes_the_repo_name(self):
        self.assertEqual(
            redact_reference(
                "/Users/mansys/repo-signal",
                repo_root="/Users/mansys/repo-signal",
                repo_name="repo-signal",
            ),
            "repo-signal",
        )

    def test_path_inside_the_repo_becomes_repo_relative(self):
        self.assertEqual(
            redact_reference(
                "/Users/mansys/repo-signal/repo_signal/memory_emit.py",
                repo_root="/Users/mansys/repo-signal",
                repo_name="repo-signal",
            ),
            "repo_signal/memory_emit.py",
        )

    def test_windows_path_inside_the_repo_becomes_posix_relative(self):
        self.assertEqual(
            redact_reference(
                "C:\\Users\\foo\\repo-signal\\docs\\ROADMAP.md",
                repo_root="C:\\Users\\foo\\repo-signal",
                repo_name="repo-signal",
            ),
            "docs/ROADMAP.md",
        )

    def test_path_outside_the_repo_falls_back_to_the_repo_name(self):
        self.assertEqual(
            redact_reference(
                "/etc/passwd",
                repo_root="/Users/mansys/repo-signal",
                repo_name="repo-signal",
            ),
            "repo-signal",
        )

    def test_logical_reference_passes_through_untouched(self):
        for value in ("repo-signal", "docs/ROADMAP.md"):
            with self.subTest(value=value):
                self.assertEqual(
                    redact_reference(
                        value, repo_root="/Users/mansys/repo-signal", repo_name="repo-signal"
                    ),
                    value,
                )

    def test_redacted_output_is_never_machine_local(self):
        """The invariant that matters: whatever goes in, nothing local comes out."""
        for value in MACHINE_LOCAL + LOGICAL:
            with self.subTest(value=value):
                result = redact_reference(
                    value, repo_root="/Users/mansys/repo-signal", repo_name="repo-signal"
                )
                self.assertFalse(
                    is_machine_local_path(result),
                    f"{value!r} redacted to {result!r}, still machine-local",
                )

    def test_missing_repo_root_still_redacts(self):
        self.assertEqual(
            redact_reference(
                "/home/user/other-repo", repo_root=None, repo_name="other-repo"
            ),
            "other-repo",
        )


if __name__ == "__main__":
    unittest.main()
