"""The human `inspect` rendering may clarify a label; `inspect.v1` may not.

`core_files` is a presence inventory: `exists = (repo / rel_path).exists()`,
status `ok`/`missing`. Nothing more is claimed, and nothing more may be read
into it. But the human label "Screenshots/output gallery" read as a claim about
content, so an empty folder printed

    - [OK] Screenshots/output gallery: docs/screenshots
    - [WARN] Publish checklist is not perfect (15/16): ... add at least one image

and the two lines looked like a contradiction. Only the text rendering is
clarified. `inspect.v1` is an integration contract: its labels, its `exists`
predicate and its issue strings stay exactly as they were. If `inspect` should
ever carry "the gallery has content" itself, that belongs in `inspect.v2` or a
new field — not in a changed meaning for `exists`.
"""

from __future__ import annotations

import json
from pathlib import Path

from repo_signal.inspect import inspect_repo, inspect_repo_data

CONTRACT_LABEL = "Screenshots/output gallery"
TEXT_LABEL = "Screenshots/output directory"


def _repo(tmp_path: Path) -> Path:
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    return tmp_path


def _empty_gallery(tmp_path: Path) -> Path:
    root = _repo(tmp_path)
    (root / "docs" / "screenshots").mkdir()
    return root


def _core_file(data: dict, path: str) -> dict:
    for record in data["core_files"]:
        if record["path"] == path:
            return record
    raise AssertionError(f"core file not found: {path}")


class TestTextRendering:
    def test_empty_directory_is_described_as_a_directory(self, tmp_path: Path):
        text = inspect_repo(str(_empty_gallery(tmp_path)))

        assert f"- [OK] {TEXT_LABEL}: docs/screenshots" in text

    def test_text_does_not_call_an_empty_directory_a_gallery(self, tmp_path: Path):
        """The exact wording difference this change exists to produce."""
        text = inspect_repo(str(_empty_gallery(tmp_path)))

        assert CONTRACT_LABEL not in text

    def test_a_populated_directory_renders_the_same_way(self, tmp_path: Path):
        """The label is about what core_files measures, not about content."""
        root = _empty_gallery(tmp_path)
        (root / "docs" / "screenshots" / "demo.png").write_bytes(b"\x89PNG\r\n\x1a\n")

        assert f"- [OK] {TEXT_LABEL}: docs/screenshots" in inspect_repo(str(root))

    def test_a_missing_directory_still_renders_the_clarified_label(self, tmp_path: Path):
        text = inspect_repo(str(_repo(tmp_path)))

        assert f"- [MISSING] {TEXT_LABEL}: docs/screenshots" in text

    def test_other_core_file_labels_are_untouched(self, tmp_path: Path):
        text = inspect_repo(str(_empty_gallery(tmp_path)))

        assert "- [OK] README: README.md" in text
        assert "- [MISSING] Examples folder: examples" in text


class TestContractIsUnchanged:
    def test_json_keeps_the_contract_label(self, tmp_path: Path):
        data = json.loads(inspect_repo(str(_empty_gallery(tmp_path)), "json"))

        assert _core_file(data, "docs/screenshots")["label"] == CONTRACT_LABEL

    def test_json_keeps_the_presence_predicate(self, tmp_path: Path):
        """An empty directory exists. core_files says only that."""
        record = _core_file(inspect_repo_data(str(_empty_gallery(tmp_path))), "docs/screenshots")

        assert record["exists"] is True
        assert record["status"] == "ok"
        assert record["importance"] == "optional"

    def test_json_issue_wording_is_unchanged_when_missing(self, tmp_path: Path):
        data = inspect_repo_data(str(_repo(tmp_path)))
        raw = [issue["raw"] for issue in data["issues"]]

        assert f"[OPTIONAL] Missing {CONTRACT_LABEL}: docs/screenshots" in raw

    def test_clarification_never_reaches_the_contract(self, tmp_path: Path):
        """No inspect.v1 payload may contain the text-only wording."""
        missing = tmp_path / "missing"
        empty = tmp_path / "empty"
        missing.mkdir()
        empty.mkdir()

        for root in (_repo(missing), _empty_gallery(empty)):
            payload = inspect_repo(str(root), "json")
            assert TEXT_LABEL not in payload

    def test_schema_is_still_inspect_v1(self, tmp_path: Path):
        assert inspect_repo_data(str(_empty_gallery(tmp_path)))["schema"] == "inspect.v1"
