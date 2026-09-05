"""Contract tests: wiki export must describe the target repo, never invent."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from repo_signal.wiki_export import build_wiki_pages, export_wiki_pages


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_repo(root: Path) -> None:
    """A target repo with every source the exporter knows how to read."""
    write(
        root,
        "README.md",
        "# widget-forge\n\n"
        "Turns widget specs into build plans.\n\n"
        "## Quick start\n\n"
        "```bash\nwidget-forge build ./spec.yaml\n```\n\n"
        "## Notes\n\nSomething else.\n",
    )
    write(root, "VERSION", "2.1.0\n")
    write(root, "CHANGELOG.md", "# Changelog\n\n## [2.1.0] - 2026-08-01\n\n- thing\n")
    write(root, "ROADMAP.md", "# Roadmap\n\n## Current focus\n\nShipping the planner.\n")
    write(root, "docs/architecture.md", "# Architecture\n\n## Components\n\nPlanner and builder.\n")
    write(root, "docs/COMMANDS.md", "# Commands\n\n```bash\nwidget-forge build .\n```\n")
    write(root, "skills/spec-linter.md", "# spec-linter\n")


class TargetRepoContentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        make_repo(self.root)
        self.pages = build_wiki_pages(self.root)

    def test_every_expected_page_is_built(self) -> None:
        self.assertEqual(
            sorted(self.pages),
            sorted(
                [
                    "Home.md",
                    "Getting-Started.md",
                    "Command-Reference.md",
                    "Architecture.md",
                    "Roadmap.md",
                    "Release-Flow.md",
                    "Skills.md",
                    "Troubleshooting.md",
                ]
            ),
        )

    def test_no_page_mentions_repo_signal_when_target_is_another_repo(self) -> None:
        """The original bug: every page described repo-signal itself."""
        for name, content in self.pages.items():
            with self.subTest(page=name):
                self.assertNotIn("repo-signal", content)

    def test_home_names_the_target_repo_and_its_version(self) -> None:
        home = self.pages["Home.md"]
        self.assertIn("widget-forge", home)
        self.assertIn("Turns widget specs into build plans.", home)
        self.assertIn("2.1.0", home)

    def test_getting_started_uses_the_readme_quick_start(self) -> None:
        self.assertIn("widget-forge build ./spec.yaml", self.pages["Getting-Started.md"])

    def test_command_reference_uses_the_commands_doc(self) -> None:
        reference = self.pages["Command-Reference.md"]
        self.assertIn("widget-forge build .", reference)
        self.assertIn("docs/COMMANDS.md", reference)

    def test_architecture_uses_the_architecture_doc(self) -> None:
        self.assertIn("Planner and builder.", self.pages["Architecture.md"])

    def test_roadmap_uses_the_roadmap_file(self) -> None:
        self.assertIn("Shipping the planner.", self.pages["Roadmap.md"])

    def test_release_flow_reports_version_and_latest_release(self) -> None:
        release = self.pages["Release-Flow.md"]
        self.assertIn("2.1.0", release)
        self.assertIn("CHANGELOG.md", release)

    def test_skills_lists_the_skills_directory(self) -> None:
        self.assertIn("spec-linter", self.pages["Skills.md"])


class MissingSourceTests(unittest.TestCase):
    """A missing source must be reported, never filled in with plausible text."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        write(self.root, "README.md", "# bare-repo\n")
        self.pages = build_wiki_pages(self.root)

    def test_bare_repo_still_builds_every_page(self) -> None:
        self.assertEqual(len(self.pages), 8)

    def test_missing_sources_are_stated_not_invented(self) -> None:
        for name in (
            "Getting-Started.md",
            "Command-Reference.md",
            "Architecture.md",
            "Roadmap.md",
            "Skills.md",
            "Troubleshooting.md",
        ):
            with self.subTest(page=name):
                self.assertIn("No ", self.pages[name])

    def test_no_page_invents_a_command(self) -> None:
        """Without a documented command surface, no page may show a shell fence."""
        for name, content in self.pages.items():
            with self.subTest(page=name):
                self.assertNotIn("```bash", content)

    def test_home_falls_back_to_the_directory_name(self) -> None:
        self.assertIn("bare-repo", self.pages["Home.md"])


class ExportTests(unittest.TestCase):
    def test_export_writes_the_built_pages(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        make_repo(root)

        summary = export_wiki_pages(str(root), "docs/wiki-export")
        output = root / "docs" / "wiki-export"

        self.assertIn("WIKI EXPORT", summary)
        self.assertIn("Repo: widget-forge", summary)
        for name in build_wiki_pages(root):
            with self.subTest(page=name):
                self.assertTrue((output / name).exists())
        self.assertIn(
            "widget-forge build ./spec.yaml",
            (output / "Getting-Started.md").read_text(encoding="utf-8"),
        )

    def test_export_reports_the_repo_name_from_the_readme_heading(self) -> None:
        """Directory name and project name differ; the summary uses the real one."""
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name) / "checkout-dir"
        root.mkdir()
        make_repo(root)

        summary = export_wiki_pages(str(root), "docs/wiki-export")

        self.assertIn("Repo: widget-forge", summary)


class GitignoredSourceTests(unittest.TestCase):
    """Gitignored files must not reach a page that gets published."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        make_repo(self.root)

        write(self.root, ".gitignore", "skills/\nROADMAP.md\n")
        write(self.root, "skills/local-only.md", "# local-only\n")

        for command in (
            ["git", "init", "-q"],
            ["git", "add", "-A"],
            ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "init"],
        ):
            subprocess.run(command, cwd=self.root, capture_output=True, check=True)

        self.pages = build_wiki_pages(self.root)

    def test_gitignored_skill_is_not_listed(self) -> None:
        self.assertNotIn("local-only", self.pages["Skills.md"])
        self.assertNotIn("spec-linter", self.pages["Skills.md"])

    def test_gitignored_document_is_reported_missing_not_read(self) -> None:
        roadmap = self.pages["Roadmap.md"]
        self.assertNotIn("Shipping the planner.", roadmap)
        self.assertIn("No roadmap found", roadmap)

    def test_tracked_documents_are_still_read(self) -> None:
        self.assertIn("Planner and builder.", self.pages["Architecture.md"])


class HelpTests(unittest.TestCase):
    def test_wiki_export_help_exits_zero_and_lists_output(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; sys.argv=['repo-signal','wiki','export','--help'];"
                "from repo_signal.cli import main; raise SystemExit(main())",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).resolve().parents[1],
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("--output", result.stdout)
        self.assertIn("never pushed", result.stdout)


if __name__ == "__main__":
    unittest.main()
