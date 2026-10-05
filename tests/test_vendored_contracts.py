"""Contracts repo-signal produces but mqobsidian owns.

repo-signal writes two records mqobsidian reads: `memory-observation.v1`
(memory_emit, during `inspect`) and `repo-review.v1` (review-export, whose
committed fixture is the published shape). The existing tests check those
records against key lists copied from the schemas by hand, which drift the
moment a schema changes. These validate against the schemas themselves.

The copies under schemas/vendor/ are byte-identical to mqobsidian's. CI checks
out mqobsidian and sets MQ_CANONICAL_MQOBSIDIAN_ROOT, so there drift fails the
build; locally the sibling checkout is used when present, and without one the
drift tests skip — drift unverified, not assumed absent.
"""
from __future__ import annotations

import json
import os
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from repo_signal.memory_emit import observation_from_inspect

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "schemas" / "vendor"
CONTRACTS = ("memory-observation.v1.json", "repo-review.v1.json")
REVIEW_FIXTURE = ROOT / "examples" / "review-export" / "repo-review.v1.md"

_explicit_root = os.environ.get("MQ_CANONICAL_MQOBSIDIAN_ROOT")
CANONICAL_ROOT = Path(_explicit_root or Path.home() / "mqobsidian").expanduser()


def _validator(name: str) -> Draft202012Validator:
    schema = json.loads((VENDOR / name).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _errors(validator: Draft202012Validator, doc: object) -> str:
    found = sorted(validator.iter_errors(doc), key=lambda e: list(e.path))
    return "\n".join(f"{list(e.path)}: {e.message}" for e in found)


class TestVendoredCopies(unittest.TestCase):
    def test_copies_match_canonical(self):
        for name in CONTRACTS:
            canonical = CANONICAL_ROOT / "schemas" / name
            with self.subTest(contract=name):
                if not canonical.is_file():
                    if _explicit_root:
                        self.fail(f"canonical schema missing: {canonical}")
                    self.skipTest(f"no mqobsidian checkout at {CANONICAL_ROOT}; drift unverified")
                self.assertEqual(
                    (VENDOR / name).read_bytes(),
                    canonical.read_bytes(),
                    f"schemas/vendor/{name} has drifted from {canonical} — re-copy, do not edit",
                )


class TestProducedRecordsConform(unittest.TestCase):
    def test_memory_observation_from_inspect(self):
        record = observation_from_inspect({
            "schema": "inspect.v1",
            "repo": {"exists": True, "name": "example-repo", "path": "example-repo"},
            "issues": [
                {"level": "fail", "message": "CHANGELOG is missing", "raw": "no CHANGELOG.md"},
                {"level": "warn", "message": "README has no install section"},
            ],
            "recommended_next_commit": "docs: add CHANGELOG",
            "git": {"branch": "main"},
        })
        self.assertIsNotNone(record)
        problems = _errors(_validator("memory-observation.v1.json"), record)
        self.assertEqual(problems, "", problems)

    def test_review_fixture_frontmatter(self):
        # Flat `key: value` frontmatter, read the way mqobsidian's
        # validate-export.py reads it.
        text = REVIEW_FIXTURE.read_text(encoding="utf-8")
        block = text.split("---\n", 2)[1]
        frontmatter = dict(line.split(": ", 1) for line in block.splitlines() if line.strip())
        problems = _errors(_validator("repo-review.v1.json"), frontmatter)
        self.assertEqual(problems, "", problems)


if __name__ == "__main__":
    unittest.main()
