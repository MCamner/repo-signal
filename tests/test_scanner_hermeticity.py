"""A scan describes the repository, not the machine it is sitting on.

`scan_repository` walked the filesystem and filtered through a hand-maintained
`IGNORE_DIRS` denylist. That list cannot keep up: this checkout carries 259
tracked files and 2,604 gitignored ones, and `.repo-signal/`, `.cursor/` and
`.codegraph/` were all absent from the list. The consequence reached a public
artifact — `examples/inspect/inspect.txt` published

    Top directories: . (11), .claude (2), .github (7), .repo-signal (9), ...

naming a gitignored directory, with a file count, in a committed example.

Git already knows what belongs to the repository, so the scan asks it instead of
maintaining a second opinion. Untracked files that are *not* ignored still
count: work in progress is part of the repository, it just is not committed yet.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

from repo_signal.core.scanner import scan_repository


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A git repo with one tracked file. No commit needed: `ls-files` reads the index."""
    root = tmp_path / "repo-signal"
    root.mkdir()
    _git(root, "init", "-q")
    (root / "README.md").write_text("# Demo\n", encoding="utf-8")
    (root / "kept.py").write_text("def kept():\n    return 1\n", encoding="utf-8")
    _git(root, "add", "README.md", "kept.py")
    return root


def _paths(root: Path) -> set[str]:
    return {node.path for node in scan_repository(root).files}


def _ignore(root: Path, *patterns: str) -> None:
    (root / ".gitignore").write_text("\n".join(patterns) + "\n", encoding="utf-8")
    _git(root, "add", ".gitignore")


class TestGitIgnoreIsRespected:
    def test_tracked_files_are_scanned(self, repo: Path):
        assert {"README.md", "kept.py"} <= _paths(repo)

    def test_ignored_directory_is_not_scanned(self, repo: Path):
        _ignore(repo, ".cursor/", ".codegraph/")
        (repo / ".cursor").mkdir()
        (repo / ".cursor" / "rules.md").write_text("local\n", encoding="utf-8")
        (repo / ".codegraph").mkdir()
        (repo / ".codegraph" / "index.py").write_text("x = 1\n", encoding="utf-8")

        paths = _paths(repo)
        assert not [p for p in paths if p.startswith((".cursor/", ".codegraph/"))]

    def test_ignored_directory_does_not_reach_top_directories(self, repo: Path):
        _ignore(repo, ".cursor/")
        (repo / ".cursor").mkdir()
        (repo / ".cursor" / "rules.md").write_text("local\n", encoding="utf-8")

        assert ".cursor" not in scan_repository(repo).top_directories

    def test_untracked_but_not_ignored_files_still_count(self, repo: Path):
        """Work in progress is part of the repository; it just is not committed."""
        (repo / "new_work.py").write_text("def wip():\n    return 2\n", encoding="utf-8")

        assert "new_work.py" in _paths(repo)

    def test_ignored_file_outside_a_directory_is_skipped(self, repo: Path):
        _ignore(repo, "secrets.env")
        (repo / "secrets.env").write_text("TOKEN=x\n", encoding="utf-8")

        assert "secrets.env" not in _paths(repo)


class TestAcceptanceCriterion:
    """The roadmap's v1.7.0 gate, asserted directly."""

    def test_gitignored_directories_do_not_change_the_scan(self, repo: Path):
        _ignore(repo, ".cursor/", ".codegraph/", "local-notes/")
        before = scan_repository(repo)

        for name in (".cursor", ".codegraph", "local-notes"):
            directory = repo / name
            directory.mkdir()
            (directory / "a.py").write_text("x = 1\n", encoding="utf-8")
            (directory / "b.md").write_text("# local\n", encoding="utf-8")

        after = scan_repository(repo)

        assert _paths(repo) == {node.path for node in before.files}
        assert after.languages == before.languages
        assert after.top_directory_counts == before.top_directory_counts
        assert after.size_bytes == before.size_bytes


class TestNonGitDirectories:
    def test_a_plain_directory_is_still_scanned(self, tmp_path: Path):
        """Without git there is no ignore information, so nothing changes."""
        root = tmp_path / "plain"
        root.mkdir()
        (root / "a.py").write_text("x = 1\n", encoding="utf-8")

        assert "a.py" in _paths(root)

    def test_the_builtin_denylist_still_applies_without_git(self, tmp_path: Path):
        root = tmp_path / "plain"
        (root / "__pycache__").mkdir(parents=True)
        (root / "__pycache__" / "a.py").write_text("x = 1\n", encoding="utf-8")
        (root / "b.py").write_text("x = 1\n", encoding="utf-8")

        paths = _paths(root)
        assert "b.py" in paths
        assert not [p for p in paths if p.startswith("__pycache__/")]


REPO_ROOT = Path(__file__).resolve().parents[1]


def _ignored_top_level(root: Path) -> set[str]:
    """Top-level entries git ignores in this checkout, asked of git directly."""
    result = subprocess.run(
        ["git", "ls-files", "--others", "--ignored", "--exclude-standard", "--directory"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    names = set()
    for line in result.stdout.splitlines():
        entry = line.strip().rstrip("/")
        if entry and "/" not in entry:
            names.add(entry)
    return names


class TestCommittedExamplesNameNothingIgnored:
    """A generated example is a public artifact; it must not name local-only paths.

    `examples/inspect/inspect.txt` published `.repo-signal (9)` in its top
    directories, and `examples/exports/symbol_index.json` carried
    `.repo-signal/chroma/chroma.sqlite3` nine times. Both are gitignored.

    The ignored set is asked of git rather than hard-coded, so a new local tool
    directory is covered the day it appears.
    """

    # examples/integrations/ is hand-written source, not generated output. It
    # names `.repo-signal/exports` on purpose: that is where `repo-signal
    # export` writes, and documenting it is the point of the example.
    HAND_WRITTEN = ("integrations",)

    # `.DS_Store` is the subject of a hygiene check, so reports name it by
    # design -- "[OK] No `.DS_Store` files found" is the check passing, not a
    # leaked path. Subject matter, not content.
    NAMED_BY_DESIGN = {".DS_Store"}

    def _generated_examples(self) -> list[Path]:
        return [
            path
            for path in (REPO_ROOT / "examples").rglob("*")
            if path.is_file()
            and path.suffix in {".txt", ".json", ".md"}
            and not any(part in self.HAND_WRITTEN for part in path.relative_to(REPO_ROOT).parts)
        ]

    def test_there_are_examples_to_check(self):
        assert self._generated_examples(), "no generated examples found; gate is vacuous"

    def test_git_reports_ignored_entries_to_check_against(self):
        assert _ignored_top_level(REPO_ROOT), "git reported nothing ignored; gate is vacuous"

    def test_no_generated_example_names_an_ignored_path(self):
        ignored = _ignored_top_level(REPO_ROOT) - self.NAMED_BY_DESIGN
        offenders = []

        for path in self._generated_examples():
            text = path.read_text(encoding="utf-8", errors="ignore")
            for name in sorted(ignored):
                # A path segment, not a substring: `build` must not match
                # `graph_builder.py`.
                pattern = rf"(?:^|[\s\"'`(/]){re.escape(name)}(?:[/\s\"'`),:]|$)"
                if re.search(pattern, text, re.MULTILINE):
                    offenders.append(f"{path.relative_to(REPO_ROOT)} names {name}")

        assert offenders == [], offenders
